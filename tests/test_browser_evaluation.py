"""Offline safeguards for opt-in evaluation; never invoke a real provider."""
from hashlib import sha256
import json
from pathlib import Path

import pytest

from scripts import run_browser_evaluation as runner


@pytest.mark.parametrize(('outcome', 'seconds', 'expected'), [
    ('COMPLETED', 10.0, True), ('COMPLETED', 10.000000001, False),
    ('COMPLETED', 9.999999999, True), ('COMPLETED', 0, True),
    ('COMPLETED', None, False), ('COMPLETED', -0.001, False),
    ('COMPLETED', float('nan'), False), ('COMPLETED', float('inf'), False),
    ('COMPLETED', True, False), ('TIMEOUT', 1.0, False),
    ('TECHNICAL_ERROR', 1.0, False), ('SUBMITTED', 1.0, False),
])
def test_deadline_uses_unrounded_complete_browser_measurement(outcome, seconds, expected):
    assert runner.latency_pass(outcome, seconds) is expected


def test_attempt_evidence_is_exclusive_and_secret_filtered(tmp_path):
    path = tmp_path / 'H01/primary.json'
    runner.write_exclusive(path, {'actual_answer': 'first response'})
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        runner.write_exclusive(path, {'actual_answer': 'replacement response'})
    assert path.read_bytes() == original
    with pytest.raises(runner.EvaluationBlocked, match='secret-boundary'):
        runner.write_exclusive(tmp_path / 'secret.json', {'value': 'fake-private-key'}, ['fake-private-key'])
    assert not (tmp_path / 'secret.json').exists()


def frozen_files(tmp_path):
    freeze = {'owner_confirmation': {'owner': 'offline owner', 'subsequent_approval': True}}
    for group in ('app_source_sha256', 'candidate_sha256', 'approved_artifact_sha256'):
        relative = group + '.txt'
        (tmp_path / relative).write_bytes(b'unchanged raw bytes\r\n')
        freeze[group] = {relative: sha256((tmp_path / relative).read_bytes()).hexdigest()}
    (tmp_path / 'protocol.json').write_bytes(b'[{"approved":"rules"}]')
    freeze['protocol_path'] = 'protocol.json'
    freeze['protocol_sha256'] = sha256((tmp_path / 'protocol.json').read_bytes()).hexdigest()
    return freeze


def test_freeze_binds_exact_bytes_and_separate_protocol(tmp_path):
    freeze = frozen_files(tmp_path)
    runner.verify_freeze(tmp_path, freeze)
    (tmp_path / 'app_source_sha256.txt').write_bytes(b'unchanged raw bytes\n')
    with pytest.raises(runner.EvaluationBlocked, match='hash mismatch'):
        runner.verify_freeze(tmp_path, freeze)


def test_freeze_rejects_missing_confirmation_and_outside_paths(tmp_path):
    freeze = frozen_files(tmp_path)
    freeze['owner_confirmation'] = None
    with pytest.raises(runner.EvaluationBlocked, match='owner confirmation'):
        runner.verify_freeze(tmp_path, freeze)
    with pytest.raises(runner.EvaluationBlocked, match='outside'):
        runner.checked_path(tmp_path, '../outside')


def test_validate_run_rejects_changed_question_or_previously_submitted_primary():
    root = Path(__file__).resolve().parents[1]
    cases = json.loads((root / 'evaluation/heldout/questions.json').read_text(encoding='utf-8'))['cases']
    run = {'cases': [{key: case[key] for key in ('id', 'files', 'question', 'category')} | {'status': 'Not run'}
                     for case in cases]}
    runner.validate_run(run, root)
    run['cases'][0]['status'] = 'SUBMITTED'
    with pytest.raises(runner.EvaluationBlocked, match='cannot be rerun'):
        runner.validate_run(run, root)
    run['cases'][0]['status'] = 'Not run'
    run['cases'][0]['question'] = 'another question'
    with pytest.raises(runner.EvaluationBlocked, match='differ'):
        runner.validate_run(run, root)


def test_rendered_source_identity_keeps_physical_pdf_page():
    assert runner.sources_from_browser([{'caption': 'onboarding.pdf · PDF page 2', 'text': 'Room 204.'}]) == [
        {'filename': 'onboarding.pdf', 'page': 2, 'text': 'Room 204.',
         'rendered_caption': 'onboarding.pdf · PDF page 2'}]
    invalid = runner.sources_from_browser([{'caption': 'unparseable source', 'text': 'passage'}])[0]
    assert invalid['filename'] is None and invalid['page'] is None


