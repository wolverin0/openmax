<!-- doc-head: STAGE661A_WA_CHAMPION_V11_284WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 661A — `WA` Champion `v11` (`284`-Window) Field Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware`.
- **284-Window Milestone**: Packages the `WA` Champion `v11` configuration (`PB-050 v1` + `PB-040`, `BQL = 15140 B`, `AQL = 2000/4000 us`, `fq_codel` `quantum = 3028 B` / `initial_quantum = 15140 B`, and `45 s` / `120 s` rollback watchdogs) into `firmware/openwrt/common/fmx_wa_v11_284window_field_kit.sh` (`SHA-256`: `a463970ca84223eb3146530b51d40af0795e995ae8622956bce056df18e3ff34`).

## 2. `WA` Champion `v11` Parameter Matrix
| Subsystem | Parameter | `WA` Champion `v11` Value | Physical & Queuing Role |
| :--- | :--- | :---: | :--- |
| Xtensa Target | `PB-050` + `PB-040` | `4000 ms` + Ring Guard | Prevents HTT TX descriptor exhaustion under burst load |
| `mac80211` Airtime | `aql_txq_limit` | `2000 / 4000 us` | Caps per-AC standing airtime to `< 4 ms` |
| Ethernet BQL | `byte_queue_limits/limit_max` | `15140 B` (`10x MTU`) | Eliminates `AR9342` GMAC TX ring bufferbloat |
| `fq_codel` Scheduler | `quantum` / `initial_quantum` | `3028 B` / `15140 B` | Aligns DRR stride (`2x MTU`) and `IW10` initial burst (`10x MTU`) |
| Rollback Watchdog | Non-DFS / DFS CAC | `45 s` / `120 s` | Full `FMX-DISC-24` DFS CAC immunity |

## 3. Safety & Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` `/dev/ame*` untouched.
