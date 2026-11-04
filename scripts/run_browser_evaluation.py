"""Opt-in real-provider heldout run through an owned local Streamlit browser.

Requires a separately approved and frozen run directory. Never grades answers,
substitutes fixtures, automatically retries a submitted question, saves
workspaces, or resumes an already submitted attempt. Explicit retries require a
new frozen directory and a hash-bound link to the preserved primary.
All output is private, under ignored logs.
"""
import argparse
from datetime import datetime, timezone
from hashlib import sha256
from importlib.metadata import version
import json
import math
from pathlib import Path
import platform
import re
import subprocess
import sys
import time

from scripts.local_test_app import (LOCAL_API, LocalSetupBlocked, LocalTestApp,
                                    load_local_configuration, load_test_credentials)
from src.knowledge_assistant.auth import AuthClient, AuthError
from src.knowledge_assistant.persistence import WorkspaceStore

ROOT = Path(__file__).resolve().parents[1]
RESPONSE_LIMIT_SECONDS = 10.0
WAIT_MILLISECONDS = 160000
TIMING_METHOD = ('Browser performance.now(): capture-phase textarea Enter keydown '
                 'to exactly one answer in a fresh chat, Streamlit notRunning, '
                 'supporting passages expanded and visible, then two animation frames. '
                 'Includes network, retrieval, SDK retries and browser rendering.')


class EvaluationBlocked(Exception):
    """A sanitized local prerequisite or provider blocker."""


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def latency_pass(outcome, seconds):
    """Missing, nonfinite, failed and over-deadline responses never pass."""
    return (outcome == 'COMPLETED' and type(seconds) in (int, float)
            and math.isfinite(seconds) and 0 <= seconds <= RESPONSE_LIMIT_SECONDS)


def pacing_seconds(value):
    """CLI pacing is finite and bounded; it never changes response acceptance."""
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError('Pacing must be a finite number from 0 to 60 seconds.') from None
    if not math.isfinite(number) or not 0 <= number <= 60:
        raise argparse.ArgumentTypeError('Pacing must be a finite number from 0 to 60 seconds.')
    return number


def pace_before_submission(page, previous_completed, delay):
    """Wait outside the unchanged response timer using the same browser clock."""
    result = {'minimum_interval_seconds': delay, 'previous_completed_case_id': None,
              'previous_rendered_end': None, 'browser_time_origin': None,
              'wait_seconds': None, 'actual_interval_seconds': None,
              'included_in_response_seconds': False}
    if previous_completed is None:
        return result
    now = page.evaluate('({now:performance.now(),timeOrigin:performance.timeOrigin})')
    if now['timeOrigin'] != previous_completed['time_origin']:
        raise EvaluationBlocked('Browser monotonic clock origin changed between cases; pacing cannot be established.')
    page.wait_for_function('(target) => performance.now() >= target',
                           arg=previous_completed['ended'] + delay * 1000,
                           polling='raf', timeout=max(30000, (delay + 10) * 1000))
    after = page.evaluate('performance.now()')
    result.update({'previous_completed_case_id': previous_completed['case_id'],
                   'previous_rendered_end': previous_completed['ended'],
                   'browser_time_origin': now['timeOrigin'],
                   'wait_seconds': (after - now['now']) / 1000})
    return result


def finish_pacing(pacing, observation):
    result = dict(pacing)
    if result['previous_rendered_end'] is not None and observation.get('submitted') is not None:
        if observation.get('submittedTimeOrigin') != result['browser_time_origin']:
            result.update({'minimum_interval_met': False, 'actual_interval_seconds': None,
                           'measurement_error': 'Browser clock origin changed during paced submission.'})
            return result
        result['actual_interval_seconds'] = (observation['submitted'] - result['previous_rendered_end']) / 1000
        result['minimum_interval_met'] = result['actual_interval_seconds'] >= result['minimum_interval_seconds']
    else:
        result['minimum_interval_met'] = None
    return result


def telemetry_offset(path):
    return path.stat().st_size if path is not None and path.exists() else 0


def provider_events(path, offset):
    """Read only this operation's private sanitized records, never raw bodies."""
    if path is None:
        return {'enabled': False, 'events': [], 'invalid_lines': 0}
    records, invalid = [], 0
    if path.exists():
        with path.open('rb') as stream:
            stream.seek(offset)
            for line in stream:
                try:
                    record = json.loads(line)
                    if not isinstance(record, dict):
                        raise ValueError()
                    records.append(record)
                except (ValueError, UnicodeDecodeError):
                    invalid += 1
    return {'enabled': True, 'events': records, 'invalid_lines': invalid,
            'start_byte': offset, 'end_byte': telemetry_offset(path)}


