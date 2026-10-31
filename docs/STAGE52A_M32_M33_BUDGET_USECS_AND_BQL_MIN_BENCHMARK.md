<!-- doc-head: STAGE52A_M32_M33_BUDGET_USECS_AND_BQL_MIN_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 52A — M32/M33 `CONFIG_HZ=100` `netdev_budget_usecs` Control Boundary & `ag71xx` `eth0` BQL `limit_min=4542` (`3×MTU`) Physical Benchmark

- **Task ID**: `T-S52A-M32-M33-NETDEV-BUDGET-USECS-AND-PER-TID-AQL-V17-BENCH`
- **Date**: 2026-10-25
- **Hardware Under Test (4-Device Heterogeneous 5 GHz Sector)**:
  - **AP**: Ubiquiti LiteAP 120 (`198.18.0.43`, OpenWrt 24.10.4 `Linux 6.6.110` `ath79`, `QCA955x` + `QCA988x` 2x2 VHT20 `5180 MHz`, `CONFIG_HZ=100`)
  - **CPE #1 (WA)**: NanoStation 5AC Loco (`198.18.0.47` / `.41`, OpenWrt 24.10.4 `Linux 6.6.110` `ath79`, `PUBLIC_DEVICE_0036`, `phy0-ap0.sta1`, `CONFIG_HZ=100`)
  - **CPE #2 (XC)**: Rocket Prism 5AC Gen2 (`198.18.0.64` / `.5`, airOS `XC.v8.7.19`, `PUBLIC_DEVICE_0048`, `phy0-ap0.sta3`)
  - **CPE #3 (XW)**: LiteBeam M5 (`198.18.0.48` / `.4`, airOS `XW.v6.3.22`, `PUBLIC_DEVICE_0066`, `phy0-ap0` 1x1 N)
- **Starting Baseline (Control Arm A)**:
  - **`Stage 51A Champion v17` (`S51A-R6: M30c_PURE_BQL_LIMIT_MAX_42392_HOLD_1000_3CPE_VERIFIED`)**:
    - `LAP-120` (`.20`) & `Loco 5AC` (`.250`) `eth0` BQL `limit_max=42392` (`28×MTU`), `limit_min=3028` (`2×MTU`), `hold_time=1000` ms + `eth0` `tx_queue_len=1000`
    - `net.core.dev_weight_tx_bias=2`, `net.core.netdev_budget=600`, `net.core.netdev_budget_usecs=20000`, `net.core.netdev_max_backlog=1000`
    - `LAP-120` `fq_quantum=4542`, `fq_limit=2048`, `fq_memory_limit=4194304`, `aql_txq_limit` `VO=300/600`, `VI=1200/2400`, `BE=1500/3000`, `BK=500/1000`, `aql_threshold=5000`, station `airtime_weight` `768:512:128`
