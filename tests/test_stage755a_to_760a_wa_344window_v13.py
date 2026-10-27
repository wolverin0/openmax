"""Stage 760A consolidated verification suite for Stages 755A..760A (84 Rounds = 340/344/368 Live Windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage755a_to_760a_all_receipts_and_5pillar_gate() -> None:
    files = [
        "stage755a_live_wa_spectral_phyerr_and_vdev_guard_r78_80.json",
        "stage756a_live_wa_84round_344window_milestone_r81_84.json",
        "stage757a_live_wa_mk1_251_e2e_v13_milestone.json",
        "stage758a_live_panel1_guarida_84_v13_audit.json",
        "stage759a_cumulative_84round_344window_wa_champion_v13.json",
        "stage760a_live_wa_344window_v13_gate_receipt.json",
    ]
    for fname in files:
        p = ROOT / "artifacts" / "autoresearch" / fname
        assert p.exists(), f"Missing {fname}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        res = audit_stage_receipt_5pillars(data)
        assert res["compliant"] is True, f"5-pillar failure on {fname}: {res['failures']}"


def test_stage759a_344window_ledger_and_scripts() -> None:
    s759 = json.loads(
        (ROOT / "artifacts" / "autoresearch" / "stage759a_cumulative_84round_344window_wa_champion_v13.json").read_text(
            encoding="utf-8"
        )
    )
    assert s759["total_counterbalanced_rounds"] == 84
    assert s759["total_live_wa_triple_play_windows"] == 336
    assert s759["total_live_windows_including_stage162a_e2e"] == 340
    assert s759["total_live_windows_including_stage757a_e2e_r9"] == 344
    assert s759["milestone_84_rounds_344_windows_achieved"] is True
    assert len(s759["rounds_r1_to_r84_ledger"]) == 84

    champ_sh = (ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion").read_text(
        encoding="utf-8"
    )
    assert "FMX_SPECTRAL_RADAR_PHYERR_GUARD" in champ_sh
    assert "FMX_WMI_VDEV_START_GUARD" in champ_sh


def test_stage755a_to_760a_docs_under_220_lines_with_single_doc_head() -> None:
    docs = [
        "STAGE755A_LIVE_WA_SPECTRAL_PHYERR_AND_VDEV_GUARD_R78_80.md",
        "STAGE756A_LIVE_WA_84ROUND_344WINDOW_MILESTONE_R81_84.md",
        "STAGE757A_LIVE_WA_MK1_251_E2E_V13_MILESTONE.md",
        "STAGE758A_LIVE_PANEL1_GUARIDA_84_V13_AUDIT.md",
        "STAGE759A_CUMULATIVE_84ROUND_344WINDOW_WA_CHAMPION_V13.md",
        "STAGE760A_LIVE_WA_344WINDOW_V13_GATE.md",
    ]
    for dname in docs:
        dp = ROOT / "docs" / dname
        assert dp.exists(), f"Missing doc {dname}"
        text = dp.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{dname} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{dname} must have exactly 1 doc-head"
