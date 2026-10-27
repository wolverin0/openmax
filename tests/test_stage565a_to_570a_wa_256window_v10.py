"""Stage 570A consolidated verification suite for Stages 565A..570A (63 Rounds = 256 Live Windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage565a_to_570a_all_receipts_and_5pillar_gate() -> None:
    files = [
        "stage565a_live_wa_pb050_v2_and_pacing_r57_59.json",
        "stage566a_live_wa_256window_milestone_r60_63.json",
        "stage567a_live_wa_mk1_251_e2e_v10_milestone.json",
        "stage568a_live_panel1_guarida_84_v10_rollout_audit.json",
        "stage569a_cumulative_63round_256window_wa_champion_v10.json",
        "stage570a_live_wa_256window_v10_gate_receipt.json",
    ]
    for fname in files:
        p = ROOT / "artifacts" / "autoresearch" / fname
        assert p.exists(), f"Missing {fname}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        res = audit_stage_receipt_5pillars(data)
        assert res["compliant"] is True, f"5-pillar failure on {fname}: {res['failures']}"


def test_stage569a_256window_ledger_and_scripts() -> None:
    s569 = json.loads(
        (ROOT / "artifacts" / "autoresearch" / "stage569a_cumulative_63round_256window_wa_champion_v10.json").read_text(
            encoding="utf-8"
        )
    )
    assert s569["total_counterbalanced_rounds"] == 63
    assert s569["total_live_wa_triple_play_windows"] == 252
    assert s569["total_live_windows_including_stage162a_e2e"] == 256
    assert s569["milestone_63_rounds_256_windows_achieved"] is True
    assert len(s569["rounds_r1_to_r63_ledger"]) == 63

    champ_sh = (ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion").read_text(
        encoding="utf-8"
    )
    assert "FMX_PB050_RC_PROBE_MS" in champ_sh
    assert "FMX_CCA_AGC_DAEMON" in champ_sh
    assert "FMX_BMISS_CSA_HELPER" in champ_sh


def test_stage565a_to_570a_docs_under_220_lines_with_single_doc_head() -> None:
    docs = [
        "STAGE565A_LIVE_WA_PB050_V2_AND_PACING_R57_59.md",
        "STAGE566A_LIVE_WA_256WINDOW_MILESTONE_R60_63.md",
        "STAGE567A_LIVE_WA_MK1_251_E2E_V10_MILESTONE.md",
        "STAGE568A_LIVE_PANEL1_GUARIDA_84_V10_ROLLOUT_AUDIT.md",
        "STAGE569A_CUMULATIVE_63ROUND_256WINDOW_WA_CHAMPION_V10.md",
        "STAGE570A_LIVE_WA_256WINDOW_V10_GATE.md",
    ]
    for dname in docs:
        dp = ROOT / "docs" / dname
        assert dp.exists(), f"Missing doc {dname}"
        text = dp.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{dname} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{dname} must have exactly 1 doc-head"
