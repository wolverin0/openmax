from __future__ import annotations

import json
from pathlib import Path

from analysis.re_ubnt_poll_and_ltu_4096qam import (
    OUTPUT_JSON_PATH,
    REPO_ROOT,
    build_deep_re_report,
)


def test_re_ubnt_poll_and_ltu_artifact_exists_and_matches_live_extraction() -> None:
    assert OUTPUT_JSON_PATH.exists(), f"Missing artifact: {OUTPUT_JSON_PATH}"
    saved = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))
    computed = build_deep_re_report()
    assert saved == computed


def test_ubnt_poll_host_cross_platform_and_sysctl_tables() -> None:
    report = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))["ubnt_poll_host_re"]

    # 1. All 5 builds present and WA vs XC .rodata/.data byte-identical
    inv = report["module_inventory"]
    assert set(inv.keys()) == {
        "WA.v8.5.12",
        "WA.v8.7.4-cs",
        "WA.v8.7.25",
        "XC.v8.7.4-cs",
        "XC.v8.7.25",
    }
    assert inv["WA.v8.7.25"]["size_bytes"] == 189880
    assert inv["XC.v8.7.25"]["size_bytes"] == 189880
    assert report["cross_platform_identity"]["wa_vs_xc_v8725_rodata_identical"] is True
    assert report["cross_platform_identity"]["wa_vs_xc_v8725_data_identical"] is True
    assert report["cross_platform_identity"]["wa_vs_xc_v874cs_rodata_identical"] is True
    assert report["cross_platform_identity"]["functions_added_between_v874cs_and_v8725"] == [
        "ubnt_poll_host_get_fwname",
        "ubnt_poll_host_get_txpower",
        "ubnt_poll_host_set_txpower",
        "ubnt_poll_host_sta_remove_oldest",
    ]
    assert report["cross_platform_identity"]["functions_added_since_v8512"] == [
        "ubnt_poll_host_get_fwname",
        "ubnt_poll_host_get_txpower",
        "ubnt_poll_host_set_txpower",
        "ubnt_poll_host_sta_remove_oldest",
    ]

    # 2. 3 global sysctls + 31 per-radio sysctls = 34 sysctl nodes
    sysctls = report["sysctl_hierarchy"]
    assert [n["procname"] for n in sysctls["global_nodes"]] == [
        "addradio",
        "gpsreset",
        "gps_info",
    ]
    assert len(sysctls["per_radio_nodes"]) == 31
    radio_names = {n["procname"] for n in sysctls["per_radio_nodes"]}
    for expected in (
        "enable",
        "timing",
        "fixed_frame",
        "netconf",
        "cms_bias",
        "voip_bias",
        "atpc",
        "daprot",
        "swr_limit",
        "noack_mode",
        "sta_priority",
        "debug_block_sta",
        "debug_tid",
    ):
        assert expected in radio_names

    # 3. 60 netconf subcommands and 58-field 104-byte struct schema
    assert len(report["netconf_subcommands"]) == 60
    assert len(report["netconf_struct_schema"]) == 58
    ht40_ac = report["rodata_netconf_profiles"]["ht40_ptmp_ac_0xb90"]
    assert ht40_ac["flags"] == 2256
    assert ht40_ac["down_dur"] == 8000
    assert ht40_ac["up_dur"] == 8000
    assert ht40_ac["cbp_dur_slot"] == 20
    assert ht40_ac["high_contention_sta_count"] == 4

    # 4. _retr_supression_levels (10 levels) & _voip_dynamic_duration_levels (10 levels)
    retr = report["rodata_retr_suppression_levels"]
    assert len(retr) == 10
    assert retr[0]["txop_qual_thresh_nr_nb_pct"] == 20
    assert retr[9]["dl_rate_ratio_thresh_nr"] == 51
    assert retr[9]["ul_per_thresh_nr_pct"] == 55
    assert retr[9]["txop_qual_thresh_nr_nb_pct"] == 85

    voip = report["rodata_voip_dynamic_duration_levels"]
    assert len(voip) == 10
    assert voip[2]["high_contention_sta_count"] == 2
    assert voip[2]["high_contention_min_down_dur_us"] == 15000
    assert voip[2]["high_contention_min_up_dur_us"] == 15000
    assert voip[9]["high_contention_sta_count"] == 8
    assert voip[9]["high_contention_min_up_dur_us"] == 7500


