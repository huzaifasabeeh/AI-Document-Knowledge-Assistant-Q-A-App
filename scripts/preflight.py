"""Check local startup prerequisites without importing the app or calling APIs."""
import argparse
from importlib.metadata import PackageNotFoundError, version
import os
from pathlib import Path
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--require-api-key', action='store_true',
                        help='Fail if server environment has no API key.')
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    problems = []
    print('Local prerequisite check — no network requests or API charges.')
    print(f'Python: {sys.version.split()[0]}')
    for line in (root / 'requirements.txt').read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        name, expected = line.split('==', 1)
        try:
            installed = version(name)
        except PackageNotFoundError:
            problems.append(f'{name}: missing')
            continue
        if installed != expected:
            problems.append(f'{name}: installed {installed}; pinned {expected}')
        else:
            print(f'OK: {name} {installed}')
    has_key = bool(os.environ.get('OPENAI_API_KEY', '').strip())
    print('API key: ' + ('configured (value hidden)' if has_key else 'not configured'))
    if args.require_api_key and not has_key:
        problems.append('Set OPENAI_API_KEY in the server environment for AI mode.')
    if not has_key:
        print('Local PDF preview does not need an API key.')
    print('This does not verify credits, model access, AI quality or deployment readiness.')
    if problems:
        for problem in problems:
            print(f'ACTION: {problem}')
        print('Install project dependencies using: python -m pip install -r requirements.txt')
        return 1
    print('Prerequisites present. Start from the repository root: python -m streamlit run app.py')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
