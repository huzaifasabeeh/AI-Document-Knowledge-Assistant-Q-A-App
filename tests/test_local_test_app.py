"""Controlled browser launch tests use fake config and owned mocked processes."""
from pathlib import Path
import subprocess
import sys
from unittest.mock import Mock, MagicMock

import pytest

from scripts import local_test_app as local
from scripts.local_gemini_smoke import QUESTION, require, verify_answer


@pytest.fixture
def config():
    return {'SUPABASE_URL': local.LOCAL_API,
            'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_offline_test',
            'AI_PROVIDER': 'gemini', 'GEMINI_API_KEY': 'fake-local-gemini-key',
            'GEMINI_CHAT_MODEL': 'test-chat', 'GEMINI_EMBEDDING_MODEL': 'test-embedding'}


@pytest.fixture
def launch(tmp_path, monkeypatch, config):
    monkeypatch.setattr(local, 'WINDOWS', False)
    process = Mock()
    process.poll.return_value = None
    popen = Mock(return_value=process)
    monkeypatch.setattr(local.subprocess, 'Popen', popen)
    monkeypatch.setattr(local, '_available_port', lambda: 49123)
    response = MagicMock()
    response.__enter__.return_value = response
    response.status, response.read.return_value = 200, b'ok'
    opener = Mock()
    opener.open.return_value = response
    factory = Mock(return_value=opener)
    monkeypatch.setattr(local, 'build_opener', factory)
    monkeypatch.setattr(local.time, 'sleep', lambda seconds: None)
    output = tmp_path / 'logs/local-verification/owned-run'
    app = local.LocalTestApp(tmp_path, output, config)
    yield app, process, popen, response, opener, factory
    app.stop()


def test_child_pins_local_settings_and_removes_inherited_services(config):
    inherited = {'PATH': 'keep-system-path', 'SUPABASE_URL': 'https://production.example',
                 'SUPABASE_SERVICE_ROLE_KEY': 'never-forward', 'OpenAI_API_KEY': 'never-forward',
                 'Gemini_API_KEY': 'never-forward', 'AI_PROVIDER': 'openai',
                 'STREAMLIT_SECRETS_FILES': 'unrelated-secrets.toml'}
    environment = local.child_environment(config, inherited)
    assert environment['SUPABASE_URL'] == local.LOCAL_API
    assert environment['GEMINI_API_KEY'] == config['GEMINI_API_KEY']
    assert environment['AI_PROVIDER'] == 'gemini'
    assert environment['OPENAI_API_KEY'] == ''
    assert environment['PATH'] == 'keep-system-path'
    assert 'never-forward' not in environment.values()
    assert 'STREAMLIT_SECRETS_FILES' not in environment
    assert inherited['AI_PROVIDER'] == 'openai'


@pytest.mark.parametrize('change', [
    {'SUPABASE_URL': 'https://production.example'},
    {'SUPABASE_URL': 'http://192.168.1.20:54321'},
    {'SUPABASE_PUBLISHABLE_KEY': 'sb_secret_never-use'},
    {'AI_PROVIDER': 'openai'},
    {'GEMINI_API_KEY': 123},
])
def test_invalid_configuration_blocks_before_launch(tmp_path, monkeypatch, config, change):
    popen = Mock()
    monkeypatch.setattr(local.subprocess, 'Popen', popen)
    with pytest.raises(local.LocalSetupBlocked):
        local.LocalTestApp(tmp_path, tmp_path / 'logs/local-verification/test', {**config, **change})
    popen.assert_not_called()