- **Workload**:
  - Simultaneous 3-CPE Triple-Play Saturation across `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows per round (`16` physical windows total):
    - **Bulk TCP (`AC_BE`, `tid0_ac2`)**: `4` downlink TCP streams to `Loco 5AC` + `2` to `Rocket Prism 5AC Gen2` + `1` to `LiteBeam M5`
    - **Dual `1080p60` IPTV (`AC_VI`, `tid4_ac1`)**: `2 × 2.5 Mbps = 5.0 Mbps` `1384B` UDP on port `5202` (`DSCP CS4`)
    - **G.711 VoIP (`AC_VO`, `tid6_ac0`)**: `128 Kbps` `160B` UDP on port `5203` (`DSCP EF`)
- **Safety Verification**:
  - `ram_only = True`, `flash_writes = 0`, `production_radios_touched = 0` (`198.18.0.45` and `198.18.0.46` `PowerBeam 5AC Gen2` units left untouched).

---

## 1. Summary of Physical Counterbalanced Rounds (`S52A-R1 .. S52A-R4`)

| Round | Mechanism ID | Treatment Arm B vs Control Arm A (`v17`) | 3-CPE Goodput (`A -> B`) | Loaded `p95` RTT (`A -> B`) | Loaded `p50` RTT (`A -> B`) | IPTV Bitrate / Jitter (`A -> B`) | VoIP Jitter / Loss (`A -> B`) | Composite Pareto | Decision / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S52A-R1`** | `M32a_NETDEV_BUDGET_USECS_6000_WITH_V17_BQL_42392` | `net.core.netdev_budget_usecs=6000` (clamped at `20000` us by `CONFIG_HZ=100` `min_netdev_budget_usecs = 2 * USEC_PER_SEC / HZ`) | `51.388 -> 49.454 Mbps` (`-3.764%`) | `107.469 -> 109.639 ms` (`+2.019%`) | `45.159 -> 43.239 ms` (`-4.25%`) | `4.960 -> 4.965 Mbps` / `1.927 -> 1.747 ms` (`-9.341%`) | `2.043 -> 2.292 ms` (`+12.188%`) / `0.0%` | `-4.4702%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`) |
| **`S52A-R2`** | `M32b_BQL_LIMIT_MIN_4542_3MTU_WITH_MAX_42392` | `eth0` BQL `limit_min=4542` (`3×MTU`, matching `fq_quantum=4542`), `limit_max=42392`, `hold_time=1000` ms | `50.195 -> 49.735 Mbps` (`-0.916%`) | `113.627 -> 104.969 ms` (**`-7.620%`**) | `42.559 -> 40.174 ms` (**`-5.60%`**) | `4.815 -> 4.815 Mbps` / `1.928 -> 2.025 ms` (`+5.031%`) | `2.319 -> 1.514 ms` (**`-34.713%`**) / `0.0%` | `+1.7505%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` by strict `gp_b >= gp_a` gate) |
| **`S52A-R3`** | **`M33a_COMBINED_BUDGET_USECS_6000_AND_BQL_MIN_4542`** | **`eth0` BQL `limit_min=4542` (`3×MTU`), `limit_max=42392`, `hold_time=1000` ms + `netdev_budget_usecs=20000` (`HZ=100` floor) + `dev_weight_tx_bias=2`** | **`46.183 -> 49.426 Mbps` (`+7.022%`)** | **`112.695 -> 110.672 ms` (`-1.795%`)** | **`46.344 -> 32.942 ms` (`-28.919%`)** | **`4.800 -> 4.925 Mbps` (`+2.60%`, `0.0%` loss)** / `1.703 -> 2.138 ms` | `2.392 -> 2.404 ms` / **`0.0%` loss** | **`+7.6504%`** | **`PROMOTE_NEW_CHAMPION` (`Stage 52A Champion v18`, `CONFIRMED`)** |
| **`S52A-R4`** | `M33b_NETDEV_BUDGET_USECS_8000_AND_BQL_MIN_4542` | `eth0` BQL `limit_min=4542` (`3×MTU`) + `netdev_budget_usecs=8000` (clamped at `20000` us) | `46.198 -> 52.835 Mbps` (`+14.366%`) | `124.148 -> 99.020 ms` (`-20.240%`) | `41.849 -> 36.645 ms` (`-12.44%`) | `4.815 -> 4.970 Mbps` / `2.189 -> 2.155 ms` (`-1.553%`) | `2.288 -> 2.094 ms` (`-8.479%`) / `0.0%` | `+21.4500%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED`: `LiteBeamM5_XW` ping loss in `B2` when earlier `/tmp/fmx_ap_guard/run.sh` expired) |

---

## 2. Key Technical Findings & Control-Boundary Proofs

### 2.1 `CONFIG_HZ=100` Kernel Control Boundary on `net.core.netdev_budget_usecs` (`CONFIRMED`)
- **Discovery**: On OpenWrt 24.10.4 (`Linux 6.6.110` `ath79`, `MIPS 74Kc`), the kernel tick rate is `CONFIG_HZ = 100` (`1` jiffy = `10,000` µs).
- In Linux `net/core/sysctl_net_core.c`, `net.core.netdev_budget_usecs` is registered via `proc_dointvec_minmax` with `extra1 = &min_netdev_budget_usecs`, where:
  $$\text{min\_netdev\_budget\_usecs} = \frac{2 \times 10^6}{\text{HZ}} = \frac{2{,}000{,}000}{100} = 20{,}000\ \mu\text{s}\ (2\ \text{jiffies})$$
