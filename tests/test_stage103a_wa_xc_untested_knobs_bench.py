"""Unit and integration verification tests for Stage 103A (T-S103A-LIVE-WA-XC-TOP-UNTESTED-UPH-KNOBS-BENCHMARK)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.benchmarks.run_stage103a_wa_xc_untested_knobs_bench import DEFAULT_OUT_JSON
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]
DOC_PATH = REPO_ROOT / "docs" / "STAGE103A_WA_XC_UNTESTED_KNOBS_BENCHMARK.md"


def test_stage103a_receipt_exists_and_passes_5pillars() -> None:
    assert DEFAULT_OUT_JSON.exists(), f"Missing receipt {DEFAULT_OUT_JSON}"
    data = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))

    assert data["stage"] == "Stage 103A"
    assert data["task_id"] == "T-S103A-LIVE-WA-XC-TOP-UNTESTED-UPH-KNOBS-BENCHMARK"
    assert data["protocol"] == "A1->B1->A2->B2"
    assert int(data["watchdog_seconds"]) == 45

    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar gate failed: {gate}"


def test_stage103a_live_readbacks_and_counterbalanced_windows() -> None:
    data = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    probe = data["live_uph_and_distance_audit"]
    xc_readback = probe["xc_198_uph_and_umac_readback"]
    assert "post_swr_limit_3_vector" in xc_readback
    assert "ff_cap_rep_shared_buffer_mirror" in xc_readback
    assert "sta_priority_3int_vector" in xc_readback
    assert "ptp_xmit_scalar" in xc_readback
    assert "noack_mode_scalar" in xc_readback
    assert "wifi0_get_distance_m" in xc_readback
    assert len(probe["kernel_boundary_discoveries"]) >= 3

    windows = data["windows"]
    assert [w["window"] for w in windows] == ["A1", "B1", "A2", "B2"]
    assert [w["arm"] for w in windows] == ["A", "B", "A", "B"]

    for w in windows:
        assert float(w["aggregate_goodput_mbps"]) > 25.0
        assert float(w["wa_ping_metrics"]["p50_ms"]) > 0.0
        assert float(w["wa_ping_metrics"]["loss_pct"]) == 0.0

    summary = data["stage103a_summary"]
    assert float(summary["arm_b_goodput_mbps"]) > 25.0
    assert float(summary["sector_p95_rtt_delta_pct"]) < 0.0
    assert summary["decision"] in ("PROMOTE_NEW_CHAMPION", "RETAIN_CURRENT_CHAMPION")


def test_stage103a_doc_budget_and_doc_head() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"{DOC_PATH.name} has {len(lines)} lines (must be < 180)"
    assert lines[0].startswith("<!-- doc-head:"), "Doc must start with <!-- doc-head: on line 1"
    doc_heads = [ln for ln in lines if "<!-- doc-head:" in ln]
    assert len(doc_heads) == 1
    for token in (
        "T-S103A-LIVE-WA-XC-TOP-UNTESTED-UPH-KNOBS-BENCHMARK",
        "swr_limit",
        "sta_priority",
        "ptp_xmit",
        "noack_mode",
        "FMX-S103A-KB-01",
    ):
        assert token in text, f"Missing token {token} in {DOC_PATH.name}"
