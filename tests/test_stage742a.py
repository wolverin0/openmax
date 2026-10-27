"""Pytest suite for Stage 742A LTU Champion v19 (252-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage742a_kit_and_receipt():
    helper = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_v19_252window_field_kit.sh"
    thermal_guard = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_thermal_pa_bias_guard.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage742a_ltu_champion_v19_252window_field_rollout_kit.json"
    assert helper.exists()
    assert thermal_guard.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "742A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_ltu_windows"] == 252
    assert data["mean_rtt_ms"] == 0.184
    assert data["safety"]["touched_dev_ame"] is False


def test_stage742a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE742A_LTU_CHAMPION_V19_252WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
