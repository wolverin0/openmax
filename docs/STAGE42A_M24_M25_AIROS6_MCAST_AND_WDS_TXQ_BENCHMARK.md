<!-- doc-head: STAGE42A_M24_M25_AIROS6_MCAST_AND_WDS_TXQ_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 42A — M24 (`airOS 6 XW` Bridge Queue & EWMA Rate Delegation Guard) and M25 (Direct Sysfs WDS `phy0-ap0*` `tx_queue_len` & Softirq Backlog Co-Design) Physical Bench

- **Task ID**: `T-S42A-M24-M25-PER-TID-QUANTUM-AND-AIROS6-MCAST-GUARD-BENCH`
- **Stage**: `42A`
- **Date**: `2026-10-25`
- **Starting Baseline**: `Stage 41A Champion v13` (`M22b_M23b_DUAL_NETDEV_AIRTIME_WEIGHT_AND_TCP_LOWAT_8K_PACING`, `S41A-R2`)
- **Promoted Champion**: **`Stage 42A Champion v14` (`S42A-R5`: `M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256`, `CONFIRMED`, Pareto `+5.9786%`)**
- **Safety Policy**: Strictly RAM-only (`0` flash writes, `0` production radios touched, counterbalanced `A1 -> B1 -> A2 -> B2` across all 5 physical rounds = `20` sub-windows).

---

## 1. Executive Summary & Three Hardware-Verified Control Boundaries

Starting strictly from **`Stage 41A Champion v13`** (`768:512:128` dual-netdev airtime weights + `tcp_notsent_lowat=8192`, `tcp_limit_output_bytes=98304`, `tcp_pacing_ca_ratio=105`, `tcp_pacing_ss_ratio=140` + `AP fq_quantum=4542`, `CPE fq_quantum=1514` + `AQL VO=300/600, VI=1200/2400, BE=1500/3000, aql_threshold=5000`), Stage 42A evaluated **`M24`** (`airOS 6 XW` `LiteBeam M5` `.251`/`198.18.0.52` bridge/poll tuning) and **`M25`** (OpenWrt `LAP-120` `.20` and `Loco 5AC` `.250` dynamic WDS `phy0-ap0*` `tx_queue_len` and `net.core.netdev_max_backlog` / `tcp_early_retrans` tuning) across 5 counterbalanced `A1 -> B1 -> A2 -> B2` physical rounds (`20` sub-windows) under simultaneous 3-Tier Triple-Play load (`128 Kbps` VoIP in `tid6_ac0` `AC_VO` + `5.0 Mbps` Dual `1080p60` IPTV in `tid4_ac1` `AC_VI` + 3-CPE Bulk TCP in `tid0_ac2` `AC_BE`).

### Three Critical Hardware Control-Boundary Discoveries (`CONFIRMED`)

1. **OpenWrt 24.10 BusyBox `ip link set txqueuelen` Silent Rejection vs Direct Sysfs `/sys/class/net/*/tx_queue_len` (`CONFIRMED`)**:
   - On OpenWrt 24.10 (`LAP-120` `.20` and `Loco 5AC` `.250`, `Linux 6.6.110`), BusyBox `ip link set dev <ifname> txqueuelen <N>` fails with `ip: either "dev" is duplicate, or "txqueuelen" is garbage`.
   - Consequently, in all prior stages (`Stage 1` through `Stage 41A`) and in `S42A-R1`/`S42A-R2`, `/sys/class/net/br-lan/tx_queue_len`, `/sys/class/net/phy0-ap0/tx_queue_len`, `/sys/class/net/phy0-ap0.sta1/tx_queue_len`, `/sys/class/net/phy0-ap0.sta2/tx_queue_len`, and `/sys/class/net/phy0-sta0/tx_queue_len` remained stuck at the kernel default of **`1000` packets**!
   - Writing directly to sysfs (`for q in /sys/class/net/br-lan/tx_queue_len /sys/class/net/phy0-ap0*/tx_queue_len; do echo 256 > $q 2>/dev/null || true; done`) is the only effective mechanism on OpenWrt 24.10 to bound netdev transmit queue lengths across `br-lan`, `phy0-ap0`, and dynamically spawned 4-addr WDS `phy0-ap0.sta*` interfaces.

