"""Opt-in local error evidence; never persist raw provider messages or bodies.

Only the owned local launcher creates the sink. Wrappers observe the final SDK
exception without changing calls, retries, timeouts, model settings or prompts.
"""
from collections import deque
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
import json
import math
import os
from pathlib import Path
import re
from uuid import uuid4

from langchain_core.embeddings import Embeddings
from .stage_timing import span

CAPTURE_ENV = 'KNOWLEDGE_ASSISTANT_PROVIDER_ERROR_FILE'
LOCAL_API = 'http://127.0.0.1:54321'
ROOT = Path(__file__).resolve().parents[2]
OPERATIONS = {'embedding_documents', 'embedding_query', 'chat'}
SAFE_CODES = {
    'RESOURCE_EXHAUSTED', 'RATE_LIMIT_EXCEEDED', 'INSUFFICIENT_QUOTA',
    'UNAUTHENTICATED', 'PERMISSION_DENIED', 'MODEL_NOT_FOUND', 'NOT_FOUND',
    'INVALID_ARGUMENT', 'INTERNAL', 'UNAVAILABLE', 'DEADLINE_EXCEEDED',
    'rate_limit_exceeded', 'insufficient_quota', 'credit_balance_exhausted',
    'invalid_api_key', 'model_not_found', 'permission_denied',
}


def validate_capture_path(root, path, owned_output=None):
    """Resolve links/traversal before permitting an ignored local JSONL sink."""
    root = Path(root).resolve()
    supplied = Path(path)
    supplied = supplied if supplied.is_absolute() else root / supplied
    resolved = supplied.resolve()
    allowed = root / 'logs/local-verification'
    if (not resolved.is_relative_to(allowed) or resolved.suffix != '.jsonl'
            or supplied.is_symlink()):
        raise ValueError('Provider evidence must be an owned local verification JSONL file.')
    if owned_output is not None and not resolved.is_relative_to(Path(owned_output).resolve()):
        raise ValueError('Provider evidence must stay inside this owned child output folder.')
    return resolved


def _attribute(value, name):
    try:
        return getattr(value, name, None)
    except Exception:
        return None


def _safe_identifier(value, secrets, *, unit=False):
    if not isinstance(value, str) or not 1 <= len(value) <= 240:
        return None
    if any(secret and secret in value for secret in secrets):
        return None
    if re.search(r'AIza|sk-|sb_secret_|Bearer|eyJ[A-Za-z0-9_-]+\.', value, re.I):
        return None
    pattern = r'[A-Za-z0-9_./{}:-]+' if unit else r'[A-Za-z0-9_./:-]+'
    return value if re.fullmatch(pattern, value) else None


def _number(value):
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)) and math.isfinite(value) and value >= 0:
        return value
    if isinstance(value, str) and re.fullmatch(r'\d+(?:\.\d+)?', value):
        number = float(value)
        return number if math.isfinite(number) else None
    return None


def _objects(value):
    # Bounded inspection of SDK/Gemini nested shapes; nothing is copied wholesale.
    queue = deque([(value, 0)])
    count = 0
    while queue and count < 512:
        item, depth = queue.popleft()
        count += 1
        if depth > 10:
            continue
        if isinstance(item, dict):
            yield item
            queue.extend((child, depth + 1) for child in list(item.values())[:64])
        elif isinstance(item, list):
            queue.extend((child, depth + 1) for child in item[:64])


def _body(error):
    body = _attribute(error, 'body')
    if body is None:
        response = _attribute(error, 'response')
        try:
            body = response.json() if response is not None else None
        except Exception:
            return None
    if isinstance(body, str):
        if len(body) > 65536:
            return None
        try:
            body = json.loads(body)
        except ValueError:
            return None
    return body if isinstance(body, (dict, list)) else None


def _exception_chain(error):
    seen = set()
    while isinstance(error, BaseException) and id(error) not in seen and len(seen) < 6:
        seen.add(id(error))
        yield error
        error = _attribute(error, '__cause__') or _attribute(error, '__context__')


