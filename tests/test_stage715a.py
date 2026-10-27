"""Pytest suite for Stage 715A WA Champion v12 (316-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage715a_kit_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_wa_v12_316window_field_kit.sh"
    htt_guard = ROOT / "firmware" / "openwrt" / "common" / "fmx_qca_htt_tx_compl_guard.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage715a_wa_champion_v12_316window_field_rollout_kit.json"
    assert helper.exists()
    assert htt_guard.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "715A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_wa_windows"] == 316
    assert data["features"]["dynamic_phy_resolution"] is True


def test_stage715a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE715A_WA_CHAMPION_V12_316WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
