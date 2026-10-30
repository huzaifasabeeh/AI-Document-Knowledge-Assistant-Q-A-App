"""Owned, isolated Streamlit child for opt-in local browser verification.

The running user app is never inspected, restarted, or reused. Service settings
come only from validated project secrets, not the parent environment or global
Streamlit secrets. All child artifacts belong in ignored local evidence folders.
"""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import tomllib
from urllib.error import URLError
from urllib.request import ProxyHandler, build_opener
from uuid import uuid4

from src.knowledge_assistant.auth import AuthClient, AuthError, NoRedirect

LOCAL_API = 'http://127.0.0.1:54321'
WINDOWS = os.name == 'nt'
SERVICE_SETTINGS = (
    'SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY', 'AI_PROVIDER',
    'OPENAI_API_KEY', 'OPENAI_CHAT_MODEL', 'OPENAI_EMBEDDING_MODEL',
    'GEMINI_API_KEY', 'GEMINI_CHAT_MODEL', 'GEMINI_EMBEDDING_MODEL',
)


class LocalSetupBlocked(Exception):
    """Configuration or local test credentials are unavailable."""


def validate_local_configuration(config):
    if config.get('SUPABASE_URL') != LOCAL_API or config.get('AI_PROVIDER') != 'gemini':
        raise LocalSetupBlocked('Expected local Supabase and Gemini configuration.')
    if any(not isinstance(config.get(name, ''), str) for name in SERVICE_SETTINGS):
        raise LocalSetupBlocked('Local service configuration must contain text settings.')
    try:
        AuthClient(LOCAL_API, config.get('SUPABASE_PUBLISHABLE_KEY', ''))
    except AuthError:
        raise LocalSetupBlocked('A local public Supabase key is required.') from None


