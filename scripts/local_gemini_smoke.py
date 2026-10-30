"""Focused real-Gemini Streamlit smoke; never substitutes a synthetic answer.

Run with the project Python: python -m scripts.local_gemini_smoke
Successful saved workspaces are retained for local handover; no broad cleanup.
"""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import time
from urllib.parse import quote
from uuid import uuid4

from pypdf import PdfReader
from src.knowledge_assistant.auth import AuthClient, AuthError
from src.knowledge_assistant.persistence import WorkspaceStore
from scripts.local_test_app import (LocalSetupBlocked, LocalTestApp,
                                    load_local_configuration, load_test_credentials)

ROOT = Path(__file__).resolve().parents[1]
API = 'http://127.0.0.1:54321'
QUESTION = 'How many days of annual leave do employees receive?'


class Blocked(Exception):
    pass


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def verify_answer(messages, pdf):
    """Check this sample's answer and every saved passage against physical pages."""
    require(len(messages) == 2 and messages[0] == {'role': 'user', 'content': QUESTION},
            'Expected the real question and exactly one answer.')
    answer = messages[1]
    require(answer['role'] == 'assistant' and re.search(r'\b20\s+days\b', answer['content'], re.I),
            'The real answer must state the sample allowance.')
    require('Sources: leave.pdf, PDF page 1' in answer['content'], 'The sample citation is missing.')
    sources = answer.get('sources', [])
    require(bool(sources), 'Supporting passages are missing.')
    pages = PdfReader(pdf).pages
    normalize = lambda text: ' '.join(text.split())
    for source in sources:
        require(source['filename'] == 'leave.pdf' and type(source['page']) is int,
                'Source identity is invalid.')
        require(1 <= source['page'] <= len(pages), 'Source page is outside the PDF.')
        require(normalize(source['text']) in normalize(pages[source['page'] - 1].extract_text()),
                'Supporting passage does not occur on its cited page.')
    require(any(source['page'] == 1 and '20 days' in source['text'] for source in sources),
            'The sample supporting passage is missing.')


