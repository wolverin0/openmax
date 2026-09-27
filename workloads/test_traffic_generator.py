"""
Unit tests for openMAX Traffic Generator and Workload Profiles.
"""

import unittest
from workloads.traffic_generator import TrafficGenerator


class TestTrafficGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = TrafficGenerator(seed=123)

    def test_bulk_saturated_workload(self):
        res = self.generator.run_workload(
            workload_id="WK-001",
            profile="bulk_saturated",
            num_stations=8,
            duration_s=5.0,
            target_bandwidth_mbps=100.0,
            enable_rts=True
        )
        self.assertEqual(res.num_stations, 8)
        self.assertGreater(res.delivered_goodput_mbps, 50.0)
        self.assertLess(res.p99_latency_ms, 100.0)
        self.assertGreater(res.jain_fairness, 0.90)

    def test_interactive_gaming_profile(self):
        res = self.generator.run_workload(
            workload_id="WK-002",
            profile="interactive_gaming",
            num_stations=4,
            duration_s=5.0,
            enable_rts=True
        )
        self.assertEqual(res.num_stations, 4)
        self.assertLess(res.p50_latency_ms, 15.0)
        self.assertLess(res.p99_latency_ms, 30.0)
        self.assertLess(res.loss_percent, 0.5)

    def test_near_far_mixed_profile(self):
        res = self.generator.run_workload(
            workload_id="WK-003",
            profile="near_far_mixed",
            num_stations=4,
            duration_s=5.0
        )
        self.assertEqual(len(res.per_station_results), 4)
        roles = [s["role"] for s in res.per_station_results]
        self.assertIn("NEAR_MCS8", roles)
        self.assertIn("FAR_MCS2", roles)


if __name__ == "__main__":
    unittest.main()
