<!-- doc-head: STAGE497A_CROSS_FLEET_CHAMPION_V48.md preserved document content -->
<!-- /doc-head -->


# Stage 497A: Cross-Fleet Champion `v48` Package Synthesis (`R1..R12` `144-Window` Milestone + PB050 RC Probe Dampener)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `mac80211` / `ath10k` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage497a_cross_fleet_champion_v48.json`](../artifacts/autoresearch/stage497a_cross_fleet_champion_v48.json)
- **Builder**: [`build_stage497a_cross_fleet_champion_v48.py`](../tools/firmware/build_stage497a_cross_fleet_champion_v48.py)
- **Verification**: [`test_stage497a.py`](../tests/test_stage497a.py)

## 1. Cross-Fleet Champion `v48.0` Architecture Matrix

| Family | Reference Radio | R12 / Ground-Up Additions in `v48.0` | Rollback Watchdog |
| :--- | :--- | :--- | :--- |
| **`XC`** | Rocket Prism 5AC Gen2 (`.198`) | Ground-Up PB050 RC probe dampener (`200 ms / 2%`) + Active-AirPrism GPIO `13..16` + BQL/AQL pacing | `45s` Non-DFS / `120s` DFS |
| **`2XC`** | Rocket 2AC Prism (`.253`) | 2.4 GHz spectral scan NF calibration (`30 s / -96 dBm`) + WMM VO/VI protection (`AC*Minfree=64/32/16/0`) + RTS `512 B` | `45s` Non-DFS |
| **`XM`** | NanoStation M5 (`.20`) | PB050 RC probe dampener (`200 ms / 2%`) + Minstrel-HT `[4,4,2,2]` + Cooperative sensing ANI (`intmit=1`) + `vm.min_free_kbytes=1536` | `45s` Non-DFS |
| **`WA`** | PowerBeam / LiteBeam 5AC Gen2 | PB050 RC probe dampener + Stage 425A–430A PBE5AC PtP findings + Stage 105A Asymmetric VHT LGI rescue | `45s` Non-DFS / `120s` DFS |
| **`XW`** | LocoM5 / PowerBeam M5 64 MB | `vm.min_free_kbytes=2048` + `tcp_limit_output_bytes=49152` + `txqueuelen=64` | `45s` Non-DFS |
| **`LTU`** | AF-LTU (`Beetle` + `ame_ASIC0`) | `tcp_limit_output_bytes=131072` + `txqueuelen=256` | `45s` Non-DFS / `120s` DFS |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko`, `ath9k.ko`, `ame_core.ko`, `eab_driver.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: Synthesized from `36` rounds (`144` counterbalanced `A1->B1->A2->B2` live windows) with mandatory `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, and `goodput_mbps`.
- **Pillar E**: `memory-master` claim `MM-STAGE497A-CROSS-FLEET-CHAMPION-V48`.
