"""Pytest suite for Stage 665A Public Tester Showcase v7 & OpenWrt/ath10k-ct RFC v7."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage665a_showcase_and_rfc_v7():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage665a_public_tester_showcase_and_rfc_v7.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "665A"
    assert data["status"] == "CONFIRMED"
    assert data["showcase_version"] == "v7.0"
    assert data["rfc_version"] == "RFC-v7"
    assert data["cumulative_windows_summary"]["wa_champion_v11_windows"] == 284
    assert len(data["rfc_v7_patches"]) == 4


def test_stage665a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE665A_PUBLIC_TESTER_SHOWCASE_AND_RFC_V7.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
