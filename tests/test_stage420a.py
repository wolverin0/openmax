#!/usr/bin/env python3
"""Tests for Stage 420A — SimPy + pymoo NSGA-II Panel2 + Panel3 Joint TDMA Coexistence."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
JSON_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage420a_panel2_panel3_joint_tdma_pareto.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE420A_PANEL2_PANEL3_JOINT_TDMA_PARETO.md"


def test_stage420a_json_receipt() -> None:
    assert JSON_PATH.exists(), f"Missing {JSON_PATH}"
    data = json.loads(JSON_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "420A"
    assert data["status"] == "COMPLETED"
    assert data["claim_status"] == "CONFIRMED"
    assert data["writes_performed"] == 0

    deltas = data["deltas_vs_baseline"]
    assert deltas["joint_goodput_gain_mbps"] > 30.0
    assert deltas["panel2_mpdus_requed_reduction_pct_points"] > 10.0
    assert deltas["panel3_local_enqued_reduction_pct_points"] > 50.0
    assert deltas["joint_p99_latency_reduction_ms"] > 50.0


def test_stage420a_doc_constraints() -> None:
    assert DOC_PATH.exists(), f"Missing {DOC_PATH}"
    text = DOC_PATH.read_text(encoding="utf-8")
    lines = text.splitlines()
    assert len(lines) < 220, f"Doc has {len(lines)} lines (>= 220)"
    assert text.count("<!-- doc-head:") == 1
