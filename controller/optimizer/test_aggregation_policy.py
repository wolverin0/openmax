import unittest

from controller.optimizer.aggregation_policy import AggregationPolicy, prepare_plan


class AggregationPolicyTests(unittest.TestCase):
    def test_source_verified_boundaries_and_external_order(self):
        for amsdu in (1, 31):
            for ampdu in (1, 64):
                self.assertEqual(AggregationPolicy(amsdu, ampdu).debugfs_value(), f"{amsdu} {ampdu}\n")

    def test_narrowing_wraparound_rejected(self):
        for value in (0, -1, 32, 65, 256, 257, 2**32 + 3):
            with self.subTest(amsdu=value), self.assertRaises(ValueError):
                AggregationPolicy(value, 64)
        for value in (0, -1, 65, 256, 257, 2**32 + 64):
            with self.subTest(ampdu=value), self.assertRaises(ValueError):
                AggregationPolicy(3, value)

    def test_non_integers_rejected(self):
        for value in (True, False, 3.0, "3", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                AggregationPolicy(value, 64)

    def test_readback_roundtrip(self):
        value = AggregationPolicy(3, 64)
        self.assertEqual(AggregationPolicy.from_readback(value.debugfs_value()), value)

    def test_readback_strict_and_range_checked(self):
        for text in ("64 3", "3 257", "3 64 extra", "3; 64", "3 64\n\n", "0 64", "3 -1"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                AggregationPolicy.from_readback(text)

    def test_default_plan_is_twelve_runs_one_variable(self):
        plan = prepare_plan(AggregationPolicy(3, 64), 32)
        runs = plan["protocol"]["rounds"]
        self.assertEqual("".join(run["arm"] for run in runs), "ABAB" * 3)
        self.assertTrue(all(run["policy"]["amsdu"] == 3 for run in runs))
        self.assertEqual([run["policy"]["ampdu"] for run in runs], [64, 32, 64, 32] * 3)
        self.assertEqual(plan["protocol"]["restore_after_run_or_error"], {"amsdu": 3, "ampdu": 64})

    def test_plan_never_grants_execution(self):
        plan = prepare_plan(AggregationPolicy(3, 64), 32)
        self.assertFalse(plan["execution_authorized"])
        self.assertEqual(plan["status"], "PREPARED_NOT_RUN")
        self.assertTrue(plan["required_before_execution"])

    def test_plan_fingerprint_deterministic_and_change_sensitive(self):
        baseline = AggregationPolicy(3, 64)
        first = prepare_plan(baseline, 32)
        self.assertEqual(first, prepare_plan(baseline, 32))
        self.assertNotEqual(first["protocol_sha256"], prepare_plan(baseline, 16)["protocol_sha256"])

    def test_same_arm_and_invalid_block_counts_rejected(self):
        with self.assertRaises(ValueError):
            prepare_plan(AggregationPolicy(3, 64), 64)
        for repeats in (0, 1, 2, 21, True, 3.0):
            with self.subTest(repeats=repeats), self.assertRaises(ValueError):
                prepare_plan(AggregationPolicy(3, 64), 32, repeats=repeats)

    def test_increased_ceiling_cannot_claim_lower_ceiling_hypothesis(self):
        with self.assertRaisesRegex(ValueError, "below baseline"):
            prepare_plan(AggregationPolicy(3, 32), 64)


if __name__ == "__main__":
    unittest.main()
