"""Consolidated pytest suite for Stages 721A to 726A (240-Window Multi-Radio Milestone & Cross-Fleet Champion v56.0)."""
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


def test_stage721a_multi_radio_240w_milestone_campaign() -> None:
    data = _load("artifacts/autoresearch/stage721a_multi_radio_240w_milestone_campaign.json")
    assert data["stage"] == "STAGE-721A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 240
    assert data["integrated_lanes"]["total_cross_lane_windows"] == 796
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE721A_MULTI_RADIO_240W_MILESTONE_CAMPAIGN.md")


def test_stage722a_nsga3_pareto_pcie_ce_rings_and_ack_timeout() -> None:
    data = _load("artifacts/autoresearch/stage722a_nsga3_pareto_pcie_ce_rings_and_ack_timeout.json")
    assert data["stage"] == "STAGE-722A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 2
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE722A_NSGA3_PARETO_PCIE_CE_RINGS_AND_ACK_TIMEOUT.md")


def test_stage723a_cross_fleet_champion_v56_bundle() -> None:
    data = _load("artifacts/autoresearch/stage723a_cross_fleet_champion_v56_bundle.json")
    assert data["stage"] == "STAGE-723A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v56.0"
    assert data["ptp_champion_v4_vht40_mbps"] == 25.47
    assert data["window_totals"]["total_cross_lane_windows"] == 796
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE723A_CROSS_FLEET_CHAMPION_V56_BUNDLE.md")


def test_stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim() -> None:
    data = _load("artifacts/autoresearch/stage724a_ptmp_mixed_openwrt_vs_airos8_amsdu_airtime_sim.json")
    assert data["stage"] == "STAGE-724A"
    assert data["status"] == "CONFIRMED"
    assert data["payload_density_ratio_7935_vs_3839"] == 1.95
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE724A_PTMP_MIXED_OPENWRT_VS_AIROS8_AMSDU_AIRTIME_SIM.md")


def test_stage725a_memorymaster_240w_v56_ledger() -> None:
    data = _load("artifacts/autoresearch/stage725a_memorymaster_240w_v56_ledger.json")
    assert data["stage"] == "STAGE-725A"
    assert data["status"] == "CONFIRMED"
    assert data["scope"] == "project:futuramax"
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE725A_MEMORYMASTER_240W_V56_LEDGER.md")


def test_stage726a_multi_radio_240w_v56_gate() -> None:
    data = _load("artifacts/autoresearch/stage726a_multi_radio_240w_v56_gate_receipt.json")
    assert data["stage"] == "STAGE-726A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE726A_MULTI_RADIO_240W_V56_GATE.md")