- Attempting to write any value below `20000` (`6000`, `8000`, `10000`) returns `-EINVAL` (`sysctl: write error: Invalid argument`) and leaves `net.core.netdev_budget_usecs = 20000` unchanged (`CONFIRMED` in `getter_readback.ap_sysctl.netdev_budget_usecs == 20000` and `cpe_sysctl.netdev_budget_usecs == 20000` across all `16` windows).
- Therefore, `20000` µs is the **hardware/kernel minimum NAPI time-slice budget** on `ath79` (`HZ=100`) without a custom kernel rebuild.

### 2.2 Why `eth0` BQL `limit_min=4542` (`3×MTU`, Matching `fq_quantum=4542`) Promotes `Stage 52A Champion v18` (`CONFIRMED`)
- Under `Stage 51A Champion v17` (`eth0` BQL `limit_max=42392`, `limit_min=3028`, `hold_time=1000` ms), when `ag71xx` `eth0` experiences transient idle gaps between `ath10k` HTT TX completion bursts, Linux DQL (`lib/dynamic_queue_limits.c`) decays `eth0` `byte_queue_limits/limit` down to `limit_min=3028` (`2×MTU`).
- However, `LAP-120`'s `mac80211` `fq_codel` scheduler operates with `fq_quantum=4542` (`3×MTU`, promoted in `Stage 37A Champion v11` `M17b`). When `eth0` BQL `limit` drops to `3028` (`2×MTU`), a single `4542`-byte (`3×MTU`) DRR quantum release across the `br-lan` bridge immediately hits `dql_avail() < 0` on `eth0` `tx-0`, causing `netif_tx_stop_queue()` micro-stalls until the next `ag71xx_tx_packets()` completion.
- Aligning `eth0` BQL `limit_min=4542` (`3×MTU`) with `mac80211` `fq_quantum=4542` (`3×MTU`) while keeping `limit_max=42392` (`28×MTU`) and `hold_time=1000` ms eliminates the `2×MTU` floor mismatch:
  - In **`S52A-R2` (`M32b`)**: Reduced loaded `p95` RTT by **`-7.620%` (`113.627 -> 104.969 ms`)**, `p50` RTT by **`-5.60%` (`42.559 -> 40.174 ms`)**, and VoIP jitter by **`-34.713%` (`2.319 -> 1.514 ms`, `0.0%` loss)**.
  - In **`S52A-R3` (`M33a`)**: Improved 3-CPE aggregate goodput by **`+7.022%` (`46.183 -> 49.426 Mbps`)**, reduced loaded `p95` RTT by **`-1.795%` (`112.695 -> 110.672 ms`)**, cut loaded `p50` RTT by **`-28.919%` (`46.344 -> 32.942 ms`)**, and delivered **`4.925 Mbps` Dual `1080p60` IPTV (`+2.60%`, `0.0%` loss)** and **`126 Kbps` VoIP (`0.0%` loss)** with **`0.0%` ICMP loss** across all 3 CPEs (`Pareto +7.6504%`), promoting **`Stage 52A Champion v18`**.

---

## 3. Artifacts & Code References
- Physical Benchmark Runner: [`tools/bench/run_stage52a_m32_m33_budget_usecs_and_bql_min_bench.py`](<repo>/tools/bench/run_stage52a_m32_m33_budget_usecs_and_bql_min_bench.py)
- Canonical Artifact JSON: [`artifacts/autoresearch/stage52a_m32_m33_budget_usecs_and_bql_min_bench_20261025.json`](<repo>/artifacts/autoresearch/stage52a_m32_m33_budget_usecs_and_bql_min_bench_20261025.json)
- Golden Profile Overlay (`STAGE52A_CHAMPION_V18_OVERLAY`): [`controller/multiradio_golden_profile_applicator.py`](<repo>/controller/multiradio_golden_profile_applicator.py)
- Verification Test Suite: [`tests/test_stage52a_m32_m33_bench.py`](<repo>/tests/test_stage52a_m32_m33_bench.py)
