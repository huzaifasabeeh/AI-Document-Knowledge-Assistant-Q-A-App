"""Local configuration checks use fake credentials and temporary files only."""
import os
import tomllib

import pytest

from scripts import configure_local_supabase as local


@pytest.fixture
def configuration(tmp_path, monkeypatch):
    monkeypatch.setattr(local, 'ROOT', tmp_path)
    monkeypatch.setattr(local, 'SECRETS', tmp_path / '.streamlit/secrets.toml')
    monkeypatch.setattr(local, 'CREDENTIALS', tmp_path / 'data/private/credentials.json')
    monkeypatch.setattr(local, 'ignored', lambda path: None)
    monkeypatch.setattr(local, 'interactive_console', lambda: None)

    def unexpected_subprocess(*args, **kwargs):
        pytest.fail('Offline configuration checks must not launch subprocesses.')

    monkeypatch.setattr(local.subprocess, 'run', unexpected_subprocess)

    def write(key=None, url=local.LOCAL_URL, newline='\n', models=True, final_newline=True):
        text = (
            '# Keep this local configuration comment.\n'
            f'SUPABASE_URL = "{url}"\n'
            'SUPABASE_PUBLISHABLE_KEY = "sb_publishable_fake_for_offline_tests"\n'
            'AI_PROVIDER = "gemini"\n'
        )
        if models:
            text += ('GEMINI_CHAT_MODEL = "existing-chat-model"\n'
                     'GEMINI_EMBEDDING_MODEL = "existing-embedding-model"\n')
        if key is not None:
            text += f'GEMINI_API_KEY = "{key}"\n'
        text += '\n[appearance]\ntheme = "dark"\n'
        if not final_newline:
            text = text.rstrip('\n')
        original = text.replace('\n', newline).encode('utf-8')
        local.SECRETS.parent.mkdir(parents=True, exist_ok=True)
        local.SECRETS.write_bytes(original)
        return original

    return write


@pytest.mark.parametrize('pasted', [
    'fake-key-prefix-123456789\x16suffix',
    'fake-key-prefix-123456789\nsuffix',
    'fake-key-prefix-123456789\tsuffix',
    'fake-key-prefix-123456789\u00e9',
    'fake-key-prefix-123456789/suffix',
    'A' * 19,
    'A' * 257,
], ids=['console-control', 'embedded-newline', 'embedded-tab', 'non-ascii',
        'invalid-symbol', 'too-short', 'too-long'])
def test_malformed_console_paste_is_not_echoed_or_saved(configuration, monkeypatch, capsys, pasted):
    original = configuration()
    monkeypatch.setattr(local.getpass, 'getpass', lambda prompt: pasted)
    monkeypatch.setattr(local.sys, 'argv', ['configure_local_supabase.py', '--collect-gemini'])

    with pytest.raises(RuntimeError, match='Key contains invalid input characters') as error:
        local.gemini_key()
    assert pasted not in str(error.value)
    assert local.main() == 1

    output = capsys.readouterr()
    assert pasted not in output.out + output.err
    assert 'STOP: Local configuration could not complete' in output.out
    assert local.SECRETS.read_bytes() == original
    assert not local.CREDENTIALS.parent.exists()


@pytest.mark.parametrize('entered, expected', [
    ('  ' + 'A' * 20 + '  ', 'A' * 20),
    ('B' * 256, 'B' * 256),
    ('', ''),
], ids=['trimmed-minimum', 'maximum', 'optional-skip'])
def test_masked_console_accepts_valid_key_or_skip(configuration, monkeypatch, capsys, entered, expected):
    monkeypatch.setattr(local.getpass, 'getpass', lambda prompt: entered)

    assert local.gemini_key() == expected
    assert capsys.readouterr().out == ''


def test_key_replacement_preserves_settings_and_original_private_backup(configuration, monkeypatch, capsys):
    old_key = 'fake-original-key-123456789'
    new_key = 'fake-replacement-key-987654321'
    original = configuration(old_key, newline='\r\n')
    before = tomllib.loads(original.decode('utf-8'))
    replace_calls = []
    actual_replace = os.replace

    def atomic_replace(source, destination):
        # The original remains intact until the completed temporary file moves.
        assert local.SECRETS.read_bytes() == original
        assert source.parent == local.CREDENTIALS.parent
        assert destination == local.SECRETS
        assert tomllib.loads(source.read_text(encoding='utf-8'))['GEMINI_API_KEY'] == new_key
        replace_calls.append((source, destination))
        return actual_replace(source, destination)

    monkeypatch.setattr(local.os, 'replace', atomic_replace)

    local.replace_gemini_key(new_key)

    assert len(replace_calls) == 1
    after = tomllib.loads(local.SECRETS.read_text(encoding='utf-8'))
    assert after == {**before, 'GEMINI_API_KEY': new_key}
    assert local.SECRETS.read_bytes() == original.replace(old_key.encode(), new_key.encode())
    backups = list(local.CREDENTIALS.parent.glob('secrets-before-gemini-key-*.toml'))
    assert len(backups) == 1
    assert backups[0].read_bytes() == original
    assert not list(local.CREDENTIALS.parent.glob('gemini-key-*.toml'))
    output = capsys.readouterr()
    assert old_key not in output.out + output.err
    assert new_key not in output.out + output.err


