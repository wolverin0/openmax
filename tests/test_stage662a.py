"""Pytest suite for Stage 662A PBE-5AC-Gen2 PtP Champion v3 VHT40 Rollout Kit."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage662a_kit_and_receipt():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_pbe5ac_ptp_champion_v3_vht40.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage662a_pbe5ac_ptp_champion_v3_vht40_rollout_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "662A"
    assert data["status"] == "CONFIRMED"
    m = data["verified_mechanism"]
    assert m["htmode"] == "VHT40"
    assert m["pktlog_filter"] == "0x0"
    assert m["vht40_synced_tcp_mbps"] == 24.83
    assert "sleep 2" in m["reassoc_sequence"]


def test_stage662a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE662A_PBE5AC_PTP_CHAMPION_V3_VHT40_ROLLOUT_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
