<!-- doc-head: STAGE523A_CROSS_FLEET_CHAMPION_V49_AND_TESTER_MATRIX.md preserved document content -->
<!-- /doc-head -->


# Stage 523A: Cross-Fleet Champion `v49` & Tester Matrix (`208` `WA` Windows + `156` Multi-Radio Windows + `144` `LTU` Windows + `VHT40` PtP)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `QCA firmware` + `ath10k` / `mac80211` + `proprietary airMAX/LTU module` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`, `45s` Non-DFS / `120s` DFS rollback watchdog)
- **Artifact**: [`stage523a_cross_fleet_champion_v49_and_tester_matrix.json`](../artifacts/autoresearch/stage523a_cross_fleet_champion_v49_and_tester_matrix.json)
- **Builder**: [`build_stage523a_cross_fleet_champion_v49_and_tester_matrix.py`](../tools/autoresearch/build_stage523a_cross_fleet_champion_v49_and_tester_matrix.py)

## 1. Cross-Fleet Champion `v49.0` Evidence & Knob Matrix

| Family | Windows Validated | Key `v49.0` Additions | Watchdog |
| :--- | :--- | :--- | :--- |
| **`WA`** | `208` | `VHT40` MCS 2 LGI (`24.83 Mbps`, `0.0%` `1472B` loss) + `g_rc_probe_period_ms=30000` / `2048` pkts + `aql_txq_limit=1500/2000` + `tcp_comp_sack_delay_ns=250000` | `45s` / `120s` |
| **`XC`** | `52` (`156` fleet) | Active-AirPrism GPIO `13..16` + `pktlog_filter=0x0` + `nf_cal_period=120` + `daprot=2` + `set_multiq=3` | `45s` / `120s` |
| **`2XC`** | `52` (`156` fleet) | 2.4 GHz Spectral Scan NF calibration (`30s / -96 dBm`) + dynamic RTS `512 B` + `AC*Minfree=64/32/16/0` | `45s` |
| **`XM`** | `52` (`156` fleet) | `aql_txq_limit=1500/2000` + Minstrel-HT `[4,4,2,2]` + `aggr_limit=16384` + `vm.min_free_kbytes=1536` | `45s` |
| **`XW`** | `48` | `vm.min_free_kbytes=2048` + `tcp_limit_output_bytes=49152` + `txqueuelen=64` | `45s` |
| **`LTU`** | `144` | `tcp_limit_output_bytes=131072` + `txqueuelen=256` (`AF-LTU` `Beetle` + `ame_ASIC0` + `eab_driver.ko`) | `45s` / `120s` |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE across 9 kernel/firmware modules + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: `156` Multi-Radio + `208` `WA` + `144` `LTU` counterbalanced `A1->B1->A2->B2` windows with `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, and `full_mtu_1472b_loss_pct`.
- **Pillar E**: `memory-master` claim `MM-STAGE523A-CROSS-FLEET-CHAMPION-V49`.
