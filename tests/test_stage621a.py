"""Pytest suite for Stage 621A Public Tester Showcase v6 (600-Stage Edition)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage621a_showcase_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage621a_public_tester_showcase_v6_600stage_edition.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "621A"
    assert data["status"] == "CONFIRMED"
    assert data["showcase_version"] == "v6.0-600stage"
    assert data["total_squashfs_v13_images"] == 180
    assert len(data["families"]) == 4


def test_stage621a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE621A_PUBLIC_TESTER_SHOWCASE_V6_600STAGE_EDITION.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
