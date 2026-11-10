"""Stage diagnostics tested with local fakes and an SDK MockTransport only."""
import json
from types import SimpleNamespace
from unittest.mock import Mock

import httpx
from openai import OpenAI
import pytest

from scripts import local_test_app as launcher
from src.knowledge_assistant import stage_timing as timing
from src.knowledge_assistant.core import Answer, Assistant, Claim
from src.knowledge_assistant.provider_telemetry import ObservedChat, ObservedEmbeddings

SECRET = 'fake-private-question-key-password-never-record'


@pytest.fixture
def capture(tmp_path, monkeypatch):
    monkeypatch.delenv(timing.TIMING_ENV, raising=False)
    path = tmp_path / 'logs/local-verification/offline/stages.jsonl'
    path.parent.mkdir(parents=True)
    path.touch()
    return timing.TimingCapture(path, root=tmp_path)


def events(capture):
    return [json.loads(line) for line in capture.path.read_text().splitlines()]


def test_nested_embedding_retrieval_generation_spans_keep_results_and_no_private_text(capture):
    embeddings = Mock()
    embeddings.embed_query.return_value = [1.0]
    query = ObservedEmbeddings(embeddings, None, SECRET)
    document = SimpleNamespace(page_content=SECRET,
                               metadata={'chunk_id': 'c1', 'filename': 'private.pdf', 'page': 1})
    def retrieve(question, **kwargs):
        query.embed_query(question)
        return [document]
    expected = Answer(status='answered', claims=[Claim(text=SECRET, source_ids=['c1'])])
    model = Mock()
    model.invoke.return_value = expected
    engine = Assistant.__new__(Assistant)
    engine.ready, engine.session_id = True, 'private-session-id'
    engine.store = SimpleNamespace(similarity_search=retrieve)
    engine.model = ObservedChat(model, None, SECRET)
    with timing.response_timing(capture):
        answer, sources = engine.ask(SECRET)
    assert answer is expected and sources['c1'] is document
    assert embeddings.embed_query.call_count == model.invoke.call_count == 1
    rows = events(capture)
    ends = {r['stage']: r for r in rows if r['event'] == 'span_end'}
    assert set(ends) == {'response_path', 'retrieval_including_query_embedding',
                         'query_embedding', 'generation_including_sdk_retries_and_parse'}
    assert ends['query_embedding']['parent_span_id'] == ends['retrieval_including_query_embedding']['span_id']
    assert ends['query_embedding']['elapsed_ns'] <= ends['retrieval_including_query_embedding']['elapsed_ns']
    assert all(r['ok'] and r['elapsed_ns'] >= 0 for r in ends.values())
    assert len({r['trace_id'] for r in rows}) == 1
    text = capture.path.read_text()
    assert SECRET not in text and 'private.pdf' not in text and 'private-session-id' not in text


def test_real_sdk_internal_retry_is_observed_without_network_or_retry_setting_change(capture):
    calls = []
    def transport(request):
        calls.append(request)
        if len(calls) == 1:
            return httpx.Response(429, headers={'retry-after': '0.001'}, json={
                'error': {'message': SECRET, 'type': 'rate_limit_error', 'code': 'rate_limit_exceeded'}})
        return httpx.Response(200, json={'object': 'list', 'data': [
            {'object': 'embedding', 'index': 0, 'embedding': [1.0]}], 'model': 'offline-model'})
    with httpx.Client(transport=httpx.MockTransport(transport)) as http:
        sdk = OpenAI(api_key=SECRET, base_url='https://example.invalid', http_client=http,
                     max_retries=2, timeout=45)
        original_transport, original_timeout = http._transport, http.timeout
        existing = Mock()
        http.event_hooks['request'].append(existing)
        assert timing.attach_http_timing(sdk)
        assert timing.attach_http_timing(sdk)  # No duplicate hook on reuse.
        with timing.response_timing(capture):
            with timing.span('generation_including_sdk_retries_and_parse'):
                result = sdk.embeddings.create(model='offline-model', input=SECRET)
        assert result.data[0].embedding == [1.0]
        assert len(calls) == existing.call_count == 2
        assert sdk.max_retries == 2 and http._transport is original_transport and http.timeout == original_timeout
    responses = [r for r in events(capture) if r['event'] == 'http_response_headers']
    assert [r['http_status'] for r in responses] == [429, 200]
    assert [r['sdk_retry_count'] for r in responses] == [0, 1]
    assert len({r['attempt_id'] for r in responses}) == 2
    assert all(r['elapsed_ns'] >= 0 for r in responses)
    text = capture.path.read_text()
    assert SECRET not in text and 'example.invalid' not in text and 'offline-model' not in text