def test_missing_or_malformed_inputs_are_blocked_without_echo(tmp_path):
    for function in [local.load_local_configuration, lambda root: local.load_test_credentials(root, ('a',))]:
        with pytest.raises(local.LocalSetupBlocked):
            function(tmp_path)
    path = tmp_path / 'data/private/local-test-credentials.json'
    path.parent.mkdir(parents=True)
    path.write_text('{"password_a": "fake-secret-that-must-not-appear",', encoding='utf-8')
    with pytest.raises(local.LocalSetupBlocked) as caught:
        local.load_test_credentials(tmp_path, ('a',))
    assert 'fake-secret-that-must-not-appear' not in str(caught.value)
    path.write_text('{"password_a": ""}', encoding='utf-8')
    with pytest.raises(local.LocalSetupBlocked):
        local.load_test_credentials(tmp_path, ('a',))


def test_start_uses_owned_loopback_app_and_explicit_empty_secrets(launch, config):
    app, process, popen, response, opener, factory = launch
    assert app.start() is app
    command = popen.call_args.args[0]
    assert '--server.address=127.0.0.1' in command
    assert '--server.port=49123' in command
    assert '--server.headless=true' in command
    assert '--browser.gatherUsageStats=false' in command
    secrets_path = Path(command[command.index('--secrets.files') + 1])
    assert secrets_path.is_relative_to(app.output)
    assert 'API_KEY' not in secrets_path.read_text(encoding='utf-8')
    assert config['GEMINI_API_KEY'] not in ' '.join(command)
    assert popen.call_args.kwargs['env']['GEMINI_API_KEY'] == config['GEMINI_API_KEY']
    assert popen.call_args.kwargs['cwd'] == app.root
    assert app.url.startswith('http://127.0.0.1:49123/local-check-')
    opener.open.assert_called_once_with(app.url + '/_stcore/health', timeout=1)
    handlers = factory.call_args.args
    assert any(isinstance(handler, local.ProxyHandler) and handler.proxies == {} for handler in handlers)
    assert local.NoRedirect in handlers
    log = app._log
    app.stop()
    process.terminate.assert_called_once()
    process.wait.assert_called_once_with(timeout=5)
    assert log.closed
    assert app._process is None
    # A second stop cannot terminate an unrelated process or reuse its PID.
    app.stop()
    process.terminate.assert_called_once()


def test_health_rejects_unrelated_app_and_stops_own_child(launch, monkeypatch):
    app, process, _, response, _, _ = launch
    response.read.return_value = b'<html>different'
    monkeypatch.setattr(local.time, 'monotonic', Mock(side_effect=[0, 0, 2]))
    with pytest.raises(TimeoutError):
        app.start(timeout=1)
    process.terminate.assert_called_once()
    assert app._log is None


def test_early_child_exit_does_not_touch_other_processes(launch):
    app, process, _, _, opener, _ = launch
    process.poll.return_value = 3
    with pytest.raises(RuntimeError, match='exited before'):
        app.start()
    opener.open.assert_not_called()
    process.terminate.assert_not_called()
    process.kill.assert_not_called()
    assert app._log is None


def test_unresponsive_own_child_is_killed_after_bounded_wait(launch):
    app, process, _, _, _, _ = launch
    app.start()
    process.wait.side_effect = [subprocess.TimeoutExpired('owned-streamlit', 5), 0]
    app.stop()
    process.terminate.assert_called_once()
    process.kill.assert_called_once()
    assert process.wait.call_count == 2
    assert app._log is None


def test_windows_stops_only_owned_live_process_tree(launch, monkeypatch):
    app, process, _, _, _, _ = launch
    app.start()
    monkeypatch.setattr(local, 'WINDOWS', True)
    process.pid = 24680
    run = Mock(return_value=Mock(returncode=0))
    monkeypatch.setattr(local.subprocess, 'run', run)
    app.stop()
    assert run.call_args.args[0] == ['taskkill', '/PID', '24680', '/T', '/F']
    assert run.call_args.kwargs['timeout'] == 10
    assert run.call_args.kwargs['stdout'] == subprocess.PIPE
    assert run.call_args.kwargs['stderr'] == subprocess.PIPE
    process.terminate.assert_not_called()
    process.kill.assert_not_called()
    process.wait.assert_called_once_with(timeout=5)
    assert app._process is None


