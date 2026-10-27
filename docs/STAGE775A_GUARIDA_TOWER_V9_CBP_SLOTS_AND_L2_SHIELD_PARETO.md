<!-- doc-head: STAGE775A_GUARIDA_TOWER_V9_CBP_SLOTS_AND_L2_SHIELD_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 775A — Guarida Tower `v9` (`ff_cbp_slots=4` & L2 Shield) Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`) / `QCA firmware` / `ath10k` / `mac80211` / `Linux`.
- **Tower `v9` Breakthrough**: Integrates `ff_cbp_slots = 4` (`240 us` contention window), `activity_aging = 1500 ms` (**`-54.17%` empty-poll waste reduction** on `Panel2` `.82`), and an L2 bridge filter blocking rogue `UDP 67 -> 68` DHCP offers and `ICMPv6 Type 134` Router Advertisements across the `34`-endpoint Guarida tower.
- **Result**: `GUARIDA_V9_FF_CBP_SLOTS4_AND_L2_SHIELD_CHAMPION` crosses the `500 Mbps` barrier at **`514.80 Mbps` (`+58.51%`)** and **`7.25 ms` `p99` RTT**.

## 2. Guarida Tower `v9` SimPy + NSGA-II Matrix
| Candidate | `ff_cbp_slots` | `activity_aging` | Empty-Poll Reduction | L2 DHCP Shield | Tower Total (`Mbps`) | `p99` RTT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `GUARIDA_STOCK_BASELINE` | `15` (`900 us`) | `5000 ms` | `0.00%` | No | `324.78` | `48.20 ms` |
| `GUARIDA_V8_BASELINE` | `8` (`480 us`) | `2500 ms` | `-31.20%` | Yes | `498.40` | `7.95 ms` |
| **`GUARIDA_V9_CHAMPION`** | **`4` (`240 us`)** | **`1500 ms`** | **`-54.17%`** | **Yes** | **`514.80` (`+58.51%`)** | **`7.25 ms`** |

## 3. Safety & Topology Compliance
- **Guarida `SG-01` Respected**: Zero live tower interruptions.
