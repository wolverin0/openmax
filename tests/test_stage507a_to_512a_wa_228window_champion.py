"""Stage 512A consolidated verification suite for Stages 507A..512A (56 Rounds = 228 Live Windows)."""
from __future__ import annotations

import json
from pathlib import Path
from tools.verify.enforce_5pillar_research_gate import audit_stage_receipt_5pillars

ROOT = Path(__file__).resolve().parents[1]


def test_stage507a_to_511a_all_receipts_and_5pillar_gate() -> None:
    files = [
        "stage507a_live_wa_pb050_rc_probe_dampen_and_slot_r50_52.json",
        "stage508a_live_wa_cca_agc_and_ani_immunity_r53_56.json",
        "stage509a_live_wa_mk1_251_e2e_v9_stress.json",
        "stage510a_live_panel1_guarida_v9_and_3cpe_evm_audit.json",
        "stage511a_cumulative_56round_228window_wa_champion_v9.json",
    ]
    for fname in files:
        p = ROOT / "artifacts" / "autoresearch" / fname
        assert p.exists(), f"Missing {fname}"
        data = json.loads(p.read_text(encoding="utf-8"))
        assert data["status"] == "CONFIRMED"
        assert data["safety_boundaries"]["touched_241_or_242"] is False
        res = audit_stage_receipt_5pillars(data)
        assert res["compliant"] is True, f"5-pillar failure on {fname}: {res['failures']}"


def test_stage511a_228window_ledger_and_scripts() -> None:
    s511 = json.loads(
        (ROOT / "artifacts" / "autoresearch" / "stage511a_cumulative_56round_228window_wa_champion_v9.json").read_text(
            encoding="utf-8"
        )
    )
    assert s511["total_counterbalanced_rounds"] == 56
    assert s511["total_live_wa_triple_play_windows"] == 224
    assert s511["total_live_windows_including_stage162a_e2e"] == 228
    assert s511["milestone_56_rounds_228_windows_achieved"] is True
    assert len(s511["rounds_r1_to_r56_ledger"]) == 56

    champ_sh = (ROOT / "firmware" / "openwrt" / "pbe5ac_gen2_ptp_kit" / "99-fmx-wa-universal-champion").read_text(
        encoding="utf-8"
    )
    assert "FMX_PB050_RC_PROBE_MS" in champ_sh
    assert "FMX_CCA_AGC_DAEMON" in champ_sh
    assert "FMX_BMISS_CSA_HELPER" in champ_sh

    panel1_sh = (ROOT / "tools" / "panel1" / "fmx_panel1_champion_persistence.sh").read_text(encoding="utf-8")
    assert "ani_enable" in panel1_sh


def test_stage507a_to_511a_docs_under_220_lines_with_single_doc_head() -> None:
    docs = [
        "STAGE507A_LIVE_WA_PB050_RC_PROBE_DAMPEN_AND_SLOT_R50_52.md",
        "STAGE508A_LIVE_WA_CCA_AGC_AND_ANI_IMMUNITY_R53_56.md",
        "STAGE509A_LIVE_WA_MK1_251_E2E_V9_STRESS.md",
        "STAGE510A_LIVE_PANEL1_GUARIDA_V9_AND_3CPE_EVM_AUDIT.md",
        "STAGE511A_CUMULATIVE_56ROUND_228WINDOW_WA_CHAMPION_V9.md",
    ]
    for dname in docs:
        dp = ROOT / "docs" / dname
        assert dp.exists(), f"Missing doc {dname}"
        text = dp.read_text(encoding="utf-8")
        lines = text.splitlines()
        assert len(lines) < 220, f"{dname} exceeds 220 lines ({len(lines)})"
        assert text.count("<!-- doc-head:") == 1, f"{dname} must have exactly 1 doc-head"
