import json
import pytest
from scripts.prepare_development_evaluation import ROOT, main, prepare


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


def test_development_and_heldout_commands_stay_separate(tmp_path):
    from scripts.prepare_evaluation import prepare as heldout_prepare
    development = tmp_path / 'development.json'
    heldout = tmp_path / 'heldout.json'
    assert main(['--output', str(development)]) == 0
    heldout_prepare(heldout)
    assert len(json.loads(development.read_text())['cases']) == 9
    assert len(json.loads(heldout.read_text())['cases']) == 40
    with pytest.raises(FileExistsError):
        heldout_prepare(heldout)


def test_development_cli_runs_in_a_fresh_interpreter(tmp_path):
    import subprocess
    import sys
    output = tmp_path / 'cli.json'
    result = subprocess.run([sys.executable, '-m', 'scripts.prepare_development_evaluation',
                             '--output', str(output)], cwd=ROOT, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert len(json.loads(output.read_text())['cases']) == 9
