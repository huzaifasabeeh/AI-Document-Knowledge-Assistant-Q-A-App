"""No provider calls: prospective rate boundaries and fail-closed policy binding."""
from copy import deepcopy
import unittest
from scripts.evaluation_latency_policy import V2_POLICY, policy_digest, prospective_latency, verify_policy_binding


class LatencyPolicyTests(unittest.TestCase):
    def setUp(self):
        self.run = {'acceptance_policy': {'policy': deepcopy(V2_POLICY),
                    'sha256': policy_digest(V2_POLICY), 'owner_confirmation': 'Owner instruction, 5 November 2026'}}

    def result(self, slow=1, completed=40, timed=40, scope=True, expected=40):
        return prospective_latency(self.run, completed_count=completed, timed_count=timed,
            exceeded_count=slow, scope_verified=scope, expected_count=expected)

    def test_rate_boundaries_without_rounding(self):
        self.assertTrue(self.result(1)['pass'])
        self.assertFalse(self.result(2)['pass'])
        self.assertEqual(self.result(1)['observed_exceedance_percent'], 2.5)
        self.assertTrue(self.result(3, completed=100, timed=100, expected=100)['pass'])
        self.assertFalse(self.result(4, completed=100, timed=100, expected=100)['pass'])

    def test_missing_failed_and_wrong_scope_do_not_pass(self):
        for kwargs in ({'completed':39}, {'timed':39}, {'scope':False}):
            with self.subTest(kwargs=kwargs):
                self.assertFalse(self.result(**kwargs)['pass'])
                self.assertIsNone(self.result(**kwargs)['observed_exceedance_percent'])

    def test_historical_default_is_not_upgraded(self):
        self.assertIsNone(prospective_latency({}, completed_count=40, timed_count=40,
            exceeded_count=1, scope_verified=True, expected_count=40))

    def test_tampered_digest_policy_or_approval_rejected(self):
        for field,value in [('sha256','0'*64), ('owner_confirmation',''), ('policy',{})]:
            binding=deepcopy(self.run['acceptance_policy']);binding[field]=value
            with self.assertRaises(ValueError): verify_policy_binding(binding)
        binding=deepcopy(self.run['acceptance_policy']);binding['policy']['require_all_scheduled_responses']=1
        with self.assertRaises(ValueError): verify_policy_binding(binding)
