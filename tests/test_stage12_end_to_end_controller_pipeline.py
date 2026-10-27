"""Comprehensive End-to-End Integration Test Suite for `controller/stage12_pipeline_orchestrator.py` (T-ORCA-GEM1-05)."""

from __future__ import annotations

from controller.dynamic_atpc_mcs_controller import AP_LNA_SATURATION_CEILING_DBM
from controller.stage12_pipeline_orchestrator import (
    build_default_stage12_five_sector_suite,
    evaluate_ltu_12x_sector_profile,
    run_stage12_end_to_end_pipeline,
    run_stage12_sector_pipeline,
)


def test_stage12_pipeline_chains_all_seven_modules_with_safety_gates() -> None:
    """Verify the top-level pipeline chains all 7 modules and enforces automatic_execution_allowed=False."""
    res = run_stage12_end_to_end_pipeline()
    assert res["pipeline_version"] == "STAGE12_E2E_V1"
    assert len(res["chained_modules"]) == 7
    assert res["sector_count"] == 5
    assert res["automatic_execution_allowed"] is False

    expected_sectors = {
        "Panel1-Guarida",
        "Panel3-Guarida",
        "Panel2-Guarida",
        "Rocket-Prism-5AC-Gen2-Sector",
        "LTU-Rocket-12x-Sector",
    }
    assert set(res["sectors"].keys()) == expected_sectors

    for sec_id, sec_out in res["sectors"].items():
        assert sec_out["automatic_execution_allowed"] is False
        assert sec_out["unified_ptmp_mac_qoe_plan"]["automatic_execution_allowed"] is False
        assert sec_out["soft_tdma_ack_pacer_plan"]["automatic_execution_allowed"] is False
        assert sec_out["per_cpe_distance_aql_schedule"]["automatic_execution_allowed"] is False
        assert sec_out["dynamic_atpc_mcs_plan"]["automatic_execution_allowed"] is False
        assert sec_out["ltu_12x_comparative_profile"]["automatic_execution_allowed"] is False


def test_panel1_guarida_4cpe_single_uploader_rts_off_and_lna_protection() -> None:
    """Verify Panel1-Guarida (4 CPEs, 1 active uploader) keeps rts=off, avoids 7% RTS tax, and clamps AP RX <= -48 dBm."""
    suite = build_default_stage12_five_sector_suite()
    p1 = run_stage12_sector_pipeline(suite[0])

    u = p1["unified_ptmp_mac_qoe_plan"]
    assert u["total_cpes"] == 4
    assert u["active_ul_cpes"] == 1
    assert u["rts_cts_enabled"] is False
    assert u["rts_iw_arg"] == "off"
    assert u["phase_count_k"] == 1
    assert u["rts_handshake_tax_avoided_pct"] >= 7.0
    assert u["lna_saturating_cpes_before"] == 1
    assert u["lna_saturating_cpes_after"] == 0
    assert u["max_ap_rx_rssi_after_dbm"] <= AP_LNA_SATURATION_CEILING_DBM


def test_panel3_guarida_6cpe_galeano_imbalance_and_rts256_k4_ack_pacing() -> None:
    """Verify Panel3-Guarida (6 active uploaders + GALEANO 10 dB chain imbalance) engages rts=256+K=4 and caps GALEANO MCS."""
    suite = build_default_stage12_five_sector_suite()
    p3 = run_stage12_sector_pipeline(suite[1])

    u = p3["unified_ptmp_mac_qoe_plan"]
    assert u["total_cpes"] == 6
    assert u["active_ul_cpes"] == 6
    assert u["rts_cts_enabled"] is True
    assert u["rts_iw_arg"] == "256"
    assert u["phase_count_k"] == 4
    assert u["max_ap_rx_rssi_after_dbm"] <= AP_LNA_SATURATION_CEILING_DBM

    galeano = next(p for p in u["cpe_profiles"] if p["cpe_id"] == "P3_GALEANO")
    assert galeano["recommended_ul_mcs_ceiling"] <= 6
    assert galeano["deficit_be_starvation_detected"] is True
    assert galeano["wmm_ac_vo_dscp_ef_bypass_enabled"] is True


