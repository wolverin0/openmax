from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage551a_168window_multi_radio_milestone() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage551a_168window_multi_radio_milestone_r105_r110.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-551A"
    assert data["cumulative_multi_radio_windows"] == 168
    assert data["new_windows_in_stage551a"] == 12
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage552a_guarida_60_61_10mhz_shift_validator() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage552a_guarida_60_61_10mhz_shift_and_evm_recovery_validator.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-552A"
    assert data["backbone_link_validation"]["chain0_evm_improvement_db"] == 7.99
    assert data["backbone_link_validation"]["goodput_gain_mbps"] == 17.17
    assert data["safety_boundaries"]["sg01_ether2_sw_poe200_untouched"] is True
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage553a_ltu_super4096_and_dpd_evm_pareto() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage553a_ltu_super4096_and_dpd_evm_pareto.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-553A"
    assert data["selected_champion"]["bbp_rf_set_super4096"] == 1
    assert data["selected_champion"]["ame_bbp_set_dpd"] == 2
    assert data["selected_champion"]["qam4096_12x_residence_pct"] > 90.0
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage554a_wa_xc_pb040_pb050_combined_ram_patch() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage554a_wa_xc_pb040_pb050_combined_ram_patch_validator.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-554A"
    assert data["combined_patch_validation"]["segments_disjoint"] is True
    assert data["combined_patch_validation"]["combined_patch_safe"] is True
    assert data["safety_boundaries"]["flash_writes_count"] == 0
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage555a_cross_fleet_champion_v50_golden_milestone() -> None:
    p = ROOT / "artifacts" / "autoresearch" / "stage555a_cross_fleet_champion_v50_golden_milestone.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-555A"
    assert data["champion_version"] == "v50.0"
    assert data["golden_milestone_summary"]["radio_families_covered"] == 8
    assert data["golden_milestone_summary"]["cumulative_multi_radio_windows"] == 168
    assert audit_stage_receipt_5pillars(data)["compliant"] is True


def test_stage556a_multi_radio_v50_golden_gate() -> None:
    p = ROOT / "artifacts" / "verification" / "stage556a_multi_radio_v50_golden_gate_receipt.json"
    assert p.exists()
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-556A"
    assert data["all_stages_passed"] is True
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    doc_p = ROOT / "docs" / "STAGE556A_MULTI_RADIO_V50_GOLDEN_GATE.md"
    assert doc_p.exists()
    lines = doc_p.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1
