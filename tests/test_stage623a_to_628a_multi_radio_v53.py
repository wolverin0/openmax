"""Pytest suite for Stages 623A to 628A (204-Window Multi-Radio Milestone & Cross-Fleet Champion v53.0)."""
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


def test_stage623a_204window_multi_radio_milestone() -> None:
    data = _load("artifacts/autoresearch/stage623a_204window_multi_radio_milestone_r123_r128.json")
    assert data["stage"] == "STAGE-623A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 204
    assert data["new_windows_in_stage623a"] == 12
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE623A_204WINDOW_MULTI_RADIO_MILESTONE_R123_R128.md")


def test_stage624a_qca988x_txbf_stbc_ldpc_pareto() -> None:
    data = _load("artifacts/autoresearch/stage624a_qca988x_txbf_stbc_ldpc_near_vs_far_field_pareto.json")
    assert data["stage"] == "STAGE-624A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 2
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE624A_QCA988X_TXBF_STBC_LDPC_NEAR_VS_FAR_FIELD_PARETO.md")


def test_stage625a_ltu_tof_ranging_and_cp_guard_pareto() -> None:
    data = _load("artifacts/autoresearch/stage625a_ltu_tof_ranging_and_cp_guard_pareto.json")
    assert data["stage"] == "STAGE-625A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 2
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE625A_LTU_TOF_RANGING_AND_CP_GUARD_PARETO.md")


def test_stage626a_guarida_full_tower_amsdu_and_slot_guard() -> None:
    data = _load("artifacts/autoresearch/stage626a_guarida_full_tower_amsdu_and_slot_guard_synthesis.json")
    assert data["stage"] == "STAGE-626A"
    assert data["status"] == "CONFIRMED"
    assert data["guarida_3panel_32cpe_summary"]["total_panels"] == 3
    assert data["guarida_3panel_32cpe_summary"]["total_cpes"] == 32
    assert data["guarida_3panel_32cpe_summary"]["stage533a_slot_guard_synthesis"]["optimal_slot_guard_us"] == 39
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE626A_GUARIDA_FULL_TOWER_AMSDU_AND_SLOT_GUARD_SYNTHESIS.md")


def test_stage627a_cross_fleet_champion_v53_200w_all_lanes() -> None:
    data = _load("artifacts/autoresearch/stage627a_cross_fleet_champion_v53_200w_all_lanes.json")
    assert data["stage"] == "STAGE-627A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v53.0"
    assert data["all_lanes_above_200_windows"] is True
    assert data["window_totals"]["total_cross_lane_windows"] == 648
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE627A_CROSS_FLEET_CHAMPION_V53_200W_ALL_LANES.md")


def test_stage628a_multi_radio_204w_v53_gate() -> None:
    data = _load("artifacts/verification/stage628a_multi_radio_204w_v53_gate_receipt.json")
    assert data["stage"] == "STAGE-628A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE628A_MULTI_RADIO_204W_V53_GATE.md")