def test_panel2_guarida_22cpe_franco_severo_and_tower_conflict_graph_pareto() -> None:
    """Verify Panel2-Guarida (22 CPEs, FRANCO_Debora & SEVERO) and Guarida 3-sector conflict-graph Pareto gains."""
    res = run_stage12_end_to_end_pipeline()
    p2 = res["sectors"]["Panel2-Guarida"]["unified_ptmp_mac_qoe_plan"]
    assert p2["total_cpes"] == 22
    assert p2["active_ul_cpes"] == 12
    assert p2["rts_cts_enabled"] is True
    assert p2["rts_iw_arg"] == "256"
    assert p2["phase_count_k"] == 4
    assert p2["ap_radio_coverage_class"] == 27  # 12 km SEVERO
    assert p2["max_ap_rx_rssi_after_dbm"] <= AP_LNA_SATURATION_CEILING_DBM

    severo = next(p for p in p2["cpe_profiles"] if p["cpe_id"] == "P2_SEVERO")
    assert severo["cpe_be_low_us"] == 3950
    assert severo["recommended_ul_mcs_ceiling"] <= 3

    # Verify Guarida 3-sector tower conflict-graph optimizer improves goodput and cuts SINR bleed
    wa_tower = res["guarida_tower_conflict_graph_wa_plan"]
    xc_tower = res["guarida_tower_conflict_graph_xc_prism_plan"]
    assert wa_tower["goodput_gain_pct_vs_baseline"] > 20.0
    assert xc_tower["recommended_knee_point_plan"]["total_tower_goodput_mbps"] > wa_tower["recommended_knee_point_plan"]["total_tower_goodput_mbps"]


def test_rocket_prism_5ac_gen2_airprism_gpio_and_step1c_ie_roundtrip() -> None:
    """Verify Rocket Prism 5AC Gen2 (0xe7e9) AirPrism GPIO 13..16 tuning and Step 1C 00:27:22 Beacon IE verification."""
    suite = build_default_stage12_five_sector_suite()
    xc = run_stage12_sector_pipeline(suite[3])

    ap_interop = xc["airprism_and_step1c_interop"]
    gpio = ap_interop["airprism_gpio_state"]
    assert gpio["board_sysid"] == "0xe7e9"
    # 5785 MHz / 20 MHz in U-NII-3 -> Stage 1 Entry 1 (GPIO15=1, GPIO16=0) + Stage 2 Entry 3 (GPIO13=0, GPIO14=1)
    assert gpio["gpio_pins"] == {"gpio15": 1, "gpio16": 0, "gpio13": 0, "gpio14": 1}
    assert gpio["soc_gpio_bitmask_hex"] == "0x0000c000"

    ie_ver = ap_interop["step1c_beacon_ie_verification"]
    assert ie_ver["valid_check_ie"] is True
    assert ie_ver["passes_gate1_scan_list"] is True
    assert ie_ver["passes_gate1_sta_list"] is True
    assert ie_ver["passes_gate2_wpad_airmax_ie"] is True
    assert ie_ver["passes_gate3_is_ap_valid"] is True
    assert ap_interop["step1c_fsm_auth_transition"]["next_state"] == "STAGE2_IE_WITHDRAWN"
    assert ap_interop["step1c_fsm_connected_transition"]["next_state"] == "STAGE1_BEACON_IE_ACTIVE"


def test_ltu_rocket_12x_4096qam_thresholds_and_bandwidth_gate() -> None:
    """Verify LTU 4096-QAM (12x) startThrd=97%, stayThrd=90%, 16 dBm TX power cap, and <=50 MHz width gate."""
    suite = build_default_stage12_five_sector_suite()
    ltu_sec = suite[4]
    ltu_out = run_stage12_sector_pipeline(ltu_sec)["ltu_12x_comparative_profile"]

    assert ltu_out["width_supports_4096qam_12x"] is True
    assert ltu_out["ap_12x_conducted_tx_power_cap_dbm"] == 16.0
    assert ltu_out["startThrd_4096_pct"] == 97
    assert ltu_out["stayThrd_4096_pct"] == 90
    assert ltu_out["eligible_12x_cpes"] == 3  # First 3 close clean CPEs qualify for 12x (4096-QAM)

    # Verify 80 MHz channel width disables 4096-QAM (12x) per table_ptpPwrRange (.data+0x1f8)
    ltu_80mhz = evaluate_ltu_12x_sector_profile("LTU-80MHz", 5800, 80, ltu_sec.cpes)
    assert ltu_80mhz["width_supports_4096qam_12x"] is False
    assert ltu_80mhz["eligible_12x_cpes"] == 0
