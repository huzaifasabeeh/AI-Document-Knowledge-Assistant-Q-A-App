"""Fail-closed account gate. No document/chat persistence is added here."""
import os
import secrets
import time
import streamlit as st
from .auth import (AuthClient, AuthError, RECOVERY_SENT, clear_session, validate_credentials,
                   validate_email, validate_recovery)

_ACTIVE_SESSIONS = {}


def _clean_sessions():
    now = time.time()
    stale = [k for k, v in _ACTIVE_SESSIONS.items() if now - v.get('created_at', 0) > 86400 * 7]
    for k in stale:
        _ACTIVE_SESSIONS.pop(k, None)


def setting(name):
    value = os.environ.get(name)
    if value:
        return value.strip()
    try:
        return str(st.secrets.get(name, '')).strip()
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ''


def password_recovery(client):
    """Email-code password reset. Never signs the user in or keeps a recovery token."""
    with st.expander('Forgot your password?'):
        st.caption('We will email a one-time code. Enter it below with a new password.')
        with st.form('recovery_request_form', clear_on_submit=True):
            email = st.text_input('Email', key='recovery_email')
            send = st.form_submit_button('Send reset code')
        if send:
            try:
                client.request_recovery(validate_email(email))
                st.success(RECOVERY_SENT)  # Same message whether or not the account exists.
            except AuthError as exc:
                st.error(str(exc))
        with st.form('recovery_reset_form', clear_on_submit=True):
            email = st.text_input('Email', key='reset_email')
            code = st.text_input('Code from email', key='reset_code')
            password = st.text_input('New password', type='password', key='reset_password')
            confirmation = st.text_input('Confirm new password', type='password', key='reset_confirm')
            reset = st.form_submit_button('Set new password')
        if reset:
            try:
                email, code = validate_recovery(email, code, password, confirmation)
                client.reset_password(email, code, password)
                st.success('Password updated. Use Log in with your new password.')
            except AuthError as exc:
                st.error(str(exc))


def require_login():
    url, key = setting('SUPABASE_URL'), setting('SUPABASE_PUBLISHABLE_KEY')
    if not url or not key:
        st.title('Document Knowledge Assistant')
        st.info('Account sign-in is not configured yet. Please contact the app owner.')
        st.stop()
    try:
        client = AuthClient(url, key)
    except AuthError as exc:
        st.error(str(exc))
        st.stop()

    token = st.session_state.get('auth_token')
    if not token and hasattr(st, 'query_params') and 'session' in st.query_params:
        session_id = st.query_params.get('session')
        cached = _ACTIVE_SESSIONS.get(session_id)
        if cached and time.time() - cached.get('created_at', 0) < 86400 * 7:
            try:
                user = client.user(cached['token'])
                st.session_state.auth_token = cached['token']
                st.session_state.auth_user_id = user['id']
                token = cached['token']
            except AuthError:
                _ACTIVE_SESSIONS.pop(session_id, None)
                st.query_params.pop('session', None)
    if token:
        # Logout is offered before validation so outages cannot trap local data.
        if st.sidebar.button('Log out', key='logout'):
            remote_failed = False
            if hasattr(st, 'query_params') and 'session' in st.query_params:
                session_id = st.query_params.pop('session', None)
                _ACTIVE_SESSIONS.pop(session_id, None)
            try:
                client.logout(token)
            except AuthError:
                remote_failed = True
            cleanup_failed = clear_session(st.session_state)
            st.session_state.auth_notice = (
                'Signed out locally. Remote sign-out could not be confirmed.' if remote_failed
                else 'You have been signed out.')
            if cleanup_failed:
                st.session_state.auth_notice += ' Index cleanup failed; contact the owner to restart the server.'
            st.rerun()
        try:
            user = client.user(token)  # Validate with the provider on every workspace rerun.
            if user['id'] != st.session_state.get('auth_user_id'):
                raise AuthError('Account changed. Please sign in again.')
        except AuthError as exc:
            if hasattr(st, 'query_params') and 'session' in st.query_params:
                session_id = st.query_params.pop('session', None)
                _ACTIVE_SESSIONS.pop(session_id, None)
            cleanup_failed = clear_session(st.session_state)
            st.session_state.auth_notice = str(exc)
            if cleanup_failed:
                st.session_state.auth_notice += ' Index cleanup failed; contact the app owner.'
            st.rerun()
        st.sidebar.caption('Signed in as ' + user.get('email', 'your account'))
        return user['id']

    st.title('Welcome to Document Knowledge Assistant')
    st.caption('Sign in to work with your documents. Save a workspace to keep PDFs and chat history in your account.')
    notice = st.session_state.pop('auth_notice', None)
    if notice:
        st.info(notice)
    login, signup = st.tabs(['Log in', 'Sign up'])
    with login:
        with st.form('login_form', clear_on_submit=True):
            email = st.text_input('Email', key='login_email')
            password = st.text_input('Password', type='password', key='login_password')
            submit = st.form_submit_button('Log in')
        if submit:
            try:
                email = validate_credentials(email, password)
                token, user = client.login(email, password)
                clear_session(st.session_state)
                _clean_sessions()
                session_id = secrets.token_urlsafe(32)
                _ACTIVE_SESSIONS[session_id] = {'token': token, 'user_id': user['id'], 'created_at': time.time()}
                if hasattr(st, 'query_params'):
                    st.query_params['session'] = session_id
                st.session_state.auth_token = token
                st.session_state.auth_user_id = user['id']
                st.rerun()
            except AuthError as exc:
                st.error(str(exc))
        password_recovery(client)
    with signup:
        with st.form('signup_form', clear_on_submit=True):
            email = st.text_input('Email', key='signup_email')
            password = st.text_input('Password', type='password', key='signup_password')
            confirmation = st.text_input('Confirm password', type='password', key='signup_confirm')
            submit = st.form_submit_button('Create account')
        if submit:
            try:
                email = validate_credentials(email, password, confirmation)
                result = client.signup(email, password)
                # Even with confirmation disabled, do not keep signup session tokens.
                if result.get('access_token'):
                    client.logout(result['access_token'])
                st.success('Request received. Check your email for a confirmation link if required, then use Log in. If you already have an account, log in instead.')
            except AuthError as exc:
                st.error(str(exc))
    st.stop()
