"""Local-only two-account API smoke test. Run with Python; no dependencies."""
import getpass
import json
import uuid
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler
from urllib.error import HTTPError

BASE = 'http://127.0.0.1:54321'

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def main():
    pdf = (Path(__file__).resolve().parents[1] / 'data/sample_pdfs/leave.pdf').read_bytes()
    key = getpass.getpass('Local publishable key: ').strip()
    if not key.startswith('sb_publishable_'):
        print('STOP: Use the local publishable key, not a secret/service-role key.')
        return 1
    http = build_opener(ProxyHandler({}), NoRedirect())
    failures = []

    def api(method, path, token=None, data=None):
        headers = {'apikey': key, 'Prefer': 'return=representation'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        raw = isinstance(data, bytes)
        headers['Content-Type'] = 'application/pdf' if raw else 'application/json'
        body = data if raw else json.dumps(data).encode() if data is not None else None
        try:
            with http.open(Request(BASE + path, data=body, headers=headers, method=method), timeout=30) as r:
                return r.status, r.read()
        except HTTPError as e:
            return e.code, e.read()

    def check(label, passed):
        print(('PASS: ' if passed else 'FAIL: ') + label)
        if not passed:
            failures.append(label)

    def login(email):
        s, b = api('POST', '/auth/v1/token?grant_type=password', data={
            'email': email, 'password': getpass.getpass(email + ' password: ')})
        if s != 200:
            raise RuntimeError('Login HTTP ' + str(s))
        result = json.loads(b)
        check('Login ' + email, True)
        return result['access_token'], str(uuid.UUID(result['user']['id']))

    def test(owner, other, label):
        token, uid = owner
        oid = str(uuid.uuid4())
        row = '/rest/v1/saved_workspaces?id=eq.' + oid
        bucket = '/storage/v1/object/user-documents'
        name = uid + '/' + oid + '/test.pdf'
        download = '/storage/v1/object/authenticated/user-documents/' + name
        try:
            s, _ = api('POST', '/rest/v1/saved_workspaces', token,
                       {'id': oid, 'user_id': uid, 'title': 'Temporary API test'})
            if s != 201:
                raise RuntimeError('Workspace creation HTTP ' + str(s))
            for method, data in [('GET', None), ('PATCH', {'title': 'Unauthorized'}), ('DELETE', None)]:
                s, b = api(method, row, other[0], data)
                check(label + ' other account blocked: ' + method, s == 200 and json.loads(b) == [])
            s, b = api('GET', row, token)
            rows = json.loads(b) if s == 200 else []
            check(label + ' own row unchanged', len(rows) == 1 and rows[0]['title'] == 'Temporary API test')
            s, _ = api('POST', bucket + '/' + name, token, pdf)
            if s not in (200, 201):
                raise RuntimeError('PDF upload HTTP ' + str(s))
            s, b = api('GET', download, token)
            check(label + ' own PDF download', s == 200 and b == pdf)
            s, _ = api('GET', download, other[0])
            check(label + ' other PDF download denied', s in (400, 403, 404))
            s, b = api('DELETE', bucket, other[0], {'prefixes': [name]})
            check(label + ' other PDF delete blocked', s in (403, 404) or (s == 200 and json.loads(b) == []))
            s, b = api('GET', download, token)
            check(label + ' PDF remains intact', s == 200 and b == pdf)
        finally:
            for title, path, data in [('PDF', bucket, {'prefixes': [name]}), ('workspace', row, None)]:
                try:
                    s, _ = api('DELETE', path, token, data)
                    check(label + ' cleanup ' + title, s in (200, 204))
                except Exception:
                    check(label + ' cleanup ' + title, False)
                    print('Manual cleanup reference:', oid)
    try:
        a, b = login('qa-a@example.com'), login('qa-b@example.com')
        if a[1] == b[1]:
            raise RuntimeError('Distinct accounts required')
        test(a, b, 'A')
        test(b, a, 'B')
    except Exception as error:
        failures.append('Interrupted')
        print('STOP:', str(error) if isinstance(error, RuntimeError) else type(error).__name__)
    print('RESULT:', 'FAIL / INCOMPLETE' if failures else 'PASS')
    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
