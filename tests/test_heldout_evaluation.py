"""Check benchmark integrity, never claim live answer quality."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import pytest
from pypdf import PdfReader
from scripts.prepare_evaluation import prepare

ROOT = Path(__file__).resolve().parents[1]


def test_heldout_distribution_and_physical_page_evidence():
    folder = ROOT / 'evaluation/heldout'
    cases = json.loads((folder/'questions.json').read_text())['cases']
    manifest = json.loads((folder/'manifest.json').read_text())
    assert len(cases) == len({c['id'] for c in cases}) == 40
    assert Counter(c['category'] for c in cases) == {
        'direct': 20, 'paraphrased': 5, 'multi_passage': 5, 'unanswerable': 10}
    for name, digest in manifest['pdf_sha256'].items():
        assert hashlib.sha256((ROOT/'data/heldout_pdfs'/name).read_bytes()).hexdigest() == digest
    for name in ('corpus.json', 'questions.json'):
        assert hashlib.sha256((folder/name).read_bytes()).hexdigest() == manifest[name+'_sha256']
    for case in cases:
        assert all((ROOT/'data/heldout_pdfs'/name).is_file() for name in case['files'])
        if case['category'] == 'unanswerable':
            assert case['expected_status'] == 'not_found'
            assert not case['evidence']
        else:
            assert case['expected_status'] == 'answered'
            assert case['evidence']
        for evidence in case['evidence']:
            assert evidence['filename'] in case['files']
            reader = PdfReader(ROOT/'data/heldout_pdfs'/evidence['filename'], strict=True)
            actual = ' '.join(reader.pages[evidence['page']-1].extract_text().split())
            assert evidence['text'] in actual
        if case['category'] == 'multi_passage':
            assert len({(e['filename'], e['page']) for e in case['evidence']}) >= 2


def test_blank_results_preserve_unknowns_and_refuse_overwrite(tmp_path):
    path = tmp_path/'run.json'
    result = prepare(path)
    assert result['run_status'] == 'Not run'
    assert result['ground_truth_approved_by'] is None
    assert len(result['cases']) == 40
    assert all(c['pass'] is None and c['answer_seconds'] is None for c in result['cases'])
    original = path.read_bytes()
    with pytest.raises(FileExistsError):
        prepare(path)
    assert path.read_bytes() == original
