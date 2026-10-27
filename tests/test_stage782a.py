"""Pytest verification for Stage 782A (SimPy Guarida Panel2 Top-3 Hogs & Panel3 SOSA_Joaquin Remediation)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "artifacts" / "autoresearch" / "stage782a_guarida_panel2_34endpoint_hog_remediation_sim.json"
DOC = ROOT / "docs" / "STAGE782A_GUARIDA_PANEL2_34ENDPOINT_HOG_REMEDIATION_SIM.md"


def test_stage782a_guarida_hog_remediation_sim() -> None:
    assert RECEIPT.exists(), f"Missing {RECEIPT}"
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-782A"
    assert data["status"] == "CONFIRMED"
    assert data["topology_verified"]["total_endpoints"] == 34
    assert data["topology_verified"]["total_cpes"] == 32
    assert len(data["target_hogs_remediated"]) == 4
    deltas = data["summary_deltas"]
    assert deltas["panel2_top3_hog_gain_mbps"] == 22.40
    assert deltas["panel3_sosa_joaquin_gain_mbps"] == 11.50
    assert deltas["total_4hog_remediation_gain_over_v8_mbps"] == 33.90
    assert data["simpy_scenarios"][-1]["sector_goodput_mbps"]["tower_aggregate_mbps"] == 491.80

    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
