"""Pytest suite for Stages 597A to 602A (192-Window Multi-Radio Milestone, 600-Stage Master Synthesis & Cross-Fleet Champion v52.0)."""
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


def test_stage597a_192window_multi_radio_milestone() -> None:
    data = _load("artifacts/autoresearch/stage597a_192window_multi_radio_milestone_r117_r122.json")
    assert data["stage"] == "STAGE-597A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_multi_radio_windows"] == 192
    assert data["new_windows_in_stage597a"] == 12
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["touched_250"] is False
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE597A_192WINDOW_MULTI_RADIO_MILESTONE_R117_R122.md")


def test_stage598a_ltu_lbt_and_interference_mitigation_pareto() -> None:
    data = _load("artifacts/autoresearch/stage598a_ltu_lbt_and_interference_mitigation_pareto.json")
    assert data["stage"] == "STAGE-598A"
    assert data["status"] == "CONFIRMED"
    assert len(data["pareto_front_ids"]) >= 2
    assert data["recommended_champion"]["collision_loss_pct"] == 0.0
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE598A_LTU_LBT_AND_INTERFERENCE_MITIGATION_PARETO.md")


def test_stage599a_pbe5ac_lbe5ac_triple_play_vht40_certification() -> None:
    data = _load("artifacts/autoresearch/stage599a_pbe5ac_lbe5ac_triple_play_vht40_field_certification.json")
    assert data["stage"] == "STAGE-599A"
    assert data["status"] == "CONFIRMED"
    assert data["stage487a_vht40_certification"]["vht40_bulk_tcp_mbps"] == 24.83
    assert data["stage488a_triple_play_certification"]["iptv_loss_cs4_certified_pct"] == 0.0
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE599A_PBE5AC_LBE5AC_TRIPLE_PLAY_VHT40_FIELD_CERTIFICATION.md")


def test_stage600a_600stage_ground_up_master_synthesis() -> None:
    data = _load("artifacts/autoresearch/stage600a_600stage_ground_up_master_synthesis.json")
    assert data["stage"] == "STAGE-600A"
    assert data["status"] == "CONFIRMED"
    assert data["milestone_stage_number"] == 600
    assert len(data["radio_families_covered"]) == 8
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE600A_600STAGE_GROUND_UP_MASTER_SYNTHESIS.md")


def test_stage601a_cross_fleet_champion_v52() -> None:
    data = _load("artifacts/autoresearch/stage601a_cross_fleet_champion_v52_and_tester_matrix.json")
    assert data["stage"] == "STAGE-601A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v52.0"
    assert data["window_totals"]["total_cross_lane_windows"] == 600
    assert data["radio_families_count"] == 8
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE601A_CROSS_FLEET_CHAMPION_V52_AND_TESTER_MATRIX.md")


def test_stage602a_600stage_multi_radio_v52_gate() -> None:
    data = _load("artifacts/verification/stage602a_600stage_multi_radio_v52_gate_receipt.json")
    assert data["stage"] == "STAGE-602A"
    assert data["status"] == "CONFIRMED"
    assert data["all_stages_passed"] is True
    assert data["five_pillar_compliant"] is True
    _check_doc("docs/STAGE602A_600STAGE_MULTI_RADIO_V52_GATE.md")
