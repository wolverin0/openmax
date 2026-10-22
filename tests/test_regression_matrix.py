"""Unit tests for tools/bench/automated_regression_matrix.py and telemetry/live_dashboard.py."""

import json
import unittest
from pathlib import Path

from tools.bench.automated_regression_matrix import (
    AutomatedRegressionMatrix,
    ComparisonMetrics,
    IterationResult,
    MatrixReceipt,
    STANDARD_TREATMENTS,
    TreatmentConfig,
    TreatmentSummary,
    calculate_delta_pct,
    calculate_jains_fairness,
    calculate_reduction_ms,
    calculate_reduction_pct,
)
from telemetry.live_dashboard import (
    LiveDashboard,
    generate_mock_dashboard_data,
    render_dashboard,
    _render_bar,
)
from telemetry.station_monitor import StationTelemetry
from telemetry.spectral_fft.parser import SpectralAnalysisReport


class TestRegressionMatrixMath(unittest.TestCase):
    """Tests for statistical and comparative formulas."""

    def test_jains_fairness_identical(self):
        # 4 stations with equal throughput -> Jain's index must be exactly 1.0
        allocations = [25.0, 25.0, 25.0, 25.0]
        self.assertEqual(calculate_jains_fairness(allocations), 1.0)

    def test_jains_fairness_uneven(self):
        # [10, 20, 30, 40]:
        # sum = 100, sum^2 = 10000
        # sum_sq = 100 + 400 + 900 + 1600 = 3000
        # n = 4, n * sum_sq = 12000
        # J = 10000 / 12000 = 0.8333
        allocations = [10.0, 20.0, 30.0, 40.0]
        self.assertAlmostEqual(calculate_jains_fairness(allocations), 0.8333, places=4)

    def test_jains_fairness_dict_input(self):
        alloc_dict = {"sta1": 50.0, "sta2": 50.0}
        self.assertEqual(calculate_jains_fairness(alloc_dict), 1.0)

    def test_jains_fairness_edge_cases(self):
        self.assertEqual(calculate_jains_fairness([]), 1.0)
        self.assertEqual(calculate_jains_fairness([42.0]), 1.0)
        self.assertEqual(calculate_jains_fairness([0.0, 0.0, 0.0]), 0.0)

    def test_calculate_delta_pct(self):
        # Baseline 100, Treatment 50 -> -50.0%
        self.assertEqual(calculate_delta_pct(100.0, 50.0), -50.0)
        # Baseline 50, Treatment 100 -> +100.0%
        self.assertEqual(calculate_delta_pct(50.0, 100.0), 100.0)
        # Zero baseline
        self.assertEqual(calculate_delta_pct(0.0, 50.0), 0.0)

    def test_calculate_reduction(self):
        # Latency dropped from 100 ms to 20 ms -> 80 ms reduction (80%)
        self.assertEqual(calculate_reduction_ms(100.0, 20.0), 80.0)
        self.assertEqual(calculate_reduction_pct(100.0, 20.0), 80.0)

        # Latency increased from 50 ms to 60 ms -> -10 ms reduction (-20%)
        self.assertEqual(calculate_reduction_ms(50.0, 60.0), -10.0)
        self.assertEqual(calculate_reduction_pct(50.0, 60.0), -20.0)


