"""Explicit prospective latency policy; historical runs remain strict by default."""
import hashlib
import json

V2_POLICY = {
    'version': 'latency-v2',
    'deadline_seconds': 10,
    'maximum_exceedance_percent': 3,
    'require_all_scheduled_responses': True,
}


def policy_digest(policy):
    return hashlib.sha256(json.dumps(policy, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def verify_policy_binding(binding):
    """Reject unknown policy shapes, changed limits and missing approval identity."""
    if not isinstance(binding, dict) or binding.get('policy') != V2_POLICY:
        raise ValueError('Missing or unsupported prospective latency policy.')
    # JSON equality alone considers True equal to 1; compare canonical bytes too.
    if policy_digest(binding['policy']) != policy_digest(V2_POLICY):
        raise ValueError('Prospective policy field types differ.')
    if binding.get('sha256') != policy_digest(V2_POLICY):
        raise ValueError('Prospective latency policy digest mismatch.')
    if not isinstance(binding.get('owner_confirmation'), str) or not binding['owner_confirmation'].strip():
        raise ValueError('Prospective policy owner confirmation is missing.')
    return binding


def prospective_latency(run, *, completed_count, timed_count, exceeded_count, scope_verified, expected_count):
    binding = run.get('acceptance_policy')
    if binding is None:
        return None
    verify_policy_binding(binding)
    allowed = expected_count * 3 // 100
    complete = completed_count == timed_count == expected_count and scope_verified
    return {'version': 'latency-v2', 'policy_sha256': binding['sha256'],
            'scheduled_count': expected_count, 'allowed_exceedance_count': allowed,
            'exceeded_deadline_count': exceeded_count,
            'observed_exceedance_percent': exceeded_count * 100 / expected_count if complete else None,
            'all_scheduled_responses_timed': complete,
            'pass': complete and exceeded_count <= allowed}
