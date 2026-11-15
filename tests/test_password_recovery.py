from io import BytesIO
from pathlib import Path
from unittest.mock import Mock
from urllib.error import HTTPError
import pytest
from streamlit.testing.v1 import AppTest
from src.knowledge_assistant.auth import (AuthClient, AuthError, RECOVERY_SENT, validate_email,
                                          validate_recovery)

APP = Path(__file__).resolve().parents[1] / 'app.py'
SEND = 'FormSubmitter:recovery_request_form-Send reset code'
RESET = 'FormSubmitter:recovery_reset_form-Set new password'


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_PUBLISHABLE_KEY', 'sb_publishable_test')
    fake = Mock()
    monkeypatch.setattr('src.knowledge_assistant.auth_ui.AuthClient', Mock(return_value=fake))
    return fake


def fill_reset(app, email='a@example.com', code='123456', password='newpassword1', confirm='newpassword1'):
    app.text_input(key='reset_email').input(email)
    app.text_input(key='reset_code').input(code)
    app.text_input(key='reset_password').input(password)
    app.text_input(key='reset_confirm').input(confirm)


def test_send_code_shows_same_message_and_does_not_log_in(client):
    app = AppTest.from_file(APP).run()
    app.text_input(key='recovery_email').input(' a@example.com ')
    app.button(key=SEND).click().run()
    assert not app.exception
    client.request_recovery.assert_called_once_with('a@example.com')
    assert app.success[0].value == RECOVERY_SENT
    assert not app.chat_input
    assert 'auth_token' not in app.session_state


def test_send_code_rejects_invalid_email_without_provider_call(client):
    app = AppTest.from_file(APP).run()
    app.text_input(key='recovery_email').input('not-an-email')
    app.button(key=SEND).click().run()
    client.request_recovery.assert_not_called()
    assert app.error


def test_send_code_provider_failure_is_shown_without_login(client):
    client.request_recovery.side_effect = AuthError('Authentication service unavailable. Please try again later.')
    app = AppTest.from_file(APP).run()
    app.text_input(key='recovery_email').input('a@example.com')
    app.button(key=SEND).click().run()
    assert not app.exception
    assert 'unavailable' in app.error[0].value
    assert not app.chat_input


def test_reset_password_success_requires_login_afterwards(client):
    app = AppTest.from_file(APP).run()
    fill_reset(app, code='123 456')
    app.button(key=RESET).click().run()
    assert not app.exception
    client.reset_password.assert_called_once_with('a@example.com', '123456', 'newpassword1')
    assert 'Password updated' in app.success[0].value
    assert not app.chat_input
    assert 'auth_token' not in app.session_state
    assert 'auth_user_id' not in app.session_state


@pytest.mark.parametrize('email,code,password,confirm', [
    ('bad', '123456', 'newpassword1', 'newpassword1'),
    ('a@example.com', 'abcdef', 'newpassword1', 'newpassword1'),
    ('a@example.com', '123', 'newpassword1', 'newpassword1'),
    ('a@example.com', '123456', 'short', 'short'),
    ('a@example.com', '123456', 'newpassword1', 'different1'),
])
def test_invalid_reset_values_do_not_reach_provider(client, email, code, password, confirm):
    app = AppTest.from_file(APP).run()
    fill_reset(app, email, code, password, confirm)
    app.button(key=RESET).click().run()
    client.reset_password.assert_not_called()
    assert app.error
    assert not app.chat_input


def test_wrong_code_shows_error_and_stays_logged_out(client):
    client.reset_password.side_effect = AuthError('That code is invalid or has expired. Request a new code and try again.')
    app = AppTest.from_file(APP).run()
    fill_reset(app)
    app.button(key=RESET).click().run()
    assert not app.exception
    assert 'invalid or has expired' in app.error[0].value
    assert not app.chat_input


def test_recovery_widgets_do_not_change_login_page_messages(client):
    app = AppTest.from_file(APP).run()
    assert not app.success and not app.error and not app.exception


@pytest.mark.parametrize('email', ['', 'x', 'a@b', ' @b.co'])
def test_validate_email_rejects_bad_values(email):
    with pytest.raises(AuthError):
        validate_email(email)


def test_validate_recovery_normalizes_email_and_code():
    assert validate_recovery(' a@b.co ', ' 12 34 56 ', 'password123', 'password123') == ('a@b.co', '123456')


def make_client():
    return AuthClient('https://example.supabase.co', 'sb_publishable_test')


def test_request_recovery_calls_recover_endpoint(monkeypatch):
    c = make_client()
    request = Mock(return_value={})
    monkeypatch.setattr(c, 'request', request)
    c.request_recovery('a@b.co')
    request.assert_called_once_with('recover', {'email': 'a@b.co'})


def test_reset_password_verifies_code_then_updates_then_signs_out(monkeypatch):
    c = make_client()
    request = Mock(side_effect=[{'access_token': 'recovery-token'}, {}])
    logout = Mock()
    monkeypatch.setattr(c, 'request', request)
    monkeypatch.setattr(c, 'logout', logout)
    c.reset_password('a@b.co', '123456', 'newpassword1')
    verify, update = request.call_args_list
    assert verify.args == ('verify', {'type': 'recovery', 'email': 'a@b.co', 'token': '123456'})
    assert update.args == ('user', {'password': 'newpassword1'})
    assert update.kwargs['token'] == 'recovery-token' and update.kwargs['method'] == 'PUT'
    logout.assert_called_once_with('recovery-token')


def test_reset_password_signs_out_even_when_update_fails(monkeypatch):
    c = make_client()
    request = Mock(side_effect=[{'access_token': 't'}, AuthError('not accepted')])
    logout = Mock(side_effect=AuthError('down'))
    monkeypatch.setattr(c, 'request', request)
    monkeypatch.setattr(c, 'logout', logout)
    with pytest.raises(AuthError, match='not accepted'):
        c.reset_password('a@b.co', '123456', 'newpassword1')
    logout.assert_called_once_with('t')


def test_reset_password_without_session_token_fails_closed(monkeypatch):
    c = make_client()
    request = Mock(return_value={})
    monkeypatch.setattr(c, 'request', request)
    with pytest.raises(AuthError):
        c.reset_password('a@b.co', '123456', 'newpassword1')
    assert request.call_count == 1


def test_update_uses_put_and_verify_failure_is_sanitized(monkeypatch):
    seen = []
    opener = Mock()

    def fake_open(req, timeout):
        seen.append((req.get_method(), req.full_url))
        raise HTTPError(req.full_url, 400, 'secret details', {}, BytesIO(b'secret'))

    opener.open.side_effect = fake_open
    monkeypatch.setattr('src.knowledge_assistant.auth.build_opener', lambda *a: opener)
    c = make_client()
    with pytest.raises(AuthError) as err:
        c.reset_password('a@b.co', '000000', 'newpassword1')
    assert seen == [('POST', 'https://example.supabase.co/auth/v1/verify')]
    assert 'invalid or has expired' in str(err.value) and 'secret' not in str(err.value)
    seen.clear()
    with pytest.raises(AuthError):
        c.request('user', {'password': 'x'}, token='t', method='PUT')
    assert seen == [('PUT', 'https://example.supabase.co/auth/v1/user')]
