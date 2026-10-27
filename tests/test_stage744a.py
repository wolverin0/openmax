"""Pytest suite for Stage 744A Zero-FP Observability Engine v8 (PHYERR & Thermal)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage744a_engine_v8_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage744a_zero_fp_observability_engine_v8_spectral_and_thermal.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "744A"
    assert data["status"] == "CONFIRMED"
    assert data["engine_version"] == "v8.0"
    d = data["v8_detectors"]
    assert d["qca988x_phyerr_storm_detector"]["spectral_radar_storm_threshold_per_sec"] == 2500.0
    assert d["ltu_pa_thermal_drift_detector"]["pa_compression_warn_c"] == 65.0


def test_stage744a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE744A_ZERO_FP_OBSERVABILITY_ENGINE_V8_SPECTRAL_AND_THERMAL.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