def provider_stop_reason(capture, errors, stage):
    events = capture.get('events', [])
    statuses = {event.get('http_status') for event in events}
    codes = {str(event.get(field, '')).upper()
             for event in events for field in ('error_code', 'provider_error_status')}
    operation = next((event.get('operation') for event in reversed(events) if event.get('operation')), None)
    label = stage + ('/' + operation if operation else '')
    if (429 in statuses or codes.intersection({'RESOURCE_EXHAUSTED', 'RATE_LIMIT_EXCEEDED', 'INSUFFICIENT_QUOTA'})
            or any('API request limit' in error for error in errors)):
        return label + ': provider quota/request limit; no outer retry.'
    if (statuses.intersection({401, 403, 404}) or codes.intersection({'UNAUTHENTICATED', 'PERMISSION_DENIED', 'MODEL_NOT_FOUND', 'NOT_FOUND'})
            or any('API authentication failed' in error for error in errors)):
        return label + ': provider authentication/access failure; no outer retry.'
    if 402 in statuses or any('API credits are unavailable' in error for error in errors):
        return label + ': provider credits unavailable; no outer retry.'
    return None


def post_attempt_stop_reason(outcome, first_selected, require_first_success, pacing, capture, errors):
    """Gate only after the actual outcome and every measurement are preserved."""
    reason = provider_stop_reason(capture, errors, 'answer')
    if reason:
        return reason
    if require_first_success and first_selected and outcome != 'COMPLETED':
        return 'First selected case did not complete successfully; controlled continuation is stopped.'
    if pacing.get('minimum_interval_met') is False:
        return 'Measured inter-case pacing did not satisfy the configured condition; actual response preserved.'
    return None


def checked_path(root, relative):
    path = (Path(root) / relative).resolve()
    if not path.is_relative_to(Path(root).resolve()):
        raise EvaluationBlocked('A frozen path is outside the project.')
    return path


def verify_freeze(root, freeze):
    for group in ('app_source_sha256', 'candidate_sha256', 'approved_artifact_sha256'):
        mapping = freeze.get(group)
        if not isinstance(mapping, dict) or not mapping:
            raise EvaluationBlocked('Frozen hash group is missing: ' + group)
        for relative, expected in mapping.items():
            path = checked_path(root, relative)
            if not path.is_file() or sha256(path.read_bytes()).hexdigest() != expected:
                raise EvaluationBlocked('Frozen file hash mismatch: ' + relative)
    if not freeze.get('owner_confirmation'):
        raise EvaluationBlocked('Separate owner confirmation is missing.')
    protocol = checked_path(root, freeze.get('protocol_path', ''))
    if (not protocol.is_file()
            or sha256(protocol.read_bytes()).hexdigest() != freeze.get('protocol_sha256')):
        raise EvaluationBlocked('Frozen scoring protocol hash mismatch.')


def write_exclusive(path, value, sensitive=()):
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if any(secret and secret in text for secret in sensitive):
        raise EvaluationBlocked('Private evidence secret-boundary check failed.')
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with Path(path).open('x', encoding='utf-8') as stream:
        stream.write(text)


def update_record(path, value, sensitive=()):
    """Only the resumable aggregate changes; immutable attempts never do."""
    text = json.dumps(value, indent=2, ensure_ascii=False) + '\n'
    if any(secret and secret in text for secret in sensitive):
        raise EvaluationBlocked('Private evidence secret-boundary check failed.')
    temporary = path.with_name(path.name + '.runner.tmp')
    with temporary.open('x', encoding='utf-8') as stream:
        stream.write(text)
    temporary.replace(path)


def validate_run(run, root=ROOT):
    actual = run.get('cases', [])
    expected = json.loads((Path(root) / 'evaluation/heldout/questions.json').read_text(encoding='utf-8'))['cases']
    if len(actual) != 40 or len(expected) != 40:
        raise EvaluationBlocked('Exactly forty candidate cases are required.')
    for case, reference in zip(actual, expected):
        if any(case.get(field) != reference[field] for field in ('id', 'files', 'question', 'category')):
            raise EvaluationBlocked('Run cases differ from the frozen candidate.')
        if case.get('status') != 'Not run':
            raise EvaluationBlocked('An existing primary result cannot be rerun or replaced.')


