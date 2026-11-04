"""Effective frozen configuration must be checked without making requests."""
from copy import deepcopy
from hashlib import sha256
import json
from unittest.mock import Mock

import pytest

from scripts import evaluation_configuration as settings
from scripts import run_browser_evaluation as runner
from scripts.prepare_evaluation import prepare


@pytest.fixture
def frozen(tmp_path):
    config = {'SUPABASE_URL': 'http://127.0.0.1:54321',
              'SUPABASE_PUBLISHABLE_KEY': 'sb_publishable_offline',
              'AI_PROVIDER': 'gemini', 'GEMINI_API_KEY': 'fake-private-api-key',
              'GEMINI_CHAT_MODEL': 'offline-chat', 'GEMINI_EMBEDDING_MODEL': 'offline-embedding'}
    execution = {'supabase_url': config['SUPABASE_URL'], 'selected_case_ids': ['H01'],
                 'inter_case_delay_seconds': 0.0, 'capture_provider_errors': False,
                 'browser_diagnostics': False, 'stage_timings': False, 'require_first_case_success': False}
    fingerprints = {'secret_values_saved_in_this_freeze': False}
    for name in settings.PRIVATE_FILES:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'offline private configuration fixture')
        fingerprints[name] = sha256(path.read_bytes()).hexdigest()
    freeze = {'configured_models': {'provider': 'gemini', 'chat_model': 'offline-chat',
                                   'embedding_model': 'offline-embedding'},
              'runtime_settings': settings.runtime_settings(), 'execution_settings': deepcopy(execution),
              'private_configuration_fingerprints': fingerprints}
    return tmp_path, freeze, config, execution


def test_valid_effective_settings_verify_without_mutating_freeze_or_recording_secrets(frozen):
    root, freeze, config, execution = frozen
    before = deepcopy(freeze)
    result = settings.verify_configuration(root, freeze, config, execution)
    assert result['status'] == 'VERIFIED'
    assert len(result['approved_configuration_sha256']) == 64
    assert freeze == before
    assert config['GEMINI_API_KEY'] not in json.dumps(result)
    assert config['SUPABASE_PUBLISHABLE_KEY'] not in json.dumps(result)


@pytest.mark.parametrize('section', ['configured_models', 'runtime_settings',
    'execution_settings', 'private_configuration_fingerprints'])
def test_missing_frozen_section_blocks(frozen, section):
    root, freeze, config, execution = frozen
    del freeze[section]
    with pytest.raises(settings.ConfigurationMismatch):
        settings.verify_configuration(root, freeze, config, execution)


@pytest.mark.parametrize(('section', 'field'), [
    ('configured_models', 'provider'), ('configured_models', 'chat_model'),
    ('configured_models', 'embedding_model'),
    *[('runtime_settings', key) for key in settings.runtime_settings()],
    *[('execution_settings', key) for key in sorted(settings.EXECUTION_FIELDS)],
])
def test_every_declared_runtime_field_is_checked(frozen, section, field):
    root, freeze, config, execution = frozen
    freeze[section][field] = 'mismatched-offline-value'
    with pytest.raises(settings.ConfigurationMismatch):
        settings.verify_configuration(root, freeze, config, execution)


@pytest.mark.parametrize('name', sorted(settings.PRIVATE_FILES))
def test_each_private_fingerprint_and_missing_file_is_checked(frozen, name):
    root, freeze, config, execution = frozen
    (root / name).write_bytes(b'changed private bytes')
    with pytest.raises(settings.ConfigurationMismatch, match='fingerprint mismatch'):
        settings.verify_configuration(root, freeze, config, execution)
    (root / name).unlink()
    with pytest.raises(settings.ConfigurationMismatch, match='unavailable'):
        settings.verify_configuration(root, freeze, config, execution)


@pytest.mark.parametrize('section', ['configured_models', 'runtime_settings', 'execution_settings'])
def test_unknown_or_missing_frozen_fields_are_not_silently_ignored(frozen, section):
    root, freeze, config, execution = frozen
    freeze[section]['unknown'] = 'not executable'
    with pytest.raises(settings.ConfigurationMismatch):
        settings.verify_configuration(root, freeze, config, execution)


def test_legacy_conflicting_conditions_cannot_override_effective_execution(frozen):
    root, freeze, config, execution = frozen
    freeze['continuation_conditions'] = {'stage_timings_enabled': True}
    with pytest.raises(settings.ConfigurationMismatch, match='Legacy'):
        settings.verify_configuration(root, freeze, config, execution)


def test_actual_shared_app_settings_are_checked_instead_of_separate_defaults(frozen, monkeypatch):
    root, freeze, config, execution = frozen
    monkeypatch.setattr(settings.core, 'RETRIEVAL_K', 99)
    with pytest.raises(settings.ConfigurationMismatch, match='runtime_settings'):
        settings.verify_configuration(root, freeze, config, execution)


@pytest.mark.parametrize('failure', ['model', 'fingerprint', 'missing_execution', 'runtime'])
def test_runner_stops_before_any_client_or_browser_on_configuration_failure(frozen, monkeypatch, failure):
    root, freeze, config, execution = frozen
    folder = root / 'logs/evaluation/offline'
    folder.mkdir(parents=True)
    prepare(folder / 'run.json')
    if failure == 'model':
        config['GEMINI_CHAT_MODEL'] = 'different-actual-model'
    elif failure == 'fingerprint':
        freeze['private_configuration_fingerprints']['.streamlit/secrets.toml'] = '0' * 64
    elif failure == 'runtime':
        freeze['runtime_settings']['sdk_max_retries'] = 9
    else:
        del freeze['execution_settings']
    path = folder / 'freeze.json'
    path.write_text(json.dumps(freeze), encoding='utf-8')
    original = path.read_bytes()
    monkeypatch.setattr(runner, 'ROOT', root)
    monkeypatch.setattr(runner, 'verify_freeze', lambda *args: None)  # Isolate config guard, not source hashes.
    monkeypatch.setattr(runner, 'load_local_configuration', lambda *args: config)
    monkeypatch.setattr(runner, 'load_test_credentials', lambda *args: {'password_a': 'fake-private-password'})
    auth, app = Mock(side_effect=AssertionError('No authentication request')), Mock(side_effect=AssertionError('No browser'))
    monkeypatch.setattr(runner, 'AuthClient', auth)
    monkeypatch.setattr(runner, 'LocalTestApp', app)
    result = runner.main(['--run-dir', 'logs/evaluation/offline', '--child-output',
                          'logs/local-verification/offline', '--case-ids', 'H01'])
    assert result == 1
    record = json.loads((folder / 'run.json').read_text())
    assert record['run_status'] == 'BLOCKED'
    assert record['blocker']['step'] == 'frozen runtime configuration verification'
    auth.assert_not_called()
    app.assert_not_called()
    assert path.read_bytes() == original
    assert not (folder / 'attempts').exists()
    assert all(case['status'] == 'Not run' for case in record['cases'])
