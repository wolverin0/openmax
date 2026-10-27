<!-- doc-head: STAGE435A_CROSS_FLEET_CHAMPION_V46.md preserved document content -->
<!-- /doc-head -->


# Stage 435A: Cross-Fleet Champion `v46` Package Synthesis (`R1..R10` `120-Window` Milestone + Stage 105A Asymmetric VHT LGI Rescue)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `mac80211` / `ath10k` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage435a_cross_fleet_champion_v46.json`](../artifacts/autoresearch/stage435a_cross_fleet_champion_v46.json)
- **Builder**: [`build_stage435a_cross_fleet_champion_v46.py`](../tools/firmware/build_stage435a_cross_fleet_champion_v46.py)
- **Verification**: [`test_stage435a.py`](../tests/test_stage435a.py)

## 1. Cross-Fleet Champion `v46.0` Architecture Matrix

| Family | Reference Radio | R10 / Ground-Up Additions in `v46.0` | Rollback Watchdog |
| :--- | :--- | :--- | :--- |
| **`XC`** | Rocket Prism 5AC Gen2 (`.198`) | Active-AirPrism GPIO `13..16` filter index verification + WMI `[4,4,2,2]` retry profile + `uph_wifi0` `AC*Minfree=64/32/16/0` | `45s` Non-DFS / `120s` DFS |
| **`2XC`** | Rocket 2AC Prism (`.253`) | 2.4 GHz urban interference immunity + dynamic RTS/CTS `512 B` + AirPrism 2.4 GHz filter guard + `ff_mcast_airtime_limit=4` | `45s` Non-DFS |
| **`XM`** | NanoStation M5 (`.20`) | Asymmetric LGI rescue + `aql_txq_limit=2000/4000 us` + Minstrel-HT `[4,4,2,2]` + `vm.min_free_kbytes=1536` (32 MB OOM shield) | `45s` Non-DFS |
| **`WA`** | PowerBeam / LiteBeam 5AC Gen2 | Stage 105A Asymmetric VHT LGI rescue (`vht_tx_sgi_80mhz=0`) + `tcp_limit_output_bytes=49152` + `txqueuelen=128` | `45s` Non-DFS / `120s` DFS |
| **`XW`** | LocoM5 / PowerBeam M5 64 MB | `vm.min_free_kbytes=2048` + `tcp_limit_output_bytes=49152` + `txqueuelen=64` | `45s` Non-DFS |
| **`LTU`** | AF-LTU (`Beetle` + `ame_ASIC0`) | `tcp_limit_output_bytes=131072` + `txqueuelen=256` | `45s` Non-DFS / `120s` DFS |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko`, `ath9k.ko`, `ame_core.ko`, `eab_driver.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: Synthesized from `30` rounds (`120` counterbalanced `A1->B1->A2->B2` live windows) with mandatory `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, and `goodput_mbps`.
- **Pillar E**: `memory-master` claim `MM-STAGE435A-CROSS-FLEET-CHAMPION-V46`.