def test_ltu_4096qam_tables_thresholds_and_knobs() -> None:
    ltu = json.loads(OUTPUT_JSON_PATH.read_text(encoding="utf-8"))["ltu_4096qam_re"]
    ap_core = ltu["aflturocket_2_4_2_ame_core"]
    cpe_core = ltu["afltu_2_4_2_ame_core"]

    # 1. AP and CPE ame_core.ko share identical rate/sensitivity/power tables
    assert cpe_core["tables_identical_to_ap"] is True

    # 2. AutoMCS tables: SISO tops out at MCS 23 (10x); MIMO reaches MCS 31 (12x 4096-QAM)
    mcs_tbls = ap_core["auto_mcs_progression_tables"]
    assert mcs_tbls["autoMcsAllSisoTbl"][-1] == {
        "mcs_index": 23,
        "mimo_flag": 0,
        "streams": "SISO (1x1)",
        "modulation": "1024-QAM (10x)",
    }
    assert mcs_tbls["autoMcsUseSisoTbl"][-1] == {
        "mcs_index": 31,
        "mimo_flag": 1,
        "streams": "MIMO (2x2)",
        "modulation": "4096-QAM (12x)",
    }
    assert mcs_tbls["autoMcsOthersTbl"][-1] == {
        "mcs_index": 31,
        "mimo_flag": 1,
        "streams": "MIMO (2x2)",
        "modulation": "4096-QAM (12x)",
    }

    # 3. Rate adaptation thresholds for 4096-QAM (12x), 1024-QAM (10x), 256-QAM (8x), 64-QAM (6x)
    thr = ap_core["rate_adaptation_thresholds"]
    assert thr["startThrd_4096_pct"] == 97
    assert thr["stayThrd_4096_pct"] == 90
    assert thr["mcsUpThrd_1024_pct"] == 93
    assert thr["mcsUpThrd_256_pct"] == 96
    assert thr["mcsUpThrd_lowqam_pct"] == 95
    assert thr["ackmcsUpThrd_pct"] == 98
    assert thr["ra_offset_table_db"] == [0, 9, 18, 25, 30]

    # 4. Sensitivity & bandwidth support for 4096-QAM (10..50 MHz enabled, 60..100 MHz disabled)
    sens = ap_core["rx_sensitivity_tables_dbm"]
    assert sens["sensitivity_ptp_6mod_by_5bw"]["10_MHz"]["4096-QAM (12x)"] == -66
    assert sens["sensitivity_ptp_6mod_by_5bw"]["20_MHz"]["4096-QAM (12x)"] == -63
    assert sens["sensitivity_ptp_6mod_by_5bw"]["40_MHz"]["4096-QAM (12x)"] == -59
    assert sens["sensitivity_ptp_6mod_by_5bw"]["50_MHz"]["4096-QAM (12x)"] == -57

    ptp_range = sens["table_ptp_pwr_range_7mod_by_8bw_profile0"]
    for bw in ("10_MHz", "20_MHz", "30_MHz", "40_MHz", "50_MHz"):
        assert ptp_range[bw]["4096-QAM (12x)"]["supported"] is True
    for bw in ("60_MHz", "80_MHz", "100_MHz"):
        assert ptp_range[bw]["4096-QAM (12x)"]["supported"] is False

    # 5. Conducted TX power backoff for 4096-QAM (12x) vs 1024-QAM (10x) vs 256-QAM (8x) vs 64-QAM (6x)
    pwr = ap_core["tx_power_backoff_by_mcs_dbm"]["mcs_txpwr_freq_ptp_dbm"]
    rocket_low = pwr["AF-5XHD_LTU-Rocket_LowBand"]
    assert rocket_low["4096-QAM (12x)"] == 16.0
    assert rocket_low["1024-QAM (10x)"] == 20.0
    assert rocket_low["256-QAM (8x)"] == 22.0
    assert rocket_low["64-QAM (6x)"] == 24.0
    assert rocket_low["16-QAM (4x)"] == 29.0

    # 6. Runtime interfaces and Stage 12 documentation
    dev_if = ltu["ame_dev_and_runtime_interfaces"]
    assert dev_if["identical_across_ap_and_cpe"] is True
    assert dev_if["debugfs_nodes_count"] == 29
    assert dev_if["sysfs_debug_attrs_count"] == 101
    assert ap_core["module_parameters_count"] == 57

    doc_path = REPO_ROOT / "docs" / "STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md"
    assert doc_path.exists()
    doc_text = doc_path.read_text(encoding="utf-8")
    assert "_retr_supression_levels" in doc_text
    assert "startThrd_4096" in doc_text
