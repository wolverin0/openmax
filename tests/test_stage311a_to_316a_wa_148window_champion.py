"""Verification test suite for Stage 311A -> Stage 316A 6-Stage WA 148-Window Megamission."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_311A = ROOT / "artifacts" / "autoresearch" / "stage311a_live_wa_asymmetric_dl_ul_and_tcp_burst_r31_33.json"
R_312A = ROOT / "artifacts" / "autoresearch" / "stage312a_live_wa_iptv_multicast_and_gaming_r34_36.json"
R_313A = ROOT / "artifacts" / "autoresearch" / "stage313a_live_wa_mk1_251_e2e_v6_benchmark.json"
R_314A = ROOT / "artifacts" / "autoresearch" / "stage314a_live_panel1_guarida_v6_rollout.json"
R_315A = ROOT / "artifacts" / "autoresearch" / "stage315a_cumulative_36round_148window_wa_champion_v6.json"
CHAMP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion"
PTP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-pbe5ac-ptp"
PANEL1_SCRIPT = ROOT / "tools" / "panel1" / "fmx_panel1_champion_persistence.sh"


def test_stage311a_asymmetric_dl_ul_and_tcp_burst_r31_to_r33_receipt() -> None:
    assert R_311A.exists(), f"Missing {R_311A}"
    data = json.loads(R_311A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["protocol"] == "A1 -> B1 -> A2 -> B2"
    assert data["cumulative_wa_rf_windows_r1_to_r33"] == 132
    assert data["cumulative_wa_total_windows_including_e2e"] == 136
    assert data["safety_boundaries"]["touched_241_or_242"] is False
    rounds = data["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S311A-R31", "S311A-R32", "S311A-R33"]
    for r in rounds:
        assert len(r["windows"]) == 4
        assert r["decision"] in ("PROMOTE_ARM_B", "RETAIN_ARM_A")
    gate = audit_stage_receipt_5pillars(data)
    assert gate["compliant"] is True, f"5-pillar failure: {gate}"


def test_stage312a_and_313a_iptv_multicast_gaming_and_mk1_251_e2e() -> None:
    assert R_312A.exists(), f"Missing {R_312A}"
    assert R_313A.exists(), f"Missing {R_313A}"

    d312 = json.loads(R_312A.read_text(encoding="utf-8"))
    assert d312["status"] == "CONFIRMED"
    assert d312["cumulative_wa_rf_windows_r1_to_r36"] == 144
    assert d312["cumulative_wa_total_windows_including_e2e"] == 148
    assert d312["milestone_148_live_windows_achieved"] is True
    rounds = d312["rounds"]
    assert len(rounds) == 3
    assert [r["round_id"] for r in rounds] == ["S312A-R34", "S312A-R35", "S312A-R36"]
    assert audit_stage_receipt_5pillars(d312)["compliant"] is True

    d313 = json.loads(R_313A.read_text(encoding="utf-8"))
    assert d313["status"] == "CONFIRMED"
    assert d313["safety_boundaries"]["touched_241_or_242"] is False
    e2e = d313["e2e_round"]
    assert e2e["round_id"] == "S313A-E2E-R2"
    assert len(e2e["windows"]) == 4
    for w in e2e["windows"]:
        assert "boca7_mk1_251_e2e_rtt" in w
        assert w["boca7_mk1_251_e2e_rtt"]["p50_ms"] > 0.0
    assert audit_stage_receipt_5pillars(d313)["compliant"] is True


def test_stage314a_and_315a_panel1_v6_rollout_and_36round_148window_champion() -> None:
    assert R_314A.exists(), f"Missing {R_314A}"
    assert R_315A.exists(), f"Missing {R_315A}"

    d314 = json.loads(R_314A.read_text(encoding="utf-8"))
    assert d314["status"] == "CONFIRMED"
    assert d314["safety_boundaries"]["touched_241_or_242"] is False
    assert d314["safety_boundaries"]["hostapd_restarted"] is False
    assert d314["safety_boundaries"]["zero_rf_disconnect_verified"] is True
    assert d314["safety_boundaries"]["active_cpes_count"] == 3
    v6_k = d314["v6_verified_knobs"]
    assert v6_k["net.core.gro_normal_batch"] == 16
    assert v6_k["fq_limit"] == 512
    assert v6_k["net.ipv4.tcp_early_retrans"] == 4
    assert v6_k["net.ipv4.tcp_slow_start_after_idle"] == 0
    assert audit_stage_receipt_5pillars(d314)["compliant"] is True

    d315 = json.loads(R_315A.read_text(encoding="utf-8"))
    assert d315["status"] == "CONFIRMED"
    assert d315["total_counterbalanced_rounds"] == 36
    assert d315["total_live_wa_triple_play_windows"] == 144
    assert d315["total_live_windows_including_stage162a_e2e"] == 148
    assert d315["milestone_36_rounds_148_windows_achieved"] is True
    assert len(d315["rounds_r1_to_r36_ledger"]) == 36
    assert audit_stage_receipt_5pillars(d315)["compliant"] is True

    champ_txt = CHAMP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_TCP_SLOW_START_AFTER_IDLE" in champ_txt
    assert "FMX_MULTICAST_TO_UNICAST" in champ_txt
    assert "FMX_DTIM_PERIOD" in champ_txt

    ptp_txt = PTP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_TCP_SLOW_START_AFTER_IDLE=0" in ptp_txt
    assert "FMX_MULTICAST_TO_UNICAST=1" in ptp_txt

    panel1_txt = PANEL1_SCRIPT.read_text(encoding="utf-8")
    assert "net.core.gro_normal_batch=16" in panel1_txt
    assert "fq_limit 512" in panel1_txt
    assert "net.ipv4.tcp_early_retrans=4" in panel1_txt
