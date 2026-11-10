"""Local provider evidence projects safe fields without changing provider calls."""
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
import openai
import pytest

from scripts import local_test_app as local
from src.knowledge_assistant import provider_telemetry as telemetry
from src.knowledge_assistant.providers import ProviderConfig, configured_assistant


SECRET = 'AIzaFakeSecretKeyThatMustNeverBeRecorded'


def sdk_error(body=None, status=429, retry_after=None):
    request = httpx.Request('POST', 'https://example.invalid/embeddings',
                            headers={'Authorization': 'Bearer ' + SECRET})
    response = httpx.Response(status, request=request, headers={
        'x-secret-header': SECRET, **({'retry-after': retry_after} if retry_after else {})})
    return openai.APIStatusError('Raw body/document/token ' + SECRET, response=response, body=body)


def quota_body():
    return {'error': {'code': 429, 'status': 'RESOURCE_EXHAUSTED',
        'message': 'Private document text ' + SECRET,
        'details': [
            {'@type': 'type.googleapis.com/google.rpc.QuotaFailure', 'violations': [{
                'quotaMetric': 'generativelanguage.googleapis.com/embed_content_free_tier_requests',
                'quotaId': 'EmbedContentRequestsPerMinutePerProject-FreeTier',
                'quotaDimensions': {'model': 'gemini-embedding-001', 'location': 'global',
                                    'consumer': SECRET}, 'description': SECRET}]},
            {'@type': 'type.googleapis.com/google.rpc.RetryInfo', 'retryDelay': '34.25s'},
        ]}}


def test_actual_sdk_status_nested_quota_and_retry_fields_without_secrets():
    event = telemetry.sanitized_error(sdk_error(quota_body(), retry_after='7'),
                                     'embedding_query', 'gemini-embedding-001', secrets=(SECRET,))
    assert event['operation'] == 'embedding_query'
    assert event['model'] == 'gemini-embedding-001'
    assert event['http_status'] == 429
    assert event['provider_error_status'] == 'RESOURCE_EXHAUSTED'
    detail = event['quota_details'][0]
    assert detail['quota_metric'].endswith('embed_content_free_tier_requests')
    assert detail['quota_id'] == 'EmbedContentRequestsPerMinutePerProject-FreeTier'
    assert detail['quota_window'] is None  # Never infer from the quota ID.
    assert detail['quota_dimensions'] == {'model': 'gemini-embedding-001', 'location': 'global'}
    assert event['retry_after_seconds'] == 7
    assert event['retry_delay_seconds'] == 34.25
    encoded = json.dumps(event)
    assert SECRET not in encoded and 'Private document text' not in encoded
    assert 'Authorization' not in encoded and 'x-secret-header' not in encoded
    assert event['raw_message_or_body_saved'] is False


@pytest.mark.parametrize('shape', ['list', 'json_string', 'exception_cause'])
def test_nested_compatibility_body_shapes(shape):
    body = [quota_body()] if shape == 'list' else json.dumps(quota_body())
    error = sdk_error(body)
    if shape == 'exception_cause':
        outer = RuntimeError('Wrapper text ' + SECRET)
        outer.__cause__ = error
        error = outer
    event = telemetry.sanitized_error(error, 'chat', 'gemini-3.5-flash-lite', secrets=(SECRET,))
    assert event['http_status'] == 429
    assert event['quota_details'][0]['quota_metric']
    assert event['retry_delay_seconds'] == 34.25
    assert SECRET not in json.dumps(event)


def test_absent_fields_stay_null_and_body_code_does_not_become_http_status():
    error = RuntimeError('A raw message with status 429 and private text ' + SECRET)
    error.body = {'error': {'code': 429}}
    event = telemetry.sanitized_error(error, 'chat', 'test-chat')
    assert event['http_status'] is None
    assert event['error_code'] == 429
    for field in ('quota_details', 'retry_after_seconds', 'retry_after_http_date',
                  'retry_delay_seconds', 'message_retry_delay_seconds'):
        assert event[field] is None
    assert SECRET not in json.dumps(event)


