"""Pytest suite for Stage 716A LTU Champion v18 (240-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage716a_kit_and_receipt():
    helper = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_v18_240window_field_kit.sh"
    gps_guard = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_gps_1pps_sync_guard.sh"
    dma_guard = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_dma_ring_backpressure_guard.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage716a_ltu_champion_v18_240window_field_rollout_kit.json"
    assert helper.exists()
    assert gps_guard.exists()
    assert dma_guard.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "716A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_ltu_windows"] == 240
    assert data["mean_rtt_ms"] == 0.186
    assert data["safety"]["touched_dev_ame"] is False


def test_stage716a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE716A_LTU_CHAMPION_V18_240WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
