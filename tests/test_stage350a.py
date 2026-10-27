#!/usr/bin/env python3
"""Pytest suite for Stage 350A — Cooperative CPE Control-Plane Differential Sensing Engine."""

from __future__ import annotations

import json

from tools.observability.build_stage350a_cooperative_cpe_differential_classifier import (
    ARTIFACT_OUT,
    C_CLASSIFIER_OUT,
    CpeTelemetrySample,
    build_stage350a_report,
    classify_sector_telemetry,
)


def test_stage350a_zero_false_positives_across_all_classes() -> None:
    report = build_stage350a_report()
    assert ARTIFACT_OUT.exists()
    assert C_CLASSIFIER_OUT.exists()
    loaded = json.loads(ARTIFACT_OUT.read_text(encoding="utf-8"))
    assert loaded["stage"] == "350A"
    assert loaded["memory_master_claim_id"] == "mm-7295"
    metrics = loaded["classification_metrics"]
    assert metrics["scenarios_tested"] == 5
    assert metrics["scenarios_correct"] == 5
    assert metrics["false_positive_count"] == 0
    assert metrics["false_positive_rate_pct"] == 0.0
    assert metrics["accuracy_pct"] == 100.0


def test_stage350a_individual_fault_discrimination() -> None:
    samples = [
        CpeTelemetrySample("CPE1", 10.0, -30.0, 0.5, 2.0, 1.0, 0, 0, 0),
        CpeTelemetrySample("CPE2_FOLIAGE", 25.0, -22.0, 3.6, 15.0, 7.8, 0, 0, 0),
        CpeTelemetrySample("CPE3_POE", 40.0, -31.0, 0.6, 3.0, 1.1, 0, 4, 12),
    ]
    res = classify_sector_telemetry(samples)
    assert res["per_cpe_verdicts"]["CPE1"]["verdict"] == "HEALTHY_SECTOR"
    assert res["per_cpe_verdicts"]["CPE2_FOLIAGE"]["verdict"] == "SINGLE_CPE_FRESNEL_FOLIAGE_OBSTRUCTION"
    assert res["per_cpe_verdicts"]["CPE3_POE"]["verdict"] == "LAN_POE_CABLE_CARRIER_FAULT"
