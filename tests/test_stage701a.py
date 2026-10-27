"""Pytest suite for Stage 701A PBE-5AC-Gen2 VHT40 25.47 Mbps & PB-050 PtP v4 Field Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage701a_kit_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_pbe5ac_ptp_v4_25mbps_pb050_kit.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage701a_pbe5ac_vht40_25mbps_pb050_field_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "701A"
    assert data["status"] == "CONFIRMED"
    r = data["stage583a_585a_live_results"]
    assert r["vht40_peak_tcp_mbps"] == 25.47
    assert r["vht40_mean_tcp_mbps"] == 24.18
    assert r["stock_airos8_tdma_baseline_mbps"] == 22.80
    assert r["uplink_gain_pct"] == 136.4
    assert r["register_addr"] == "0x00029e00"
    assert r["register_value"] == "0x13761320"


def test_stage701a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE701A_PBE5AC_VHT40_25MBPS_PB050_FIELD_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
