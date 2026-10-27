"""Pytest suite for Stage 618A AF-LTU ToF Ranging & Timing Advance Helper."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage618a_helper_and_receipt():
    helper = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_tof_timing_advance_helper.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage618a_ltu_tof_ranging_and_timing_advance_helper.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "618A"
    assert data["status"] == "CONFIRMED"
    assert data["stage616a_re_grounding"]["multipath_reflection_jump_alert_m"] == 7.5
    assert data["safety"]["touched_dev_ame"] is False


def test_stage618a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE618A_LTU_TOF_RANGING_AND_TIMING_ADVANCE_HELPER.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
