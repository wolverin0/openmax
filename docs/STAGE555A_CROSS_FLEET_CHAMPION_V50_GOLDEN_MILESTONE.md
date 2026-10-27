<!-- doc-head: STAGE555A_CROSS_FLEET_CHAMPION_V50_GOLDEN_MILESTONE.md preserved document content -->
<!-- /doc-head -->


# Stage 555A: Golden Milestone Cross-Fleet Champion `v50.0` across All `8` Radio Families (`168` Multi-Radio Windows + `220` `WA` Windows + `144` `LTU` Windows)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` + `ath10k` / `mac80211` + `proprietary airMAX/LTU module` + `Linux` + `hardware`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `45s` Non-DFS / `120s` DFS rollback watchdog)
- **Artifact**: [`stage555a_cross_fleet_champion_v50_golden_milestone.json`](../artifacts/autoresearch/stage555a_cross_fleet_champion_v50_golden_milestone.json)
- **Builder**: [`build_stage555a_cross_fleet_champion_v50_golden_milestone.py`](../tools/autoresearch/build_stage555a_cross_fleet_champion_v50_golden_milestone.py)

## 1. Golden Milestone `v50.0` 8-Family Fleet Matrix

| # | Radio Family | Hardware / Firmware | Key `v50.0` Golden Milestone Knobs |
| :--- | :--- | :--- | :--- |
| 1 | **`WA_Mode_A_OpenWrt`** | `AR9342 + QCA9882` (`OpenWrt 24.10.4`) | `aql_txq_limit=1500/2000 us` + `tcp_comp_sack_delay_ns=250000` + `multicast_querier=1` |
| 2 | **`WA_Mode_B_airOS8`** | `AR9342 + QCA9882` (`WA.v8.7.19`) | `PB-040` + `PB-050` (`30000 ms / 2048 pkts`) + `VHT40` MCS 2 LGI (`24.83 Mbps`, `0.0%` loss) |
| 3 | **`XC_5GHz_AirPrism`** | `QCA9558 + QCA9880` (`XC.v8.7.25`) | Active-AirPrism GPIO `13..16` + `PB-040`/`PB-050` + `+10 MHz` shift (`+7.99 dB` EVM) |
| 4 | **`2XC_24GHz_AirPrism`** | `QCA9558 + QCA9880` (`2XC.v8.7.11`) | 2.4 GHz Spectral NF (`30s / -96 dBm`) + RTS `512 B` + WMM `[1500,2500,3000,1000] us` |
| 5 | **`XM_M5_32MB`** | `AR7241 + AR9280` (`32 MB` RAM) | `vm.min_free_kbytes=1536` + ANI OFDM/CCK immunity + `aql_txq_limit=1500/2000` + Minstrel `[4,4,2,2]` |
| 6 | **`XW_M5_64MB`** | `AR9342` (`64 MB` RAM, `XW.v6.3.x`) | `vm.min_free_kbytes=2048` + ANI OFDM/CCK immunity + DFS chirp guard + `txqueuelen=64` |
| 7 | **`TI_AR9344_GigE`** | `AR9344 + AR9380` GigE (`TI.v6.3.x`) | `vm.min_free_kbytes=3072` + `dev_weight=64` + `netdev_budget=384` + `txqueuelen=128` |
| 8 | **`LTU_Beetle_ASIC0`** | `AF-LTU` `Beetle` + `ame_ASIC0` | `bbp_rf_set_super4096=1` + `ame_bbp_set_dpd=2` + `-2 dB` autopwr (`94.8%` `4096-QAM` `12X`) |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE across 9 kernel/firmware modules + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: `168` Multi-Radio + `220` `WA` + `144` `LTU` counterbalanced `A1->B1->A2->B2` windows with `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, `full_mtu_1472b_loss_pct`, and `qam4096_12x_residence_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE555A-CROSS-FLEET-CHAMPION-V50-GOLDEN-MILESTONE`.
