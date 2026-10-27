"""Guarida, Stage 29B AF-4X/M5, Stage 51A/52A Champion v17/v18, Stage 48B/49B/50B LTU OTA, and Stage 54D PtP Production Rollout Deploy Packager (`T-S54D-GEM2-STAGE52A-CHAMPION-V18-AND-PTP-PRODUCTION-ROLLOUT-PACKAGER`).

Combines:
1. Guarida & Almafuerte 3-stage deterministic dry-run rollout bundle (`Stage A` 46 Mbps BNG CAKE, `Stage B` Panel2 22-CPE Mode B `cms_bias=6`/`voip_bias=6`/`daprot=2`, `Stage C` Panel3 6-CPE Canary stress validation) with `ether2-sw-poe200` backbone protection.
2. Stage 29B AF-4X Invictus (`2.5 ms` frame, `CP=8`, `BER 1e-5`, `txqueuelen=256`) and PowerBeam M5 AR934x (`tx_chainmask=2`, `rx_chainmask=3`, `txop=15 ms`, `A-MPDU 16f/16KB`) optimization models.
3. Stage 48B LTU OTA Triple-Play Champion (`STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION` / `S48B-R1-CHAMPION-V1`):
   - `ulpwrtune=-75` (`+36 dB` UL RSSI gain `-116 -> -80 dBm` via `ame_bbp_set_rxtarget(1745): NewGain(75,74) target -75`)
   - Port-5 `eth0.2`/`br0` loop teardown eliminating `force_loop_flee(290)`
   - `sch_htb.ko` + `cls_u32.ko` + `/sys/class/ame/ame_ctrl_dev/dscp` (`dscp.4.value=32` for `TOS 0x80` = `CS4`), cutting loaded `p50` RTT by `-92.5%` (`65.04 -> 4.85 ms`) and `p95` RTT by `-82.7%` (`74.34 -> 12.84 ms`).
4. Stage 51A Champion v17 (`STAGE51A_CHAMPION_V17` / `S51A-R6` `M30c_PURE_BQL_LIMIT_MAX_42392_HOLD_1000_3CPE_VERIFIED`):
   - `eth0` BQL `limit_max=42392` (`28×MTU`), `limit_min=3028` (`2×MTU`), `hold_time=1000` ms + `dev_weight_tx_bias=2` at full `netdev_budget=600` (`+6.611%` goodput `39.723 -> 42.349 Mbps`, `-36.007%` `p50` RTT, `-6.102%` `p95` RTT, `-20.977%` IPTV jitter, `-34.685%` VoIP jitter, Pareto `+8.7464%`).
5. Stage 49B LTU `pb_boost` & EVM-Matched MCS Ceiling Champion (`STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION`):
   - `pb_boost=1` (`ON`), `ulautogain 0` + `ulpwrtune -75`, `frame_len -> duty_cycle` sysfs bug guard (`echo 750 > /sys/class/ame/ame_ctrl_dev/duty_cycle`, `/bin/af set framelength 2`), and `autoMcsCeiling=15` (`64qam (6x)`), cutting median loaded `p95` RTT by `-90.8%` (`93.301 -> 8.617 ms`) while `S49B-R1` cuts IPTV UDP loss by `-83.9%` (`4.731% -> 0.762%`).
6. Stage 50B LTU Hybrid SWQ, AP-Centralized `cpe_mcs`, `maxBD` High-Water Telemetry & 3-Tier HTB Champion (`STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION`):
   - AP-centralized `cpe_mcs` (`7/11/15/19/23/31` -> `QPSKl`, `16Ql`, `64Ql`, `256Ql`, `1024Ql`, `4096l`) contract via `ame_core_set_cpe_mcs` (`3329`/`3345`).
   - `/sys/class/ame/ame_ctrl_dev/maxBD` in-flight EAB high-water telemetry (`0x31 -> 0x5..0xa`).
   - 3-tier HTB (`21000kbit` root) + `SWQ_INTERVAL_EXTEND=2` + `DGAIN_DL_ENABLE=1` achieving `7.663 ms` mean / `7.424 ms` median loaded `p95` RTT in `S50B-R1` and `4.105 ms` `p50` RTT in `S50B-R2` with `0.0%` VoIP loss.
7. Stage 52A Champion v18 (`STAGE52A_CHAMPION_V18` / `S52A-R3`: `M33a_COMBINED_BUDGET_USECS_6000_AND_BQL_MIN_4542`):
   - `eth0` BQL `limit_min=4542` (`3×MTU` matching `fq_quantum=4542`), `limit_max=42392` (`28×MTU`), `hold_time=1000` ms + `dev_weight_tx_bias=2` (`+7.022%` goodput `46.183 -> 49.426 Mbps`, `-28.919%` `p50` RTT `46.344 -> 32.942 ms`, `-1.795%` `p95` RTT `112.695 -> 110.672 ms`, `0.0%` IPTV/VoIP loss, Pareto `+7.6504%`).
8. Stage 54D PowerBeam 5AC Gen2 / LiteBeam 5AC Gen2 PtP Production Rollout Profile (`STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE`):
   - No-loop STP / `ebtables` L2 loop guard (`brctl stp br0 on`, `ebtables -A FORWARD -i ath0 -o eth0.2 -j DROP`) + 45s OTA rollback timer (`/tmp/wd_s54 45`) + BQL v18 / airOS PtP profile (`S53A-R4` + `S54A-R3`: `tx_queue_len=192`, `ampduFrames=24`, `acktimeout=25 us`, `netdev_budget=600`, WMM `AC_VI`/`AC_VO` -> `+7.3%` Bulk TCP goodput `18.041 -> 19.355 Mbps`, `27.205 Mbps` Aggregate DL, `-50.3%` `p95` RTT `34.323 -> 17.045 ms`, `-27.7%` IPTV jitter).

Safety boundary: 100% offline deterministic deploy packager (`automatic_execution_allowed=False`, `live_devices_touched=False`).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from controller.af4x_invictus_and_m5_airmax_optimizer import (
    AF4XInvictusMimoAndQueueModel,
    AF4XInvictusTddSymbolModel,
    M5AirMaxMimoRankAndChainModel,
    M5AirMaxTdmaAndQueuePacingModel,
)
from controller.stage34c_ltu_4096qam_deploy_packager import (
    STAGE48B_ARTIFACT_PATH,
    STAGE48B_DOC_PATH,
    STAGE48B_HTB_AND_DSCP_COMMANDS,
    STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION,
    STAGE48B_PORT5_LOOP_TEARDOWN_COMMANDS,
    STAGE49B_ARTIFACT_PATH,
    STAGE49B_DOC_PATH,
    STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION,
    STAGE49B_PB_BOOST_AND_EVM_MCS_COMMANDS,
    STAGE50B_ARTIFACT_PATH,
    STAGE50B_DOC_PATH,
    STAGE50B_HYBRID_SWQ_AND_3TIER_HTB_COMMANDS,
    STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION,
    STAGE50B_VALID_AP_CPE_MCS_CEILINGS,
    STAGE51A_ARTIFACT_PATH,
    STAGE51A_BQL_42392_COMMANDS,
    STAGE51A_CHAMPION_V17,
    STAGE51A_DOC_PATH,
    STAGE51C_RECEIPT_PATH,
    STAGE52A_ARTIFACT_PATH,
    STAGE52A_BQL_V18_COMMANDS,
    STAGE52A_CHAMPION_V18,
    STAGE52A_DOC_PATH,
    STAGE52C_RECEIPT_PATH,
    STAGE53A_ARTIFACT_PATH,
    STAGE53A_DOC_PATH,
    STAGE53C_RECEIPT_PATH,
    STAGE54A_ARTIFACT_PATH,
    STAGE54A_DOC_PATH,
    STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE,
    STAGE54D_PTP_45S_OTA_ROLLBACK_TIMER_SPEC,
    STAGE54D_PTP_AIROS_CHAMPION_COMMANDS,
    STAGE54D_PTP_NO_LOOP_STP_EBTABLES_GUARD_COMMANDS,
    STAGE54D_RECEIPT_PATH,
    STAGE55A_CHAMPION_V19,
    STAGE55A_CHAMPION_V19_COMMANDS,
    STAGE55A_OPENWRT_PTP_CHAMPION_PROFILE,
    STAGE55A_OPENWRT_PTP_COMMANDS,
    STAGE62A_AIROS8_PTP_CHAMPION_V4_COMMANDS,
    STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4,
    STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_CHAMPION,
    STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_COMMANDS,
    STAGE66A_RECEIPT_PATH,
    STAGE68A_AIROS8_PTP_CHAMPION_V5_COMMANDS,
    STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5,
    STAGE72A_CHAMPION_V20,
    STAGE72A_XC_PTMP_STATION_V20_COMMANDS,
    STAGE72A_XW_RATE_WARMUP_GUARD_SPEC,
    STAGE73A_AIROS8_PTP_CHAMPION_V6_COMMANDS,
    STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6,
    STAGE74B_RECEIPT_PATH,
    STAGE79A_AIROS8_PTP_CHAMPION_V7_COMMANDS,
    STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7,
    STAGE86A_AIROS8_PTP_CHAMPION_V8_COMMANDS,
    STAGE86A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V8,
    STAGE81C_CHAMPION_V21,
    STAGE81C_XC_PTMP_STATION_V21_COMMANDS,
    STAGE81C_XW_PTMP_STATION_V21_COMMANDS,
    STAGE83B_LTU_STAGE80A_SMP_AND_BINARY_PATCH_CHAMPION,
    STAGE83B_LTU_STAGE80A_SMP_AND_BINARY_PATCH_COMMANDS,
    STAGE88A_XW_M5_STAGE84B_REMEDIATION_COMMANDS,
    STAGE88A_XW_M5_STAGE84B_REMEDIATION_PROFILE,
    STAGE93A_PKTLOG_BUG01_REMEDIATION_COMMANDS,
    STAGE93A_PKTLOG_BUG01_REMEDIATION_PROFILE,
    build_stage34c_ltu_deploy_package,
    build_stage52c_deploy_package,
    build_stage53c_deploy_package,
    build_stage54d_deploy_package,
    build_stage66a_curated_all_champions_deploy_package,
    compute_canonical_sha256,
    export_stage51c_ltu_ota_triple_play_champion_receipt,
    export_stage52c_champion_v17_and_stage49b_ltu_receipt,
    export_stage53c_ltu_hybrid_swq_and_maxbd_receipt,
    export_stage54d_champion_v18_and_ptp_rollout_receipt,
    export_stage66a_curated_all_champions_rollout_receipt,
    export_stage74b_champion_v20_receipt,
    render_stage48b_ltu_poststart_and_htb_script,
    render_stage49b_ltu_pb_boost_and_evm_mcs_script,
    render_stage50b_ltu_hybrid_swq_and_3tier_htb_script,
    render_stage51a_champion_v17_bql_script,
    render_stage52a_champion_v18_bql_script,
    render_stage54d_ptp_production_rollout_script,
    render_stage55a_champion_v19_script,
    render_stage55a_openwrt_ptp_script,
    render_stage62a_airos8_ptp_champion_v4_script,
    render_stage64a_ltu_ground_up_and_binary_patch_script,
    render_stage68a_airos8_ptp_champion_v5_script,
    render_stage72a_xc_ptmp_station_v20_script,
    render_stage73a_airos8_ptp_champion_v6_script,
    render_stage79a_airos8_ptp_champion_v7_script,
    render_stage86a_airos8_ptp_champion_v8_script,
    render_stage81c_xc_ptmp_station_v21_script,
    render_stage81c_xw_ptmp_station_v21_script,
    render_stage83b_ltu_stage80a_smp_and_binary_patch_script,
    render_stage88a_xw_m5_stage84b_remediation_script,
    render_stage93a_pktlog_bug01_remediation_script,
    validate_stage48b_ltu_ota_triple_play_champion,
    validate_stage50b_ltu_hybrid_swq_and_maxbd_guard,
    validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard,
    validate_stage52a_champion_v18_and_ptp_production_rollout_guard,
    validate_stage66a_all_curated_champions_guard,
)
from tools.deploy.build_guarida_almafuerte_rollout_bundle import (
    PROTECTED_BACKBONE_INTERFACE,
    build_stage_a_almafuerte_cake_bundle,
    build_stage_b_panel2_modeb_bundle,
    build_stage_c_panel3_canary_stress_bundle,
    generate_guarida_almafuerte_rollout_bundle,
    verify_command_list_safety,
)


def build_guarida_stage29b_and_stage48b_deploy_bundle() -> Dict[str, Any]:
    """Build unified Guarida + Stage 29B AF-4X/M5 + Stage 48B/49B/50B LTU + Stage 51A/52A Champion v17/v18 + Stage 54D PtP deploy bundle."""
    guarida_bundle = generate_guarida_almafuerte_rollout_bundle()
    ltu_pkg = build_stage34c_ltu_deploy_package()
    s52c_pkg = build_stage52c_deploy_package()
    s53c_pkg = build_stage53c_deploy_package()
    s54d_pkg = build_stage54d_deploy_package()
    s66a_pkg = build_stage66a_curated_all_champions_deploy_package()

    af4x_tdd = AF4XInvictusTddSymbolModel().evaluate_frame_and_cp(
        frame_length_ms=2.5,
        cyclic_prefix_samples=8,
        short_cp_enabled=True,
        strict_timing_enabled=True,
        duty_cycle_dl_pct=50.0,
    )
    af4x_q = AF4XInvictusMimoAndQueueModel().evaluate(
        rxpower0_dbm=-72.0,
        rxpower1_dbm=-73.0,
        noise_floor_dbm=-98.0,
        target_ber_exponent=5,
        txqueuelen_packets=256,
        flowcntl_enabled=True,
    )
    m5_mimo = M5AirMaxMimoRankAndChainModel(imbalance_threshold_db=5.0).evaluate_mimo_and_chainmask(
        chain0_rssi_db=9.0,
        chain1_rssi_db=16.5,
        stbc_enabled=True,
        ewma_delegate_enabled=True,
    )
    m5_tdma = M5AirMaxTdmaAndQueuePacingModel().evaluate_tdma_and_queue(
        txop_limit_ms=15,
        txop_min_slot_ms=5,
        ampdu_max_frames=16,
        ampdu_max_bytes=16384,
        phy_rate_mbps=40.5,
        per_pct=5.5,
        txqueuelen_packets=256,
        no_auto_prio=1,
        no_ack_rate=1,
        burst_enabled=True,
    )

    safety_check = verify_command_list_safety(
        STAGE48B_PORT5_LOOP_TEARDOWN_COMMANDS
        + STAGE48B_HTB_AND_DSCP_COMMANDS
        + STAGE51A_BQL_42392_COMMANDS
        + STAGE49B_PB_BOOST_AND_EVM_MCS_COMMANDS
        + STAGE50B_HYBRID_SWQ_AND_3TIER_HTB_COMMANDS
        + STAGE52A_BQL_V18_COMMANDS
        + STAGE54D_PTP_NO_LOOP_STP_EBTABLES_GUARD_COMMANDS
        + STAGE54D_PTP_AIROS_CHAMPION_COMMANDS
        + STAGE55A_CHAMPION_V19_COMMANDS
        + STAGE55A_OPENWRT_PTP_COMMANDS
        + STAGE62A_AIROS8_PTP_CHAMPION_V4_COMMANDS
        + STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_COMMANDS
        + STAGE72A_XC_PTMP_STATION_V20_COMMANDS
        + STAGE73A_AIROS8_PTP_CHAMPION_V6_COMMANDS
        + STAGE79A_AIROS8_PTP_CHAMPION_V7_COMMANDS
        + STAGE86A_AIROS8_PTP_CHAMPION_V8_COMMANDS
    )

    return {
        "schema_version": "1.0",
        "stage": "66A",
        "task_id": "T-S66A-MERGE-ALL-CURATED-CHAMPIONS-INTO-DEPLOY-PACKAGER",
        "protected_backbone_interface": PROTECTED_BACKBONE_INTERFACE,
        "guarida_rollout_master_sha256": guarida_bundle["bundle_master_sha256"],
        "guarida_stages_count": len(guarida_bundle["stages"]),
        "stage29b_models": {
            "af4x_invictus": {
                "tdd_frame_irq140_hz": af4x_tdd.tdd_frame_irq140_hz,
                "cyclic_prefix_duration_us": af4x_tdd.cyclic_prefix_duration_us,
                "snr_margin_gain_from_ber5_db": af4x_q.snr_margin_gain_from_ber5_db,
                "txqueuelen_packets": 256,
            },
            "m5_ar934x": {
                "asymmetric_simo_tx_chainmask": m5_mimo.asymmetric_simo_tx_chainmask,
                "asymmetric_mrc_rx_chainmask": m5_mimo.asymmetric_mrc_rx_chainmask,
                "ampdu_airtime_serialization_ms": m5_tdma.ampdu_airtime_serialization_ms,
                "fits_within_tdma_txop_slot": m5_tdma.fits_within_tdma_txop_slot,
            },
        },
        "stage72a_champion_v20": STAGE72A_CHAMPION_V20,
        "stage55a_champion_v19": STAGE55A_CHAMPION_V19,
        "stage55a_openwrt_ptp_champion_profile": STAGE55A_OPENWRT_PTP_CHAMPION_PROFILE,
        "stage62a_pbe5ac_lbe5ac_airos8_ptp_champion_v4": STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4,
        "stage68a_pbe5ac_lbe5ac_airos8_ptp_champion_v5": STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5,
        "stage73a_pbe5ac_lbe5ac_airos8_ptp_champion_v6": STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6,
        "stage79a_pbe5ac_lbe5ac_airos8_ptp_champion_v7": STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7,
        "stage86a_pbe5ac_lbe5ac_airos8_ptp_champion_v8": STAGE86A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V8,
        "stage83b_ltu_stage80a_smp_and_binary_patch_champion": STAGE83B_LTU_STAGE80A_SMP_AND_BINARY_PATCH_CHAMPION,
        "stage88a_xw_m5_stage84b_remediation_profile": STAGE88A_XW_M5_STAGE84B_REMEDIATION_PROFILE,
        "stage93a_pktlog_bug01_remediation_profile": STAGE93A_PKTLOG_BUG01_REMEDIATION_PROFILE,
        "stage64a_ltu_ground_up_and_binary_patch_champion": STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_CHAMPION,
        "stage52a_champion_v18": STAGE52A_CHAMPION_V18,
        "stage54d_pbe5ac_lbe5ac_ptp_production_rollout_profile": STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE,
        "stage50b_ltu_hybrid_swq_and_maxbd_champion": STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION,
        "stage51a_champion_v17": STAGE51A_CHAMPION_V17,
        "stage49b_ltu_pb_boost_and_evm_mcs_ceiling_champion": STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION,
        "stage48b_ltu_ota_triple_play_champion": STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION,
        "stage34c_ltu_deploy_package": ltu_pkg,
        "stage52c_deploy_package": s52c_pkg,
        "stage53c_deploy_package": s53c_pkg,
        "stage54d_deploy_package": s54d_pkg,
        "stage66a_deploy_package": s66a_pkg,
        "safety_invariants_verified": safety_check,
        "automatic_execution_allowed": False,
        "live_devices_touched": False,
    }


def export_stage51c_unified_receipt(
    output_path: Path = STAGE51C_RECEIPT_PATH,
) -> Dict[str, Any]:
    """Export unified Stage 51C LTU OTA Triple-Play Champion receipt JSON."""
    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    receipt = {
        **bundle["stage34c_ltu_deploy_package"],
        "guarida_rollout_master_sha256": bundle["guarida_rollout_master_sha256"],
        "guarida_stages_count": bundle["guarida_stages_count"],
        "stage29b_models": bundle["stage29b_models"],
        "safety_invariants_verified": bundle["safety_invariants_verified"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def export_stage52c_unified_receipt(
    output_path: Path = STAGE52C_RECEIPT_PATH,
) -> Dict[str, Any]:
    """Export unified Stage 52C Champion v17 & Stage 49B LTU receipt JSON."""
    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    receipt = {
        **bundle["stage52c_deploy_package"],
        "guarida_rollout_master_sha256": bundle["guarida_rollout_master_sha256"],
        "guarida_stages_count": bundle["guarida_stages_count"],
        "stage29b_models": bundle["stage29b_models"],
        "safety_invariants_verified": bundle["safety_invariants_verified"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def export_stage53c_unified_receipt(
    output_path: Path = STAGE53C_RECEIPT_PATH,
) -> Dict[str, Any]:
    """Export unified Stage 53C Stage 50B LTU Hybrid SWQ & maxBD receipt JSON."""
    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    receipt = {
        **bundle["stage53c_deploy_package"],
        "guarida_rollout_master_sha256": bundle["guarida_rollout_master_sha256"],
        "guarida_stages_count": bundle["guarida_stages_count"],
        "stage29b_models": bundle["stage29b_models"],
        "safety_invariants_verified": bundle["safety_invariants_verified"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def export_stage54d_unified_receipt(
    output_path: Path = STAGE54D_RECEIPT_PATH,
) -> Dict[str, Any]:
    """Export unified Stage 54D Champion v18 & PBE-5AC / LBE-5AC PtP Production Rollout receipt JSON."""
    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    receipt = {
        **bundle["stage54d_deploy_package"],
        "guarida_rollout_master_sha256": bundle["guarida_rollout_master_sha256"],
        "guarida_stages_count": bundle["guarida_stages_count"],
        "stage29b_models": bundle["stage29b_models"],
        "safety_invariants_verified": bundle["safety_invariants_verified"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def export_stage66a_unified_receipt(
    output_path: Path = STAGE66A_RECEIPT_PATH,
) -> Dict[str, Any]:
    """Export unified Stage 66A Curated All-Champions Rollout receipt JSON."""
    bundle = build_guarida_stage29b_and_stage48b_deploy_bundle()
    receipt = {
        **bundle["stage66a_deploy_package"],
        "guarida_rollout_master_sha256": bundle["guarida_rollout_master_sha256"],
        "guarida_stages_count": bundle["guarida_stages_count"],
        "stage29b_models": bundle["stage29b_models"],
        "safety_invariants_verified": bundle["safety_invariants_verified"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


__all__ = [
    "PROTECTED_BACKBONE_INTERFACE",
    "STAGE48B_ARTIFACT_PATH",
    "STAGE48B_DOC_PATH",
    "STAGE48B_HTB_AND_DSCP_COMMANDS",
    "STAGE48B_LTU_OTA_TRIPLE_PLAY_CHAMPION",
    "STAGE48B_PORT5_LOOP_TEARDOWN_COMMANDS",
    "STAGE49B_ARTIFACT_PATH",
    "STAGE49B_DOC_PATH",
    "STAGE49B_LTU_PB_BOOST_AND_EVM_MCS_CEILING_CHAMPION",
    "STAGE49B_PB_BOOST_AND_EVM_MCS_COMMANDS",
    "STAGE50B_ARTIFACT_PATH",
    "STAGE50B_DOC_PATH",
    "STAGE50B_HYBRID_SWQ_AND_3TIER_HTB_COMMANDS",
    "STAGE50B_LTU_HYBRID_SWQ_AND_MAXBD_CHAMPION",
    "STAGE50B_VALID_AP_CPE_MCS_CEILINGS",
    "STAGE51A_ARTIFACT_PATH",
    "STAGE51A_BQL_42392_COMMANDS",
    "STAGE51A_CHAMPION_V17",
    "STAGE51A_DOC_PATH",
    "STAGE51C_RECEIPT_PATH",
    "STAGE52A_ARTIFACT_PATH",
    "STAGE52A_BQL_V18_COMMANDS",
    "STAGE52A_CHAMPION_V18",
    "STAGE52A_DOC_PATH",
    "STAGE52C_RECEIPT_PATH",
    "STAGE53A_ARTIFACT_PATH",
    "STAGE53A_DOC_PATH",
    "STAGE53C_RECEIPT_PATH",
    "STAGE54A_ARTIFACT_PATH",
    "STAGE54A_DOC_PATH",
    "STAGE54D_PBE5AC_LBE5AC_PTP_PRODUCTION_ROLLOUT_PROFILE",
    "STAGE54D_PTP_45S_OTA_ROLLBACK_TIMER_SPEC",
    "STAGE54D_PTP_AIROS_CHAMPION_COMMANDS",
    "STAGE54D_PTP_NO_LOOP_STP_EBTABLES_GUARD_COMMANDS",
    "STAGE54D_RECEIPT_PATH",
    "STAGE55A_CHAMPION_V19",
    "STAGE55A_CHAMPION_V19_COMMANDS",
    "STAGE55A_OPENWRT_PTP_CHAMPION_PROFILE",
    "STAGE55A_OPENWRT_PTP_COMMANDS",
    "STAGE62A_AIROS8_PTP_CHAMPION_V4_COMMANDS",
    "STAGE62A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V4",
    "STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_CHAMPION",
    "STAGE64A_LTU_GROUND_UP_AND_BINARY_PATCH_COMMANDS",
    "STAGE66A_RECEIPT_PATH",
    "STAGE68A_AIROS8_PTP_CHAMPION_V5_COMMANDS",
    "STAGE68A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V5",
    "STAGE72A_CHAMPION_V20",
    "STAGE72A_XC_PTMP_STATION_V20_COMMANDS",
    "STAGE72A_XW_RATE_WARMUP_GUARD_SPEC",
    "STAGE73A_AIROS8_PTP_CHAMPION_V6_COMMANDS",
    "STAGE73A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V6",
    "STAGE74B_RECEIPT_PATH",
    "STAGE79A_AIROS8_PTP_CHAMPION_V7_COMMANDS",
    "STAGE79A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V7",
    "STAGE86A_AIROS8_PTP_CHAMPION_V8_COMMANDS",
    "STAGE86A_PBE5AC_LBE5AC_AIROS8_PTP_CHAMPION_V8",
    "STAGE81C_CHAMPION_V21",
    "STAGE81C_XC_PTMP_STATION_V21_COMMANDS",
    "STAGE81C_XW_PTMP_STATION_V21_COMMANDS",
    "STAGE83B_LTU_STAGE80A_SMP_AND_BINARY_PATCH_CHAMPION",
    "STAGE83B_LTU_STAGE80A_SMP_AND_BINARY_PATCH_COMMANDS",
    "STAGE88A_XW_M5_STAGE84B_REMEDIATION_COMMANDS",
    "STAGE88A_XW_M5_STAGE84B_REMEDIATION_PROFILE",
    "STAGE93A_PKTLOG_BUG01_REMEDIATION_COMMANDS",
    "STAGE93A_PKTLOG_BUG01_REMEDIATION_PROFILE",
    "build_guarida_stage29b_and_stage48b_deploy_bundle",
    "build_stage34c_ltu_deploy_package",
    "build_stage52c_deploy_package",
    "build_stage53c_deploy_package",
    "build_stage54d_deploy_package",
    "build_stage66a_curated_all_champions_deploy_package",
    "build_stage_a_almafuerte_cake_bundle",
    "build_stage_b_panel2_modeb_bundle",
    "build_stage_c_panel3_canary_stress_bundle",
    "compute_canonical_sha256",
    "export_stage51c_ltu_ota_triple_play_champion_receipt",
    "export_stage51c_unified_receipt",
    "export_stage52c_champion_v17_and_stage49b_ltu_receipt",
    "export_stage52c_unified_receipt",
    "export_stage53c_ltu_hybrid_swq_and_maxbd_receipt",
    "export_stage53c_unified_receipt",
    "export_stage54d_champion_v18_and_ptp_rollout_receipt",
    "export_stage54d_unified_receipt",
    "export_stage66a_curated_all_champions_rollout_receipt",
    "export_stage66a_unified_receipt",
    "export_stage74b_champion_v20_receipt",
    "generate_guarida_almafuerte_rollout_bundle",
    "render_stage48b_ltu_poststart_and_htb_script",
    "render_stage49b_ltu_pb_boost_and_evm_mcs_script",
    "render_stage50b_ltu_hybrid_swq_and_3tier_htb_script",
    "render_stage51a_champion_v17_bql_script",
    "render_stage52a_champion_v18_bql_script",
    "render_stage54d_ptp_production_rollout_script",
    "render_stage55a_champion_v19_script",
    "render_stage55a_openwrt_ptp_script",
    "render_stage62a_airos8_ptp_champion_v4_script",
    "render_stage64a_ltu_ground_up_and_binary_patch_script",
    "render_stage68a_airos8_ptp_champion_v5_script",
    "render_stage72a_xc_ptmp_station_v20_script",
    "render_stage73a_airos8_ptp_champion_v6_script",
    "render_stage79a_airos8_ptp_champion_v7_script",
    "render_stage86a_airos8_ptp_champion_v8_script",
    "render_stage81c_xc_ptmp_station_v21_script",
    "render_stage81c_xw_ptmp_station_v21_script",
    "render_stage83b_ltu_stage80a_smp_and_binary_patch_script",
    "render_stage88a_xw_m5_stage84b_remediation_script",
    "render_stage93a_pktlog_bug01_remediation_script",
    "validate_stage48b_ltu_ota_triple_play_champion",
    "validate_stage50b_ltu_hybrid_swq_and_maxbd_guard",
    "validate_stage51a_bql_42392_and_stage49b_ltu_pb_boost_guard",
    "validate_stage52a_champion_v18_and_ptp_production_rollout_guard",
    "validate_stage66a_all_curated_champions_guard",
    "verify_command_list_safety",
]


if __name__ == "__main__":
    export_stage51c_unified_receipt()
    export_stage52c_unified_receipt()
    export_stage53c_unified_receipt()
    export_stage54d_unified_receipt()
    export_stage66a_unified_receipt()
