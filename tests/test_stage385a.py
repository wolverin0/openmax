"""Verification test for Stage 385A (Cumulative 42-Round 172-Window Universal WA Champion v7)."""

from __future__ import annotations

import json
from pathlib import Path

from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]
R_385A = ROOT / "artifacts" / "autoresearch" / "stage385a_cumulative_42round_172window_wa_champion_v7.json"
CHAMP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion"
PTP_SCRIPT = ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-pbe5ac-ptp"
PANEL1_SCRIPT = ROOT / "tools" / "panel1" / "fmx_panel1_champion_persistence.sh"


def test_stage385a_cumulative_42round_172window_wa_champion_v7() -> None:
    assert R_385A.exists(), f"Missing {R_385A}"
    data = json.loads(R_385A.read_text(encoding="utf-8"))
    assert data["status"] == "CONFIRMED"
    assert data["total_counterbalanced_rounds"] == 42
    assert data["total_live_wa_triple_play_windows"] == 168
    assert data["total_live_windows_including_stage162a_e2e"] == 172
    assert data["milestone_42_rounds_172_windows_achieved"] is True
    assert len(data["rounds_r1_to_r42_ledger"]) == 42
    assert audit_stage_receipt_5pillars(data)["compliant"] is True

    champ_txt = CHAMP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_TCP_AUTOCORKING" in champ_txt
    assert "FMX_HTT_MAX_AMSDU_AMPDU" in champ_txt
    assert "FMX_CHAIN_IMBALANCE_RESCUE" in champ_txt

    ptp_txt = PTP_SCRIPT.read_text(encoding="utf-8")
    assert "FMX_TCP_AUTOCORKING=0" in ptp_txt

    panel1_txt = PANEL1_SCRIPT.read_text(encoding="utf-8")
    assert "net.ipv4.tcp_autocorking=0" in panel1_txt
    assert "htt_max_amsdu_ampdu" in panel1_txt
