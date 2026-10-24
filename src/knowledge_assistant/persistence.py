"""Account-scoped workspace snapshots using the user's JWT and RLS."""
import json
from datetime import datetime, timezone
from uuid import uuid4, UUID
from urllib.request import Request, build_opener
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from .auth import AuthClient, NoRedirect
from .core import Upload, extract


class PersistenceError(Exception):
    pass


class WorkspaceStore:
    def __init__(self, url, key, token, user_id):
        config = AuthClient(url, key)
        self.url, self.key = config.url, config.key
        self.token, self.user_id = token, str(UUID(user_id))

    def request(self, path, method='GET', payload=None, binary=False):
        body = payload if binary else (json.dumps(payload).encode() if payload is not None else None)
        headers = {'apikey': self.key, 'Authorization': 'Bearer ' + self.token,
                   'Content-Type': 'application/pdf' if binary else 'application/json',
                   'Prefer': 'return=representation'}
        try:
            with build_opener(NoRedirect).open(Request(self.url + path, data=body,
                    headers=headers, method=method), timeout=45) as response:
                raw = response.read(105000000)
                return raw if binary and method == 'GET' else (json.loads(raw) if raw else None)
        except (HTTPError, URLError, OSError, ValueError):
            raise PersistenceError('Saved workspace service unavailable or access denied. Your current work is still in this session; sign in again if needed and retry.') from None

    def list(self):
        return self.request('/rest/v1/saved_workspaces?select=id,title,created_at,status&order=created_at.desc&limit=100')

    def save(self, title, uploads, messages):
        title = title.strip()
        if not 1 <= len(title) <= 120:
            raise PersistenceError('Enter a workspace name of 1–120 characters.')
        extract(uploads, 'save-validation')
        workspace_id, documents = str(uuid4()), []
        for upload in uploads:
            path = self.user_id + '/' + workspace_id + '/' + str(uuid4()) + '.pdf'
            documents.append({'name': upload.name, 'path': path})
        # Record every intended object first so interrupted saves remain recoverable.
        self.request('/rest/v1/saved_workspaces', 'POST', {
            'id': workspace_id, 'user_id': self.user_id, 'title': title,
            'documents': documents, 'messages': messages, 'status': 'saving'})
        try:
            for upload, doc in zip(uploads, documents):
                self.request('/storage/v1/object/user-documents/' + doc['path'],
                             'POST', upload.data, binary=True)
            rows = self.request('/rest/v1/saved_workspaces?id=eq.' + workspace_id + '&status=eq.saving',
                                'PATCH', {'status': 'ready'})
            if not rows:
                raise PersistenceError('Save interrupted. Refresh saved workspaces to clean up.')
        except PersistenceError:
            # Do not erase a possibly successful save after an ambiguous timeout.
            # Its recorded paths allow explicit cleanup from the workspace list.
            raise PersistenceError('Save could not be confirmed. Refresh saved workspaces: ready items can be opened; incomplete items can be deleted. Do not delete an item while another tab is saving it.') from None
        return workspace_id

    def load(self, workspace_id):
        rows = self.request('/rest/v1/saved_workspaces?id=eq.' + str(UUID(workspace_id)) + '&status=eq.ready&select=*')
        if len(rows) != 1:
            raise PersistenceError('This saved workspace is no longer available.')
        row, uploads = rows[0], []
        if len(row['documents']) > 10:
            raise PersistenceError('Saved workspace exceeds the document limit.')
        for doc in row['documents']:
            if not doc['path'].startswith(self.user_id + '/'):
                raise PersistenceError('Saved document ownership does not match.')
            data = self.request('/storage/v1/object/authenticated/user-documents/' + quote(doc['path'], safe='/'), binary=True)
            uploads.append(Upload(doc['name'], data))
        extract(uploads, 'restore-validation')
        return uploads, row['messages']

    def save_chat(self, workspace_id, messages):
        rows = self.request('/rest/v1/saved_workspaces?id=eq.' + str(UUID(workspace_id)) + '&status=eq.ready', 'PATCH', {
            'messages': messages, 'updated_at': datetime.now(timezone.utc).isoformat()})
        if not rows:
            raise PersistenceError('Chat was not saved. Save a new workspace and retry.')

    def delete(self, workspace_id):
        path = '/rest/v1/saved_workspaces?id=eq.' + str(UUID(workspace_id))
        rows = self.request(path, 'PATCH', {'status': 'deleting'})
        if not rows:
            return
        prefix = self.user_id + '/' + str(UUID(workspace_id)) + '/'
        paths = [d['path'] for d in rows[0]['documents']]
        if any(not p.startswith(prefix) for p in paths):
            raise PersistenceError('Document ownership does not match; deletion stopped.')
        # Remove binary objects through Storage, never by deleting storage SQL rows.
        # Keep the deleting record on failure so the user can retry safely.
        if paths:
            self.request('/storage/v1/object/user-documents', 'DELETE', {'prefixes': paths})
        self.request(path + '&status=eq.deleting', 'DELETE')
