#!/usr/bin/env python3
"""
Unit tests for Stage 36C — WISP IPTV Multicast/IGMP, DMS, Edge Micro-Caching & WMM AC_VI Sector Optimizer
Task ID: T-S36C-GEM2-WISP-IPTV-MULTICAST-IGMP-AND-ABR-SECTOR-OPTIMIZER
"""

from pathlib import Path

from controller.multiradio_golden_profile_applicator import FORBIDDEN_TOKENS
from controller.wisp_iptv_ptmp_sector_optimizer import (
    build_default_wmm_ac_vi_qos_config,
    compare_iptv_delivery_modes,
    compute_32cpe_sector_iptv_capacity,
    generate_stage36c_iptv_artifact,
    load_empirical_m13_m15_multicast_evidence,
    render_openwrt_iptv_ac_vi_qos_and_dms_script,
)


def test_delivery_architecture_comparisons_cover_all_four_modes() -> None:
    modes = {m.mode_id: m for m in compare_iptv_delivery_modes()}
    assert set(modes.keys()) == {
        "RAW_L2_80211_MULTICAST",
        "NAIVE_UNICAST_HLS_H264_STOCK",
        "IGMP_SNOOPING_DMS_UNICAST_CONVERSION",
        "FUTURAMAX_CHAMPION_V8_EDGE_CMAF_AV1_HEVC_DMS_AC_VI",
    }

    raw_mcast = modes["RAW_L2_80211_MULTICAST"]
    assert raw_mcast.wireless_phy_rate_mbps == 6.0
    assert raw_mcast.uses_ampdu_aggregation is False
    assert raw_mcast.max_simultaneous_1080p60_streams_20mhz_sector == 0
    assert raw_mcast.verdict == "REJECT_FATAL_AIRTIME_COLLAPSE"

    champion = modes["FUTURAMAX_CHAMPION_V8_EDGE_CMAF_AV1_HEVC_DMS_AC_VI"]
    assert champion.stream_bitrate_mbps == 2.2
    assert champion.uses_ampdu_aggregation is True
    assert champion.uses_igmp_dms_multicast_to_unicast is True
    assert champion.uses_pop_edge_cmaf_micro_cache is True
    assert champion.max_simultaneous_1080p60_streams_20mhz_sector == 22


def test_wmm_ac_vi_qos_script_is_ram_safe_and_configures_dms_and_aql() -> None:
    cfg = build_default_wmm_ac_vi_qos_config()
    assert cfg.ac_vi_aql_low_us == 1200
    assert cfg.ac_vi_aql_high_us == 2400
    assert cfg.ac_be_aql_low_us == 1500
    assert cfg.ac_be_aql_high_us == 3000
    assert cfg.global_aql_threshold_us == 5000
    assert cfg.fq_codel_quantum_bytes == 3028
    assert cfg.fq_memory_limit_bytes == 4194304

    script = render_openwrt_iptv_ac_vi_qos_and_dms_script(cfg)
    for token in FORBIDDEN_TOKENS:
        assert token not in script
    assert "multicast_to_unicast" in script
    assert "echo fq_quantum 3028" in script
    assert "echo fq_memory_limit 4194304" in script
    assert "1 1200 2400" in script
    assert "2 1500 3000" in script
    assert "quantum 3028" in script
    assert "ip dscp set cs4" in script
    assert "ip dscp set af41" in script


def test_32cpe_sector_capacity_and_empirical_m13_m15_evidence(tmp_path: Path) -> None:
    evidence = load_empirical_m13_m15_multicast_evidence()
    assert evidence["m15_airos_ff_mcast_airtime_limit"]["decision"] == "KEEP"
    assert evidence["m15_airos_ff_mcast_airtime_limit"]["goodput_delta_pct"] > 7.0
    assert evidence["m13_ltu_add_stall_bd_mcast_threshold"]["decision"] == "REJECT"

    cap = compute_32cpe_sector_iptv_capacity()
    summary = cap["summary_comparison"]
    assert summary["stock_20mhz_1080p60_subscribers"] == 3
    assert summary["futuramax_20mhz_1080p60_subscribers"] == 22
    assert summary["futuramax_20mhz_abr_subscribers"] == 32
    assert summary["futuramax_40mhz_1080p60_subscribers"] == 28
    assert summary["capacity_multiplier_20mhz_1080p60"] == 7.33

    out_json = tmp_path / "stage36c.json"
    receipt = generate_stage36c_iptv_artifact(out_json)
    assert out_json.exists()
    assert receipt["stage"] == "36C"
