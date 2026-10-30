"""Create a review worksheet without calling a provider or grading answers."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
"""Create a blank evaluation record without running models or overwriting results."""
import argparse
import hashlib
import json
from pathlib import Path

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
def prepare(output):
    folder = ROOT / 'evaluation/heldout'
    cases = json.loads((folder/'questions.json').read_text())['cases']
    manifest = json.loads((folder/'manifest.json').read_text())
    for name in ('corpus.json', 'questions.json'):
        if hashlib.sha256((folder/name).read_bytes()).hexdigest() != manifest[name+'_sha256']:
            raise ValueError('Evaluation inputs changed. Review and regenerate the candidate manifest first.')
    for name, expected in manifest['pdf_sha256'].items():
        if hashlib.sha256((ROOT/'data/heldout_pdfs'/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Evaluation PDF differs from the candidate manifest.')
    result = {
        'benchmark_version': manifest['version'], 'manifest': manifest,
        'run_status': 'Not run', 'ground_truth_approved_by': None,
        'ground_truth_approved_at': None, 'commit': None, 'deployed_revision': None,
        'provider': None, 'chat_model': None, 'embedding_model': None,
        'prompt_revision': None, 'chunk_settings': None, 'environment': None,
        'tester': None, 'started_at': None, 'currency': None,
        'cases': [{
            'id': c['id'], 'category': c['category'], 'files': c['files'],
            'question': c['question'], 'status': 'Not run', 'actual_answer': None,
            'retrieved_sources': None, 'cited_sources': None,
            'indexing_seconds': None, 'answer_seconds': None,
            'manual_search_seconds': None, 'comparison_order': None,
            'input_tokens': None, 'output_tokens': None, 'embedding_tokens': None,
            'cost': None, 'fully_correct_supported': None,
            'factual_claims': None, 'claims_with_citations': None,
            'citation_pairs': None, 'supported_citation_pairs': None,
            'appropriate_abstention': None, 'pass': None, 'reviewer': None,
            'notes': None,
        } for c in cases],
    }
    # Exclusive creation protects earlier result logs.
    with Path(output).open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.output)
    print('Blank record created. No API calls made; all results are Not run.')