2. **`airOS 6 XW` (`Linux 2.6.32.68`) Bridge IGMP Snooping Absence & Unpolled `ubnt_poll` Contention (`CONFIRMED`)**:
   - Unlike `airOS 8 XC/WA` (`Linux 3.x`), `LiteBeam M5` (`XW.v6.3.22`, `Linux 2.6.32.68`) is compiled **without `CONFIG_BRIDGE_IGMP_SNOOPING`** (`/sys/devices/virtual/net/br0/bridge/multicast_*` and `/sys/devices/virtual/net/br0/brif/*/multicast_fast_leave` do not exist).
   - Furthermore, writing `txop_params='15 5'`, `no_ack_rate=1`, and `no_auto_prio=1` into `/proc/sys/dev/ubnt_poll/*` when `LiteBeam M5` is associated in standard 802.11n mode to an OpenWrt AP (unpolled mode) degrades 3-CPE aggregate goodput by **`-8.35%`** (`44.523 -> 40.807 Mbps` in `S42A-R1`).
   - Conversely, bounding `ifconfig br0 txqueuelen 256` (`br0_txqueuelen: 1000 -> 256`), `ifconfig ath0 txqueuelen 256`, `ifconfig eth0 txqueuelen 256`, and enabling `echo 1 > /sys/module/ath_rate_atheros/parameters/ubnt_ewma_delegate_on` while keeping `ubnt_poll` in clean unpolled state (`txop_params='0 0'`, `no_ack_rate=0`, `no_auto_prio=0`) (`M24e`) operates cleanly without ACK/TXOP contention.

3. **Single-Core `MIPS 74Kc` `net.core.netdev_max_backlog=2000` Softirq Latency Inflation (`REFUTED` in `S42A-R3`/`S42A-R4`, Resolved in `S42A-R5`)**:
   - Raising `net.core.netdev_max_backlog` from `1000` to `2000` on the single-core `560 MHz` `AR9342` (`MIPS 74Kc`) AP and CPE inflated loaded `p95` RTT by `+2.38%` (`S42A-R3`, with `tx_queue_len=128` + `tcp_early_retrans=4`) and `+29.47%` (`S42A-R4`, `93.497 -> 121.052 ms` with `tx_queue_len=256`).
   - Retaining `net.core.netdev_max_backlog=1000` and `net.ipv4.tcp_early_retrans=3` while isolating pure direct-sysfs `tx_queue_len=256` across `br-lan`, `phy0-ap0`, `phy0-ap0.sta1`, `phy0-ap0.sta2` (AP) and `br-lan`/`phy0-sta0` (CPE) + `M24e` on `LiteBeam M5` (`S42A-R5`) achieved **`+3.21%` aggregate goodput (`45.331 -> 46.785 Mbps`)**, **`-7.92%` `p95` RTT (`104.429 -> 96.161 ms`)**, **`-12.36%` Dual IPTV jitter (`1.902 -> 1.667 ms`, `0.00%` loss)**, and **`-8.11%` VoIP jitter (`2.429 -> 2.232 ms`, `0.00%` loss)**, earning **`PROMOTE_NEW_CHAMPION` (`Stage 42A Champion v14`, Pareto `+5.9786%`)**.

---

## 2. Counterbalanced Physical Benchmark Matrix (`S42A-R1` .. `S42A-R5`)

