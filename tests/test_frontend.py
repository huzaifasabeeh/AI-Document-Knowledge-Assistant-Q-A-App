from pathlib import Path
from unittest.mock import Mock
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest
from langchain_core.documents import Document
from src.knowledge_assistant.core import Answer, Claim
from src.knowledge_assistant.presentation import provider_error, format_answer

APP = Path(__file__).resolve().parents[1] / 'app.py'


def test_local_preview_needs_no_key_or_provider(monkeypatch):
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    file = Mock()
    file.name = 'leave.pdf'
    file.getvalue.return_value = (APP.parent / 'data/sample_pdfs/leave.pdf').read_bytes()
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **kw: [file])
    factory = Mock(side_effect=AssertionError('No provider allowed'))
    monkeypatch.setattr('src.knowledge_assistant.core.openai_assistant', factory)
    app = AppTest.from_file(APP).run()
    app.button(key='preview_pages').click().run()
    assert not app.exception
    assert len(app.session_state['preview']) == 2
    assert app.session_state['preview'][0]['page'] == 1
    assert '20 days' in app.session_state['preview'][0]['text']
    assert app.button(key='index').disabled
    assert app.chat_input[0].disabled
    factory.assert_not_called()
    app.button(key='reset').click().run()
    assert app.session_state['preview'] == []


def test_failed_index_shows_quota_and_allows_fresh_retry(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY', 'sk-test')
    file = Mock()
    file.name = 'leave.pdf'
    file.getvalue.return_value = (APP.parent / 'data/sample_pdfs/leave.pdf').read_bytes()
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **kw: [file])
    error = RuntimeError('secret raw response must not appear')
    error.code = 'credit_balance_exhausted'
    failed = Mock()
    failed.ingest.side_effect = error
    successful = Mock()
    successful.ingest.return_value = 2
    factory = Mock(side_effect=[failed, successful])
    monkeypatch.setattr('src.knowledge_assistant.core.openai_assistant', factory)
    app = AppTest.from_file(APP).run()
    app.checkbox(key='consent').check().run()
    app.button(key='index').click().run()
    assert not app.exception
    assert any('credits are unavailable' in e.value for e in app.error)
    assert not any('secret raw' in e.value for e in app.error)
    assert app.chat_input[0].disabled
    failed.close.assert_called_once()
    app.button(key='index').click().run()
    assert not app.exception
    assert not app.chat_input[0].disabled
    assert app.session_state['documents'] == ['leave.pdf']
    app.checkbox(key='consent').uncheck().run()
    assert app.chat_input[0].disabled
    app.button(key='reset').click().run()
    assert not app.exception
    successful.close.assert_called_once()
    assert app.session_state['documents'] == []
    assert app.chat_input[0].disabled


def test_cleanup_failure_blocks_chat_until_reset():
    engine = Mock()
    engine.close.side_effect = [RuntimeError('busy'), None]
    app = AppTest.from_file(APP)
    app.session_state['assistant'] = engine
    app.session_state['documents'] = ['leave.pdf']
    app.run()
    app.button(key='reset').click().run()
    assert app.session_state['cleanup_blocked']
    app.button(key='reset').click().run()
    assert not app.exception
    assert not app.session_state['cleanup_blocked']
    assert app.chat_input[0].disabled


def test_source_cards_keep_citation_mapping_and_deduplicate():
    sources = {'c1': Document(page_content='20 days', metadata={'filename':'leave.pdf','page':1})}
    answer = Answer(status='answered', claims=[Claim(text='20 days', source_ids=['c1','c1'])])
    text, evidence = format_answer(answer, sources)
    assert text == '20 days\nSources: leave.pdf, PDF page 1'
    assert evidence == [{'filename':'leave.pdf','page':1,'text':'20 days'}]
    assert format_answer(Answer(status='not_found', claims=[]), sources)[1] == []


@pytest.mark.parametrize('status,code,expected', [(429,'credit_balance_exhausted','credits'), (429,None,'request limit'), (401,None,'authentication'), (500,None,'network')])
def test_provider_errors_never_echo_raw_details(status, code, expected):
    error = RuntimeError('private secret')
    error.status_code = status
    error.body = {'error': {'code': code}}
    result = provider_error(error)
    assert expected in result
    assert 'private secret' not in result


def test_chat_renders_sources_and_keeps_evidence_out_of_history():
    engine = Mock()
    engine.ask.return_value = (
        Answer(status='answered', claims=[Claim(text='20 days.', source_ids=['c1'])]),
        {'c1': Document(page_content='Employees receive 20 days.', metadata={'filename':'leave.pdf','page':1})})
    app = AppTest.from_file(APP)
    app.session_state['assistant'] = engine
    app.session_state['documents'] = ['leave.pdf']
    app.session_state['consent'] = True
    app.run()
    app.chat_input[0].set_value('How much leave?').run()
    assert not app.exception
    assert len(app.chat_message) == 2
    assert any(e.label == 'View supporting passages' for e in app.expander)
    assert app.session_state['messages'][1]['sources'][0]['page'] == 1
    app.chat_input[0].set_value('Who receives it?').run()
    history = engine.ask.call_args.args[1]
    assert all(set(turn) == {'role', 'content'} for turn in history)
    app.button(key='reset').click().run()
    assert app.session_state['messages'] == []
    assert app.chat_input[0].disabled


def test_preview_clears_when_same_filename_content_changes(monkeypatch):
    file = Mock()
    file.name = 'leave.pdf'
    file.getvalue.return_value = (APP.parent / 'data/sample_pdfs/leave.pdf').read_bytes()
    monkeypatch.setattr(st, 'file_uploader', lambda *a, **kw: [file])
    app = AppTest.from_file(APP).run()
    app.button(key='preview_pages').click().run()
    assert app.session_state['preview']
    file.getvalue.return_value = b'not a PDF'
    app.run()
    assert not app.session_state['preview']
    app.button(key='preview_pages').click().run()
    assert app.error
    assert not app.exception


def test_clear_chat_keeps_index_and_removes_followup_context():
    engine = Mock()
    engine.ask.return_value = (Answer(status='not_found', claims=[]), {})
    app = AppTest.from_file(APP)
    app.session_state['assistant'] = engine
    app.session_state['documents'] = ['leave.pdf']
    app.session_state['consent'] = True
    app.session_state['messages'] = [
        {'role': 'user', 'content': 'Old question'},
        {'role': 'assistant', 'content': 'Old answer', 'sources': []}]
    app.run()
    app.button(key='clear_chat').click().run()
    assert not app.exception
    assert app.session_state['messages'] == []
    assert app.session_state['documents'] == ['leave.pdf']
    engine.close.assert_not_called()
    app.chat_input[0].set_value('New question').run()
    assert engine.ask.call_args.args[1] == []


def test_export_includes_exact_evidence_without_mutating_history():
    from copy import deepcopy
    from src.knowledge_assistant.presentation import export_chat
    messages = [{'role': 'assistant', 'content': '20 days.', 'sources': [
        {'filename': 'leave.pdf', 'page': 1, 'text': 'Employees receive 20 days.'}]}]
    before = deepcopy(messages)
    text = export_chat(messages)
    assert 'leave.pdf | PDF page 1' in text
    assert 'Employees receive 20 days.' in text
    assert messages == before


@pytest.fixture(autouse=True)
def authenticated_workspace_for_existing_flow_tests(monkeypatch):
    # These tests exercise document UI; account gate is tested in test_auth.py.
    monkeypatch.setattr('src.knowledge_assistant.auth_ui.require_login', lambda: 'test-user')
