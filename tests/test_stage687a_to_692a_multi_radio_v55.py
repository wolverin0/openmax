"""Consolidated pytest suite for Stages 687A to 692A (228-Window Multi-Radio Milestone & Cross-Fleet Champion v55.0)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _load(rel_path: str) -> dict:
    p = ROOT / rel_path
    assert p.exists(), f"Missing artifact: {rel_path}"
    return json.loads(p.read_text(encoding="utf-8"))


def _check_doc(rel_path: str) -> None:
    p = ROOT / rel_path
    assert p.exists(), f"Missing doc: {rel_path}"
    text = p.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1


def test_stage687a_multi_radio_228w_milestone_campaign() -> None:
    data = _load("artifacts/autoresearch/stage687a_multi_radio_228w_milestone_campaign.json")
    assert data["stage"] == "STAGE-687A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 228
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE687A_MULTI_RADIO_228W_MILESTONE_CAMPAIGN.md")


def test_stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33() -> None:
    data = _load("artifacts/autoresearch/stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33.json")
    assert data["stage"] == "STAGE-688A"
    assert data["status"] == "CONFIRMED"
    assert data["panel2_82_dl_airtime_gain_pct"] == 34.84
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE688A_NSGA3_PARETO_SLOT_GUARD_AND_DL_UL_67_33.md")


def test_stage689a_cross_fleet_champion_v55_bundle() -> None:
    data = _load("artifacts/autoresearch/stage689a_cross_fleet_champion_v55_bundle.json")
    assert data["stage"] == "STAGE-689A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v55.0"
    assert data["guarida_v6_aggregate_capacity_mbps"] == 457.90
    assert data["window_totals"]["total_cross_lane_windows"] == 728
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE689A_CROSS_FLEET_CHAMPION_V55_BUNDLE.md")


def test_stage690a_ptp_vht40_vs_vht80_near_field_isi_sim() -> None:
    data = _load("artifacts/autoresearch/stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.json")
    assert data["stage"] == "STAGE-690A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_goodput_mbps"] == 24.83
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE690A_PTP_VHT40_VS_VHT80_NEAR_FIELD_ISI_SIM.md")


def test_stage691a_memorymaster_228w_v55_ledger() -> None:
    data = _load("artifacts/autoresearch/stage691a_memorymaster_228w_v55_ledger.json")
    assert data["stage"] == "STAGE-691A"
    assert data["status"] == "CONFIRMED"
    assert data["scope"] == "project:futuramax"
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE691A_MEMORYMASTER_228W_V55_LEDGER.md")


def test_stage692a_multi_radio_228w_v55_gate() -> None:
    data = _load("artifacts/autoresearch/stage692a_multi_radio_228w_v55_gate_receipt.json")
    assert data["stage"] == "STAGE-692A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE692A_MULTI_RADIO_228W_V55_GATE.md")
