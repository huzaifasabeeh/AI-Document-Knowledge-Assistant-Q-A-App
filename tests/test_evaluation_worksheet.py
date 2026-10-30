import json
import pytest
from scripts.prepare_evaluation import ROOT, main, prepare


def test_worksheet_keeps_expected_evidence_and_does_not_claim_success():
    cases = json.loads((ROOT / 'evaluation/pdf_questions.json').read_text())
    result = prepare(cases, 'candidate')
    assert result['candidate_commit'] == 'candidate'
    assert len(result['cases']) == 9
    for expected, row in zip(cases, result['cases']):
        assert row['expected_evidence'] == expected['evidence']
        assert row['status'] == 'Not run'
        assert row['supported_answer_pass'] is None
        assert row['citation_support_pass'] is None
        assert row['actual_answer'] is None


def test_existing_review_cannot_be_overwritten(tmp_path):
    output = tmp_path / 'review.json'
    output.write_text('existing review')
    with pytest.raises(FileExistsError):
        main(['--output', str(output)])
    assert output.read_text() == 'existing review'


def test_cli_creates_valid_unrun_worksheet(tmp_path):
    output = tmp_path / 'review.json'
    assert main(['--output', str(output)]) == 0
    assert json.loads(output.read_text())['status'] == 'Not run'
