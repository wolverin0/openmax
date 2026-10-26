#!/usr/bin/env python3
"""
Tests for Stage 99B (`T-S99B-LTU-80SYMBOL-SUPERFRAME-SIMPY-AND-PYMOO-PARETO-MODEL`).
"""

from __future__ import annotations

import json

from tools.sim.run_stage99b_ltu_80symbol_superframe_simpy_pymoo import (
    DEFAULT_OUT_JSON,
    DOC_PATH,
    compute_superframe_geometry,
    run_stage99b_simpy_and_pymoo,
    simulate_ltu_superframe_simpy,
)
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars


def test_stage99b_canonical_80symbol_superframe_geometry() -> None:
    idle = compute_superframe_geometry(2.0, 750, 0)
    assert idle["total_symbols"] == 80
    assert idle["dl_total_symbols"] == 61
    assert idle["ul_total_symbols"] == 19
    assert idle["dl_duty_pct"] == 76.25
    assert idle["ul_duty_pct"] == 23.75
    assert idle["dl_preamble_symbols"] == 1
    assert idle["dl_beacon_symbols"] == 2
    assert idle["dl_null_symbols"] == 58
    assert idle["ul_reserve_symbols"] == 19

    for fp, expected_sym in ((1.0, 40), (2.0, 80), (4.0, 160)):
        geom = compute_superframe_geometry(fp, 670, 8)
        assert geom["total_symbols"] == expected_sym
        assert geom["dl_total_symbols"] + geom["ul_total_symbols"] == expected_sym
        assert geom["dl_data_symbols"] > 0
        assert geom["ul_data_symbols"] > 0


def test_stage99b_simpy_and_pymoo_pareto_execution() -> None:
    unpinned = simulate_ltu_superframe_simpy(2.0, 750, 10, 8, smp_isolated=False)
    isolated = simulate_ltu_superframe_simpy(2.0, 750, 10, 8, smp_isolated=True)
    assert isolated["agg_goodput_mbps"] > unpinned["agg_goodput_mbps"]
    assert isolated["voip_p99_rtt_ms"] < unpinned["voip_p99_rtt_ms"]
    assert isolated["cpu0_isr_headroom_pct"] > unpinned["cpu0_isr_headroom_pct"]

    receipt = run_stage99b_simpy_and_pymoo()
    assert DEFAULT_OUT_JSON.exists()
    assert receipt["stage"] == "99B"
    assert receipt["status"] == "CONFIRMED"
    assert receipt["grid_configurations_evaluated"] == 288
    pareto = receipt["pymoo_nsga2_pareto_summary"]
    assert pareto["pop_size"] == 40
    assert pareto["n_gen"] == 25
    assert pareto["seed"] == 99
    assert pareto["unique_pareto_front_count"] >= 8
    assert all(sol["smp_isolated"] is True for sol in pareto["top_pareto_solutions"])


def test_stage99b_doc_and_5pillar_gate_compliance() -> None:
    loaded = json.loads(DEFAULT_OUT_JSON.read_text(encoding="utf-8"))
    audit = audit_stage_receipt_5pillars(loaded)
    assert audit["compliant"] is True, f"5-pillar gate failed: {audit}"

    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 180, f"{DOC_PATH.name} has {len(lines)} lines (>= 180)"
    doc_heads = [ln for ln in lines if "<!-- doc-head" in ln]
    assert len(doc_heads) == 1, f"{DOC_PATH.name} must have exactly 1 doc-head"