def main():
    from playwright.sync_api import expect, sync_playwright

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = ROOT / 'logs/local-verification' / ('gemini-smoke-' + stamp + '-' + uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    title = 'Live Gemini smoke ' + stamp + '-' + uuid4().hex[:8]
    evidence = {'result': 'INCOMPLETE', 'app_url': None, 'supabase_url': API,
                'workspace_title': title, 'workspace_id': None, 'checks': [],
                'answer_origin': 'Real Gemini through Streamlit; no fixture fallback'}
    page = browser = playwright = client = store = token = None
    app = None
    step, complete, failed = 'configuration', False, False
    sensitive = []

    def record():
        text = json.dumps(evidence, indent=2) + '\n'
        if any(secret and secret in text for secret in sensitive):
            raise RuntimeError('Secret boundary check failed; evidence not written.')
        (output / 'evidence.json').write_text(text, encoding='utf-8')

    def check(label, condition=True):
        require(condition, label)
        evidence['checks'].append(label)
        record()
        print('PASS:', label, flush=True)

    def settled():
        expect(page.get_by_test_id('stApp')).to_have_attribute('data-test-script-state', 'notRunning')

    def click(label):
        page.get_by_role('button', name=label, exact=True).click()

    def login():
        page.get_by_role('textbox', name='Email', exact=True).first.fill('qa-a@example.com')
        page.get_by_role('textbox', name='Password', exact=True).first.fill(credentials['password_a'])
        click('Log in')
        expect(page.get_by_role('button', name='Log out', exact=True)).to_be_visible(timeout=30000)

    def logout():
        click('Log out')
        expect(page.get_by_role('button', name='Log in', exact=True)).to_be_visible(timeout=30000)

    def saved_controls():
        settled()
        panel = page.get_by_test_id('stExpander').filter(has_text='Saved workspaces').first
        if panel.locator('details').get_attribute('open') is None:
            panel.locator('summary').click()

    def source_panel():
        panel = page.get_by_test_id('stExpander').filter(has_text='View supporting passages').first
        if panel.locator('details').get_attribute('open') is None:
            panel.locator('summary').click()
        expect(panel).to_contain_text('leave.pdf')
        expect(panel).to_contain_text('PDF page 1')
        expect(panel).to_contain_text('20 days')

    def wait_for_provider(predicate, seconds=160):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            if predicate():
                return
            alerts = ' '.join(page.get_by_test_id('stAlert').all_text_contents()).lower()
            for words, reason in [
                ('request limit', 'provider quota/rate limit'),
                ('credits are unavailable', 'provider quota unavailable'),
                ('api authentication failed', 'provider authentication'),
                ('ai processing failed', 'provider processing/access/network'),
            ]:
                if words in alerts:
                    raise Blocked(reason)
            page.wait_for_timeout(250)
        raise Blocked('provider operation did not complete within the smoke timeout')

    try:
        config = load_local_configuration(ROOT)
        if not all(config.get(name) for name in ('GEMINI_API_KEY', 'GEMINI_CHAT_MODEL', 'GEMINI_EMBEDDING_MODEL')):
            raise Blocked('missing local Gemini key/model configuration')
        credentials = load_test_credentials(ROOT, ('a',))
        sensitive = [config['GEMINI_API_KEY'], config['SUPABASE_PUBLISHABLE_KEY'],
                     *(value for value in credentials.values() if isinstance(value, str))]
        evidence['models'] = {name: config[name] for name in ('GEMINI_CHAT_MODEL', 'GEMINI_EMBEDDING_MODEL')}
        sample = ROOT / 'data/sample_pdfs/leave.pdf'
        evidence['sample_sha256'] = sha256(sample.read_bytes()).hexdigest()
        client = AuthClient(API, config['SUPABASE_PUBLISHABLE_KEY'])
        token, user = client.login('qa-a@example.com', credentials['password_a'])
        sensitive.append(token)
        store = WorkspaceStore(API, client.key, token, user['id'])
        check('Local Supabase and complete Gemini configuration confirmed')

        step = 'controlled local app startup'
        app = LocalTestApp(ROOT, output, config)
        app.start()
        evidence['app_url'] = app.url
        record()
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 1000})
        page.set_default_timeout(20000)
        step = 'A browser login and sample upload'
        page.goto(app.url)
        login()
        page.locator('input[type=file]').set_input_files(sample)
        consent = 'I agree to send these documents and questions to Google Gemini.'
        page.get_by_text(consent, exact=True).click()
        expect(page.get_by_role('checkbox', name=consent, exact=True)).to_be_checked()
        check('Sample PDF uploaded and Gemini consent enabled in the actual app')

        step = 'real Gemini indexing'
        expect(page.get_by_role('button', name='Index documents', exact=True)).to_be_enabled()
        click('Index documents')
        question = page.get_by_placeholder('Ask about your indexed PDFs')
        wait_for_provider(lambda: question.is_enabled())
        check('Real Gemini embeddings indexed the sample PDF')
        step = 'real Gemini answer'
        question.fill(QUESTION)
        question.press('Enter')
        wait_for_provider(lambda: page.get_by_test_id('stChatMessage').count() == 2)
        settled()
        source_panel()
        check('Real answer displays a PDF citation and supporting passage')
        page.screenshot(path=str(output / 'real-answer.png'), full_page=True)

        step = 'save real workspace and conversation'
        saved_controls()
        page.get_by_role('textbox', name='Workspace name', exact=True).fill(title)
        click('Save as new workspace')
        expect(page.get_by_text('Workspace saved to your account.', exact=True)).to_be_visible(timeout=30000)
        rows = store.request('/rest/v1/saved_workspaces?title=eq.' + quote(title, safe='') + '&select=*')
        require(len(rows) == 1 and rows[0]['status'] == 'ready', 'Expected one ready saved workspace.')
        evidence['workspace_id'] = rows[0]['id']
        evidence['workspace_retained_for_handover'] = True
        uploads, messages = store.load(rows[0]['id'])
        require(len(uploads) == 1 and uploads[0].data == sample.read_bytes(), 'The saved PDF changed.')
        verify_answer(messages, sample)
        transcript = json.dumps(messages, indent=2) + '\n'
        require(not any(secret and secret in transcript for secret in sensitive),
                'Secret boundary check failed; transcript not written.')
        (output / 'real-conversation.json').write_text(transcript, encoding='utf-8')
        check('UI save persisted exact PDF and real answer with valid page citations/passages')

        step = 'logout/login and restore real conversation'
        logout()
        check('A logged out after saving the real conversation')
        login()
        saved_controls()
        click('Refresh saved workspaces')
        settled()
        box = page.get_by_role('combobox', name='Choose saved workspace', exact=True)
        expect(box).to_be_visible()
        if not box.input_value().startswith(title):
            box.fill(title)
            box.press('ArrowDown')
            page.get_by_role('option').filter(has_text=title).click()
        expect(box).to_have_value(re.compile('^' + re.escape(title) + r'(?:\s|$)'))
        click('Open saved workspace')
        expect(page.get_by_test_id('stChatMessage')).to_have_count(2)
        settled()
        body = page.locator('body').inner_text()
        require(all(message['content'] in body for message in messages), 'The displayed conversation changed.')
        source_panel()
        restored_uploads, restored_messages = store.load(rows[0]['id'])
        require(restored_messages == messages and restored_uploads[0].data == sample.read_bytes(),
                'The restored conversation or PDF changed.')
        verify_answer(restored_messages, sample)
        check('Logout/login restore recovered the exact real answer, citations, passages and PDF')
        page.screenshot(path=str(output / 'restored-real-answer.png'), full_page=True)
        logout()
        check('Browser ended signed out; saved real workspace retained for handover')
        complete = True
    except Blocked as error:
        failed = True
        evidence['result'] = 'BLOCKED'
        evidence['blocker'] = {'step': step, 'reason': str(error)}
        print('BLOCKED:', step, '-', str(error), flush=True)
    except (LocalSetupBlocked, AuthError) as error:
        failed = True
        evidence['result'] = 'BLOCKED'
        evidence['blocker'] = {'step': step, 'type': type(error).__name__}
        print('BLOCKED:', step, '(' + type(error).__name__ + ')', flush=True)
    except Exception as error:
        failed = True
        evidence['result'] = 'FAIL'
        evidence['failure'] = {'step': step, 'type': type(error).__name__}
        print('FAIL:', step, '(' + type(error).__name__ + ')', flush=True)
    finally:
        # An evidence screenshot failure must not prevent the signout attempt.
        if failed and page is not None and not page.is_closed():
            try:
                page.screenshot(path=str(output / 'incomplete.png'), full_page=True)
            except Exception:
                evidence['failure_screenshot_unavailable'] = True
        if page is not None and not page.is_closed():
            try:
                page.keyboard.press('Escape')
                if page.get_by_role('button', name='Log out', exact=True).is_visible():
                    logout()
            except Exception:
                failed = True
                evidence['browser_signout_unconfirmed'] = True
        for resource, method in [(browser, 'close'), (playwright, 'stop')]:
            if resource is not None:
                try:
                    getattr(resource, method)()
                except Exception:
                    failed = True
                    evidence['browser_cleanup_unconfirmed'] = True
        if app is not None:
            try:
                app.stop()
            except Exception:
                failed = True
                evidence['child_app_shutdown_unconfirmed'] = True
        if client is not None and token:
            try:
                client.logout(token)
            except Exception:
                failed = True
                evidence['witness_signout_unconfirmed'] = True
        if complete and not failed:
            evidence['result'] = 'PASS'
        elif evidence['result'] == 'INCOMPLETE':
            evidence['result'] = 'FAIL / INCOMPLETE'
        record()
    print('RESULT:', evidence['result'], flush=True)
    print('Evidence:', output.relative_to(ROOT), flush=True)
    return 0 if evidence['result'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
