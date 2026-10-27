"""Pytest suite for Stage 591A QCA988x WMI_PEER_ASSOC_CMDID SGI/LGI & Retry Helper."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage591a_artifacts_and_profiles():
    helper = ROOT / "firmware" / "openwrt" / "common" / "fmx_qca988x_peer_sgi_retry_helper.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage591a_qca988x_wmi_peer_assoc_sgi_and_retry_helper.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "591A"
    assert data["status"] == "CONFIRMED"
    assert data["stage487a_grounding"]["vht40_synced_tcp_mbps"] == 24.83
    assert "CLEAN_PTP_VHT40_SGI" in data["profiles"]
    assert data["safety"]["touched_protected_nodes"] is False


def test_stage591a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE591A_QCA988X_WMI_PEER_ASSOC_SGI_AND_RETRY_HELPER.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 220
    assert text.count("<!-- doc-head:") == 1
