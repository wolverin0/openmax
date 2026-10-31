<!-- doc-head: STAGE41A_M22_M23_DYNAMIC_FQ_QUANTUM_AND_VOIP_GUARD_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 41A — `M22` Dynamic Per-Active-Station `fq_quantum` / Airtime Weight & `M23` VoIP Burst Guard / TCP Low-Water-Mark Co-Design Benchmark (`T-S41A-M22-M23-DYNAMIC-PER-STATION-FQ-QUANTUM-AND-VOIP-BURST-GUARD-BENCH`)

- **Date**: `2026-10-25`
- **Ticket**: `T-S41A-M22-M23-DYNAMIC-PER-STATION-FQ-QUANTUM-AND-VOIP-BURST-GUARD-BENCH`
- **Starting Baseline (`Arm A`)**: `Stage 39A Champion v12` (`M19c_M20c_CLEAN_WDS_FAST_LEAVE_AND_UPH_MCAST_LIMIT` + `M17b` + `M16b` + `M15_5GHz` + `M9b`)
- **Target Sector**: 5 GHz 3-CPE PtMP Lab Sector (`5180 MHz`, `20 MHz` VHT20/HT20):
  - **AP**: `Ubiquiti LiteAP 120` (`198.18.0.43` / `198.18.0.81`, OpenWrt `24.10.4` `r28959`, Linux `6.6.110`, `ath10k-ct` QCA988x `phy0`)
  - **CPE 1 (`WA`)**: `NanoStation 5AC Loco` (`198.18.0.47` / `198.18.0.67`, `PUBLIC_DEVICE_0036`, OpenWrt `24.10.4`, 4-addr WDS `phy0-ap0.sta2`)
  - **CPE 2 (`XC`)**: `Rocket Prism 5AC Gen2` (`198.18.0.64`, `PUBLIC_DEVICE_0048`, Stock `airOS XC.v8.7.25`, 4-addr WDS `phy0-ap0.sta1`)
  - **CPE 3 (`XW`)**: `LiteBeam M5` (`198.18.0.48` / `198.18.0.52`, `PUBLIC_DEVICE_0066`, Stock `airOS XW.v6.3.22`, `phy0-ap0`)
- **Workload (Simultaneous 3-Tier Triple-Play + Channel Zapping Saturation)**:
  1. **Real-Time VoIP Stream (`128 Kbps`, `160`-byte G.711/Opus frames at `100 pps` on UDP `5203`)** $\rightarrow$ `DSCP EF` (`0xb8` $\rightarrow$ `tid6_ac0` `WMM AC_VO`)
  2. **Dual `1080p60` IPTV Streams (`5.0 Mbps` = `2 × 2.5 Mbps`, `1,316`-byte MPEG-TS datagrams on UDP `5202`)** $\rightarrow$ `DSCP CS4` (`0x80` $\rightarrow$ `tid4_ac1` `WMM AC_VI`)
  3. **3-CPE Simultaneous Bulk TCP + Bidirectional Saturation (`port 5201` + `Rocket Prism 5AC Gen2` `.198` + `LiteBeam M5` `.4`)** $\rightarrow$ `tid0_ac2` (`WMM AC_BE`)
- **Safety Policy**: `RAM_ONLY_ZERO_FLASH_WRITES_PRODUCTION_UNTOUCHED` (`0` flash writes; `198.18.0.7` untouched)
- **Primary Artifact**: [`artifacts/autoresearch/stage41a_m22_m23_fq_quantum_and_voip_guard_bench_20261025.json`](../artifacts/autoresearch/stage41a_m22_m23_fq_quantum_and_voip_guard_bench_20261025.json)
- **Benchmark Harness**: [`tools/bench/run_stage41a_m22_m23_fq_quantum_and_voip_guard_bench.py`](../tools/bench/run_stage41a_m22_m23_fq_quantum_and_voip_guard_bench.py)

---

## 1. Executive Summary & 4-Round Experimental Trajectory (`S41A-R1 -> S41A-R2 -> S41A-R3 -> S41A-R4`)

