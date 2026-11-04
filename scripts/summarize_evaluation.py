"""Summarize recorded primary outcomes and explicit grades; never run models."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import statistics


CASE_IDS = tuple(f'H{number:02d}' for number in range(1, 41))
ANSWERABLE_IDS = CASE_IDS[:30]
UNSUPPORTED_IDS = CASE_IDS[30:]
TIMING_SCOPE = 'browser_submission_to_rendered_answer_and_sources'
TIMING_CLOCK = 'window.performance.now'
FAILURE_STATUSES = {'TECHNICAL_ERROR', 'TIMEOUT', 'Failed', 'Timeout'}
COUNT_FIELDS = (
    'factual_claims', 'claims_with_citations',
    'citation_pairs', 'supported_citation_pairs',
)
COMPLETED_RUN_STATUSES = {'COMPLETED_UNSCORED', 'COMPLETED_SCORED'}


def primary_provenance(cases, run):
    """Do not infer primary identity from a successful answer or case ID."""
    verified, retries, ambiguous = [], [], []
    for case_id, case in cases.items():
        number = case.get('attempt_number')
        if (case.get('is_primary') is True and type(number) is int and number == 1
                and 'retry_of' in case and case['retry_of'] is None
                and ('primary_attempt' not in case or
                     type(case['primary_attempt']) is int and case['primary_attempt'] == 1)):
            verified.append(case_id)
        elif case.get('is_primary') is False or case.get('retry_of') is not None:
            retries.append(case_id)
        else:
            ambiguous.append(case_id)
    missing = sorted(set(CASE_IDS) - cases.keys())
    identity = run.get('attempt_identity')
    consistent = ('attempt_identity' not in run or
                  isinstance(identity, dict) and identity.get('primary') is True
                  and type(identity.get('attempt')) is int and identity['attempt'] == 1
                  and identity.get('retry_of') is None)
    consistent = consistent and run.get('retry_of') is None
    return {'verified_primary_ids': sorted(verified), 'nonprimary_ids': sorted(retries),
            'unverified_ids': sorted(ambiguous), 'missing_ids': missing,
            'run_identity_consistent': consistent,
            'all_primary_verified': len(verified) == len(CASE_IDS) and consistent}


def run_validity(run):
    """Completion, preservation and configuration are independent of answer scores."""
    reasons = []
    if run.get('run_status') not in COMPLETED_RUN_STATUSES or run.get('selected_cases_finished') is not True:
        reasons.append('run_completion_unverified_or_failed')
    if run.get('failure') or run.get('blocker'):
        reasons.append('run_failure_or_blocker_recorded')
    if any(value for name, value in run.items() if 'unconfirmed' in name):
        reasons.append('run_has_unconfirmed_checks')
    before, after = run.get('workspaces_before'), run.get('workspaces_after')
    def witness(value):
        return (isinstance(value, dict) and type(value.get('workspace_count')) is int
                and value['workspace_count'] >= 0
                and isinstance(value.get('row_and_pdf_sha256'), str)
                and len(value['row_and_pdf_sha256']) == 64
                and all(c in '0123456789abcdef' for c in value['row_and_pdf_sha256']))
    if (run.get('preexisting_workspaces_unchanged') is not True
            or not witness(before) or not witness(after) or before != after):
        reasons.append('preservation_unverified_or_mismatched')
    verification = run.get('configuration_verification')
    snapshot = verification.get('verified_configuration') if isinstance(verification, dict) else None
    snapshot_valid = (isinstance(snapshot, dict) and set(snapshot) == {
        'configured_models', 'runtime_settings', 'execution_settings', 'private_configuration_fingerprints'}
        and all(isinstance(value, dict) and value for value in snapshot.values()))
    fingerprint = (hashlib.sha256(json.dumps(snapshot, sort_keys=True, separators=(',', ':')).encode()).hexdigest()
                   if snapshot_valid else None)
    if (not isinstance(verification, dict) or verification.get('status') != 'VERIFIED'
            or not snapshot_valid or verification.get('approved_configuration_sha256') != fingerprint
            or snapshot['configured_models'] != {key: run.get(key) for key in
                ('provider', 'chat_model', 'embedding_model')}
            or snapshot['runtime_settings'] != run.get('runtime_settings')):
        reasons.append('configuration_unverified')
    return {'verified': not reasons, 'blocking_reasons': reasons}


def _number(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0)


def _by_id(records, label):
    if not isinstance(records, list):
        raise ValueError(f'{label} cases must be a list.')
    result = {}
    for record in records:
        if not isinstance(record, dict) or record.get('id') not in CASE_IDS:
            raise ValueError(f'{label} contains an invalid case ID.')
        if record['id'] in result:
            raise ValueError(f'{label} contains duplicate {record["id"]}.')
        result[record['id']] = record
    return result


def _validate_grade(grade):
    for field in ('fully_correct_supported', 'appropriate_abstention'):
        if grade.get(field) is not None and not isinstance(grade[field], bool):
            raise ValueError(f'{grade["id"]}: {field} must be boolean or null.')
    for field in COUNT_FIELDS:
        value = grade.get(field)
        if value is not None and (type(value) is not int or value < 0):
            raise ValueError(f'{grade["id"]}: {field} must be a nonnegative integer or null.')
    for numerator, denominator in (
        ('claims_with_citations', 'factual_claims'),
        ('supported_citation_pairs', 'citation_pairs'),
    ):
        if (grade.get(numerator) is not None and grade.get(denominator) is not None
                and grade[numerator] > grade[denominator]):
            raise ValueError(f'{grade["id"]}: {numerator} exceeds {denominator}.')


def _metric(numerator, denominator, threshold, incomplete_ids):
    complete = not incomplete_ids
    ratio = numerator / denominator if complete and denominator else None
    return {
        'numerator': numerator, 'denominator': denominator,
        'ratio': ratio, 'threshold': threshold,
        'grading_complete': complete, 'incomplete_ids': sorted(incomplete_ids),
        'pass': ratio >= threshold if ratio is not None else None,
    }


def summarize_records(run, grading=None):
    """Return descriptive metrics without guessing missing judgments or timings."""
    cases = _by_id(run.get('cases'), 'Run')
    grades = _by_id((grading or {}).get('cases', []), 'Grading')
    provenance = primary_provenance(cases, run)
    validity = run_validity(run)
    for grade in grades.values():
        _validate_grade(grade)
    completed = {
        case_id for case_id, case in cases.items()
        if case.get('status') == 'Completed'
        and isinstance(case.get('actual_answer'), str) and case['actual_answer'].strip()
    }
    failures = {
        case_id for case_id, case in cases.items()
        if case.get('status') in FAILURE_STATUSES
    }
    unknown_outcomes = set(CASE_IDS) - completed - failures

    def correctness(ids, field, threshold):
        numerator = 0
        incomplete = []
        for case_id in ids:
            if case_id in failures:
                continue  # A submitted technical failure is known incorrect.
            value = grades.get(case_id, {}).get(field)
            if case_id not in completed or value is None:
                incomplete.append(case_id)
            elif value:
                numerator += 1
        return _metric(numerator, len(ids), threshold, incomplete)

    counted_ids = []
    totals = dict.fromkeys(COUNT_FIELDS, 0)
    missing_count_grades = []
    for case_id in sorted(completed):
        grade = grades.get(case_id, {})
        if any(grade.get(field) is None for field in COUNT_FIELDS):
            missing_count_grades.append(case_id)
            continue
        counted_ids.append(case_id)
        for field in COUNT_FIELDS:
            totals[field] += grade[field]
    count_incomplete = set(missing_count_grades) | unknown_outcomes
    quality = {
        'answer_correctness': correctness(ANSWERABLE_IDS, 'fully_correct_supported', 0.8),
        'unsupported_handling': correctness(UNSUPPORTED_IDS, 'appropriate_abstention', 0.9),
        'citation_correctness': _metric(
            totals['supported_citation_pairs'], totals['citation_pairs'], 0.95,
            count_incomplete),
        'citation_coverage': _metric(
            totals['claims_with_citations'], totals['factual_claims'], 1.0,
            count_incomplete),
        'source_count_totals': totals,
        'source_count_graded_completed_ids': counted_ids,
        'missing_source_count_grade_ids': missing_count_grades,
    }

    timed = {case_id: cases[case_id]['answer_seconds'] for case_id in completed
             if _number(cases[case_id].get('answer_seconds'))}
    sorted_times = sorted(timed.values())
    exceeded = sorted(case_id for case_id, seconds in timed.items() if seconds > 10.0)
    scope_verified = (run.get('timing_scope') == TIMING_SCOPE
                      and run.get('timing_clock') == TIMING_CLOCK)
    latency_pass = (len(completed) == 40 and len(timed) == 40
                    and scope_verified and not exceeded)
    latency = {
        'deadline_seconds': 10.0,
        'timing_scope': run.get('timing_scope'), 'timing_clock': run.get('timing_clock'),
        'browser_timing_scope_verified': scope_verified,
        'completed_response_count': len(completed), 'timed_completed_count': len(timed),
        'missing_completed_timing_ids': sorted(completed - timed.keys()),
        'exceeded_deadline_count': len(exceeded), 'exceeded_deadline_ids': exceeded,
        'median_seconds': statistics.median(sorted_times) if sorted_times else None,
        'p95_nearest_rank_seconds': (
            sorted_times[math.ceil(0.95 * len(sorted_times)) - 1] if sorted_times else None),
        'max_seconds': max(sorted_times) if sorted_times else None,
        'pass': latency_pass,
        'note': 'Every primary response must complete within 10.000 seconds; median/p95/max are descriptive.',
    }

    def recorded_total(field):
        measured = [case[field] for case in cases.values() if _number(case.get(field))]
        return {'recorded_case_count': len(measured),
                'total': sum(measured) if len(measured) == 40 else None}

    manual = {case_id: case['manual_search_seconds'] for case_id, case in cases.items()
              if _number(case.get('manual_search_seconds'))}
    quality_pass = all(quality[name]['pass'] is True for name in (
        'answer_correctness', 'unsupported_handling',
        'citation_correctness', 'citation_coverage'))
    return {
        'summary_type': 'Offline primary-attempt aggregation; semantic grades are supplied separately',
        'run_status': run.get('run_status'),
        'tested_commit': run.get('commit'), 'deployed_revision': run.get('deployed_revision'),
        'expected_case_count': 40,
        'outcomes': {
            'completed_ids': sorted(completed), 'failed_ids': sorted(failures),
            'technical_error_ids': sorted(case_id for case_id in failures
                                          if cases[case_id].get('status') in {'TECHNICAL_ERROR', 'Failed'}),
            'timeout_ids': sorted(case_id for case_id in failures
                                  if cases[case_id].get('status') in {'TIMEOUT', 'Timeout'}),
            'unconfirmed_submission_ids': sorted(
                case_id for case_id, case in cases.items()
                if case.get('status') == 'SUBMITTED_OUTCOME_UNCONFIRMED'),
            'not_run_ids': sorted(case_id for case_id, case in cases.items()
                                  if case.get('status') == 'Not run'),
            'missing_case_ids': sorted(set(CASE_IDS) - cases.keys()),
            'unresolved_outcome_ids': sorted(unknown_outcomes),
            'excluded_noncompleted_grade_ids': sorted(grades.keys() - completed),
        },
        'quality': quality, 'latency': latency,
        'primary_provenance': provenance, 'run_validity': validity,
        'usage_and_cost': {field: recorded_total(field) for field in (
            'input_tokens', 'output_tokens', 'embedding_tokens', 'cost')},
        'currency': run.get('currency'),
        'manual_search': {
            'recorded_case_count': len(manual),
            'missing_ids': sorted(set(CASE_IDS) - manual.keys()),
            'median_seconds': statistics.median(manual.values()) if manual else None,
            'total_seconds': sum(manual.values()) if len(manual) == 40 else None,
        },
        'acceptance': {
            'descriptive_quality_thresholds_pass': quality_pass,
            'quality_thresholds_pass': quality_pass and provenance['all_primary_verified'],
            'all_primary_responses_within_deadline': latency_pass and provenance['all_primary_verified'],
            'full_set_pass': (quality_pass and latency_pass and provenance['all_primary_verified']
                              and validity['verified']),
            'deployment_acceptance': 'Not established by this local evaluation',
        },
    }


def summarize(run_dir, grades_path=None, output_path=None):
    """Read immutable inputs and exclusively create a new summary JSON file."""
    run_dir = Path(run_dir)
    run_path = run_dir / 'run.json'
    grades_path = Path(grades_path) if grades_path is not None else run_dir / 'scoring.json'
    output_path = Path(output_path) if output_path is not None else run_dir / 'summary.json'
    run_bytes = run_path.read_bytes()
    grade_bytes = grades_path.read_bytes() if grades_path.exists() else None
    result = summarize_records(
        json.loads(run_bytes), json.loads(grade_bytes) if grade_bytes is not None else None)
    result['input_sha256'] = {
        'run.json': hashlib.sha256(run_bytes).hexdigest(),
        'grades': hashlib.sha256(grade_bytes).hexdigest() if grade_bytes is not None else None,
    }
    result['grading_file'] = str(grades_path)
    with output_path.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--grades', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    summarize(args.run_dir, args.grades, args.output)
    print('Offline summary created. No API calls made; missing evidence cannot pass.')
