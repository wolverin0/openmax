"""Pytest suite for Stage 703A Executive Plain-Language Summary & 4-Step Rollout Matrix."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage703a_summary_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage703a_executive_human_summary_and_rollout_matrix.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "703A"
    assert data["status"] == "CONFIRMED"
    assert len(data["headline_multipliers"]) == 4
    assert len(data["four_step_rollout"]) == 4


def test_stage703a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE703A_EXECUTIVE_HUMAN_SUMMARY_AND_ROLLOUT_MATRIX.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