def test_missing_retry_header_stays_unknown_and_hooks_do_not_read_response_body(capture):
    request = httpx.Request('POST', 'https://example.invalid', headers={'authorization': SECRET})
    response = Mock(request=request, status_code=200)
    with timing.response_timing(capture), timing.span('query_embedding'):
        timing._request_hook(request)
        timing._response_hook(response)
    response.read.assert_not_called()
    response.json.assert_not_called()
    row = next(r for r in events(capture) if r['event'] == 'http_response_headers')
    assert row['sdk_retry_count'] is None


def test_error_span_preserves_original_exception_and_failed_sink_never_masks_it(capture):
    failure = RuntimeError(SECRET)
    delegate = Mock()
    delegate.embed_query.side_effect = failure
    with pytest.raises(RuntimeError) as caught:
        with timing.response_timing(capture):
            ObservedEmbeddings(delegate, None, SECRET).embed_query(SECRET)
    assert caught.value is failure and delegate.embed_query.call_count == 1
    assert all(r['ok'] is False for r in events(capture) if r['event'] == 'span_end')
    assert SECRET not in capture.path.read_text()
    capture.path.unlink()
    with pytest.raises(RuntimeError) as caught:
        with timing.response_timing(capture), timing.span('query_embedding'):
            raise failure
    assert caught.value is failure and not capture.path.exists()


def test_timing_is_disabled_without_explicit_local_existing_sink(capture, monkeypatch):
    monkeypatch.setattr(timing, 'ROOT', capture.root)
    monkeypatch.setenv(timing.TIMING_ENV, str(capture.path))
    monkeypatch.setenv('AI_PROVIDER', 'gemini')
    monkeypatch.setenv('SUPABASE_URL', 'https://remote.example')
    assert timing.local_timing_capture() is None
    with timing.response_timing(), timing.span('answer_formatting'):
        pass
    assert capture.path.read_bytes() == b''
    monkeypatch.setenv('SUPABASE_URL', launcher.LOCAL_API)
    assert timing.local_timing_capture() is not None
    monkeypatch.delenv(timing.TIMING_ENV)
    assert timing.local_timing_capture() is None


@pytest.mark.parametrize('saved', [False, True])
def test_persistence_io_is_distinguished_from_skipped_branch(capture, monkeypatch, saved):
    from src.knowledge_assistant import persistence_ui as ui
    class State(dict):
        __getattr__ = dict.__getitem__
    state = State(messages=[{'content': SECRET}])
    if saved:
        state['saved_workspace_id'] = SECRET
    store = Mock()
    monkeypatch.setattr(ui.st, 'session_state', state)
    monkeypatch.setattr(ui, 'workspace_store', lambda: store)
    with timing.response_timing(capture):
        ui.persist_chat()
    rows = events(capture)
    if saved:
        store.save_chat.assert_called_once_with(SECRET, state['messages'])
        assert any(r['event'] == 'span_end' and r['stage'] == 'workspace_persistence' for r in rows)
    else:
        store.save_chat.assert_not_called()
        assert any(r['event'] == 'persistence_skipped' for r in rows)
        assert not any(r['event'] == 'span_end' and r['stage'] == 'workspace_persistence' for r in rows)
    assert SECRET not in capture.path.read_text()


def test_launcher_rejects_inherited_unowned_and_existing_timing_sinks(tmp_path):
    config = {'SUPABASE_URL': launcher.LOCAL_API, 'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_offline',
              'AI_PROVIDER': 'gemini', 'GEMINI_API_KEY': SECRET,
              'GEMINI_CHAT_MODEL': 'offline-chat', 'GEMINI_EMBEDDING_MODEL': 'offline-embedding'}
    env = launcher.child_environment(config, {timing.TIMING_ENV.lower(): 'do-not-inherit'})
    assert timing.TIMING_ENV.lower() not in env and timing.TIMING_ENV not in env
    output = tmp_path / 'logs/local-verification/owned'
    sink = output / 'stages.jsonl'
    app = launcher.LocalTestApp(tmp_path, output, config, stage_timing_file=sink)
    assert app.environment[timing.TIMING_ENV] == str(sink) and not sink.exists()
    with pytest.raises(ValueError):
        launcher.LocalTestApp(tmp_path, output, config, stage_timing_file=tmp_path / 'public.jsonl')
    output.mkdir(parents=True)
    sink.write_text('preserved')
    with pytest.raises(FileExistsError):
        launcher.LocalTestApp(tmp_path, output, config, stage_timing_file=sink)
    assert sink.read_text() == 'preserved'
