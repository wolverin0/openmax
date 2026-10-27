"""Tests for Stage 515A: SimPy + pymoo NSGA-II Evaluation of LTU DCXO GPS Discipline vs Free-Running TCXO on 4096-QAM (12X)."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage515a_ltu_dcxo_gps_vs_tcxo_4096qam_cfo_pareto.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE515A_LTU_DCXO_GPS_VS_TCXO_4096QAM_CFO_PARETO.md"


def test_stage515a_dcxo_gps_vs_tcxo_pareto():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "515A"
    re_info = data["stage486a_dcxo_tcxo_re_integration"]
    assert re_info["dcxo_symbol_hits"] == 43
    assert re_info["tcxo_symbol_hits"] == 25
    assert "bbp_rf_dcxo_is_sync_by_gps" in re_info["verified_dcxo_symbols"]
    champ = data["gps_disciplined_dcxo_pareto_champion"]
    assert champ["dwell_4096qam_12x_pct"] == 100.0
    assert champ["ldpc_retrans_rate_pct"] == 0.0
    assert data["comparative_deltas"]["goodput_gain_pct"] > 15.0
    assert "five_pillar_compliance" in data


def test_stage515a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
