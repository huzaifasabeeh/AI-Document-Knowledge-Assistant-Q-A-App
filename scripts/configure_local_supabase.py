"""Configure local Streamlit safely; optionally collect QA secrets in a local console."""
import argparse
import getpass
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import tomllib
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
SECRETS = ROOT / '.streamlit/secrets.toml'
CREDENTIALS = ROOT / 'data/private/local-test-credentials.json'
LOCAL_URL = 'http://127.0.0.1:54321'


def ignored(path):
    result = subprocess.run(['git', 'check-ignore', '--quiet', str(path)], cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError('Secret destination is not gitignored; stopped.')


def configure():
    ignored(SECRETS)
    if SECRETS.exists():
        existing = tomllib.loads(SECRETS.read_text(encoding='utf-8'))
        if (existing.get('SUPABASE_URL') != LOCAL_URL or
                not existing.get('SUPABASE_PUBLISHABLE_KEY', '').startswith('sb_publishable_')):
            raise RuntimeError('Existing secrets need local review; nothing overwritten.')
        print('Existing local secrets preserved.')
        return
    result = subprocess.run(['npx.cmd', 'supabase@2.122.0', 'status', '-o', 'json'],
                            cwd=ROOT, capture_output=True, text=True, check=False)
    if result.returncode:
        raise RuntimeError('Cannot discover local Supabase status; no secrets written.')
    status = json.loads(result.stdout)
    key = status.get('PUBLISHABLE_KEY', '')
    if status.get('API_URL') != LOCAL_URL or not key.startswith('sb_publishable_'):
        raise RuntimeError('Expected local API and publishable key were not found.')
    SECRETS.parent.mkdir(exist_ok=True)
    with SECRETS.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write('SUPABASE_URL = ' + json.dumps(LOCAL_URL) + '\n')
        stream.write('SUPABASE_PUBLISHABLE_KEY = ' + json.dumps(key) + '\n')
        stream.write('AI_PROVIDER = "gemini"\n')
    print('Local Supabase configured; Gemini selected. No secret values printed.')


def interactive_console():
    if not sys.stdin.isatty():
        raise RuntimeError('Use an interactive local console for hidden secret entry.')


def gemini_key(dialog=False):
    if dialog:
        import tkinter as tk
        from tkinter import simpledialog
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)
        try:
            value = simpledialog.askstring('Local Gemini setup',
                'Paste the Gemini API key here (masked). Only local configuration will change.',
                show='*', parent=root)
        finally:
            root.destroy()
    else:
        interactive_console()
        value = getpass.getpass('Optional Gemini API key (Enter to skip): ')
    value = (value or '').strip()
    if value and (not value.isascii() or not re.fullmatch(r'[A-Za-z0-9._-]{20,256}', value)):
        raise RuntimeError('Key contains invalid input characters; nothing saved. Use the masked dialog for paste.')
    return value


def write_gemini_configuration(original_bytes, updated, backup_prefix):
    """Back up the reviewed document and atomically replace it without stale writes."""
    ignored(SECRETS)
    if SECRETS.read_bytes() != original_bytes:
        raise RuntimeError('Local configuration changed; nothing overwritten.')
    CREDENTIALS.parent.mkdir(parents=True, exist_ok=True)
    backup = CREDENTIALS.parent / (backup_prefix + uuid4().hex + '.toml')
    ignored(backup)
    with backup.open('xb') as stream:
        stream.write(original_bytes)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='wb', dir=CREDENTIALS.parent,
                prefix='gemini-key-', suffix='.toml', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(updated.encode('utf-8'))
        if SECRETS.read_bytes() != original_bytes:
            raise RuntimeError('Local configuration changed; nothing overwritten.')
        os.replace(temporary, SECRETS)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def replace_gemini_key(key):
    """Replace one reviewed local field, backing up and preserving all other text."""
    original_bytes = SECRETS.read_bytes()
    original = original_bytes.decode('utf-8')
    before = tomllib.loads(original)
    if before.get('SUPABASE_URL') != LOCAL_URL or before.get('AI_PROVIDER') != 'gemini':
        raise RuntimeError('Only local Gemini configuration can be updated.')
    updated, count = re.subn(r'^GEMINI_API_KEY[ \t]*=[^\r\n]*',
                            lambda _: 'GEMINI_API_KEY = ' + json.dumps(key),
                            original, flags=re.MULTILINE)
    after = tomllib.loads(updated)
    if count != 1 or {**before, 'GEMINI_API_KEY': key} != after:
        raise RuntimeError('Key field is ambiguous; nothing overwritten.')
    write_gemini_configuration(original_bytes, updated, 'secrets-before-gemini-key-')


