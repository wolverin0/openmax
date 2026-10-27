"""Unit tests for Stage 51C, Stage 52C, Stage 53C & Stage 54D (`T-S54D-GEM2-STAGE52A-CHAMPION-V18-AND-PTP-PRODUCTION-ROLLOUT-PACKAGER`)."""

from __future__ import annotations

import json
from pathlib import Path
import pytest

from controller.guarida_stage29b_deploy_packager import (
    PROTECTED_BACKBONE_INTERFACE,
    STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION as GUARIDA_S48B_CHAMPION,
    STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION as GUARIDA_S49B_CHAMPION,
    STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION as GUARIDA_S50B_CHAMPION,
    STAGE51A_CHAMPION_V17 as GUARIDA_S51A_CHAMPION,
    STAGE51C_RECEIPT_PATH,
    STAGE52A_CHAMPION_V18 as GUARIDA_S52A_CHAMPION_V18,
    STAGE52C_RECEIPT_PATH,
    STAGE53C_RECEIPT_PATH,
    STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE as GUARIDA_S54D_PTP_PROFILE,
    STAGE54D_RECEIPT_PATH,
    build_guarida_stage29b_and_stage48b_deploy_bundle,
    export_stage51c_unified_receipt,
    export_stage52c_unified_receipt,
    export_stage53c_unified_receipt,
    export_stage54d_unified_receipt,
    validate_stage48b_ltu_ota_triple_play_champion,
    validate_stage50b_ltu_hybrid_swq_and_maxbd_guard,
    validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard,
    validate_stage52a_champion_v18_and_ptp_production_rollout_guard,
)
from controller.stage34c_ltu_4096qam_deploy_packager import (
    STAGE48B_HTB_AND_DSCP_COMMANDS,
    STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION as STAGE34C_S48B_CHAMPION,
    STAGE48B_PORT5_LOOP_TEARDOWN_COMMANDS,
    STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION as STAGE34C_S49B_CHAMPION,
    STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION as STAGE34C_S50B_CHAMPION,
    STAGE50B_VALID_AP_CPE_MCS_CEILINGS,
    STAGE51A_CHAMPION_V17 as STAGE34C_S51A_CHAMPION,
    build_stage34c_ltu_deploy_package,
    build_stage52c_deploy_package,
    build_stage53c_deploy_package,
    build_stage54d_deploy_package,
    render_stage48b_ltu_poststart_and_htb_script,
    render_stage49b_ltu_pb_boost_and_evm_mcs_script,
    render_stage50b_ltu_hybrid_swq_and_3tier_htb_script,
    render_stage51a_champion_v17_bql_script,
    render_stage52a_champion_v18_bql_script,
    render_stage54d_ptp_production_rollout_script,
)
from tools.deploy.guarida_stage29b_deploy_packager import (
    STAGE52A_CHAMPION_V18 as TOOLS_DEPLOY_S52A_CHAMPION_V18,
    STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE as TOOLS_DEPLOY_S54D_PTP_PROFILE,
    STAGE55A_CHAMPION_V19,
    STAGE55A_OPENWRT_PTP_CHAMPION_PROFILE,
    STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4,
    STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_CHAMPION,
    STAGE66A_RECEIPT_PATH,
    export_stage54d_unified_receipt as tools_export_stage54d_unified_receipt,
    export_stage66a_unified_receipt,
    render_stage55a_champion_v19_script,
    render_stage55a_openwrt_ptp_script,
    render_stage62a_airos8_ptp_champion_v4_script,
    render_stage64a_ltu_ground_up_and_binary_patch_script,
    validate_stage66a_all_curated_champions_guard,
)

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_stage48b_ltu_ota_triple_play_champion_exported_in_both_packagers() -> None:
    """Verify STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION is identical across both packager modules."""
    assert GUARIDA_S48B_CHAMPION == STAGE34C_S48B_CHAMPION
    champ = GUARIDA_S48B_CHAMPION
    assert champ["champion_id"] == "STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION"
    assert champ["profile_id"] == "S48B-R1-CHAMPION-V1"
    assert champ["baseline_profile_id"] == "S48B-R0-STOCK-QUEUE"
    assert champ["automatic_execution_allowed"] is False
    assert champ["live_devices_touched"] is False