def load_local_configuration(root):
    try:
        config = tomllib.loads((Path(root) / '.streamlit/secrets.toml').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise LocalSetupBlocked('Local secrets are missing or invalid; use the secure setup helper.') from None
    validate_local_configuration(config)
    return config


def load_test_credentials(root, labels):
    try:
        credentials = json.loads((Path(root) / 'data/private/local-test-credentials.json').read_text(encoding='utf-8'))
        if not isinstance(credentials, dict) or any(
                not isinstance(credentials.get('password_' + label), str)
                or not credentials['password_' + label] for label in labels):
            raise ValueError()
    except (OSError, ValueError):
        raise LocalSetupBlocked('Local QA credentials are missing or invalid; use the secure setup helper.') from None
    return credentials


def child_environment(config, inherited=None):
    validate_local_configuration(config)
    inherited = os.environ if inherited is None else inherited
    # Windows environment names are case insensitive. Also discard unused
    # privileged credentials and Streamlit overrides rather than forwarding them.
    prefixes = ('SUPABASE_', 'OPENAI_', 'GEMINI_', 'STREAMLIT_')
    result = {name: value for name, value in inherited.items()
              if name.upper() != 'AI_PROVIDER' and not name.upper().startswith(prefixes)}
    result.update({name: config.get(name, '') for name in SERVICE_SETTINGS})
    result['PYTHONUNBUFFERED'] = '1'
    return result


def _available_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(('127.0.0.1', 0))
        return listener.getsockname()[1]


class LocalTestApp:
    def __init__(self, root, output, config, port=None):
        self.root, self.output = Path(root).resolve(), Path(output).resolve()
        allowed = self.root / 'logs/local-verification'
        if not self.output.is_relative_to(allowed) or self.output == allowed:
            raise ValueError('Child app output must be in its own ignored local verification folder.')
        self.environment = child_environment(config)
        if port is not None and (type(port) is not int or not 1024 <= port <= 65535):
            raise ValueError('Choose an unprivileged local port between 1024 and 65535.')
        self.port = port
        self.url = None
        self._process = self._log = None

    def start(self, timeout=45):
        if self._process is not None:
            raise RuntimeError('The controlled local app has already started.')
        # Refuse a busy user-selected port; never take over an existing app.
        if self.port is not None:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
                listener.bind(('127.0.0.1', self.port))
        self.output.mkdir(parents=True, exist_ok=True)
        # An empty explicit secrets file excludes both global and project secrets.
        # Nonempty service settings are pinned in the child environment instead.
        secrets = self.output / 'child-app-secrets.toml'
        with secrets.open('x', encoding='utf-8') as stream:
            stream.write('# Controlled local test app: settings arrive through its environment.\n')
        self._log = (self.output / 'child-streamlit.log').open('xb')
        try:
            port, route = self.port or _available_port(), 'local-check-' + uuid4().hex
            self.url = f'http://127.0.0.1:{port}/{route}'
            command = [sys.executable, '-m', 'streamlit', 'run', str(self.root / 'app.py'),
                       '--server.address=127.0.0.1', f'--server.port={port}',
                       f'--server.baseUrlPath={route}', '--server.headless=true',
                       '--server.fileWatcherType=none', '--browser.gatherUsageStats=false',
                       '--secrets.files', str(secrets)]
            self._process = subprocess.Popen(command, cwd=self.root, env=self.environment,
                                             stdin=subprocess.DEVNULL, stdout=self._log,
                                             stderr=subprocess.STDOUT)
            deadline = time.monotonic() + timeout
            opener = build_opener(ProxyHandler({}), NoRedirect)
            while time.monotonic() < deadline:
                if self._process.poll() is not None:
                    raise RuntimeError('Controlled local app exited before becoming healthy; inspect its ignored log.')
                try:
                    # The unique route and exact response avoid accepting another
                    # app if an unrelated process claims the selected port first.
                    with opener.open(self.url + '/_stcore/health', timeout=1) as response:
                        healthy = response.status == 200 and response.read(16) == b'ok'
                    if healthy and self._process.poll() is None:
                        return self
                except (URLError, OSError):
                    pass
                time.sleep(0.1)
            raise TimeoutError('Controlled local app did not become healthy within its startup timeout.')
        except BaseException:
            self.stop()
            raise

    def stop(self):
        try:
            if self._process is not None:
                if self._process.poll() is None:
                    if WINDOWS:
                        # The Windows venv executable can redirect to another
                        # Python process. Stop only this still-owned live tree,
                        # so its Streamlit child cannot become an orphan.
                        result = subprocess.run(
                            ['taskkill', '/PID', str(self._process.pid), '/T', '/F'],
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=10, check=False)
                        if result.returncode != 0 and self._process.poll() is None:
                            raise RuntimeError('The owned local app process tree could not be stopped.')
                        self._process.wait(timeout=5)
                    else:
                        self._process.terminate()
                        try:
                            self._process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            self._process.kill()
                            self._process.wait(timeout=5)
                self._process = None
        finally:
            if self._log is not None:
                self._log.close()
                self._log = None


def main():
    parser = argparse.ArgumentParser(description='Run a controlled local-only Streamlit app until Ctrl+C.')
    parser.add_argument('--port', type=int, help='Use an unoccupied local port; otherwise choose a temporary port.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    output = root / 'logs/local-verification' / ('local-app-' + stamp + '-' + uuid4().hex[:8])
    app = None
    try:
        app = LocalTestApp(root, output, load_local_configuration(root), port=args.port)
        app.start()
        print('Controlled local app:', app.url, flush=True)
        print('Child log:', output.relative_to(root) / 'child-streamlit.log', flush=True)
        print('Press Ctrl+C to stop this app. Existing app processes are preserved.', flush=True)
        while app._process.poll() is None:
            time.sleep(1)
        raise RuntimeError('Controlled local app exited.')
    except KeyboardInterrupt:
        return 0
    except LocalSetupBlocked:
        print('BLOCKED: Use the secure setup helper to configure local Supabase and Gemini.', flush=True)
        return 1
    except Exception as error:
        # Never echo raw subprocess/configuration exceptions or secret values.
        print('FAIL: Controlled local app could not continue (' + type(error).__name__ + ').', flush=True)
        return 1
    finally:
        if app is not None:
            app.stop()


if __name__ == '__main__':
    raise SystemExit(main())
