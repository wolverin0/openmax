"""Unit tests for Stage 15 3-Unit LTU PtMP Sector Benchmark and WallDetectorGate."""

from __future__ import annotations

import json
import pathlib
import pytest

from tools.bench.run_stage15_ltu_ptmp_sector import (
    CANDIDATE_ROUNDS,
    DEFAULT_OUTPUT_PATH,
    UNITS,
    WallDetectorGate,
    compute_jain_fairness,
    compute_objective_j,
    compute_percentiles,
    evaluate_round_decision,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE15_LTU_PTMP_3UNIT_OTA_BENCHMARK.md"


def test_wall_detector_gate_early_stop_and_reset() -> None:
    gate = WallDetectorGate(goodput_threshold_pct=1.5, p95_threshold_pct=5.0, patience=2)

    # Round 1: significant improvement (+4.0% goodput, -20.0% p95) -> not within wall band
    r1 = gate.evaluate("LTU-S15-R1", 40.0, 41.6, 100.0, 80.0)
    assert not r1.is_within_wall_band
    assert r1.consecutive_wall_hits == 0
    assert not r1.stop_early

    # Round 2: within wall band (+0.8% goodput, -2.0% p95) -> hit 1/2
    r2 = gate.evaluate("LTU-S15-R2", 41.6, 41.93, 80.0, 78.4)
    assert r2.is_within_wall_band
    assert r2.consecutive_wall_hits == 1
    assert not r2.stop_early

    # Round 3: large shift (-12.0% p95) -> resets consecutive_wall_hits to 0
    r3 = gate.evaluate("LTU-S15-R3", 41.93, 42.10, 78.4, 69.0)
    assert not r3.is_within_wall_band
    assert r3.consecutive_wall_hits == 0
    assert not r3.stop_early

    # Round 4 & 5: two consecutive rounds inside |dGoodput|<1.5% and |dp95|<5.0% -> stop_early=True
    r4 = gate.evaluate("LTU-S15-R4", 42.10, 42.30, 69.0, 68.1)
    assert r4.is_within_wall_band
    assert r4.consecutive_wall_hits == 1
    assert not r4.stop_early

    r5 = gate.evaluate("LTU-S15-R5", 42.30, 42.45, 68.1, 67.5)
    assert r5.is_within_wall_band
    assert r5.consecutive_wall_hits == 2
    assert r5.stop_early
    assert "WALL_DETECTED" in r5.reason


def test_wall_detector_validation_errors() -> None:
    with pytest.raises(ValueError):
        WallDetectorGate(goodput_threshold_pct=0.0, p95_threshold_pct=5.0)
    with pytest.raises(ValueError):
        WallDetectorGate(goodput_threshold_pct=1.5, p95_threshold_pct=5.0, patience=0)


def test_metrics_and_round_decision_helpers() -> None:
    assert compute_jain_fairness([14.0, 14.0]) == pytest.approx(1.0)
    assert 0.99 < compute_jain_fairness([13.8, 14.1, 13.9]) <= 1.0
    assert compute_jain_fairness([]) == 0.0

    pcts = compute_percentiles([20.0, 22.0, 24.0, 26.0, 50.0])
    assert pcts["p50_ms"] == 24.0
    assert pcts["p95_ms"] == 50.0

    j_base = compute_objective_j(30.0, 80.0, 40.0)
    j_cand = compute_objective_j(29.5, 48.0, 41.2)
    assert j_cand < j_base
    assert evaluate_round_decision(30.0, 29.5, 80.0, 48.0, 40.0, 41.2, j_base, j_cand) == "KEEP"
    # Guardrail reject when p50 degrades > 6%
    assert evaluate_round_decision(30.0, 33.0, 80.0, 48.0, 40.0, 41.2, j_base, j_cand) == "REJECT"


def test_stage15_units_and_candidate_rounds_inventory() -> None:
    assert len(UNITS) == 3
    assert UNITS[0]["boca"] == 7
    assert UNITS[0]["host"] == "fe80::e263:daff:febf:a4f6%27"
    assert UNITS[0]["short_fw"] == "aflturocket.v2.1.0"
    assert UNITS[1]["boca"] == 5
    assert UNITS[1]["host"] == "fe80::e063:daff:febf:5399%27"
    assert UNITS[2]["boca"] == 2
    assert UNITS[2]["host"] == "fe80::e063:daff:febf:58cc%27"
    assert len(CANDIDATE_ROUNDS) == 8
    assert [r["round_id"] for r in CANDIDATE_ROUNDS] == [f"LTU-S15-R{i}" for i in range(1, 9)]


def test_stage15_artifact_and_doc_integrity() -> None:
    assert DEFAULT_OUTPUT_PATH.exists(), f"Missing artifact {DEFAULT_OUTPUT_PATH}"
    data = json.loads(DEFAULT_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert data["experiment_id"] == "FMX-STAGE15-LTU-PTMP-3UNIT-SECTOR"
    assert len(data["units"]) == 3
    assert data["final_ap_cool_power_guard"]["powerout"] == 0
    assert 1 <= len(data["rounds"]) <= 8

    for r in data["rounds"]:
        assert r["round_id"].startswith("LTU-S15-R")
        assert r["ap_cool_power_guard_post_round"]["powerout"] == 0
        assert r["summary"]["decision"] in ("KEEP", "REJECT")
        assert "wall_detector" in r["summary"]
        for phase in ("A1", "B1", "A2", "B2"):
            assert r[phase]["aggregate_goodput_mbps"] > 0.0
            assert r[phase]["ap_powerout"] == 0

    assert DOC_PATH.exists(), f"Missing documentation {DOC_PATH}"
    doc_text = DOC_PATH.read_text(encoding="utf-8")
    assert "fe80::e263:daff:febf:a4f6%27" in doc_text
    assert "fe80::e063:daff:febf:5399%27" in doc_text
    assert "fe80::e063:daff:febf:58cc%27" in doc_text
    assert "WallDetectorGate" in doc_text
