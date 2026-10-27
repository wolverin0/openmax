"""Tests for Phase 0 Workstream D: Explicit channel_width_mhz validation and goodput_per_mhz schema."""

from __future__ import annotations

import json
import pytest

from analysis.metrics.schema import (
    SUPPORTED_CHANNEL_WIDTHS_MHZ,
    ExperimentMetadata,
    ExperimentResultRecord,
    RunSample,
    migrate_legacy_record_dict,
    validate_channel_width_mhz,
)


def _make_metadata(width_mhz: int = 20) -> ExperimentMetadata:
    return ExperimentMetadata(
        experiment_id="PB-020",
        hypothesis="Exact channel width normalization eliminates 40 MHz bias",
        hardware_revision="LAP-120 + Loco5AC (AR9342 + QCA988x)",
        firmware_build_hash="openwrt-24.10.4-ath10k",
        config_snapshot={"channel_width_mhz": width_mhz},
        topology="PtP Lab Bench",
        channel_mhz=5745,
        channel_width_mhz=width_mhz,
        tx_power_dbm=8.0,
        attenuation_db=55.0,
        offered_load_profile="Bidirectional TCP + UDP RTT probe",
        repetitions=6,
        treatment_order=["A", "B", "A", "B", "A", "B"],
        rollback_condition="p99 latency regression > 10%",
    )


def test_supported_channel_widths_computed_accurately() -> None:
    assert SUPPORTED_CHANNEL_WIDTHS_MHZ == (5, 10, 20, 40, 80)
    for width in SUPPORTED_CHANNEL_WIDTHS_MHZ:
        sample = RunSample(
            treatment_id="baseline",
            iteration=1,
            duration_seconds=30.0,
            aggregate_goodput_mbps=100.0,
            channel_width_mhz=width,
        )
        assert sample.goodput_per_mhz == round(100.0 / float(width), 4)
        assert sample.require_verified_width() == width


def test_missing_channel_width_never_divides_by_40_silently() -> None:
    sample = RunSample(
        treatment_id="baseline",
        iteration=1,
        duration_seconds=30.0,
        aggregate_goodput_mbps=80.0,
    )
    # Previously this silently set goodput_per_mhz = 80.0 / 40.0 = 2.0!
    assert sample.goodput_per_mhz == 0.0
    assert sample.width_source == "unverified_missing_width"
    with pytest.raises(ValueError, match="missing a verified channel_width_mhz"):
        sample.require_verified_width()


def test_invalid_channel_widths_rejected() -> None:
    for invalid_width in (0, -20, 15, 30, 160, None, True):
        with pytest.raises(ValueError):
            validate_channel_width_mhz(invalid_width)  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="Invalid channel_width_mhz"):
        _make_metadata(width_mhz=25)

    with pytest.raises(ValueError, match="Inconsistent goodput_per_mhz"):
        RunSample(
            treatment_id="candidate",
            iteration=1,
            duration_seconds=30.0,
            aggregate_goodput_mbps=92.0,
            channel_width_mhz=20,
            goodput_per_mhz=2.3,  # Wrong 40 MHz normalized value for 20 MHz sample
        )


def test_experiment_result_record_propagates_metadata_width_and_rejects_mismatch() -> None:
    meta = _make_metadata(width_mhz=20)
    s_base = RunSample("baseline", 1, 30.0, 90.0, per_cpe_goodput_mbps={"cpe1": 45.0, "cpe2": 45.0})
    s_cand = RunSample("candidate", 1, 30.0, 102.0, per_cpe_goodput_mbps={"cpe1": 51.0, "cpe2": 51.0})

    record = ExperimentResultRecord(
        metadata=meta,
        baseline_samples=[s_base],
        candidate_samples=[s_cand],
    )
    assert record.baseline_samples[0].channel_width_mhz == 20
    assert record.baseline_samples[0].goodput_per_mhz == 4.5
    assert record.candidate_samples[0].goodput_per_mhz == 5.1

    roundtrip = ExperimentResultRecord.from_json(record.to_json())
    assert roundtrip.baseline_samples[0].goodput_per_mhz == 4.5
    assert roundtrip.candidate_samples[0].goodput_per_mhz == 5.1

    mismatched_sample = RunSample("candidate", 2, 30.0, 100.0, channel_width_mhz=40)
    with pytest.raises(ValueError, match="conflicts with ExperimentMetadata.channel_width_mhz"):
        ExperimentResultRecord(
            metadata=meta,
            baseline_samples=[s_base],
            candidate_samples=[mismatched_sample],
        )


def test_legacy_record_migration_corrects_40mhz_bias_reproducibly() -> None:
    legacy_payload = {
        "metadata": asdict_meta(_make_metadata(width_mhz=20)),
        "baseline_samples": [
            {
                "treatment_id": "baseline",
                "iteration": 1,
                "duration_seconds": 30.0,
                "aggregate_goodput_mbps": 80.0,
                "goodput_per_mhz": 2.0,  # Legacy 40 MHz hard-coded bug on a 20 MHz channel
            }
        ],
        "candidate_samples": [
            {
                "treatment_id": "candidate",
                "iteration": 1,
                "duration_seconds": 30.0,
                "aggregate_goodput_mbps": 90.0,
                "goodput_per_mhz": 2.25,  # Legacy 40 MHz hard-coded bug on a 20 MHz channel
            }
        ],
        "decision": "INCONCLUSIVE",
    }
    migrated = migrate_legacy_record_dict(legacy_payload)
    assert migrated["baseline_samples"][0]["goodput_per_mhz"] == 4.0
    assert migrated["baseline_samples"][0]["width_source"] == "legacy_migrated"
    assert migrated["candidate_samples"][0]["goodput_per_mhz"] == 4.5

    rec = ExperimentResultRecord.from_legacy_json(json.dumps(legacy_payload))
    assert rec.baseline_samples[0].goodput_per_mhz == 4.0
    assert rec.candidate_samples[0].goodput_per_mhz == 4.5


def asdict_meta(meta: ExperimentMetadata) -> dict:
    from dataclasses import asdict
    return asdict(meta)
