from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage519a_156window_multi_radio_milestone() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage519a_156window_multi_radio_milestone_r99_r104.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-519A"
    assert data["cumulative_multi_radio_windows"] == 156
    assert data["new_windows_in_stage519a"] == 12
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage520a_wa_xc_xtensa_pb050_rc_dampen_pareto.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-520A"
    assert data["factorial_design"]["total_grid_points"] == 9
    assert data["factorial_design"]["selected_champion_point"]["full_mtu_1472b_loss_pct"] == 0.0
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage521a_ptmp_32cpe_airtime_fairness_v3() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage521a_ptmp_32cpe_airtime_fairness_and_voip_protect_v3.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-521A"
    assert data["guarida_topology_summary"]["total_panels"] == 3
    assert data["guarida_topology_summary"]["total_cpes"] == 32
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage522a_pbe5ac_lbe5ac_vht40_25mbps_validator() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage522a_pbe5ac_lbe5ac_vht40_25mbps_field_rollout_validator.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-522A"
    assert data["all_targets_rollout_ready"] is True
    assert data["validated_profile"]["validated_goodput_mbps"] == 24.83
    assert data["validated_profile"]["validated_1472b_loss_pct"] == 0.0
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage523a_cross_fleet_champion_v49() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage523a_cross_fleet_champion_v49_and_tester_matrix.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-523A"
    assert data["champion_version"] == "v49.0"
    assert data["evidence_matrix"]["multi_radio_xc_2xc_xm_windows_count"] == 156
    assert data["evidence_matrix"]["wa_windows_count"] >= 200
    assert data["evidence_matrix"]["ltu_windows_count"] == 144
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage524a_multi_radio_v49_suite_gate() -> None:
    p = ROOT / "artifacts" / "verification" / "stage524a_multi_radio_v49_suite_gate_receipt.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-524A"
    assert data["all_stages_passed"] is True
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_p = ROOT / "docs" / "STAGE524A_MULTI_RADIO_V49_SUITE_GATE.md"
    assert doc_p.exists()
    lines = doc_p.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