def test_continuation_selects_only_explicit_known_unique_cases():
    run = {'cases': [{'id': f'H{number:02d}'} for number in range(1, 41)]}
    assert runner.selected_cases(run) == run['cases']
    assert [case['id'] for case in runner.selected_cases(run, ['H08', 'H06'])] == ['H06', 'H08']
    for invalid in ([], ['H06', 'H06'], ['H41']):
        with pytest.raises(runner.EvaluationBlocked, match='unique known'):
            runner.selected_cases(run, invalid)
    assert run['cases'][0] == {'id': 'H01'}


def test_retry_is_linked_by_exact_primary_bytes_and_never_claimed_primary(tmp_path):
    case = {'id': 'H22', 'question': 'An approved question?', 'files': ['assigned.pdf']}
    original = {'case_id': 'H22', 'question': case['question'], 'files': case['files'],
                'primary': True, 'attempt': 1, 'state': 'TECHNICAL_ERROR'}
    path = tmp_path / 'logs/evaluation/old/attempts/H22/primary.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(original), encoding='utf-8')
    before = path.read_bytes()
    result = runner.attempt_identity(tmp_path, [case], path)
    assert result['primary'] is False and result['attempt'] == 2
    assert result['retry_of']['sha256'] == sha256(before).hexdigest()
    assert result['retry_of']['original_state'] == 'TECHNICAL_ERROR'
    assert path.read_bytes() == before
    assert runner.attempt_identity(tmp_path, [case]) == {'primary': True, 'attempt': 1}
    with pytest.raises(runner.EvaluationBlocked, match='exactly one'):
        runner.attempt_identity(tmp_path, [case, case], path)
    with pytest.raises(runner.EvaluationBlocked, match='exact preserved'):
        runner.attempt_identity(tmp_path, [case | {'files': ['other.pdf']}], path)


@pytest.mark.parametrize('change', [{'primary': False}, {'attempt': 2}, {'state': 'SUBMITTED'}, {'case_id': 'H27'}])
def test_retry_rejects_another_retry_uncertain_submission_and_wrong_case(tmp_path, change):
    case = {'id': 'H22', 'question': 'question', 'files': ['assigned.pdf']}
    path = tmp_path / 'logs/evaluation/old/primary.json'
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps({'case_id': 'H22', 'question': 'question', 'files': ['assigned.pdf'],
                               'primary': True, 'attempt': 1, 'state': 'COMPLETED'} | change))
    with pytest.raises(runner.EvaluationBlocked, match='exact preserved'):
        runner.attempt_identity(tmp_path, [case], path)


def test_retry_rejects_outside_evidence(tmp_path):
    with pytest.raises(runner.EvaluationBlocked, match='outside'):
        runner.attempt_identity(tmp_path, [{'id': 'H22'}], '../outside.json')


@pytest.mark.parametrize('value', ['-1', 'nan', 'inf', '61', 'not a number'])
def test_inter_case_delay_rejects_invalid_values(value):
    import argparse
    with pytest.raises(argparse.ArgumentTypeError):
        runner.pacing_seconds(value)


def test_first_case_pacing_has_no_invented_previous_measurement():
    pacing = runner.pace_before_submission(None, None, 10.0)
    assert pacing['actual_interval_seconds'] is None
    assert pacing['previous_completed_case_id'] is None
    assert pacing['included_in_response_seconds'] is False
    assert runner.finish_pacing(pacing, {'submitted': 20})['minimum_interval_met'] is None


def test_actual_submission_interval_uses_unrounded_browser_clock():
    pacing = {'minimum_interval_seconds': 10.0, 'previous_rendered_end': 1000.0,
              'browser_time_origin': 7.0}
    observation = {'submitted': 10999.999999, 'submittedTimeOrigin': 7.0}
    measured = runner.finish_pacing(pacing, observation)
    assert measured['actual_interval_seconds'] < 10.0
    assert measured['minimum_interval_met'] is False
    observation['submitted'] = 11000.0
    assert runner.finish_pacing(pacing, observation)['minimum_interval_met'] is True
    observation['submittedTimeOrigin'] = 8.0
    invalid = runner.finish_pacing(pacing, observation)
    assert invalid['minimum_interval_met'] is False
    assert invalid['actual_interval_seconds'] is None
    assert 'clock origin changed' in invalid['measurement_error']


