"""Tests for Stage 446A: Pillar 2 80 MHz MAC Clock (12.5 ns / 1.87 m) Hardware ToF Ranging & Fresnel Multipath Drift Detector."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
RECEIPT_PATH = REPO_ROOT / "artifacts" / "autoresearch" / "stage446a_hardware_tof_187m_fresnel_drift_detector.json"
DOC_PATH = REPO_ROOT / "docs" / "STAGE446A_HARDWARE_TOF_187M_FRESNEL_DRIFT_DETECTOR.md"


def test_stage446a_receipt_physics_and_links():
    assert RECEIPT_PATH.exists()
    data = json.loads(RECEIPT_PATH.read_text(encoding="utf-8"))
    assert data["stage"] == "446A"
    spec = data["hardware_trailer_spec"]
    assert spec["mac_clock_hz"] == 80_000_000
    assert spec["tick_resolution_ns"] == 12.5
    assert 1.87 <= spec["distance_resolution_m"] <= 1.88
    links = {lk["link_id"]: lk for lk in data["evaluated_links"]}
    assert links["GUARIDA_MONZON_41_LOS"]["fresnel_classification"] == "CLEAN_FIRST_FRESNEL_ZONE_LOS"
    assert links["GUARIDA_GAMBOA_223_WET_FOLIAGE_FRESNEL"]["fresnel_classification"] == "FRESNEL_POLARIZATION_MULTIPATH_OBSTRUCTION"
    assert "five_pillar_compliance" in data


def test_stage446a_doc_under_220_lines():
    assert DOC_PATH.exists()
    text = DOC_PATH.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