def _quota_detail(item, secrets):
    aliases = {
        'quota_metric': ('quotaMetric', 'quota_metric'),
        'quota_id': ('quotaId', 'quota_id'),
        'quota_window': ('quotaWindow', 'quota_window'),
        'quota_limit': ('quota_limit',),
        'quota_unit': ('quota_unit', 'quotaUnit'),
        'quota_limit_value': ('quota_limit_value',),
        'quota_value': ('quotaValue', 'quota_value'),
    }
    if not any(key in item for names in aliases.values() for key in names):
        return None
    result = {'provenance': 'structured_provider_fields'}
    for target, names in aliases.items():
        provided = next((item[name] for name in names if name in item), None)
        result[target] = (_number(provided) if target in {'quota_value', 'quota_limit_value'}
                          else _safe_identifier(provided, secrets, unit=target == 'quota_unit'))
    dimensions = item.get('quotaDimensions', item.get('quota_dimensions'))
    result['quota_dimensions'] = ({
        name: _safe_identifier(dimensions[name], secrets)
        for name in ('model', 'location') if name in dimensions
    } if isinstance(dimensions, dict) else None)
    return result if any(value is not None for key, value in result.items()
                         if key != 'provenance') else None


def _message_fields(message, secrets):
    """Project only explicit Google metric/limit and retry-duration tokens.

    No sentence is retained; names of quota IDs never imply a window or reset.
    These fields carry different provenance from structured details/HTTP headers.
    """
    if not isinstance(message, str) or len(message) > 65536:
        return [], None, None
    details = []
    for line in message.splitlines()[:64]:
        metric = re.search(r'\bmetric:\s*(generativelanguage\.googleapis\.com/[A-Za-z0-9_./-]+)', line)
        if not metric:
            continue
        value = _safe_identifier(metric.group(1), secrets)
        if value is None:
            continue
        limit = re.search(r'\blimit:\s*(\d+(?:\.\d+)?)\b', line)
        model = re.search(r'\bmodel:\s*([A-Za-z0-9_./:-]+)', line)
        details.append({
            'provenance': 'provider_message_explicit_fields',
            'quota_metric': value, 'quota_id': None, 'quota_window': None,
            'quota_limit': None, 'quota_unit': None, 'quota_value': None,
            'quota_limit_value': _number(limit.group(1)) if limit else None,
            'quota_dimensions': ({'model': _safe_identifier(model.group(1), secrets)}
                                 if model else None),
        })
    retry = re.search(r'\bretry\s+(?:in|after)\s+(\d+(?:\.\d{1,9})?)\s*(?:seconds?\b|s\b)', message, re.I)
    duration = retry.group(1) + 's' if retry else None
    seconds = _number(retry.group(1)) if retry else None
    return details, duration, seconds


def sanitized_error(error, operation, model, provider='gemini', secrets=()):
    """Select structured evidence only; body/message/request/headers are not logged."""
    if operation not in OPERATIONS:
        raise ValueError('Unknown provider operation.')
    status = code = provider_status = retry_after = retry_date = retry_delay = None
    retry_delay_seconds = retry_delay_source = None
    message_retry_delay = message_retry_seconds = None
    quota = []
    for current in _exception_chain(error):
        response = _attribute(current, 'response')
        actual_status = _attribute(current, 'status_code')
        if actual_status is None:
            actual_status = _attribute(response, 'status_code')
        if status is None and type(actual_status) is int and 100 <= actual_status <= 599:
            status = actual_status
        actual_code = _attribute(current, 'code')
        if code is None and (actual_code in SAFE_CODES if isinstance(actual_code, str) else False):
            code = actual_code
        try:
            header = response.headers.get('retry-after') if response is not None else None
        except Exception:
            header = None
        if retry_after is None and retry_date is None and isinstance(header, str):
            retry_after = _number(header)
            if retry_after is None and len(header) <= 60:
                try:
                    parsed = parsedate_to_datetime(header)
                    if parsed.tzinfo is not None:
                        retry_date = parsed.isoformat()
                except (ValueError, TypeError, OverflowError):
                    pass
        for item in _objects(_body(current)):
            for key in ('code', 'status'):
                provided = item.get(key)
                if isinstance(provided, str) and provided in SAFE_CODES:
                    if key == 'status' and provider_status is None:
                        provider_status = provided
                    elif key == 'code' and code is None:
                        code = provided
                elif key == 'code' and code is None and type(provided) is int and 100 <= provided <= 599:
                    code = provided
            detail = _quota_detail(item, secrets)
            if detail is not None and detail not in quota and len(quota) < 20:
                quota.append(detail)
            provided_delay = item.get('retryDelay', item.get('retry_delay'))
            if retry_delay is None and isinstance(provided_delay, str):
                if re.fullmatch(r'\d+(?:\.\d{1,9})?s', provided_delay):
                    retry_delay_seconds = _number(provided_delay[:-1])
                    if retry_delay_seconds is not None:
                        retry_delay = provided_delay
                        retry_delay_source = 'structured_provider_retry_delay'
            message_details, message_delay, message_seconds = _message_fields(item.get('message'), secrets)
            for detail in message_details:
                if detail not in quota and len(quota) < 20:
                    quota.append(detail)
            if message_retry_delay is None and message_delay is not None:
                message_retry_delay, message_retry_seconds = message_delay, message_seconds
        message_details, message_delay, message_seconds = _message_fields(
            _attribute(current, 'message'), secrets)
        for detail in message_details:
            if detail not in quota and len(quota) < 20:
                quota.append(detail)
        if message_retry_delay is None and message_delay is not None:
            message_retry_delay, message_retry_seconds = message_delay, message_seconds
    return {
        'event_id': uuid4().hex, 'recorded_at': datetime.now(timezone.utc).isoformat(),
        'provider': provider if provider in {'gemini', 'openai'} else None,
        'operation': operation, 'model': _safe_identifier(model, secrets),
        'http_status': status, 'error_code': code, 'provider_error_status': provider_status,
        'sanitized_message': 'Provider operation failed; raw error text intentionally omitted.',
        'quota_details': quota or None,
        'retry_after_seconds': retry_after, 'retry_after_http_date': retry_date,
        'retry_delay': retry_delay, 'retry_delay_seconds': retry_delay_seconds,
        'retry_delay_source': retry_delay_source,
        'message_retry_delay': message_retry_delay,
        'message_retry_delay_seconds': message_retry_seconds,
        'message_retry_provenance': ('provider_message_explicit_retry_duration'
                                     if message_retry_delay is not None else None),
        'raw_message_or_body_saved': False,
    }