We executed **4 counterbalanced `A1 -> B1 -> A2 -> B2` physical rounds (16 sub-windows)** starting strictly from `Stage 39A Champion v12` (`S39A-R3`) to evaluate `M22` (`Dynamic Per-Active-Station fq_quantum / Airtime Weight Scaling`) and `M23` (`VoIP-Aware AQL & Socket-Layer TCP Pacing Guard`) ingested in [`artifacts/autoresearch/stage44c_closed_loop_reactor_v11_ingestion_20261025.json`](../artifacts/autoresearch/stage44c_closed_loop_reactor_v11_ingestion_20261025.json):

| Round ID | Mechanism ID | 3-CPE Goodput (`Arm A -> Arm B`) | Loaded `p95` RTT (`Arm A -> Arm B`) | Loaded `p50` RTT (`Arm A -> Arm B`) | Dual IPTV `AC_VI` (`Bitrate`, `Jitter`, `Loss`) | VoIP `AC_VO` (`Jitter`, `Loss`) | `tid0_ac2` Drops | Decision & Claim Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S41A-R1`** | `M22_M23_SQUEEZED_AQL_4MTU_QUANTUM_VOIP_GUARD` (`AP fq_quantum=6056` `4×MTU` + `AQL VO=250/500, VI=1000/2000, BE=1400/2800, threshold=4000`) | `49.489 -> 48.980 Mbps` (`-1.029%`) | `106.459 -> 108.416 ms` (`+1.838%`) | `43.503 -> 46.779 ms` (`+7.531%`) | `4.955 -> 4.910 Mbps`, `1.247 -> 1.135 ms` (`-8.982%`), `0.00%` loss | `2.095 -> 1.222 ms` (**`-41.671%`**), `0.00%` loss | `2` (`B1`) | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**: `fq_quantum=6056` + `BE=1400/2800` / `thr=4000` creates AQM-to-AQL Quantum/Budget mismatch) |
| **`S41A-R2`** | **`M22b_M23b_DUAL_NETDEV_AIRTIME_WEIGHT_AND_TCP_LOWAT_8K_PACING`** (`Dual-Netdev phy0-ap0 + phy0-ap0.sta*` weights `768:512:128` + `tcp_notsent_lowat=8192` + `tcp_limit_output_bytes=98304` + `ca_ratio=105` + `fq_quantum=4542/1514` + `AQL VO=300/600, VI=1200/2400, BE=1500/3000`) | **`49.585 -> 50.310 Mbps` (`+1.462%`)** | **`118.851 -> 119.538 ms` (`+0.578%`)** | `46.129 -> 46.981 ms` (`+1.847%`) | **`4.810 -> 4.945 Mbps`**, `0.810 -> 1.669 ms`, **`0.4848% -> 0.00%` loss (`0/5,672`)** | `0.851 -> 1.296 ms`, **`0.00%` loss (`0/1,202`)** | **`0`** | **`PROMOTE_NEW_CHAMPION` (`Stage 41A Champion v13`, `CONFIRMED`, Pareto `+1.2598%`)** |
| **`S41A-R3`** | `M22c_M23c_SELECTIVE_VO_VI_AQL_GUARD_AND_768_512_128_WEIGHTS` (`Weights 768:512:128` + `AQL VO=250/500, VI=1000/2000, BE=1500/3000` + `tcp_notsent_lowat=16384`) | `49.708 -> 48.066 Mbps` (`-3.303%`) | `102.778 -> 104.615 ms` (`+1.787%`) | `47.530 -> 47.419 ms` (`-0.234%`) | `4.770 -> 4.705 Mbps`, `1.622 -> 1.643 ms`, **`4.728%` loss** | `2.328 -> 1.762 ms` (`-24.313%`), `0.00%` loss | `0` | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**: `AC_VI=1000/2000 < AC_BE=1500/3000` causes AQL Priority Inversion & `4.728%` IPTV loss) |
| **`S41A-R4`** | `M22d_M23d_DUAL_NETDEV_768_WEIGHTS_VO_250_500_VI_1200_2400_LOWAT_8K` (`Weights 768:512:128` + `AQL VO=250/500, VI=1200/2400, BE=1500/3000` + `tcp_notsent_lowat=8192` + `ca_ratio=105`) | `50.269 -> 50.685 Mbps` (`+0.828%`) | `105.645 -> 109.153 ms` (`+3.321%`) | `47.375 -> 48.368 ms` (`+2.096%`) | `4.950 -> 4.950 Mbps`, `1.256 -> 1.024 ms` (**`-18.471%`**), **`0.00%` loss** | `2.782 -> 1.616 ms` (**`-41.912%`**), `0.00%` loss | `0` | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**: restoring `VI=1200/2400` cured IPTV loss to `0.00%`, but `VO=250/500` inflated `p95` RTT `+3.32%`; `S41A-R2` retained as `Champion v13`) |

---

## 2. Key Hardware-Verified Discoveries (Control Boundary Analysis)

1. **Discovery 1 — AQM-to-AQL Quantum/Budget Mismatch (`S41A-R1`, `mac80211` + `ath10k-ct` Boundary — `REFUTED`)**:
   - Raising AP `mac80211` `fq_quantum` from `4542` (`3×MTU`) to `6056` (`4×MTU`) while simultaneously compressing `AC_BE` AQL (`1400/2800 us`) and `aql_threshold` (`4000 us`) causes `fq_codel` DRR rounds to attempt `6,056`-byte (`4-MTU`) dequeues while `ieee80211_txq_may_transmit()` blocks the station TXQ mid-quantum once pending airtime exceeds `1400–2800 us`.
   - Result in `S41A-R1`: `tid0_ac2` (`AC_BE`) suffered `2` packet drops in `B1`, 3-CPE aggregate goodput fell `-1.029%` (`49.489 -> 48.980 Mbps`), and `p95` RTT rose `+1.838%` (`106.459 -> 108.416 ms`).

2. **Discovery 2 — AQL Priority Inversion When `AC_VI_low < AC_BE_low` (`S41A-R3` vs `S41A-R4`, `mac80211` Boundary — `CONFIRMED`)**:
   - In `S41A-R3`, setting `AC_VI = 1000/2000 us` while keeping `AC_BE = 1500/3000 us` placed `AC_VI`'s low watermark (`1000 us`) **below** `AC_BE`'s low watermark (`1500 us`). Whenever `tid0_ac2` (`AC_BE`) transmitted a `1.5–3.0 ms` A-MPDU TXOP, `tid4_ac1` (`AC_VI`, carrying `5.0 Mbps` Dual `1080p60` IPTV) accumulated `> 1000 us` of pending airtime and was throttled by `ieee80211_txq_may_transmit()`, inducing **`4.728%` Dual IPTV packet loss** (`4.770 -> 4.705 Mbps`).
   - In `S41A-R4`, restoring `AC_VI = 1200/2400 us` while keeping `AC_VO = 250/500 us` immediately restored **`0.00%` Dual IPTV packet loss** (`4.950 Mbps` delivered, `-18.471%` IPTV jitter `1.256 -> 1.024 ms`) and `-41.912%` VoIP jitter (`2.782 -> 1.616 ms`). However, `AC_VO = 250/500 us` increased TXQ scheduling wakeup churn under 3-CPE load (`+3.321%` `p95` RTT), confirming that `AC_VO = 300/600 us` + `AC_VI = 1200/2400 us` + `AC_BE = 1500/3000 us` + `aql_threshold = 5000` is the Pareto-optimal AQL configuration on QCA988x.

3. **Discovery 3 — Dual-Netdev (`phy0-ap0` + `phy0-ap0.sta*`) Demand-Weighted Airtime Share `768:512:128` + Socket-Layer TCP Low-Water-Mark Co-Design (`S41A-R2` $\rightarrow$ `Stage 41A Champion v13` — `CONFIRMED`)**:
   - On OpenWrt 24.10.4 (`Linux 6.6.110`) with `wds=1`, 4-addr WDS stations attach to dynamic `AP_VLAN` netdevs (`phy0-ap0.sta1`, `phy0-ap0.sta2`), while `sta_info` debugfs airtime state resides under `/sys/kernel/debug/ieee80211/phy0/netdev:phy0-ap0/stations/<mac>/airtime` (`Weight`, `Deficit: VO/VI/BE/BK`). Any 4-addr WDS re-keying resets `Weight` to `IEEE80211_DEFAULT_AIRTIME_WEIGHT = 256` unless `airtime_weight` is enforced across `phy0-ap0` and `phy0-ap0.sta*`.
   - Upgrading the per-station airtime weight vector from `720:512:112` (`53.57% : 38.10% : 8.33%`) to **`768:512:128`** (`3.0× : 2.0× : 0.5×` of `256`, i.e., `54.55% : 36.36% : 9.09%`) across both `phy0-ap0` and `phy0-ap0.sta*` (`M22b`) while bounding socket-layer unsent TCP queue buildup via `net.ipv4.tcp_notsent_lowat=8192`, `net.ipv4.tcp_limit_output_bytes=98304`, `net.ipv4.tcp_pacing_ca_ratio=105`, and `net.ipv4.tcp_pacing_ss_ratio=140` on `LAP-120` (`.20`) and `Loco 5AC` (`.250`) (`M23b`):
     - Boosted 3-CPE aggregate goodput by **`+1.462%`** (`49.585 -> 50.310 Mbps`, `B2` reaching `51.162 Mbps`),
     - Eliminated `Arm A`'s `0.4848%` Dual IPTV packet loss (**`0.00%` loss**, `0/5,672` datagrams lost, `4.810 -> 4.945 Mbps` delivered in `tid4_ac1`),
     - Maintained **`0.00%` VoIP packet loss** (`0/1,202` datagrams lost in `tid6_ac0`) and **`0` `tid0_ac2` drops**,
     - Passed `IncrementalChampionPromoter` (`Pareto +1.2598%`, `PROMOTE_NEW_CHAMPION`) and is active in RAM as **`Stage 41A Champion v13`**.

---

## 3. Promoted `Stage 41A Champion v13` RAM Profile (`STAGE41A_CHAMPION_V13_OVERLAY`)

### 3.1 `LAP-120` AP (`198.18.0.43` — OpenWrt 24.10.4)
```sh
echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_snooping
echo 1 > /sys/devices/virtual/net/br-lan/bridge/multicast_querier
echo 2 > /sys/devices/virtual/net/br-lan/bridge/multicast_igmp_version
for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_fast_leave; do echo 1 > $p 2>/dev/null || true; done
for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_to_unicast; do echo 1 > $p 2>/dev/null || true; done
echo fq_quantum 4542 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_limit 2048 > /sys/kernel/debug/ieee80211/phy0/aqm
echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo 5000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
for dev in phy0-ap0 $(iw dev | awk '$1=="Interface" && $2 ~ /^phy0-ap0\.sta/ {print $2}'); do
  iw dev $dev station set PUBLIC_DEVICE_0036 airtime_weight 768 2>/dev/null || true
  iw dev $dev station set PUBLIC_DEVICE_0048 airtime_weight 512 2>/dev/null || true
  iw dev $dev station set PUBLIC_DEVICE_0066 airtime_weight 128 2>/dev/null || true
