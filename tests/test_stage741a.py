"""Pytest suite for Stage 741A PBE-5AC-Gen2 & LBE-5AC-Gen2 Production Bundle v5."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage741a_bundle_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_pbe5ac_lbe5ac_production_v5.sh"
    phyerr_guard = ROOT / "firmware" / "openwrt" / "common" / "fmx_qca_spectral_radar_phyerr_guard.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage741a_pbe5ac_lbe5ac_vht40_pb050_production_bundle_v5.json"
    assert helper.exists()
    assert phyerr_guard.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "741A"
    assert data["status"] == "CONFIRMED"
    sysids = [b["sysid"] for b in data["supported_boards"]]
    assert "0xe3d6" in sysids and "0xe7f9" in sysids
    assert data["verified_capabilities"]["vht40_peak_tcp_mbps"] == 25.47


def test_stage741a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE741A_PBE5AC_LBE5AC_VHT40_PB050_PRODUCTION_BUNDLE_V5.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
