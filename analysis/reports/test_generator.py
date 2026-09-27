"""Unit tests for analysis.reports.generator (ReportGenerator)."""

import tempfile
import unittest
from pathlib import Path
from analysis.metrics.schema import ExperimentMetadata, RunSample, ExperimentResultRecord
from analysis.reports.generator import ReportGenerator


class TestReportGenerator(unittest.TestCase):
    def setUp(self):
        self.meta = ExperimentMetadata(
            experiment_id="FMX-0013",
            hypothesis="CoTSQ 6ms restores 802.11ac A-MPDU depth",
            hardware_revision="LAP-120 AR9342 rev 2 + QCA9880",
            firmware_build_hash="openwrt-24.10.4-f2a89c",
            config_snapshot={"net.ipv4.tcp_limit_output_bytes": 300000},
            topology="1 AP + 20 CPEs (Hidden Nodes)",
            channel_mhz=5180,
            channel_width_mhz=40,
            tx_power_dbm=20.0,
            attenuation_db=45.0,
            offered_load_profile="Saturated Reverse Uplink",
            repetitions=4,
            treatment_order=["A", "B", "A", "B"],
            rollback_condition="p99 latency increases > 10%",
        )
        self.b1 = RunSample(
            treatment_id="baseline",
            iteration=1,
            duration_seconds=10.0,
            aggregate_goodput_mbps=42.0,
            p50_latency_ms=12.0,
            p95_latency_ms=45.0,
            p99_latency_ms=110.0,
            packet_loss_pct=1.2,
            retry_rate=0.15,
            jain_fairness_index=0.75,
        )
        self.c1 = RunSample(
            treatment_id="candidate",
            iteration=1,
            duration_seconds=10.0,
            aggregate_goodput_mbps=68.5,
            p50_latency_ms=8.0,
            p95_latency_ms=22.0,
            p99_latency_ms=48.0,
            packet_loss_pct=0.1,
            retry_rate=0.04,
            jain_fairness_index=0.91,
        )
        self.record = ExperimentResultRecord(
            metadata=self.meta,
            baseline_samples=[self.b1],
            candidate_samples=[self.c1],
            decision="KEEP",
            goodput_delta_pct=63.1,
            p99_latency_delta_pct=-56.4,
            fairness_delta_pct=21.3,
            p_value_goodput=0.005,
            p_value_p99_latency=0.002,
            rationale="Statistically significant +63.1% goodput gain with 56.4% latency drop.",
        )

    def test_generate_markdown_content(self):
        md = ReportGenerator.generate_markdown(self.record)
        self.assertIn("# Experiment Report: FMX-0013", md)
        self.assertIn("**[KEEP - PROMOTED]**", md)
        self.assertIn("LAP-120 AR9342 rev 2 + QCA9880", md)
        self.assertIn("## 1. Experiment Metadata", md)
        self.assertIn("## 2. Key Metrics Summary", md)
        self.assertIn("## 3. Per-Iteration Measurement Ledger", md)
        self.assertIn("Baseline (A)", md)
        self.assertIn("Candidate (B)", md)
        self.assertIn("+63.10%", md)
        self.assertIn("-56.40%", md)

    def test_save_report_to_disk(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_md = Path(tmp_dir) / "reports" / "FMX-0013_report.md"
            saved_md = ReportGenerator.save_report(self.record, out_md)

            self.assertTrue(saved_md.exists())
            self.assertTrue(saved_md.with_suffix(".json").exists())

            # Read back saved files
            content_md = saved_md.read_text(encoding="utf-8")
            content_json = saved_md.with_suffix(".json").read_text(encoding="utf-8")

            self.assertIn("# Experiment Report: FMX-0013", content_md)
            self.assertIn('"experiment_id": "FMX-0013"', content_json)


if __name__ == "__main__":
    unittest.main()
