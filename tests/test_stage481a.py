"""Tests for Stage 481A: Fraunhofer Near-Field (< 2*D^2/lambda = 6.15m for 400mm Dish) vs Far-Field Automatic Detector and VHT Policy Switch."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage481a_nearfield_fraunhofer_dish_cavity_compensator.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE481A_NEARFIELD_FRAUNHOFER_DISH_CAVITY_COMPENSATOR.md"


def test_stage481a_fraunhofer_physics_and_reconciliation():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "481A"
    geom = data["fraunhofer_dish_geometry"]
    assert 6.10 <= geom["fraunhofer_boundary_400mm_m"] <= 6.25
    ev = data["reconciled_live_bench_evidence_stages_105a_425a_429a"]
    assert ev["stage425a_asymmetric_mcs_ceiling"]["ap_mcs3_sta_mcs2_aggregate_mbps"] == 19.62
    assert ev["stage426a_txpower_cavity_coupling_proof"]["txp4_loss_pct"] == 100.0
    assert ev["stage427a_bandwidth_coherence_proof"]["vht20_associated"] is True
    assert ev["stage427a_bandwidth_coherence_proof"]["vht40_associated"] is False
    regimes = data["evaluated_detector_regimes"]
    assert regimes[0]["selected_htmode"] == "VHT20"
    assert regimes[2]["selected_htmode"] == "VHT80"
    assert "five_pillar_compliance" in data


def test_stage481a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
