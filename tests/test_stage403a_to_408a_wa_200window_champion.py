"""Stage 408A consolidated verification suite for Stages 403A..408A (49 Rounds = 200 Live Windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage403a_to_407a_all_receipts_and_5pillar_gate() -> None:
    files = [
        "stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json",
        "stage404a_live_wa_200window_milestone_r46_49.json",
        "stage405a_live_wa_mk1_251_4class_diffserv_e2e_v8.json",
        "stage406a_live_panel1_guarida_v8_gamboa_audit.json",
        "stage407a_cumulative_49round_200window_wa_champion_v8.json",
    ]
    for fname in files:
        p = ROOT / "artifacts" / "autoresearch" / fname
        assert p.exists(), f"Missing {fname}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        res = audit_stage_receipt_5pillars(data)
        assert res["compliant"] is True, f"5-pillar failure on {fname}: {res['failures']}"


def test_stage407a_200window_ledger_and_scripts() -> None:
    s407 = json.loads(
        (ROOT / "artifacts" / "autoresearch" / "stage407a_cumulative_49round_200window_wa_champion_v8.json").read_text(
            encoding="utf-8"
        )
    )
    assert s407["total_counterbalanced_rounds"] == 49
    assert s407["total_live_wa_triple_play_windows"] == 196
    assert s407["total_live_windows_including_stage162a_e2e"] == 200
    assert s407["milestone_49_rounds_200_windows_achieved"] is True
    assert len(s407["rounds_r1_to_r49_ledger"]) == 49

    champ_sh = (ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion").read_text(
        encoding="utf-8"
    )
    assert "FMX_TCP_COMP_SACK_DELAY_NS" in champ_sh
    assert "FMX_NF_CAL_PERIOD" in champ_sh
    assert "FMX_PKTLOG_FILTER" in champ_sh

    panel1_sh = (ROOT / "tools" / "panel1" / "fmx_panel1_champion_persistence.sh").read_text(encoding="utf-8")
    assert "tcp_comp_sack_delay_ns" in panel1_sh
    assert "nf_cal_period" in panel1_sh
    assert "pktlog_filter" in panel1_sh


def test_stage403a_to_407a_docs_under_220_lines_with_single_doc_head() -> None:
    docs = [
        "STAGE403A_LIVE_WA_PB040_RAM_CANARY_AND_NFCAL_R43_45.md",
        "STAGE404A_LIVE_WA_200WINDOW_MILESTONE_R46_49.md",
        "STAGE405A_LIVE_WA_MK1_251_4CLASS_DIFFSERV_E2E_V8.md",
        "STAGE406A_LIVE_PANEL1_GUARIDA_V8_GAMBOA_AUDIT.md",
        "STAGE407A_CUMULATIVE_49ROUND_200WINDOW_WA_CHAMPION_V8.md",
    ]
    for dname in docs:
        dp = ROOT / "docs" / dname
        assert dp.exists(), f"Missing doc {dname}"
        text = dp.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{dname} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{dname} must have exactly 1 doc-head"
