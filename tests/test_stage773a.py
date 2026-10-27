"""Pytest suite for Stage 773A WA Champion v13 (344-Window) Field Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage773a_kit_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_wa_v13_344window_field_kit.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage773a_wa_champion_v13_344window_field_rollout_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "773A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_wa_windows"] == 344
    m = data["verified_metrics"]
    assert m["vht20_peak_tcp_mbps"] == 78.51
    assert m["vht20_mean_tcp_mbps"] == 76.55
    assert m["loaded_p50_rtt_reduction_e2e_mk1_251_pct"] == 86.37
    assert m["dhcp_lan_ignore"] == 1


def test_stage773a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
