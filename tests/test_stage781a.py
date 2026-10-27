"""Pytest verification for Stage 781A (Cross-Fleet Champion v58.0 Bundle with Zero-Rogue-DHCP Guarantee)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / "artifacts" / "autoresearch" / "stage781a_cross_fleet_champion_v58_bundle.json"
DOC = ROOT / "docs" / "STAGE781A_CROSS_FLEET_CHAMPION_V58_BUNDLE.md"


def test_stage781a_champion_v58_bundle() -> None:
    assert RECEIPT.exists(), f"Missing {RECEIPT}"
    data = json.loads(RECEIPT.read_text(encoding="utf-8"))
    assert data["stage"] == "STAGE-781A"
    assert data["status"] == "CONFIRMED"
    assert data["champion_version"] == "v58.0"
    assert data["total_cross_lane_counterbalanced_windows"] == 872
    dhcp = data["zero_rogue_dhcp_guarantee"]
    assert dhcp["guaranteed_across_all_families"] is True
    assert dhcp["openwrt_dhcp_lan_ignore"] == "1"
    assert dhcp["openwrt_verified_squashfs_images_count"] == 180
    assert dhcp["ltu_rogue_dhcp_daemons_on_bridge"] == 0
    assert len(data["radio_family_matrix"]) == 8

    assert DOC.exists()
    lines = DOC.read_text(encoding="utf-8").splitlines()
    assert len(lines) < 200
    assert lines[0].startswith("<!-- doc-head:")
