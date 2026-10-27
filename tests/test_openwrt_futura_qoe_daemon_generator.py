#!/usr/bin/env python3
"""
Unit tests for Mission 4:
  - controller/openwrt_futura_qoe_daemon_generator.py
  - artifacts/canary_panel1_guarida/openwrt_futura_qoe_procd_bundle_20261024.json
"""

from __future__ import annotations

import json
from pathlib import Path

from controller.openwrt_futura_qoe_daemon_generator import (
    CONFIRMED_PHYSICAL_BENCH_ANCHORS,
    REGIME_BIDIR_CONGESTED,
    REGIME_UNIDIR_DL_DOMINANT,
    REGIME_UNIDIR_UL_DOMINANT,
    build_coverage_class_lookup_table,
    classify_sector_traffic_regime,
    compute_autopilot_profile,
    compute_cpe_ul_concave_be_low_us,
    generate_etc_initd_futura_qoe_script,
    generate_openwrt_futura_qoe_procd_bundle,
    generate_usr_sbin_futura_qoe_autopilot_script,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def test_concave_ul_distance_law_matches_r113_to_r120_physical_bench():
    """Verify the concave-logarithmic UL law reproduces exact R113..R120 physical bench receipts."""
    expected_by_cov = {
        0: 2100,   # R113..R115 0km bench
        2: 2650,   # R116 1km (covclass=2)
        6: 3150,   # R117 3km (covclass=6)
        13: 3550,  # R118 6km (covclass=13)
        20: 3800,  # R119 9km (covclass=20)
        26: 3950,  # R120 12km (covclass=26)
        31: 4100,  # Max 14.3km (covclass=31)
    }
    for cov, expected_low_us in expected_by_cov.items():
        actual = compute_cpe_ul_concave_be_low_us(cov)
        assert actual == expected_low_us, f"cov={cov}: expected {expected_low_us}, got {actual}"

    # Verify monotonicity across all 0..31 coverage classes
    values = [compute_cpe_ul_concave_be_low_us(c) for c in range(32)]
    for i in range(1, 32):
        assert values[i] >= values[i - 1]


def test_classify_sector_traffic_regime_and_ul_hammering():
    # 1. UNIDIR_DL_DOMINANT (single downloader, minimal UL)
    dl_res = classify_sector_traffic_regime(
        dl_kbps=68500.0,
        ul_kbps=1800.0,
        station_ul_kbps_list=[180.0, 120.0],
    )
    assert dl_res["regime"] == REGIME_UNIDIR_DL_DOMINANT
    assert dl_res["active_uploading_cpes"] == 0
    assert dl_res["uplink_hammering_protection_active"] is False

    # 2. UNIDIR_UL_DOMINANT with single uploader (no RTS needed)
    ul_single = classify_sector_traffic_regime(
        dl_kbps=2100.0,
        ul_kbps=59200.0,
        station_ul_kbps_list=[59200.0, 80.0],
    )
    assert ul_single["regime"] == REGIME_UNIDIR_UL_DOMINANT
    assert ul_single["active_uploading_cpes"] == 1
    assert ul_single["uplink_hammering_protection_active"] is False

    # 3. UNIDIR_UL_DOMINANT with 4 simultaneous uploaders (UL Hammering active)
    ul_multi = classify_sector_traffic_regime(
        dl_kbps=3400.0,
        ul_kbps=48000.0,
        station_ul_kbps_list=[12000.0, 12000.0, 12000.0, 12000.0],
    )
    assert ul_multi["regime"] == REGIME_UNIDIR_UL_DOMINANT
    assert ul_multi["active_uploading_cpes"] == 4
    assert ul_multi["uplink_hammering_protection_active"] is True

    # 4. BIDIR_CONGESTED with 6 simultaneous uploaders
    bidir = classify_sector_traffic_regime(
        dl_kbps=38000.0,
        ul_kbps=32000.0,
        station_ul_kbps_list=[5300.0] * 6,
    )
    assert bidir["regime"] == REGIME_BIDIR_CONGESTED
    assert bidir["active_uploading_cpes"] == 6
    assert bidir["uplink_hammering_protection_active"] is True


def test_compute_autopilot_profile_across_regimes():
    p_bidir = compute_autopilot_profile(REGIME_BIDIR_CONGESTED, 6, active_uploading_cpes=1)
    assert p_bidir.ap_be_low_us == 1550
    assert p_bidir.ap_be_high_us == 3100
    assert p_bidir.cpe_be_low_us == 2100
    assert p_bidir.cpe_be_high_us == 4200
    assert p_bidir.cpe_fq_target_us == 8000
    assert p_bidir.cpe_rc_per_thresh == 24
    assert p_bidir.fq_memory_limit_bytes == 4194304
    assert p_bidir.rts_cts_enabled is False

    p_dl = compute_autopilot_profile(REGIME_UNIDIR_DL_DOMINANT, 6, active_uploading_cpes=1)
    assert p_dl.ap_be_low_us == 1900
    assert p_dl.ap_be_high_us == 3800
    assert p_dl.cpe_be_low_us == 2100
    assert p_dl.cpe_be_high_us == 4200

    p_ul_6km = compute_autopilot_profile(REGIME_UNIDIR_UL_DOMINANT, 13, active_uploading_cpes=3)
    assert p_ul_6km.ap_be_low_us == 1900
    assert p_ul_6km.ap_be_high_us == 3800
    assert p_ul_6km.cpe_be_low_us == 3550
    assert p_ul_6km.cpe_be_high_us == 7100
    assert p_ul_6km.cpe_aql_threshold_us == 14200
    assert p_ul_6km.cpe_fq_target_us == 16000
    assert p_ul_6km.cpe_fq_interval_us == 80000
    assert p_ul_6km.cpe_tcp_limit_output_bytes == 1048576
    assert p_ul_6km.cpe_rc_per_thresh == 50
    assert p_ul_6km.rts_cts_enabled is True
    assert p_ul_6km.rts_threshold_bytes == 256
    assert p_ul_6km.soft_tdma_ack_pacing_enabled is True
    assert p_ul_6km.soft_tdma_phase_count_k >= 2


def test_procd_scripts_and_generated_bundle_artifact():
    init_script = generate_etc_initd_futura_qoe_script()
    assert "USE_PROCD=1" in init_script
    assert "procd_set_param respawn" in init_script
    assert "5000 12000" in init_script
    assert "rts off" in init_script

    daemon_script = generate_usr_sbin_futura_qoe_autopilot_script()
    assert "/tmp/futura_qoe_disable" in daemon_script
    assert "-900" in daemon_script
    assert "4194304" in daemon_script
    assert 'RTS_MODE="256"' in daemon_script
    assert 'RTS_MODE="off"' in daemon_script
    assert "3950" in daemon_script  # covclass=26 (12km R120)

    table = build_coverage_class_lookup_table()
    assert len(table) == 32
    assert table[26][REGIME_UNIDIR_UL_DOMINANT]["cpe_be_low_us"] == 3950

    artifact_path = REPO_ROOT / "artifacts" / "canary_panel1_guarida" / "openwrt_futura_qoe_procd_bundle_20261024.json"
    assert artifact_path.exists()
    bundle = json.loads(artifact_path.read_text(encoding="utf-8"))
    assert bundle["schema_version"] == "1.0"
    assert bundle["automatic_execution_allowed"] is False
    assert len(bundle["coverage_class_regime_lookup_table"]) == 32
    assert "R120_12km_unidir_ul_2flow" in bundle["confirmed_physical_bench_anchors"]
    assert bundle["watchdog_and_safety_invariants"]["fq_memory_limit_bytes"] == 4194304
    assert bundle["watchdog_and_safety_invariants"]["hostapd_wpa_supplicant_oom_score_adj"] == -900
