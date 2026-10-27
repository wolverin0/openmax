<!-- doc-head: STAGE339A_CROSS_FLEET_CHAMPION_V43.md preserved document content -->
<!-- /doc-head -->


# Stage 339A — Cross-Fleet Champion `v43.0` Package Generator (`R1..R7` `84-Window` Synthesis)

## 1. Executive Summary (`CONFIRMED`)
Generates the unified **Cross-Fleet Champion `v43.0`** production configuration matrix (`artifacts/autoresearch/stage339a_cross_fleet_champion_v43.json`) integrating all **7 counterbalanced live rounds (`84` windows / `42` paired comparisons)** from [`Stage 338A`](STAGE338A_MULTI_RADIO_7ROUND_SCORECARD.md):
- **`XC` (`Rocket Prism 5AC Gen2`, `XC.v8.7.25`)**: `dev_weight=96`, `netdev_budget=600`, `tcp_thin_linear_timeouts=1`, `tcp_limit_output_bytes=65536`, `txqueuelen=192`, `uph_wifi0` (`set_multiq=3`, `daprot=2`, `ff_mcast_airtime_limit=5`, `swr_limit=3`, `AC*Minfree=64/32/16/0`).
- **`2XC` (`Rocket 2AC Prism`, `2XC.v8.7.11`)**: `dev_weight=96`, `netdev_budget=600`, `uph_wifi0` (`daprot=2`, `ff_mcast_airtime_limit=4`), ARP/multicast pinning (`gc_stale_time=120`, `gc_thresh1=256`, `igmp_max_memberships=32`, `icmp_ratelimit=100`), `txqueuelen=192`.
- **`XM` (`NanoStation M5` `32 MB` RAM, `XM.v6.1.12`)**: `vm.min_free_kbytes=1536`, `ani_enable=1` (`intmit=1`), `eth0` BQL `limit_max=24576`, `fq_codel` (`5ms`/`50ms`/`300`/`384`), `dev_weight=48`, `netdev_budget=240`, `txqueuelen=48`, `tcp_limit_output_bytes=32768`.
- **Cross-Fleet Parity (`WA`, `XW`, `LTU`)**: Full parameter alignment with `45s` Non-DFS / `120s` DFS (`FMX-DISC-24`) rollback watchdogs.

## 2. Champion `v43.0` Parameter Matrix
| Family | Target Radio / RAM | `dev_weight` / `budget` | `txqueuelen` / BQL | `uph_wifi0` / Radio Knobs | TCP Pacing / Memory |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`XC`** | `Rocket Prism 5AC Gen2` (`128 MB`) | `96` / `600` | `192` / Driver | `daprot=2`, `mcast=5`, `swr=3` | `tcp_limit=65536`, `thin_lto=1` |
| **`2XC`** | `Rocket 2AC Prism` (`128 MB`) | `96` / `600` | `192` / Driver | `daprot=2`, `mcast=4`, `gc_stale=120` | `tcp_limit=65536`, `icmp_rate=100` |
| **`XM`** | `NanoStation M5` (`32 MB`) | `48` / `240` | `48` / `24576 B` | `ani=1`, `AC*Minfree=0/16/32/64` | `min_free=1536`, `tcp_limit=32768` |
| **`WA`** | `PBE/LBE 5AC Gen2` (`64 MB`) | `64` / `300` | `128` / `32768 B` | `daprot=2`, `mcast=5` | `min_free=2560`, `tcp_limit=65536` |
| **`XW`** | `Loco/PBE M5 XW` (`64 MB`) | `64` / `300` | `64` / `32768 B` | `ani=1`, `AC*Minfree=0/16/32/64` | `min_free=2048`, `tcp_limit=49152` |
| **`LTU`** | `AF-LTU` (`Beetle` + `ame_ASIC0`) | `96` / `600` | `256` / `65536 B` | `eab_driver.ko` + `45s`/`120s` WD | `tcp_limit=131072` |

## 3. Safety & Verification Artifacts
- **Safety Boundaries**: `0` flash writes; `.241`, `.242`, and `.250` untouched (`CONFIRMED`).
- Generator: [`tools/firmware/build_stage339a_cross_fleet_champion_v43.py`](../tools/firmware/build_stage339a_cross_fleet_champion_v43.py)
- Receipt: [`artifacts/autoresearch/stage339a_cross_fleet_champion_v43.json`](../artifacts/autoresearch/stage339a_cross_fleet_champion_v43.json)
- Test Suite: [`tests/test_stage339a.py`](../tests/test_stage339a.py)