def test_private_error_capture_is_partitioned_by_operation_offset(tmp_path):
    path = tmp_path / 'provider-errors.jsonl'
    path.write_text(json.dumps({'operation': 'embedding_documents', 'http_status': 429}) + '\n', encoding='utf-8')
    offset = runner.telemetry_offset(path)
    with path.open('a', encoding='utf-8') as stream:
        stream.write(json.dumps({'operation': 'chat', 'http_status': 403}) + '\n')
        stream.write('incomplete record\n')
    capture = runner.provider_events(path, offset)
    assert capture['events'] == [{'operation': 'chat', 'http_status': 403}]
    assert capture['invalid_lines'] == 1
    assert capture['end_byte'] > capture['start_byte']
    assert 'answer/chat' in runner.provider_stop_reason(capture, [], 'answer')
    assert runner.provider_events(None, 0) == {'enabled': False, 'events': [], 'invalid_lines': 0}


def test_error_diagnostics_stop_quota_and_access_at_exact_operation():
    for status in (401, 403, 404, 429):
        capture = {'events': [{'operation': 'embedding_query', 'http_status': status}]}
        reason = runner.provider_stop_reason(capture, ['AI processing failed.'], 'answer')
        assert reason.startswith('answer/embedding_query:') and 'no outer retry' in reason
    assert runner.provider_stop_reason({'events': []}, ['The API request limit was reached.'], 'indexing').startswith('indexing:')
    assert runner.provider_stop_reason({'events': []}, ['AI processing failed.'], 'answer') is None
    quota = {'events': [{'operation': 'chat', 'http_status': None, 'error_code': 'RESOURCE_EXHAUSTED'}]}
    assert 'quota/request limit' in runner.provider_stop_reason(quota, [], 'answer')
    assert 'HTTP 429' not in runner.provider_stop_reason(quota, [], 'answer')


@pytest.mark.parametrize('provider_status', ['RESOURCE_EXHAUSTED', 'PERMISSION_DENIED', 'MODEL_NOT_FOUND'])
def test_nested_google_status_from_actual_sanitizer_stops_without_http_status(provider_status):
    from src.knowledge_assistant.provider_telemetry import sanitized_error
    error = RuntimeError('Raw provider message is not recorded.')
    error.body = {'error': {'status': provider_status, 'code': 429,
                            'message': 'Raw provider body is not recorded.'}}
    event = sanitized_error(error, 'embedding_query', 'offline-model')
    assert event['http_status'] is None
    assert event['provider_error_status'] == provider_status
    reason = runner.provider_stop_reason({'events': [event]}, [], 'answer')
    assert reason.startswith('answer/embedding_query:') and 'no outer retry' in reason


@pytest.mark.parametrize('outcome', ['TECHNICAL_ERROR', 'TIMEOUT', 'SUBMITTED_OUTCOME_UNCONFIRMED'])
def test_controlled_first_case_failure_stops_before_following_cases(outcome):
    reason = runner.post_attempt_stop_reason(outcome, True, True, {}, {'events': []}, [])
    assert reason.startswith('First selected case did not complete successfully')
    assert runner.post_attempt_stop_reason(outcome, False, True, {}, {'events': []}, []) is None


def test_post_attempt_gate_retains_pacing_error_and_prioritizes_exact_quota_stage():
    pacing = {'minimum_interval_met': False}
    assert 'actual response preserved' in runner.post_attempt_stop_reason(
        'COMPLETED', False, True, pacing, {'events': []}, [])
    reason = runner.post_attempt_stop_reason(
        'TECHNICAL_ERROR', True, True, {},
        {'events': [{'operation': 'embedding_query', 'http_status': 429}]}, [])
    assert reason.startswith('answer/embedding_query:')


@pytest.fixture
def offline_browser():
    playwright_api = pytest.importorskip('playwright.sync_api', reason='Optional local browser timing validation requires Playwright.')
    with playwright_api.sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch()
        except playwright_api.Error as error:
            if "Executable doesn't exist" in str(error):
                pytest.skip('Optional local browser timing validation requires the Chromium binary.')
            raise
        yield browser
        browser.close()


