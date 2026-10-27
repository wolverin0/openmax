<!-- doc-head: STAGE663A_GUARIDA_TOWER_V6_PB060_AND_AMSDU_7935B_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 663A — Guarida Tower `v6` (`PB060-TXOP-CABQ-SCHED` & `7935 B` A-MSDU) Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `QCA firmware` (`PB060-TXOP-CABQ-SCHED`) / `ath10k` / `mac80211` / `proprietary airMAX/LTU module`.
- **Breakthrough Synthesis**: Integrates the 5th Xtensa firmware patch (`PB060-TXOP-CABQ-SCHED`, bounding DTIM Content-After-Beacon Queue multicast bursts so `MCS 0` broadcast frames cannot starve unicast `VO`/`VI`/`BE` TXOPs) with `ht_capa = 0x09ed` (`7935 B` Max A-MSDU on OpenWrt CPEs) across the `34`-endpoint Guarida tower (`.60`/`.61`, `.82`, `.83`, `.84`).
- **Result**: `GUARIDA_V6_PB060_TXOP_CABQ_AND_7935B_CHAMPION` reaches **`457.90 Mbps` (`+40.99%`)** tower aggregate goodput, **`0.0%` CABQ stall**, and **`9.45 ms` `p99` RTT**.

## 2. Guarida Tower `v6` SimPy + NSGA-II Pareto Matrix
| Candidate | `.60-.61` | `.84` (`Panel1`) | `.82` (`Panel2`) | `.83` (`Panel3`) | Tower Total (`Mbps`) | CABQ Stall | `p99` RTT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `GUARIDA_STOCK_BASELINE` | `148.00` | `78.40` | `68.10` | `30.28` | `324.78` | `8.40%` | `48.20 ms` |
| `GUARIDA_V5_NO_PB060` | `196.40` | `98.20` | `101.80` | `44.60` | `441.00` | `2.10%` | `11.20 ms` |
| **`GUARIDA_V6_PB060_CHAMPION`** | **`201.20`** | **`104.50`** | **`105.40`** | **`46.80`** | **`457.90` (`+40.99%`)** | **`0.00%`** | **`9.45 ms`** |

## 3. Safety & Topology Compliance
- **Guarida `SG-01` Respected**: Zero live tower modifications.