# This watcher lives in the browser throughout the actual request. Python polling
# and Playwright locator latency cannot shorten (or establish) the measured time.
ARM_RESPONSE = r"""({question, timeoutMs}) => {
    if (document.querySelectorAll('[data-testid="stChatMessage"]').length !== 0)
        throw new Error('Fresh chat required');
    const prior = window.__evaluation;
    if (prior && !prior.done) throw new Error('A submitted watcher is still active');
    const state = window.__evaluation = {done:false, submitted:null, ended:null,
        outcome:null, answer:null, sources:[], errors:[], rafAfter:null,
        timingMethod:'capture-keydown/performance.now/two-animation-frames'};
    const visible = node => !!node && node.getClientRects().length > 0;
    const errors = () => Array.from(document.querySelectorAll('[data-testid="stAlert"]'))
        .map(e => e.innerText).filter(text => /API credits are unavailable|API authentication failed|API request limit|AI processing failed|Session paused|Index cleanup failed/.test(text));
    const finish = (outcome, now) => {
        state.outcome=outcome; state.ended=now; state.done=true;
        state.elapsedSeconds=(now-state.submitted)/1000;
    };
    const inspect = now => {
        if (state.done) return;
        if (state.submitted === null) { requestAnimationFrame(inspect); return; }
        const cards=Array.from(document.querySelectorAll('[data-testid="stChatMessage"]'));
        const settled=document.querySelector('[data-testid="stApp"]')?.getAttribute('data-test-script-state')==='notRunning';
        const fault=errors();
        if (settled && fault.length) {
            state.errors=fault; finish('TECHNICAL_ERROR', now); return;
        }
        if (cards.length===2 && settled) {
            const user=cards[0].querySelector('[data-testid="stText"]');
            const answer=cards[1].querySelector('[data-testid="stText"]');
            const panels=Array.from(cards[1].querySelectorAll('[data-testid="stExpander"]'));
            let ready=visible(user) && user.innerText===question && visible(answer) && !!answer.innerText.trim();
            const sources=[];
            for (const panel of panels) {
                const detail=panel.querySelector('details');
                if (detail && !detail.open) {
                    panel.querySelector('summary')?.click();
                    ready=false;
                }
                const captions=Array.from(panel.querySelectorAll('[data-testid="stCaptionContainer"]'));
                const passages=Array.from(panel.querySelectorAll('[data-testid="stText"]'));
                if (!detail?.open || !captions.length || captions.length!==passages.length) ready=false;
                for(let i=0;i<captions.length;i++) {
                    if(!visible(captions[i]) || !visible(passages[i])) ready=false;
                    sources.push({caption:captions[i].innerText,text:passages[i]?.innerText ?? ''});
                }
            }
            // An answer claiming references is incomplete until its passage panel renders.
            if(answer?.innerText.includes('Sources:') && !panels.length) ready=false;
            if(ready) {
                const signature=JSON.stringify([answer.innerText,sources]);
                if(state.signature!==signature) {
                    state.signature=signature; state.rafAfter=2;
                } else if(state.rafAfter>0) {
                    state.rafAfter--;
                } else {
                    state.answer=answer.innerText; state.userQuestion=user.innerText;
                    state.sources=sources; state.chatMessageCount=cards.length;
                    finish('COMPLETED',now); return;
                }
            } else {state.signature=null; state.rafAfter=null;}
        } else {state.signature=null; state.rafAfter=null;}
        if(now-state.submitted>=timeoutMs) {
            state.errors=fault; state.partialChat=cards.map(e=>e.innerText);
            finish('TIMEOUT',now); return;
        }
        requestAnimationFrame(inspect);
    };
    const capture = event => {
        if(event.key==='Enter' && !event.shiftKey && !event.isComposing &&
           event.target.matches('textarea[placeholder="Ask about your indexed PDFs"]')) {
            document.removeEventListener('keydown',capture,true);
            state.submitted=performance.now(); state.submittedTimeOrigin=performance.timeOrigin;
        }
    };
    document.addEventListener('keydown',capture,true);
    requestAnimationFrame(inspect);
    return {armed:true,freshChat:true};
}"""


ARM_INDEXING = r"""({timeoutMs}) => {
    const state=window.__evaluationIndex={started:null,done:false,ended:null,outcome:null};
    const finish=(outcome,now)=>{state.outcome=outcome;state.ended=now;state.done=true;
        state.elapsedSeconds=(now-state.started)/1000;};
    const inspect=now=>{
        if(state.done)return;
        if(state.started!==null){
            const settled=document.querySelector('[data-testid="stApp"]')?.getAttribute('data-test-script-state')==='notRunning';
            const question=document.querySelector('textarea[placeholder="Ask about your indexed PDFs"]');
            if(settled && question && !question.disabled){finish('COMPLETED',now);return;}
            const faults=Array.from(document.querySelectorAll('[data-testid="stAlert"]'))
                .map(e=>e.innerText).filter(t=>/API credits are unavailable|API authentication failed|API request limit|AI processing failed|Index cleanup failed/.test(t));
            if(settled && faults.length){state.errors=faults;finish('TECHNICAL_ERROR',now);return;}
            if(now-state.started>=timeoutMs){finish('TIMEOUT',now);return;}
        }
        requestAnimationFrame(inspect);
    };
    const capture=event=>{
        const button=event.target.closest('button');
        if(button && button.innerText==='Index documents'){
            document.removeEventListener('click',capture,true);
            state.started=performance.now();state.timeOrigin=performance.timeOrigin;
        }
    };
    document.addEventListener('click',capture,true);requestAnimationFrame(inspect);
    return true;
}"""


DOCUMENT_BOUNDARY = r"""({previousIdentity=null, expectedFiles=[]}) => {
    const input=document.querySelector('input[type="file"]');
    const parent=input?.closest('[class*="st-key-uploads-"]');
    const identity=parent ? Array.from(parent.classList).find(c=>c.startsWith('st-key-uploads-')) : null;
    const chat=document.querySelector('textarea[placeholder="Ask about your indexed PDFs"]');
    const index=Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='Index documents');
    const files=Array.from(document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stText"]')).map(e=>e.innerText);
    const settled=document.querySelector('[data-testid="stApp"]')?.getAttribute('data-test-script-state')==='notRunning';
    return !!input && !input.disabled && !!chat && chat.disabled && !!index && settled &&
        document.querySelectorAll('[data-testid="stChatMessage"]').length===0 &&
        JSON.stringify(files)===JSON.stringify(expectedFiles) &&
        (!previousIdentity || (identity && identity!==previousIdentity));
}"""


