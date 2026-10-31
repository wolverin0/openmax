<!-- doc-head: STAGE37A_TRIPLE_PLAY_IPTV_VOIP_AND_MAC80211_FQ_LIMIT_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 37A — Live 3-CPE 5 GHz Triple-Play (`AC_VO` VoIP + `AC_VI` Dual IPTV + `AC_BE` Bulk TCP) & `mac80211` `fq_limit` Physical Benchmark (`T-S37A-MULTI-STREAM-IPTV-PLUS-VOIP-AC-VO-AND-MAC80211-FQ-LIMIT-BENCH`)

- **Date**: `2026-10-25`
- **Task ID**: `T-S37A-MULTI-STREAM-IPTV-PLUS-VOIP-AC-VO-AND-MAC80211-FQ-LIMIT-BENCH`
- **Hardware Sector**: `LAP-120` AP (`198.18.0.43`, OpenWrt 24.10.4 `r28959`, `QCA988x` 5 GHz `20 MHz` `5180 MHz`) + `NanoStation 5AC Loco` (`198.18.0.47` / `198.18.0.67`, `WA`) + `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC` Stock airOS v8.7.11) + `LiteBeam M5` (`198.18.0.48` / `198.18.0.52`, `XW` Stock airOS v6.3.22)
- **Baseline Starting Point**: **`Stage 36A Champion v10`** (`M16b_IPTV_AC_VI_MAC80211_AQM` + `M15_5GHz` + `M9b`: `fq_quantum=3028/1514`, `fq_memory_limit=4194304`, default `fq_limit=8192`, `airtime_weight = 720:512:112`, `multicast_to_unicast=1`, `ff_mcast_airtime_limit=5`)
- **Safety Verification**: **`0` flash writes** (`flash_writes: 0`, RAM-only `/sys/kernel/debug/ieee80211/phy0/aqm`, `/sys/kernel/debug/ieee80211/phy0/aql_txq_limit`, and `nftables` postrouting DSCP clamp; `0` production radio interactions)
- **Authoritative Receipt**: [`artifacts/autoresearch/stage37a_triple_play_aqm_fq_limit_bench_20261025.json`](../artifacts/autoresearch/stage37a_triple_play_aqm_fq_limit_bench_20261025.json)

---

## 1. Research Question & Physical Control Boundary

In **Stage 36A** (`S36A-R2`, `Stage 36A Champion v10`), we proved that tuning `mac80211`'s internal software TXQ FQ-CoDel quantum (`fq_quantum=3028/1514`, `fq_memory_limit=4194304`) and steering a single `2.5 Mbps` `1080p60` IPTV stream (`DSCP CS4 0x80`) into `tid 4 ac 1` (`WMM AC_VI`) increased sector goodput by `+2.513%` and reduced `p99` RTT by `-8.990%` with `0.00%` video packet loss.