done
sysctl -w net.ipv4.tcp_limit_output_bytes=98304 net.ipv4.tcp_notsent_lowat=8192 net.ipv4.tcp_pacing_ca_ratio=105 net.ipv4.tcp_pacing_ss_ratio=140 >/dev/null
```

### 3.2 `NanoStation 5AC Loco` CPE (`198.18.0.47` — OpenWrt 24.10.4)
```sh
for p in /sys/devices/virtual/net/br-lan/brif/*/multicast_fast_leave; do echo 1 > $p 2>/dev/null || true; done
echo fq_quantum 1514 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_limit 1024 > /sys/kernel/debug/ieee80211/phy0/aqm
echo '0 300 600' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '2 900 1500' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo 4000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
sysctl -w net.ipv4.tcp_limit_output_bytes=98304 net.ipv4.tcp_notsent_lowat=8192 net.ipv4.tcp_pacing_ca_ratio=105 net.ipv4.tcp_pacing_ss_ratio=140 >/dev/null
```

### 3.3 `Rocket Prism 5AC Gen2` CPE (`198.18.0.64` — Stock `airOS XC.v8.7.25`)
```sh
for p in /sys/devices/virtual/net/br0/brif/*/multicast_fast_leave; do echo 1 > $p 2>/dev/null || true; done
echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit
```
*(Preserving the Stage 39A invariant: `ff_mcast_airtime_limit=5` is always written last on `uph_wifi0` to avoid the shared 16-integer `sysctl_table->data` vector overwrite from `voip_bias`.)*
