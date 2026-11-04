"""Acceptance metrics must preserve missing evidence and the exact deadline."""
import json

import pytest

from scripts.summarize_evaluation import (
    CASE_IDS, TIMING_CLOCK, TIMING_SCOPE, summarize, summarize_records,
)


def complete_records(seconds=10.0):
    run = {
        'cases': [{
            'id': case_id, 'status': 'Completed', 'actual_answer': 'Synthetic response',
            'answer_seconds': seconds,
        } for case_id in CASE_IDS],
        'timing_scope': TIMING_SCOPE, 'timing_clock': TIMING_CLOCK,
    }
    grades = {'cases': [{
        'id': case_id, 'fully_correct_supported': True,
        'appropriate_abstention': True,
        'factual_claims': 1, 'claims_with_citations': 1,
        'citation_pairs': 1, 'supported_citation_pairs': 1,
    } for case_id in CASE_IDS]}
    return run, grades


@pytest.mark.parametrize('seconds, passed', [(10.0, True), (10.000001, False)])
def test_exact_each_response_deadline(seconds, passed):
    run, grades = complete_records()
    run['cases'][-1]['answer_seconds'] = seconds
    result = summarize_records(run, grades)
    assert result['latency']['pass'] is passed
    assert result['acceptance']['full_set_pass'] is passed
    assert result['latency']['p95_nearest_rank_seconds'] == 10.0
    assert result['latency']['exceeded_deadline_ids'] == ([] if passed else ['H40'])


@pytest.mark.parametrize('seconds', [None, -1, float('inf'), float('nan'), True, '9.0'])
def test_missing_or_invalid_timing_cannot_pass(seconds):
    run, grades = complete_records()
    run['cases'][0]['answer_seconds'] = seconds
    result = summarize_records(run, grades)
    assert result['latency']['pass'] is False
    assert result['latency']['missing_completed_timing_ids'] == ['H01']
    assert result['latency']['timed_completed_count'] == 39


@pytest.mark.parametrize('status', [
    'TECHNICAL_ERROR', 'TIMEOUT', 'SUBMITTED_OUTCOME_UNCONFIRMED', 'Not run',
])
def test_uncompleted_case_cannot_pass_latency_or_use_success_grade(status):
    run, grades = complete_records()
    run['cases'][0]['status'] = status
    result = summarize_records(run, grades)
    assert result['latency']['pass'] is False
    assert result['latency']['completed_response_count'] == 39
    assert result['quality']['answer_correctness']['numerator'] == 29
    assert result['quality']['answer_correctness']['denominator'] == 30
    assert result['quality']['answer_correctness']['ratio'] == (
        29 / 30 if status in {'TECHNICAL_ERROR', 'TIMEOUT'} else None)
    assert result['outcomes']['excluded_noncompleted_grade_ids'] == ['H01']


def test_failed_requests_are_not_supported_abstentions():
    run, grades = complete_records()
    run['cases'][-1]['status'] = 'TECHNICAL_ERROR'
    result = summarize_records(run, grades)
    metric = result['quality']['unsupported_handling']
    assert metric['numerator'] == 9 and metric['denominator'] == 10
    assert metric['ratio'] == 0.9
    assert metric['pass'] is True
    assert result['latency']['pass'] is False


def test_zero_source_denominators_are_undefined():
    run, grades = complete_records()
    for grade in grades['cases']:
        for field in ('factual_claims', 'claims_with_citations',
                      'citation_pairs', 'supported_citation_pairs'):
            grade[field] = 0
    result = summarize_records(run, grades)
    for name in ('citation_correctness', 'citation_coverage'):
        assert result['quality'][name]['ratio'] is None
        assert result['quality'][name]['pass'] is None
    assert result['acceptance']['full_set_pass'] is False


def test_missing_grades_do_not_become_zero_or_pass():
    run, _ = complete_records()
    result = summarize_records(run)
    assert result['latency']['pass'] is True
    for name in ('answer_correctness', 'unsupported_handling',
                 'citation_correctness', 'citation_coverage'):
        assert result['quality'][name]['ratio'] is None
        assert result['quality'][name]['pass'] is None
    assert result['acceptance']['quality_thresholds_pass'] is False
    assert result['usage_and_cost']['cost']['total'] is None
    assert result['manual_search']['median_seconds'] is None


def test_partial_counts_are_not_mixed_into_totals():
    run, grades = complete_records()
    grades['cases'][0]['supported_citation_pairs'] = None
    result = summarize_records(run, grades)
    assert result['quality']['source_count_totals']['factual_claims'] == 39
    assert result['quality']['citation_correctness']['ratio'] is None
    assert result['quality']['missing_source_count_grade_ids'] == ['H01']


def test_backend_or_missing_scope_cannot_establish_browser_latency():
    run, grades = complete_records()
    run['timing_scope'] = 'backend_only'
    assert summarize_records(run, grades)['latency']['pass'] is False
    run['timing_scope'] = TIMING_SCOPE
    run['timing_clock'] = None
    assert summarize_records(run, grades)['latency']['pass'] is False


def test_empty_answer_cannot_be_a_completed_response():
    run, grades = complete_records()
    run['cases'][0]['actual_answer'] = ' '
    result = summarize_records(run, grades)
    assert result['latency']['pass'] is False
    assert result['outcomes']['unresolved_outcome_ids'] == ['H01']


def test_fixed_quality_thresholds_and_separate_citation_semantics():
    run, grades = complete_records()
    for grade in grades['cases'][:6]:
        grade['fully_correct_supported'] = False
    grades['cases'][-1]['appropriate_abstention'] = False
    grades['cases'][0]['supported_citation_pairs'] = 0
    grades['cases'][1]['supported_citation_pairs'] = 0
    result = summarize_records(run, grades)
    assert result['quality']['answer_correctness']['ratio'] == 0.8
    assert result['quality']['answer_correctness']['pass'] is True
    assert result['quality']['unsupported_handling']['ratio'] == 0.9
    assert result['quality']['citation_correctness']['ratio'] == 0.95
    assert result['quality']['citation_coverage']['ratio'] == 1.0
    assert result['acceptance']['full_set_pass'] is True


@pytest.mark.parametrize('mutation', ['duplicate_run', 'duplicate_grade', 'bad_count', 'impossible_count'])
def test_invalid_input_is_rejected(mutation):
    run, grades = complete_records()
    if mutation == 'duplicate_run':
        run['cases'].append(run['cases'][0])
    elif mutation == 'duplicate_grade':
        grades['cases'].append(grades['cases'][0])
    elif mutation == 'bad_count':
        grades['cases'][0]['citation_pairs'] = True
    else:
        grades['cases'][0]['supported_citation_pairs'] = 2
    with pytest.raises(ValueError):
        summarize_records(run, grades)


def test_summary_exclusive_creation_preserves_run_and_grades(tmp_path):
    run, grades = complete_records()
    run_path, grades_path = tmp_path / 'run.json', tmp_path / 'scoring.json'
    run_path.write_text(json.dumps(run), encoding='utf-8')
    grades_path.write_text(json.dumps(grades), encoding='utf-8')
    before = run_path.read_bytes(), grades_path.read_bytes()
    result = summarize(tmp_path)
    assert result['acceptance']['full_set_pass'] is True
    summary_bytes = (tmp_path / 'summary.json').read_bytes()
    with pytest.raises(FileExistsError):
        summarize(tmp_path)
    assert (tmp_path / 'summary.json').read_bytes() == summary_bytes
    assert (run_path.read_bytes(), grades_path.read_bytes()) == before
