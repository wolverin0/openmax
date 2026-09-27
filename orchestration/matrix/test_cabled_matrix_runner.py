"""Unit tests for orchestration.matrix.cabled_matrix_runner (CabledMatrixRunner)."""

import unittest
from orchestration.matrix.cabled_matrix_runner import (
    CabledMatrixRunner,
    MatrixExperimentConfig,
    ChannelAttenuationStep,
)


class TestCabledMatrixRunner(unittest.TestCase):
    def test_calculate_fspl_accuracy(self):
        # 1000m at 5180 MHz: theoretical FSPL is ~106.7 dB
        fspl = CabledMatrixRunner.calculate_fspl_db(1000.0, 5180.0)
        self.assertAlmostEqual(fspl, 106.7, delta=0.5)

        # 100m at 5180 MHz should be 20 dB less than 1000m
        fspl_100 = CabledMatrixRunner.calculate_fspl_db(100.0, 5180.0)
        self.assertAlmostEqual(fspl - fspl_100, 20.0, delta=0.1)

    def test_calculate_required_matrix_attenuation(self):
        # Total FSPL ~106.7 dB, fixed loss 8 dB -> attenuator set to ~98.7 dB
        att = CabledMatrixRunner.calculate_required_matrix_attenuation(1000.0, 5180.0, fixed_bench_loss_db=8.0)
        self.assertAlmostEqual(att, 98.7, delta=0.5)

    def test_plan_attenuation_steps(self):
        cfg = MatrixExperimentConfig(
            experiment_id="FMX-0010-MAT",
            frequency_mhz=5180,
            target_distances_meters=[100.0, 500.0, 2000.0],
        )
        runner = CabledMatrixRunner(cfg)
        steps = runner.plan_attenuation_steps()

        self.assertEqual(len(steps), 3)
        self.assertEqual(steps[0].equivalent_distance_meters, 100.0)
        self.assertEqual(steps[1].equivalent_distance_meters, 500.0)
        self.assertEqual(steps[2].equivalent_distance_meters, 2000.0)

        # Expected RSSI should strictly decrease with distance
        self.assertGreater(steps[0].expected_rssi_dbm, steps[1].expected_rssi_dbm)
        self.assertGreater(steps[1].expected_rssi_dbm, steps[2].expected_rssi_dbm)

    def test_run_synthetic_sweep(self):
        cfg = MatrixExperimentConfig(
            experiment_id="FMX-0010-SWEEP",
            frequency_mhz=5180,
            target_distances_meters=[100.0, 1000.0, 150000.0],
        )
        runner = CabledMatrixRunner(cfg)
        report = runner.run_sweep()

        self.assertTrue(report.is_fully_executed)
        self.assertEqual(len(report.steps), 3)
        
        # Near distance (100m) should have high goodput
        self.assertEqual(report.steps[0].aggregate_goodput_mbps, 95.0)
        self.assertTrue(report.steps[0].is_link_established)

        # Extreme distance (150 km) should fail link or drop goodput
        self.assertFalse(report.steps[2].is_link_established)
        self.assertEqual(report.steps[2].aggregate_goodput_mbps, 0.0)

    def test_run_sweep_with_hardware_callback(self):
        cfg = MatrixExperimentConfig(
            experiment_id="FMX-0010-HW",
            frequency_mhz=5180,
            target_distances_meters=[200.0],
        )
        runner = CabledMatrixRunner(cfg)

        attenuation_set_log = []

        def mock_set_att(db: float) -> bool:
            attenuation_set_log.append(db)
            return True

        def mock_benchmark(step: ChannelAttenuationStep):
            return {
                "measured_rssi": -63.5,
                "goodput_mbps": 88.4,
                "p50_ms": 4.2,
                "p95_ms": 8.1,
                "p99_ms": 12.3,
                "loss_pct": 0.02,
                "retry_rate": 0.04,
                "is_up": True,
            }

        report = runner.run_sweep(
            set_hardware_attenuation_fn=mock_set_att,
            traffic_benchmark_fn=mock_benchmark,
        )

        self.assertEqual(len(attenuation_set_log), 1)
        step = report.steps[0]
        self.assertEqual(step.measured_rssi_dbm, -63.5)
        self.assertEqual(step.aggregate_goodput_mbps, 88.4)
        self.assertEqual(step.p99_latency_ms, 12.3)
        self.assertEqual(step.retry_rate, 0.04)


if __name__ == "__main__":
    unittest.main()
