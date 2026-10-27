#!/usr/bin/env python3
"""Tests for Stage 454A — Guarida .60 <-> .61 5-Snapshot EVM Notch & CINR Gap Audit."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage454a_guarida_60_61_subcarrier_notch_and_cinr_gap.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE454A_GUARIDA_60_61_SUBCARRIER_NOTCH_AND_CINR_GAP.md"


def test_stage454a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "454A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    ta = data["five_snapshot_temporal_analysis"]
    assert ta["snapshot_count_per_radio"] == 5
    assert ta["almafuerte_60_rx"]["chain0_minus_chain1_mean_gap_db"] <= -7.5
    assert ta["guarida_bh_61_rx"]["chain0_minus_chain1_mean_gap_db"] <= -8.5
    assert ta["mcs_distribution_impact"]["ap_60_to_sta_61_dl"]["mcs7_downshift_share_pct"] > 30.0


def test_stage454a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
