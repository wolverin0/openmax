#!/usr/bin/env python3
"""Stage69B RF exposition service. Reads local producer snapshots; never polls radios.

Qualified schema v1 carries AP-local station observations and a real boot epoch.
Stage61A receipts are supported as unqualified historical input, not live proof.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import math
from pathlib import Path
import re
import threading
import time

GENERATIONS = {"openwrt_wa", "airos8_wa", "airos8_xc", "airos6_xw", "ltu"}
MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_LINKS = 1024
PROM_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"
OPENMETRICS_CONTENT_TYPE = "application/openmetrics-text; version=1.0.0; charset=utf-8"
STATE_VALUES = {"UP": 1, "PENDING": 0, "DOWN": -1, "UNKNOWN": -2}
LTU_BUG_IDS = tuple(f"LTU-BUG-{i:02d}" for i in range(1, 9))
LTU_NUMBERS = {
    "irq63_cpu0_total": (0, 2**53 - 1), "irq63_cpu1_total": (0, 2**53 - 1),
    "gmax_bd_ever": (0, 65535), "bd_handle_once": (0, 65535),
    "auto_mcs_ceiling": (0, 31), "sched_mcs_ceiling_qam": (2, 4096),
    "rx_target_power_dbm": (-120, 0), "rx_target_power_expected_dbm": (-120, 0),
    "pb_boost_mode": (0, 1), "pb_boost_gain_index": (0, 255),
    "ini_rx_target_pwr": (-120, 1200), "loaded_rtt_ms": (0, 3600000),
    "loaded_loss_ratio": (0, 1),
}
LTU_BOOLS = {"expect_4096_qam", "ulpwr_enabled", "pb_boost_expected",
             "auto_mcs_write_attempted", "auto_mcs_oops_observed", "ini_parse_error",
             "htb_active", "cls_u32_loaded", "shaping_expected",
             "loaded_stalls_observed", "uplink_degraded", "under_load"}
LTU_METRICS = {
    "irq63_cpu0_total": "fmx_ltu_cpu0_irq63_total",
    "irq63_cpu1_total": "fmx_ltu_cpu1_irq63_total",
    "gmax_bd_ever": "fmx_ltu_gmax_bd_ever", "bd_handle_once": "fmx_ltu_bd_handle_once",
    "auto_mcs_ceiling": "fmx_ltu_auto_mcs_ceiling",
    "sched_mcs_ceiling_qam": "fmx_ltu_sched_mcs_ceiling_qam",
    "rx_target_power_dbm": "fmx_ltu_rx_target_power_dbm",
    "rx_target_power_expected_dbm": "fmx_ltu_rx_target_power_expected_dbm",
    "pb_boost_mode": "fmx_ltu_pb_boost_mode", "pb_boost_gain_index": "fmx_ltu_pb_boost_gain_index",
    "ulpwr_enabled": "fmx_ltu_ulpwr_enabled", "htb_active": "fmx_ltu_htb_active",
    "cls_u32_loaded": "fmx_ltu_cls_u32_loaded", "loaded_loss_ratio": "fmx_ltu_loaded_loss_ratio",
}
OPENWRT_V20_NUMBERS = {
    "bql_limit_min": (1514, 65536), "bql_limit_max": (4542, 262144),
    "bql_hold_time_ms": (100, 10000), "dev_weight_tx_bias": (1, 16),
    "fq_quantum": (1514, 9084), "fq_memory_limit": (1048576, 67108864),
    "hostapd_oom_score_adj": (-1000, 1000), "aql_threshold": (1000, 24000),
    "tsq_limit_bytes": (16384, 1048576), "tx_queue_len": (32, 4096),
}
OPENWRT_V20_METRICS = {
    "bql_limit_min": "fmx_openwrt_bql_limit_min_bytes",
    "bql_limit_max": "fmx_openwrt_bql_limit_max_bytes",
    "bql_hold_time_ms": "fmx_openwrt_bql_hold_time_ms",
    "dev_weight_tx_bias": "fmx_openwrt_dev_weight_tx_bias",
    "fq_quantum": "fmx_openwrt_fq_quantum_bytes",
    "fq_memory_limit": "fmx_openwrt_fq_memory_limit_bytes",
    "hostapd_oom_score_adj": "fmx_openwrt_hostapd_oom_score_adj",
    "aql_threshold": "fmx_openwrt_aql_threshold",
    "tsq_limit_bytes": "fmx_openwrt_tsq_limit_bytes",
    "tx_queue_len": "fmx_openwrt_tx_queue_len",
}
AIROS8_V6_NUMBERS = {
    "ptp_xmit": (0, 1), "daprot": (0, 2), "ff_mcast_airtime_limit": (0, 100),
    "cabq_maxdur": (0, 100), "syncflex": (0, 1), "netdev_budget": (64, 4096),
    "tsq_limit_bytes": (16384, 1048576), "set_multiq": (0, 1), "enable_tx_tcp_cksum": (0, 1),
}
AIROS8_V6_BOOLS = {"daprot_written_before_ff_mcast"}
AIROS8_V6_METRICS = {
    "ptp_xmit": "fmx_airos8_ptp_xmit",
    "daprot": "fmx_airos8_daprot",
    "ff_mcast_airtime_limit": "fmx_airos8_ff_mcast_airtime_limit",
    "cabq_maxdur": "fmx_airos8_cabq_maxdur",
    "syncflex": "fmx_airos8_syncflex",
    "netdev_budget": "fmx_airos8_netdev_budget",
    "tsq_limit_bytes": "fmx_airos8_tsq_limit_bytes",
    "set_multiq": "fmx_airos8_set_multiq",
    "enable_tx_tcp_cksum": "fmx_airos8_enable_tx_tcp_cksum",
}
AIROS6_XW_NUMBERS = {
    "tx_phy_mbps": (1.0, 300.0), "expected_min_tx_phy_mbps": (6.5, 300.0),
    "netdev_budget": (64, 4096), "txqueuelen": (32, 4096),
}
AIROS6_XW_BOOLS = {"warmup_completed", "under_load"}
AIROS6_XW_METRICS = {
    "tx_phy_mbps": "fmx_xw_tx_phy_mbps",
    "expected_min_tx_phy_mbps": "fmx_xw_expected_min_tx_phy_mbps",
    "netdev_budget": "fmx_xw_netdev_budget",
    "txqueuelen": "fmx_xw_txqueuelen",
}
OPENWRT_V23_NUMBERS = {
    "xc_auto_heal_recovery_ms": (0.0, 60000.0),
    "survivor_wa_to_mk1_p95_rtt_ms": (0.0, 60000.0),
    "vlan107_eth0_107_tx_queue_len": (32, 4096),
    "aql_be_low_us": (300, 10000),
    "aql_be_high_us": (600, 20000),
    "aql_threshold": (1000, 24000),
}
OPENWRT_V23_BOOLS = {"healer_daemon_active"}
OPENWRT_V23_METRICS = {
    "xc_auto_heal_recovery_ms": "fmx_openwrt_v23_xc_auto_heal_recovery_ms",
    "survivor_wa_to_mk1_p95_rtt_ms": "fmx_openwrt_v23_survivor_wa_mk1_p95_rtt_ms",
    "vlan107_eth0_107_tx_queue_len": "fmx_openwrt_v23_vlan107_tx_queue_len",
    "aql_be_low_us": "fmx_openwrt_v23_aql_be_low_us",
    "aql_be_high_us": "fmx_openwrt_v23_aql_be_high_us",
    "aql_threshold": "fmx_openwrt_v23_aql_threshold",
}
VLAN107_MK1_NUMBERS = {
    "cpe_to_mk1_e2e_p50_rtt_ms": (0.0, 60000.0),
    "cpe_to_mk1_e2e_p95_rtt_ms": (0.0, 60000.0),
    "voip_jitter_ms": (0.0, 60000.0),
}
VLAN107_MK1_BOOLS = {
    "dscp_ef_cs4_preserved",
    "qos_egress_ingress_map_active",
    "btest_port_2000_reachable",
}
VLAN107_MK1_METRICS = {
    "cpe_to_mk1_e2e_p50_rtt_ms": "fmx_vlan107_mk1_e2e_p50_rtt_ms",
    "cpe_to_mk1_e2e_p95_rtt_ms": "fmx_vlan107_mk1_e2e_p95_rtt_ms",
    "voip_jitter_ms": "fmx_vlan107_mk1_voip_jitter_ms",
}
LTU_SUPERFRAME_NUMBERS = {
    "superframe_total_symbols": (1, 160),
    "superframe_dl_symbols": (1, 160),
    "superframe_ul_symbols": (1, 160),
    "isr_checkpoint3_cycles": (0, 1000000),
    "scheduler_giveup_total": (0, 65535),
    "symbol_giveup_total": (0, 65535),
    "soc_tcp_goodput_mbps": (0.0, 1000.0),
}
LTU_SUPERFRAME_BOOLS = {"smp_irq_isolated"}
LTU_SUPERFRAME_METRICS = {
    "superframe_total_symbols": "fmx_ltu_superframe_total_symbols",
    "superframe_dl_symbols": "fmx_ltu_superframe_dl_symbols",
    "superframe_ul_symbols": "fmx_ltu_superframe_ul_symbols",
    "isr_checkpoint3_cycles": "fmx_ltu_isr_checkpoint3_cycles",
    "scheduler_giveup_total": "fmx_ltu_scheduler_giveup",
    "symbol_giveup_total": "fmx_ltu_symbol_giveup",
    "soc_tcp_goodput_mbps": "fmx_ltu_soc_tcp_goodput_mbps",
}
R2AC_2XC_NUMBERS = {
    "airview_irq2_per_sec": (0.0, 100000.0),
    "set_multiq": (0, 3),
    "vow_extstats": (0, 1),
    "bulk_tcp_goodput_mbps": (0.0, 500.0),
}
R2AC_2XC_BOOLS = {"hs_uart_irq22_gps_stopped", "ath_pktlog_unloaded"}
R2AC_2XC_METRICS = {
    "airview_irq2_per_sec": "fmx_r2ac_2xc_airview_irq2_per_sec",
    "set_multiq": "fmx_r2ac_2xc_set_multiq",
    "vow_extstats": "fmx_r2ac_2xc_vow_extstats",
    "bulk_tcp_goodput_mbps": "fmx_r2ac_2xc_bulk_tcp_goodput_mbps",
}
S102D_CSA_NUMBERS = {
    "csa_bcn_count": (1, 64),
    "station_retention_count": (0, 64),
    "wa_to_mk1_csa_p95_rtt_ms": (0.0, 60000.0),
    "wa_to_mk1_csa_jitter_ms": (0.0, 60000.0),
    "sector_goodput_mbps": (0.0, 500.0),
}
S102D_CSA_BOOLS = {"csa_block_tx"}
S102D_CSA_METRICS = {
    "csa_bcn_count": "fmx_s102d_csa_bcn_count",
    "station_retention_count": "fmx_s102d_csa_station_retention_count",
    "wa_to_mk1_csa_p95_rtt_ms": "fmx_s102d_csa_wa_mk1_p95_rtt_ms",
    "wa_to_mk1_csa_jitter_ms": "fmx_s102d_csa_wa_mk1_jitter_ms",
    "sector_goodput_mbps": "fmx_s102d_csa_sector_goodput_mbps",
}
S102E_LTU_TAIL_NUMBERS = {
    "sched_mcs_limit_symbol_end": (1, 80),
    "sched_max_agg_cnt": (1, 32),
    "multi_ack_enable": (0, 1),
    "ldpc_iteration": (1, 32),
    "ofdma_subbands_mask": (0, 255),
    "netdev_budget": (64, 4096),
    "dev_weight": (16, 512),
    "tcp_limit_output_bytes": (16384, 1048576),
    "iptv_jitter_ms": (0.0, 60000.0),
    "gmac0_p95_rtt_ms": (0.0, 60000.0),
}
S102E_LTU_TAIL_BOOLS = {"lite2_ota_sync_staged"}
S102E_LTU_TAIL_METRICS = {
    "sched_mcs_limit_symbol_end": "fmx_s102e_ltu_sched_mcs_limit_symbol_end",
    "sched_max_agg_cnt": "fmx_s102e_ltu_sched_max_agg_cnt",
    "multi_ack_enable": "fmx_s102e_ltu_multi_ack_enable",
    "ldpc_iteration": "fmx_s102e_ltu_ldpc_iteration",
    "ofdma_subbands_mask": "fmx_s102e_ltu_ofdma_subbands_mask",
    "netdev_budget": "fmx_s102e_ltu_netdev_budget",
    "dev_weight": "fmx_s102e_ltu_dev_weight",
    "tcp_limit_output_bytes": "fmx_s102e_ltu_tcp_limit_output_bytes",
    "iptv_jitter_ms": "fmx_s102e_ltu_iptv_jitter_ms",
    "gmac0_p95_rtt_ms": "fmx_s102e_ltu_gmac0_p95_rtt_ms",
}
S103A_UPH_NUMBERS = {
    "swr_limit": (0, 8),
    "ff_mcast_airtime_limit": (0, 100),
    "ptp_xmit": (0, 1),
    "noack_mode": (0, 1),
    "set_multiq": (0, 3),
    "wa_loaded_p95_rtt_ms": (0.0, 60000.0),
    "wa_rtt_jitter_ms": (0.0, 60000.0),
}
S103A_UPH_BOOLS = {"sta_priority_enabled", "swr_written_before_ff_mcast"}
S103A_UPH_METRICS = {
    "swr_limit": "fmx_s103a_uph_swr_limit",
    "ff_mcast_airtime_limit": "fmx_s103a_uph_ff_mcast_airtime_limit",
    "ptp_xmit": "fmx_s103a_uph_ptp_xmit",
    "noack_mode": "fmx_s103a_uph_noack_mode",
    "set_multiq": "fmx_s103a_uph_set_multiq",
    "wa_loaded_p95_rtt_ms": "fmx_s103a_uph_wa_loaded_p95_rtt_ms",
    "wa_rtt_jitter_ms": "fmx_s103a_uph_wa_rtt_jitter_ms",
}
S103D_DIFFSERV4_NUMBERS = {
    "diffserv4_tins_active": (1, 8),
    "overhead_bytes": (0, 128),
    "mpu_bytes": (0, 256),
    "wa_to_mk1_64b_p50_rtt_ms": (0.0, 60000.0),
    "wa_to_mk1_64b_p99_rtt_ms": (0.0, 60000.0),
    "voip_64b_jitter_ms": (0.0, 60000.0),
    "sector_goodput_mbps": (0.0, 500.0),
}
S103D_DIFFSERV4_METRICS = {
    "diffserv4_tins_active": "fmx_s103d_diffserv4_tins_active",
    "overhead_bytes": "fmx_s103d_diffserv4_overhead_bytes",
    "mpu_bytes": "fmx_s103d_diffserv4_mpu_bytes",
    "wa_to_mk1_64b_p50_rtt_ms": "fmx_s103d_wa_mk1_64b_p50_rtt_ms",
    "wa_to_mk1_64b_p99_rtt_ms": "fmx_s103d_wa_mk1_64b_p99_rtt_ms",
    "voip_64b_jitter_ms": "fmx_s103d_voip_64b_jitter_ms",
    "sector_goodput_mbps": "fmx_s103d_sector_goodput_mbps",
}
S103E_PBE_MK1_NUMBERS = {
    "set_multiq": (0, 3),
    "ptp_xmit": (0, 1),
    "pbe242_to_mk1_p50_rtt_ms": (0.0, 60000.0),
    "pbe242_to_mk1_p95_rtt_ms": (0.0, 60000.0),
    "voip_jitter_ms": (0.0, 60000.0),
    "mk1_btest_p95_ms": (0.0, 60000.0),
}
S103E_PBE_MK1_BOOLS = {"l2_loop_guard_whitelisted"}
S103E_PBE_MK1_METRICS = {
    "set_multiq": "fmx_s103e_pbe_mk1_set_multiq",
    "ptp_xmit": "fmx_s103e_pbe_mk1_ptp_xmit",
    "pbe242_to_mk1_p50_rtt_ms": "fmx_s103e_pbe242_mk1_p50_rtt_ms",
    "pbe242_to_mk1_p95_rtt_ms": "fmx_s103e_pbe242_mk1_p95_rtt_ms",
    "voip_jitter_ms": "fmx_s103e_pbe_mk1_voip_jitter_ms",
    "mk1_btest_p95_ms": "fmx_s103e_mk1_btest_p95_ms",
}
S103F_2XC_NUMBERS = {
    "swr_limit": (0, 8),
    "ptp_xmit": (0, 1),
    "ff_cap_rep": (0, 8),
    "umac_max_peers": (1, 256),
    "umac_vow_config": (0, 3),
    "set_multiq": (0, 3),
    "cabq_maxdur": (0, 100),
    "soc_bulk_tcp_mbps": (0.0, 1000.0),
    "loaded_p95_rtt_ms": (0.0, 60000.0),
}
S103F_2XC_METRICS = {
    "swr_limit": "fmx_s103f_2xc_swr_limit",
    "ptp_xmit": "fmx_s103f_2xc_ptp_xmit",
    "ff_cap_rep": "fmx_s103f_2xc_ff_cap_rep",
    "umac_max_peers": "fmx_s103f_2xc_umac_max_peers",
    "umac_vow_config": "fmx_s103f_2xc_umac_vow_config",
    "set_multiq": "fmx_s103f_2xc_set_multiq",
    "cabq_maxdur": "fmx_s103f_2xc_cabq_maxdur",
    "soc_bulk_tcp_mbps": "fmx_s103f_2xc_soc_bulk_tcp_mbps",
    "loaded_p95_rtt_ms": "fmx_s103f_2xc_loaded_p95_rtt_ms",
}


def _need(condition, code):
    if not condition:
        raise ValueError(code)


def _number(value, lo, hi, *, integer=False):
    _need(type(value) in (int, float) and math.isfinite(value) and lo <= value <= hi,
          "INVALID_NUMERIC_MEASUREMENT")
    _need(not integer or type(value) is int, "INTEGER_COUNTER_REQUIRED")
    return value


def _label(value):
    _need(type(value) is str and 0 < len(value) <= 96 and
          all(ord(c) >= 32 and ord(c) != 127 for c in value), "INVALID_BOUNDED_LABEL")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("UTF8_LABEL_REQUIRED") from error
    return value


def _validate_observation(item):
    _need(type(item) is dict, "OBSERVATION_OBJECT_REQUIRED")
    # Copy only this contract's fields; no arbitrary input/credentials enter exposition.
    result = {k: _label(item.get(k)) for k in ("link", "generation", "ap", "peer_mac", "boot_id")}
    _need(result["generation"] in GENERATIONS, "UNKNOWN_HARDWARE_GENERATION")
    _need(re.fullmatch(r"(?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}", result["peer_mac"]),
          "PEER_MAC_REQUIRED")
    result["peer_mac"] = result["peer_mac"].lower()
    for key in ("timestamp_s", "probe_seq", "survey_active_time_ms", "tx_packets", "rx_packets",
                "icmp_sent", "icmp_rcvd"):
        result[key] = _number(item.get(key), 0, 2**53 - 1, integer=key != "timestamp_s")
    _need(result["icmp_sent"] == 5 and result["icmp_rcvd"] <= 5, "FIVE_PROBE_ROUND_REQUIRED")
    _need(type(item.get("l2_associated")) is bool, "ASSOCIATION_BOOL_REQUIRED")
    result["l2_associated"] = item["l2_associated"]
    result["probe_scope"] = item.get("probe_scope", "unverified")
    result["l2_scope"] = item.get("l2_scope", "unverified")
    _need(result["probe_scope"] in {"ap_local", "unverified", "central"} and
          result["l2_scope"] in {"station", "interface", "unverified"}, "INVALID_SOURCE_SCOPE")
    for key, bounds in {"signal_dbm": (-120, 0), "chain0_dbm": (-120, 0),
                        "chain1_dbm": (-120, 0), "avg_rtt_ms": (0, 3600000)}.items():
        if key in item and item[key] is not None:
            result[key] = _number(item[key], *bounds)
    if "avg_rtt_ms" in result:
        _need(result["icmp_rcvd"] > 0, "RTT_WITHOUT_RESPONSES")
    if "ltu" in item:
        _need(result["generation"] == "ltu" and type(item["ltu"]) is dict, "LTU_OBJECT_REQUIRED")
        ltu = {}
        for key, bounds in LTU_NUMBERS.items():
            if key not in item["ltu"] or item["ltu"][key] is None:
                continue
            value = item["ltu"][key]
            if key == "gmax_bd_ever" and type(value) is str:
                _need(re.fullmatch(r"0[xX][0-9a-fA-F]{1,4}", value), "EXPLICIT_HIGH_WATER_HEX_REQUIRED")
                value = int(value, 16)
            ltu[key] = _number(value, *bounds, integer=key not in
                               {"rx_target_power_dbm", "rx_target_power_expected_dbm",
                                "loaded_rtt_ms", "loaded_loss_ratio"})
        for key in LTU_BOOLS:
            if key in item["ltu"]:
                _need(type(item["ltu"][key]) is bool, "LTU_BOOL_REQUIRED")
                ltu[key] = item["ltu"][key]
        if "sched_mcs_ceiling_qam" in ltu:
            _need(ltu["sched_mcs_ceiling_qam"] in {2, 4, 16, 64, 256, 1024, 4096}, "QAM_ORDER_REQUIRED")
        result["ltu"] = ltu
    if "openwrt_v20" in item:
        _need(result["generation"] == "openwrt_wa" and type(item["openwrt_v20"]) is dict,
              "OPENWRT_V20_OBJECT_REQUIRED")
        v20 = {}
        for key, bounds in OPENWRT_V20_NUMBERS.items():
            if key in item["openwrt_v20"] and item["openwrt_v20"][key] is not None:
                v20[key] = _number(item["openwrt_v20"][key], *bounds, integer=True)
        result["openwrt_v20"] = v20
    if "airos8_v6" in item:
        _need(result["generation"] in {"airos8_xc", "airos8_wa"} and type(item["airos8_v6"]) is dict,
              "AIROS8_V6_OBJECT_REQUIRED")
        v6 = {}
        for key, bounds in AIROS8_V6_NUMBERS.items():
            if key in item["airos8_v6"] and item["airos8_v6"][key] is not None:
                v6[key] = _number(item["airos8_v6"][key], *bounds, integer=True)
        for key in AIROS8_V6_BOOLS:
            if key in item["airos8_v6"]:
                _need(type(item["airos8_v6"][key]) is bool, "AIROS8_V6_BOOL_REQUIRED")
                v6[key] = item["airos8_v6"][key]
        result["airos8_v6"] = v6
    if "airos6_xw" in item:
        _need(result["generation"] == "airos6_xw" and type(item["airos6_xw"]) is dict,
              "AIROS6_XW_OBJECT_REQUIRED")
        xw = {}
        for key, bounds in AIROS6_XW_NUMBERS.items():
            if key in item["airos6_xw"] and item["airos6_xw"][key] is not None:
                xw[key] = _number(item["airos6_xw"][key], *bounds,
                                  integer=key in {"netdev_budget", "txqueuelen"})
        for key in AIROS6_XW_BOOLS:
            if key in item["airos6_xw"]:
                _need(type(item["airos6_xw"][key]) is bool, "AIROS6_XW_BOOL_REQUIRED")
                xw[key] = item["airos6_xw"][key]
        result["airos6_xw"] = xw
    if "openwrt_v23" in item:
        _need(result["generation"] == "openwrt_wa" and type(item["openwrt_v23"]) is dict,
              "OPENWRT_V23_OBJECT_REQUIRED")
        v23 = {}
        for key, bounds in OPENWRT_V23_NUMBERS.items():
            if key in item["openwrt_v23"] and item["openwrt_v23"][key] is not None:
                v23[key] = _number(
                    item["openwrt_v23"][key], *bounds,
                    integer=key not in {"xc_auto_heal_recovery_ms", "survivor_wa_to_mk1_p95_rtt_ms"}
                )
        for key in OPENWRT_V23_BOOLS:
            if key in item["openwrt_v23"]:
                _need(type(item["openwrt_v23"][key]) is bool, "OPENWRT_V23_BOOL_REQUIRED")
                v23[key] = item["openwrt_v23"][key]
        result["openwrt_v23"] = v23
    if "vlan107_mk1" in item:
        _need(result["generation"] == "openwrt_wa" and type(item["vlan107_mk1"]) is dict,
              "VLAN107_MK1_OBJECT_REQUIRED")
        mk1 = {}
        for key, bounds in VLAN107_MK1_NUMBERS.items():
            if key in item["vlan107_mk1"] and item["vlan107_mk1"][key] is not None:
                mk1[key] = _number(item["vlan107_mk1"][key], *bounds)
        for key in VLAN107_MK1_BOOLS:
            if key in item["vlan107_mk1"]:
                _need(type(item["vlan107_mk1"][key]) is bool, "VLAN107_MK1_BOOL_REQUIRED")
                mk1[key] = item["vlan107_mk1"][key]
        result["vlan107_mk1"] = mk1
    if "ltu_superframe" in item:
        _need(result["generation"] == "ltu" and type(item["ltu_superframe"]) is dict,
              "LTU_SUPERFRAME_OBJECT_REQUIRED")
        sf = {}
        for key, bounds in LTU_SUPERFRAME_NUMBERS.items():
            if key in item["ltu_superframe"] and item["ltu_superframe"][key] is not None:
                sf[key] = _number(
                    item["ltu_superframe"][key], *bounds,
                    integer=key != "soc_tcp_goodput_mbps"
                )
        for key in LTU_SUPERFRAME_BOOLS:
            if key in item["ltu_superframe"]:
                _need(type(item["ltu_superframe"][key]) is bool, "LTU_SUPERFRAME_BOOL_REQUIRED")
                sf[key] = item["ltu_superframe"][key]
        result["ltu_superframe"] = sf
    if "r2ac_2xc" in item:
        _need(result["generation"] == "airos8_xc" and type(item["r2ac_2xc"]) is dict,
              "R2AC_2XC_OBJECT_REQUIRED")
        r2ac = {}
        for key, bounds in R2AC_2XC_NUMBERS.items():
            if key in item["r2ac_2xc"] and item["r2ac_2xc"][key] is not None:
                r2ac[key] = _number(
                    item["r2ac_2xc"][key], *bounds,
                    integer=key in {"set_multiq", "vow_extstats"}
                )
        for key in R2AC_2XC_BOOLS:
            if key in item["r2ac_2xc"]:
                _need(type(item["r2ac_2xc"][key]) is bool, "R2AC_2XC_BOOL_REQUIRED")
                r2ac[key] = item["r2ac_2xc"][key]
        result["r2ac_2xc"] = r2ac
    if "stage102d_csa" in item:
        _need(result["generation"] == "openwrt_wa" and type(item["stage102d_csa"]) is dict,
              "S102D_CSA_OBJECT_REQUIRED")
        s102d = {}
        for key, bounds in S102D_CSA_NUMBERS.items():
            if key in item["stage102d_csa"] and item["stage102d_csa"][key] is not None:
                s102d[key] = _number(
                    item["stage102d_csa"][key], *bounds,
                    integer=key in {"csa_bcn_count", "station_retention_count"}
                )
        for key in S102D_CSA_BOOLS:
            if key in item["stage102d_csa"]:
                _need(type(item["stage102d_csa"][key]) is bool, "S102D_CSA_BOOL_REQUIRED")
                s102d[key] = item["stage102d_csa"][key]
        result["stage102d_csa"] = s102d
    if "stage102e_ltu_tail_guard" in item:
        _need(result["generation"] == "ltu" and type(item["stage102e_ltu_tail_guard"]) is dict,
              "S102E_LTU_TAIL_OBJECT_REQUIRED")
        s102e = {}
        for key, bounds in S102E_LTU_TAIL_NUMBERS.items():
            if key in item["stage102e_ltu_tail_guard"] and item["stage102e_ltu_tail_guard"][key] is not None:
                s102e[key] = _number(
                    item["stage102e_ltu_tail_guard"][key], *bounds,
                    integer=key not in {"iptv_jitter_ms", "gmac0_p95_rtt_ms"}
                )
        for key in S102E_LTU_TAIL_BOOLS:
            if key in item["stage102e_ltu_tail_guard"]:
                _need(type(item["stage102e_ltu_tail_guard"][key]) is bool, "S102E_LTU_TAIL_BOOL_REQUIRED")
                s102e[key] = item["stage102e_ltu_tail_guard"][key]
        result["stage102e_ltu_tail_guard"] = s102e
    if "stage103a_uph_knobs" in item:
        _need(result["generation"] in {"airos8_xc", "airos8_wa", "openwrt_wa"} and type(item["stage103a_uph_knobs"]) is dict,
              "S103A_UPH_OBJECT_REQUIRED")
        s103a = {}
        for key, bounds in S103A_UPH_NUMBERS.items():
            if key in item["stage103a_uph_knobs"] and item["stage103a_uph_knobs"][key] is not None:
                s103a[key] = _number(
                    item["stage103a_uph_knobs"][key], *bounds,
                    integer=key not in {"wa_loaded_p95_rtt_ms", "wa_rtt_jitter_ms"}
                )
        for key in S103A_UPH_BOOLS:
            if key in item["stage103a_uph_knobs"]:
                _need(type(item["stage103a_uph_knobs"][key]) is bool, "S103A_UPH_BOOL_REQUIRED")
                s103a[key] = item["stage103a_uph_knobs"][key]
        result["stage103a_uph_knobs"] = s103a
    if "stage103d_diffserv4_rfc2544" in item:
        _need(result["generation"] == "openwrt_wa" and type(item["stage103d_diffserv4_rfc2544"]) is dict,
              "S103D_DIFFSERV4_OBJECT_REQUIRED")
        s103d = {}
        for key, bounds in S103D_DIFFSERV4_NUMBERS.items():
            if key in item["stage103d_diffserv4_rfc2544"] and item["stage103d_diffserv4_rfc2544"][key] is not None:
                s103d[key] = _number(
                    item["stage103d_diffserv4_rfc2544"][key], *bounds,
                    integer=key in {"diffserv4_tins_active", "overhead_bytes", "mpu_bytes"}
                )
        result["stage103d_diffserv4_rfc2544"] = s103d
    if "stage103e_pbe5ac_mk1_e2e" in item:
        _need(result["generation"] in {"airos8_wa", "openwrt_wa"} and type(item["stage103e_pbe5ac_mk1_e2e"]) is dict,
              "S103E_PBE_MK1_OBJECT_REQUIRED")
        s103e = {}
        for key, bounds in S103E_PBE_MK1_NUMBERS.items():
            if key in item["stage103e_pbe5ac_mk1_e2e"] and item["stage103e_pbe5ac_mk1_e2e"][key] is not None:
                s103e[key] = _number(
                    item["stage103e_pbe5ac_mk1_e2e"][key], *bounds,
                    integer=key in {"set_multiq", "ptp_xmit"}
                )
        for key in S103E_PBE_MK1_BOOLS:
            if key in item["stage103e_pbe5ac_mk1_e2e"]:
                _need(type(item["stage103e_pbe5ac_mk1_e2e"][key]) is bool, "S103E_PBE_MK1_BOOL_REQUIRED")
                s103e[key] = item["stage103e_pbe5ac_mk1_e2e"][key]
        result["stage103e_pbe5ac_mk1_e2e"] = s103e
    if "stage103f_r2ac_2xc_multiq" in item:
        _need(result["generation"] == "airos8_xc" and type(item["stage103f_r2ac_2xc_multiq"]) is dict,
              "S103F_2XC_OBJECT_REQUIRED")
        s103f = {}
        for key, bounds in S103F_2XC_NUMBERS.items():
            if key in item["stage103f_r2ac_2xc_multiq"] and item["stage103f_r2ac_2xc_multiq"][key] is not None:
                s103f[key] = _number(
                    item["stage103f_r2ac_2xc_multiq"][key], *bounds,
                    integer=key not in {"soc_bulk_tcp_mbps", "loaded_p95_rtt_ms"}
                )
        result["stage103f_r2ac_2xc_multiq"] = s103f
    return result


def adapt_stage61_payload(payload):
    """Pure adapter. No import of Stage61A or its vault/SSH/autopilot dependencies.

    The old producer lacks boot identity/scope attestation, combines interface
    traffic on R2AC, hardcodes R2AC/LTU RSSI and has ambiguous maxBD parsing.
    Keep those links unqualified and omit synthetic/misinterpretable metrics.
    """
    _need(payload.get("stage") == "61A", "SCHEMA_VERSION_REQUIRED")
    mapping = {"OpenWrt_24.10.4_WA": "openwrt_wa", "airOS8_XC_AirPrism": "airos8_xc",
               "airOS8_WA": "airos8_wa", "airOS8_2XC_AirPrism": "airos8_xc",
               "airOS6_XW_AR934x": "airos6_xw", "LTU_v2.3.1_EAB": "ltu"}
    batches = []
    for key in ("round1", "round2"):
        row = payload.get(key)
        _need(type(row) is dict and type(row.get("samples")) is dict and
              type(row.get("link_meta")) is dict, "STAGE61_ROUNDS_REQUIRED")
        observations = []
        for link, sample in row["samples"].items():
            _need(type(sample) is dict, "STAGE61_SAMPLE_REQUIRED")
            meta = row["link_meta"].get(link, {})
            _need(type(meta) is dict, "STAGE61_META_REQUIRED")
            _need(meta.get("gen") in mapping, "UNKNOWN_STAGE61_GENERATION")
            obs = {**sample, "link": link, "generation": mapping[meta["gen"]],
                   "ap": "stage61-unverified", "peer_mac": meta.get("mac"),
                   "boot_id": "legacy-unverified", "probe_scope": "unverified", "l2_scope": "unverified"}
            obs.pop("signal_dbm", None)
            if obs["generation"] == "ltu":
                ltu_row = row.get("ltu_lite_ota", {})
                _need(type(ltu_row) is dict, "STAGE61_LTU_OBJECT_REQUIRED")
                ame = ltu_row.get("ame_knobs", {})
                _need(type(ame) is dict, "STAGE61_AME_OBJECT_REQUIRED")
                obs["ltu"] = {new: ame[old] for old, new in
                              (("autoMcsCeiling", "auto_mcs_ceiling"), ("pb_boost", "pb_boost_mode")) if old in ame}
            observations.append(obs)
        batches.append({"schema_version": 1, "observations": observations})
    return batches


@dataclass
class LinkState:
    sample: dict | None = None
    watermark: dict | None = None
    state: str = "UNKNOWN"
    reason: str = "BASELINE_REQUIRED"
    failures: int = 0
    progress: int | None = None
    telemetry_valid: bool = False
    needs_baseline: bool = True
    irq_delta: tuple | None = None


class TelemetryExporter:
    def __init__(self, *, max_age_seconds=150, min_round_spacing_seconds=45,
                 max_round_gap_seconds=90, expected_links=(), clock=time.time):
        _number(max_age_seconds, 1, 150)
        _number(min_round_spacing_seconds, 1, 90)
        _number(max_round_gap_seconds, min_round_spacing_seconds, 150)
        self.max_age = max_age_seconds
        self.min_spacing = min_round_spacing_seconds
        self.max_gap = max_round_gap_seconds
        self.clock = clock
        _need(not isinstance(expected_links, str), "EXPECTED_LINK_LIST_REQUIRED")
        self.links = {_label(k): LinkState() for k in expected_links}
        _need(len(self.links) <= MAX_LINKS, "LINK_LIMIT")
        self.input_valid = False
        self.last_success = 0.0
        self.last_error = "NO_INPUT"
        self.rejected_inputs = 0
        self.lock = threading.RLock()

    @staticmethod
    def _qualified(sample):
        return sample["probe_scope"] == "ap_local" and sample["l2_scope"] == "station" and sample["boot_id"] != "legacy-unverified"

    def _invalidate(self, reason):
        self.input_valid = False
        self.last_error = reason
        self.rejected_inputs += 1
        for state in self.links.values():
            state.state = "UNKNOWN"; state.reason = reason
            state.failures = 0; state.progress = None; state.telemetry_valid = False
            state.needs_baseline = True; state.irq_delta = None

    def ingest(self, payload, now=None):
        now = self.clock() if now is None else now
        with self.lock:
            try:
                _number(now, 0, 2**53 - 1)
                _need(type(payload) is dict, "INPUT_OBJECT_REQUIRED")
                batches = adapt_stage61_payload(payload) if payload.get("stage") == "61A" else [payload]
                validated = []
                for batch in batches:
                    _need(type(batch.get("schema_version")) is int and batch["schema_version"] == 1,
                          "SCHEMA_VERSION_REQUIRED")
                    observations = batch.get("observations")
                    _need(type(observations) is list and 0 < len(observations) <= MAX_LINKS, "NONEMPTY_BOUNDED_OBSERVATIONS_REQUIRED")
                    rows = [_validate_observation(x) for x in observations]
                    _need(len({x["link"] for x in rows}) == len(rows), "DUPLICATE_LINK")
                    validated.append(rows)
                _need(len(set(self.links) | {x["link"] for rows in validated for x in rows}) <= MAX_LINKS, "LINK_LIMIT")
            except (ValueError, TypeError, KeyError, OverflowError, RecursionError):
                self._invalidate("INVALID_INPUT")
                return False
            for rows in validated:
                present = {r["link"] for r in rows}
                for key, state in self.links.items():
                    if key not in present:
                        state.state = "UNKNOWN"; state.reason = "MISSING_LINK"
                        state.failures = 0; state.telemetry_valid = False; state.needs_baseline = True
                        state.progress = None; state.irq_delta = None
                for row in rows:
                    state = self.links.setdefault(row["link"], LinkState())
                    self._advance(state, row, now)
            self.input_valid = True
            self.last_error = ""
            # Producer measurement time, not file mtime or HTTP scrape time.
            self.last_success = max(x["timestamp_s"] for x in validated[-1])
            return True

    def _advance(self, state, row, now):
        previous = state.watermark
        if previous == row and not state.needs_baseline:
            return  # File polling/scraping must not manufacture probe rounds.
        prior_failures = state.failures
        state.state = "UNKNOWN"; state.reason = "BASELINE_REQUIRED"
        state.failures = 0; state.progress = None; state.irq_delta = None; state.telemetry_valid = False
        identity = ("generation", "ap", "peer_mac", "boot_id", "probe_scope", "l2_scope")
        same_identity = previous is not None and all(previous[k] == row[k] for k in identity)
        if previous is not None and (row["timestamp_s"] < previous["timestamp_s"] or
                (not same_identity and row["timestamp_s"] <= previous["timestamp_s"]) or
                (same_identity and row["probe_seq"] < previous["probe_seq"])):
            # Keep the last accepted watermark. An older pair cannot replay UP.
            state.reason = "OBSERVATION_ROLLBACK"; state.needs_baseline = True
            return
        if same_identity and previous != row and (row["probe_seq"] == previous["probe_seq"] or
                                                   row["timestamp_s"] == previous["timestamp_s"]):
            state.reason = "REPLAYED_ROUND_CHANGED"; state.needs_baseline = True
            return
        state.sample = row
        if not 0 <= now - row["timestamp_s"] <= self.max_age:
            state.reason = "STALE_OR_FUTURE_OBSERVATION"; state.needs_baseline = True
            return
        if not self._qualified(row):
            state.reason = "UNQUALIFIED_SOURCE"; state.needs_baseline = True
            return
        # Rejected future/unqualified observations may describe UNKNOWN labels,
        # but can never advance the accepted epoch's anti-replay watermark.
        state.watermark = row
        if previous is None or state.needs_baseline:
            state.needs_baseline = False
            return
        if not same_identity:
            state.reason = "IDENTITY_OR_BOOT_CHANGED"
            return
        if (row["probe_seq"] <= previous["probe_seq"] or row["timestamp_s"] <= previous["timestamp_s"] or
                row["survey_active_time_ms"] <= previous["survey_active_time_ms"] or
                row["tx_packets"] < previous["tx_packets"] or row["rx_packets"] < previous["rx_packets"]):
            state.reason = "NONMONOTONIC_OR_FROZEN_COUNTERS"
            return
        spacing = row["timestamp_s"] - previous["timestamp_s"]
        if row["probe_seq"] != previous["probe_seq"] + 1 or not self.min_spacing <= spacing <= self.max_gap:
            state.reason = "ROUND_GAP_OR_SPACING_INVALID"
            return
        state.telemetry_valid = True
        state.progress = row["tx_packets"] - previous["tx_packets"] + row["rx_packets"] - previous["rx_packets"]
        if row["icmp_rcvd"] > 0 or (row["l2_associated"] and state.progress > 0):
            state.state = "UP"; state.reason = "RESPONSES_OR_STATION_PROGRESS"
        elif state.progress == 0:
            state.failures = prior_failures + 1
            state.state = "DOWN" if state.failures >= 2 else "PENDING"
            state.reason = "CONFIRMED_TWO_ROUNDS" if state.failures >= 2 else "FIRST_FAILED_ROUND"
        else:
            state.state = "UNKNOWN"; state.reason = "ASSOCIATION_COUNTER_CONFLICT"
            state.telemetry_valid = False
        old, new = previous.get("ltu", {}), row.get("ltu", {})
        keys = ("irq63_cpu0_total", "irq63_cpu1_total")
        if all(k in old and k in new and new[k] >= old[k] for k in keys):
            state.irq_delta = tuple(new[k] - old[k] for k in keys)

    def refresh_file(self, path, now=None):
        try:
            raw_path = str(path).replace("\\", "/")
            _need(raw_path and not raw_path.startswith("//") and "\x00" not in raw_path and
                  (not re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", raw_path) or
                   re.match(r"^[A-Za-z]:/", raw_path)), "LOCAL_INPUT_PATH_REQUIRED")
            path = Path(path)
            _need(path.stem.split(".")[0].upper() not in
                  {"CON", "PRN", "AUX", "NUL", *[f"COM{i}" for i in range(1, 10)],
                   *[f"LPT{i}" for i in range(1, 10)]}, "NONDEVICE_INPUT_REQUIRED")
            for part in (path, *path.absolute().parents):
                _need(not part.is_symlink() and not (getattr(part.lstat(), "st_file_attributes", 0) & 0x400),
                      "REPARSE_INPUT_REJECTED")
            _need(path.is_file() and path.stat().st_size <= MAX_INPUT_BYTES, "BOUNDED_LOCAL_FILE_REQUIRED")
            with path.open("rb") as handle:
                raw = handle.read(MAX_INPUT_BYTES + 1)
            _need(len(raw) <= MAX_INPUT_BYTES, "BOUNDED_LOCAL_FILE_REQUIRED")
            def pairs(items):
                result = {}
                for k, value in items:
                    _need(k not in result, "DUPLICATE_JSON_KEY")
                    result[k] = value
                return result
            def bad_constant(_):
                raise ValueError("FINITE_JSON_REQUIRED")
            payload = json.loads(raw, object_pairs_hook=pairs, parse_constant=bad_constant)
        except (OSError, ValueError, TypeError, RecursionError):
            with self.lock:
                self._invalidate("INPUT_UNREADABLE_OR_INVALID_JSON")
            return False
        return self.ingest(payload, now=now)

    def _effective(self, state, now):
        if not self.input_valid or state.sample is None:
            return "UNKNOWN", False, state.reason
        if not 0 <= now - state.sample["timestamp_s"] <= self.max_age:
            return "UNKNOWN", False, "STALE_OR_FUTURE_OBSERVATION"
        return state.state, state.telemetry_valid, state.reason

    def health(self, now=None):
        now = self.clock() if now is None else now
        with self.lock:
            links = {key: {"state": self._effective(state, now)[0], "reason": self._effective(state, now)[2]}
                     for key, state in self.links.items()}
            return {"ready": self.input_valid and bool(links) and all(x["state"] == "UP" for x in links.values()),
                    "input_valid": self.input_valid, "links": links, "error": self.last_error}

    def render(self, openmetrics=False, now=None):
        now = self.clock() if now is None else now
        with self.lock:
            metrics = {}
            def add(name, value, labels=None, kind="gauge", help_text=None):
                _need(math.isfinite(value), "NONFINITE_EXPOSITION_REJECTED")
                if name not in metrics:
                    metrics[name] = (kind, help_text or name.replace("_", " "), [])
                lab = "" if not labels else "{" + ",".join(
                    k + '="' + str(v).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'
                    for k, v in sorted(labels.items())) + "}"
                metrics[name][2].append(name + lab + " " + format(value, ".17g"))
            add("fmx_exporter_input_valid", int(self.input_valid))
            add("fmx_exporter_last_success_timestamp_seconds", self.last_success)
            # Gauge deliberately: process restart is not an observed radio counter reset.
            add("fmx_exporter_rejected_inputs", self.rejected_inputs)
            for link, state in sorted(self.links.items()):
                sample = state.sample or {}
                labels = {"link": link, "generation": sample.get("generation", "unknown"),
                          "ap": sample.get("ap", "unknown"), "peer_mac": sample.get("peer_mac", "unknown")}
                effective, valid, _ = self._effective(state, now)
                qualified = bool(sample and self._qualified(sample))
                for name, value in {
                    "fmx_rf_state": STATE_VALUES[effective], "fmx_rf_telemetry_valid": int(valid),
                    "fmx_rf_source_qualified": int(qualified),
                    "fmx_rf_observation_timestamp_seconds": sample.get("timestamp_s", 0),
                    "fmx_rf_consecutive_failures": state.failures if valid else 0,
                    "fmx_rf_kuma_push_allowed": int(effective == "UP" and valid and qualified),
                }.items():
                    add(name, value, labels)
                if state.progress is not None and valid:
                    add("fmx_rf_packet_progress", state.progress, labels)
                if sample:
                    add("fmx_rf_last_round_loss_ratio", (5 - sample["icmp_rcvd"]) / 5, labels)
                if not valid:
                    if sample.get("generation") == "ltu":
                        self._render_ltu({}, state, labels, add, False)
                        self._render_ltu_superframe({}, labels, add, False)
                        self._render_s102e_ltu_tail_guard({}, labels, add, False)
                    elif sample.get("generation") == "openwrt_wa":
                        self._render_openwrt_v20({}, labels, add, False)
                        self._render_openwrt_v23({}, labels, add, False)
                        self._render_vlan107_mk1({}, labels, add, False)
                        self._render_s102d_csa({}, labels, add, False)
                        self._render_s103a_uph({}, labels, add, False)
                        self._render_s103d_diffserv4({}, labels, add, False)
                        self._render_s103e_pbe_mk1({}, labels, add, False)
                    elif sample.get("generation") in {"airos8_xc", "airos8_wa"}:
                        self._render_airos8_v6({}, labels, add, False)
                        self._render_s103a_uph({}, labels, add, False)
                        if sample.get("generation") == "airos8_xc":
                            self._render_r2ac_2xc({}, labels, add, False)
                            self._render_s103f_2xc({}, labels, add, False)
                        else:
                            self._render_s103e_pbe_mk1({}, labels, add, False)
                    elif sample.get("generation") == "airos6_xw":
                        self._render_airos6_xw({}, labels, add, False)
                    continue
                if "signal_dbm" in sample:
                    add("fmx_station_signal_dbm", sample["signal_dbm"], labels)
                if "chain0_dbm" in sample and "chain1_dbm" in sample:
                    add("fmx_station_chain_delta_db", abs(sample["chain0_dbm"] - sample["chain1_dbm"]), labels)
                if "avg_rtt_ms" in sample:
                    add("fmx_station_rtt_seconds", sample["avg_rtt_ms"] / 1000, labels)
                if sample.get("generation") == "ltu":
                    self._render_ltu(sample.get("ltu", {}), state, labels, add, valid)
                    self._render_ltu_superframe(sample.get("ltu_superframe", {}), labels, add, valid)
                    self._render_s102e_ltu_tail_guard(sample.get("stage102e_ltu_tail_guard", {}), labels, add, valid)
                elif sample.get("generation") == "openwrt_wa":
                    self._render_openwrt_v20(sample.get("openwrt_v20", {}), labels, add, valid)
                    self._render_openwrt_v23(sample.get("openwrt_v23", {}), labels, add, valid)
                    self._render_vlan107_mk1(sample.get("vlan107_mk1", {}), labels, add, valid)
                    self._render_s102d_csa(sample.get("stage102d_csa", {}), labels, add, valid)
                    self._render_s103a_uph(sample.get("stage103a_uph_knobs", {}), labels, add, valid)
                    self._render_s103d_diffserv4(sample.get("stage103d_diffserv4_rfc2544", {}), labels, add, valid)
                    self._render_s103e_pbe_mk1(sample.get("stage103e_pbe5ac_mk1_e2e", {}), labels, add, valid)
                elif sample.get("generation") in {"airos8_xc", "airos8_wa"}:
                    self._render_airos8_v6(sample.get("airos8_v6", {}), labels, add, valid)
                    self._render_s103a_uph(sample.get("stage103a_uph_knobs", {}), labels, add, valid)
                    if sample.get("generation") == "airos8_xc":
                        self._render_r2ac_2xc(sample.get("r2ac_2xc", {}), labels, add, valid)
                        self._render_s103f_2xc(sample.get("stage103f_r2ac_2xc_multiq", {}), labels, add, valid)
                    else:
                        self._render_s103e_pbe_mk1(sample.get("stage103e_pbe5ac_mk1_e2e", {}), labels, add, valid)
                elif sample.get("generation") == "airos6_xw":
                    self._render_airos6_xw(sample.get("airos6_xw", {}), labels, add, valid)
            lines = []
            for name, (kind, help_text, samples) in sorted(metrics.items()):
                family = name[:-6] if openmetrics and kind == "counter" and name.endswith("_total") else name
                lines.extend([f"# HELP {family} {help_text}", f"# TYPE {family} {kind}", *samples])
            if openmetrics:
                lines.append("# EOF")
            return "\n".join(lines) + "\n"

    @staticmethod
    def _render_openwrt_v20(v20, labels, add, valid):
        for key, metric in OPENWRT_V20_METRICS.items():
            if valid and key in v20:
                add(metric, float(v20[key]), labels)
        available = valid and all(k in v20 for k in OPENWRT_V20_NUMBERS)
        add("fmx_openwrt_v20_evidence_available", int(available), labels)
        if available:
            compliant = (
                v20["bql_limit_min"] == 4542
                and v20["bql_limit_max"] == 42392
                and v20["bql_hold_time_ms"] == 800
                and v20["dev_weight_tx_bias"] == 2
                and v20["fq_quantum"] in (1514, 4542)
                and v20["fq_memory_limit"] == 4194304
                and v20["hostapd_oom_score_adj"] == -900
                and v20["aql_threshold"] == 5000
                and v20["tsq_limit_bytes"] == 98304
                and v20["tx_queue_len"] == 256
            )
            add("fmx_openwrt_v20_profile_compliant", int(compliant), labels)

    @staticmethod
    def _render_airos8_v6(v6, labels, add, valid):
        for key, metric in AIROS8_V6_METRICS.items():
            if valid and key in v6:
                add(metric, float(v6[key]), labels)
        available = (
            valid
            and all(k in v6 for k in AIROS8_V6_NUMBERS)
            and all(k in v6 for k in AIROS8_V6_BOOLS)
        )
        add("fmx_airos8_v6_evidence_available", int(available), labels)
        if available:
            compliant = (
                v6["ptp_xmit"] == 1
                and v6["daprot"] == 2
                and v6["ff_mcast_airtime_limit"] == 5
                and v6["daprot_written_before_ff_mcast"] is True
                and v6["cabq_maxdur"] == 20
                and v6["syncflex"] == 0
                and v6["netdev_budget"] == 800
                and v6["tsq_limit_bytes"] in (98304, 131072)
                and v6["set_multiq"] == 1
                and v6["enable_tx_tcp_cksum"] == 1
            )
            add("fmx_airos8_v6_ptp_profile_compliant", int(compliant), labels)

    @staticmethod
    def _render_airos6_xw(xw, labels, add, valid):
        for key, metric in AIROS6_XW_METRICS.items():
            if valid and key in xw:
                add(metric, float(xw[key]), labels)
        available = (
            valid
            and all(k in xw for k in ("tx_phy_mbps", "expected_min_tx_phy_mbps"))
            and all(k in xw for k in AIROS6_XW_BOOLS)
        )
        add("fmx_xw_mcs0_warmup_evidence_available", int(available), labels)
        if available:
            cold_rate = xw["under_load"] and (
                (not xw["warmup_completed"])
                or xw["tx_phy_mbps"] < xw["expected_min_tx_phy_mbps"]
            )
            add("fmx_xw_mcs0_cold_rate_condition", int(cold_rate), labels)

    @staticmethod
    def _render_openwrt_v23(v23, labels, add, valid):
        for key, metric in OPENWRT_V23_METRICS.items():
            if valid and key in v23:
                add(metric, float(v23[key]), labels)
        if valid and "healer_daemon_active" in v23:
            add("fmx_openwrt_v23_wds_healer_active", int(v23["healer_daemon_active"]), labels)
        available = (
            valid
            and all(k in v23 for k in OPENWRT_V23_NUMBERS)
            and all(k in v23 for k in OPENWRT_V23_BOOLS)
        )
        add("fmx_openwrt_v23_evidence_available", int(available), labels)
        if available:
            compliant = (
                v23["healer_daemon_active"] is True
                and v23["xc_auto_heal_recovery_ms"] <= 1500.0
                and v23["survivor_wa_to_mk1_p95_rtt_ms"] <= 10.0
                and v23["vlan107_eth0_107_tx_queue_len"] == 64
                and v23["aql_be_low_us"] == 1200
                and v23["aql_be_high_us"] == 2400
                and v23["aql_threshold"] == 4000
            )
            add("fmx_openwrt_v23_profile_compliant", int(compliant), labels)

    @staticmethod
    def _render_vlan107_mk1(mk1, labels, add, valid):
        for key, metric in VLAN107_MK1_METRICS.items():
            if valid and key in mk1:
                add(metric, float(mk1[key]), labels)
        available = (
            valid
            and all(k in mk1 for k in VLAN107_MK1_NUMBERS)
            and all(k in mk1 for k in VLAN107_MK1_BOOLS)
        )
        add("fmx_vlan107_mk1_evidence_available", int(available), labels)
        if available:
            compliant = (
                mk1["dscp_ef_cs4_preserved"] is True
                and mk1["qos_egress_ingress_map_active"] is True
                and mk1["btest_port_2000_reachable"] is True
                and mk1["cpe_to_mk1_e2e_p95_rtt_ms"] <= 12.0
            )
            add("fmx_vlan107_mk1_dscp_qos_compliant", int(compliant), labels)

    @staticmethod
    def _render_ltu_superframe(sf, labels, add, valid):
        for key, metric in LTU_SUPERFRAME_METRICS.items():
            if valid and key in sf:
                add(metric, float(sf[key]), labels)
        available = (
            valid
            and all(k in sf for k in LTU_SUPERFRAME_NUMBERS)
            and all(k in sf for k in LTU_SUPERFRAME_BOOLS)
        )
        add("fmx_ltu_superframe_smp_evidence_available", int(available), labels)
        if available:
            compliant = (
                sf["superframe_total_symbols"] == 80
                and sf["superframe_dl_symbols"] == 61
                and sf["superframe_ul_symbols"] == 19
                and sf["scheduler_giveup_total"] == 0
                and sf["symbol_giveup_total"] == 0
                and sf["smp_irq_isolated"] is True
            )
            add("fmx_ltu_superframe_smp_compliant", int(compliant), labels)

    @staticmethod
    def _render_r2ac_2xc(r2ac, labels, add, valid):
        for key, metric in R2AC_2XC_METRICS.items():
            if valid and key in r2ac:
                add(metric, float(r2ac[key]), labels)
        available = (
            valid
            and all(k in r2ac for k in R2AC_2XC_NUMBERS)
            and all(k in r2ac for k in R2AC_2XC_BOOLS)
        )
        add("fmx_r2ac_2xc_evidence_available", int(available), labels)
        if available:
            compliant = (
                r2ac["airview_irq2_per_sec"] == 0.0
                and r2ac["hs_uart_irq22_gps_stopped"] is True
                and r2ac["ath_pktlog_unloaded"] is True
                and r2ac["set_multiq"] == 3
                and r2ac["vow_extstats"] == 0
            )
            add("fmx_r2ac_2xc_profile_compliant", int(compliant), labels)

    @staticmethod
    def _render_s102d_csa(s102d, labels, add, valid):
        for key, metric in S102D_CSA_METRICS.items():
            if valid and key in s102d:
                add(metric, float(s102d[key]), labels)
        if valid and "csa_block_tx" in s102d:
            add("fmx_s102d_csa_block_tx", int(s102d["csa_block_tx"]), labels)
        available = (
            valid
            and all(k in s102d for k in S102D_CSA_NUMBERS)
            and all(k in s102d for k in S102D_CSA_BOOLS)
        )
        add("fmx_s102d_csa_evidence_available", int(available), labels)
        if available:
            compliant = (
                s102d["csa_bcn_count"] == 10
                and s102d["csa_block_tx"] is False
                and s102d["station_retention_count"] >= 3
                and s102d["wa_to_mk1_csa_p95_rtt_ms"] <= 12.0
                and s102d["wa_to_mk1_csa_jitter_ms"] <= 4.5
            )
            add("fmx_s102d_csa_profile_compliant", int(compliant), labels)

    @staticmethod
    def _render_s102e_ltu_tail_guard(s102e, labels, add, valid):
        for key, metric in S102E_LTU_TAIL_METRICS.items():
            if valid and key in s102e:
                add(metric, float(s102e[key]), labels)
        if valid and "lite2_ota_sync_staged" in s102e:
            add("fmx_s102e_ltu_lite2_ota_sync_staged", int(s102e["lite2_ota_sync_staged"]), labels)
        available = (
            valid
            and all(k in s102e for k in S102E_LTU_TAIL_NUMBERS)
            and all(k in s102e for k in S102E_LTU_TAIL_BOOLS)
        )
        add("fmx_s102e_ltu_tail_guard_evidence_available", int(available), labels)
        if available:
            compliant = (
                s102e["sched_mcs_limit_symbol_end"] == 59
                and s102e["sched_max_agg_cnt"] == 8
                and s102e["multi_ack_enable"] == 1
                and s102e["ldpc_iteration"] == 12
                and s102e["ofdma_subbands_mask"] == 255
                and s102e["netdev_budget"] == 640
                and s102e["dev_weight"] == 80
                and s102e["tcp_limit_output_bytes"] in (65536, 196608)
                and s102e["iptv_jitter_ms"] <= 0.6
                and s102e["gmac0_p95_rtt_ms"] <= 7.5
                and s102e["lite2_ota_sync_staged"] is True
            )
            add("fmx_s102e_ltu_tail_guard_compliant", int(compliant), labels)

    @staticmethod
    def _render_s103a_uph(s103a, labels, add, valid):
        for key, metric in S103A_UPH_METRICS.items():
            if valid and key in s103a:
                add(metric, float(s103a[key]), labels)
        if valid and "sta_priority_enabled" in s103a:
            add("fmx_s103a_uph_sta_priority_enabled", int(s103a["sta_priority_enabled"]), labels)
        available = (
            valid
            and all(k in s103a for k in S103A_UPH_NUMBERS)
            and all(k in s103a for k in S103A_UPH_BOOLS)
        )
        add("fmx_s103a_uph_evidence_available", int(available), labels)
        if available:
            compliant = (
                s103a["swr_limit"] in (2, 3)
                and s103a["ff_mcast_airtime_limit"] == 5
                and s103a["sta_priority_enabled"] is True
                and s103a["ptp_xmit"] == 0
                and s103a["noack_mode"] == 0
                and s103a["set_multiq"] == 3
                and s103a["swr_written_before_ff_mcast"] is True
                and s103a["wa_loaded_p95_rtt_ms"] <= 45.0
                and s103a["wa_rtt_jitter_ms"] <= 12.0
            )
            add("fmx_s103a_uph_profile_compliant", int(compliant), labels)

    @staticmethod
    def _render_s103d_diffserv4(s103d, labels, add, valid):
        for key, metric in S103D_DIFFSERV4_METRICS.items():
            if valid and key in s103d:
                add(metric, float(s103d[key]), labels)
        available = valid and all(k in s103d for k in S103D_DIFFSERV4_NUMBERS)
        add("fmx_s103d_diffserv4_evidence_available", int(available), labels)
        if available:
            compliant = (
                s103d["diffserv4_tins_active"] == 4
                and s103d["overhead_bytes"] == 38
                and s103d["mpu_bytes"] == 84
                and s103d["wa_to_mk1_64b_p50_rtt_ms"] <= 13.0
                and s103d["wa_to_mk1_64b_p99_rtt_ms"] <= 40.0
                and s103d["voip_64b_jitter_ms"] <= 2.2
            )
            add("fmx_s103d_diffserv4_compliant", int(compliant), labels)

    @staticmethod
    def _render_s103e_pbe_mk1(s103e, labels, add, valid):
        for key, metric in S103E_PBE_MK1_METRICS.items():
            if valid and key in s103e:
                add(metric, float(s103e[key]), labels)
        if valid and "l2_loop_guard_whitelisted" in s103e:
            add("fmx_s103e_pbe_mk1_l2_whitelisted", int(s103e["l2_loop_guard_whitelisted"]), labels)
        available = (
            valid
            and all(k in s103e for k in S103E_PBE_MK1_NUMBERS)
            and all(k in s103e for k in S103E_PBE_MK1_BOOLS)
        )
        add("fmx_s103e_pbe_mk1_evidence_available", int(available), labels)
        if available:
            compliant = (
                s103e["l2_loop_guard_whitelisted"] is True
                and s103e["set_multiq"] == 3
                and s103e["ptp_xmit"] == 1
                and s103e["pbe242_to_mk1_p50_rtt_ms"] <= 3.5
                and s103e["pbe242_to_mk1_p95_rtt_ms"] <= 6.0
                and s103e["voip_jitter_ms"] <= 1.0
                and s103e["mk1_btest_p95_ms"] <= 6.0
            )
            add("fmx_s103e_pbe_mk1_e2e_compliant", int(compliant), labels)

    @staticmethod
    def _render_s103f_2xc(s103f, labels, add, valid):
        for key, metric in S103F_2XC_METRICS.items():
            if valid and key in s103f:
                add(metric, float(s103f[key]), labels)
        available = valid and all(k in s103f for k in S103F_2XC_NUMBERS)
        add("fmx_s103f_2xc_evidence_available", int(available), labels)
        if available:
            compliant = (
                s103f["swr_limit"] == 2
                and s103f["ptp_xmit"] == 1
                and s103f["ff_cap_rep"] == 2
                and s103f["umac_max_peers"] == 32
                and s103f["umac_vow_config"] == 1
                and s103f["set_multiq"] == 3
                and s103f["cabq_maxdur"] in (5, 20)
                and s103f["loaded_p95_rtt_ms"] <= 7.5
            )
            add("fmx_s103f_2xc_multiq_compliant", int(compliant), labels)

    @staticmethod
    def _render_ltu(ltu, state, labels, add, valid):
        for key, metric in LTU_METRICS.items():
            add("fmx_ltu_metric_available", int(key in ltu), {**labels, "metric": key})
            if key in ltu:
                kind = "counter" if key.startswith("irq63_") else "gauge"
                add(metric, float(ltu[key]), labels, kind=kind)
        # Raw cumulative IRQ counters may reset on boot; the separate IRQ delta
        # is derived only across qualified, same-boot, monotone observations.
        if "loaded_rtt_ms" in ltu:
            add("fmx_ltu_loaded_rtt_seconds", ltu["loaded_rtt_ms"] / 1000, labels)
        if "ini_rx_target_pwr" in ltu:
            add("fmx_ltu_ini_rx_target_valid", int(0 <= ltu["ini_rx_target_pwr"] <= 1200), labels)
        if valid and state.irq_delta is not None:
            add("fmx_ltu_cpu1_irq63_delta", state.irq_delta[1], labels)
            add("fmx_ltu_cpu0_irq63_delta", state.irq_delta[0], labels)
        conditions = {}
        if valid and state.irq_delta is not None:
            conditions[1] = state.irq_delta[0] > 0 and state.irq_delta[1] == 0
        if all(k in ltu for k in ("bd_handle_once", "loaded_stalls_observed")):
            conditions[2] = ltu["bd_handle_once"] == 0 and ltu["loaded_stalls_observed"]
        if all(k in ltu for k in ("auto_mcs_write_attempted", "auto_mcs_oops_observed")):
            conditions[3] = ltu["auto_mcs_write_attempted"] and ltu["auto_mcs_oops_observed"]
        if all(k in ltu for k in ("expect_4096_qam", "auto_mcs_ceiling", "sched_mcs_ceiling_qam")):
            conditions[4] = ltu["expect_4096_qam"] and ltu["auto_mcs_ceiling"] == 31 and ltu["sched_mcs_ceiling_qam"] < 4096
        if all(k in ltu for k in ("rx_target_power_dbm", "rx_target_power_expected_dbm", "ulpwr_enabled", "uplink_degraded")):
            conditions[5] = ltu["uplink_degraded"] and ltu["ulpwr_enabled"] and ltu["rx_target_power_dbm"] - ltu["rx_target_power_expected_dbm"] >= 20
        if all(k in ltu for k in ("pb_boost_expected", "pb_boost_mode", "pb_boost_gain_index")):
            conditions[6] = ltu["pb_boost_expected"] and ltu["pb_boost_mode"] == 1 and ltu["pb_boost_gain_index"] == 0
        if all(k in ltu for k in ("ini_rx_target_pwr", "ini_parse_error")):
            conditions[7] = ltu["ini_rx_target_pwr"] < 0 and ltu["ini_parse_error"]
        if all(k in ltu for k in ("shaping_expected", "htb_active", "cls_u32_loaded", "under_load")):
            conditions[8] = ltu["under_load"] and ltu["shaping_expected"] and (not ltu["htb_active"] or not ltu["cls_u32_loaded"])
        for i, bug in enumerate(LTU_BUG_IDS, 1):
            bug_labels = {**labels, "bug_id": bug}
            available = i in conditions and valid
            add("fmx_ltu_bug_evidence_available", int(available), bug_labels)
            if available:
                add("fmx_ltu_bug_condition", int(conditions[i]), bug_labels)


def _openmetrics_requested(accept):
    weights = {}
    for entry in accept.split(","):
        parts = [x.strip() for x in entry.split(";")]
        params = dict(x.split("=", 1) for x in parts[1:] if "=" in x)
        try:
            q = float(params.get("q", "1"))
        except ValueError:
            continue
        if not math.isfinite(q) or not 0 < q <= 1:
            continue
        if parts[0] == "application/openmetrics-text" and params.get("version", "1.0.0") == "1.0.0":
            weights["open"] = max(weights.get("open", 0), q)
        if parts[0] == "text/plain" and params.get("version", "0.0.4") == "0.0.4":
            weights["prom"] = max(weights.get("prom", 0), q)
    return weights.get("open", 0) > 0 and weights.get("open", 0) >= weights.get("prom", 0)


def make_server(exporter, host="127.0.0.1", port=0):
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup()
            self.connection.settimeout(5)

        def log_message(self, *_):
            pass

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            code = 200
            if path == "/metrics":
                om = _openmetrics_requested(self.headers.get("Accept", ""))
                content_type = OPENMETRICS_CONTENT_TYPE if om else PROM_CONTENT_TYPE
                data = exporter.render(openmetrics=om).encode("utf-8")
            elif path in {"/healthz", "/readyz"}:
                health = exporter.health()
                code = 503 if path == "/readyz" and not health["ready"] else 200
                content_type = "application/json; charset=utf-8"
                data = (json.dumps(health, allow_nan=False) + "\n").encode()
            else:
                content_type = "text/plain; charset=utf-8"
                data = b"Not found\n"; code = 404
            self.send_response(code)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self):
            self.send_error(405)

    class Server(ThreadingHTTPServer):
        daemon_threads = True
        request_queue_size = 16
        def __init__(self, *args, **kwargs):
            self.slots = threading.BoundedSemaphore(16)
            super().__init__(*args, **kwargs)

        def process_request(self, request, client_address):
            if not self.slots.acquire(blocking=False):
                self.shutdown_request(request)
                return
            try:
                super().process_request(request, client_address)
            except Exception:
                self.slots.release()
                raise

        def process_request_thread(self, request, client_address):
            try:
                super().process_request_thread(request, client_address)
            finally:
                self.slots.release()

    return Server((host, port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Local atomic producer JSON; never an SSH/HTTP source")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=9118)
    parser.add_argument("--poll-seconds", type=float, default=5)
    parser.add_argument("--expected-link", action="append", default=[])
    parser.add_argument("--once", action="store_true", help="Print local Prometheus exposition and exit; no listener")
    args = parser.parse_args(argv)
    if not math.isfinite(args.poll_seconds) or args.poll_seconds < 0.5 or not 0 <= args.port <= 65535:
        parser.error("poll-seconds must be finite >=0.5; port must be0..65535")
    exporter = TelemetryExporter(expected_links=args.expected_link)
    exporter.refresh_file(args.input)
    if args.once:
        print(exporter.render(), end="")
        return 0 if exporter.input_valid else 2
    stop = threading.Event()
    def poll():
        while not stop.wait(args.poll_seconds):
            exporter.refresh_file(args.input)
    with make_server(exporter, args.host, args.port) as server:
        worker = threading.Thread(target=poll, daemon=True)
        worker.start()
        try:
            server.serve_forever(poll_interval=0.5)
        except KeyboardInterrupt:
            pass
        finally:
            stop.set(); worker.join(timeout=5)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