def test_browser_watcher_counts_rendered_passages_and_monotonic_time(offline_browser):
    """Exercise real browser DOM/paint timing locally, without Streamlit/network."""
    browser = offline_browser
    if browser:
        page = browser.new_page()
        page.set_content('''<main data-testid="stApp" data-test-script-state="notRunning">
            <textarea placeholder="Ask about your indexed PDFs"></textarea><div id="chat"></div></main>''')
        page.evaluate(runner.ARM_RESPONSE, {'question': 'An offline question?', 'timeoutMs': 5000})
        box = page.get_by_placeholder('Ask about your indexed PDFs')
        box.fill('An offline question?')
        box.press('Enter')
        page.evaluate('''() => {
            document.querySelector('[data-testid="stApp"]').setAttribute('data-test-script-state','running');
            setTimeout(() => {
                document.getElementById('chat').innerHTML=`
                    <section data-testid="stChatMessage"><pre data-testid="stText">An offline question?</pre></section>
                    <section data-testid="stChatMessage"><pre data-testid="stText">Room 204.\nSources: onboarding.pdf, PDF page 2</pre>
                    <div data-testid="stExpander"><details><summary>View supporting passages</summary>
                    <p data-testid="stCaptionContainer">onboarding.pdf · PDF page 2</p>
                    <pre data-testid="stText">New starters collect laptops from Room 204.</pre>
                    </details></div></section>`;
                document.querySelector('[data-testid="stApp"]').setAttribute('data-test-script-state','notRunning');
            },100);
        }''')
        page.wait_for_function('window.__evaluation.done', timeout=6000)
        actual = page.evaluate('window.__evaluation')
        assert actual['outcome'] == 'COMPLETED'
        assert actual['elapsedSeconds'] >= 0.1
        assert actual['submitted'] < actual['ended']
        assert actual['chatMessageCount'] == 2
        assert actual['sources'][0]['caption'] == 'onboarding.pdf · PDF page 2'
        assert page.locator('details').get_attribute('open') is not None


def test_browser_watcher_refuses_prior_chat(offline_browser):
    browser = offline_browser
    if browser:
        page = browser.new_page()
        page.set_content('<div data-testid="stChatMessage">cached prior answer</div>')
        with pytest.raises(Exception, match='Fresh chat required'):
            page.evaluate(runner.ARM_RESPONSE, {'question': 'new question', 'timeoutMs': 5000})


def test_browser_watcher_times_completed_abstention_without_inventing_sources(offline_browser):
    page = offline_browser.new_page()
    page.set_content('''<main data-testid="stApp" data-test-script-state="notRunning">
        <textarea placeholder="Ask about your indexed PDFs"></textarea><div id="chat"></div></main>''')
    page.evaluate(runner.ARM_RESPONSE, {'question': 'An unsupported question?', 'timeoutMs': 5000})
    box = page.get_by_placeholder('Ask about your indexed PDFs')
    box.fill('An unsupported question?')
    box.press('Enter')
    page.evaluate('''() => {
        document.getElementById('chat').innerHTML=`
            <section data-testid="stChatMessage"><pre data-testid="stText">An unsupported question?</pre></section>
            <section data-testid="stChatMessage"><pre data-testid="stText">I could not find a supported answer in the uploaded documents.</pre></section>`;
    }''')
    page.wait_for_function('window.__evaluation.done', timeout=6000)
    actual = page.evaluate('window.__evaluation')
    assert actual['outcome'] == 'COMPLETED'
    assert actual['sources'] == []
    assert 0 < actual['elapsedSeconds'] < 5
    assert runner.latency_pass(actual['outcome'], actual['elapsedSeconds'])


def test_reset_waits_for_new_upload_generation_and_empty_chat(offline_browser):
    page = offline_browser.new_page()
    page.set_content('''<main data-testid="stApp" data-test-script-state="notRunning">
        <aside data-testid="stSidebar"><div class="st-key-uploads-0"><input type="file" disabled></div>
        <pre data-testid="stText">onboarding.pdf</pre></aside>
        <textarea placeholder="Ask about your indexed PDFs"></textarea>
        <div data-testid="stChatMessage">prior response</div>
        <button disabled>Index documents</button><button id="reset">Reset documents and chat</button></main>''')
    page.evaluate('''() => document.getElementById('reset').onclick=() => {
        // Preserve the previous notRunning frame while the reset is queued.
        window.resetClicked=performance.now();
        setTimeout(()=>{
            document.querySelector('[data-testid="stSidebar"]').innerHTML=
                '<div class="st-key-uploads-1"><input type="file"></div>';
            document.querySelector('textarea').disabled=true;
            document.querySelector('[data-testid="stChatMessage"]').remove();
            window.resetRendered=performance.now();
        },150);
    }''')
    runner.reset_document_boundary(page)
    observed = runner.failure_observation(page)
    assert observed['chatMessageCount'] == 0
    assert observed['uploadDisabled'] is False
    assert observed['questionDisabled'] is True
    assert observed['indexedFileNames'] == []
    assert page.evaluate('window.resetRendered-window.resetClicked') >= 140
    assert page.evaluate(runner.DOCUMENT_BOUNDARY, {'previousIdentity': 'st-key-uploads-0', 'expectedFiles': []})


