"""Opt-in paid provider smoke test using synthetic PDFs only. Run as a module."""
import json
import sys
from pathlib import Path
from src.knowledge_assistant.core import Upload, openai_assistant


def main():
    root = Path(__file__).resolve().parents[1]
    engine = openai_assistant()
    results = []
    try:
        engine.ingest([Upload('leave.pdf', (root / 'data/sample_pdfs/leave.pdf').read_bytes())])
        for question, expected in [('How many days of annual leave do employees receive?', 'answered'),
                                   ('What is the CEO salary?', 'not_found')]:
            answer, sources = engine.ask(question)
            results.append({'question': question, 'expected_status': expected,
                            'actual': answer.model_dump(),
                            'sources': {key: doc.metadata for key, doc in sources.items()},
                            'status_check_passed': answer.status == expected})
        print(json.dumps(results, indent=2))
        print('Review factual correctness and citation support manually; status checks alone are not an accuracy benchmark.')
        return 0 if all(row['status_check_passed'] for row in results) else 1
    finally:
        failure = sys.exception()
        try:
            engine.close()
        except Exception:
            if failure is None:
                raise
            print('Index cleanup also failed; restart the server before retrying.', file=sys.stderr)


if __name__ == '__main__':
    raise SystemExit(main())
