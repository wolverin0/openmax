<!-- doc-head: STAGE465A_CROSS_FLEET_CHAMPION_V47.md preserved document content -->
<!-- /doc-head -->


# Stage 465A: Cross-Fleet Champion `v47` Package Synthesis (`R1..R11` `132-Window` Milestone + Stage 425A–430A PBE5AC PtP Findings)

- **Claim Status**: `CONFIRMED`
- **Primary Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`, `uph_wifi0`, `ath_dev.ko`) + `mac80211` / `ath10k` + `Linux`
- **Safety Gate**: `.241`, `.242`, `.250` untouched (`CONFIRMED`)
- **Artifact**: [`stage465a_cross_fleet_champion_v47.json`](../artifacts/autoresearch/stage465a_cross_fleet_champion_v47.json)
- **Builder**: [`build_stage465a_cross_fleet_champion_v47.py`](../tools/firmware/build_stage465a_cross_fleet_champion_v47.py)
- **Verification**: [`test_stage465a.py`](../tests/test_stage465a.py)

## 1. Cross-Fleet Champion `v47.0` Architecture Matrix

| Family | Reference Radio | R11 / Ground-Up Additions in `v47.0` | Rollback Watchdog |
| :--- | :--- | :--- | :--- |
| **`XC`** | Rocket Prism 5AC Gen2 (`.198`) | Ground-Up CCA/AGC dynamic stepping (`-68 dBm` / `4 dB`) + Active-AirPrism GPIO `13..16` + TCP pacing `110/150` | `45s` Non-DFS / `120s` DFS |
| **`2XC`** | Rocket 2AC Prism (`.253`) | 2.4 GHz co-channel immunity + WMM airtime deficit fairness (`[1500,2500,3000,1000] us`) + dynamic RTS/CTS `512 B` | `45s` Non-DFS |
| **`XM`** | NanoStation M5 (`.20`) | Cooperative sensing ANI (`intmit=1`) + `aggr_limit_bytes=16384` + asymmetric LGI rescue + `vm.min_free_kbytes=1536` | `45s` Non-DFS |
| **`WA`** | PowerBeam / LiteBeam 5AC Gen2 | Stage 425A–430A PBE5AC PtP findings + Stage 105A Asymmetric VHT LGI rescue (`vht_tx_sgi_80mhz=0`) + `txqueuelen=128` | `45s` Non-DFS / `120s` DFS |
| **`XW`** | LocoM5 / PowerBeam M5 64 MB | `vm.min_free_kbytes=2048` + `tcp_limit_output_bytes=49152` + `txqueuelen=64` | `45s` Non-DFS |
| **`LTU`** | AF-LTU (`Beetle` + `ame_ASIC0`) | `tcp_limit_output_bytes=131072` + `txqueuelen=256` | `45s` Non-DFS / `120s` DFS |

## 2. Five-Pillar Compliance Summary

- **Pillar A**: Binary RE of `ubnt_poll_host.ko`, `ath_dev.ko`, `umac.ko`, `ath9k.ko`, `ame_core.ko`, `eab_driver.ko` + 571-knob catalog.
- **Pillar B**: Closed-loop `HYPERRESEARCH V8` + `scholar-mcp` verification (`FMX-DISC-07`, `FMX-DISC-11`, `FMX-DISC-24`, `FMX-DISC-33`).
- **Pillar C**: Synthesized from `33` rounds (`132` counterbalanced `A1->B1->A2->B2` live windows) with mandatory `45s`/`120s` rollback watchdog.
- **Pillar D**: Pareto optimal across `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, `softirq_pct`, and `goodput_mbps`.
- **Pillar E**: `memory-master` claim `MM-STAGE465A-CROSS-FLEET-CHAMPION-V47`.
