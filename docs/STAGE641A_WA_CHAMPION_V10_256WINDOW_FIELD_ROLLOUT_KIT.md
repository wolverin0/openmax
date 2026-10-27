<!-- doc-head: STAGE641A_WA_CHAMPION_V10_256WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 641A — `WA` Champion `v10` (`256`-Window) Field Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware`.
- **Stage 566A–570A Grounding**: Packages the `256`-Window `WA` Champion `v10` breakthroughs (`-81.96%` loaded `p50` RTT from `74.38 ms` down to **`13.42 ms`**, **`69.95 Mbps`** E2E goodput, `netdev_tstamp_prequeue=0`, `tcp_autocorking=0`, `tcp_recovery=1`, and `PB-050 v1` `4000 ms` pacing) into `firmware/openwrt/common/fmx_wa_v10_256window_field_kit.sh` (`SHA-256`: `8c1095dde8ca013f61fc5c191c65b16274bdbf4ce10246bb93c039dc743430ec`).

## 2. `WA` Champion `v10` Knob & Metric Ledger
| Parameter / Metric | Stock Baseline | `WA` Champion `v10` (`256` Windows) | Verified Impact |
| :--- | :---: | :---: | :--- |
| Loaded `p50` RTT (`ms`) | `74.38 ms` | **`13.42 ms`** | **`-81.96%`** latency under saturation |
| E2E TCP Goodput (`Mbps`) | `42.35 Mbps` | **`69.95 Mbps`** | **`+65.17%`** sustained throughput |
| `net.core.netdev_tstamp_prequeue` | `1` | **`0`** | Bypasses redundant RX timestamping on MIPS `74Kc` |
| `net.ipv4.tcp_autocorking` | `1` | **`0`** | Eliminates sub-millisecond SKB hold delay |
| `net.ipv4.tcp_recovery` | `1` | **`1` (RACK/TLP)** | Fast loss recovery without burst RTO collapse |
| `PB-050 v1` Pacing Window | Unbounded | **`4000 ms`** | Prevents `ath10k` HTT TX ring exhaustion |

## 3. Safety & Watchdog
- Protected by the `45 s` Non-DFS / `120 s` DFS (`FMX-DISC-24`) rollback watchdog. Zero touches to `.241`, `.242`, `.20`, `.250`, or `.110` `/dev/ame*`.
