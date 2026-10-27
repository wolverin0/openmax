"""Verification test suite for Stage 167A, Stage 168A, and Stage 169A WA & Panel1-Guarida Megamission."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_167A = ROOT / "artifacts" / "autoresearch" / "stage167a_live_wa_round19_21_autoresearch.json"
R_168A = ROOT / "artifacts" / "autoresearch" / "stage168a_live_panel1_guarida_v2_champion_verification.json"
R_169A = ROOT / "artifacts" / "autoresearch" / "stage169a_cumulative_21round_wa_champion_v3.json"
CHAMP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion"
PTP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-pbe5ac-ptp"
PANEL1_SCRIPT = ROOT / "tools" / "panel1" / "fmx_panel1_champion_persistence.sh"


def test_stage167a_round19_to_21_receipt_and_5pillars() -> None:
    assert R_167A.exists(), f"Missing {R_167A}"
    data = json.loads(R_167A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["cumulative_wa_rf_windows_r1_to_r21"] == 84
    assert data["cumulative_wa_total_windows_including_e2e"] == 88
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    rounds = data["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S167A-R19", "S167A-R20", "S167A-R21"]
    for r in rounds:
        assert len(r["windows"]) == 4
        assert r["decision"] in ("PROMOTE_ARM_B", "RETAIN_ARM_A")
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"


def test_stage168a_panel1_guarida_live_verification_receipt() -> None:
    assert R_168A.exists(), f"Missing {R_168A}"
    data = json.loads(R_168A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    assert data["safety_boundaries"]["hostapd_restarted"] is False
    assert data["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert data["safety_boundaries"]["active_cpes_count"] >= 2
    assert data["after_telemetry"]["sysctls"]["vm.min_free_kbytes"] == "4096"
    assert data["after_telemetry"]["aql_threshold_us"] == 4000
    assert data["after_telemetry"]["memory_mb"]["MemAvailable"] > data["before_telemetry"]["memory_mb"]["MemAvailable"]
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"


def test_stage169a_cumulative_21round_wa_champion_v3_and_scripts() -> None:
    assert R_169A.exists(), f"Missing {R_169A}"
    data = json.loads(R_169A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["total_counterbalanced_rounds"] == 21
    assert data["total_live_wa_triple_play_windows"] == 84
    assert data["total_live_windows_including_stage162a_e2e"] == 88
    assert len(data["rounds_r1_to_r21_ledger"]) == 21
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"

    champ_txt = CHAMP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_VHT40_AQL_BE_LOW" in champ_txt
    assert "FMX_OPTMEM_MAX" in champ_txt

    ptp_txt = PTP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_DISTANCE_M=300" in ptp_txt
    assert "tcp_pacing_ca_ratio=110" in ptp_txt

    panel1_txt = PANEL1_SCRIPT.read_text(encoding="utf-8")
    assert "vm.min_free_kbytes=4096" in panel1_txt
    assert "echo 4000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold" in panel1_txt
