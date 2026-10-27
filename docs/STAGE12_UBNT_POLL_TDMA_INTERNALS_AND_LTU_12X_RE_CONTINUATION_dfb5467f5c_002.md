<!-- doc-head: STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE.md) | Part 2/3
<a id="stage-12--deep-reverse-engineering-of-ubnt_poll_hostko-airmax-ac-tdma-scheduler--ltu-4096-qam-12x-phymac-internals"></a> [Stage 12 — Deep Reverse Engineering of `ubnt_poll_host.ko` (airMAX AC TDMA Scheduler) & LTU `4096-QAM` (`12x`) PHY/MAC Internals](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#stage-12--deep-reverse-engineering-of-ubnt_poll_hostko-airmax-ac-tdma-scheduler--ltu-4096-qam-12x-phymac-internals) | <a id="1-executive-summary"></a> [1. Executive Summary](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#1-executive-summary) | <a id="2-ubnt_poll_hostko-multi-version--cross-platform-inventory-wa-vs-xc"></a> [2. `ubnt_poll_host.ko` Multi-Version & Cross-Platform Inventory (`WA` vs `XC`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#2-ubnt_poll_hostko-multi-version--cross-platform-inventory-wa-vs-xc) | <a id="21-binary-inventory-across-5-extracted-firmware-builds"></a> [2.1 Binary Inventory Across 5 Extracted Firmware Builds](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#21-binary-inventory-across-5-extracted-firmware-builds) | <a id="22-evolution-across-v8512-rightarrow-v874-cs-rightarrow-v8725"></a> [2.2 Evolution Across `v8.5.12` $\rightarrow$ `v8.7.4-cs` $\rightarrow$ `v8.7.25`](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#22-evolution-across-v8512-rightarrow-v874-cs-rightarrow-v8725) | <a id="3-complete-ubnt_poll_hostko-sysctl-procfs--character-device-architecture"></a> [3. Complete `ubnt_poll_host.ko` Sysctl, Procfs & Character-Device Architecture](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#3-complete-ubnt_poll_hostko-sysctl-procfs--character-device-architecture) | <a id="31-global-sysctl-table-procsysdevuph-in-data-at-0x0080"></a> [3.1 Global Sysctl Table (`/proc/sys/dev/uph/*` in `.data` at `0x0080`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#31-global-sysctl-table-procsysdevuph-in-data-at-0x0080) | <a id="32-per-radio-sysctl-table-procsysdevuph_-in-rodata-at-0x0000"></a> [3.2 Per-Radio Sysctl Table (`/proc/sys/dev/uph_<radio>/*` in `.rodata` at `0x0000`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#32-per-radio-sysctl-table-procsysdevuph_-in-rodata-at-0x0000) | <a id="33-character-device-devuph_--ku_comm-ioctl-interface"></a> [3.3 Character Device `/dev/uph_<radio>` & `ku_comm` IOCTL Interface](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#33-character-device-devuph_--ku_comm-ioctl-interface) | <a id="4-complete-104-byte-ptmp_netconf-struct--rodata-bandwidth-profiles"></a> [4. Complete `104`-Byte `ptmp_netconf` Struct & `.rodata` Bandwidth Profiles](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#4-complete-104-byte-ptmp_netconf-struct--rodata-bandwidth-profiles) | <a id="41-exact-55-field-ptmp_netconf-struct-layout-uph_dev--156--259"></a> [4.1 Exact 55-Field `ptmp_netconf` Struct Layout (`uph_dev + 156 .. 259`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_001.md#41-exact-55-field-ptmp_netconf-struct-layout-uph_dev--156--259) | <a id="55-conducted-tx-power-backoff-tables-by-mcs-rodata-0x4e9c0x55b0"></a> [5.5 Conducted TX Power Backoff Tables by MCS (`.rodata` `0x4e9c..0x55b0`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_003.md#55-conducted-tx-power-backoff-tables-by-mcs-rodata-0x4e9c0x55b0) | <a id="6-ltu-runtime-control-plane-af-ame_cfgsh-ame_adjsh-sysfs-debugfs-module-params"></a> [6. LTU Runtime Control Plane (`af`, `ame_cfg.sh`, `ame_adj.sh`, `sysfs`, `debugfs`, Module Params)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_003.md#6-ltu-runtime-control-plane-af-ame_cfgsh-ame_adjsh-sysfs-debugfs-module-params) | <a id="61-kernel-ini-config-interface-sysdevicesplatformame_ctrl_devconfig"></a> [6.1 Kernel INI Config Interface (`/sys/devices/platform/ame_ctrl_dev/config`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_003.md#61-kernel-ini-config-interface-sysdevicesplatformame_ctrl_devconfig) | <a id="62-56-ame_coreko-module-parameters-sysmoduleame_coreparameters"></a> [6.2 56 `ame_core.ko` Module Parameters (`/sys/module/ame_core/parameters/*`)](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_003.md#62-56-ame_coreko-module-parameters-sysmoduleame_coreparameters) | <a id="63-100-sysdevicesplatformame_debug_dev-attributes--30-syskerneldebugame-telemetry-dumps"></a> [6.3 100 `/sys/devices/platform/ame_debug_dev/*` Attributes & 30 `/sys/kernel/debug/ame/*` Telemetry Dumps](STAGE12_UBNT_POLL_TDMA_INTERNALS_AND_LTU_12X_RE_CONTINUATION_dfb5467f5c_003.md#63-100-sysdevicesplatformame_debug_dev-attributes--30-syskerneldebugame-telemetry-dumps)

<!-- stage822a-payload-begin -->
| Struct Offset | `uph_dev` Offset | Type | Field Name | `HT40` AC PtMP (`0xb90`) | `HT30` AC PtMP (`0xc60`) | `HT20` AC PtMP (`0xd30`) | `HT10` AC PtMP (`0xe00`) | `HT40` Hybrid/Max (`0xb28`) | `HT20` Hybrid/Max (`0xcc8`) |
| ---: | ---: | :--- | :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `+0` | `156` | `u32` | `flags` | `2256` (`0x08d0`) | `2256` | `2256` | `2256` | `10768` (`0x2a10`) | `10768` |
| `+4` | `160` | `u16` | `down_dur_min` (us) | `210` | `210` | `210` | `210` | `900` | `900` |
| `+6` | `162` | `u16` | `cfp_dur_min` (us) | `210` | `210` | `210` | `210` | `5000` | `10000` |
| `+8` | `164` | `u16` | `cbp_dur_slot` (us) | `20` | `30` | `50` | `100` | `300` | `300` |
| `+10` | `166` | `u16` | `down_dur` (us) | `8000` | `8000` | `8000` | `10000` | `15000` | `30000` |
| `+12` | `168` | `u16` | `up_dur` (us) | `8000` | `8000` | `8000` | `10000` | `15000` | `30000` |
| `+14` | `170` | `u16` | `cbp_dur` (us) | `300` | `400` | `500` | `1000` | `900` | `900` |
| `+16` | `172` | `u16` | `cbp_usable_dur` (us) | `200` | `300` | `300` | `800` | `900` | `900` |
| `+18` | `174` | `u16` | `downlink_active_thresh` | `100` | `100` | `100` | `200` | `0` | `0` |
| `+20` | `176` | `u16` | `cbp_duty_cycle_thresh` (%) | `20` | `20` | `20` | `40` | `5` | `5` |
| `+22` | `178` | `u16` | `cbp_duty_cycle_hwm` (%) | `15` | `15` | `15` | `30` | `5` | `5` |
| `+24` | `180` | `u8` | `duty_cycle_metric_maws` | `3` | `3` | `3` | `3` | `0` | `0` |
| `+25` | `181` | `u8` | `duty_cycle_metric_sms` | `3` | `3` | `3` | `3` | `10` | `10` |
| `+26` | `182` | `u8` | `high_contention_sta_count` | `4` | `4` | `4` | `4` | `1` | `1` |
| `+27` | `183` | `u8` | `cbp_use_sta_count_limit` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+28` | `184` | `u32` | `activity_aging` (us) | `3000000` | `3000000` | `3000000` | `3000000` | `0` | `0` |
| `+32` | `188` | `u32` | `activity_aging_da` (us) | `10000000` | `10000000` | `10000000` | `10000000` | `0` | `0` |
| `+36` | `192` | `u32` | `activity_aging_hb` (us) | `1000000` | `1000000` | `1000000` | `1000000` | `0` | `0` |
| `+40` | `196` | `u32` | `usage_report_interval` (us) | `1000000` | `1000000` | `1000000` | `1000000` | `0` | `0` |
| `+44` | `200` | `u32` | `sounding_interval` (us) | `1000000` | `1000000` | `1000000` | `1000000` | `0` | `0` |
| `+48` | `204` | `u32` | `eval_report_interval` (us) | `5000000` | `5000000` | `5000000` | `5000000` | `0` | `0` |
| `+52` | `208` | `u32` | `network_config_interval` (us) | `1000000` | `1000000` | `1000000` | `1000000` | `0` | `0` |
| `+56` | `212` | `u16` | `high_contention_min_down_dur` | `8000` | `8000` | `8000` | `10000` | `15000` | `30000` |
| `+58` | `214` | `u16` | `high_contention_min_up_dur` | `2000` | `2000` | `2000` | `4000` | `15000` | `30000` |
| `+60` | `216` | `u16` | `cbp_use_txop_cycle_window` | `100` | `100` | `100` | `100` | `0` | `0` |
| `+62` | `218` | `u16` | `cbp_use_allowed_in_window` | `40` | `40` | `40` | `40` | `0` | `0` |
| `+64` | `220` | `u16` | `down_dur_gap` (us) | `75` | `75` | `75` | `150` | `0` | `0` |
| `+66` | `222` | `u16` | `up_dur_gap` (us) | `200` | `300` | `400` | `400` | `0` | `0` |
| `+68..+74` | `224..230` | `7xu8` | `dl/ul_*_thresh_*` (from `cms_bias`) | `0..0` | `0..0` | `0..0` | `0..0` | `0..0` | `0..0` |
| `+75` | `231` | `u8` | `cms_bias` (`0..9`) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+76` | `232` | `u16` | `hyb_cfp_min_dur_low_use` (us) | `0` | `0` | `0` | `0` | `210` | `210` |
| `+78` | `234` | `u16` | `hyb_bal_dl_avg_dur_thresh` (us) | `0` | `0` | `0` | `0` | `2500` | `5000` |
| `+80` | `236` | `u16` | `hyb_bal_dl_avg_txuse_thresh` | `0` | `0` | `0` | `0` | `200` | `200` |
| `+82` | `238` | `u16` | `hyb_cfp_dur_unit` (us) | `0` | `0` | `0` | `0` | `1000` | `1000` |
| `+84` | `240` | `u8` | `voip_bias` (`0..9`) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+85` | `241` | `u8` | `voip_pps_min` | `12` | `12` | `12` | `12` | `12` | `12` |
| `+86` | `242` | `u8` | `voip_pps_max` | `60` | `60` | `60` | `60` | `60` | `60` |
| `+87` | `243` | `i8` | `atpc_target_rssi` (dBm) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+88` | `244` | `u16` | `ff_frame_dur` (us) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+90` | `246` | `u8` | `ff_dl_alloc` (%) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+91` | `247` | `u8` | `ff_cbp_slots` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+92` | `248` | `u8` | `ff_dl_ctrl_rate` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+93` | `249` | `u8` | `ff_ul_ctrl_rate` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+94` | `250` | `u8` | `ff_dl_swr_count` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+95` | `251` | `u8` | `ff_ul_swr_count` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+96` | `252` | `u16` | `ff_dack_arbit_max` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+98` | `254` | `u8` | `ff_unit_shift` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+99` | `255` | `u8` | `ff_guard_units` | `0` | `0` | `0` | `0` | `0` | `0` |
| `+100` | `256` | `u8` | `atpc_max_power` (dBm) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+101` | `257` | `u8` | `atpc_min_power` (dBm) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+102` | `258` | `u8` | `ff_mcast_airtime_limit` (%) | `0` | `0` | `0` | `0` | `0` | `0` |
| `+103` | `259` | `i8` | `ff_sta_rx_rssi_th` (dBm) | `0` | `0` | `0` | `0` | `0` | `0` |

### 4.2 Hidden-Node Retry Suppression Table (`_retr_supression_levels` at `.rodata` `0xea4`)

In `ubnt_poll_host_init_ptmp_netconf` (`0xdb1c..0xdb68`) and `ubnt_poll_host_send_ptmp_netconf` (`0xe358`), indexing `_retr_supression_levels` (`70` bytes = `10` rows $\times$ `7` `uint8` columns) by `cms_bias` (`0..9`) populates offsets `+68..+74` (`uph_dev + 224..230`):

| `cms_bias` Level | `dl_rate_ratio_thresh_nr` (`+68`) | `dl_per_thresh_nr` % (`+69`) | `ul_rate_ratio_thresh_nb` (`+70`) | `ul_per_thresh_nb` % (`+71`) | `ul_rate_ratio_thresh_nr` (`+72`) | `ul_per_thresh_nr` % (`+73`) | `txop_qual_thresh_nr_nb` % (`+74`) |
| :---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `0` (Default) | `0` | `100` | `0` | `100` | `0` | `100` | `20` |
| `1` | `9` | `80` | `0` | `100` | `9` | `80` | `60` |
| `2` | `9` | `80` | `9` | `80` | `17` | `80` | `60` |
| `3` | `17` | `70` | `9` | `80` | `17` | `70` | `65` |
| `4` | `17` | `70` | `17` | `70` | `26` | `70` | `65` |
| `5` | `26` | `70` | `17` | `70` | `26` | `70` | `70` |
| `6` | `26` | `70` | `26` | `70` | `34` | `65` | `70` |
| `7` | `34` | `65` | `26` | `70` | `34` | `65` | `80` |
| `8` | `34` | `65` | `34` | `65` | `51` | `60` | `85` |
| `9` (Aggressive) | `51` | `60` | `34` | `65` | `51` | `55` | `85` |

> **Engineering Significance**: By default (`cms_bias = 0`), `dl_per_thresh_nr = 100%`, `ul_per_thresh_nr = 100%`, and `txop_qual_thresh_nr_nb = 20%`, meaning retry suppression under hidden-node/narrowband interference is practically disabled unless `cms_bias` (`1..9`) is written to `/proc/sys/dev/uph_wifi0/cms_bias` or individual thresholds (`dl_per_thresh_nr`, `ul_per_thresh_nr`, `txop_qual_thresh_nr_nb`) are tuned via `/proc/sys/dev/uph_wifi0/netconf`!

### 4.3 VoIP Dynamic Duration Table (`_voip_dynamic_duration_levels` at `.rodata` `0xe68`)

In `ubnt_poll_host_init_ptmp_netconf` (`0xdb8c..0xdbf0`), indexing `_voip_dynamic_duration_levels` (`60` bytes = `10` rows $\times$ `6` bytes) by `voip_bias` (`0..9`) overrides `high_contention_sta_count` (`+26`), `high_contention_min_down_dur` (`+56`), and `high_contention_min_up_dur` (`+58`):

| `voip_bias` Level | `high_contention_sta_count` (`+26`) | `high_contention_min_down_dur` (us, `+56`) | `high_contention_min_up_dur` (us, `+58`) |
| :---: | ---: | ---: | ---: |
| `0` (Default) | `0` (Keep profile default `4`) | `0` (Keep profile default `8000` us) | `0` (Keep profile default `2000` us) |
| `1` | `0` (Keep profile default `4`) | `0` (Keep profile default `8000` us) | `0` (Keep profile default `2000` us) |
| `2` | `2` | `15000` | `15000` |
| `3` | `2` | `15000` | `7500` |
| `4` | `3` | `15000` | `7500` |
| `5` | `4` | `15000` | `7500` |
| `6` | `5` | `15000` | `7500` |
| `7` | `6` | `15000` | `7500` |
| `8` | `7` | `15000` | `7500` |
| `9` | `8` | `15000` | `7500` |

---

## 5. Deep Reverse Engineering of LTU `4096-QAM` (`12x`) PHY/MAC (`ame_core.ko` & `ame_dev.ko`)

### 5.1 Module Architecture & Binary Identity (`aflturocket-2.4.2` vs `afltu-2.4.2`)

| Module | `aflturocket-2.4.2` (AP) Size & SHA256 | `afltu-2.4.2` (CPE) Size & SHA256 | Role in LTU Stack |
| :--- | :--- | :--- | :--- |
| `ame_core.ko` | `3,318,764` B (`a8d58e8d6a0c0665...`) | `3,282,052` B (`fe5d489ea66bd2f3...`) | Complete LTU baseband (`ame_bbp_*`), EAB (`AME_EAB_*`), HFE (`AME_HFE_*`), TDMA/OFDMA scheduler (`AME_Sched*`), `autoMCS_*`, and `autopwr_*` engine |
| `ame_dev.ko` | `298,760` B (`912a7c1923aad381...`) | `298,760` B (`912a7c1923aad381...`, **100% identical**) | Platform netdev (`ath0`), `/sys/devices/platform/ame_ctrl_dev/config` INI parser, `/sys/devices/platform/ame_debug_dev/*` (100 sysfs knobs), `/sys/kernel/debug/ame/*` (30 debugfs dumps), UBUS bridge |
| `ame_radio_mod.ko` | `578,528` B (`f36b837822fcefcc...`) | `578,424` B (`4aeac9b76454446e...`) | RFIC transceiver synthesis, calibration, DPD/PA tables |
| `ame_dfs.ko` | `170,108` B (`eb5e56ca9c1ab7d5...`) | `141,472` B (`16a860c6ef1c1b73...`) | Radar pulse detector & zero-wait DFS state machine |

All rate-progression tables (`autoMcs*Tbl`), rate-adaptation thresholds (`startThrd_4096`, `stayThrd_4096`, `mcsUpThrd_*`), RX sensitivity tables (`sensitivity`, `sensitivity_ptmp`, `table_ptmpAPPwrRange`, `table_ptpPwrRange`), and conducted TX power backoff tables (`mcs_txpwr_freq_ptp`, `af_5xhd_mcs_txpwr_freq`, `af_ltu5_mcs_txpwr_freq`, `af_ltuLR_mcs_txpwr_freq`) are **100% byte-identical** between `aflturocket-2.4.2` (`ame_core.ko`) and `afltu-2.4.2` (`ame_core.ko`).

### 5.2 LTU AutoMCS Progression Tables (`.rodata` at `0xd378..0xd3a2`)

Each entry is a 2-byte `(mcs_index, is_mimo)` pair selected by `autoMCS_get_rate_table` (`0x156098`):

| Step | `autoMcsAllSisoTbl` (`0xd378`, 5 steps) | `autoMcsUseSisoTbl` (`0xd384`, 7 steps) | `autoMcsOthersTbl` (`0xd394`, 7 steps) | Modulation & Coding Rate |
| :---: | :--- | :--- | :--- | :--- |
| `0` | `(7, 0)` — SISO `MCS 7` | `(7, 0)` — SISO `MCS 7` | `(7, 0)` — SISO `MCS 7` | `QPSK` (`2x`) |
| `1` | `(11, 0)` — SISO `MCS 11` | `(11, 0)` — SISO `MCS 11` | `(7, 1)` — MIMO `MCS 7` | `16-QAM` (`4x` SISO) / `QPSK` (`2x` MIMO) |
| `2` | `(15, 0)` — SISO `MCS 15` | `(15, 0)` — SISO `MCS 15` | `(11, 1)` — MIMO `MCS 11` | `64-QAM` (`6x` SISO) / `16-QAM` (`4x` MIMO) |
| `3` | `(19, 0)` — SISO `MCS 19` | `(15, 1)` — MIMO `MCS 15` | `(15, 1)` — MIMO `MCS 15` | `256-QAM` (`8x` SISO) / `64-QAM` (`6x` MIMO) |
| `4` | `(23, 0)` — SISO `MCS 23` | `(19, 1)` — MIMO `MCS 19` | `(19, 1)` — MIMO `MCS 19` | `1024-QAM` (`10x` SISO) / `256-QAM` (`8x` MIMO) |
| `5` | *(SISO ceiling = `10x`)* | `(23, 1)` — MIMO `MCS 23` | `(23, 1)` — MIMO `MCS 23` | `1024-QAM` (`10x` MIMO) |
| `6` | — | `(31, 1)` — MIMO `MCS 31` | `(31, 1)` — MIMO `MCS 31` | **`4096-QAM` (`12x` MIMO)** |

> **Key Finding (`CONFIRMED`)**: `autoMcsAllSisoTbl` tops out at `(23, 0)` (`1024-QAM` `10x`); `4096-QAM` (`12x`, `MCS 31`) only appears as `(31, 1)` (2x2 MIMO) in `autoMcsUseSisoTbl` and `autoMcsOthersTbl`.

### 5.3 LTU Rate-Adaptation, BLER & EVM/CINR Thresholds (`6x`, `8x`, `10x`, `12x`)

1. **Codeword Success / BLER Hysteresis Thresholds (`.rodata` `0xd5bc..0xd5e4` & `.data` `0x12b8..0x1304`)**:
   - `mcsUpThrd_lowqam = 95%`: Codeword success rate required to step up in `QPSK` (`2x`), `16-QAM` (`4x`), and `64-QAM` (`6x`).
   - `mcsUpThrd_256 = 96%`: Codeword success rate required to step up from `256-QAM` (`8x`, `MCS 19`) to `1024-QAM` (`10x`, `MCS 23`).
   - `mcsUpThrd_1024 = 93%`: Codeword success rate threshold for `1024-QAM` (`10x`) normal operation (`cont1024Threshold = 1`).
   - **`startThrd_4096 = 97%`**: Codeword success rate at `1024-QAM` (`MCS 23`) required to promote to **`4096-QAM` (`12x`, `MCS 31`)**.
   - **`stayThrd_4096 = 90%`**: Minimum codeword success rate required to remain at **`4096-QAM` (`12x`, `MCS 31`)** before demoting back to `1024-QAM` (`10x`).
   - `ackmcsUpThrd = 98%`, `ack_ratio_thr = 90%`: ACK symbol modulation promotion and reliability thresholds.
   - `mcsUpThreshold = 7`, `mcsDownThreshold = 10`, `mcsUpThreshold_timer = 90`, `mcsDnThreshold_timer = 1`, `penaltyThreshold = 25`, `penaltyTime = 4`, `avgWeight = 20`: Asymmetric fast-down (`1` timer tick) / slow-up (`90` timer ticks) rate-adaptation state machine, runtime-modifiable via `/sys/devices/platform/ame_debug_dev/autoMcsUpDown` (`ame_core_set_automcsUpDown` at `0x84d8`).
   - `ra_offset_table = [0, 9, 18, 25, 30]` (dB): Relative SNR/CINR progression offsets across modulation tiers.

2. **Hardware BBP EVM-to-MCS Demapper (`ame_bbp_op_evm_mcs_map` at `0x18e280`) & `table_ptpPwrRange` (`0x1f8`)**:
   - In `ame_bbp_op_evm_mcs_map`, the hardware EVM measurement (in `0.01 dB`, negated to CINR) is compared against exact immediate constants:
     - `CINR <= 10.00 dB` (`EVM >= -10.00 dB`) $\rightarrow$ BBP MCS `25` (`QPSK 1x`)
     - `10.00 dB < CINR <= 16.23 dB` (`-16.23 dB <= EVM < -10.00 dB`) $\rightarrow$ BBP MCS `26` (`QPSK 2x`)
     - `16.23 dB < CINR <= 22.30 dB` (`-22.30 dB <= EVM < -16.23 dB`) $\rightarrow$ BBP MCS `27` (`16-QAM 4x`)
     - `CINR > 22.30 dB` (`EVM < -22.30 dB`) $\rightarrow$ BBP MCS `28` (`64-QAM 6x` and higher data modes)
   - In `table_ptpPwrRange` (`.data` `0x1f8`, `448` bytes = `4` profiles $\times$ `8` bandwidths $\times$ `7` modulations $\times$ `2` bytes `[cinr_or_txpwr_idx, neg_rx_sens_dbm]`):

| Bandwidth | `4096-QAM` (`12x`) | `1024-QAM` (`10x`) | `256-QAM` (`8x`) | `64-QAM` (`6x`) | `16-QAM` (`4x`) | `QPSK` (`2x`) | `QPSK` (`1x`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`10 MHz`** | `(20, -59 dBm)` | `(17, -68 dBm)` | `(14, -75 dBm)` | `(11, -80 dBm)` | `(10, -86 dBm)` | `(10, -90 dBm)` | `(10, -95 dBm)` |
| **`20 MHz`** | `(20, -56 dBm)` | `(17, -65 dBm)` | `(14, -71 dBm)` | `(11, -77 dBm)` | `(10, -83 dBm)` | `(10, -88 dBm)` | `(10, -91 dBm)` |
| **`30 MHz`** | `(20, -59 dBm)` | `(17, -63 dBm)` | `(14, -70 dBm)` | `(11, -76 dBm)` | `(10, -81 dBm)` | `(10, -86 dBm)` | `(10, -89 dBm)` |
| **`40 MHz`** | `(20, -55 dBm)` | `(17, -61 dBm)` | `(14, -69 dBm)` | `(11, -74 dBm)` | `(10, -79 dBm)` | `(10, -85 dBm)` | `(10, -88 dBm)` |
| **`50 MHz`** | `(20, -50 dBm)` | `(17, -60 dBm)` | `(14, -68 dBm)` | `(11, -73 dBm)` | `(10, -78 dBm)` | `(10, -84 dBm)` | `(10, -87 dBm)` |
| **`60 MHz`** | **`(0, 0)` DISABLED** | `(17, -58 dBm)` | `(14, -67 dBm)` | `(11, -72 dBm)` | `(10, -78 dBm)` | `(10, -83 dBm)` | `(10, -86 dBm)` |
| **`80 MHz`** | **`(0, 0)` DISABLED** | `(17, -57 dBm)` | `(14, -65 dBm)` | `(11, -71 dBm)` | `(10, -76 dBm)` | `(10, -82 dBm)` | `(10, -85 dBm)` |
| **`100 MHz`** | **`(0, 0)` DISABLED** | `(17, -52 dBm)` | `(14, -64 dBm)` | `(11, -70 dBm)` | `(10, -75 dBm)` | `(10, -81 dBm)` | `(10, -83 dBm)` |

### 5.4 RX Sensitivity Tables (`sensitivity` at `0x5948` & `table_ptmpAPPwrRange` at `0x54c0`)

<!-- stage822a-payload-end -->
