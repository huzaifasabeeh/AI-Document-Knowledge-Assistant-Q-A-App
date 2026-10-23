"""Small Supabase Auth REST client; no shared clients, passwords or disk sessions."""
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler


class AuthError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class AuthClient:
    def __init__(self, url, key):
        parts = urlsplit(url)
        if (parts.scheme != 'https' or not parts.hostname or parts.username
                or parts.password or parts.query or parts.fragment
                or parts.path not in ('', '/')):
            raise AuthError('Authentication configuration is invalid. Contact the app owner.')
        # Use a publishable key or legacy anon key, never a privileged service key.
        if not key or key.startswith('sb_secret_'):
            raise AuthError('Authentication requires a public project key.')
        if not key.startswith('sb_publishable_'):
            import base64
            try:
                payload = key.split('.')[1]
                role = json.loads(base64.urlsafe_b64decode(payload + '=' * (-len(payload) % 4)))['role']
                if role != 'anon':
                    raise ValueError()
            except (ValueError, IndexError, KeyError, TypeError):
                raise AuthError('Authentication requires a publishable or anon key.') from None
        self.url, self.key = url.rstrip('/'), key

    def request(self, path, data=None, token=None):
        headers = {'apikey': self.key, 'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        req = Request(self.url + '/auth/v1/' + path, headers=headers,
                      data=json.dumps(data).encode() if data is not None else None,
                      method='POST' if data is not None else 'GET')
        try:
            with build_opener(NoRedirect).open(req, timeout=15) as response:
                raw = response.read()
                result = json.loads(raw) if raw else {}
                if not isinstance(result, dict):
                    raise ValueError()
                return result
        except HTTPError as exc:
            if exc.code == 429:
                message = 'Too many attempts. Please wait and try again.'
            elif exc.code in (400, 401, 403, 422):
                message = 'Authentication failed. Check your details and confirm your email, then retry.'
            else:
                message = 'Authentication service unavailable. Please try again later.'
            raise AuthError(message) from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise AuthError('Authentication service unavailable. Please try again later.') from None

    def signup(self, email, password):
        return self.request('signup', {'email': email, 'password': password})

    def login(self, email, password):
        result = self.request('token?grant_type=password', {'email': email, 'password': password})
        token = result.get('access_token')
        if not isinstance(token, str) or not token:
            raise AuthError('Sign-in did not complete. Please try again.')
        return token, self.user(token)

    def user(self, token):
        user = self.request('user', token=token)
        if not user.get('id') or not user.get('email_confirmed_at'):
            raise AuthError('Confirm your email before signing in.')
        return user

    def logout(self, token):
        self.request('logout?scope=local', {}, token)


def validate_credentials(email, password, confirmation=None):
    email = email.strip()
    if not re.fullmatch(r'[^\s@]+@[^\s@]+\.[^\s@]+', email) or not password:
        raise AuthError('Enter a valid email address and password.')
    if confirmation is not None:
        if len(password) < 8:
            raise AuthError('Use a password with at least 8 characters.')
        if password != confirmation:
            raise AuthError('Passwords do not match.')
    return email


def clear_session(state):
    """Drop all user state even if ephemeral index cleanup fails."""
    failed = False
    seen = set()
    for name in ('assistant', 'failed_engine'):
        engine = state.get(name)
        if engine is not None and id(engine) not in seen:
            seen.add(id(engine))
            try:
                engine.close()
            except Exception:
                failed = True
    state.clear()
    return failed
