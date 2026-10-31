<!-- doc-head: STAGE36A_LIVE_IPTV_AC_VI_AND_DMS_PTMP_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 36A — Live 3-CPE 5 GHz IPTV-Under-Bulk-Saturation (`WMM AC_VI` + Per-AC AQL + Direct `mac80211` `aqm` Quantum) Physical Benchmark

- **Task ID**: `T-S36A-LIVE-IPTV-AC-VI-DMS-AND-HLS-PACING-PTMP-BENCH`
- **Date**: `2026-10-25`
- **Author**: `subagent:bench-runner`
- **Persistence Mode**: **`0` Flash Writes (`100%` RAM-Only across all physical bench radios)**
- **Authoritative Receipt**: [`artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json`](../artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json)
- **Benchmark Runner**: [`tools/bench/run_stage36a_live_iptv_ac_vi_ptmp_bench.py`](../tools/bench/run_stage36a_live_iptv_ac_vi_ptmp_bench.py)

---

## 1. Executive Summary & Research Question

**Research Question**: Can a 20 MHz 5 GHz PtMP sector (`LAP-120` `.20` serving `NanoStation 5AC Loco` `.250`, `Rocket Prism 5AC Gen2` `.198`, and `LiteBeam M5` `.251`) sustain a live `3.5 Mbps` HEVC 1080p60 IPTV stream (`1,316`-byte MPEG-TS UDP datagrams = 7×188B TS cells) with **`0.00%` packet loss** and **sub-3ms jitter** during simultaneous 3-CPE bulk TCP saturation by isolating IPTV into `WMM AC_VI` (`DSCP CS4 0x80` -> `UP 4` -> `TID 4` -> `AC 1`) with dedicated per-AC AQL limits on top of `Stage 35A Champion v9`?

### Two-Round Counterbalanced Physical Progression (`S36A-R1 -> S36A-R2`)

1. **`S36A-R1` (`M16_IPTV_AC_VI` — Squeezing `AC_BE` from `1500/3000` to `1000/2000` with `aql_threshold=4000` -> `RETAIN_CURRENT_CHAMPION`, `REFUTED`)**:
   - **What Happened**: Routing the `3.5 Mbps` IPTV stream into `TID 4 AC 1` (`WMM AC_VI`, `1200/2400 us`) while tightening `AC_BE` to `1000/2000 us` (`aql_threshold=4000 us`) delivered **`100%` of IPTV datagrams (`0/3,985` lost = `0.00%` loss)** and cut loaded 3-CPE sector `p95` RTT by **`-13.351%` (`83.731 -> 72.552 ms`)** and `p99` RTT by **`-13.054%` (`92.710 -> 80.608 ms`)**.
   - **Why It Was Rejected by the Pareto Guard**: Lowering `AC_BE` below `1500/3000 us` starved 2-MTU bulk TCP A-MPDU aggregation (`69.077 -> 64.777 Mbps`, **`-6.225%`**), independently re-confirming our Stage 30A `S30A-R2` physical law (`2 × 1514B = 3028B` + RTS/CTS at `78 Mbps` requires `~1,450 us` of airtime).
   - **Hardware Diagnostic Uncovered During `S36A-R1`**: Inspecting `/sys/kernel/debug/ieee80211/phy0/aqm` on `LAP-120` and `Loco 5AC` revealed that on OpenWrt 24.10.4 (`Linux 6.6.110`), `/sys/kernel/debug/ieee80211/phy0/aqm` is a **single debugfs file** (not a directory) that requires `echo fq_quantum 3028 > /sys/kernel/debug/ieee80211/phy0/aqm` and `echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm`. Because `tc` is not installed on the 64 MB RAM image and `phy0-ap0` uses `mac80211`'s internal `fq` TXQ, previous `tc qdisc replace ... 2>/dev/null || true` calls were no-ops, leaving `fq_quantum = 300` bytes (`0.2` MTU) and `fq_memory_limit = 16777216` (`16 MB`).

