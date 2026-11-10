"""Start from any working directory using this interpreter and project config."""
from pathlib import Path
import subprocess
import sys


def main():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run([sys.executable, str(root / 'scripts/preflight.py')], cwd=root)
    if result.returncode:
        return result.returncode
    try:
        return subprocess.call([sys.executable, '-m', 'streamlit', 'run', 'app.py',
                                '--server.address=127.0.0.1',
                                '--browser.gatherUsageStats=false'], cwd=root)
    except KeyboardInterrupt:
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
