"""Pytest suite for Stage 592A LTU LBT Interference Mitigation & Auto-Frequency Helper."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage592a_helper_and_receipt():
    helper = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_lbt_auto_freq_helper.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage592a_ltu_lbt_interference_and_auto_freq_helper.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "592A"
    assert data["status"] == "CONFIRMED"
    assert len(data["supported_boards"]) == 5
    assert data["safety"]["touched_dev_ame"] is False
    assert data["safety"]["zero_dev_ame_ioctls"] is True


def test_stage592a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE592A_LTU_LBT_INTERFERENCE_AND_AUTO_FREQ_HELPER.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
