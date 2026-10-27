"""
Unit tests for openMAX Autonomous Regression Gatekeeper.
"""

import unittest
from analysis.regression_gate.gatekeeper import RegressionGatekeeper, RunMetrics


class TestRegressionGatekeeper(unittest.TestCase):

    def setUp(self):
        self.gate = RegressionGatekeeper(max_p99_regression_pct=10.0, min_goodput_gain_pct=10.0)

    def test_keep_clear_winner(self):
        """Candidate B achieves +25% goodput with lower p99 latency across 6 paired blocks -> SYNTHETIC_PASS; no physical promotion."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r2", "B", 63.0, 14.0, 28.0, 0.1, 0.98, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r3", "A", 50.5, 15.5, 31.0, 0.1, 0.95, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r4", "B", 64.0, 14.5, 29.0, 0.1, 0.97, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r5", "A", 50.2, 15.2, 30.5, 0.1, 0.95, channel_width_mhz=20, block_index=2, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r6", "B", 63.5, 14.2, 28.4, 0.1, 0.98, channel_width_mhz=20, block_index=2, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r7", "A", 49.8, 15.1, 30.2, 0.1, 0.95, channel_width_mhz=20, block_index=3, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r8", "B", 63.2, 14.1, 28.2, 0.1, 0.97, channel_width_mhz=20, block_index=3, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r9", "A", 50.4, 15.4, 30.8, 0.1, 0.95, channel_width_mhz=20, block_index=4, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r10", "B", 63.8, 14.4, 28.8, 0.1, 0.98, channel_width_mhz=20, block_index=4, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r11", "A", 50.1, 15.3, 30.4, 0.1, 0.95, channel_width_mhz=20, block_index=5, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r12", "B", 63.6, 14.3, 28.5, 0.1, 0.97, channel_width_mhz=20, block_index=5, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "SYNTHETIC_PASS")
        self.assertFalse(decision.promotion_eligible)
        self.assertGreater(decision.goodput_delta_pct, 20.0)
        self.assertLess(decision.p99_delta_pct, 0.0)

        # A boolean never promotes a synthetic fixture; n=2 stays INCONCLUSIVE
        paired_decision = self.gate.evaluate_paired(runs, holdout_replicated=True)
        self.assertEqual(paired_decision.verdict, "SYNTHETIC_PASS")
        self.assertFalse(paired_decision.promotion_eligible)
        underpowered_n2 = self.gate.evaluate(runs[:4])
        self.assertEqual(underpowered_n2.verdict, "INCONCLUSIVE")

    def test_reject_latency_regression(self):
        """Candidate B achieves higher throughput but blows out p99 bufferbloat -> REJECT."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r2", "B", 70.0, 45.0, 95.0, 0.1, 0.90, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),  # Latency blowout!
            RunMetrics("r3", "A", 50.5, 15.5, 31.0, 0.1, 0.95, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r4", "B", 71.0, 48.0, 100.0, 0.1, 0.90, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "REJECT")
        self.assertIn("Bufferbloat", decision.rationale)

    def test_reject_firmware_instability(self):
        """Candidate B triggers a firmware reset -> immediate REJECT."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r2", "B", 65.0, 14.0, 28.0, 0.1, 0.98, firmware_resets=1, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r3", "A", 50.5, 15.5, 31.0, 0.1, 0.95, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r4", "B", 64.0, 14.5, 29.0, 0.1, 0.97, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "REJECT")
        self.assertIn("Firmware instability", decision.summary)

    def test_inconclusive_insufficient_samples(self):
        """Only 1 run of B -> INCONCLUSIVE."""
        runs = [
            RunMetrics("r1", "A", 50.0, 15.0, 30.0, 0.1, 0.95, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r2", "A", 50.5, 15.5, 31.0, 0.1, 0.95, channel_width_mhz=20, block_index=0, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
            RunMetrics("r3", "B", 65.0, 14.0, 28.0, 0.1, 0.98, channel_width_mhz=20, block_index=1, worst_peer_goodput_mbps=20.0, evidence_state="SYNTHETIC"),
        ]
        decision = self.gate.evaluate(runs)
        self.assertEqual(decision.verdict, "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
