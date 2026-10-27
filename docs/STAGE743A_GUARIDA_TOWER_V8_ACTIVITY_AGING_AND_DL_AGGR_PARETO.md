<!-- doc-head: STAGE743A_GUARIDA_TOWER_V8_ACTIVITY_AGING_AND_DL_AGGR_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 743A — Guarida Tower `v8` (`activity_aging` & `aggr_limit_bytes`) Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) / `QCA firmware` / `ath10k` / `mac80211`.
- **Stage 681A / 735A Grounding**: In `ubnt_poll_host.ko`, when `22` CPEs on `Panel2` (`.82`) remain in the active poll list due to a sluggish `activity_aging` timer (`1000 ms`), the per-CPE downlink aggregation ceiling (`aggr_limit_bytes`) collapses to `4096 B` (`~2` subframes). Tuning `activity_aging = 250 ms` alongside `Fixed 10ms 67/33` demotes idle CPEs within `250 ms` so active downloaders maintain `aggr_limit_bytes >= 49152 B`.
- **Result**: `GUARIDA_V8_ACTIVITY_AGING_AND_DL_AGGR_CHAMPION` reaches **`498.40 Mbps` (`+53.46%`)** tower aggregate goodput and **`7.95 ms` `p99` RTT**.

## 2. Guarida Tower `v8` SimPy + NSGA-II Matrix
| Candidate | `activity_aging` | `aggr_limit_bytes` | `.82` (`Panel2`) | `.83` (`Panel3`) | Tower Total (`Mbps`) | `p99` RTT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `GUARIDA_STOCK_AGGR_COLLAPSE` | `1000 ms` | `4096 B` | `68.10` | `30.28` | `324.78` | `48.20 ms` |
| `GUARIDA_V7_SYNC_67_33` | `500 ms` | `24576 B` | `118.40` | `52.10` | `481.20` | `8.60 ms` |
| **`GUARIDA_V8_CHAMPION`** | **`250 ms`** | **`49152 B`** | **`127.90`** | **`55.30`** | **`498.40` (`+53.46%`)** | **`7.95 ms`** |

## 3. Safety & Topology Compliance
- **Guarida `SG-01` Respected**: Zero live tower interruptions.
