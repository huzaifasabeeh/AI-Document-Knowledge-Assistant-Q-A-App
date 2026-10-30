"""Focused real-Gemini Streamlit smoke; never substitutes a synthetic answer.

Run with the project Python: python -m scripts.local_gemini_smoke
Successful saved workspaces are retained for local handover; no broad cleanup.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
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
SECOND_QUESTION = 'Who must approve leave requests?'
THIRD_QUESTION = 'What is the annual leave entitlement stated in the PDF?'
CONVERSATION_CASES = (
    (QUESTION, r'\b20\s+days\b', 1, '20 days'),
    (SECOND_QUESTION, r'\bmanager\b', 2, 'manager approval'),
    (THIRD_QUESTION, r'\b20\s+days\b', 1, '20 days'),
)


class Blocked(Exception):
    pass


def require(condition, label):
    if not condition:
        raise AssertionError(label)


def verify_answer(messages, pdf, case=CONVERSATION_CASES[0]):
    """Check this sample's answer and every saved passage against physical pages."""
    question, pattern, required_page, required_passage = case
    require(len(messages) == 2 and messages[0] == {'role': 'user', 'content': question},
            'Expected the real question and exactly one answer.')
    answer = messages[1]
    require(answer['role'] == 'assistant' and re.search(pattern, answer['content'], re.I),
            'The real answer must state the sample allowance or approval requirement.')
    require('Sources:' in answer['content'] and
            f'leave.pdf, PDF page {required_page}' in answer['content'], 'The sample citation is missing.')
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
    require(any(source['page'] == required_page and required_passage in source['text'] for source in sources),
            'The sample supporting passage is missing.')