def test_windows_failed_tree_stop_is_reported_and_log_closed(launch, monkeypatch):
    app, process, _, _, _, _ = launch
    app.start()
    monkeypatch.setattr(local, 'WINDOWS', True)
    run = Mock(return_value=Mock(returncode=1))
    monkeypatch.setattr(local.subprocess, 'run', run)
    with pytest.raises(RuntimeError, match='could not be stopped'):
        app.stop()
    assert app._log is None
    # Leave fixture teardown able to stop its mocked child.
    monkeypatch.setattr(local, 'WINDOWS', False)


def test_subprocess_start_failure_closes_private_log(launch):
    app, _, popen, _, _, _ = launch
    popen.side_effect = OSError('fake launch failure')
    with pytest.raises(OSError):
        app.start()
    assert app._log is None


def test_rejects_public_output_and_preserves_existing_artifacts(tmp_path, config):
    with pytest.raises(ValueError, match='ignored'):
        local.LocalTestApp(tmp_path, tmp_path / 'public-artifacts', config)
    output = tmp_path / 'logs/local-verification/previous-run'
    output.mkdir(parents=True)
    marker = output / 'child-app-secrets.toml'
    marker.write_text('Existing evidence.', encoding='utf-8')
    app = local.LocalTestApp(tmp_path, output, config)
    with pytest.raises(FileExistsError):
        app.start()
    assert marker.read_text(encoding='utf-8') == 'Existing evidence.'


def test_explicit_port_refuses_occupied_listener_before_process(tmp_path, monkeypatch, config):
    import socket
    popen = Mock()
    monkeypatch.setattr(local.subprocess, 'Popen', popen)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(('127.0.0.1', 0))
        listener.listen()
        port = listener.getsockname()[1]
        app = local.LocalTestApp(tmp_path, tmp_path / 'logs/local-verification/test', config, port=port)
        with pytest.raises(OSError):
            app.start()
        popen.assert_not_called()
        assert not app.output.exists()


def test_real_answer_validation_rejects_wrong_allowance_and_fabricated_passage():
    sample = Path(__file__).resolve().parents[1] / 'data/sample_pdfs/leave.pdf'
    answer = {'role': 'assistant', 'content': 'Employees receive 20 days.\nSources: leave.pdf, PDF page 1',
              'sources': [{'filename': 'leave.pdf', 'page': 1,
                           'text': 'Employees receive 20 days of annual leave.'}]}
    messages = [{'role': 'user', 'content': QUESTION}, answer]
    verify_answer(messages, sample)
    answer['sources'][0]['text'] = 'A fabricated 20 days supporting passage.'
    with pytest.raises(AssertionError, match='does not occur'):
        verify_answer(messages, sample)
    answer['content'] = 'Employees receive 99 days.\nSources: leave.pdf, PDF page 1'
    with pytest.raises(AssertionError, match='allowance'):
        verify_answer(messages, sample)
    with pytest.raises(AssertionError, match='explicit guard'):
        require(False, 'explicit guard')


def test_optimized_python_cannot_skip_local_or_result_guards():
    code = '''
from scripts.local_test_app import child_environment, LocalSetupBlocked
from scripts.local_gemini_smoke import require
try:
    child_environment({'SUPABASE_URL': 'https://production.example', 'AI_PROVIDER': 'gemini'}, {})
except LocalSetupBlocked:
    pass
else:
    raise RuntimeError('local boundary was skipped')
try:
    require(False, 'result validation')
except AssertionError:
    pass
else:
    raise RuntimeError('result validation was skipped')
'''
    result = subprocess.run([sys.executable, '-O', '-c', code], capture_output=True,
                            text=True, cwd=Path(__file__).resolve().parents[1], timeout=20)
    assert result.returncode == 0, result.stderr