2. **`S36A-R2` (`M16b_IPTV_AC_VI_MAC80211_AQM` — Preserving `AC_BE=1500/3000` (`aql_threshold=5000`) + `WMM AC_VI` IPTV Isolation (`TID 4 AC 1`, `1200/2400`) + Direct `mac80211` `aqm` Programming `fq_quantum 3028/1514` & `fq_memory_limit 4194304` -> `PROMOTE_NEW_CHAMPION` / `Stage 36A Champion v10`, `CONFIRMED`)**:
   - **Aggregate 3-CPE Goodput**: **`55.352 -> 56.743 Mbps` (`+2.513%`, peaking at `57.756 Mbps` in `B1`)**
   - **Loaded 3-CPE Sector `p95` RTT**: **`79.268 -> 76.593 ms` (`-3.375%`)**
   - **Loaded 3-CPE Sector `p99` RTT**: **`94.423 -> 85.934 ms` (`-8.990%`)**
   - **IPTV Stream Delivery (`3.5 Mbps` HEVC 1080p60 Profile)**: **`3.470 Mbps` delivered (`0/3,980` lost datagrams = `0.00%` loss, `1.591–2.510 ms` jitter = `<0.15` of a `16.67 ms` 60fps video frame)**
   - **Kernel `mac80211` Per-TID TXQ Verification (`/sys/kernel/debug/ieee80211/phy0/netdev:*/stations/*/aqm`)**:
     - In `Arm A` (`A1`, `A2`), `tid4_ac1` (`WMM AC_VI`) transmitted **`0` packets**, and all IPTV + bulk TCP packets (`24,819` packets in `A1`, `24,054` packets in `A2`) collided in `tid0_ac2` (`WMM AC_BE`).
     - In `Arm B` (`B1`, `B2`), `tid4_ac1` (`WMM AC_VI`) cleanly isolated **`1,993` packets (`2,757,000` bytes) in `B1`** and **`1,989` packets (`2,751,464` bytes) in `B2`** with **`0` drops, `0` marks, and `0` overlimits**, while `tid0_ac2` (`WMM AC_BE`) carried `23,944` (`B1`) and `23,287` (`B2`) bulk TCP packets with **`0` drops**!

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Summary Table (`S36A-R1` & `S36A-R2`)

| Round | Mechanism ID | `Arm A` (Control) | `Arm B` (Treatment) | Aggregate Goodput (`A -> B`) | Sector `p95` RTT (`A -> B`) | Sector `p99` RTT (`A -> B`) | IPTV Loss / Bitrate / Jitter (`B`) | Verdict |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`S36A-R1`** | `M16_IPTV_AC_VI` | `Champion v9` + `AQL 1500/3000` + IPTV in `AC_BE` (`fq_quantum=300`) | `DSCP CS4 -> AC_VI (1200/2400)` + `AC_BE=1000/2000` (`thresh=4000`) | `69.077 -> 64.777 Mbps` (`-6.225%`) | **`83.731 -> 72.552 ms` (`-13.351%`)** | **`92.710 -> 80.608 ms` (`-13.054%`)** | **`0.00%` loss** · `3.48 Mbps` · `2.157 ms` (`1.814 ms` in `B2`) | **`RETAIN_CURRENT_CHAMPION` (`REFUTED` — `AC_BE=1000/2000` starves 2-MTU TCP)** |
| **`S36A-R2`** | **`M16b_IPTV_AC_VI_MAC80211_AQM`** | `Champion v9` + `fq_quantum=300` + IPTV in `AC_BE` (`TID 0 AC 2`) | **`DSCP CS4 -> AC_VI (1200/2400)` + `AC_BE=1500/3000` (`thresh=5000`) + `mac80211 aqm fq_quantum=3028/1514` & `fq_memory_limit=4MB`** | **`55.352 -> 56.743 Mbps` (`+2.513%`)** | **`79.268 -> 76.593 ms` (`-3.375%`)** | **`94.423 -> 85.934 ms` (`-8.990%`)** | **`0.00%` loss** · `3.47 Mbps` · `2.050 ms` (`1.591 ms` in `B2`) | **`PROMOTE_NEW_CHAMPION` (`Stage 36A Champion v10`, `CONFIRMED`, Pareto `+3.694%`)** |

---

## 3. Exact `Stage 36A Champion v10` RAM Configuration (Active on Physical Bench, `0` Flash Writes)

### 3.1 `LAP-120` 5 GHz Sector AP (`198.18.0.43`, OpenWrt 24.10.4 `Linux 6.6.110`)
```sh
# 1. Direct mac80211 internal FQ-CoDel TXQ programming (2-MTU AP quantum + 4 MB RAM ceiling)
echo fq_quantum 3028 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm

# 2. Per-AC AQL Isolation (VO=600/1200, VI=1200/2400 for IPTV, BE=1500/3000 for 2-MTU TCP, BK=500/1000)
echo '0 600 1200' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo 5000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold

# 3. 4-Addr WDS Bridge Multicast-to-Unicast (DMS) & Snooping across all dynamic phy0-ap0.sta* ports
echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_snooping
echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_querier
for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_to_unicast; do echo 1 > $p 2>/dev/null || true; done

# 4. IPTV DSCP CS4 (0x80 -> UP 4 -> TID 4 -> WMM AC_VI txq_id=1) classification
nft delete table inet fmx_iptv_qos 2>/dev/null || true
nft add table inet fmx_iptv_qos
nft 'add chain inet fmx_iptv_qos mangle_out { type filter hook postrouting priority -150; policy accept; udp dport 5202 ip dscp set cs4 counter; }'
```

### 3.2 `NanoStation 5AC Loco` CPE #1 (`198.18.0.47`, OpenWrt 24.10.4 `Linux 6.6.110`)
```sh
echo fq_quantum 1514 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
echo '0 600 1200' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '2 900 1500' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo 4000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
```

### 3.3 `Rocket Prism 5AC Gen2` CPE #2 (`198.18.0.64`, `airOS 8 XC.v8.7.19`)
```sh
echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit
```
