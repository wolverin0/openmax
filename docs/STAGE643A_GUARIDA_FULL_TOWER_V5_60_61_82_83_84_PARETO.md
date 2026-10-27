<!-- doc-head: STAGE643A_GUARIDA_FULL_TOWER_V5_60_61_82_83_84_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 643A — Guarida Full-Tower `v5` (`.60`/`.61`, `.82`, `.83`, `.84`) Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module`.
- **Full-Tower `v5` Synthesis**: Combines all verified Guarida (`34` endpoints: `32` CPEs + `2` backbone `.60`/`.61`) breakthroughs into a unified SimPy + `pymoo` NSGA-II Pareto model:
  1. **Backbone `.60 <-> .61`**: `+10 MHz` center-frequency shift dodging the Subcarrier-51 (`+15.9375 MHz`) mixer spur + `ast_rxorn` IRQ/NAPI rescue (`148.0 -> 196.40 Mbps`).
  2. **`Panel1` `.84` (`OpenWrt`)**: Per-peer `ht_capa = 0x09ed` (`7935 B` Max A-MSDU) on OpenWrt CPEs + `3839 B` (`0x01ad`) on Stock CPE (`78.40 -> 98.20 Mbps`, `+25.26%`).
  3. **`Panel2` `.82` (`22` CPEs)**: `cbp_dur=900us` amortizing the `39 us` (`rtt_us + 21`) TDMA slot guard from `26.0%` down to `4.33%` (`68.10 -> 101.80 Mbps`).
  4. **`Panel3` `.83` (`6` CPEs)**: `cbp_dur=900us` + MCS 2 `local_enqued` storm suppression (`30.28 -> 44.60 Mbps`).

## 2. Full-Tower Pareto Matrix
| Candidate | `.60-.61` (`Mbps`) | `.84` (`Mbps`) | `.82` (`Mbps`) | `.83` (`Mbps`) | Tower Total (`Mbps`) | `p99` RTT (`ms`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| `GUARIDA_STOCK_UNCOORDINATED` | `148.00` | `78.40` | `68.10` | `30.28` | `324.78` | `48.20` |
| `GUARIDA_V4_COOP_CBP900` | `182.50` | `88.10` | `94.20` | `41.22` | `406.02` | `13.45` |
| **`GUARIDA_V5_FULL_TOWER_CHAMPION`** | **`196.40`** | **`98.20`** | **`101.80`** | **`44.60`** | **`441.00` (`+35.78%`)** | **`11.20`** |

## 3. Safety & Topology Compliance
- **Guarida `SG-01` Respected**: Zero live tower touches.
