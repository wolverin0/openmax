<!-- doc-head: STAGE393A_CROSS_FLEET_CHAMPION_V45.md preserved document content -->
<!-- /doc-head -->


# Stage 393A — Cross-Fleet Champion `v45.0` Package Generator (`R1..R9` `108-Window` Synthesis)

## 1. Executive Summary (`CONFIRMED`)
Generates the unified **Cross-Fleet Champion `v45.0`** production configuration matrix (`artifacts/autoresearch/stage393a_cross_fleet_champion_v45.json`) integrating all **9 counterbalanced live rounds (`108` windows / `54` paired comparisons)** from [`Stage 392A`](STAGE392A_MULTI_RADIO_9ROUND_SCORECARD.md):
- **`XC` (`Rocket Prism 5AC Gen2`, `XC.v8.7.25`)**: `/proc/sys/dev/uph_wifi0` (`AC*Minfree=64/32/16/0`, `set_multiq=3`, `daprot=2`, `ff_mcast_airtime_limit=5`, `swr_limit=3`), `tcp_limit_output_bytes=49152`, `rmem_default=131072`, `wmem_default=131072`, `dev_weight=96`, `netdev_budget=600`, `tcp_thin_linear_timeouts=1`, `txqueuelen=192`.
- **`2XC` (`Rocket 2AC Prism`, `2XC.v8.7.11`)**: `/proc/sys/dev/uph_wifi0` (`AC*Minfree=64/32/16/0`, `set_multiq=3`, `daprot=2`, `ff_mcast_airtime_limit=4`, `swr_limit=3`), `tcp_limit_output_bytes=49152`, `dev_weight=96`, `netdev_budget=600`, ARP/multicast pinning (`gc_stale_time=120`, `gc_thresh1=256`, `igmp_max_memberships=32`, `icmp_ratelimit=100`), `txqueuelen=192`.
- **`XM` (`NanoStation M5` `32 MB` RAM, `XM.v6.1.12` / OpenWrt `23.05.5`)**: `aql_txq_limit_low_us=2000`, `aql_txq_limit_high_us=4000`, `aql_threshold=12000`, `ath9k_txq_max_depth=64`, `minstrel_retry_chain=[4,4,2,2]`, `aggr_limit_bytes=16384`, `vm.min_free_kbytes=1536`, `ani_enable=1`, `eth0` BQL `limit_max=24576`, `netdev_budget_usecs=4000`, `txqueuelen=48`.
- **Cross-Fleet Parity (`WA`, `XW`, `LTU`)**: Full parameter alignment with `45s` Non-DFS / `120s` DFS (`FMX-DISC-24`) rollback watchdogs.

## 2. Champion `v45.0` Parameter Matrix
| Family | Target Radio / RAM | `dev_weight` / `budget` | `txqueuelen` / BQL | `uph_wifi0` / Radio Knobs | TCP Pacing / Memory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`XC`** | `Rocket Prism 5AC Gen2` (`128 MB`) | `96` / `600` | `192` / Driver | `AC*Minfree=64/32/16/0`, `daprot=2`, `mcast=5` | `tcp_limit=49152`, `rmem_def=131072` |
| **`2XC`** | `Rocket 2AC Prism` (`128 MB`) | `96` / `600` | `192` / Driver | `AC*Minfree=64/32/16/0`, `daprot=2`, `mcast=4` | `tcp_limit=49152`, `gc_stale=120` |
| **`XM`** | `NanoStation M5` (`32 MB`) | `48` / `240` (`4000us`) | `48` / `24576 B` | `aql=2000/4000us`, `minstrel=[4,4,2,2]` | `min_free=1536`, `tcp_limit=32768` |
| **`WA`** | `PBE/LBE 5AC Gen2` (`64 MB`) | `64` / `300` | `128` / `32768 B` | `daprot=2`, `mcast=5` | `min_free=2560`, `tcp_limit=49152` |
| **`XW`** | `Loco/PBE M5 XW` (`64 MB`) | `64` / `300` | `64` / `32768 B` | `ani=1`, `AC*Minfree=0/16/32/64` | `min_free=2048`, `tcp_limit=49152` |
| **`LTU`** | `AF-LTU` (`Beetle` + `ame_ASIC0`) | `96` / `600` | `256` / `65536 B` | `eab_driver.ko` + `45s`/`120s` WD | `tcp_limit=131072` |

## 3. Safety & Verification Artifacts
- **Safety Boundaries**: `0` flash writes; `.241`, `.242`, and `.250` untouched (`CONFIRMED`).
- Generator: [`tools/firmware/build_stage393a_cross_fleet_champion_v45.py`](../tools/firmware/build_stage393a_cross_fleet_champion_v45.py)
- Receipt: [`artifacts/autoresearch/stage393a_cross_fleet_champion_v45.json`](../artifacts/autoresearch/stage393a_cross_fleet_champion_v45.json)
- Test Suite: [`tests/test_stage393a.py`](../tests/test_stage393a.py)
