"""Pytest suite for Stage 776A Zero-FP Observability Engine v9 (Rogue DHCP Detector & ANI Auditor)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage776a_engine_v9_receipt():
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage776a_zero_fp_observability_engine_v9_rogue_dhcp_detector.json"
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "776A"
    assert data["status"] == "CONFIRMED"
    assert data["engine_version"] == "v9.0"
    sigs = data["v9_detectors"]["rogue_dhcp_and_ra_detector"]["known_rogue_signatures"]
    assert any(s["source_ip"] == "192.168.1.20" for s in sigs)
    assert data["v9_detectors"]["qca988x_ani_state_auditor"]["expected_state"] == 1


def test_stage776a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE776A_ZERO_FP_OBSERVABILITY_ENGINE_V9_ROGUE_DHCP_DETECTOR.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