def test_message_only_explicit_fields_are_projected_with_provenance():
    body = {'error': {'message': (
        'Private passage ' + SECRET + '\n'
        '* Quota exceeded for metric: generativelanguage.googleapis.com/generate_content_free_tier_requests, limit: 0, model: gemini-3.5-flash-lite\n'
        'Please retry in 39.631354448s.')}}
    event = telemetry.sanitized_error(sdk_error(body), 'chat', 'gemini-3.5-flash-lite', secrets=(SECRET,))
    detail = event['quota_details'][0]
    assert detail['provenance'] == 'provider_message_explicit_fields'
    assert detail['quota_limit_value'] == 0
    assert detail['quota_id'] is None and detail['quota_window'] is None
    assert detail['quota_dimensions'] == {'model': 'gemini-3.5-flash-lite'}
    assert event['message_retry_delay_seconds'] == 39.631354448
    assert event['message_retry_provenance'] == 'provider_message_explicit_retry_duration'
    assert event['retry_after_seconds'] is None  # Not an actual response header.
    assert event['retry_delay_seconds'] is None  # Not structured RetryInfo.
    assert SECRET not in json.dumps(event) and 'Private passage' not in json.dumps(event)


def test_conflicting_provided_retry_hints_are_preserved_separately():
    body = quota_body()
    body['error']['message'] = 'Please retry in 9 seconds. ' + SECRET
    event = telemetry.sanitized_error(sdk_error(body, retry_after='7'),
                                     'chat', 'test-chat', secrets=(SECRET,))
    assert event['retry_after_seconds'] == 7
    assert event['retry_delay_seconds'] == 34.25
    assert event['retry_delay_source'] == 'structured_provider_retry_delay'
    assert event['message_retry_delay_seconds'] == 9
    assert event['message_retry_provenance'] == 'provider_message_explicit_retry_duration'
    assert SECRET not in json.dumps(event)


def test_secret_like_identifiers_and_unknown_codes_are_omitted():
    error = sdk_error({'error': {'code': SECRET, 'details': [{
        'quotaId': SECRET, 'quotaMetric': 'x/' + SECRET,
        'quotaDimensions': {'model': SECRET}, 'description': SECRET}]}})
    event = telemetry.sanitized_error(error, 'chat', SECRET, secrets=(SECRET,))
    assert event['model'] is None and event['error_code'] is None
    assert SECRET not in json.dumps(event)


def test_http_date_retry_header_is_not_converted_into_a_guessed_delay():
    event = telemetry.sanitized_error(sdk_error(retry_after='Wed, 21 Oct 2015 07:28:00 GMT'),
                                     'chat', 'test-chat')
    assert event['retry_after_seconds'] is None
    assert event['retry_after_http_date'] == '2015-10-21T07:28:00+00:00'


@pytest.fixture
def capture(tmp_path):
    sink = tmp_path / 'logs/local-verification/owned/provider-errors.jsonl'
    sink.parent.mkdir(parents=True)
    sink.touch(exist_ok=False)
    return telemetry.LocalProviderErrorCapture(sink, root=tmp_path, secrets=(SECRET,))


def events(capture):
    return [json.loads(line) for line in capture.path.read_text(encoding='utf-8').splitlines()]


def test_external_query_proxy_records_once_when_sdk_calls_its_own_document_method(capture):
    error = sdk_error(quota_body())
    class SDKEmbeddings:
        def embed_documents(self, texts, **kwargs):
            raise error

        def embed_query(self, text, **kwargs):
            return self.embed_documents([text], **kwargs)[0]

    observed = telemetry.ObservedEmbeddings(SDKEmbeddings(), capture, 'gemini-embedding-001')
    with pytest.raises(openai.APIStatusError) as caught:
        observed.embed_query('Private query must not be recorded')
    assert caught.value is error
    assert [event['operation'] for event in events(capture)] == ['embedding_query']
    assert 'Private query' not in capture.path.read_text(encoding='utf-8')