def test_upload_boundary_requires_server_rendered_assigned_pdf_names(offline_browser):
    page = offline_browser.new_page()
    page.set_content('''<main data-testid="stApp" data-test-script-state="notRunning">
        <aside data-testid="stSidebar"><div class="st-key-uploads-1"><input type="file"></div></aside>
        <textarea placeholder="Ask about your indexed PDFs" disabled></textarea><button disabled>Index documents</button></main>''')
    expected = {'expectedFiles': ['travel.pdf']}
    assert not page.evaluate(runner.DOCUMENT_BOUNDARY, expected)
    page.evaluate('''() => {
        const filename=document.createElement('pre');filename.dataset.testid='stText';
        filename.innerText='travel.pdf';document.querySelector('aside').append(filename);
    }''')
    assert page.evaluate(runner.DOCUMENT_BOUNDARY, expected)
    assert not page.evaluate(runner.DOCUMENT_BOUNDARY, {'expectedFiles': ['onboarding.pdf']})


def test_browser_pacing_is_outside_response_timer_and_records_actual_interval(offline_browser):
    page = offline_browser.new_page()
    page.set_content('''<main data-testid="stApp" data-test-script-state="notRunning">
        <textarea placeholder="Ask about your indexed PDFs"></textarea><div id="chat"></div></main>''')
    previous = page.evaluate('({case_id:"H22",ended:performance.now(),time_origin:performance.timeOrigin})')
    pacing = runner.pace_before_submission(page, previous, 0.15)
    assert pacing['wait_seconds'] >= 0
    page.evaluate(runner.ARM_RESPONSE, {'question': 'Timed after pacing?', 'timeoutMs': 5000})
    box = page.get_by_placeholder('Ask about your indexed PDFs')
    box.fill('Timed after pacing?')
    box.press('Enter')
    page.evaluate('''() => {
        document.getElementById('chat').innerHTML=`
            <section data-testid="stChatMessage"><pre data-testid="stText">Timed after pacing?</pre></section>
            <section data-testid="stChatMessage"><pre data-testid="stText">Insufficient information.</pre></section>`;
    }''')
    page.wait_for_function('window.__evaluation.done', timeout=6000)
    observation = page.evaluate('window.__evaluation')
    actual = runner.finish_pacing(pacing, observation)
    assert actual['actual_interval_seconds'] >= 0.15
    assert actual['minimum_interval_met'] is True
    assert actual['included_in_response_seconds'] is False
    assert observation['elapsedSeconds'] == (observation['ended'] - observation['submitted']) / 1000
    assert observation['submitted'] >= previous['ended'] + 150


def test_diagnostic_markers_are_passive_and_do_not_invent_backend_timings(offline_browser):
    page = offline_browser.new_page()
    page.set_content('''<main data-testid="stApp" data-test-script-state="notRunning">
        <textarea placeholder="Ask about your indexed PDFs"></textarea><div id="chat"></div></main>''')
    page.evaluate(runner.ARM_RESPONSE, {'question': 'Diagnostic question?', 'timeoutMs': 5000})
    page.evaluate(runner.ARM_DIAGNOSTICS)
    box = page.get_by_placeholder('Ask about your indexed PDFs')
    box.fill('Diagnostic question?')
    box.press('Enter')
    page.evaluate('''() => {
        const app=document.querySelector('[data-testid="stApp"]');
        app.setAttribute('data-test-script-state','running');
        setTimeout(()=>{
            document.getElementById('chat').innerHTML=`
              <section data-testid="stChatMessage"><pre data-testid="stText">Diagnostic question?</pre></section>
              <section data-testid="stChatMessage"><pre data-testid="stText">Insufficient information.</pre></section>`;
            app.setAttribute('data-test-script-state','notRunning');
        },150);
    }''')
    page.wait_for_function('window.__evaluation.done', timeout=6000)
    observation = page.evaluate('window.__evaluation')
    diagnostic = runner.collect_diagnostics(page, observation)
    markers = diagnostic['observations']['markers']
    assert 0 <= markers['script_running_first_seen_seconds'] < markers['assistant_text_first_seen_seconds']
    assert markers['assistant_text_first_seen_seconds'] >= 0.14
    assert markers['assistant_text_first_seen_seconds'] <= observation['elapsedSeconds']
    assert 'supporting_passages_visible_first_seen_seconds' not in markers
    assert diagnostic['observations']['sampled_frames'] > 0
    assert diagnostic['response_end_seconds'] == observation['elapsedSeconds']
    assert observation['elapsedSeconds'] == (observation['ended'] - observation['submitted']) / 1000
    assert all(diagnostic[field] is None for field in (
        'backend_retrieval_seconds', 'query_embedding_seconds', 'chat_provider_seconds',
        'provider_internal_retries', 'render_cpu_seconds'))
    assert 'Insufficient information.' not in json.dumps(diagnostic)
