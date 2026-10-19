"""Validate fixture references, not live model answer quality."""
import json
from pathlib import Path
from pypdf import PdfReader


def test_pdf_evaluation_evidence_matches_actual_pages():
    root = Path(__file__).resolve().parents[1]
    cases = json.loads((root / 'evaluation/pdf_questions.json').read_text())
    assert len({case['id'] for case in cases}) == len(cases)
    assert {'answered', 'not_found', 'conflict'} == {c['expected_status'] for c in cases}
    for case in cases:
        for filename in case['files']:
            assert (root / 'data/sample_pdfs' / filename).is_file()
        for evidence in case['evidence']:
            assert evidence['filename'] in case['files']
            reader = PdfReader(root / 'data/sample_pdfs' / evidence['filename'], strict=True)
            assert evidence['text'] in reader.pages[evidence['page'] - 1].extract_text()
