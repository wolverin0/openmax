#!/usr/bin/env python3
"""Tests for Stage 421A — Formalization of FMX-DISC-45 & FMX-DISC-46."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage421a_fmx_disc_45_46_curation_receipt.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE421A_FMX_DISC_45_46_CURATION.md"
CURATED_PATH = REPO_ROOT / "docs" / "CURATED_HISTORICAL_DISCOVERIES_AND_GAPS_AUDIT.md"


def test_stage421a_json_receipt_and_curated_doc() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "421A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    ver = data["curated_doc_verification"]
    assert ver["has_fmx_disc_45"] is True
    assert ver["has_fmx_disc_46"] is True
    assert ver["line_count"] < 220
    assert ver["doc_head_count"] == 1

    curated_text = CURATED_PATH.read_text(encoding="utf-8")
    assert "FMX-DISC-45" in curated_text
    assert "FMX-DISC-46" in curated_text
    assert len(curated_text.splitlines()) < 220


def test_stage421a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