def test_document_and_chat_operations_append_independently_and_preserve_exceptions(capture):
    error = sdk_error(quota_body())
    embeddings = Mock()
    embeddings.embed_documents.side_effect = error
    model = Mock()
    model.invoke.side_effect = error
    for observed, call in (
        (telemetry.ObservedEmbeddings(embeddings, capture, 'embedding-model'), 'embed_documents'),
        (telemetry.ObservedChat(model, capture, 'chat-model'), 'invoke'),
    ):
        with pytest.raises(openai.APIStatusError) as caught:
            getattr(observed, call)(['private input'])
        assert caught.value is error
    assert [(e['operation'], e['model']) for e in events(capture)] == [
        ('embedding_documents', 'embedding-model'), ('chat', 'chat-model')]
    assert len({e['event_id'] for e in events(capture)}) == 2


def test_success_does_not_log_or_change_result_and_capture_failure_preserves_error(capture):
    model = Mock()
    value = object()
    model.invoke.return_value = value
    observed = telemetry.ObservedChat(model, capture, 'chat-model')
    assert observed.invoke('private input', config={'test': True}) is value
    model.invoke.assert_called_once_with('private input', config={'test': True})
    assert events(capture) == []
    error = sdk_error()
    model.invoke.side_effect = error
    capture.path.unlink()
    with pytest.raises(openai.APIStatusError) as caught:
        observed.invoke('private input')
    assert caught.value is error and not capture.path.exists()


def local_config():
    return {'SUPABASE_URL': local.LOCAL_API, 'AI_PROVIDER': 'gemini',
            'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_offline_test',
            'GEMINI_API_KEY': SECRET, 'GEMINI_CHAT_MODEL': 'test-chat',
            'GEMINI_EMBEDDING_MODEL': 'test-embedding'}


def test_launcher_strips_inherited_capture_and_pins_only_explicit_owned_sink(tmp_path):
    inherited = {telemetry.CAPTURE_ENV.lower(): 'public-leak.jsonl', 'PATH': 'keep'}
    assert telemetry.CAPTURE_ENV.lower() not in local.child_environment(local_config(), inherited)
    output = tmp_path / 'logs/local-verification/owned'
    sink = output / 'provider-errors.jsonl'
    app = local.LocalTestApp(tmp_path, output, local_config(), provider_error_file=sink)
    assert app.environment[telemetry.CAPTURE_ENV] == str(sink)
    assert not sink.exists()  # The launcher creates it exclusively at start.
    default = local.LocalTestApp(tmp_path, output, local_config())
    assert telemetry.CAPTURE_ENV not in default.environment


def test_launcher_exclusively_creates_sink_before_its_mocked_child(tmp_path, monkeypatch):
    from unittest.mock import MagicMock
    output = tmp_path / 'logs/local-verification/owned'
    sink = output / 'provider-errors.jsonl'
    process = Mock()
    process.poll.return_value = None
    def launch(*args, **kwargs):
        assert sink.read_bytes() == b''
        assert kwargs['env'][telemetry.CAPTURE_ENV] == str(sink)
        return process
    monkeypatch.setattr(local, 'WINDOWS', False)
    monkeypatch.setattr(local.subprocess, 'Popen', launch)
    monkeypatch.setattr(local, '_available_port', lambda: 49123)
    response = MagicMock()
    response.__enter__.return_value = response
    response.status, response.read.return_value = 200, b'ok'
    opener = Mock()
    opener.open.return_value = response
    monkeypatch.setattr(local, 'build_opener', lambda *args: opener)
    app = local.LocalTestApp(tmp_path, output, local_config(), provider_error_file=sink)
    try:
        app.start()
    finally:
        app.stop()
    assert sink.read_bytes() == b''


