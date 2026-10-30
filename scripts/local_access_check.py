"""Local-only two-account API checks; public key and user tokens only."""
import argparse
import getpass
import json
import tomllib
import uuid
from pathlib import Path
from urllib.request import Request, build_opener, ProxyHandler, HTTPRedirectHandler
from urllib.error import HTTPError

BASE = 'http://127.0.0.1:54321'
ROOT = Path(__file__).resolve().parents[1]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


class LocalAPI:
    def __init__(self, key):
        if not key.startswith('sb_publishable_'):
            raise RuntimeError('Use the local publishable key, never a privileged key.')
        self.key = key
        self.http = build_opener(ProxyHandler({}), NoRedirect())

    def __call__(self, method, path, token=None, data=None):
        headers = {'apikey': self.key, 'Prefer': 'return=representation'}
        if token:
            headers['Authorization'] = 'Bearer ' + token
        raw = isinstance(data, bytes)
        headers['Content-Type'] = 'application/pdf' if raw else 'application/json'
        body = data if raw else json.dumps(data).encode() if data is not None else None
        try:
            with self.http.open(Request(BASE + path, data=body, headers=headers, method=method), timeout=30) as response:
                return response.status, response.read()
        except HTTPError as error:
            return error.code, error.read()


def run_checks(key, passwords):
    pdf = (ROOT / 'data/sample_pdfs/leave.pdf').read_bytes()
    api, failures, accounts = LocalAPI(key), [], []

    def check(label, passed):
        print(('PASS: ' if passed else 'FAIL: ') + label, flush=True)
        if not passed:
            failures.append(label)

    def rows(method, path, token, data=None):
        status, body = api(method, path, token, data)
        return status, json.loads(body)

    def test(owner, other, label):
        token, uid = owner
        other_token, other_uid = other
        oid, forged_id, anonymous_id = (str(uuid.uuid4()) for _ in range(3))
        table = '/rest/v1/saved_workspaces'
        row = table + '?id=eq.' + oid
        bucket = '/storage/v1/object/user-documents'
        name = uid + '/' + oid + '/test.pdf'
        forged_name = other_uid + '/' + oid + '/forged.pdf'
        anonymous_name = uid + '/' + oid + '/anonymous.pdf'

        def download(path, who):
            return api('GET', '/storage/v1/object/authenticated/user-documents/' + path, who)

        try:
            status, _ = api('POST', table, token,
                            {'id': oid, 'user_id': uid, 'title': 'Temporary API test'})
            if status != 201:
                raise RuntimeError('Workspace creation HTTP ' + str(status))
            status, own = rows('GET', row, token)
            check(label + ' own row readable', status == 200 and len(own) == 1 and own[0]['user_id'] == uid)
            for method, data in [('GET', None), ('PATCH', {'title': 'Unauthorized'}), ('DELETE', None)]:
                status, result = rows(method, row, other_token, data)
                check(label + ' other account blocked: ' + method, status == 200 and result == [])

            status, _ = api('POST', table, token,
                            {'id': forged_id, 'user_id': other_uid, 'title': 'Forged owner test'})
            check(label + ' forged insert denied', status in (401, 403))
            status, result = rows('GET', table + '?id=eq.' + forged_id, other_token)
            check(label + ' forged row absent for intended owner', status == 200 and result == [])
            status, _ = api('PATCH', row, token, {'user_id': other_uid})
            check(label + ' ownership reassignment denied', status in (401, 403))

            for method, data, target in [
                ('GET', None, row), ('PATCH', {'title': 'Anonymous'}, row), ('DELETE', None, row),
                ('POST', {'id': anonymous_id, 'user_id': uid, 'title': 'Anonymous test'}, table),
            ]:
                status, _ = api(method, target, data=data)
                check(label + ' unauthenticated workspace denied: ' + method, status in (401, 403))
            status, result = rows('GET', row, token)
            check(label + ' own row unchanged', status == 200 and len(result) == 1 and
                  result[0]['title'] == 'Temporary API test' and result[0]['user_id'] == uid)

            status, _ = api('POST', bucket + '/' + name, token, pdf)
            if status not in (200, 201):
                raise RuntimeError('PDF upload HTTP ' + str(status))
            status, body = download(name, token)
            check(label + ' own PDF download', status == 200 and body == pdf)
            status, _ = download(name, other_token)
            check(label + ' other PDF download denied', status in (400, 401, 403, 404))
            status, body = api('DELETE', bucket, other_token, {'prefixes': [name]})
            check(label + ' other PDF delete blocked', status in (401, 403, 404) or
                  (status == 200 and json.loads(body) == []))
            status, _ = api('POST', bucket + '/' + forged_name, token, pdf)
            check(label + ' upload into other folder denied', status in (400, 401, 403))
            status, _ = download(forged_name, other_token)
            check(label + ' forged PDF absent for folder owner', status in (400, 404))

            status, _ = download(name, None)
            check(label + ' unauthenticated PDF download denied', status in (400, 401, 403, 404))
            status, _ = api('GET', '/storage/v1/object/public/user-documents/' + name)
            check(label + ' private PDF public route denied', status in (400, 401, 403, 404))
            status, _ = api('POST', bucket + '/' + anonymous_name, data=pdf)
            check(label + ' unauthenticated upload denied', status in (400, 401, 403))
            status, body = api('DELETE', bucket, data={'prefixes': [name]})
            check(label + ' unauthenticated PDF delete blocked', status in (400, 401, 403, 404) or
                  (status == 200 and json.loads(body) == []))
            status, body = download(name, token)
            check(label + ' PDF remains intact', status == 200 and body == pdf)
        finally:
            # Both user tokens clean up only this run's exact UUIDs/paths,
            # including any unexpectedly successful forgery.
            cleanup_ok = True
            for account_token, _ in (owner, other):
                for path in (name, forged_name, anonymous_name):
                    try:
                        status, _ = api('DELETE', bucket, account_token, {'prefixes': [path]})
                        cleanup_ok &= status in (200, 204)
                    except Exception:
                        cleanup_ok = False
                for resource_id in (oid, forged_id, anonymous_id):
                    try:
                        status, _ = api('DELETE', table + '?id=eq.' + resource_id, account_token)
                        cleanup_ok &= status in (200, 204)
                    except Exception:
                        cleanup_ok = False
            for account_token, _ in (owner, other):
                for resource_id in (oid, forged_id, anonymous_id):
                    try:
                        status, result = rows('GET', table + '?id=eq.' + resource_id, account_token)
                        cleanup_ok &= status == 200 and result == []
                    except Exception:
                        cleanup_ok = False
            for path, folder_token in [(name, token), (forged_name, other_token), (anonymous_name, token)]:
                try:
                    status, _ = download(path, folder_token)
                    cleanup_ok &= status in (400, 404)
                except Exception:
                    cleanup_ok = False
            check(label + ' cleanup verified: rows and PDFs absent', cleanup_ok)
            if not cleanup_ok:
                print('Manual cleanup references:', oid, forged_id, anonymous_id)

    try:
        for label, email in [('a', 'qa-a@example.com'), ('b', 'qa-b@example.com')]:
            status, body = api('POST', '/auth/v1/token?grant_type=password', data={
                'email': email, 'password': passwords[label]})
            if status != 200:
                raise RuntimeError('Login HTTP ' + str(status))
            result = json.loads(body)
            accounts.append((result['access_token'], str(uuid.UUID(result['user']['id']))))
            check('Login ' + email, True)
        if accounts[0][1] == accounts[1][1]:
            raise RuntimeError('Distinct accounts required')
        test(accounts[0], accounts[1], 'A')
        test(accounts[1], accounts[0], 'B')
    except Exception as error:
        failures.append('Interrupted')
        print('STOP:', str(error) if isinstance(error, RuntimeError) else type(error).__name__)
    finally:
        for token, _ in accounts:
            try:
                status, _ = api('POST', '/auth/v1/logout?scope=local', token, {})
                check('Test session signed out', status in (200, 204))
            except Exception:
                check('Test session signed out', False)
    print('RESULT:', 'FAIL / INCOMPLETE' if failures else 'PASS')
    return 1 if failures else 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--credentials-file', type=Path,
                        help='Gitignored local JSON with password_a and password_b; no secrets on command line.')
    args = parser.parse_args()
    if args.credentials_file:
        config = tomllib.loads((ROOT / '.streamlit/secrets.toml').read_text(encoding='utf-8'))
        if config.get('SUPABASE_URL') != BASE:
            raise RuntimeError('Only the fixed local API is supported.')
        key = config['SUPABASE_PUBLISHABLE_KEY']
        local = json.loads(args.credentials_file.read_text(encoding='utf-8'))
        passwords = {'a': local['password_a'], 'b': local['password_b']}
    else:
        key = getpass.getpass('Local publishable key: ').strip()
        passwords = {label: getpass.getpass(email + ' password: ') for label, email in
                     [('a', 'qa-a@example.com'), ('b', 'qa-b@example.com')]}
    return run_checks(key, passwords)


if __name__ == '__main__':
    raise SystemExit(main())
