#!/usr/bin/env python3
"""
Stage 50C (`T-S50C-GEM2-STAGE46A-CHAMPION-V16-TX-BIAS-2-AND-STAGE47B-LTU-OTA-PACKAGER`):
OpenWrt PtMP / Multi-CPE AQM Profile & Stage 46A Champion v16 (`S46A-R3`:
`M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`, `+3.489%` goodput `39.642->41.025 Mbps`,
`-6.291%` loaded p95 RTT `90.986->85.262 ms`, `-6.113%` p99 RTT `95.257->89.434 ms`,
`-17.703%` Dual IPTV jitter `2.412->1.985 ms`, `-5.206%` VoIP jitter `2.689->2.549 ms`,
Pareto `+5.6906%`) & Stage 47B LTU OTA 1024-QAM MIMO (`FMX-LTU` + `5500 5520` DCXO + `+15 dBm`:
`5.1s` OTA association `AP-PTMP(Run)` <-> `CPE-PTMP(Run)`, `TA=235`, `SpectrumEfficient=1535/1319`,
`61.4/79.1 Mbps` DL & `41.9 Mbps` UL) Guard.

Enforces the hardware-verified Stage 44A, 45B, 46A & 47B physical laws:
  1. Enforces `dev_weight_tx_bias == 2` at full `netdev_budget == 600` on OpenWrt (`S46A-R3` Champion v16).
  2. Preserves dynamic kernel `dql` BQL (`limit_min=0, limit_max=1879048192, hold_time=1000` ms) and
     `tx_queue_len=1000` on `ag71xx` `eth0` (`S46A-R1/R5` proved manual static BQL `limit_max`/`limit_min`
     clips bulk TCP bursts by `-0.98%` to `-10.27%`).
  3. Preserves `lbm5_netdev_budget == 300` on 400 MHz AR934x `airOS 6` `LiteBeam M5` (`S46A-R6` proved
     `netdev_budget=600` inflates p95 RTT by `+8.84%`).
  4. Sets sysfs `tx_queue_len=256` on `br-lan` and `phy0-ap0*`/`phy0-sta0` (`S42A-R5`/`S44A-R5`),
     and `Rocket Prism 5AC Gen2` (`airOS 8 XC`) `br0/ath0/eth0` `tx_queue_len=256` & `netdev_budget=600`.
  5. Enforces `1 <= len(ltu_ssid.encode('utf-8')) <= 16` (`FMX-LTU`) and alternating `ltu_freq_list`
     (`5500 5520 5500 5520` full DCXO calibration) verified OTA in Stage 47B (`103.3 Mbps` aggregate).
"""

from __future__ import annotations

from pathlib import Path
import sys

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from controller.wisp_iptv_ptmp_sector_optimizer import (
    export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template,
    export_openwisp_dual_netdev_champion_v13_netjson_template,
    export_openwisp_iptv_netjson_template,
    export_openwisp_sysfs_txq256_champion_v14_netjson_template,
    export_openwisp_triple_play_champion_v11_netjson_template,
    export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template,
    export_openwisp_wds_fast_leave_champion_v12_netjson_template,
    export_r2ac_24ghz_m18_iptv_netjson_template,
    load_empirical_stage40a_and_stage42a_evidence,
    load_empirical_stage41a_champion_v13_evidence,
    load_empirical_stage42a_champion_v14_evidence,
    load_empirical_stage44a_and_stage45b_champion_v15_evidence,
    load_empirical_stage46a_and_stage47b_champion_v16_evidence,
    render_openwrt_bql_eth0_r5ac_txq256_champion_v15_script,
    render_openwrt_dual_netdev_champion_v13_script,
    render_openwrt_sysfs_txq256_champion_v14_script,
    render_openwrt_tx_bias_2_dynamic_bql_champion_v16_script,
    validate_aql_and_aqm_priority_inversion_guard,
    validate_openwrt_netdev_txq_and_airos6_unpolled_guard,
    validate_stage44a_bql_eth0_and_ltu_16byte_ssid_guard,
    validate_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard,
)

CHAMPION_V14_PROFILE_ID = "openwrt_sysfs_txq256_champion_v14"
CHAMPION_V14_ROUND_ID = "S42A-R5"
CHAMPION_V14_MECHANISM_ID = "M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256"

CHAMPION_V15_PROFILE_ID = "openwrt_bql_eth0_1000_r5ac_txq256_champion_v15"
CHAMPION_V15_ROUND_ID = "S44A-R5"
CHAMPION_V15_MECHANISM_ID = "M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000"

CHAMPION_V16_PROFILE_ID = "openwrt_tx_bias_2_dynamic_bql_champion_v16"
CHAMPION_V16_ROUND_ID = "S46A-R3"
CHAMPION_V16_MECHANISM_ID = "M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600"

__all__ = [
    "CHAMPION_V16_PROFILE_ID",
    "CHAMPION_V16_ROUND_ID",
    "CHAMPION_V16_MECHANISM_ID",
    "CHAMPION_V15_PROFILE_ID",
    "CHAMPION_V15_ROUND_ID",
    "CHAMPION_V15_MECHANISM_ID",
    "CHAMPION_V14_PROFILE_ID",
    "CHAMPION_V14_ROUND_ID",
    "CHAMPION_V14_MECHANISM_ID",
    "validate_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard",
    "validate_stage44a_bql_eth0_and_ltu_16byte_ssid_guard",
    "validate_openwrt_netdev_txq_and_airos6_unpolled_guard",
    "validate_aql_and_aqm_priority_inversion_guard",
    "load_empirical_stage46a_and_stage47b_champion_v16_evidence",
    "load_empirical_stage44a_and_stage45b_champion_v15_evidence",
    "load_empirical_stage42a_champion_v14_evidence",
    "load_empirical_stage40a_and_stage42a_evidence",
    "load_empirical_stage41a_champion_v13_evidence",
    "render_openwrt_tx_bias_2_dynamic_bql_champion_v16_script",
    "render_openwrt_bql_eth0_r5ac_txq256_champion_v15_script",
    "render_openwrt_sysfs_txq256_champion_v14_script",
    "render_openwrt_dual_netdev_champion_v13_script",
    "export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template",
    "export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template",
    "export_openwisp_sysfs_txq256_champion_v14_netjson_template",
    "export_openwisp_dual_netdev_champion_v13_netjson_template",
    "export_openwisp_wds_fast_leave_champion_v12_netjson_template",
    "export_openwisp_triple_play_champion_v11_netjson_template",
    "export_openwisp_iptv_netjson_template",
    "export_r2ac_24ghz_m18_iptv_netjson_template",
]
