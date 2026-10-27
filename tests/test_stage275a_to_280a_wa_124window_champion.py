"""Verification test suite for Stage 275A -> Stage 280A 6-Stage WA 124-Window Megamission."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_275A = ROOT / "artifacts" / "autoresearch" / "stage275a_live_wa_vht80_and_gro_batch_r25_27.json"
R_276A = ROOT / "artifacts" / "autoresearch" / "stage276a_live_wa_wmm_dscp_tid_isolation_r28_30.json"
R_277A = ROOT / "artifacts" / "autoresearch" / "stage277a_live_wa_nftables_dscp_classifier.json"
R_278A = ROOT / "artifacts" / "autoresearch" / "stage278a_live_panel1_guarida_18h_soak_scorecard.json"
R_279A = ROOT / "artifacts" / "autoresearch" / "stage279a_cumulative_30round_124window_wa_champion_v5.json"
CHAMP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion"
WMM_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wmm-dscp-qos"
PTP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-pbe5ac-ptp"


def test_stage275a_vht80_and_gro_batch_r25_to_r27_receipt() -> None:
    assert R_275A.exists(), f"Missing {R_275A}"
    data = json.loads(R_275A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["cumulative_wa_rf_windows_r1_to_r27"] == 108
    assert data["cumulative_wa_total_windows_including_e2e"] == 112
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    rounds = data["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S275A-R25", "S275A-R26", "S275A-R27"]
    for r in rounds:
        assert len(r["windows"]) == 4
        assert r["decision"] in ("PROMOTE_ARM_B", "RETAIN_ARM_A")
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"


def test_stage276a_and_277a_wmm_dscp_tid_isolation_and_nftables_classifier() -> None:
    assert R_276A.exists(), f"Missing {R_276A}"
    assert R_277A.exists(), f"Missing {R_277A}"
    assert WMM_SCRIPT.exists(), f"Missing {WMM_SCRIPT}"

    d276 = json.loads(R_276A.read_text(encoding="utf-8"))
    assert d276["status"] == "CONFIRMED"
    assert d276["cumulative_wa_rf_windows_r1_to_r30"] == 120
    assert d276["cumulative_wa_total_windows_including_e2e"] == 124
    rounds = d276["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S276A-R28", "S276A-R29", "S276A-R30"]
    assert audit_stage_receipt_5pillars(d276)["compliant"] is True

    d277 = json.loads(R_277A.read_text(encoding="utf-8"))
    assert d277["status"] == "CONFIRMED"
    assert d277["nftables_table"] == "inet fmx_wmm_qos"
    assert audit_stage_receipt_5pillars(d277)["compliant"] is True

    wmm_txt = WMM_SCRIPT.read_text(encoding="utf-8")
    assert "table inet fmx_wmm_qos" in wmm_txt
    assert "ip dscp set ef" in wmm_txt
    assert "ip dscp set af41" in wmm_txt


def test_stage278a_and_279a_panel1_18h_soak_and_30round_124window_champion_v5() -> None:
    assert R_278A.exists(), f"Missing {R_278A}"
    assert R_279A.exists(), f"Missing {R_279A}"

    d278 = json.loads(R_278A.read_text(encoding="utf-8"))
    assert d278["status"] == "CONFIRMED"
    assert d278["safety_boundaries"]["touched_241_or_242"] is False
    assert d278["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert d278["safety_boundaries"]["active_cpes_count"] == 3
    assert d278["uptime_hours"] >= 17.5
    assert d278["memory_mb"]["MemAvailable"] >= 8.0
    assert audit_stage_receipt_5pillars(d278)["compliant"] is True

    d279 = json.loads(R_279A.read_text(encoding="utf-8"))
    assert d279["status"] == "CONFIRMED"
    assert d279["total_counterbalanced_rounds"] == 30
    assert d279["total_live_wa_triple_play_windows"] == 120
    assert d279["total_live_windows_including_stage162a_e2e"] == 124
    assert d279["milestone_30_rounds_124_windows_achieved"] is True
    assert len(d279["rounds_r1_to_r30_ledger"]) == 30
    assert audit_stage_receipt_5pillars(d279)["compliant"] is True

    champ_txt = CHAMP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_VHT80_AQL_BE_LOW" in champ_txt
    assert "FMX_GRO_NORMAL_BATCH" in champ_txt
    assert "FMX_ENABLE_WMM_DSCP_QOS" in champ_txt

    ptp_txt = PTP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_GRO_NORMAL_BATCH" in ptp_txt
