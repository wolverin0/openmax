"""Tests for Stages 179A, 180A, and 181A (Guarida Backhaul Digital Twin, 28-CPE Readiness Matrix & Pre-Flight Gate)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars
from tools.verify.verify_guarida_panel2_panel3_preflight_gate import verify_preflight_gates

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage179a_almafuerte_guarida_0xe3d6_backhaul_digital_twin() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage179a_almafuerte_guarida_0xe3d6_backhaul_digital_twin.json"
    assert p.exists(), "Missing Stage 179A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "179A"
    assert data["production_safety_audit"]["almafuerte_60_writes"] == 0
    assert data["production_safety_audit"]["guarida_61_writes"] == 0

    ep = data["live_backhaul_endpoints"]
    assert ep["ap_almafuerte_60"]["sysid"] == "0xe3d6"
    assert ep["sta_guarida_61"]["sysid"] == "0xe3d6"
    assert ep["ap_almafuerte_60"]["cinr_rx_db"] == 30
    assert ep["sta_guarida_61"]["cinr_rx_db"] == 30

    timing = data["distance_and_slot_timing_model"]
    assert timing["measured_distance_m"] == 3750
    assert timing["recommended_openwrt_distance_m"] == 4050
    assert timing["coverage_class"] == 5
    assert timing["calibrated_slottime_us"] == 22
    assert timing["calibrated_ack_timeout_us"] == 54

    regimes = {r["regime_id"]: r for r in data["simpy_pymoo_pareto_regimes"]}
    assert len(regimes) == 4
    assert regimes["R2_OPENWRT_24_10_4_WA_CHAMPION_V2_VHT20"]["pareto_fmx_loss"] < regimes["R0_STOCK_AIROS8_WA_V8_7_25_VHT20"]["pareto_fmx_loss"]
    assert regimes["R3_OPENWRT_24_10_4_WA_CHAMPION_V2_VHT40"]["tcp_goodput_aggregate_mbps"] > 250.0

    doc = REPO_ROOT / "docs" / "STAGE179A_ALMAFUERTE_GUARIDA_0XE3D6_BACKHAUL_DIGITAL_TWIN.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 179A failed 5-pillar gate: {audit}"


def test_stage180a_guarida_panel2_panel3_28cpe_readiness_matrix() -> None:
    p = REPO_ROOT / "artifacts" / "autoresearch" / "stage180a_guarida_panel2_panel3_28cpe_readiness_matrix.json"
    assert p.exists(), "Missing Stage 180A JSON artifact"
    data = json.loads(p.read_text(encoding="utf-8"))
    assert data["stage"] == "180A"
    assert data["production_safety_audit"]["panel2_82_writes"] == 0
    assert data["production_safety_audit"]["panel3_83_writes"] == 0

    summary = data["summary"]
    assert summary["total_guarida_cpes"] == 32
    assert summary["panel1_cpe_count"] == 4
    assert summary["panel2_cpe_count"] == 22
    assert summary["panel3_cpe_count"] == 6
    assert summary["panel2_and_panel3_total_cpes"] == 28
    assert summary["live_wstalist_online_now_count"] == 10
    assert summary["xm_32mb_cpe_count"] == 1
    assert summary["xw_64mb_cpe_count"] == 1
    assert summary["wa_64mb_cpe_count"] == 26
    assert summary["mode_a_openwrt_eligible_count"] == 27
    assert summary["mode_b_rc_poststart_eligible_count"] == 28

    cpes = data["cpes"]
    assert len(cpes) == 28
    xm_cpes = [c for c in cpes if c["board_family"] == "XM_AR7241_32MB"]
    assert len(xm_cpes) == 1
    assert xm_cpes[0]["mode_a_openwrt_eligible"] is False

    doc = REPO_ROOT / "docs" / "STAGE180A_GUARIDA_PANEL2_PANEL3_28CPE_READINESS_MATRIX.md"
    assert doc.exists()
    lines = doc.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 220
    assert sum(1 for ln in lines if "<!-- doc-head:" in ln) == 1

    audit = audit_stage_receipt_5pillars(data)
    assert audit["compliant"], f"Stage 180A failed 5-pillar gate: {audit}"


def test_stage181a_guarida_panel2_panel3_preflight_gate() -> None:
    receipt = verify_preflight_gates(REPO_ROOT)
    assert receipt["all_gates_passed"] is True, f"Pre-flight gate failures: {receipt['failures']}"
    for gate_id in (
        "SG-01_GUARIDA_BACKBONE_PROTECTION",
        "SG-02_PROTECTED_PARTITIONS_AND_SYSID_0XE8E5_IMAGE",
        "SG-03_EXACT_3PANEL_32CPE_TOPOLOGY",
        "SG-04_KERNEL_6_6_110_MAC80211_TEB_ABI_GATE",
        "SG-05_ZERO_TOUCH_STOCK_INTEROP_AND_WATCHDOG",
    ):
        assert receipt["gates"][gate_id]["passed"] is True

    audit = audit_stage_receipt_5pillars(receipt)
    assert audit["compliant"], f"Stage 181A failed 5-pillar gate: {audit}"
