"""Fail-closed, offline verification of the effective local evaluation settings."""
from hashlib import sha256
import json
import math
from pathlib import Path

from src.knowledge_assistant import core, providers


class ConfigurationMismatch(ValueError):
    """Messages identify only a fixed section, never secret values."""


def runtime_settings():
    # These constants are used by the app itself, not independent test defaults.
    return {'system_prompt_sha256': sha256(core.SYSTEM.encode()).hexdigest(),
            'chunk_size': core.CHUNK_SIZE, 'chunk_overlap': core.CHUNK_OVERLAP,
            'retrieval_k': core.RETRIEVAL_K, 'sdk_max_retries': providers.SDK_MAX_RETRIES,
            'chat_timeout_seconds': providers.CHAT_TIMEOUT_SECONDS,
            'embedding_timeout_seconds': providers.EMBEDDING_TIMEOUT_SECONDS}


EXECUTION_FIELDS = {'supabase_url', 'selected_case_ids', 'inter_case_delay_seconds',
                    'capture_provider_errors', 'browser_diagnostics', 'stage_timings',
                    'require_first_case_success'}
PRIVATE_FILES = {'.streamlit/secrets.toml', 'data/private/local-test-credentials.json'}


def _same(expected, actual):
    if isinstance(actual, dict):
        return (isinstance(expected, dict) and expected.keys() == actual.keys()
                and all(_same(expected[k], v) for k, v in actual.items()))
    if isinstance(actual, list):
        return (isinstance(expected, list) and len(expected) == len(actual)
                and all(_same(a, b) for a, b in zip(expected, actual)))
    if type(actual) in (int, float):
        return (type(expected) in (int, float) and math.isfinite(expected)
                and expected == actual)
    return type(expected) is type(actual) and expected == actual


def verify_configuration(root, freeze, config, execution):
    """No client construction, request, freeze mutation or secret serialization."""
    root = Path(root).resolve()
    if freeze.get('continuation_conditions'):
        raise ConfigurationMismatch('Legacy mixed continuation conditions require a separately approved execution-settings freeze.')
    effective = providers.provider_config(config.get)
    if not effective.ready or effective.provider != 'gemini':
        raise ConfigurationMismatch('Local provider configuration is incomplete.')
    if set(execution) != EXECUTION_FIELDS or execution.get('supabase_url') != 'http://127.0.0.1:54321':
        raise ConfigurationMismatch('Effective execution settings are incomplete or nonlocal.')
    actual = {'configured_models': {'provider': effective.provider,
              'chat_model': effective.chat_model, 'embedding_model': effective.embedding_model},
              'runtime_settings': runtime_settings(), 'execution_settings': execution}
    for section, fields in actual.items():
        if not _same(freeze.get(section), fields):
            raise ConfigurationMismatch('Missing or mismatched frozen ' + section + '.')
    fingerprints = freeze.get('private_configuration_fingerprints')
    if (not isinstance(fingerprints, dict) or not PRIVATE_FILES <= fingerprints.keys()
            or fingerprints.get('secret_values_saved_in_this_freeze') is not False):
        raise ConfigurationMismatch('Missing or invalid frozen private configuration fingerprints.')
    actual_fingerprints = {'secret_values_saved_in_this_freeze': False}
    for relative, expected in fingerprints.items():
        if relative == 'secret_values_saved_in_this_freeze':
            continue
        if (not isinstance(expected, str) or len(expected) != 64
                or any(c not in '0123456789abcdef' for c in expected)):
            raise ConfigurationMismatch('Invalid frozen private configuration fingerprint.')
        path = (root / relative).resolve()
        if not path.is_relative_to(root):
            raise ConfigurationMismatch('Frozen private configuration path is outside the project.')
        try:
            actual_fingerprints[relative] = sha256(path.read_bytes()).hexdigest()
        except OSError:
            raise ConfigurationMismatch('Frozen private configuration file is unavailable.') from None
        if actual_fingerprints[relative] != expected:
            raise ConfigurationMismatch('Frozen private configuration fingerprint mismatch.')
    actual['private_configuration_fingerprints'] = actual_fingerprints
    digest = sha256(json.dumps(actual, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
    return {'status': 'VERIFIED', 'approved_configuration_sha256': digest,
            'verified_sections': sorted(actual), 'verified_configuration': actual}