class LocalProviderErrorCapture:
    def __init__(self, path, root=None, secrets=()):
        self.root = Path(ROOT if root is None else root).resolve()
        self.path = validate_capture_path(self.root, path)
        self.secrets = tuple(value for value in secrets if isinstance(value, str) and value)

    def record(self, error, operation, model):
        path = validate_capture_path(self.root, self.path)
        # The launcher exclusively creates the sink; recording never creates or
        # replaces one. One append write preserves complete JSONL event boundaries.
        event = sanitized_error(error, operation, model, secrets=self.secrets)
        encoded = (json.dumps(event, ensure_ascii=True, allow_nan=False) + '\n').encode('utf-8')
        descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0))
        try:
            os.write(descriptor, encoded)
        finally:
            os.close(descriptor)


def local_capture(config):
    target = os.environ.get(CAPTURE_ENV)
    if (not target or config.provider != 'gemini'
            or os.environ.get('SUPABASE_URL') != LOCAL_API):
        return None
    try:
        capture = LocalProviderErrorCapture(target, secrets=(config.api_key,))
        return capture if capture.path.is_file() else None
    except (OSError, ValueError):
        return None


def _observe(capture, error, operation, model):
    try:
        capture.record(error, operation, model)
    except Exception:
        # Evidence failure must never mask or replace the original SDK exception.
        pass


class ObservedEmbeddings(Embeddings):
    """External proxy: SDK embed_query may call its own embed_documents once."""
    def __init__(self, delegate, capture, model):
        self.delegate, self.capture, self.model = delegate, capture, model

    def embed_documents(self, *args, **kwargs):
        try:
            with span('document_embedding'):
                return self.delegate.embed_documents(*args, **kwargs)
        except Exception as error:
            _observe(self.capture, error, 'embedding_documents', self.model)
            raise

    def embed_query(self, *args, **kwargs):
        try:
            with span('query_embedding'):
                return self.delegate.embed_query(*args, **kwargs)
        except Exception as error:
            _observe(self.capture, error, 'embedding_query', self.model)
            raise

    async def aembed_documents(self, *args, **kwargs):
        try:
            with span('document_embedding'):
                return await self.delegate.aembed_documents(*args, **kwargs)
        except Exception as error:
            _observe(self.capture, error, 'embedding_documents', self.model)
            raise

    async def aembed_query(self, *args, **kwargs):
        try:
            with span('query_embedding'):
                return await self.delegate.aembed_query(*args, **kwargs)
        except Exception as error:
            _observe(self.capture, error, 'embedding_query', self.model)
            raise


class ObservedChat:
    def __init__(self, delegate, capture, model):
        self.delegate, self.capture, self.model = delegate, capture, model

    def invoke(self, *args, **kwargs):
        try:
            with span('generation_including_sdk_retries_and_parse'):
                return self.delegate.invoke(*args, **kwargs)
        except Exception as error:
            _observe(self.capture, error, 'chat', self.model)
            raise

    async def ainvoke(self, *args, **kwargs):
        try:
            with span('generation_including_sdk_retries_and_parse'):
                return await self.delegate.ainvoke(*args, **kwargs)
        except Exception as error:
            _observe(self.capture, error, 'chat', self.model)
            raise
