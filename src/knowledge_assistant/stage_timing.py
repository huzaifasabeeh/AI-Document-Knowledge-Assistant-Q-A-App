"""Opt-in local diagnostic spans; no inputs, outputs, URLs or credentials.

Parent spans include children. HTTP hooks observe request start and response
headers, not full-body transfer or pure provider computation. SDK retry counts
are retained only when explicitly supplied in its numeric request header.
"""
from contextlib import contextmanager
from contextvars import ContextVar
import json
import os
from pathlib import Path
from time import perf_counter_ns, time_ns
from uuid import uuid4

TIMING_ENV = 'KNOWLEDGE_ASSISTANT_STAGE_TIMING_FILE'
ROOT = Path(__file__).resolve().parents[2]
STAGES = frozenset({'response_path', 'retrieval_including_query_embedding',
                    'query_embedding', 'document_embedding',
                    'generation_including_sdk_retries_and_parse',
                    'answer_formatting', 'workspace_persistence'})
_active = ContextVar('knowledge_assistant_timing', default=None)
_parent = ContextVar('knowledge_assistant_timing_parent', default=None)
_stage = ContextVar('knowledge_assistant_timing_stage', default=None)


class TimingCapture:
    def __init__(self, path, root=None):
        from .provider_telemetry import validate_capture_path
        self.root = Path(ROOT if root is None else root).resolve()
        self.path = validate_capture_path(self.root, path)

    def emit(self, event, stage=None, span_id=None, parent_id=None, elapsed_ns=None,
             ok=None, http_status=None, sdk_retry_count=None, attempt_id=None):
        active = _active.get()
        if active is None or stage not in STAGES or event not in {
                'span_start', 'span_end', 'http_request_start',
                'http_response_headers', 'persistence_skipped'}:
            return
        record = {'event': event, 'stage': stage, 'trace_id': active[1],
                  'span_id': span_id, 'parent_span_id': parent_id,
                  'monotonic_ns': perf_counter_ns(), 'wall_time_ns': time_ns()}
        if elapsed_ns is not None:
            record['elapsed_ns'] = elapsed_ns
        if ok is not None:
            record['ok'] = bool(ok)
        if attempt_id is not None:
            record.update({'attempt_id': attempt_id, 'http_status': http_status,
                           'sdk_retry_count': sdk_retry_count})
        try:
            from .provider_telemetry import validate_capture_path
            path = validate_capture_path(self.root, self.path)
            encoded = (json.dumps(record, allow_nan=False) + '\n').encode('utf-8')
            descriptor = os.open(path, os.O_WRONLY | os.O_APPEND | getattr(os, 'O_NOFOLLOW', 0))
            try:
                os.write(descriptor, encoded)
            finally:
                os.close(descriptor)
        except Exception:
            # Diagnostics must not replace application output/errors.
            pass


def local_timing_capture():
    target = os.environ.get(TIMING_ENV)
    if (not target or os.environ.get('SUPABASE_URL') != 'http://127.0.0.1:54321'
            or os.environ.get('AI_PROVIDER') != 'gemini'):
        return None
    try:
        capture = TimingCapture(target)
        return capture if capture.path.is_file() else None
    except (ValueError, OSError):
        return None


@contextmanager
def response_timing(capture=None):
    capture = local_timing_capture() if capture is None else capture
    if capture is None:
        yield
        return
    token = _active.set((capture, uuid4().hex))
    parent = _parent.set(None)
    try:
        with span('response_path'):
            yield
    finally:
        _parent.reset(parent)
        _active.reset(token)


@contextmanager
def span(stage):
    active = _active.get()
    if active is None:
        yield
        return
    if stage not in STAGES:
        raise ValueError('Unknown diagnostic timing stage.')
    capture, _ = active
    span_id, parent_id = uuid4().hex, _parent.get()
    started = perf_counter_ns()
    capture.emit('span_start', stage, span_id, parent_id)
    parent_token, stage_token = _parent.set(span_id), _stage.set(stage)
    ok = False
    try:
        yield
        ok = True
    finally:
        capture.emit('span_end', stage, span_id, parent_id,
                     elapsed_ns=perf_counter_ns() - started, ok=ok)
        _stage.reset(stage_token)
        _parent.reset(parent_token)


def persistence_skipped():
    active = _active.get()
    if active:
        active[0].emit('persistence_skipped', 'workspace_persistence',
                       parent_id=_parent.get())


def _request_hook(request):
    try:
        active, stage = _active.get(), _stage.get()
        if not active or stage not in {'query_embedding', 'generation_including_sdk_retries_and_parse'}:
            return
        value = request.headers.get('x-stainless-retry-count')
        retry = int(value) if isinstance(value, str) and value.isascii() and value.isdigit() and len(value) <= 4 else None
        item = (active[0], stage, _parent.get(), perf_counter_ns(), uuid4().hex, retry)
        request.extensions['_knowledge_assistant_timing'] = item
        item[0].emit('http_request_start', stage, parent_id=item[2],
                     attempt_id=item[4], sdk_retry_count=retry)
    except Exception:
        pass


def _response_hook(response):
    try:
        item = response.request.extensions.pop('_knowledge_assistant_timing', None)
        if item is None:
            return
        capture, stage, parent_id, started, attempt_id, retry = item
        status = response.status_code
        capture.emit('http_response_headers', stage, parent_id=parent_id,
                     elapsed_ns=perf_counter_ns() - started, attempt_id=attempt_id,
                     sdk_retry_count=retry,
                     http_status=status if type(status) is int and 100 <= status <= 599 else None)
    except Exception:
        pass


def attach_http_timing(sdk_client):
    """Add hooks to the existing sync client, preserving transport/pools/retries."""
    try:
        client = sdk_client._client
        hooks = client.event_hooks
        if _request_hook not in hooks['request']:
            hooks['request'].append(_request_hook)
        if _response_hook not in hooks['response']:
            hooks['response'].append(_response_hook)
        return True
    except (AttributeError, KeyError, TypeError):
        return False
