#!/usr/bin/env python3
"""
Unit tests for Stage 37C — PtMP/PtP Realistic Capacity Ceiling, 6-Family Matrix & WISP IPTV NetJSON Template
Task ID: T-S37C-GEM2-PTMP-PTP-REALISTIC-CAPACITY-CEILING-AND-IPTV-NETJSON-TEMPLATE
"""

from pathlib import Path

from analysis.realistic_ptmp_ptp_capacity_and_iptv_roi_calculator import (
    build_six_family_capacity_ceiling_matrix,
    compute_wisp_iptv_roi_and_backhaul_savings,
    generate_stage37c_artifact,
    render_mikrotik_routeros_v7_iptv_config,
    render_pop_nginx_cmaf_edge_cache_and_ffmpeg_config,
)
from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from controller.wisp_iptv_ptmp_sector_optimizer import export_openwisp_iptv_netjson_template


def test_six_family_capacity_ceiling_matrix_invariants() -> None:
    rows = build_six_family_capacity_ceiling_matrix()
    assert len(rows) == 7  # 6 families with Family 1 split into PtP and PtMP
    family_ids = {r.family_id for r in rows}
    assert "FAM1_OPENWRT_QCA988X_PTP_20MHZ" in family_ids
    assert "FAM1_OPENWRT_QCA988X_PTMP_20MHZ" in family_ids
    assert "FAM2_AIROS8_5GHZ_XC_WA_20MHZ" in family_ids
    assert "FAM3_AIROS8_24GHZ_2XC_XM_20MHZ" in family_ids
    assert "FAM4_LTU_AMESOC_CYCLONEV_20MHZ" in family_ids
    assert "FAM5_AIROS6_M5_XW_WEAK_OTA_20MHZ" in family_ids
    assert "FAM6_AIRFIBER_4X_INVICTUS2_TDD" in family_ids

    for row in rows:
        # Monotonicity: Stock <= Current Achieved <= Realistic Fine-Tuned <= Physical Silicon Ceiling
        assert row.stock_baseline_goodput_mbps <= row.current_achieved_champion_mbps
        assert row.current_achieved_champion_mbps <= row.realistic_fine_tuned_target_mbps
        assert row.realistic_fine_tuned_target_mbps <= row.physical_silicon_ceiling_mbps
        # Latency monotonicity: Stock >= Current Achieved >= Realistic >= Physical Floor
        assert row.stock_loaded_p95_rtt_ms >= row.current_achieved_p95_rtt_ms
        assert row.current_achieved_p95_rtt_ms >= row.realistic_fine_tuned_p95_rtt_ms
        assert row.realistic_fine_tuned_p95_rtt_ms >= row.physical_floor_p95_rtt_ms
        assert row.iptv_1080p60_streams_champion_av1 > row.iptv_1080p60_streams_stock


def test_openwisp_iptv_netjson_template_is_valid_and_deterministic() -> None:
    t1 = export_openwisp_iptv_netjson_template()
    t2 = export_openwisp_iptv_netjson_template()
    assert t1["backend"] == "netjsonconfig.OpenWrt"
    assert t1["config"]["type"] == "DeviceConfiguration"
    assert t1["profile_sha256"] == t2["profile_sha256"]
    assert len(t1["profile_sha256"]) == 64

    files = {f["path"]: f["contents"] for f in t1["config"]["files"]}
    assert "/tmp/futuramax/openwrt_iptv_ac_vi_dms_champion_v8.json" in files
    assert "/tmp/futuramax/apply_iptv_ac_vi_dms_ram.sh" in files
    script = files["/tmp/futuramax/apply_iptv_ac_vi_dms_ram.sh"]
    assert "multicast_to_unicast" in script
    assert "maxrate 3500kbit" in script
    assert "ff_mcast_airtime_limit" in script
    for token in FORBIDDEN_TOKENS:
        assert token not in script


def test_mikrotik_nginx_configs_and_roi_calculator(tmp_path: Path) -> None:
    ros_cfg = render_mikrotik_routeros_v7_iptv_config()
    assert "new-dscp=32" in ros_cfg
    assert "new-dscp=34" in ros_cfg
    assert "cake-diffserv=diffserv4" in ros_cfg
    assert "ether2-sw-poe200" in ros_cfg

    edge_cfg = render_pop_nginx_cmaf_edge_cache_and_ffmpeg_config()
    assert "proxy_cache_lock on;" in edge_cfg["nginx_cmaf_edge_cache_conf"]
    assert "libsvtav1" in edge_cfg["ffmpeg_svtav1_cmaf_abr_command"]

    roi = compute_wisp_iptv_roi_and_backhaul_savings()
    sec = roi["single_32cpe_sector_metrics"]
    assert sec["stock_max_1080p60_iptv_subscribers"] == 3
    assert sec["futuramax_v8_max_1080p60_iptv_subscribers"] == 22
    assert sec["futuramax_v8_max_abr_iptv_subscribers"] == 32
    assert sec["net_additional_1080p60_subscribers_unlocked"] == 19
    assert sec["backhaul_bandwidth_saved_mbps"] == 119.2
    assert sec["backhaul_bandwidth_reduction_pct"] == 93.12

    out_path = tmp_path / "stage37c.json"
    receipt = generate_stage37c_artifact(out_path)
    assert out_path.exists()
    assert receipt["stage"] == "37C"