def test_stage48b_ulpwrtune_75_and_36db_ul_rssi_gain() -> None:
    """Verify ulpwrtune=-75 (+36 dB UL RSSI gain -116 -> -80 dBm) invariants."""
    ul = GUARIDA_S48B_CHAMPION["uplink_rx_gain_tuning"]
    assert ul["ulpwrtune_dbm"] == -75
    assert ul["command"] == "/bin/af set ulpwrtune -75"
    assert "NewGain(75,74) target -75" in ul["kernel_log_proof"]
    assert ul["ul_rssi_before_dbm"] == -116.0
    assert ul["ul_rssi_after_dbm"] == -80.0
    assert ul["ul_rssi_gain_db"] == 36.0


def test_stage48b_port5_eth02_br0_loop_teardown_eliminating_force_loop_flee() -> None:
    """Verify Port-5 eth0.2/br0 loop teardown commands eliminate force_loop_flee(290)."""
    loop = GUARIDA_S48B_CHAMPION["port5_loop_teardown"]
    assert loop["eliminated_pathology"] == "force_loop_flee(290)"
    assert loop["bridged_interface"] == "eth0.2"
    assert loop["bridge_device"] == "br0"
    joined = "\n".join(loop["teardown_commands"])
    assert "killall -9 dnsmasq udapi-bridge" in joined
    assert "brctl delif br0 eth0.2" in joined
    assert "ifconfig eth0.2 down" in joined
    assert "ifconfig br0 down" in joined
    assert "ssdk_sh portvlan member del 5 0" in joined
    assert "ssdk_sh portvlan member del 0 5" in joined


def test_stage48b_htb_cls_u32_and_dscp_32_latency_reduction() -> None:
    """Verify sch_htb.ko + cls_u32.ko + DSCP 32 screener and -92.5% p50 / -82.7% p95 RTT deltas."""
    aqm = GUARIDA_S48B_CHAMPION["triple_play_htb_and_dscp_aqm"]
    assert "/lib/modules/3.14.65/sch_htb.ko" in aqm["kernel_modules"]
    assert "/lib/modules/3.14.65/cls_u32.ko" in aqm["kernel_modules"]
    assert aqm["dscp_screener_sysfs"] == "/sys/class/ame/ame_ctrl_dev/dscp"
    assert aqm["dscp_cs4_entry"] == "dscp.4.value=32"
    assert aqm["ath0_txqueuelen"] == 256

    bench = GUARIDA_S48B_CHAMPION["benchmark_summary"]
    r0 = bench["S48B-R0-STOCK-QUEUE"]
    r1 = bench["S48B-R1-CHAMPION-V1"]
    deltas = bench["causal_deltas"]

    assert r0["mean_loaded_ping_p50_ms"] == 65.037
    assert r1["mean_loaded_ping_p50_ms"] == 4.847
    assert deltas["loaded_p50_rtt_before_ms"] == 65.04
    assert deltas["loaded_p50_rtt_after_ms"] == 4.85
    assert deltas["loaded_p50_rtt_delta_pct"] == -92.5

    assert r0["mean_loaded_ping_p95_ms"] == 74.339
    assert r1["mean_loaded_ping_p95_ms"] == 12.835
    assert deltas["loaded_p95_rtt_before_ms"] == 74.34
    assert deltas["loaded_p95_rtt_after_ms"] == 12.84
    assert deltas["loaded_p95_rtt_delta_pct"] == -82.7


def test_validate_stage48b_champion_guard_rejects_violations() -> None:
    """Verify validate_stage48b_ltu_ota_triple_play_champion rejects invalid parameters."""
    res = validate_stage48b_ltu_ota_triple_play_champion()
    assert res["valid"] is True

    with pytest.raises(ValueError, match="ulpwrtune_dbm must be -75"):
        validate_stage48b_ltu_ota_triple_play_champion(ulpwrtune_dbm=-60)

    with pytest.raises(ValueError, match="ath0_txqueuelen must be 256"):
        validate_stage48b_ltu_ota_triple_play_champion(ath0_txqueuelen=1000)

    with pytest.raises(ValueError, match="1..16 bytes"):
        validate_stage48b_ltu_ota_triple_play_champion(ltu_ssid="FuturaMAX-LTU-Test-Over16Bytes")

    with pytest.raises(ValueError, match="alternate adjacent frequencies"):
        validate_stage48b_ltu_ota_triple_play_champion(cpe_freq_list=[5500, 5500, 5520])

    with pytest.raises(ValueError, match="force_loop_flee"):
        validate_stage48b_ltu_ota_triple_play_champion(teardown_commands=["echo noop"])

    with pytest.raises(ValueError, match="HTB \\+ DSCP AQM"):
        validate_stage48b_ltu_ota_triple_play_champion(htb_commands=["/bin/af set ulpwrtune -75"])


