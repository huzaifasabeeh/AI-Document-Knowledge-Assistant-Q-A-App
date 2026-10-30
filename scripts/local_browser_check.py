"""Opt-in local Streamlit browser acceptance; requires Playwright and local QA entry.

Run: python -m scripts.local_browser_check
No browser traces, session storage, passwords or provider keys are recorded.
"""
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import time
from uuid import uuid4
from urllib.parse import quote

from playwright.sync_api import sync_playwright, expect
from src.knowledge_assistant.auth import AuthClient, AuthError
from src.knowledge_assistant.persistence import WorkspaceStore
from scripts.local_test_app import (LocalSetupBlocked, LocalTestApp,
                                    load_local_configuration, load_test_credentials)

ROOT = Path(__file__).resolve().parents[1]
API = 'http://127.0.0.1:54321'
OUTPUT = ROOT / 'logs/local-verification'


def main():
    title = 'Local browser QA ' + uuid4().hex
    sample = ROOT / 'data/sample_pdfs/leave.pdf'
    output = OUTPUT / ('browser-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    evidence = {'app_url': None, 'workspace_title': title, 'checks': [], 'skips': [],
                'chat_origin': None, 'workspace_id': None, 'result': 'INCOMPLETE'}
    accounts, store, page, browser, playwright = [], None, None, None, None
    app = None
    step = 'setup'
    failed = False
    workflow_complete = False

    def record():
        (output / 'browser-evidence.json').write_text(json.dumps(evidence, indent=2) + '\n', encoding='utf-8')

    def check(label, condition=True):
        if not condition:
            raise AssertionError(label)
        evidence['checks'].append(label)
        record()
        print('PASS:', label, flush=True)

    def click(label):
        page.get_by_role('button', name=label, exact=True).click()

    def saved_controls():
        expect(page.get_by_test_id('stApp')).to_have_attribute('data-test-script-state', 'notRunning')
        panel = page.get_by_test_id('stExpander').filter(has_text='Saved workspaces').first
        details = panel.locator('details')
        if details.get_attribute('open') is None:
            panel.locator('summary').click()
        return panel

    def login(label):
        page.get_by_role('textbox', name='Email', exact=True).first.fill('qa-' + label + '@example.com')
        page.get_by_role('textbox', name='Password', exact=True).first.fill(credentials['password_' + label])
        click('Log in')
        expect(page.get_by_role('button', name='Log out', exact=True)).to_be_visible(timeout=30000)

    def logout():
        click('Log out')
        expect(page.get_by_role('button', name='Log in', exact=True)).to_be_visible(timeout=30000)
        expect(page.locator('input[type=file]')).to_have_count(0)

    def current_rows():
        return store.request('/rest/v1/saved_workspaces?title=eq.' + quote(title, safe='') + '&select=*')

    def choose_test_workspace():
        # This Streamlit version renders the selected label as an input value.
        # Refresh normally selects the newest item; verify it before acting.
        expect(page.get_by_test_id('stApp')).to_have_attribute('data-test-script-state', 'notRunning')
        box = page.get_by_role('combobox', name='Choose saved workspace', exact=True)
        expect(box).to_be_visible()
        if not box.input_value().startswith(title):
            box.fill(title)
            box.press('ArrowDown')
            page.get_by_role('option').filter(has_text=title).click()
        expect(box).to_have_value(re.compile('^' + re.escape(title) + r'(?:\s|$)'))
        expect(page.get_by_role('checkbox', name='Permanently delete: ' + title, exact=True)).to_be_attached()

    try:
        config = load_local_configuration(ROOT)
        credentials = load_test_credentials(ROOT, ('a', 'b'))
        client = AuthClient(API, config['SUPABASE_PUBLISHABLE_KEY'])
        # Independent user-token API witnesses observe UI writes; no privileged key.
        for label in ('a', 'b'):
            token, user = client.login('qa-' + label + '@example.com', credentials['password_' + label])
            accounts.append((token, user['id']))
        store = WorkspaceStore(API, client.key, *accounts[0])
        other = WorkspaceStore(API, client.key, *accounts[1])
        step = 'controlled local app startup'
        app = LocalTestApp(ROOT, output, config)
        app.start()
        evidence['app_url'] = app.url
        record()
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch()
        context = browser.new_context(accept_downloads=True, viewport={'width': 1440, 'height': 1000})
        page = context.new_page()
        page.set_default_timeout(20000)
        step = 'unauthenticated gate'
        page.goto(app.url)
        expect(page.get_by_role('button', name='Log in', exact=True)).to_be_visible(timeout=45000)
        check('Unauthenticated UI hides document controls', page.locator('input[type=file]').count() == 0)
        step = 'A login and upload'
        login('a')
        check('A logs in through Streamlit')
        page.locator('input[type=file]').set_input_files(sample)
        expect(page.get_by_role('button', name='Preview pages (no API)', exact=True)).to_be_enabled()
        click('Preview pages (no API)')
        expect(page.get_by_text('Local page preview', exact=False)).to_be_visible()
        check('Sample PDF upload and local page preview', '20 days' in page.locator('body').inner_text())
        step = 'save workspace'
        saved_controls()
        page.get_by_role('textbox', name='Workspace name', exact=True).fill(title)
        click('Save as new workspace')
        expect(page.get_by_text('Workspace saved to your account.', exact=True)).to_be_visible(timeout=30000)
        rows = current_rows()
        check('UI save creates a ready workspace row', len(rows) == 1 and rows[0]['status'] == 'ready'
              and len(rows[0]['documents']) == 1)
        row = rows[0]
        evidence['workspace_id'] = row['id']
        uploads, messages = store.load(row['id'])
        check('UI save persists exact PDF bytes', len(uploads) == 1 and uploads[0].data == sample.read_bytes())
        expect(page.locator('input[type=file]')).to_be_disabled()
        check('Saved workspace binds the uploaded document set')

        gemini_ready = all(config.get(name) for name in
            ('GEMINI_API_KEY', 'GEMINI_CHAT_MODEL', 'GEMINI_EMBEDDING_MODEL'))
        if gemini_ready:
            step = 'Gemini indexing and answer'
            page.get_by_role('checkbox', name='I agree to send these documents and questions to Google Gemini.', exact=True).check()
            click('Index documents')
            question = page.get_by_placeholder('Ask about your indexed PDFs')
            expect(question).to_be_enabled(timeout=180000)
            question.fill('How many days of annual leave do employees receive?')
            question.press('Enter')
            expect(page.get_by_test_id('stChatMessage')).to_have_count(2, timeout=180000)
            deadline = time.monotonic() + 30
            while True:
                _, messages = store.load(row['id'])
                if len(messages) == 2 or time.monotonic() >= deadline:
                    break
                page.wait_for_timeout(200)
            check('Gemini answer and supporting passages saved from UI', len(messages) == 2 and
                  messages[1].get('sources') and '20' in messages[1]['content'])
            evidence['chat_origin'] = 'Live Gemini answer through Streamlit'
        else:
            evidence['skips'].append('Live Gemini indexing/answer: key and model IDs unavailable')
            print('SKIP: Live Gemini indexing/answer; configuration unavailable.', flush=True)
            # Explicit fixture exercises storage/recovery/export without
            # presenting an authored transcript as a generated answer.
            messages = [
                {'role': 'user', 'content': '[Synthetic QA fixture] What is the annual leave allowance?'},
                {'role': 'assistant', 'content': '[Synthetic QA fixture; not AI generated] Employees receive 20 days of annual leave.',
                 'sources': [{'filename': 'leave.pdf', 'page': 1,
                              'text': 'Employees receive 20 days of annual leave.'}]},
            ]
            store.save_chat(row['id'], messages)
            evidence['chat_origin'] = 'Synthetic transcript seeded via authenticated WorkspaceStore.save_chat; no AI call'
            check('Synthetic chat fixture saved through user-token API')

        step = 'logout and restore: login'
        logout()
        check('Logout removes document controls')
        login('a')
        check('A logs back in through Streamlit')
        saved_controls()
        click('Refresh saved workspaces')
        step = 'logout and restore: select saved workspace'
        choose_test_workspace()
        expect(page.get_by_role('button', name='Open saved workspace', exact=True)).to_be_enabled()
        step = 'logout and restore: open saved workspace'
        click('Open saved workspace')
        expect(page.get_by_test_id('stChatMessage')).to_have_count(2)
        body = page.locator('body').inner_text()
        check('Saved chat recovered after logout/login', all(m['content'] in body for m in messages))
        expect(page.locator('input[type=file]')).to_be_disabled()
        click('Preview pages (no API)')
        expect(page.get_by_text('Local page preview', exact=False)).to_be_visible()
        check('Restored PDF can be previewed with page content', '20 days' in page.locator('body').inner_text())
        page.screenshot(path=str(output / 'restored-workspace.png'), full_page=True)

        step = 'export chat and sources'
        with page.expect_download() as received:
            click('Download chat and sources')
        download = received.value
        path = output / 'document-chat.txt'
        download.save_as(path)
        text = path.read_text(encoding='utf-8')
        check('Browser chat download includes messages and page sources', all(m['content'] in text for m in messages)
              and 'leave.pdf | PDF page 1' in text and messages[1]['sources'][0]['text'] in text)

        step = 'reset versus saved copy'
        click('Reset documents and chat')
        expect(page.get_by_test_id('stChatMessage')).to_have_count(0)
        expect(page.locator('input[type=file]')).to_be_enabled()
        uploads, recovered = store.load(row['id'])
        check('Reset clears UI and preserves saved PDF/chat', uploads[0].data == sample.read_bytes() and recovered == messages)
        saved_controls()
        click('Refresh saved workspaces')
        choose_test_workspace()
        click('Open saved workspace')
        expect(page.get_by_test_id('stChatMessage')).to_have_count(2)
        check('Saved copy reopens after reset')

        step = 'B account isolation'
        logout()
        login('b')
        saved_controls()
        click('Refresh saved workspaces')
        expect(page.get_by_role('button', name='Refresh saved workspaces', exact=True)).to_be_enabled()
        check('B cannot see A workspace in browser or user-token API', title not in page.locator('body').inner_text()
              and row['id'] not in {item['id'] for item in other.list()})
        check('A chat and document selection absent in B session', page.get_by_test_id('stChatMessage').count() == 0
              and page.get_by_test_id('stFileUploaderFile').count() == 0)

        step = 'A deletes workspace: logout B'
        logout()
        step = 'A deletes workspace: login A'
        login('a')
        saved_controls()
        click('Refresh saved workspaces')
        step = 'A deletes workspace: choose target'
        choose_test_workspace()
        step = 'A deletes workspace: confirm deletion'
        page.get_by_text('Permanently delete: ' + title, exact=True).click()
        expect(page.get_by_role('checkbox', name='Permanently delete: ' + title, exact=True)).to_be_checked()
        step = 'A deletes workspace: click delete'
        expect(page.get_by_role('button', name='Delete saved workspace', exact=True)).to_be_enabled()
        click('Delete saved workspace')
        step = 'A deletes workspace: confirm result'
        expect(page.get_by_text('Saved copy deleted.', exact=False)).to_be_visible(timeout=30000)
        check('A deletes saved workspace through UI', current_rows() == [])
        from scripts.local_access_check import LocalAPI
        witness = LocalAPI(client.key)
        absent = len(row['documents']) == 1 and all(witness('GET', '/storage/v1/object/authenticated/user-documents/' + doc['path'],
                             accounts[0][0])[0] in (400, 404) for doc in row['documents'])
        folder_empty = store.request('/storage/v1/object/list/user-documents', 'POST',
            {'prefix': accounts[0][1] + '/' + row['id'] + '/', 'limit': 100}) == []
        check('Deleted workspace PDF no longer downloads and folder is empty as owner', absent and folder_empty)
        saved_controls()
        click('Refresh saved workspaces')
        expect(page.get_by_role('checkbox', name='Permanently delete: ' + title, exact=True)).to_have_count(0)
        check('Deleted workspace absent after refreshing browser list', title not in page.locator('body').inner_text())
        logout()
        check('Browser test ends signed out')
        browser.close()
        workflow_complete = True
    except (LocalSetupBlocked, AuthError) as error:
        failed = True
        evidence['result'] = 'BLOCKED'
        # AuthError messages and local setup messages are deliberately generic.
        evidence['blocker'] = {'step': step, 'type': type(error).__name__}
        print('BLOCKED:', step, '(' + type(error).__name__ + ')', flush=True)
    except Exception as error:
        failed = True
        # Playwright exceptions can echo fill values. Never print exception text.
        evidence['failure'] = {'step': step, 'type': type(error).__name__}
        print('FAIL:', step, '(' + type(error).__name__ + ')', flush=True)
    finally:
        if failed and page is not None and not page.is_closed():
            try:
                page.screenshot(path=str(output / 'failure.png'), full_page=True)
            except Exception:
                pass
        if page is not None and not page.is_closed():
            try:
                page.keyboard.press('Escape')
                if page.get_by_role('button', name='Log out', exact=True).is_visible():
                    page.get_by_role('button', name='Log out', exact=True).click(timeout=5000)
                    expect(page.get_by_role('button', name='Log in', exact=True)).to_be_visible(timeout=10000)
            except Exception:
                failed = True
                print('FAIL: Browser session signout could not be confirmed', flush=True)
        if browser is not None:
            try:
                browser.close()
            except Exception:
                failed = True
                print('FAIL: Browser shutdown could not be confirmed', flush=True)
        if playwright is not None:
            try:
                playwright.stop()
            except Exception:
                failed = True
                print('FAIL: Browser driver shutdown could not be confirmed', flush=True)
        if app is not None:
            try:
                app.stop()
            except Exception:
                failed = True
                evidence['child_app_shutdown_unconfirmed'] = True
                print('FAIL: Controlled local app shutdown could not be confirmed', flush=True)
        if store is not None:
            try:
                for row in current_rows():
                    store.delete(row['id'])
                check('Final scoped workspace cleanup verified', current_rows() == [])
            except Exception:
                failed = True
                print('FAIL: Final scoped cleanup; reference:', title, flush=True)
        for token, _ in accounts:
            try:
                client.logout(token)
            except Exception:
                failed = True
                print('FAIL: API witness signout', flush=True)
        if evidence['result'] != 'BLOCKED':
            evidence['result'] = 'PASS' if workflow_complete and not failed else 'FAIL / INCOMPLETE'
        record()
    print('RESULT:', evidence['result'], flush=True)
    print('Evidence:', output.relative_to(ROOT), flush=True)
    return 0 if evidence['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
