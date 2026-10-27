"""Tests for Stage 479A: Guarida Panel2 (.82) & Panel3 (.83) Coexistence Champion v3 Safe Kit."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
KIT_PATH = REPO_ROOT / "firmware" / "guarida_safe_kits" / "rc.poststart_panel2_panel3_coexistence_v3.sh"
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage479a_guarida_panel2_panel3_coexistence_champion_kit.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE479A_GUARIDA_PANEL2_PANEL3_COEXISTENCE_CHAMPION_KIT.md"


def test_stage479a_kit_script_lf_and_knobs():
    assert KIT_PATH.exists()
    raw = KIT_PATH.read_bytes()
    assert b"\r\n" not in raw
    text = raw.decode("utf-8")
    assert "cbp_dur" in text
    assert "900" in text
    assert "6672" in text
    assert "rollback" in text


def test_stage479a_receipt_integrates_417a_418a_420a():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "479A"
    ev = data["integrated_re_and_pareto_evidence"]
    assert ev["stage417a_cbp_dur_and_deferred_list_re"]["panel2_champion_cbp_dur_us"] == 900
    assert ev["stage418a_panel3_local_enqued_mcs2_storm_re"]["tx_mcs2_to_local_enqued_ratio_pct"] == 99.2
    assert ev["stage420a_deltas_vs_baseline"]["joint_goodput_gain_mbps"] == 46.36
    assert "five_pillar_compliance" in data


def test_stage479a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
