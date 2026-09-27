"""
Unit tests for openMAX Autonomous Regression Gatekeeper.
"""

import unittest
from analysis.regression_gate.gatekeeper import RegressionGatekeeper, RunMetrics


class TestRegressionGatekeeper(unittest.TestCase):

    def setUp(self):
        self.gate = RegressionGatekeeper(max_p99_regression_pct=10.0, min_goodput_gain_pct=10.0)

    def test_keep_clear_winner(self):
        """Candidate B achieves +25% goodput with lower p99 latency -> KEEP."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95),
            RunMetrics("r2", "B", 63.0, 14.0, 28.0, 0.1, 0.98),
            RunMetrics("r3", "A", 50.5, 15.5, 31.0, 0.1, 0.95),
            RunMetrics("r4", "B", 64.0, 14.5, 29.0, 0.1, 0.97),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "KEEP")
        self.assertGreater(decision.goodput_delta_pct, 20.0)
        self.assertLess(decision.p99_delta_pct, 0.0)

    def test_reject_latency_regression(self):
        """Candidate B achieves higher throughput but blows out p99 bufferbloat -> REJECT."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95),
            RunMetrics("r2", "B", 70.0, 45.0, 95.0, 0.1, 0.90),  # Latency blowout!
            RunMetrics("r3", "A", 50.5, 15.5, 31.0, 0.1, 0.95),
            RunMetrics("r4", "B", 71.0, 48.0, 100.0, 0.1, 0.90),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "REJECT")
        self.assertIn("Bufferbloat", decision.rationale)

    def test_reject_firmware_instability(self):
        """Candidate B triggers a firmware reset -> immediate REJECT."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95),
            RunMetrics("r2", "B", 65.0, 14.0, 28.0, 0.1, 0.98, firmware_resets=1),
            RunMetrics("r3", "A", 50.5, 15.5, 31.0, 0.1, 0.95),
            RunMetrics("r4", "B", 64.0, 14.5, 29.0, 0.1, 0.97),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "REJECT")
        self.assertIn("Firmware instability", decision.summary)

    def test_inconclusive_insufficient_samples(self):
        """Only 1 run of B -> INCONCLUSIVE."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95),
            RunMetrics("r2", "A", 50.5, 15.5, 31.0, 0.1, 0.95),
            RunMetrics("r3", "B", 65.0, 14.0, 28.0, 0.1, 0.98),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
