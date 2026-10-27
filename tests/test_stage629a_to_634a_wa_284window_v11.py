"""Stage 634A consolidated verification suite for Stages 629A..634A (70 Rounds = 284 Live Windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage629a_to_634a_all_receipts_and_5pillar_gate() -> None:
    files = [
        "stage629a_live_wa_pb050_v3_and_sgi_guard_r64_66.json",
        "stage630a_live_wa_70round_284window_milestone_r67_70.json",
        "stage631a_live_wa_mk1_251_e2e_v11_milestone.json",
        "stage632a_live_panel1_guarida_84_v11_20h_audit.json",
        "stage633a_cumulative_70round_284window_wa_champion_v11.json",
        "stage634a_live_wa_284window_v11_gate_receipt.json",
    ]
    for fname in files:
        p = ROOT / "artifacts" / "autoresearch" / fname
        assert p.exists(), f"Missing {fname}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        res = audit_stage_receipt_5pillars(data)
        assert res["compliant"] is True, f"5-pillar failure on {fname}: {res['failures']}"


def test_stage633a_284window_ledger_and_scripts() -> None:
    s633 = json.loads(
        (ROOT / "artifacts" / "autoresearch" / "stage633a_cumulative_70round_284window_wa_champion_v11.json").read_text(
            encoding="utf-8"
        )
    )
    assert s633["total_counterbalanced_rounds"] == 70
    assert s633["total_live_wa_triple_play_windows"] == 280
    assert s633["total_live_windows_including_stage162a_e2e"] == 284
    assert s633["milestone_70_rounds_284_windows_achieved"] is True
    assert len(s633["rounds_r1_to_r70_ledger"]) == 70

    champ_sh = (ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion").read_text(
        encoding="utf-8"
    )
    assert "FMX_PB050_V3_RC_PROBE_MS" in champ_sh
    assert "FMX_UDP_RMEM_MIN" in champ_sh
    assert "FMX_SGI_RETRY_GUARD" in champ_sh


def test_stage629a_to_634a_docs_under_220_lines_with_single_doc_head() -> None:
    docs = [
        "STAGE629A_LIVE_WA_PB050_V3_AND_SGI_GUARD_R64_66.md",
        "STAGE630A_LIVE_WA_70ROUND_284WINDOW_MILESTONE_R67_70.md",
        "STAGE631A_LIVE_WA_MK1_251_E2E_V11_MILESTONE.md",
        "STAGE632A_LIVE_PANEL1_GUARIDA_84_V11_20H_AUDIT.md",
        "STAGE633A_CUMULATIVE_70ROUND_284WINDOW_WA_CHAMPION_V11.md",
        "STAGE634A_LIVE_WA_284WINDOW_V11_GATE.md",
    ]
    for dname in docs:
        dp = ROOT / "docs" / dname
        assert dp.exists(), f"Missing doc {dname}"
        text = dp.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{dname} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{dname} must have exactly 1 doc-head"
