"""Pytest suite for Stage 642A LTU Champion v15 (204-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage642a_kit_and_receipt():
    helper = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_v15_204window_field_kit.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage642a_ltu_champion_v15_204window_field_rollout_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "642A"
    assert data["status"] == "CONFIRMED"
    g = data["stage603a_608a_grounding"]
    assert g["cumulative_ltu_windows"] == 204
    assert len(g["supported_boards"]) == 5
    assert data["safety"]["touched_dev_ame"] is False


def test_stage642a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE642A_LTU_CHAMPION_V15_204WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