def collect_gemini(chat_model='', embedding_model='', dialog=False, replace_key=False):
    if not dialog:
        interactive_console()
    if bool(chat_model) != bool(embedding_model):
        raise RuntimeError('Provide both model IDs or neither; nothing written.')
    ignored(SECRETS)
    original_bytes = SECRETS.read_bytes()
    original = original_bytes.decode('utf-8')
    existing = tomllib.loads(original)
    if existing.get('SUPABASE_URL') != LOCAL_URL or existing.get('AI_PROVIDER') != 'gemini':
        raise RuntimeError('Only local Gemini configuration can be updated.')
    if replace_key:
        if not existing.get('GEMINI_API_KEY'):
            raise RuntimeError('No existing Gemini key to replace.')
        key = gemini_key(dialog)
        if key:
            replace_gemini_key(key)
            print('Local Gemini key updated; all other settings preserved. No secret values displayed.')
        return
    gemini = {}
    if not existing.get('GEMINI_API_KEY'):
        key = gemini_key(dialog)
        if key:
            gemini = {'GEMINI_API_KEY': key,
                      'GEMINI_CHAT_MODEL': chat_model or input('Gemini chat model ID: ').strip(),
                      'GEMINI_EMBEDDING_MODEL': embedding_model or input('Gemini embedding model ID: ').strip()}
            if not all(gemini.values()) or any(name in existing for name in gemini):
                raise RuntimeError('Missing model or existing setting; nothing overwritten.')
    if gemini:
        # Root assignments must precede any TOML tables. Prepending also keeps
        # existing multiline strings and a missing final newline intact.
        newline = '\r\n' if '\r\n' in original else '\n'
        additions = newline.join(name + ' = ' + json.dumps(value) for name, value in gemini.items())
        updated = additions + newline + newline + original
        if tomllib.loads(updated) != {**existing, **gemini}:
            raise RuntimeError('Gemini fields are ambiguous; nothing overwritten.')
        write_gemini_configuration(original_bytes, updated, 'secrets-before-gemini-settings-')
        print('Gemini settings saved locally. No secret values were displayed.')
    else:
        print('No Gemini settings changed.')


def collect():
    ignored(CREDENTIALS)
    if CREDENTIALS.exists():
        raise RuntimeError('QA credential file already exists; nothing overwritten.')
    interactive_console()
    print('Enter secrets here locally, never in chat. Password input is hidden.')
    passwords = {name: getpass.getpass(email + ' password: ') for name, email in (
        ('password_a', 'qa-a@example.com'), ('password_b', 'qa-b@example.com'))}
    if not all(passwords.values()):
        raise RuntimeError('Both QA passwords are required; nothing saved.')
    CREDENTIALS.parent.mkdir(parents=True, exist_ok=True)
    with CREDENTIALS.open('x', encoding='utf-8') as stream:
        json.dump(passwords, stream)
    collect_gemini()
    print('Local secret entry saved in gitignored files. You may close this console.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--collect-credentials', action='store_true')
    parser.add_argument('--collect-gemini', action='store_true',
                        help='Collect optional Gemini settings without asking for QA passwords again.')
    parser.add_argument('--chat-model', default='', help='Verified chat model ID; never an API key.')
    parser.add_argument('--embedding-model', default='', help='Verified embedding model ID; never an API key.')
    parser.add_argument('--key-dialog', action='store_true', help='Use a masked local paste dialog.')
    parser.add_argument('--replace-gemini-key', action='store_true',
                        help='Replace only the existing local Gemini key, preserving a private backup.')
    args = parser.parse_args()
    try:
        configure()
        if args.collect_credentials:
            collect()
        elif args.collect_gemini:
            collect_gemini(args.chat_model.strip(), args.embedding_model.strip(),
                           args.key_dialog, args.replace_gemini_key)
    except (RuntimeError, OSError, ValueError):
        print('STOP: Local configuration could not complete; inspect local file presence before retrying. No existing values were replaced.')
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
