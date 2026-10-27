"""Tests for Stage 547A: SimPy + pymoo NSGA-II Evaluation of Guarida Panel2 (22 CPEs) & Panel3 (6 CPEs) TDMA vs CSMA Airtime Pareto."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage547a_guarida_panel2_panel3_tdma_vs_csma_airtime_pareto.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE547A_GUARIDA_PANEL2_PANEL3_TDMA_VS_CSMA_AIRTIME_PARETO.md"


def test_stage547a_28cpe_pareto_and_stage455a_anchor():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "547A"
    anchor = data["stage455a_re_anchor"]
    assert anchor["panel2_82_baseline_mpdus_requed"] == 139751148
    assert anchor["panel3_83_baseline_excess_retries"] == 9522084
    assert data["comparative_deltas"]["joint_goodput_gain_mbps"] > 35.0
    assert data["comparative_deltas"]["panel3_excess_retries_reduction_pct_points"] > 20.0
    assert "five_pillar_compliance" in data


def test_stage547a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
