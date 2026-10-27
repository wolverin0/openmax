"""Stage 680A consolidated verification suite for Stages 675A..680A (77 Rounds = 312/316 Live Windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage675a_to_680a_all_receipts_and_5pillar_gate() -> None:
    files = [
        "stage675a_live_wa_pb060_and_htt_tx_compl_r71_73.json",
        "stage676a_live_wa_77round_312window_milestone_r74_77.json",
        "stage677a_live_wa_mk1_251_e2e_v12_milestone.json",
        "stage678a_live_panel1_guarida_84_v12_audit.json",
        "stage679a_cumulative_77round_316window_wa_champion_v12.json",
        "stage680a_live_wa_316window_v12_gate_receipt.json",
    ]
    for fname in files:
        p = ROOT / "artifacts" / "autoresearch" / fname
        assert p.exists(), f"Missing {fname}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        res = audit_stage_receipt_5pillars(data)
        assert res["compliant"] is True, f"5-pillar failure on {fname}: {res['failures']}"


def test_stage679a_316window_ledger_and_scripts() -> None:
    s679 = json.loads(
        (ROOT / "artifacts" / "autoresearch" / "stage679a_cumulative_77round_316window_wa_champion_v12.json").read_text(
            encoding="utf-8"
        )
    )
    assert s679["total_counterbalanced_rounds"] == 77
    assert s679["total_live_wa_triple_play_windows"] == 308
    assert s679["total_live_windows_including_stage162a_e2e"] == 312
    assert s679["total_live_windows_including_stage677a_e2e_r8"] == 316
    assert s679["milestone_77_rounds_312_windows_achieved"] is True
    assert s679["milestone_316_windows_with_e2e_achieved"] is True
    assert len(s679["rounds_r1_to_r77_ledger"]) == 77

    champ_sh = (ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion").read_text(
        encoding="utf-8"
    )
    assert "FMX_PB060_TXOP_RETRY_GUARD" in champ_sh
    assert "FMX_HTT_TX_COMPL_GUARD" in champ_sh
    assert "FMX_TXBF_STBC_LDPC_GUARD" in champ_sh


def test_stage675a_to_680a_docs_under_220_lines_with_single_doc_head() -> None:
    docs = [
        "STAGE675A_LIVE_WA_PB060_AND_HTT_TX_COMPL_R71_73.md",
        "STAGE676A_LIVE_WA_77ROUND_312WINDOW_MILESTONE_R74_77.md",
        "STAGE677A_LIVE_WA_MK1_251_E2E_V12_MILESTONE.md",
        "STAGE678A_LIVE_PANEL1_GUARIDA_84_V12_AUDIT.md",
        "STAGE679A_CUMULATIVE_77ROUND_316WINDOW_WA_CHAMPION_V12.md",
        "STAGE680A_LIVE_WA_316WINDOW_V12_GATE.md",
    ]
    for dname in docs:
        dp = ROOT / "docs" / dname
        assert dp.exists(), f"Missing doc {dname}"
        text = dp.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{dname} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{dname} must have exactly 1 doc-head"
