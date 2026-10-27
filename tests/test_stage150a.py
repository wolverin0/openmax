from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage150a_ltu_vs_openmax_ptmp_pareto_receipt.json"


def test_stage150a_receipt_exists_and_safety_envelope() -> None:
    assert RECEIPT_PATH.exists(), f"Missing {RECEIPT_PATH}"
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "150A"
    assert data["status"] == "CONFIRMED"
    assert data["safety_envelope"]["simulation_only"] is True
    assert data["safety_envelope"]["touched_dev_ame_nodes"] is False
    assert data["safety_envelope"]["touched_241_or_242"] is False
    assert data["sector_topology"]["cpe_count"] == 32


def test_stage150a_head_to_head_and_pareto_front() -> None:
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    h2h = data["head_to_head_profiles_40mhz"]
    ltu80 = h2h["ltu_12x_80sym_67_33_champion"]
    openmax = h2h["openmax_wa_xc_8x_aql4500_fq3028_champion"]
    legacy = h2h["stock_80211ac_legacy_24ms_bufferbloat"]

    assert ltu80["sector_aggregate_goodput_mbps"] > openmax["sector_aggregate_goodput_mbps"]
    assert openmax["p99_sojourn_latency_ms"] < legacy["p99_sojourn_latency_ms"]
    assert data["comparative_deltas"]["ltu_12x_vs_openmax_8x_goodput_gain_pct"] > 10.0

    pf = data["nsga2_pareto_front"]
    assert pf["pareto_solutions_count"] >= 1
    assert len(pf["top_10_pareto_solutions"]) >= 1


def test_stage150a_five_pillars() -> None:
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    for k in (
        "pillar_1_binary_re",
        "pillar_2_closed_loop_reactor",
        "pillar_3_counterbalanced_harness",
        "pillar_4_scientific_skills",
        "pillar_5_memory_master",
    ):
        assert data[k]["status"] == "CONFIRMED"
