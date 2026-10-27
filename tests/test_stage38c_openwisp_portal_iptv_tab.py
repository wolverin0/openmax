#!/usr/bin/env python3
"""
Unit tests for Stage 38C — OpenWISP Dual-NMS Portal IPTV & 6-Family Capacity Ceiling Integration
Task ID: T-S38C-GEM2-OPENWISP-PORTAL-IPTV-TAB-AND-FULL-WISP-ROLLOUT-BLUEPRINT
"""

from pathlib import Path

from tools.serve_openwisp_dual_nms_live import (
    build_iptv_and_capacity_ceiling_api_payload,
    build_openwisp_dual_nms_registry,
    build_openwisp_portal_html,
)


def test_stage38c_iptv_and_capacity_ceiling_api_payload() -> None:
    payload = build_iptv_and_capacity_ceiling_api_payload()
    assert payload["stage"] == "38C"
    tpl = payload["openwisp_iptv_netjson_template"]
    assert tpl["name"] == "FMX openwrt_iptv_ac_vi_dms_champion_v8"
    assert tpl["profile_sha256"].startswith("a0a3ef9ebd0be07e")
    assert len(payload["six_family_capacity_ceiling_matrix"]) == 7

    summary = payload["sector_32cpe_iptv_concurrency"]["summary_comparison"]
    assert summary["stock_20mhz_1080p60_subscribers"] == 3
    assert summary["futuramax_20mhz_1080p60_subscribers"] == 22
    assert summary["futuramax_20mhz_abr_subscribers"] == 32
    assert summary["futuramax_40mhz_1080p60_subscribers"] == 28

    roi = payload["wisp_iptv_roi_and_backhaul_savings"]["single_32cpe_sector_metrics"]
    assert roi["backhaul_bandwidth_reduction_pct"] == 93.12


def test_stage38c_openwisp_portal_html_contains_iptv_and_ceiling_tab(tmp_path: Path) -> None:
    reg = build_openwisp_dual_nms_registry()
    assert "iptv_and_capacity_ceiling" in reg

    out_html = tmp_path / "OPENWISP_DUAL_NMS_PORTAL.html"
    build_openwisp_portal_html(out_html)
    text = out_html.read_text(encoding="utf-8")

    # Verify all 4 required sub-panels (a, b, c, d) are rendered inside OPENWISP_DUAL_NMS_PORTAL.html
    assert "WISP IPTV &amp; 6-Family Capacity Ceiling" in text
    assert "FMX openwrt_iptv_ac_vi_dms_champion_v8" in text
    assert "da0bd9dfe0f96432" in text
    assert "6-Family Realistic PtMP/PtP Capacity Ceiling Matrix" in text
    assert "32-CPE Sector IPTV Concurrency Calculator" in text
    assert "22/32" in text
    assert "28/32" in text
    assert "32/32" in text
    assert "ether2-sw-poe200" in text
    assert "proxy_cache_lock on;" in text
    assert "-93.12%" in text
