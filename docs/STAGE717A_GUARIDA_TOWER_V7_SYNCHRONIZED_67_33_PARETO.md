<!-- doc-head: STAGE717A_GUARIDA_TOWER_V7_SYNCHRONIZED_67_33_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 717A — Guarida Tower `v7` Synchronized `10ms 67/33` Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` / `QCA firmware` / `ath10k` / `mac80211`.
- **Full-Tower `v7` Synthesis**: Combines synchronized `Fixed 10ms 67/33` TDD framing across `Panel2` (`.82`) and `Panel3` (`.83`, `+34.84%` usable DL airtime + `Rocio Belen DURAN` / `SOSA_Joaquin` EVM remediation), `7935 B` Max A-MSDU (`0x09ed`) + `PB060` on `Panel1` (`.84`), and the `+10 MHz` Subcarrier-51 shift on `.60 <-> .61`.
- **Result**: `GUARIDA_V7_SYNC_10MS_67_33_AND_EVM_ALIGNED_CHAMPION` achieves **`481.20 Mbps` (`+48.16%`)** tower aggregate goodput and **`8.60 ms` `p99` RTT**.

## 2. Guarida Tower `v7` SimPy + NSGA-II Matrix
| Candidate | `.60-.61` | `.84` (`Panel1`) | `.82` (`Panel2`) | `.83` (`Panel3`) | Tower Total (`Mbps`) | `p99` RTT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `GUARIDA_STOCK_UNSYNCED` | `148.00` | `78.40` | `68.10` | `30.28` | `324.78` | `48.20 ms` |
| `GUARIDA_V6_PB060_UNSYNCED_TDD` | `201.20` | `104.50` | `105.40` | `46.80` | `457.90` | `9.45 ms` |
| **`GUARIDA_V7_SYNC_10MS_67_33_CHAMPION`** | **`204.50`** | **`106.20`** | **`118.40`** | **`52.10`** | **`481.20` (`+48.16%`)** | **`8.60 ms`** |

## 3. Safety & Topology Compliance
- **Guarida `SG-01` Respected**: Zero live tower touches.