class TestAutomatedRegressionMatrix(unittest.TestCase):
    """Tests for multi-treatment matrix execution and report formatting."""

    def test_dry_run_matrix_execution(self):
        orchestrator = AutomatedRegressionMatrix(
            target_ip="10.99.0.1",
            iface="eth0",
            bandwidth="50Mbit",
            repetitions=2,
            duration=5,
            dry_run=True,
        )

        receipt = orchestrator.run_matrix()

        # Verify receipt structure
        self.assertEqual(receipt.target, "10.99.0.1")
        self.assertEqual(receipt.repetitions, 2)
        self.assertEqual(len(receipt.treatments), 4)
        self.assertEqual(len(receipt.comparisons), 4)

        # Verify all 4 standard treatments are present
        for trt in STANDARD_TREATMENTS:
            self.assertIn(trt.id, receipt.treatments)
            summary = receipt.treatments[trt.id]
            self.assertEqual(summary.iteration_count, 2)
            self.assertEqual(len(summary.iterations), 2)
            self.assertGreater(summary.mean_goodput_mbps, 0.0)
            self.assertGreater(summary.mean_p95_latency_ms, 0.0)

        # Check comparisons
        cmp_t1 = receipt.comparisons["T1"]
        self.assertEqual(cmp_t1.goodput_delta_pct, 0.0)
        self.assertEqual(cmp_t1.p95_reduction_ms, 0.0)

        cmp_t2 = receipt.comparisons["T2"]
        # CAKE should reduce p95 latency by > 50%
        self.assertGreater(cmp_t2.p95_reduction_pct, 50.0)
        self.assertGreater(cmp_t2.p95_reduction_ms, 50.0)
        self.assertGreater(cmp_t2.jain_fairness_delta, 0.0)

        cmp_t4 = receipt.comparisons["T4"]
        # CAKE + Dyn Aggr should achieve highest p95 reduction
        self.assertGreater(cmp_t4.p95_reduction_pct, cmp_t2.p95_reduction_pct)

    def test_save_receipt_and_markdown(self, tmp_path=None):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp_dir:
            orchestrator = AutomatedRegressionMatrix(
                target_ip="10.99.0.1",
                repetitions=1,
                out_dir=tmp_dir,
                dry_run=True,
            )
            receipt = orchestrator.run_matrix()
            json_file = orchestrator.save_receipt(receipt)

            self.assertTrue(json_file.exists())
            loaded_json = json.loads(json_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded_json["matrix_id"], receipt.matrix_id)

            md_file = Path(tmp_dir) / f"{receipt.matrix_id}.md"
            self.assertTrue(md_file.exists())
            md_content = md_file.read_text(encoding="utf-8")
            self.assertIn("# FuturaMAX Automated Regression Matrix Report", md_content)
            self.assertIn("T1: Stock Baseline", md_content)
            self.assertIn("T4: CAKE + Dynamic Aggregation", md_content)


class TestLiveDashboard(unittest.TestCase):
    """Tests for live terminal dashboard rendering."""

    def test_render_bar(self):
        bar_0 = _render_bar(0.0, width=10)
        self.assertIn("[----------]", bar_0)
        self.assertIn("0.0%", bar_0)

        bar_50 = _render_bar(50.0, width=10)
        self.assertIn("[=====-----]", bar_50)
        self.assertIn("50.0%", bar_50)

        bar_100 = _render_bar(100.0, width=10)
        self.assertIn("[==========]", bar_100)
        self.assertIn("100.0%", bar_100)

    def test_mock_dashboard_generation_and_render(self):
        stations, spectral = generate_mock_dashboard_data()
        self.assertEqual(len(stations), 3)
        self.assertIsNotNone(spectral)

        dashboard_output = render_dashboard(stations, spectral, {"target_ap": "10.99.0.1", "iface": "phy0-ap0"})

        self.assertIn("FUTURAMAX TELEMETRY DASHBOARD", dashboard_output)
        self.assertIn("10.99.0.1 [phy0-ap0]", dashboard_output)
        self.assertIn("RF SPECTRUM OCCUPANCY & INTERFERENCE CLASSIFIER", dashboard_output)
        self.assertIn("ASSOCIATED CPE STATIONS", dashboard_output)
        self.assertIn("SECTOR SUMMARY & AIRTIME DEMAND", dashboard_output)

        # Check that degraded station 00:27:22:77:88:99 is flagged
        self.assertIn("!00:27:22:77:88:99", dashboard_output)
        self.assertIn("CRITICAL (1 degraded)", dashboard_output)

    def test_live_dashboard_poll_once_mock(self):
        dashboard = LiveDashboard(target_ap="10.99.0.1", mock=True)
        stations, spectral = dashboard.poll_once()
        self.assertEqual(len(stations), 3)
        rendered = dashboard.render()
        self.assertIn("CPE-North-Silo", rendered)
        self.assertIn("CPE-South-Farm", rendered)


if __name__ == "__main__":
    unittest.main()
