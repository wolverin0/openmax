"""Tests for Stage 482A: SimPy + pymoo NSGA-II Evaluation of Pillar 5 32-CPE Cooperative Differential Fault Classification & Airtime Rescue."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage482a_cooperative_32cpe_edge_micro_worker_pareto.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE482A_COOPERATIVE_32CPE_EDGE_MICRO_WORKER_PARETO.md"


def test_stage482a_32cpe_pareto_and_zero_false_positives():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "482A"
    topo = data["guarida_topology_modeled"]
    assert topo["total_panels"] == 3
    assert topo["total_cpes"] == 32
    champ = data["cooperative_32cpe_pareto_champion"]
    assert champ["false_positive_alert_rate_pct"] == 0.0
    assert champ["fault_classification_accuracy_pct"] == 100.0
    assert champ["jain_fairness_32cpe"] >= 0.92
    assert data["comparative_deltas"]["goodput_gain_pct"] > 50.0
    assert data["comparative_deltas"]["p99_latency_reduction_pct"] > 50.0
    assert "five_pillar_compliance" in data


def test_stage482a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