def verify_conversation(messages, pdf, cases):
    require(len(messages) == 2 * len(cases), 'The saved conversation has a missing or extra turn.')
    for index, case in enumerate(cases):
        verify_answer(messages[2 * index:2 * index + 2], pdf, case)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--conversation-persistence', action='store_true',
                        help='Also verify subsequent-turn autosave and asking after restored-PDF reindexing.')
    args = parser.parse_args()
    from playwright.sync_api import expect, sync_playwright

    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = ROOT / 'logs/local-verification' / ('gemini-smoke-' + stamp + '-' + uuid4().hex[:8])
    output.mkdir(parents=True, exist_ok=False)
    title = ('Gemini conversation persistence ' if args.conversation_persistence else 'Live Gemini smoke ') + stamp + '-' + uuid4().hex[:8]
    evidence = {'result': 'INCOMPLETE', 'app_url': None, 'supabase_url': API,
                'workspace_title': title, 'workspace_id': None, 'checks': [],
                'answer_origin': 'Real Gemini through Streamlit; no fixture fallback'}
    evidence['mode'] = 'conversation-persistence' if args.conversation_persistence else 'one-turn'
    evidence['tested_revision'] = subprocess.run(
        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()
    # Hash actual executable sources as well as HEAD: a live run may include an
    # uncommitted harness change. Do not describe that as a clean revision test.
    paths = [ROOT / 'app.py', *sorted((ROOT / 'src/knowledge_assistant').glob('*.py')),
             Path(__file__).resolve(), ROOT / 'scripts/local_test_app.py']
    evidence['source_sha256'] = {path.relative_to(ROOT).as_posix(): sha256(path.read_bytes()).hexdigest()
                                 for path in paths}
    evidence['tracked_changes'] = subprocess.run(
        ['git', 'diff', '--name-only', 'HEAD'], cwd=ROOT, capture_output=True, text=True,
        check=True).stdout.splitlines()
    page = browser = playwright = client = store = token = None
    app = None
    step, complete, failed = 'configuration', False, False
    sensitive = []
    original_rows = None
    original_pdfs = {}

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

    def displayed_conversation():
        """Read actual rendered answers and sources, independently of the DB."""
        messages = []
        cards = page.get_by_test_id('stChatMessage')
        for index in range(cards.count()):
            card = cards.nth(index)
            message = {'role': 'user' if index % 2 == 0 else 'assistant',
                       'content': card.get_by_test_id('stText').first.inner_text()}
            if index % 2:
                panel = card.get_by_test_id('stExpander').filter(has_text='View supporting passages')
                expect(panel).to_have_count(1)
                if panel.locator('details').get_attribute('open') is None:
                    panel.locator('summary').click()
                captions = panel.get_by_test_id('stCaptionContainer').all_text_contents()
                passages = panel.get_by_test_id('stText').all_text_contents()
                require(len(captions) == len(passages) and bool(passages),
                        'The displayed answer is missing source identities or passages.')
                sources = []
                for caption, passage in zip(captions, passages):
                    match = re.fullmatch(r'(.+)\s+·\s+PDF page (\d+)', caption.strip())
                    require(match is not None, 'The displayed source identity is invalid.')
                    sources.append({'filename': match[1], 'page': int(match[2]), 'text': passage})
                message['sources'] = sources
            messages.append(message)
        return messages

    def snapshot(label, messages):
        text = json.dumps(messages, indent=2) + '\n'
        require(not any(secret and secret in text for secret in sensitive),
                'Secret boundary check failed; transcript not written.')
        (output / (label + '.json')).write_text(text, encoding='utf-8')
        evidence.setdefault('transcript_sha256', {})[label] = sha256(text.encode()).hexdigest()

    def verify_saved(messages):
        uploads, saved = store.load(evidence['workspace_id'])
        require(len(uploads) == 1 and uploads[0].data == sample.read_bytes(), 'The saved PDF changed.')
        require(saved == messages, 'Automatic save did not persist the exact displayed conversation and sources.')

    def pdf_fingerprints(workspace_id):
        uploads, _ = store.load(workspace_id)
        return [{'name': upload.name, 'sha256': sha256(upload.data).hexdigest()} for upload in uploads]

    def restore(messages):
        logout()
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
        expect(page.get_by_test_id('stChatMessage')).to_have_count(len(messages))
        settled()
        require(displayed_conversation() == messages, 'Restore changed displayed messages or source records.')
        expect(page.get_by_placeholder('Ask about your indexed PDFs')).to_be_disabled()
        verify_saved(messages)

    def ask(case, previous):
        question = page.get_by_placeholder('Ask about your indexed PDFs')
        expect(question).to_be_enabled()
        question.fill(case[0])
        question.press('Enter')
        wait_for_provider(lambda: page.get_by_test_id('stChatMessage').count() == len(previous) + 2)
        settled()
        messages = displayed_conversation()
        require(messages[:-2] == previous, 'A subsequent question changed an earlier conversation turn.')
        verify_conversation(messages, sample, CONVERSATION_CASES[:len(messages) // 2])
        # Deliberately no Save chat now: this read must witness automatic saving.
        verify_saved(messages)
        return messages

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
        if args.conversation_persistence:
            # Read-only fingerprints ensure pre-existing workspaces, including
            # the retained review workspace, remain byte-for-byte unchanged.
            rows = store.request('/rest/v1/saved_workspaces?select=*')
            original_rows = {row['id']: row for row in rows}
            evidence['preexisting_workspace_count'] = len(original_rows)
            evidence['preexisting_rows_sha256'] = sha256(json.dumps(
                original_rows, sort_keys=True).encode()).hexdigest()
            require(not any(row['title'] == title for row in rows), 'The unique test workspace already exists.')
            original_pdfs = {key: pdf_fingerprints(key) for key, row in original_rows.items()
                             if row['status'] == 'ready'}
            evidence['preexisting_pdfs_sha256'] = sha256(json.dumps(
                original_pdfs, sort_keys=True).encode()).hexdigest()
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
        require(displayed_conversation() == messages, 'UI save changed the displayed conversation or sources.')
        snapshot('real-conversation', messages)
        check('UI save persisted exact PDF and real answer with valid page citations/passages')

        if args.conversation_persistence:
            step = 'subsequent real question and automatic save'
            messages = ask(CONVERSATION_CASES[1], messages)
            snapshot('two-turn-conversation', messages)
            check('Second real Gemini answer and sources automatically saved to the same workspace')
            page.screenshot(path=str(output / 'two-turn-answer.png'), full_page=True)

            step = 'first logout/login and exact two-turn restore'
            restore(messages)
            check('First logout/login restored both exact turns, sources and PDF; chat required reindexing')
            page.screenshot(path=str(output / 'restored-two-turns.png'), full_page=True)

            step = 'reindex restored PDF without changing recovered conversation'
            consent = 'I agree to send these documents and questions to Google Gemini.'
            page.get_by_text(consent, exact=True).click()
            expect(page.get_by_role('checkbox', name=consent, exact=True)).to_be_checked()
            click('Index documents')
            wait_for_provider(lambda: page.get_by_placeholder('Ask about your indexed PDFs').is_enabled())
            settled()
            require(displayed_conversation() == messages, 'Reindexing changed the recovered conversation or sources.')
            verify_saved(messages)
            check('Real Gemini reindexing of the restored PDF preserved both saved turns and sources')

            step = 'new question after restore/reindex and automatic save'
            messages = ask(CONVERSATION_CASES[2], messages)
            snapshot('three-turn-conversation', messages)
            check('New real answer after restored-PDF reindexing automatically saved with all three turns')
            page.screenshot(path=str(output / 'three-turn-answer.png'), full_page=True)

            step = 'second logout/login and exact three-turn restore'
            restore(messages)
            verify_conversation(messages, sample, CONVERSATION_CASES)
            snapshot('restored-three-turn-conversation', displayed_conversation())
            check('Second logout/login recovered all three exact real turns, citations, passages and PDF')
            page.screenshot(path=str(output / 'restored-three-turns.png'), full_page=True)
            logout()
            check('Browser ended signed out; unique conversation workspace retained for review')
            complete = True

        if not args.conversation_persistence:
            step = 'logout/login and restore real conversation'
            restore(messages)
            verify_answer(messages, sample)
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
        if original_rows is not None:
            try:
                current = {row['id']: row for row in store.request('/rest/v1/saved_workspaces?select=*')}
                require(all(current.get(key) == row for key, row in original_rows.items()),
                        'A pre-existing workspace changed during focused verification.')
                require(all(pdf_fingerprints(key) == fingerprints for key, fingerprints in original_pdfs.items()),
                        'A pre-existing workspace PDF changed during focused verification.')
                evidence['preexisting_workspaces_unchanged'] = True
            except Exception:
                failed = True
                evidence['preexisting_workspaces_preservation_unconfirmed'] = True
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