def test_key_replacement_refuses_nonlocal_configuration(configuration):
    original = configuration('fake-original-key-123456789', url='https://example.supabase.co')

    with pytest.raises(RuntimeError, match='Only local Gemini configuration'):
        local.replace_gemini_key('fake-replacement-key-987654321')

    assert local.SECRETS.read_bytes() == original
    assert not local.CREDENTIALS.parent.exists()


def test_existing_gemini_settings_are_preserved_without_explicit_replacement(configuration, monkeypatch, capsys):
    original = configuration('fake-original-key-123456789')

    def unexpected_key_prompt(*args, **kwargs):
        pytest.fail('Existing Gemini settings must not trigger another key prompt.')

    monkeypatch.setattr(local, 'gemini_key', unexpected_key_prompt)

    local.collect_gemini(chat_model='different-chat-model', embedding_model='different-embedding-model')

    assert local.SECRETS.read_bytes() == original
    assert not local.CREDENTIALS.parent.exists()
    assert capsys.readouterr().out == 'No Gemini settings changed.\n'


@pytest.mark.parametrize('newline', ['\n', '\r\n'], ids=['lf', 'crlf'])
@pytest.mark.parametrize('final_newline', [True, False], ids=['final-newline', 'no-final-newline'])
def test_new_gemini_settings_stay_at_root_before_existing_tables(
        configuration, monkeypatch, capsys, newline, final_newline):
    original = configuration(models=False, newline=newline, final_newline=final_newline)
    before = tomllib.loads(original.decode('utf-8'))
    key = 'fake-collected-key-123456789'
    monkeypatch.setattr(local.getpass, 'getpass', lambda prompt: key)

    local.collect_gemini(chat_model='new-chat-model', embedding_model='new-embedding-model')

    updated = local.SECRETS.read_bytes()
    expected_fields = {'GEMINI_API_KEY': key, 'GEMINI_CHAT_MODEL': 'new-chat-model',
                       'GEMINI_EMBEDDING_MODEL': 'new-embedding-model'}
    assert tomllib.loads(updated.decode('utf-8')) == {**before, **expected_fields}
    assert updated.endswith(original)
    assert updated.index(b'GEMINI_API_KEY') < updated.index(b'[appearance]')
    backups = list(local.CREDENTIALS.parent.glob('secrets-before-gemini-settings-*.toml'))
    assert len(backups) == 1 and backups[0].read_bytes() == original
    assert not list(local.CREDENTIALS.parent.glob('gemini-key-*.toml'))
    output = capsys.readouterr()
    assert key not in output.out + output.err
    assert 'Gemini settings saved locally.' in output.out


def test_new_root_settings_preserve_nested_fields_and_multiline_text(configuration, monkeypatch):
    original = configuration(models=False, final_newline=False)
    # Brackets inside a multiline value must not be mistaken for a table header.
    original = original.replace(b'AI_PROVIDER = "gemini"',
        b'AI_PROVIDER = "gemini"\nnote = """keep this text\n[not_a_table]\nunchanged"""')
    original += b'\nGEMINI_API_KEY = "nested-field-must-stay"'
    local.SECRETS.write_bytes(original)
    before = tomllib.loads(original.decode('utf-8'))
    monkeypatch.setattr(local.getpass, 'getpass', lambda prompt: 'fake-collected-key-123456789')

    local.collect_gemini(chat_model='new-chat-model', embedding_model='new-embedding-model')

    after = tomllib.loads(local.SECRETS.read_text(encoding='utf-8'))
    assert after['GEMINI_API_KEY'] == 'fake-collected-key-123456789'
    assert after['appearance'] == before['appearance']
    assert after['note'] == before['note']
    assert local.SECRETS.read_bytes().endswith(original)


@pytest.mark.parametrize('replace_existing', [True, False], ids=['replace-key', 'collect-settings'])
def test_failed_atomic_write_preserves_original_and_backup_without_temporary_secrets(
        configuration, monkeypatch, replace_existing):
    original = configuration('fake-original-key-123456789') if replace_existing else configuration(models=False)

    def fail_replace(*args):
        raise OSError('Simulated atomic replacement failure')

    monkeypatch.setattr(local.os, 'replace', fail_replace)
    monkeypatch.setattr(local.getpass, 'getpass', lambda prompt: 'fake-collected-key-123456789')

    with pytest.raises(OSError, match='Simulated atomic replacement failure'):
        if replace_existing:
            local.replace_gemini_key('fake-replacement-key-987654321')
        else:
            local.collect_gemini(chat_model='new-chat-model', embedding_model='new-embedding-model')

    assert local.SECRETS.read_bytes() == original
    backups = list(local.CREDENTIALS.parent.glob('secrets-before-gemini-*.toml'))
    assert len(backups) == 1 and backups[0].read_bytes() == original
    assert not list(local.CREDENTIALS.parent.glob('gemini-key-*.toml'))


def test_new_gemini_collection_refuses_nonlocal_configuration(configuration, monkeypatch):
    original = configuration(url='https://example.supabase.co', models=False)
    monkeypatch.setattr(local.getpass, 'getpass', lambda prompt: pytest.fail('Must reject before asking for secrets'))

    with pytest.raises(RuntimeError, match='Only local Gemini configuration'):
        local.collect_gemini(chat_model='new-chat-model', embedding_model='new-embedding-model')

    assert local.SECRETS.read_bytes() == original
    assert not local.CREDENTIALS.parent.exists()
