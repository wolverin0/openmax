"""Pytest suite for Stage 704A Reddit Tester Release & HackerOne Update."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage704a_release_and_h1_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage704a_reddit_tester_release_and_hackerone_update.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "704A"
    assert data["status"] == "CONFIRMED"
    assert data["reddit_tester_release"]["headline_benchmarks"]["pbe5ac_vht40_peak_mbps"] == 25.47
    assert len(data["hackerone_dossier_update"]) == 3


def test_stage704a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE704A_REDDIT_TESTER_RELEASE_AND_HACKERONE_UPDATE.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