**Stage 37A (`T-S37A-MULTI-STREAM-IPTV-PLUS-VOIP-AC-VO-AND-MAC80211-FQ-LIMIT-BENCH`)** scales the physical benchmark to a full **3-Tier WISP Triple-Play Workload** across all three active `mac80211` / `QCA988x` WMM hardware TXQs simultaneously while bounding `mac80211` internal FQ-CoDel packet queue depth (`fq_limit`):
1. **Tier 1 — VoIP (`WMM AC_VO`, `DSCP EF` / `TOS 0xb8` $\rightarrow$ `tid 6 ac 0`)**: `128 Kbps` (`100 pps`, `160`-byte G.711/Opus payload datagrams on UDP port `5203`).
2. **Tier 2 — Dual `1080p60` IPTV (`WMM AC_VI`, `DSCP CS4` / `TOS 0x80` $\rightarrow$ `tid 4 ac 1`)**: `5.0 Mbps` (`2 × 2.5 Mbps`, `470 pps`, `1,316`-byte `7 × 188B` MPEG-TS payload datagrams on UDP port `5202`).
3. **Tier 3 — 3-CPE Bulk TCP + Flood Saturation (`WMM AC_BE`, `TOS 0x00` $\rightarrow$ `tid 0 ac 2`)**: Bidirectional TCP saturation (`iperf3 --bidir -P 2` on port `5201`) plus simultaneous 3-CPE packet load (`Loco 5AC` `.250`, `Rocket Prism 5AC Gen2` `.198`, and `LiteBeam M5` `.251`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Physical Benchmark Results

| Round ID | Mechanism ID | Control Arm A | Treatment Arm B | Arm A Goodput | Arm B Goodput | Goodput $\Delta$ | Arm A `p95` RTT | Arm B `p95` RTT | `p95` RTT $\Delta$ | Arm A `p50` RTT | Arm B `p50` RTT | Dual IPTV (`tid4_ac1`) Loss / Jitter | VoIP (`tid6_ac0`) Loss / Jitter | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S37A-R1`** | `M17_MAC80211_FQ_LIMIT_TRIPLE_PLAY` | `Champion v10` (`fq_limit=8192`, `fq_quantum=3028/1514`, VoIP in `AC_BE` + Dual IPTV in `AC_VI`) | `fq_limit=2048/1024` + 3-Tier WMM TXQ Isolation (`VoIP EF -> tid6_ac0`, `Dual IPTV CS4 -> tid4_ac1`, `fq_quantum=3028/1514`, `AC_VO aql=600/1200`) | `51.650 Mbps` | `49.776 Mbps` | `-3.628%` | `120.232 ms` | `116.591 ms` | **`-3.028%`** | `46.846 ms` | `49.414 ms` | `3.18% -> 2.31%` loss / **`1.180 -> 0.687 ms` (`-41.78%`)** | **`0.00%` loss** / **`2.220 -> 1.113 ms` (`-49.87%`)** | `RETAIN_CURRENT_CHAMPION` (`REFUTED` for `fq_quantum=3028`) |
| **`S37A-R2`** | `M17b_MAC80211_FQ_LIMIT_TRIPLE_PLAY_QUANTUM_VO_AQL` | `Champion v10` under Triple-Play (`fq_limit=8192`, `fq_quantum=3028/1514`, `AC_VO aql=600/1200`, `VoIP EF -> tid6_ac0`, `Dual IPTV CS4 -> tid4_ac1`) | **`Stage 37A Champion v11`** (`fq_limit=2048/1024`, AP `fq_quantum=4542` `3×MTU`, `AC_VO aql=300/600 us`, `nftables` `cs4`+`ef` clamp) | `49.657 Mbps` | **`50.972 Mbps`** | **`+2.648%`** | `110.720 ms` | **`106.537 ms`** | **`-3.778%`** | `53.638 ms` | **`41.595 ms` (`-22.45%`)** | **`0.00%` loss** (`0/5,684` pkts, `4.945 Mbps`) / `1.878 ms` | **`0.00%` loss** (`0/1,198` pkts, `127.5 Kbps`) / `2.328 ms` | **`PROMOTE_NEW_CHAMPION` (`Champion v11`, Pareto `+3.971%`)** |

---

## 3. Causal Diagnosis: Why `S37A-R1` Preempted `AC_BE` A-MPDUs and Why `S37A-R2` (`M17b`) Solved It

1. **What Happened in `S37A-R1` (`M17_MAC80211_FQ_LIMIT_TRIPLE_PLAY`)**:
   - Steering `128 Kbps` VoIP (`100 pps` of `160`-byte datagrams) from `AC_BE` (`tid0_ac2`) into `WMM AC_VO` (`tid6_ac0`, `DSCP EF 0xb8`) alongside `fq_limit=2048/1024` slashed VoIP jitter in half (**`2.220 -> 1.113 ms`, `-49.865%`**) with **`0.00%` VoIP loss** (`0/1,188` packets), slashed Dual IPTV jitter by **`-41.780%`** (**`1.180 -> 0.687 ms`**), reduced Dual IPTV loss (`3.1822% -> 2.3136%`), and lowered loaded 3-CPE `p95` RTT by **`-3.028%`** (`120.232 -> 116.591 ms`).
   - **However**, because `WMM AC_VO` (`CWmin=3, CWmax=7, AIFSN=2`) wins internal EDCA contention `100` times per second (`every 10 ms`) and `Dual IPTV` (`WMM AC_VI`, `CWmin=7, CWmax=15, AIFSN=2`) wins contention `470` times per second, `tid0_ac2` (`AC_BE`) is frequently preempted. With `LAP-120` AP `fq_quantum = 3028` (`2 × MTU`) and `AC_VO aql_txq_limit = 600/1200 us`, each DRR round of `tid0_ac2` only released `2` TCP segments before yielding, causing shorter `AC_BE` A-MPDUs and a `-3.628%` bulk TCP goodput dip (`51.650 -> 49.776 Mbps`).
2. **Changed Hypothesis Verified in `S37A-R2` (`M17b_MAC80211_FQ_LIMIT_TRIPLE_PLAY_QUANTUM_VO_AQL` $\rightarrow$ `Stage 37A Champion v11`)**:
   - Under active 3-tier Triple-Play hardware contention (`tid6_ac0` + `tid4_ac1` + `tid0_ac2`), increasing `LAP-120` AP `fq_quantum` from `3028` (`2 × MTU`) to **`4542` (`3 × MTU`)** (`echo fq_quantum 4542 > /sys/kernel/debug/ieee80211/phy0/aqm`), bounding `fq_limit` to **`2048`** (`LAP-120`) and **`1024`** (`Loco 5AC`), and tightening `AC_VO` (`ac 0`) AQL from `600/1200 us` to **`300/600 us`** (`echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit`):
     - Increases 3-CPE aggregate goodput from **`49.657 Mbps` to `50.972 Mbps` (`+2.648%`)** (`B1 = 50.515 Mbps`, `B2 = 51.430 Mbps` vs `A1 = 50.150 Mbps`, `A2 = 49.165 Mbps`),
     - Cuts loaded 3-CPE `p95` RTT from **`110.720 ms` to `106.537 ms` (`-3.778%`)**,
     - Cuts loaded 3-CPE `p50` RTT from **`53.638 ms` to `41.595 ms` (`-22.452%`)**,
     - Delivers **`0.00%` packet loss** on Dual `1080p60` IPTV (`0 / 5,684` datagrams lost across `B1` + `B2`, `4.945 Mbps` delivered, `1.878 ms` jitter) and **`0.00%` packet loss** on VoIP (`0 / 1,198` datagrams lost across `B1` + `B2`, `127.5 Kbps` delivered, `2.328 ms` jitter).

---

## 4. Hardware Per-Station 3-Tier TXQ Verification (`/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0.sta2/stations/PUBLIC_DEVICE_0036/aqm`)

| Phase (`S37A-R2`) | `tid0_ac2` (`WMM AC_BE` Bulk TCP) Packets / Bytes | `tid4_ac1` (`WMM AC_VI` Dual `1080p60` IPTV) Packets / Bytes | `tid6_ac0` (`WMM AC_VO` `128 Kbps` VoIP) Packets / Bytes | Dual IPTV Delivered / Loss / Jitter | VoIP Delivered / Loss / Jitter | 3-CPE Goodput | 3-CPE `p50` / `p95` RTT |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1` (`Champion v10`)** | `18,945 pkts` / `26.70 MB` | `2,847 pkts` / `3.94 MB` | `601 pkts` / `136.9 KB` | `4.95 Mbps` / `0/2,845 (0.00%)` / `1.097 ms` | `127 Kbps` / `0/600 (0.00%)` / `1.579 ms` | `50.150 Mbps` | `51.285 ms` / `109.187 ms` |
| **`B1` (`Champion v11`)** | `19,445 pkts` / `27.22 MB` | `2,841 pkts` / `3.93 MB` | `601 pkts` / `136.9 KB` | `4.94 Mbps` / `0/2,839 (0.00%)` / `1.679 ms` | `128 Kbps` / `0/600 (0.00%)` / `2.067 ms` | **`50.515 Mbps`** | **`43.492 ms`** / `111.643 ms` |
| **`A2` (`Champion v10`)** | `18,604 pkts` / `26.45 MB` | `2,828 pkts` / `3.91 MB` | `600 pkts` / `136.6 KB` | `4.94 Mbps` / `0/2,826 (0.00%)` / `0.633 ms` | `127 Kbps` / `0/599 (0.00%)` / `1.233 ms` | `49.165 Mbps` | `55.990 ms` / `112.253 ms` |
| **`B2` (`Champion v11`)** | `19,804 pkts` / `28.06 MB` | `2,847 pkts` / `3.94 MB` | `599 pkts` / `136.4 KB` | `4.95 Mbps` / `0/2,845 (0.00%)` / `2.077 ms` | `127 Kbps` / `0/598 (0.00%)` / `2.589 ms` | **`51.430 Mbps`** | **`39.698 ms` / `101.430 ms`** |

---

## 5. Exact `Stage 37A Champion v11` RAM Profile (`STAGE37A_CHAMPION_V11_OVERLAY`)

- **OpenWrt `LAP-120` AP (`198.18.0.43`)**:
  ```sh
  echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_snooping
  echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_querier
  for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_to_unicast; do echo 1 > $p 2>/dev/null || true; done
  echo fq_quantum 4542 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_limit 2048 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo 5000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
  nft delete table inet fmx_iptv_qos 2>/dev/null || true
  nft add table inet fmx_iptv_qos
  nft 'add chain inet fmx_iptv_qos mangle_out { type filter hook postrouting priority -150; policy accept; udp dport 5202 ip dscp set cs4 counter; udp dport 5203 ip dscp set ef counter; }'
  ```
- **OpenWrt `NanoStation 5AC Loco` CPE (`198.18.0.47` / `198.18.0.67`)**:
  ```sh
  echo fq_quantum 1514 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo fq_limit 1024 > /sys/kernel/debug/ieee80211/phy0/aqm
  echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '2 900 1500' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
  echo 4000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
  ```
- **Stock airOS `Rocket Prism 5AC Gen2` CPE (`198.18.0.64`)**:
  ```sh
  echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit
  ```
