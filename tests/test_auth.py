from pathlib import Path
from unittest.mock import Mock
import pytest
from streamlit.testing.v1 import AppTest
from src.knowledge_assistant.auth import AuthClient, AuthError, clear_session, validate_credentials

APP = Path(__file__).resolve().parents[1] / 'app.py'


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_test')
    fake = Mock()
    fake.user.return_value = {'id': 'user-a', 'email': 'a@example.com', 'email_confirmed_at': 'now'}
    fake.login.return_value = ('test-token', fake.user.return_value)
    fake.signup.return_value = {'id': 'user-a'}
    monkeypatch.setattr('src.knowledge_assistant.auth_ui.AuthClient', Mock(return_value=fake))
    return fake


def test_unconfigured_app_is_closed(monkeypatch):
    monkeypatch.delenv('SUPABASE_URL', raising=False)
    monkeypatch.delenv('SUPABASE_PUBLISHABLE_KEY', raising=False)
    app = AppTest.from_file(APP).run()
    assert not app.exception
    assert not app.chat_input
    assert not app.get('file_uploader')
    assert 'not configured' in app.info[0].value


def test_login_logout_clears_workspace_even_when_provider_fails(client):
    app = AppTest.from_file(APP).run()
    assert not app.chat_input
    app.text_input(key='login_email').input('a@example.com')
    app.text_input(key='login_password').input('password123')
    app.button(key='FormSubmitter:login_form-Log in').click().run()
    assert not app.exception
    assert len(app.chat_input) == 1
    app.session_state['messages'] = [{'role': 'user', 'content': 'private'}]
    app.session_state['documents'] = ['private.pdf']
    engine = Mock()
    engine.close.side_effect = RuntimeError('secret')
    app.session_state['assistant'] = engine
    client.logout.side_effect = AuthError('unavailable')
    app.button(key='logout').click().run()
    assert not app.exception
    assert not app.chat_input
    assert 'auth_token' not in app.session_state
    assert 'messages' not in app.session_state
    assert 'documents' not in app.session_state
    engine.close.assert_called_once()
    assert 'Remote sign-out' in app.info[0].value


def test_invalid_login_does_not_expose_workspace(client):
    client.login.side_effect = AuthError('Authentication failed.')
    app = AppTest.from_file(APP).run()
    app.text_input(key='login_email').input('a@example.com')
    app.text_input(key='login_password').input('incorrect')
    app.button(key='FormSubmitter:login_form-Log in').click().run()
    assert not app.exception
    assert not app.chat_input
    assert app.error


def test_signup_requires_confirmation_and_does_not_log_in(client):
    app = AppTest.from_file(APP).run()
    app.text_input(key='signup_email').input('a@example.com')
    app.text_input(key='signup_password').input('password123')
    app.text_input(key='signup_confirm').input('password123')
    app.button(key='FormSubmitter:signup_form-Create account').click().run()
    assert not app.exception
    client.signup.assert_called_once_with('a@example.com', 'password123')
    assert not app.chat_input
    assert app.success


def test_expired_or_changed_account_clears_old_workspace(client):
    app = AppTest.from_file(APP)
    app.session_state['auth_token'] = 'old-token'
    app.session_state['auth_user_id'] = 'user-b'
    app.session_state['messages'] = ['private']
    app.run()
    assert not app.exception
    assert not app.chat_input
    assert 'messages' not in app.session_state
    assert 'auth_token' not in app.session_state


def test_sessions_do_not_share_login(client):
    a, b = AppTest.from_file(APP), AppTest.from_file(APP)
    a.session_state['auth_token'] = 'token-a'
    a.session_state['auth_user_id'] = 'user-a'
    a.run(); b.run()
    assert len(a.chat_input) == 1
    assert not b.chat_input
    assert 'auth_token' not in b.session_state


def test_cleanup_drops_all_secrets_even_if_close_fails():
    engine = Mock(); engine.close.side_effect = RuntimeError()
    state = {'assistant': engine, 'failed_engine': engine, 'auth_token': 'secret', 'messages': ['private']}
    assert clear_session(state)
    assert state == {}
    engine.close.assert_called_once()


@pytest.mark.parametrize('email,password,confirmation', [('bad', 'password123', 'password123'), ('a@b.co', 'short', 'short'), ('a@b.co', 'password123', 'different')])
def test_invalid_signup_values(email, password, confirmation):
    with pytest.raises(AuthError):
        validate_credentials(email, password, confirmation)


def test_auth_client_checks_provider_user(monkeypatch):
    c = AuthClient('https://example.supabase.co', 'sb_publishable_test')
    request = Mock(side_effect=[{'access_token': 'token'}, {'id': 'u', 'email_confirmed_at': 'now'}])
    monkeypatch.setattr(c, 'request', request)
    assert c.login('a@b.co', 'password123')[1]['id'] == 'u'
    assert request.call_args_list[1].args == ('user',)
    assert request.call_args_list[1].kwargs == {'token': 'token'}


def test_unverified_user_rejected(monkeypatch):
    c = AuthClient('https://example.supabase.co', 'sb_publishable_test')
    monkeypatch.setattr(c, 'request', lambda *a, **kw: {'id': 'u'})
    with pytest.raises(AuthError):
        c.user('token')


def test_http_failure_does_not_leak_provider_body(monkeypatch):
    from urllib.error import HTTPError
    from io import BytesIO
    opener = Mock()
    opener.open.side_effect = HTTPError('https://example', 400, 'secret details', {}, BytesIO(b'secret'))
    monkeypatch.setattr('src.knowledge_assistant.auth.build_opener', lambda *a: opener)
    c = AuthClient('https://example.supabase.co', 'sb_publishable_test')
    with pytest.raises(AuthError) as err:
        c.login('a@b.co', 'password123')
    assert 'secret' not in str(err.value)


@pytest.mark.parametrize('url,key', [('http://example.com', 'sb_publishable_test'), ('https://example.com', 'sb_secret_bad'), ('https://example.com/path', 'sb_publishable_test')])
def test_invalid_config_rejected(url, key):
    with pytest.raises(AuthError):
        AuthClient(url, key)
