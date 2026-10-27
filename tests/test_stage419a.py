#!/usr/bin/env python3
"""Tests for Stage 419A — Guarida 64-Subcarrier EVM Notch & Spectral Tilt Radiography."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage419a_guarida_subcarrier_evm_notch_tilt.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE419A_GUARIDA_SUBCARRIER_EVM_NOTCH_TILT.md"


def test_stage419a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "419A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    metrics = data["summary_metrics"]
    assert metrics["total_links_analyzed"] == 12
    assert metrics["subcarriers_per_chain"] == 64
    assert metrics["total_subcarrier_samples"] == 3072
    assert metrics["worst_multipath_notch_link"]["max_multipath_notch_depth_db"] >= 9.0
    assert metrics["worst_spectral_tilt_link"]["max_abs_spectral_tilt_db"] >= 2.0


def test_stage419a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
