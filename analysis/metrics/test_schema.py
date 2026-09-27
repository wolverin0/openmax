"""Unit tests for analysis.metrics.schema (ExperimentResultRecord and RunSample)."""

import unittest
from analysis.metrics.schema import (
    ExperimentMetadata,
    RunSample,
    ExperimentResultRecord,
)


class TestMetricsSchema(unittest.TestCase):
    def test_run_sample_auto_computations(self):
        # 4 CPEs with unequal rates: [10.0, 20.0, 30.0, 40.0]
        # sum = 100, sum^2 = 10000
        # sum_sq = 100 + 400 + 900 + 1600 = 3000
        # Jain index = 10000 / (4 * 3000) = 10000 / 12000 = 0.8333
        sample = RunSample(
            treatment_id="candidate",
            iteration=1,
            duration_seconds=10.0,
            aggregate_goodput_mbps=100.0,
            per_cpe_goodput_mbps={
                "cpe1": 10.0,
                "cpe2": 20.0,
                "cpe3": 30.0,
                "cpe4": 40.0,
            },
            p99_latency_ms=18.5,
        )
        self.assertAlmostEqual(sample.jain_fairness_index, 0.8333, places=4)
        self.assertEqual(sample.goodput_per_mhz, 2.5)  # 100 / 40 MHz

    def test_json_roundtrip_serialization(self):
        meta = ExperimentMetadata(
            experiment_id="FMX-0013",
            hypothesis="CoTSQ 6ms restores A-MPDU depth",
            hardware_revision="LAP-120 AR9342 rev 2",
            firmware_build_hash="openwrt-24.10.4-sha256",
            config_snapshot={"tcp_limit_output_bytes": 300000},
            topology="1 AP + 20 CPEs",
            channel_mhz=5180,
            channel_width_mhz=40,
            tx_power_dbm=20.0,
            attenuation_db=40.0,
            offered_load_profile="Saturated Reverse Mode",
            repetitions=4,
            treatment_order=["A", "B", "A", "B"],
            rollback_condition="p99 latency increases > 10%",
        )

        s_base = RunSample(
            treatment_id="baseline",
            iteration=1,
            duration_seconds=10.0,
            aggregate_goodput_mbps=42.0,
            p99_latency_ms=85.0,
        )

        s_cand = RunSample(
            treatment_id="candidate",
            iteration=1,
            duration_seconds=10.0,
            aggregate_goodput_mbps=68.5,
            p99_latency_ms=38.0,
        )

        record = ExperimentResultRecord(
            metadata=meta,
            baseline_samples=[s_base],
            candidate_samples=[s_cand],
            decision="KEEP",
            goodput_delta_pct=63.1,
            p99_latency_delta_pct=-55.3,
            p_value_goodput=0.002,
            p_value_p99_latency=0.001,
            rationale="Statistically significant 63% goodput increase with 55% p99 latency reduction",
        )

        json_data = record.to_json()
        deserialized = ExperimentResultRecord.from_json(json_data)

        self.assertEqual(deserialized.metadata.experiment_id, "FMX-0013")
        self.assertEqual(deserialized.decision, "KEEP")
        self.assertEqual(len(deserialized.baseline_samples), 1)
        self.assertEqual(len(deserialized.candidate_samples), 1)
        self.assertEqual(deserialized.candidate_samples[0].aggregate_goodput_mbps, 68.5)
        self.assertAlmostEqual(deserialized.goodput_delta_pct, 63.1)


if __name__ == "__main__":
    unittest.main()
