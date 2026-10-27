#!/usr/bin/env python3
"""Pytest suite for Stage 442A — Ground-Up 5-Pillars Combined SimPy + pymoo NSGA-II Pareto."""

from __future__ import annotations

import json

from tools.sim.run_stage442a_ground_up_5pillars_combined_pareto import (
    OUT_JSON,
    OUT_MD,
    run_stage442a,
)


def test_stage442a_5pillar_pareto_dominance() -> None:
    report = run_stage442a()
    assert OUT_JSON.exists()
    assert OUT_MD.exists()
    loaded = json.loads(OUT_JSON.read_text(encoding="utf-8"))
    assert loaded["stage"] == "442A"
    assert loaded["memory_master_claim_id"] == "mm-6005"
    comp = loaded["baselines_vs_5pillar_champion"]
    airos = comp["stock_airos8"]
    owrt = comp["openwrt_stock"]
    champ = comp["fmx_5pillar_ground_up_champion"]

    assert champ["combined_sector_goodput_mbps"] > owrt["combined_sector_goodput_mbps"] > airos["combined_sector_goodput_mbps"]
    assert champ["triple_play_p99_latency_ms"] < owrt["triple_play_p99_latency_ms"] < airos["triple_play_p99_latency_ms"]
    assert champ["fault_false_positive_rate_pct"] == 0.0
    assert report["pareto_front_sample_count"] >= 5