| Round ID | Mechanism ID | `ap_netdev_tx_queue_len` (`br-lan`/`phy0-ap0*`) | `ap_sysctl` (`backlog` / `early_retrans`) | `LiteBeam M5` (`198.18.0.52`) State | Arm A Mean GP (Mbps) | Arm B Mean GP (Mbps) | GP Delta (%) | Arm A `p95` RTT (ms) | Arm B `p95` RTT (ms) | `p95` Delta (%) | IPTV Jitter A -> B (ms) | VoIP Jitter A -> B (ms) | Pareto Score (%) | Decision / Status |
| :--- | :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S42A-R1`** | `M24_M25_AIROS6_MCAST_POLL_AND_WDS_TXQ_128_BACKLOG_2000` | `1000` (`ip link` rejected `txqueuelen`) | `2000` / `4` | `br0=256`, `txop='15 5'`, `no_ack=1`, `no_auto_prio=1` | `44.523` | `40.807` | `-8.35%` | `103.173` | `91.118` | `-11.68%` | `2.489 -> 1.958` (`-21.33%`) | `2.937 -> 2.442` (`-16.85%`) | `-4.2568%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S42A-R2`** | `M24b_M25b_AIROS6_MCAST_POLL_AND_WDS_TXQ_256_CO_DESIGN` | `1000` (`ip link` rejected `txqueuelen`) | `2000` / `4` | `240s` WPA timer expired | `45.703` | `45.062` | `-1.40%` | `71.539` | `66.872` | `-6.52%` | `1.575 -> 1.562` (`-0.83%`, `0%` loss) | `2.214 -> 2.188` (`-1.17%`) | `+0.8808%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S42A-R3`** | `M24c_M25c_SYSFS_NETDEV_TXQ_128_AND_LBM5_BR0_TXQ_256` | **`128`** (direct sysfs verified) | `2000` / `4` | `br0/ath0/eth0=256`, `ewma=1`, `txop='0 0'` | `43.682` | `43.835` | `+0.35%` | `96.613` | `98.910` | `+2.38%` | `1.157 -> 1.629` (`+40.80%`) | `0.999 -> 1.994` (`+99.60%`) | `-0.4819%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S42A-R4`** | `M24d_M25d_SYSFS_NETDEV_TXQ_256_BACKLOG_2000_AND_LBM5_BR0_TXQ_256` | **`256`** (direct sysfs verified) | `2000` / `3` | `br0/ath0/eth0=256`, `ewma=1`, `txop='0 0'` | `45.254` | `43.895` | `-3.00%` | `93.497` | `121.052` | `+29.47%` | `1.486 -> 1.781` (`+19.85%`) | `1.810 -> 3.165` (`+74.86%`) | `-13.3181%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S42A-R5`** | **`M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256`** | **`256`** (direct sysfs verified) | **`1000` / `3`** | **`br0/ath0/eth0=256`, `ewma=1`, `txop='0 0'`** | **`45.331`** | **`46.785`** | **`+3.21%`** | **`104.429`** | **`96.161`** | **`-7.92%`** | **`1.902 -> 1.667` (`-12.36%`, `0.00%` loss)** | **`2.429 -> 2.232` (`-8.11%`, `0.00%` loss)** | **`+5.9786%`** | **`PROMOTE_NEW_CHAMPION` (`Stage 42A Champion v14`, `CONFIRMED`)** |

---

## 3. Sub-Window Breakdown of Promoted `S42A-R5` (`Stage 42A Champion v14`)

| Sub-Window | Arm | `br-lan` & `phy0-ap0*` `tx_queue_len` | Aggregate Goodput (Mbps) | `Loco 5AC` (`.250`) GP (Mbps) | `Rocket Prism` (`.198`) GP (Mbps) | `LiteBeam M5` (`.251`) GP (Mbps) | Sector `p95` RTT (ms) | Dual IPTV (`tid4_ac1`) Rate / Jitter / Loss | VoIP (`tid6_ac0`) Rate / Jitter / Loss | `tid0_ac2` AQM Drops |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `Stage 41A Champion v13` (Control) | `1000` | `45.454` | `44.394` | `1.028` | `0.032` | `99.513` | `4.97 Mbps` / `2.016 ms` / `0/2845 (0.00%)` | `128 Kbps` / `3.222 ms` / `0/600 (0.00%)` | `0` |
| **`B1`** | **`Stage 42A Champion v14` (Treatment)** | **`256`** | **`46.576`** | **`45.572`** | `0.974` | `0.030` | **`91.237`** | **`4.96 Mbps` / `1.785 ms` / `0/2845 (0.00%)`** | **`128 Kbps` / `2.008 ms` / `0/600 (0.00%)`** | **`0`** |
| **`A2`** | `Stage 41A Champion v13` (Control) | `1000` | `45.208` | `44.167` | `1.009` | `0.032` | `109.345` | `4.95 Mbps` / `1.789 ms` / `0/2833 (0.00%)` | `127 Kbps` / `1.637 ms` / `0/601 (0.00%)` | `1` |
| **`B2`** | **`Stage 42A Champion v14` (Treatment)** | **`256`** | **`46.993`** | **`45.952`** | `1.009` | `0.032` | **`101.086`** | **`4.96 Mbps` / `1.548 ms` / `0/2849 (0.00%)`** | **`128 Kbps` / `2.456 ms` / `0/600 (0.00%)`** | **`0`** |

---

## 4. Promoted `Stage 42A Champion v14` RAM Recipe

- **OpenWrt AP (`LAP-120` `198.18.0.43`)**:
  ```sh
  for q in /sys/class/net/br-lan/tx_queue_len /sys/class/net/phy0-ap0*/tx_queue_len; do echo 256 > $q 2>/dev/null || true; done
  sysctl -w net.core.netdev_max_backlog=1000 net.ipv4.tcp_early_retrans=3 net.ipv4.tcp_limit_output_bytes=98304 net.ipv4.tcp_notsent_lowat=8192 net.ipv4.tcp_pacing_ca_ratio=105 net.ipv4.tcp_pacing_ss_ratio=140 >/dev/null
  ```
- **OpenWrt CPE (`NanoStation 5AC Loco` `198.18.0.47`)**:
  ```sh
  for q in /sys/class/net/br-lan/tx_queue_len /sys/class/net/phy0-sta0/tx_queue_len; do echo 256 > $q 2>/dev/null || true; done
  sysctl -w net.core.netdev_max_backlog=1000 net.ipv4.tcp_early_retrans=3 net.ipv4.tcp_limit_output_bytes=98304 net.ipv4.tcp_notsent_lowat=8192 net.ipv4.tcp_pacing_ca_ratio=105 net.ipv4.tcp_pacing_ss_ratio=140 >/dev/null
  ```
- **`airOS 6 XW` CPE (`LiteBeam M5` `198.18.0.48` / `198.18.0.52`)**:
  ```sh
  ifconfig br0 txqueuelen 256 2>/dev/null || true
  ifconfig ath0 txqueuelen 256 2>/dev/null || true
  ifconfig eth0 txqueuelen 256 2>/dev/null || true
  echo 1 > /sys/module/ath_rate_atheros/parameters/ubnt_ewma_delegate_on 2>/dev/null || true
  ```
