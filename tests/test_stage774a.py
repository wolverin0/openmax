"""Pytest suite for Stage 774A LTU Champion v20 (264-Window & Zero Rogue DHCP Kit)."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_stage774a_kit_and_receipt():
    helper = ROOT / "firmware" / "ltu_safe_kit" / "fmx_ltu_v20_264window_zero_dhcp_kit.sh"
    receipt_path = ROOT / "artifacts" / "autoresearch" / "stage774a_ltu_champion_v20_264window_zero_dhcp_kit.json"
    assert helper.exists()
    assert receipt_path.exists()
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert data["stage"] == "774A"
    assert data["status"] == "CONFIRMED"
    assert data["cumulative_ltu_windows"] == 264
    assert data["rogue_dhcp_remediation"]["fallback_ip"] == "192.168.1.20"
    assert data["rogue_dhcp_remediation"]["rogue_leases_emitted"] == 0
    assert data["safety"]["touched_dev_ame"] is False


def test_stage774a_doc_limits():
    doc_path = ROOT / "docs" / "STAGE774A_LTU_CHAMPION_V20_264WINDOW_ZERO_DHCP_KIT.md"
    assert doc_path.exists()
    text = doc_path.read_text(encoding="utf-8")
    assert len(text.splitlines()) < 200
    assert text.count("<!-- doc-head:") == 1