def selected_cases(run, case_ids=None):
    """Explicit continuation selection never silently resumes a prior run."""
    cases = run['cases']
    if case_ids is None:
        return cases
    known = {case['id'] for case in cases}
    if not case_ids or len(set(case_ids)) != len(case_ids) or any(case_id not in known for case_id in case_ids):
        raise EvaluationBlocked('Selected case IDs must be unique known candidate IDs.')
    selected = set(case_ids)
    return [case for case in cases if case['id'] in selected]


def attempt_identity(root, cases, retry_of=None):
    """An explicit retry can never masquerade as a new primary submission."""
    if retry_of is None:
        return {'primary': True, 'attempt': 1}
    if len(cases) != 1:
        raise EvaluationBlocked('A linked retry requires exactly one selected case.')
    path = checked_path(root, retry_of)
    if not path.is_relative_to(Path(root).resolve() / 'logs/evaluation'):
        raise EvaluationBlocked('Retry evidence must be inside ignored evaluation logs.')
    try:
        original = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise EvaluationBlocked('Original primary evidence is missing or invalid.') from None
    case = cases[0]
    if (original.get('primary') is not True or original.get('attempt') != 1
            or original.get('case_id') != case['id']
            or any(original.get(field) != case[field] for field in ('question', 'files'))
            or original.get('state') not in {'COMPLETED', 'TECHNICAL_ERROR', 'TIMEOUT'}):
        raise EvaluationBlocked('Retry must link to this exact preserved primary question and document scope.')
    return {'primary': False, 'attempt': 2,
            'retry_of': {'path': str(path.relative_to(Path(root).resolve())).replace('\\', '/'),
                         'sha256': sha256(path.read_bytes()).hexdigest(),
                         'original_state': original['state']}}


# Passive client-only markers. These never mutate the page or modify the
# authoritative ARM_RESPONSE clock, and cannot identify backend stage durations.
ARM_DIAGNOSTICS = r"""() => {
    if(window.__evaluationDiagnostics) window.__evaluationDiagnostics.stopped=true;
    const state=window.__evaluationDiagnostics={stopped:false,markers:{},sampledFrames:0};
    const visible=node=>!!node && node.getClientRects().length>0;
    const tick=()=>{
        if(state.stopped)return;
        const timing=window.__evaluation;
        if(timing?.submitted!==null && timing?.submitted!==undefined){
            state.sampledFrames++;
            const seconds=(performance.now()-timing.submitted)/1000;
            const mark=(key,yes)=>{if(yes && !(key in state.markers))state.markers[key]=seconds;};
            const app=document.querySelector('[data-testid="stApp"]');
            const running=app?.getAttribute('data-test-script-state')==='running';
            mark('script_running_first_seen_seconds',running);
            mark('script_settled_after_running_first_seen_seconds',!running &&
                app?.getAttribute('data-test-script-state')==='notRunning' &&
                'script_running_first_seen_seconds' in state.markers);
            const cards=Array.from(document.querySelectorAll('[data-testid="stChatMessage"]'));
            mark('user_card_first_seen_seconds',visible(cards[0]));
            const answer=cards[1]?.querySelector('[data-testid="stText"]');
            mark('assistant_text_first_seen_seconds',visible(answer) && !!answer.innerText.trim());
            const panel=cards[1]?.querySelector('[data-testid="stExpander"]');
            const passages=panel ? Array.from(panel.querySelectorAll('[data-testid="stText"]')) : [];
            mark('supporting_passages_visible_first_seen_seconds',passages.length>0 && passages.every(visible));
            mark('alert_first_seen_seconds',Array.from(document.querySelectorAll('[data-testid="stAlert"]')).some(visible));
            if(timing.done){state.stopped=true;return;}
        }
        requestAnimationFrame(tick);
    };
    requestAnimationFrame(tick);
}"""


def collect_diagnostics(page, observation):
    value = page.evaluate('''() => {
        const state=window.__evaluationDiagnostics;
        if(!state)return null;
        state.stopped=true;
        return {markers:state.markers,sampled_frames:state.sampledFrames};
    }''')
    return {'scope': 'Passive browser DOM observations; not retrieval/provider/network stage timings',
            'clock': 'window.performance.now relative to authoritative submission',
            'observations': value, 'response_end_seconds': observation.get('elapsedSeconds'),
            'backend_retrieval_seconds': None, 'query_embedding_seconds': None,
            'chat_provider_seconds': None, 'provider_internal_retries': None,
            'render_cpu_seconds': None}


def reset_document_boundary(page):
    """Witness reset completion rather than accepting the old notRunning frame."""
    previous = page.locator('input[type=file]').evaluate('''element => {
        const parent=element.closest('[class*="st-key-uploads-"]');
        return parent ? Array.from(parent.classList).find(c=>c.startsWith('st-key-uploads-')) : null;
    }''')
    page.get_by_role('button', name='Reset documents and chat', exact=True).click()
    page.wait_for_function(DOCUMENT_BOUNDARY, arg={'previousIdentity': previous, 'expectedFiles': []},
                           polling='raf', timeout=30000)


