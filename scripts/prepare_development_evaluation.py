"""Create a review worksheet without calling a provider or grading answers."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def prepare(cases, commit):
    return {
        'created_at': datetime.now(timezone.utc).isoformat(),
        'candidate_commit': commit,
        'chat_model': None,
        'embedding_model': None,
        'reviewer': None,
        'status': 'Not run',
        'cases': [{
            'id': case['id'], 'files': case['files'],
            'question': case['question'],
            'expected_status': case['expected_status'],
            'expected_answer': case['expected_answer'],
            'expected_evidence': case['evidence'],
            'actual_answer': None, 'actual_sources': [], 'latency_seconds': None,
            'supported_answer_pass': None, 'citation_support_pass': None,
            'review_notes': '', 'status': 'Not run',
        } for case in cases],
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args(argv)
    cases = json.loads((ROOT / 'evaluation/pdf_questions.json').read_text())
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    # Exclusive creation protects prior human review evidence from overwrites.
    with args.output.open('x', encoding='utf-8') as handle:
        json.dump(prepare(cases, commit), handle, indent=2)
        handle.write('\n')
    print(f'Prepared {len(cases)} unrun cases: {args.output}')
    print('No API calls made. Fill actual results and obtain reviewer sign-off separately.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