@pytest.mark.parametrize('name', [
    'public.jsonl', 'logs/local-verification/../public.jsonl',
    'logs/local-verification/other/provider-errors.jsonl',
])
def test_launcher_rejects_unowned_sink(tmp_path, name):
    with pytest.raises(ValueError):
        local.LocalTestApp(tmp_path, tmp_path / 'logs/local-verification/owned', local_config(),
                           provider_error_file=tmp_path / name)


def test_existing_sink_is_preserved(tmp_path):
    output = tmp_path / 'logs/local-verification/owned'
    output.mkdir(parents=True)
    sink = output / 'provider-errors.jsonl'
    sink.write_text('Prior evidence\n', encoding='utf-8')
    with pytest.raises(FileExistsError):
        local.LocalTestApp(tmp_path, output, local_config(), provider_error_file=sink)
    assert sink.read_text(encoding='utf-8') == 'Prior evidence\n'


def test_symlink_sink_is_rejected_if_supported(tmp_path):
    output = tmp_path / 'logs/local-verification/owned'
    output.mkdir(parents=True)
    target = output / 'target.jsonl'
    target.touch()
    link = output / 'linked.jsonl'
    try:
        link.symlink_to(target)
    except OSError:
        pytest.skip('Creating symlinks requires an unavailable operating-system privilege.')
    with pytest.raises(ValueError):
        local.LocalTestApp(tmp_path, output, local_config(), provider_error_file=link)


def test_capture_requires_opt_in_local_supabase_and_existing_private_sink(tmp_path, monkeypatch):
    monkeypatch.setattr(telemetry, 'ROOT', tmp_path)
    config = ProviderConfig('gemini', SECRET, 'test-chat', 'test-embedding')
    monkeypatch.setenv('SUPABASE_URL', local.LOCAL_API)
    assert telemetry.local_capture(config) is None
    sink = tmp_path / 'logs/local-verification/owned/provider-errors.jsonl'
    sink.parent.mkdir(parents=True)
    sink.touch()
    monkeypatch.setenv(telemetry.CAPTURE_ENV, str(sink))
    assert telemetry.local_capture(config) is not None
    monkeypatch.setenv('SUPABASE_URL', 'https://production.example')
    assert telemetry.local_capture(config) is None


@pytest.mark.parametrize('enabled', [False, True])
def test_provider_constructor_models_retries_timeouts_and_schema_unchanged(monkeypatch, enabled):
    import langchain_openai
    import src.knowledge_assistant.core as core
    chat, embeddings, assistant = Mock(), Mock(), Mock()
    chat_factory = Mock(return_value=chat)
    embedding_factory = Mock(return_value=embeddings)
    monkeypatch.setattr(langchain_openai, 'ChatOpenAI', chat_factory)
    monkeypatch.setattr(langchain_openai, 'OpenAIEmbeddings', embedding_factory)
    monkeypatch.setattr(core, 'Assistant', assistant)
    capture = Mock() if enabled else None
    monkeypatch.setattr(telemetry, 'local_capture', lambda config: capture)
    configured_assistant(ProviderConfig('gemini', SECRET, 'chat-model', 'embedding-model'))
    assert chat_factory.call_args.kwargs == {
        'model': 'chat-model', 'timeout': 45, 'use_responses_api': False,
        'api_key': SECRET, 'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
        'max_retries': 2}
    assert embedding_factory.call_args.kwargs == {
        'model': 'embedding-model', 'request_timeout': 45,
        'api_key': SECRET, 'base_url': 'https://generativelanguage.googleapis.com/v1beta/openai/',
        'max_retries': 2, 'check_embedding_ctx_length': False, 'chunk_size': 20,
        'model_kwargs': {'encoding_format': 'float'}}
    chat.with_structured_output.assert_called_once_with(core.Answer, method='json_schema')
    actual_embeddings, actual_model = assistant.call_args.args
    if enabled:
        assert actual_embeddings.delegate is embeddings
        assert actual_model.delegate is chat.with_structured_output.return_value
    else:
        assert actual_embeddings is embeddings
        assert actual_model is chat.with_structured_output.return_value
