"""Pytest suite for Stage 641A WA Champion v10 (256-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage641a_kit_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_wa_v10_256window_field_kit.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage641a_wa_champion_v10_256window_field_rollout_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "641A"
    assert data["status"] == "CONFIRMED"
    g = data["stage566a_570a_grounding"]
    assert g["cumulative_wa_windows"] == 256
    assert g["loaded_p50_rtt_reduction_pct"] == 81.96
    assert g["e2e_goodput_mbps"] == 69.95


def test_stage641a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE641A_WA_CHAMPION_V10_256WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
