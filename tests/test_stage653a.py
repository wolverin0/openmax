#!/usr/bin/env python3
"""Tests for Stage 653A: SimPy + pymoo NSGA-II Triple-Patch Pareto Validation."""
from __future__ import annotations

from tools.sim.run_stage653a_pb040_pb050_pb060_triple_patch_pareto import (
    OUT_JSON,
    ROOT,
    run_stage653a_pareto,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage653a_pb040_pb050_pb060_triple_patch_pareto() -> None:
    rep = run_stage653a_pareto()
    assert OUT_JSON.exists()
    assert rep["stage"] == "653A"
    assert rep["status"] == "CONFIRMED"
    assert rep["live_devices_touched"] is False
    assert audit_stage_receipt_5pillars(rep)["compliant"] is True

    p = rep["profiles_evaluated"]
    s_stock = p["stock_10_1_467_ct_and_v8725"]
    s_pb040 = p["pb040_retry_aggr_only"]
    s_dual = p["pb040_plus_pb050_dual_patch"]
    s_triple = p["pb040_plus_pb050_plus_pb060_triple_patch"]

    assert (
        s_triple["goodput_mbps"]
        > s_dual["goodput_mbps"]
        > s_pb040["goodput_mbps"]
        > s_stock["goodput_mbps"]
    )
    assert (
        s_triple["p99_latency_ms"]
        < s_dual["p99_latency_ms"]
        < s_stock["p99_latency_ms"]
    )
    assert (
        s_triple["triple_play_qoe_score"]
        > s_dual["triple_play_qoe_score"]
        > s_stock["triple_play_qoe_score"]
    )
    assert rep["nsga2_pareto_front_count"] >= 5

    doc_path = (
        ROOT / "docs" / "STAGE653A_PB040_PB050_PB060_TRIPLE_PATCH_PARETO.md"
    )
    assert doc_path.exists()
    lines = doc_path.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
