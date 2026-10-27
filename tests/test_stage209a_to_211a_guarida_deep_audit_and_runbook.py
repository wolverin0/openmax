"""Tests for Stages 209A, 210A, and 211A (Guarida Deep TDMA/ATHSTATS Audit & Zero-Downtime Staged Runbook)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage209a_almafuerte_guarida_tdma_and_ackdistance_audit() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage209a_almafuerte_guarida_tdma_and_ackdistance_audit.json"
    assert p.exists(), "Missing Stage 209A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "209A"
    assert data["production_safety_audit"]["almafuerte_60_writes"] == 0
    assert data["production_safety_audit"]["guarida_61_writes"] == 0

    ep = data["endpoints_deep_audit"]
    assert ep["almafuerte_60_ap"]["rc_poststart_present"] is False
    assert ep["guarida_61_sta"]["rc_poststart_present"] is False
    assert ep["almafuerte_60_ap"]["ackdistance_cfg_m"] == 600
    assert ep["guarida_61_sta"]["ackdistance_cfg_m"] == 600
    assert ep["almafuerte_60_ap"]["polling_11ac_11n_compat"] == 0
    assert ep["guarida_61_sta"]["polling_11ac_11n_compat"] == 1
    assert ep["guarida_61_sta"]["irq33_ath_spectral_filter_count"] > 1000000000

    loss = data["tdma_and_ackdistance_loss_quantification"]
    assert loss["physical_link_distance_m"] == 3750
    assert loss["required_acktimeout_us_for_3750m"] == 54
    assert loss["estimated_tdma_airtime_loss_pct"] > 10.0

    doc = REPO_ROOT / "docs" / "STAGE209A_ALMAFUERTE_GUARIDA_TDMA_AND_ACKDISTANCE_AUDIT.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 209A failed 5-pillar gate: {audit}"


def test_stage210a_panel2_panel3_live_telemetry_and_contention_audit() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage210a_panel2_panel3_live_telemetry_and_contention_audit.json"
    assert p.exists(), "Missing Stage 210A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "210A"
    assert data["production_safety_audit"]["panel2_82_writes"] == 0
    assert data["production_safety_audit"]["panel3_83_writes"] == 0

    sec = data["sectors_deep_telemetry"]
    assert sec["Panel2_Guarida_82"]["polling"] == "enabled"
    assert sec["Panel3_Guarida_83"]["polling"] == "disabled"
    assert sec["Panel2_Guarida_82"]["qdisc_ath0_dropped"] == 168857
    assert sec["Panel3_Guarida_83"]["qdisc_ath0_dropped"] == 41402
    assert sec["Panel3_Guarida_83"]["irq33_ath_spectral_filter_count"] == 2142307805

    doc = REPO_ROOT / "docs" / "STAGE210A_PANEL2_PANEL3_LIVE_TELEMETRY_AND_CONTENTION_AUDIT.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 210A failed 5-pillar gate: {audit}"


def test_stage211a_guarida_tower_zero_downtime_runbook() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage211a_guarida_tower_zero_downtime_runbook.json"
    assert p.exists(), "Missing Stage 211A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "211A"
    assert data["operator_gate_required"] is True
    assert data["production_safety_audit"]["writes_performed"] == 0

    phases = {ph["phase_id"]: ph for ph in data["staged_execution_phases"]}
    assert len(phases) == 3
    assert phases["STAGE_0_ZERO_FLASH_MODE_B_AND_SPECTRAL_CLEANUP"]["requires_flash"] is False
    assert phases["STAGE_1_ZERO_TOUCH_AP_SIDE_OPENWRT_MIGRATION_PANEL3_AND_PANEL2"]["teb_module_sha256"] == (
        "3e3d812ff0d4a2fd1a1f9c1257a9356058ac439108e3c27ef6b11d944b696868"
    )
    assert phases["STAGE_2_STAGED_OTA_HYBRID_TO_FULL_OPENWRT_BACKHAUL_60_61"]["board_sysid"] == "0xe3d6"

    doc = REPO_ROOT / "docs" / "STAGE211A_GUARIDA_TOWER_ZERO_DOWNTIME_RUNBOOK.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 211A failed 5-pillar gate: {audit}"
