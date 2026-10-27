"""Pytest suite for Stages 577A to 582A (180-Window Multi-Radio Milestone & Cross-Fleet Champion v51.0)."""
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
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1


def test_stage577a_180window_multi_radio_milestone() -> None:
    data = _load("artifacts/autoresearch/stage577a_180window_multi_radio_milestone_r111_r116.json")
    assert data["stage"] == "STAGE-577A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 180
    assert data["new_windows_in_stage577a"] == 12
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE577A_180WINDOW_MULTI_RADIO_MILESTONE_R111_R116.md")


def test_stage578a_qca_paprd_olpc_clpc_evm_pareto() -> None:
    data = _load("artifacts/autoresearch/stage578a_qca_paprd_olpc_clpc_evm_pareto.json")
    assert data["stage"] == "STAGE-578A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 2
    assert data["recommended_champion"]["evm_db"] <= -34.0
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE578A_QCA_PAPRD_OLPC_CLPC_EVM_PARETO.md")


def test_stage579a_ltu_tdma_framelen_and_split_freq_pareto() -> None:
    data = _load("artifacts/autoresearch/stage579a_ltu_tdma_framelen_and_split_freq_pareto.json")
    assert data["stage"] == "STAGE-579A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 3
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE579A_LTU_TDMA_FRAMELEN_AND_SPLIT_FREQ_PARETO.md")


def test_stage580a_panel1_guarida_84_v9_expansion_blueprint() -> None:
    data = _load("artifacts/autoresearch/stage580a_panel1_guarida_84_v9_to_panel2_panel3_expansion_blueprint.json")
    assert data["stage"] == "STAGE-580A"
    assert data["status"] == "CONFIRMED"
    assert data["guarida_topology_truth"]["total_panels"] == 3
    assert data["guarida_topology_truth"]["total_cpes"] == 32
    assert data["guarida_topology_truth"]["panel1_guarida_84"]["v9_burn_in_hours"] == 19.36
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE580A_PANEL1_GUARIDA_84_V9_TO_PANEL2_PANEL3_EXPANSION_BLUEPRINT.md")


def test_stage581a_cross_fleet_champion_v51() -> None:
    data = _load("artifacts/autoresearch/stage581a_cross_fleet_champion_v51_and_tester_bundle.json")
    assert data["stage"] == "STAGE-581A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v51.0"
    assert data["window_totals"]["total_cross_lane_windows"] == 588
    assert data["radio_families_count"] == 8
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE581A_CROSS_FLEET_CHAMPION_V51_AND_TESTER_BUNDLE.md")


def test_stage582a_multi_radio_v51_suite_gate() -> None:
    data = _load("artifacts/verification/stage582a_multi_radio_v51_suite_gate_receipt.json")
    assert data["stage"] == "STAGE-582A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE582A_MULTI_RADIO_V51_SUITE_GATE.md")