def test_stage51c_receipt_and_unified_deploy_bundle() -> None:
    """Verify Stage 51C receipt JSON and unified Guarida + Stage 29B + Stage 48B bundle."""
    receipt = export_stage51c_unified_receipt()
    assert STAGE51C_RECEIPT_PATH.exists()
    disk = json.loads(STAGE51C_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert disk["stage"] == "51C"
    assert disk["task_id"] == "T-S51C-GEM2-STAGE48B-LTU-OTA-TRIPLE-PLAY-ULPWRTUNE-75-AND-PORT5-LOOP-PACKAGER"
    assert disk["empirical_verification"]["p50_rtt_delta_pct"] == -92.5
    assert disk["empirical_verification"]["p95_rtt_delta_pct"] == -82.7
    assert disk["empirical_verification"]["ul_rssi_gain_db"] == 36.0
    assert disk["empirical_verification"]["eliminated_pathology"] == "force_loop_flee(290)"
    assert disk["safety_invariants_verified"]["all_safety_checks_passed"] is True
    assert disk["safety_invariants_verified"]["protects_ether2_sw_poe200"] is True

    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    assert bundle["protected_backbone_interface"] == PROTECTED_BACKBONE_INTERFACE
    assert bundle["guarida_stages_count"] == 3
    assert bundle["stage29b_models"]["af4x_invictus"]["tdd_frame_irq140_hz"] == 400.0
    assert bundle["stage29b_models"]["m5_ar934x"]["fits_within_tdma_txop_slot"] is True

    script = render_stage48b_ltu_poststart_and_htb_script()
    assert "/bin/af set ulpwrtune -75" in script
    assert "ssdk_sh portvlan member del 5 0" in script
    assert "insmod /lib/modules/3.14.65/sch_htb.ko" in script
    assert "dscp.4.value=32" in script


def test_stage51a_champion_v17_bql_42392_and_metrics() -> None:
    """Verify STAGE51A_CHAMPION_V17 (eth0 BQL 42392/3028/1000ms + dev_weight_tx_bias=2) in both packagers."""
    assert GUARIDA_S51A_CHAMPION == STAGE34C_S51A_CHAMPION
    v17 = GUARIDA_S51A_CHAMPION
    assert v17["champion_id"] == "STAGE51A_CHAMPION_V17"
    assert v17["round_id"] == "S51A-R6"
    bql = v17["eth0_bql_sweetspot"]
    assert bql["limit_max"] == 42392
    assert bql["limit_min"] == 3028
    assert bql["hold_time_ms"] == 1000
    assert v17["napi_and_backlog_sysctl"]["dev_weight_tx_bias"] == 2
    assert v17["napi_and_backlog_sysctl"]["netdev_budget"] == 600

    bench = v17["benchmark_summary"]
    assert bench["arm_a_mean_goodput_mbps"] == 39.723
    assert bench["arm_b_mean_goodput_mbps"] == 42.349
    assert bench["goodput_delta_pct"] == 6.611
    assert bench["p50_rtt_delta_pct"] == -36.007
    assert bench["p95_rtt_delta_pct"] == -6.102
    assert bench["iptv_jitter_delta_pct"] == -20.977
    assert bench["voip_jitter_delta_pct"] == -34.685
    assert bench["pareto_score_delta_pct"] == 8.7464


def test_stage49b_ltu_pb_boost_and_evm_mcs_ceiling_champion() -> None:
    """Verify STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION invariants and metrics."""
    assert GUARIDA_S49B_CHAMPION == STAGE34C_S49B_CHAMPION
    s49b = GUARIDA_S49B_CHAMPION
    assert s49b["champion_id"] == "STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION"
    cfg = s49b["pb_boost_and_ul_gain_config"]
    assert cfg["pb_boost"] == 1
    assert cfg["ulautogain"] == 0
    assert cfg["ulpwrtune_dbm"] == -75

    bug_guard = s49b["frame_len_to_duty_cycle_bug_guard"]
    assert bug_guard["ame_core_sysfs_frame_len_bug_confirmed"] is True
    assert bug_guard["safe_duty_cycle_restore_cmd"] == "echo 750 > /sys/class/ame/ame_ctrl_dev/duty_cycle"
    assert bug_guard["safe_framelength_cmd"] == "/bin/af set framelength 2"

    mcs_guard = s49b["evm_mcs_ceiling_and_cpe_mcs_guard"]
    assert mcs_guard["auto_mcs_ceiling"] == 15
    assert mcs_guard["cpe_mcs_level"] == 32
    assert "echo 0 32 0 > /sys/class/ame/ame_ctrl_dev/cpe_mcs" in mcs_guard["cpe_mcs_dl_cmd"]

    deltas = s49b["benchmark_summary"]["causal_deltas"]
    assert deltas["r2_median_loaded_p95_rtt_before_ms"] == 93.301
    assert deltas["r2_median_loaded_p95_rtt_after_ms"] == 8.617
    assert deltas["r2_median_loaded_p95_rtt_delta_pct"] == -90.8
    assert deltas["r1_iptv_loss_before_pct"] == 4.731
    assert deltas["r1_iptv_loss_after_pct"] == 0.762
    assert deltas["r1_iptv_loss_delta_pct"] == -83.9


def test_validate_stage51a_and_stage49b_guard_and_stage52c_receipt() -> None:
    """Verify Stage 52C guard validation and receipt generation."""
    res = validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard()
    assert res["valid"] is True

    with pytest.raises(ValueError, match="eth0_bql_limit_max must be 42392"):
        validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard(eth0_bql_limit_max=24576)

    with pytest.raises(ValueError, match="eth0_bql_limit_min must be 3028"):
        validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard(eth0_bql_limit_min=0)

    with pytest.raises(ValueError, match="eth0_bql_hold_time_ms must be 1000"):
        validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard(eth0_bql_hold_time_ms=750)

    with pytest.raises(ValueError, match="cpe_mcs_level MUST be 32"):
        validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard(cpe_mcs_level=15)

    with pytest.raises(ValueError, match="FORBIDDEN sysfs write to /sys/class/ame/ame_ctrl_dev/frame_len"):
        validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard(
            ltu_commands=["echo 5000 > /sys/class/ame/ame_ctrl_dev/frame_len"]
        )

    receipt = export_stage52c_unified_receipt()
    assert STAGE52C_RECEIPT_PATH.exists()
    disk = json.loads(STAGE52C_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert disk["stage"] == "52C"
    assert disk["task_id"] == "T-S52C-GEM2-STAGE51A-CHAMPION-V17-BQL-42392-AND-STAGE49B-LTU-PACKAGER"
    assert disk["empirical_verification"]["stage51a_r6_goodput_delta_pct"] == 6.611
    assert disk["empirical_verification"]["stage49b_r2_median_p95_rtt_delta_pct"] == -90.8
    assert disk["empirical_verification"]["stage49b_r1_iptv_loss_delta_pct"] == -83.9

    s51a_script = render_stage51a_champion_v17_bql_script()
    assert "42392 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max" in s51a_script
    s49b_script = render_stage49b_ltu_pb_boost_and_evm_mcs_script()
    assert "echo 1 > /sys/class/ame/ame_ctrl_dev/pb_boost" in s49b_script
    assert "echo 0 32 0 > /sys/class/ame/ame_ctrl_dev/cpe_mcs" in s49b_script


def test_stage50b_ltu_hybrid_swq_and_maxbd_champion_and_stage53c_receipt() -> None:
    """Verify STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION, guard validation, and Stage 53C receipt."""
    assert GUARIDA_S50B_CHAMPION == STAGE34C_S50B_CHAMPION
    s50b = GUARIDA_S50B_CHAMPION
    assert s50b["champion_id"] == "STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION"
    assert s50b["winning_profile_id"] == "S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X"
    assert s50b["low_latency_profile_id"] == "S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2"

    contract = s50b["ap_centralized_cpe_mcs_contract"]
    assert contract["valid_mcs_ceiling_levels"] == STAGE50B_VALID_AP_CPE_MCS_CEILINGS
    assert set(contract["valid_mcs_ceiling_levels"].keys()) == {7, 11, 15, 19, 23, 31}
    assert contract["winning_mcs_ceiling"] == 19

    maxbd = s50b["maxbd_eab_high_water_telemetry"]
    assert maxbd["unshaped_stage48b_r0_peak_hex"] == "0x31"
    assert maxbd["stage50b_shaped_peak_range_hex"] == "0x5..0xa"

    bench = s50b["benchmark_summary"]
    r1 = bench["S50B-R1-HYBRID-AUTOMCS-19-256QAM-8X"]
    r2 = bench["S50B-R2-HYBRID-AUTOMCS-15-64QAM-6X-SWQ2"]
    assert r1["mean_loaded_ping_p95_ms"] == 7.663
    assert r1["median_loaded_ping_p95_ms"] == 7.424
    assert r1["mean_voip_loss_pct"] == 0.0
    assert r2["mean_loaded_ping_p50_ms"] == 4.105
    assert r2["median_loaded_ping_p50_ms"] == 4.119
    assert r2["mean_voip_loss_pct"] == 0.0

    guard = validate_stage50b_ltu_hybrid_swq_and_maxbd_guard()
    assert guard["valid"] is True
    assert guard["cpe_mcs_label"] == "256Ql"

    with pytest.raises(ValueError, match="cpe_mcs_level in"):
        validate_stage50b_ltu_hybrid_swq_and_maxbd_guard(cpe_mcs_level=32)

    with pytest.raises(ValueError, match="maxBD peak in-flight EAB descriptors"):
        validate_stage50b_ltu_hybrid_swq_and_maxbd_guard(max_bd_peak_descriptors=49)

    with pytest.raises(ValueError, match="SWQ_INTERVAL_EXTEND=2 and DGAIN_DL_ENABLE=1"):
        validate_stage50b_ltu_hybrid_swq_and_maxbd_guard(swq_interval_extend=20)

    with pytest.raises(ValueError, match="htb_root_rate_kbit=21000"):
        validate_stage50b_ltu_hybrid_swq_and_maxbd_guard(htb_root_rate_kbit=26000)

    receipt = export_stage53c_unified_receipt()
    assert STAGE53C_RECEIPT_PATH.exists()
    disk = json.loads(STAGE53C_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert disk["stage"] == "53C"
    assert disk["task_id"] == "T-S53C-GEM2-STAGE50B-LTU-HYBRID-SWQ-MAXBD-AND-PTP-PBE5AC-PACKAGER"
    assert disk["empirical_verification"]["s50b_r1_mean_loaded_ping_p95_ms"] == 7.663
    assert disk["empirical_verification"]["s50b_r1_median_loaded_ping_p95_ms"] == 7.424
    assert disk["empirical_verification"]["s50b_r2_mean_loaded_ping_p50_ms"] == 4.105
    assert disk["empirical_verification"]["s50b_r1_voip_loss_pct"] == 0.0
    assert disk["empirical_verification"]["maxBD_shaped_range_hex"] == "0x5..0xa"

    s50b_script = render_stage50b_ltu_hybrid_swq_and_3tier_htb_script()
    assert "echo 0 > /sys/class/ame/ame_ctrl_dev/maxBD" in s50b_script
    assert "echo 0 19 0 > /sys/class/ame/ame_ctrl_dev/cpe_mcs" in s50b_script
    assert "classid 1:15 htb rate 10500kbit ceil 21000kbit prio 2" in s50b_script


def test_stage52a_champion_v18_and_ptp_production_rollout_profile_and_stage54d_receipt() -> None:
    """Verify Stage 52A Champion v18, PBE-5AC/LBE-5AC PtP Production Rollout Profile, and Stage 54D receipt."""
    assert GUARIDA_S52A_CHAMPION_V18 == TOOLS_DEPLOY_S52A_CHAMPION_V18
    assert GUARIDA_S54D_PTP_PROFILE == TOOLS_DEPLOY_S54D_PTP_PROFILE

    v18 = TOOLS_DEPLOY_S52A_CHAMPION_V18
    assert v18["champion_id"] == "STAGE52A_CHAMPION_V18"
    assert v18["round_id"] == "S52A-R3"
    assert v18["eth0_bql_v18"]["limit_min"] == 4542
    assert v18["eth0_bql_v18"]["matches_mac80211_fq_quantum_bytes"] == 4542
    assert v18["eth0_bql_v18"]["limit_max"] == 42392
    assert v18["eth0_bql_v18"]["hold_time_ms"] == 1000
    assert v18["napi_and_backlog_sysctl"]["dev_weight_tx_bias"] == 2
    assert v18["napi_and_backlog_sysctl"]["netdev_budget"] == 600
    assert v18["napi_and_backlog_sysctl"]["netdev_budget_usecs"] == 20000

    bench_v18 = v18["benchmark_summary"]
    assert bench_v18["arm_a_mean_goodput_mbps"] == 46.183
    assert bench_v18["arm_b_mean_goodput_mbps"] == 49.426
    assert bench_v18["goodput_delta_pct"] == 7.022
    assert bench_v18["arm_a_mean_p50_rtt_ms"] == 46.344
    assert bench_v18["arm_b_mean_p50_rtt_ms"] == 32.942
    assert bench_v18["p50_rtt_delta_pct"] == -28.919
    assert bench_v18["iptv_arm_b_mean_loss_pct"] == 0.0
    assert bench_v18["voip_arm_b_mean_loss_pct"] == 0.0
    assert bench_v18["pareto_score_delta_pct"] == 7.6504

    ptp = TOOLS_DEPLOY_S54D_PTP_PROFILE
    assert ptp["profile_id"] == "STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE"
    assert ptp["no_loop_stp_ebtables_guard"]["stp_enabled"] is True
    assert ptp["no_loop_stp_ebtables_guard"]["ebtables_ath0_eth02_loop_drop"] is True
    assert ptp["ota_45s_rollback_timer"]["timeout_seconds"] == 45
    assert ptp["ota_45s_rollback_timer"]["watchdog_binary_path"] == "/tmp/wd_s54"
    assert ptp["airos_ptp_champion_parameters"]["tx_queue_len"] == 192
    assert ptp["airos_ptp_champion_parameters"]["ampdu_frames"] == 24
    assert ptp["airos_ptp_champion_parameters"]["acktimeout_us"] == 25

    ptp_bench = ptp["benchmark_summary"]
    assert ptp_bench["stage53a_r4_ptp_241_to_242"]["p50_rtt_delta_pct"] == -42.3
    assert ptp_bench["stage53a_r4_ptp_241_to_242"]["p95_rtt_delta_pct"] == -36.9
    assert ptp_bench["stage54a_r3_multihop_251_to_241_to_242"]["bulk_tcp_delta_pct"] == 7.3
    assert ptp_bench["stage54a_r3_multihop_251_to_241_to_242"]["p95_rtt_delta_pct"] == -50.3
    assert ptp_bench["stage54a_r3_multihop_251_to_241_to_242"]["iptv_jitter_delta_pct"] == -27.7

    guard = validate_stage52a_champion_v18_and_ptp_production_rollout_guard()
    assert guard["valid"] is True

    with pytest.raises(ValueError, match="eth0_bql_limit_min=4542"):
        validate_stage52a_champion_v18_and_ptp_production_rollout_guard(eth0_bql_limit_min=3028)

    with pytest.raises(ValueError, match="min_netdev_budget_usecs"):
        validate_stage52a_champion_v18_and_ptp_production_rollout_guard(netdev_budget_usecs=6000)

    with pytest.raises(ValueError, match="ampduFrames=24"):
        validate_stage52a_champion_v18_and_ptp_production_rollout_guard(ptp_ampdu_frames=32)

    with pytest.raises(ValueError, match="acktimeout=25 us"):
        validate_stage52a_champion_v18_and_ptp_production_rollout_guard(ptp_acktimeout_us=48)

    with pytest.raises(ValueError, match="45s OTA rollback timer"):
        validate_stage52a_champion_v18_and_ptp_production_rollout_guard(ota_rollback_timer_s=15)

    receipt = tools_export_stage54d_unified_receipt()
    assert STAGE54D_RECEIPT_PATH.exists()
    disk = json.loads(STAGE54D_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert disk["stage"] == "54D"
    assert disk["task_id"] == "T-S54D-GEM2-STAGE52A-CHAMPION-V18-AND-PTP-PRODUCTION-ROLLOUT-PACKAGER"
    assert disk["empirical_verification"]["stage52a_r3_goodput_delta_pct"] == 7.022
    assert disk["empirical_verification"]["stage52a_r3_p50_rtt_delta_pct"] == -28.919
    assert disk["empirical_verification"]["stage52a_r3_iptv_loss_pct"] == 0.0
    assert disk["empirical_verification"]["stage52a_r3_voip_loss_pct"] == 0.0
    assert disk["empirical_verification"]["stage54a_r3_bulk_tcp_delta_pct"] == 7.3
    assert disk["empirical_verification"]["stage54a_r3_p95_rtt_delta_pct"] == -50.3
    assert disk["empirical_verification"]["ptp_3_endpoints_cfgmtd_persisted"] is True

    v18_script = render_stage52a_champion_v18_bql_script()
    assert "4542 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min" in v18_script
    ptp_script = render_stage54d_ptp_production_rollout_script()
    assert "brctl stp br0 on" in ptp_script
    assert "/tmp/wd_s54 45" in ptp_script
    assert "iwpriv wifi0 ampduFrames 24" in ptp_script
    assert "iwpriv wifi0 acktimeout 25" in ptp_script


def test_markdown_docs_line_budget_and_no_embedded_doc_head() -> None:
    """Verify CURRENT_STATE.md and MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md stay <250 lines and have no mid-body doc-head."""
    for rel in ("docs/CURRENT_STATE.md", "docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md"):
        p = REPO_ROOT / rel
        lines = p.read_text(encoding="utf-8").splitlines()
        assert len(lines) < 250, f"{rel} has {len(lines)} lines (must be < 250)"
        body_text = "\n".join(lines[5:])
        assert "<!-- doc-head" not in body_text, f"{rel} has an embedded <!-- doc-head --> block inside body"


def test_stage66a_curated_all_champions_and_stability_guards_and_receipt() -> None:
    """Verify all 4 Stage 66A unmerged production champions, 3 critical stability guards, and rollout receipt."""
    # 1. Stage 55A Champion v19 (OpenWrt PtMP) + 64MB AR9342 stability guards
    v19 = STAGE55A_CHAMPION_V19
    assert v19["champion_id"] == "STAGE55A_CHAMPION_V19"
    assert v19["round_id"] == "S55A-R2"
    assert v19["eth0_bql_v19"]["hold_time_ms"] == 800
    assert v19["eth0_bql_v19"]["limit_min"] == 4542
    assert v19["eth0_bql_v19"]["limit_max"] == 42392
    assert v19["napi_and_backlog_sysctl"]["dev_weight_tx_bias"] == 2
    assert v19["napi_and_backlog_sysctl"]["netdev_budget_usecs"] == 20000
    guards = v19["ar9342_64mb_stability_guards"]
    assert guards["hostapd_oom_score_adj"] == -900
    assert guards["fq_memory_limit_bytes"] == 4194304
    assert guards["forbid_busybox_ip_link_txqueuelen"] is True
    v19_script = render_stage55a_champion_v19_script()
    assert "echo -900 > /proc/$(pidof hostapd)/oom_score_adj" in v19_script
    assert "echo 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm/fq_memory_limit" in v19_script
    assert "echo 800 > /sys/class/net/eth0/queues/tx-0/byte_queue_limits/hold_time" in v19_script
    assert "ip link set" not in v19_script

    # 2. Stage 55A OpenWrt PtP Champion Profile
    owrt_ptp = STAGE55A_OPENWRT_PTP_CHAMPION_PROFILE
    assert owrt_ptp["profile_id"] == "STAGE55A_OPENWRT_PTP_CHAMPION_PROFILE"
    assert owrt_ptp["aql_per_ac_us"]["ap_ac_be"] == [1500, 3000]
    assert owrt_ptp["aql_per_ac_us"]["cpe_ac_be"] == [900, 1500]
    assert owrt_ptp["aqm_and_bql"]["fq_quantum_bytes"] == 4542
    assert owrt_ptp["aqm_and_bql"]["eth0_bql_hold_time_ms"] == 800
    assert owrt_ptp["aqm_and_bql"]["fq_memory_limit_bytes"] == 4194304
    assert owrt_ptp["aqm_and_bql"]["oom_score_adj"] == -900
    owrt_ptp_script = render_stage55a_openwrt_ptp_script()
    assert "echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit" in owrt_ptp_script

    # 3. Stage 62A PBE-5AC / LBE-5AC airOS 8 PtP Champion v4 + FMX-DISC-07 cron persistence
    ptp_v4 = STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4
    assert ptp_v4["champion_id"] == "STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4"
    assert ptp_v4["stage60a_r3_mac_and_rps_parameters"]["ac_be_cwmin"] == 3
    assert ptp_v4["stage60a_r3_mac_and_rps_parameters"]["ac_be_cwmax"] == 6
    assert ptp_v4["stage60a_r3_mac_and_rps_parameters"]["ampdu_frames"] == 32
    assert ptp_v4["stage60a_r3_mac_and_rps_parameters"]["tx_queue_len"] == 192
    assert ptp_v4["stage60a_r3_mac_and_rps_parameters"]["rps_cpus"] == 1
    assert ptp_v4["stage62a_r2_multiq_swretry_and_offload_parameters"]["ath0_set_multiq"] == 1
    assert ptp_v4["stage62a_r2_multiq_swretry_and_offload_parameters"]["wifi0_aggr_swretry"] == 6
    assert ptp_v4["stage62a_r2_multiq_swretry_and_offload_parameters"]["wifi0_nonaggr_swretry"] == 8
    assert ptp_v4["stage62a_r2_multiq_swretry_and_offload_parameters"]["umac_enable_tx_tcp_cksum"] == 1
    assert ptp_v4["stage62a_r2_multiq_swretry_and_offload_parameters"]["netdev_budget"] == 800
    assert ptp_v4["stage62a_r2_multiq_swretry_and_offload_parameters"]["tcp_limit_output_bytes"] == 98304
    assert ptp_v4["universal_persistence_fmx_disc_07"]["cron_status"] == "enabled"
    ptp_v4_script = render_stage62a_airos8_ptp_champion_v4_script()
    assert "iwpriv ath0 set_multiq 1" in ptp_v4_script
    assert "iwpriv wifi0 aggr_swretry 6" in ptp_v4_script
    assert "iwpriv wifi0 nonaggr_swretry 8" in ptp_v4_script
    assert "cron.status=enabled" in ptp_v4_script

    # 4. Stage 63B + 64A LTU Ground-Up & Binary Patch Champion
    ltu_c = STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_CHAMPION
    assert ltu_c["champion_id"] == "STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_CHAMPION"
    assert ltu_c["stage63b_smp_and_scheduler_optimizations"]["gBDHandleOnce"] == 84
    assert ltu_c["stage63b_smp_and_scheduler_optimizations"]["rps_cpus_mask"] == 2
    assert ltu_c["stage63b_smp_and_scheduler_optimizations"]["level6_4096qam_12x_scheduler_unlock"] is True
    assert ltu_c["stage64a_fullrea_binary_patch_loader"]["total_overlapped_relocations"] == 0
    assert ltu_c["stage64a_fullrea_binary_patch_loader"]["startThrd_4096_pct"] == 90
    assert ltu_c["stage64a_fullrea_binary_patch_loader"]["stayThrd_4096_pct"] == 82
    ltu_script = render_stage64a_ltu_ground_up_and_binary_patch_script()
    assert "echo 84 > /sys/class/ame/ame_ctrl_dev/maxBD" in ltu_script
    assert "rc.poststart.ltu_stage64a_guard.sh" in ltu_script

    # 5. Guard validation and Stage 66A rollout receipt
    guard = validate_stage66a_all_curated_champions_guard()
    assert guard["valid"] is True
    with pytest.raises(ValueError, match="hold_time=800ms"):
        validate_stage66a_all_curated_champions_guard(openwrt_bql_hold_time_ms=1000)
    with pytest.raises(ValueError, match="oom_score_adj=-900"):
        validate_stage66a_all_curated_champions_guard(hostapd_oom_score_adj=0)
    with pytest.raises(ValueError, match="FMX-DISC-16 violation"):
        validate_stage66a_all_curated_champions_guard(openwrt_commands=["ip link set dev br-lan txqueuelen 256"])

    receipt = export_stage66a_unified_receipt()
    assert STAGE66A_RECEIPT_PATH.exists()
    disk = json.loads(STAGE66A_RECEIPT_PATH.read_text(encoding="utf-8"))
    assert disk["stage"] == "66A"
    assert disk["task_id"] == "T-S66A-MERGE-ALL-CURATED-CHAMPIONS-INTO-DEPLOY-PACKAGER"
    assert disk["safety_invariants_verified"]["all_safety_checks_passed"] is True
    assert disk["safety_invariants_verified"]["protects_ether2_sw_poe200"] is True
    assert disk["validation_gate"]["valid"] is True

