"""Verification test suite for Stage 212A, Stage 213A, and Stage 214A WA 100-Window Champion v4 & Panel1-Guarida 3-CPE QoS Audit."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_212A = ROOT / "artifacts" / "autoresearch" / "stage212a_live_wa_round22_24_100window_milestone.json"
R_213A = ROOT / "artifacts" / "autoresearch" / "stage213a_live_panel1_guarida_3cpe_qos_audit.json"
R_214A = ROOT / "artifacts" / "autoresearch" / "stage214a_cumulative_24round_100window_wa_champion_v4.json"
CHAMP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion"
PTP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-pbe5ac-ptp"


def test_stage212a_round22_to_24_100window_milestone_receipt() -> None:
    assert R_212A.exists(), f"Missing {R_212A}"
    data = json.loads(R_212A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["cumulative_wa_rf_windows_r1_to_r24"] == 96
    assert data["cumulative_wa_total_windows_including_e2e"] == 100
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    rounds = data["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S212A-R22", "S212A-R23", "S212A-R24"]
    for r in rounds:
        assert len(r["windows"]) == 4
        assert r["decision"] in ("PROMOTE_ARM_B", "RETAIN_ARM_A")
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"


def test_stage213a_panel1_guarida_3cpe_qos_audit_receipt() -> None:
    assert R_213A.exists(), f"Missing {R_213A}"
    data = json.loads(R_213A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["hostapd_restarted"] is False
    assert data["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert data["safety_boundaries"]["active_cpes_count"] == 3
    audits = data["cpe_qos_audits"]
    assert len(audits) == 3
    for a in audits:
        assert a["rtt_samples"] >= 50
        assert a["p50_rtt_ms"] > 0.0
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"


def test_stage214a_cumulative_24round_100window_wa_champion_v4() -> None:
    assert R_214A.exists(), f"Missing {R_214A}"
    data = json.loads(R_214A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["total_counterbalanced_rounds"] == 24
    assert data["total_live_wa_triple_play_windows"] == 96
    assert data["total_live_windows_including_stage162a_e2e"] == 100
    assert data["milestone_100_live_windows_achieved"] is True
    assert len(data["rounds_r1_to_r24_ledger"]) == 24
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"

    champ_txt = CHAMP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_TCP_EARLY_RETRANS" in champ_txt
    assert "FMX_TCP_RECOVERY" in champ_txt

    ptp_txt = PTP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_TCP_EARLY_RETRANS" in ptp_txt
