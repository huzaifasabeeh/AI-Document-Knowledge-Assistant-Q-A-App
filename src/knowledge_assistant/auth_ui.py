"""Fail-closed account gate. No document/chat persistence is added here."""
import os
import streamlit as st
from .auth import AuthClient, AuthError, clear_session, validate_credentials


def setting(name):
    value = os.environ.get(name)
    if value:
        return value.strip()
    try:
        return str(st.secrets.get(name, '')).strip()
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        return ''


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
    if token:
        # Logout is offered before validation so outages cannot trap local data.
        if st.sidebar.button('Log out', key='logout'):
            remote_failed = False
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
            cleanup_failed = clear_session(st.session_state)
            st.session_state.auth_notice = str(exc)
            if cleanup_failed:
                st.session_state.auth_notice += ' Index cleanup failed; contact the app owner.'
            st.rerun()
        st.sidebar.caption('Signed in as ' + user.get('email', 'your account'))
        return user['id']

    st.title('Welcome to Document Knowledge Assistant')
    st.caption('Sign in to work with your documents. Documents and chats are temporary in this version.')
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
                st.session_state.auth_token = token
                st.session_state.auth_user_id = user['id']
                st.rerun()
            except AuthError as exc:
                st.error(str(exc))
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
