#!/usr/bin/env python3
"""Unit tests for Stage 78A Live Multi-Generation aeon Regime Classifier Bridge."""

from __future__ import annotations

import json
from pathlib import Path

from tools.telemetry.run_stage61a_unified_multigen_deterministic_rf_collector import (
    OUT_JSON_PATH as STAGE61A_JSON_PATH,
    classify_all_multigen_links,
    classify_multigen_collector_window,
    snapshots_to_aeon_multivariate_window,
)
from tools.telemetry.run_stage78a_live_multigen_regime_classifier_bridge import (
    DEFAULT_OUTPUT_JSON,
    run_stage78a_live_multigen_regime_classifier_bridge,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE78A_LIVE_MULTIGEN_AEON_REGIME_CLASSIFIER_BRIDGE.md"


def test_stage78a_snapshots_to_aeon_window_and_classification() -> None:
    s61 = json.loads(STAGE61A_JSON_PATH.read_text(encoding="utf-8"))
    r1, r2 = s61["round1"], s61["round2"]

    X_win = snapshots_to_aeon_multivariate_window([r1, r2], "Loco5AC_WA_OpenWrt", n_timepoints=60)
    assert X_win.shape == (1, 6, 60)

    live_all = classify_all_multigen_links([r1, r2])
    assert len(live_all) == 5
    for link_id, res in live_all.items():
        assert res["aeon_regime_id"] == 0, f"{link_id} expected NORMAL_LOAD"
        assert res["aeon_regime_name"] == "NORMAL_LOAD"
        assert res["deterministic_monitor_status"] == "UP"
        assert res["kuma_push_allowed"] is True
        assert res["is_false_alarm_suppressed"] is False
        assert 0.50 <= res["confidence"] <= 1.0

    frozen_res = classify_multigen_collector_window([r1, r1], "LTU_Lite_AF_LTU_OTA")
    assert frozen_res["aeon_regime_id"] == 4
    assert frozen_res["aeon_regime_name"] == "FROZEN_COLLECTOR_FALSE_ALARM"
    assert frozen_res["deterministic_monitor_status"] == "MONITOR_STALE_ERROR"
    assert frozen_res["kuma_push_allowed"] is False
    assert frozen_res["is_false_alarm_suppressed"] is True


def test_stage78a_bridge_receipt_and_5pillar_gate() -> None:
    payload = run_stage78a_live_multigen_regime_classifier_bridge()
    assert DEFAULT_OUTPUT_JSON.exists()
    gate = audit_stage_receipt_5pillars(payload)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"

    summary = payload["bridge_summary"]
    assert summary["monitored_links_count"] == 5
    assert summary["hardware_generations_covered"] == 4
    assert summary["all_live_advancing_windows_normal_load"] is True
    assert summary["all_frozen_collector_windows_suppressed"] is True
    assert summary["all_fault_injection_regimes_matched"] is True
    assert summary["false_positive_rf_alarm_rate"] == 0.0
    assert "fmx_aeon_regime_id" in payload["prometheus_regime_metrics_text"]


def test_stage78a_doc_budget() -> None:
    assert DOC_PATH.exists()
    lines = DOC_PATH.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert lines[0].startswith("<!-- doc-head:")
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
