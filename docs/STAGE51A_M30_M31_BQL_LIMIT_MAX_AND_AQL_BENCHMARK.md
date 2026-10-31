<!-- doc-head: Stage 51A physical benchmark report for M30 ag71xx BQL sweetspot (limit_max=42392, limit_min=3028, hold_time=1000) and M31 ath10k per-AC AQL co-design under dev_weight_tx_bias=2 -->
Stage 51A counterbalanced 3-CPE 5 GHz Triple-Play benchmark report (`S51A-R1 .. S51A-R6`, 24 physical windows).
Promotes `S51A-R6` (`M30c_PURE_BQL_LIMIT_MAX_42392_HOLD_1000_3CPE_VERIFIED`) as `Stage 51A Champion v17` (`+6.611%` goodput, `-6.102%` p95 RTT, `-20.977%` IPTV jitter, `-34.685%` VoIP jitter, Pareto `+8.7464%`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 51A Physical Benchmark Report — `M30` (`ag71xx` `eth0` BQL `limit_max=42392` / `36336` Sweetspot) & `M31` (`ath10k` `AC_VI` AQL Headroom & `dev_weight=80` Co-Design) (`T-S51A-M30-M31-BQL-LIMIT-MAX-36288-AND-PER-AC-AQL-TX-BIAS-BENCH`)

- **Date**: `2026-10-26T01:11:54Z`
- **Task ID**: `T-S51A-M30-M31-BQL-LIMIT-MAX-36288-AND-PER-AC-AQL-TX-BIAS-BENCH`
- **Starting Baseline**: **`Stage 46A Champion v16` (`S46A-R3`: `M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`)**
- **Hardware Topology**:
  - **AP**: `LAP-120` (`198.18.0.43` / `PUBLIC_DEVICE_0091%29`, OpenWrt 24.10.4 `Linux 6.6.110`, `QCA988x` 5 GHz `20 MHz` `5180 MHz`, `4addr WDS`)
  - **CPE 1 (`WA`)**: `NanoStation 5AC Loco` (`198.18.0.47` / `198.18.0.67`, OpenWrt 24.10.4 `Linux 6.6.110`, `phy0-ap0.sta2`, `airtime_weight = 768`)
  - **CPE 2 (`XC`)**: `Rocket Prism 5AC Gen2` (`198.18.0.64` / `198.18.0.68`, Stock `airOS 8` `XC.v8.7.11`, `phy0-ap0.sta1`, `airtime_weight = 512`)
  - **CPE 3 (`XW`)**: `LiteBeam M5` (`198.18.0.48` / `198.18.0.52`, Stock `airOS 6` `XW.v6.3.22`, `phy0-ap0`, `airtime_weight = 128`)
- **Safety & Execution Policy**:
  - `100%` RAM-only (`0` flash writes; `0` production radios touched).
  - Counterbalanced `A1 -> B1 -> A2 -> B2` design (`6` rounds × `4` windows = `24` physical windows) under simultaneous 3-Tier Triple-Play saturation (`128 Kbps` `DSCP EF` VoIP in `tid6_ac0` `WMM AC_VO` + `5.0 Mbps` Dual `1080p60` `DSCP CS4` IPTV in `tid4_ac1` `WMM AC_VI` + 3-CPE Simultaneous Bulk TCP in `tid0_ac2` `WMM AC_BE`).

---

## 1. Executive Summary & Counterbalanced Results (`S51A-R1 .. S51A-R6`)

| Round ID | Mechanism ID | Goodput (`Arm A -> Arm B`) | Goodput $\Delta$ | Loaded `p95` RTT (`Arm A -> Arm B`) | `p95` RTT $\Delta$ | Dual IPTV Jitter (`Arm A -> Arm B`) | VoIP Jitter (`Arm A -> Arm B`) | Pareto Score $\Delta$ | Verdict & Claim Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S51A-R1`** | `M30a_AP_BQL_LIMIT_MAX_36336_MIN_3028_HOLD_750_WITH_TX_BIAS_2` | `37.376 -> 40.910 Mbps` | `+9.455%` | `106.593 -> 111.941 ms` | `+5.017%` | `2.023 -> 2.537 ms` (`+25.41%`) | `2.458 -> 2.527 ms` (`+2.81%`) | `+7.6992%` | **`RETAIN_CURRENT_CHAMPION` (`REFUTED`)** |
| **`S51A-R2`** | `M30b_AP_BQL_LIMIT_MAX_42392_MIN_3028_HOLD_1000_WITH_TX_BIAS_2` | `36.275 -> 36.550 Mbps` | `+0.758%` | `75.958 -> 75.444 ms` | `-0.677%` | `2.173 -> 2.353 ms` (`+8.28%`) | `3.341 -> 2.385 ms` (`-28.61%`) | `+0.9949%` | **`RETAIN_CURRENT_CHAMPION` (`REFUTED` — `LBM5` ping gate)** |
| **`S51A-R3`** | `M31a_ATH10K_AC_VI_AQL_2000_3500_WITH_TX_BIAS_2` | `35.349 -> 36.431 Mbps` | `+3.061%` | `73.112 -> 69.638 ms` | `-4.752%` | `1.241 -> 1.621 ms` (`+30.62%`) | `2.583 -> 2.660 ms` (`+2.98%`) | `+4.7240%` | **`RETAIN_CURRENT_CHAMPION` (`REFUTED` — `LBM5` ping gate)** |
| **`S51A-R4`** | `M30_M31b_DEV_WEIGHT_80_TX_BIAS_2_AND_BQL_42392_AC_VI_AQL` | `40.790 -> 39.870 Mbps` | `-2.255%` | `71.394 -> 82.042 ms` | `+14.914%` | `1.392 -> 1.976 ms` (`+41.95%`) | `2.838 -> 2.753 ms` (`-2.99%`) | `-7.4754%` | **`RETAIN_CURRENT_CHAMPION` (`REFUTED`)** |
| **`S51A-R5`** | `M31a_PURE_ATH10K_AC_VI_AQL_2000_3500_WITH_TX_BIAS_2_3CPE_VERIFIED` | `61.764 -> 48.687 Mbps` | `-21.173%` | `97.246 -> 81.035 ms` | `-16.670%` | `1.288 -> 1.224 ms` (`-4.97%`) | `1.940 -> 2.058 ms` (`+6.08%`) | `-15.3380%` | **`RETAIN_CURRENT_CHAMPION` (`REFUTED`)** |
| **`S51A-R6`** | **`M30c_PURE_BQL_LIMIT_MAX_42392_HOLD_1000_3CPE_VERIFIED`** | **`39.723 -> 42.349 Mbps`** | **`+6.611%`** | **`98.760 -> 92.734 ms`** | **`-6.102%`** | **`1.945 -> 1.537 ms` (`-20.98%`)** | **`2.638 -> 1.723 ms` (`-34.69%`)** | **`+8.7464%`** | **`PROMOTE_NEW_CHAMPION` (`Stage 51A Champion v17`, `CONFIRMED`)** |

---

## 2. Physical & Causal Analysis of Each Round

### 2.1 `S51A-R1` (`M30a`: `ag71xx` `eth0` BQL `limit_max=36336` [`24×MTU`], `limit_min=3028`, `hold_time=750` ms + `dev_weight_tx_bias=2`)
- **Result**: Aggregate goodput improved **`+9.455%` (`37.376 -> 40.910 Mbps`)**, and `p50` RTT improved `-11.14%` (`42.308 -> 37.594 ms`) and `p99` RTT improved `-1.79%` (`116.706 -> 114.620 ms`), but reducing `hold_time` from `1000` ms to `750` ms caused Linux `dql` to adjust `eth0` `limit` too frequently during 3-CPE TCP window oscillations, inflating `p95` RTT by `+5.017%` (`106.593 -> 111.941 ms`) -> **`RETAIN_CURRENT_CHAMPION` (`REFUTED`)**.

### 2.2 `S51A-R2` .. `S51A-R5`: `M31a` (`AC_VI` AQL `2000/3500` us) & `M31b` (`dev_weight=80, dev_weight_tx_bias=2`)
- **Harness Discovery (`ensure_3cpes_healthy_600s` 1-Packet Ping Transition)**:
  - Right after `S51A-R1` `B2` saturation ended, `ensure_3cpes_healthy_600s` ran a single `ping -c 1 -W 1 198.18.0.52` while `LiteBeam M5`'s TX queue was still draining, causing `ensure_3cpes_healthy_600s` to switch `LAP-120` to open mode while `LiteBeam M5` was still running `wpa_supplicant` in WPA2-PSK mode. All failed results (`S51A-R2 .. S51A-R5`) were preserved verbatim in [`artifacts/autoresearch/stage51a_m30_m31_bql_limit_max_and_aql_bench_20261025.json`](../artifacts/autoresearch/stage51a_m30_m31_bql_limit_max_and_aql_bench_20261025.json).
- **Why `M31a` (`AC_VI` AQL `2000/3500` us) & `M31b` (`dev_weight=80`) Are Refuted (`S51A-R4` & `S51A-R5`)**:
  - In `S51A-R4`, raising `net.core.dev_weight` from `64` to `80` with `dev_weight_tx_bias=2` (`160` effective TX quota) prolonged per-device NAPI softirq slices on single-core `MIPS 74Kc` (`AR9342` `560 MHz`), degrading goodput by `-2.255%` (`40.790 -> 39.870 Mbps`) and inflating `p95` RTT by `+14.914%` (`71.394 -> 82.042 ms`).
  - In `S51A-R5`, expanding `AC_VI` (`AC 1`) AQL from `1200/2400` us to `2000/3500` us (`> AC_BE 1500/3000` us) cut `p95` RTT by `-16.670%` (`97.246 -> 81.035 ms`) and Dual IPTV jitter by `-4.969%` (`1.288 -> 1.224 ms`), but allowed `AC_VI` TXOP bursts to preempt `AC_BE` bulk TCP A-MPDU formation (`61.764 -> 48.687 Mbps`, `-21.173%`) -> **`RETAIN_CURRENT_CHAMPION` (`REFUTED`)**.

### 2.3 `S51A-R6` (`M30c_PURE_BQL_LIMIT_MAX_42392_HOLD_1000_3CPE_VERIFIED` -> `Stage 51A Champion v17`, `CONFIRMED`)
- **Hypothesis & Mechanism**:
  - In `Stage 46A` (`S46A-R1`), clamping `ag71xx` `eth0` `byte_queue_limits/limit_max = 24576` (`16×MTU`) and `hold_time = 500` ms proved too tight (`-0.98%` goodput), whereas in `S46A-R5`, setting `limit_max = 65536` (`43×MTU`) and `limit_min = 4542` (`3×MTU`) without `dev_weight_tx_bias=2` proved too loose (`-10.27%` goodput).
  - Under **`Stage 46A Champion v16` (`net.core.dev_weight_tx_bias = 2` at full `netdev_budget = 600`)**, setting `ag71xx` `eth0` `byte_queue_limits`:
    - `limit_max = 42392` (`28 × 1514` B = `28×MTU`, capping the upper tail of Linux `dql`'s `54,250` B drift on `LAP-120` `.20` without clipping 24-to-28-frame TCP bursts),
    - `limit_min = 3028` (`2 × 1514` B = `2×MTU`, curing `Loco 5AC` `.250` `eth0`'s `1,780` B BQL starvation floor),
    - `hold_time = 1000` ms (preserving smooth `1.0` s `dql` windowing),
    achieves a **strict 4-dimensional Pareto improvement** with all 3 CPEs (`Loco5AC_WA`, `Rocket5AC_XC`, `LiteBeamM5_XW`) verified at **`0.0%` ICMP loss** across all 4 windows (`A1`, `B1`, `A2`, `B2`):
    - **Aggregate 3-CPE Goodput**: **`39.723 -> 42.349 Mbps` (`+6.611%`, `B1=42.814 Mbps`, `B2=41.885 Mbps` vs `A1=37.674 Mbps`, `A2=41.772 Mbps`)**
    - **Loaded 3-CPE `p95` RTT**: **`98.760 -> 92.734 ms` (`-6.102%`, `B1=95.742 ms`, `B2=89.726 ms` vs `A1=90.022 ms`, `A2=107.498 ms`)**
    - **Loaded 3-CPE `p50` RTT**: **`52.895 -> 33.849 ms` (`-36.007%`)**
    - **Loaded 3-CPE `p99` RTT**: **`102.803 -> 98.234 ms` (`-4.444%`)**
    - **Dual `1080p60` IPTV (`tid4_ac1` `WMM AC_VI`)**: **`1.945 -> 1.537 ms` jitter (`-20.977%`)**, `4.960 Mbps` delivered, loss reduced from `0.1229%` (`7/5,687`) to `0.0702%` (`4/5,698`, `0` lost in `B1`)
    - **Real-Time VoIP (`tid6_ac0` `WMM AC_VO`)**: **`2.638 -> 1.723 ms` jitter (`-34.685%`)**, **`0.00%` loss (`0/1,196` lost frames across `B1+B2`)**
    - **Pareto Score Delta**: **`+8.7464%` (`PROMOTE_NEW_CHAMPION` -> `Stage 51A Champion v17`)**.

---

## 3. Hardware Getter Readback Verification (`S51A-R6` `Arm A` vs `Arm B`)

| Parameter / Kernel Interface | `LAP-120` (`.20`) `Arm A` (`v16`) | `LAP-120` (`.20`) `Arm B` (`v17`) | `Loco 5AC` (`.250`) `Arm A` (`v16`) | `Loco 5AC` (`.250`) `Arm B` (`v17`) |
| :--- | :---: | :---: | :---: | :---: |
| `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max` | `1879048192` | **`42392` (`28×MTU`)** | `1879048192` | **`42392` (`28×MTU`)** |
| `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_min` | `0` | **`3028` (`2×MTU`)** | `0` | **`3028` (`2×MTU`)** |
| `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/hold_time` | `1000` ms | **`1000` ms** | `1000` ms | **`1000` ms** |
| `net.core.dev_weight` / `net.core.dev_weight_tx_bias` | `64` / `2` | **`64` / `2`** | `64` / `2` | **`64` / `2`** |
| `net.core.netdev_budget` / `net.core.netdev_budget_usecs` | `600` / `20000` | **`600` / `20000`** | `600` / `20000` | **`600` / `20000`** |
| `/sys/class/net/eth0/tx_queue_len` | `1000` | **`1000`** | `1000` | **`1000`** |
| `/sys/class/net/br-lan/tx_queue_len` & `phy0-*/tx_queue_len` | `256` | **`256`** | `256` | **`256`** |
| `/sys/kernel/debug/ieee80211/phy0/aqm` (`fq_quantum` / `fq_limit`) | `4542` / `2048` | **`4542` / `2048`** | `1514` / `1024` | **`1514` / `1024`** |
| `/sys/kernel/debug/ieee80211/phy0/aql_txq_limit` (`VO` / `VI` / `BE`) | `300/600`, `1200/2400`, `1500/3000` | **`300/600`, `1200/2400`, `1500/3000`** | `300/600`, `1200/2400`, `900/1500` | **`300/600`, `1200/2400`, `900/1500`** |

---

## 4. Artifacts & Reproducibility

- **Benchmark Runner**: [`tools/bench/run_stage51a_m30_m31_bql_sweetspot_and_aql_bench.py`](../tools/bench/run_stage51a_m30_m31_bql_sweetspot_and_aql_bench.py)
- **JSON Receipts**:
  - [`artifacts/autoresearch/stage51a_m30_m31_bql_limit_max_and_aql_bench_20261025.json`](../artifacts/autoresearch/stage51a_m30_m31_bql_limit_max_and_aql_bench_20261025.json)
  - [`artifacts/autoresearch/stage51a_m30_m31_bql_sweetspot_and_aql_bench_20261025.json`](../artifacts/autoresearch/stage51a_m30_m31_bql_sweetspot_and_aql_bench_20261025.json)
- **Controller Profile Overlay**: `STAGE51A_CHAMPION_V17_OVERLAY` & `get_stage51a_champion_v17_profile()` in [`controller/multiradio_golden_profile_applicator.py`](../controller/multiradio_golden_profile_applicator.py)
- **Test Suite**: [`tests/test_stage51a_m30_m31_bql_and_aql_bench.py`](../tests/test_stage51a_m30_m31_bql_and_aql_bench.py) & [`tests/test_stage51a_m30_m31_bench.py`](../tests/test_stage51a_m30_m31_bench.py)