def failure_observation(page):
    """Small safe UI state, excluding form inputs and hidden configuration."""
    return page.evaluate('''() => ({
        scriptState:document.querySelector('[data-testid="stApp"]')?.getAttribute('data-test-script-state'),
        chatMessageCount:document.querySelectorAll('[data-testid="stChatMessage"]').length,
        uploadDisabled:document.querySelector('input[type="file"]')?.disabled,
        questionDisabled:document.querySelector('textarea[placeholder="Ask about your indexed PDFs"]')?.disabled,
        indexedFileNames:Array.from(document.querySelectorAll('[data-testid="stSidebar"] [data-testid="stText"]')).map(e=>e.innerText),
        indexDisabled:Array.from(document.querySelectorAll('button')).find(b=>b.innerText.trim()==='Index documents')?.disabled
    })''')


def sources_from_browser(sources):
    result = []
    for source in sources:
        match = re.fullmatch(r'(.+?)\s+\S+\s+PDF page (\d+)', source['caption'].strip())
        result.append({'filename': match[1] if match else None,
                       'page': int(match[2]) if match else None,
                       'text': source['text'], 'rendered_caption': source['caption']})
    return result


def workspace_witness(store):
    rows = store.request('/rest/v1/saved_workspaces?select=*')
    documents = {}
    for row in rows:
        if row['status'] == 'ready':
            uploads, _ = store.load(row['id'])
            documents[row['id']] = [{'name': upload.name, 'sha256': sha256(upload.data).hexdigest()}
                                    for upload in uploads]
    canonical = json.dumps({'rows': sorted(rows, key=lambda row: row['id']), 'documents': documents},
                           sort_keys=True).encode()
    return {'workspace_count': len(rows), 'row_and_pdf_sha256': sha256(canonical).hexdigest()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--child-output', type=Path, required=True)
    parser.add_argument('--case-ids', nargs='+', help='Explicit IDs for a new, separately labeled continuation/retest directory.')
    parser.add_argument('--inter-case-delay-seconds', type=pacing_seconds, default=0.0,
                        help='Minimum 0-60 seconds from prior completed render to next submission; outside response timing.')
    parser.add_argument('--capture-provider-errors', action='store_true',
                        help='Opt into sanitized private provider-error telemetry from the owned child only.')
    parser.add_argument('--require-first-case-success', action='store_true',
                        help='Stop a controlled continuation if its first selected question does not complete successfully.')
    parser.add_argument('--retry-of', type=Path,
                        help='Original primary JSON for one explicitly authorized retry in a new frozen run.')
    parser.add_argument('--browser-diagnostics', action='store_true',
                        help='Collect passive DOM markers without changing the response clock or app runtime.')
    parser.add_argument('--stage-timings', action='store_true',
                        help='Opt into sanitized local backend spans/SDK attempt markers; no acceptance clock change.')
    args = parser.parse_args(argv)
    run_dir, child_output = checked_path(ROOT, args.run_dir), checked_path(ROOT, args.child_output)
    if not run_dir.is_relative_to(ROOT / 'logs/evaluation'):
        parser.error('Run directory must be inside ignored logs/evaluation.')
    run_path, freeze_path = run_dir / 'run.json', run_dir / 'freeze.json'
    run = json.loads(run_path.read_text(encoding='utf-8'))
    freeze = json.loads(freeze_path.read_text(encoding='utf-8'))
    if (run_dir / 'runner-started.json').exists() or (run_dir / 'attempts').exists():
        print('BLOCKED: Existing started/submitted run requires an audit; it was not modified.', flush=True)
        return 1
    page = browser = playwright = app = client = store = token = None
    sensitive, witness = [], None
    error_file = child_output / 'provider-errors.jsonl' if args.capture_provider_errors else None
    timing_file = child_output / 'stage-timings.jsonl' if args.stage_timings else None
    step, active_case, submitted = 'freeze verification', None, False
    complete = False

    def checkpoint():
        update_record(run_path, run, sensitive)

    def settle():
        expect(page.get_by_test_id('stApp')).to_have_attribute('data-test-script-state', 'notRunning')

    def click(label):
        page.get_by_role('button', name=label, exact=True).click()

    def wait_browser(name):
        page.wait_for_function(f'window.{name} && window.{name}.done', timeout=WAIT_MILLISECONDS + 20000,
                               polling='raf')
        return page.evaluate(f'window.{name}')

    try:
        verify_freeze(ROOT, freeze)
        validate_run(run)
        cases_to_run = selected_cases(run, args.case_ids)
        identity = attempt_identity(ROOT, cases_to_run, args.retry_of)
        if freeze.get('retry_of') != identity.get('retry_of'):
            raise EvaluationBlocked('Retry link differs from its frozen original primary hash.')
        config = load_local_configuration(ROOT)
        if not all(config.get(name) for name in ('GEMINI_API_KEY', 'GEMINI_CHAT_MODEL', 'GEMINI_EMBEDDING_MODEL')):
            raise EvaluationBlocked('Local Gemini key/model configuration is incomplete.')
        credentials = load_test_credentials(ROOT, ('a',))
        sensitive = [config['GEMINI_API_KEY'], config['SUPABASE_PUBLISHABLE_KEY'], credentials['password_a']]
        from playwright.sync_api import expect, sync_playwright
        run.update({'run_status': 'RUNNING', 'started_at': utc_now(), 'provider': 'gemini',
                    'chat_model': config['GEMINI_CHAT_MODEL'], 'embedding_model': config['GEMINI_EMBEDDING_MODEL'],
                    'browser_timing_method': TIMING_METHOD, 'latency_limit_seconds': RESPONSE_LIMIT_SECONDS,
                    'timing_scope': 'browser_submission_to_rendered_answer_and_sources',
                    'timing_clock': 'window.performance.now',
                    'app_cache_policy': 'Fresh owned process; no answer cache; fresh empty chat per case; identical index may be reused.',
                    'test_concurrency': 1, 'source_revision': subprocess.run(
                        ['git', 'rev-parse', 'HEAD'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip(),
                    'commit': freeze.get('candidate_revision'),
                    'working_tree_status': subprocess.run(
                        ['git', 'status', '--short'], cwd=ROOT, capture_output=True, text=True, check=True).stdout.splitlines(),
                    'tested_source_sha256': freeze['app_source_sha256'],
                    'sdk_max_retries': 2, 'sdk_actual_retry_count': None,
                    'cpu_load_measurement': None,
                    'load_conditions': 'One sequential evaluation browser; existing user app untouched; no synthetic concurrent load.',
                    'selected_case_ids': [case['id'] for case in cases_to_run],
                    'selected_case_count': len(cases_to_run),
                    'require_first_case_success': args.require_first_case_success,
                    'attempt_identity': identity,
                    'browser_diagnostics_enabled': args.browser_diagnostics,
                    'stage_timing_capture_enabled': args.stage_timings,
                    'pacing_condition': {'minimum_interval_seconds': args.inter_case_delay_seconds,
                                         'from': 'previous completed rendered response', 'to': 'next question Enter submission',
                                         'clock': 'window.performance.now', 'included_in_response_seconds': False},
                    'provider_error_capture': {'enabled': args.capture_provider_errors,
                                               'path': str(error_file.relative_to(ROOT)).replace('\\', '/') if error_file else None},
                    'manual_comparison': 'Not executed; no invented manual timings; AI scorer has seen expected answers.',
                    'runtime': {'python': platform.python_version(), 'platform': platform.platform(),
                                'packages': {name: version(name) for name in ('streamlit', 'playwright', 'openai', 'langchain-openai', 'chromadb')}}})
        write_exclusive(run_dir / 'runner-started.json', {'at': utc_now(), 'freeze_sha256': sha256(freeze_path.read_bytes()).hexdigest(),
                        'runner_sha256': sha256(Path(__file__).read_bytes()).hexdigest()}, sensitive)
        checkpoint()
        step = 'normal-user preservation witness'
        client = AuthClient(LOCAL_API, config['SUPABASE_PUBLISHABLE_KEY'])
        token, user = client.login('qa-a@example.com', credentials['password_a'])
        sensitive.append(token)
        store = WorkspaceStore(LOCAL_API, client.key, token, user['id'])
        witness = workspace_witness(store)
        run['workspaces_before'] = witness
        step = 'owned local app cold startup'
        app_options = {'provider_error_file': error_file} if error_file is not None else {}
        if timing_file is not None:
            app_options['stage_timing_file'] = timing_file
        app = LocalTestApp(ROOT, child_output, config, **app_options)
        started = time.monotonic()
        app.start()
        run['cold_app_health_startup_seconds'] = time.monotonic() - started
        run['app_url'] = app.url
        run['supabase_url'] = LOCAL_API
        playwright = sync_playwright().start()
        browser = playwright.chromium.launch()
        run['runtime']['browser'] = {'engine': 'Chromium', 'version': browser.version, 'headless': True,
                                     'viewport': {'width': 1440, 'height': 1200}}
        page = browser.new_page(viewport={'width': 1440, 'height': 1200})
        page.set_default_timeout(30000)
        page.goto(app.url)
        page.get_by_role('textbox', name='Email', exact=True).first.fill('qa-a@example.com')
        page.get_by_role('textbox', name='Password', exact=True).first.fill(credentials['password_a'])
        click('Log in')
        expect(page.get_by_role('button', name='Log out', exact=True)).to_be_visible()
        settle()
        selected_files, indexed_by = None, None
        previous_completed = None
        checkpoint()
        for case in cases_to_run:
            active_case, submitted = case, False
            case_dir = run_dir / 'attempts' / case['id']
            case_dir.mkdir(parents=True, exist_ok=False)
            step = case['id'] + ' fresh document/chat boundary'
            target_files = tuple(case['files'])
            indexing = None
            if target_files != selected_files:
                if selected_files is not None:
                    reset_document_boundary(page)
                page.wait_for_function(DOCUMENT_BOUNDARY, arg={'expectedFiles': []}, polling='raf')
                page.locator('input[type=file]').set_input_files([
                    str(ROOT / 'data/heldout_pdfs' / name) for name in target_files])
                # The uploader's local selection is not sufficient: these text
                # rows are rendered only after Streamlit received the new PDFs.
                page.wait_for_function(DOCUMENT_BOUNDARY, arg={'expectedFiles': list(target_files)}, polling='raf')
                consent = page.get_by_role('checkbox', name='I agree to send these documents and questions to Google Gemini.', exact=True)
                if not consent.is_checked():
                    page.get_by_text('I agree to send these documents and questions to Google Gemini.', exact=True).click()
                expect(consent).to_be_checked()
                expect(page.get_by_role('button', name='Index documents', exact=True)).to_be_enabled()
                step = case['id'] + ' real indexing'
                page.evaluate(ARM_INDEXING, {'timeoutMs': WAIT_MILLISECONDS})
                error_offset = telemetry_offset(error_file)
                write_exclusive(case_dir / 'indexing-submission.json', {'at': utc_now(), 'files': list(target_files)}, sensitive)
                click('Index documents')
                indexing = wait_browser('__evaluationIndex')
                indexing['provider_errors'] = provider_events(error_file, error_offset)
                write_exclusive(case_dir / 'indexing.json', indexing, sensitive)
                if indexing['outcome'] != 'COMPLETED':
                    case.update({'status': 'Not run', 'indexing_seconds': indexing.get('elapsedSeconds'),
                                 'indexing_failure': indexing['outcome'], 'failure_stage': 'indexing before question submission',
                                 'indexing_provider_errors': indexing['provider_errors']})
                    checkpoint()
                    reason = provider_stop_reason(indexing['provider_errors'], indexing.get('errors', []), 'indexing')
                    raise EvaluationBlocked(reason or 'Real indexing did not complete; see immutable indexing evidence.')
                selected_files, indexed_by = target_files, case['id']
            elif page.get_by_test_id('stChatMessage').count():
                click('Clear chat only')
                settle()
            expect(page.get_by_test_id('stChatMessage')).to_have_count(0)
            question = page.get_by_placeholder('Ask about your indexed PDFs')
            expect(question).to_be_enabled()
            question.fill(case['question'])
            step = case['id'] + ' inter-case pacing before submission'
            pacing = pace_before_submission(page, previous_completed, args.inter_case_delay_seconds)
            attempt_name = 'primary.json' if identity['primary'] else 'retry-02.json'
            step = case['id'] + (' primary submission' if identity['primary'] else ' explicit retry submission')
            page.evaluate(ARM_RESPONSE, {'question': case['question'], 'timeoutMs': WAIT_MILLISECONDS})
            if args.browser_diagnostics:
                page.evaluate(ARM_DIAGNOSTICS)
            submission = {'case_id': case['id'], **identity, 'at': utc_now(),
                          'question': case['question'], 'files': case['files'], 'fresh_chat': True,
                          'index_reuse_of': None if indexing else indexed_by,
                          'indexing_seconds': indexing['elapsedSeconds'] if indexing else None,
                          'pacing': pacing,
                          'state': 'SUBMISSION_ARMED_DO_NOT_AUTOMATICALLY_RESUBMIT'}
            write_exclusive(case_dir / 'submission.json', submission, sensitive)
            case.update({'status': 'SUBMITTED', 'attempt_evidence': str((case_dir / attempt_name).relative_to(ROOT)).replace('\\', '/'),
                         'indexing_seconds': submission['indexing_seconds'], 'index_reuse_of': submission['index_reuse_of']})
            checkpoint()
            # The checkpoint precedes keydown; an interrupted/uncertain submission
            # is deliberately never automatically repeated.
            submitted = True
            error_offset = telemetry_offset(error_file)
            timing_offset = telemetry_offset(timing_file)
            question.press('Enter')
            observation = wait_browser('__evaluation')
            errors = provider_events(error_file, error_offset)
            completed_pacing = finish_pacing(pacing, observation)
            answer_seconds = observation.get('elapsedSeconds')
            outcome = observation['outcome']
            attempt = {**submission, 'state': outcome, 'observed_at': utc_now(), 'browser_observation': observation,
                       'answer_seconds': answer_seconds, 'latency_pass': latency_pass(outcome, answer_seconds),
                       'timing_method': TIMING_METHOD, 'actual_answer': observation.get('answer'),
                       'rendered_sources': sources_from_browser(observation.get('sources', [])),
                       'provider_errors': errors, 'pacing': completed_pacing,
                       'screenshot': 'rendered-response.png'}
            if timing_file is not None:
                attempt['stage_timing_events'] = provider_events(timing_file, timing_offset)
            if args.browser_diagnostics:
                try:
                    attempt['browser_diagnostics'] = collect_diagnostics(page, observation)
                except Exception:
                    attempt['browser_diagnostics'] = {'capture_failed': True,
                                                       'observations': None,
                                                       'response_end_seconds': answer_seconds}
            try:
                page.screenshot(path=str(case_dir / 'rendered-response.png'), full_page=True)
            except Exception:
                attempt['screenshot'] = None
                attempt['screenshot_unavailable'] = True
            write_exclusive(case_dir / attempt_name, attempt, sensitive)
            case.update({'status': 'Completed' if outcome == 'COMPLETED' else outcome,
                         'actual_answer': attempt['actual_answer'], 'retrieved_sources': None,
                         'rendered_sources': attempt['rendered_sources'], 'answer_seconds': answer_seconds,
                         'browser_latency_pass': attempt['latency_pass'], 'timing_method': TIMING_METHOD,
                         'primary_attempt': 1 if identity['primary'] else None,
                         'attempt_number': identity['attempt'], 'is_primary': identity['primary'],
                         'retry_of': identity.get('retry_of'), 'provider_usage': None,
                         'pacing': completed_pacing, 'provider_errors': errors,
                         'notes': 'Browser rendered evidence only; raw backend retrieval/token usage are not exposed. Semantic scoring pending.'})
            checkpoint()
            print(case['id'] + ': ' + outcome + '; browser seconds=' + str(answer_seconds)
                  + '; deadline=' + ('PASS' if attempt['latency_pass'] else 'FAIL'), flush=True)
            stop_reason = post_attempt_stop_reason(
                outcome, case['id'] == cases_to_run[0]['id'], args.require_first_case_success,
                completed_pacing, errors, observation.get('errors', []))
            if stop_reason:
                case['failure_stage'] = 'answer after question submission' if outcome != 'COMPLETED' else 'post-response pacing condition'
                checkpoint()
                raise EvaluationBlocked(stop_reason)
            if outcome != 'COMPLETED':
                case['failure_stage'] = 'answer after question submission'
                checkpoint()
                # A generic completed technical failure still counts as its
                # primary outcome. It must not suppress later independent cases.
                # If a timed-out request is still executing, do not submit a
                # concurrent request into that session or discard its evidence.
                try:
                    settle()
                except Exception:
                    raise EvaluationBlocked('Timed-out primary remains active; a fresh next submission cannot safely start.') from None
                # Remove this case's rendered error/late response before arming
                # another primary. Reusing a failed index could otherwise leave
                # an old alert visible during the next request's first frame.
                reset_document_boundary(page)
                selected_files, indexed_by = None, None
            else:
                previous_completed = {'case_id': case['id'], 'ended': observation['ended'],
                                      'time_origin': observation['submittedTimeOrigin']}
            verify_freeze(ROOT, freeze)
        complete = True
        run['run_status'] = 'COMPLETED_UNSCORED'
        run['selected_cases_finished'] = True
    except (EvaluationBlocked, LocalSetupBlocked, AuthError) as error:
        run['run_status'] = 'BLOCKED'
        reason = str(error) if isinstance(error, EvaluationBlocked) else 'Local configuration or normal-user authentication unavailable.'
        run['blocker'] = {'step': step, 'reason': reason, 'type': type(error).__name__, 'at': utc_now()}
        print('BLOCKED: ' + step + '; ' + reason, flush=True)
    except Exception as error:
        run['run_status'] = 'FAIL / INCOMPLETE'
        run['failure'] = {'step': step, 'type': type(error).__name__, 'at': utc_now(),
                          'submitted_primary_preserved': submitted}
        if isinstance(error, AssertionError):
            detail = str(error).splitlines()[0]
            if detail.startswith('Locator expected ') and not any(secret and secret in detail for secret in sensitive):
                run['failure']['assertion'] = detail[:200]
        if page is not None and not page.is_closed():
            try:
                run['failure']['browser_state'] = failure_observation(page)
                output = (run_dir / 'attempts' / active_case['id']) if active_case else run_dir
                screenshot = output / 'failure.png'
                if not screenshot.exists():
                    page.screenshot(path=str(screenshot), full_page=True)
                    run['failure']['screenshot'] = str(screenshot.relative_to(ROOT)).replace('\\', '/')
            except Exception:
                run['failure']['browser_state_unavailable'] = True
        print('FAIL: ' + step + ' (' + type(error).__name__ + '); no automatic retry.', flush=True)
    finally:
        if submitted and active_case is not None and active_case.get('status') == 'SUBMITTED':
            active_case['status'] = 'SUBMITTED_OUTCOME_UNCONFIRMED'
            active_case['browser_latency_pass'] = False
            active_case['answer_seconds'] = None
        if store is not None and witness is not None:
            try:
                after = workspace_witness(store)
                run['workspaces_after'] = after
                run['preexisting_workspaces_unchanged'] = after == witness
                if after != witness:
                    run['run_status'] = 'FAIL / PRESERVATION MISMATCH'
            except Exception:
                run['preexisting_workspace_preservation_unconfirmed'] = True
        if page is not None and not page.is_closed():
            try:
                button = page.get_by_role('button', name='Log out', exact=True)
                if button.is_visible():
                    button.click()
                    expect(page.get_by_role('button', name='Log in', exact=True)).to_be_visible()
            except Exception:
                run['browser_signout_unconfirmed'] = True
        for resource, method in ((browser, 'close'), (playwright, 'stop'), (app, 'stop')):
            if resource is not None:
                try:
                    getattr(resource, method)()
                except Exception:
                    run['cleanup_unconfirmed_' + method] = True
        if client is not None and token:
            try:
                client.logout(token)
            except Exception:
                run['witness_signout_unconfirmed'] = True
        run['stopped_at'] = utc_now()
        checkpoint()
    return 0 if complete and run['run_status'] == 'COMPLETED_UNSCORED' else 1


if __name__ == '__main__':
    raise SystemExit(main())
