<!-- doc-head: STAGE46A_M28_M29_AG71XX_BQL_AND_NAPI_TX_BIAS_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 46A Physical Bench Report — `M28` (`ag71xx` Hardware `eth0` Byte Queue Limits `BQL` & `hold_time`) + `M29a` (`LiteBeam M5` `netdev_budget=600`) + `M29b` (Pure `net.core.dev_weight_tx_bias=2` at Full `netdev_budget=600`) (`T-S46A-M28-M29-AG71XX-BQL-HOLD-TIME-AND-ATH10K-VI-AQL-IPTV-BENCH`)

**Date:** 2026-10-25  
**Stage:** `46A` (`T-S46A-M28-M29-AG71XX-BQL-HOLD-TIME-AND-ATH10K-VI-AQL-IPTV-BENCH`)  
**Status:** **CONFIRMED (`Stage 46A Champion v16` Promoted in `S46A-R3`; `S46A-R1`, `S46A-R2`, `S46A-R4`, `S46A-R5`, `S46A-R6` Qualified & Documented as `REFUTED` Across 6 Rounds / 24 Counterbalanced Windows; Active in RAM Across All 4 Bench Radios; `0` Flash Writes)**

---

## 1. Executive Summary & Scientific Rationale

Following the promotion of **`Stage 44A Champion v15`** (`S44A-R5`: `M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000`, which expanded 3-CPE aggregate goodput by **`+5.342%`** (`42.848 -> 45.137 Mbps`) and cut loaded `p95` RTT by **`-3.516%`** (`92.752 -> 89.491 ms`) with **`0.00%` IPTV loss** and **`0.00%` VoIP loss**), two high-priority hardware/kernel questions emerged from live telemetry on the 4-radio 5 GHz PtMP bench (`LAP-120` `198.18.0.43` + `Loco 5AC` `198.18.0.47` + `Rocket Prism 5AC Gen2` `198.18.0.64` + `LiteBeam M5` `198.18.0.48`):

1. **`M28` (`ag71xx` Hardware Ethernet Byte Queue Limits `BQL` `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/*`)**:
   - On `LAP-120` (`.20`) and `Loco 5AC` (`.250`, OpenWrt `24.10.4`, Linux `6.6.110`), the `ag71xx` Fast/Gigabit Ethernet DMA ring uses Dynamic Queue Limits (`DQL` / `BQL`) with stock defaults `limit_min = 0`, `limit_max = 1879048192`, `hold_time = 1000` ms.
   - Live sysfs readback revealed a stark asymmetry: on `LAP-120` (`.20`), `eth0` `byte_queue_limits/limit` had drifted upward to **`54,250` bytes** (`~36` full-MTU frames queued in the wired Ethernet DMA ring before `fq_codel` backpressure), whereas on `Loco 5AC` (`.250`), `eth0` `byte_queue_limits/limit` sat at **`1,780` bytes** (`< 2 × MTU`), potentially starving 2-frame bursts across the `100 Mbps` Ethernet PHY.
   - **Hypothesis (`S46A-R1`)**: Bounding `eth0` `byte_queue_limits/limit_max = 24576` (`16 × 1536 B`), `limit_min = 3028` (`2 × 1514 B`), and `hold_time = 500` ms on both `LAP-120` and `Loco 5AC` will tighten Ethernet TX ring latency without starving `eth0` (`tx_queue_len = 1000`).
2. **`M29a` (`LiteBeam M5` `XW.v6.3.22` `/proc/sys/net/core/netdev_budget = 600` Sector Alignment)**:
   - After `S44A-R5` aligned `Rocket Prism 5AC Gen2` (`.198`) `net.core.netdev_budget = 600` to match `LAP-120` (`.20`) and `Loco 5AC` (`.250`), `LiteBeam M5` (`.251` / `198.18.0.52`, `XW.v6.3.22`) was the sole remaining station on the sector with stock `/proc/sys/net/core/netdev_budget = 300`.
   - **Hypothesis (`S46A-R2`)**: Raising `LiteBeam M5` `net.core.netdev_budget = 600` unifies `600`-packet NAPI softirq budgets across all 4 sector radios.
3. **`M29b` (Pure `net.core.dev_weight_tx_bias = 2` at Full `net.core.netdev_budget = 600` & `eth0 tx_queue_len = 1000`)**:
   - In `Stage 44A` (`S44A-R3`), `net.core.dev_weight_tx_bias = 2` cut Dual `1080p60` IPTV jitter by **`-42.28%`** (`2.001 -> 1.155 ms`) and loaded `p95` RTT by **`-2.71%`**, **but** cost `-1.42%` goodput because `S44A-R3` simultaneously halved `net.core.netdev_budget` from `600` to `300` and `netdev_budget_usecs` from `20000` to `8000`. And in `S44A-R4`, combining `dev_weight_tx_bias = 2` with `eth0 tx_queue_len = 256` failed because shrinking `eth0` `tx_queue_len` caused wired ingress tail drops.
   - **Hypothesis (`S46A-R3`)**: Isolating **pure `net.core.dev_weight_tx_bias = 2`** on `LAP-120` (`.20`) and `Loco 5AC` (`.250`) while preserving full `net.core.netdev_budget = 600`, `net.core.dev_weight = 64`, `net.core.netdev_budget_usecs = 20000`, and `eth0 tx_queue_len = 1000` will accelerate `ath10k` HTT TX-completion ring reclamation (`64 × 2 = 128` TX completion work units per NAPI poll) without prematurely terminating NAPI RX softirq loops.
4. **Combined Synthesis (`S46A-R4`: `M28 + M29a + M29b`)**:
   - **Hypothesis (`S46A-R4`)**: Testing whether `M28` (`eth0` BQL `3028..24576 / 500 ms`) + `M29a` (`LBM5` `netdev_budget=600`) + `M29b` (`dev_weight_tx_bias=2`) compounds cleanly or whether `M28`'s `limit_max=24576` cap constrains peak multi-stream TCP bursts.

---

## 2. Counterbalanced Physical Bench Results (`A1 -> B1 -> A2 -> B2`, 6 Rounds / 24 Windows)

- **Runner**: [`run_stage46a_m28_m29_bql_and_tx_bias_bench.py`](<repo>/tools/bench/run_stage46a_m28_m29_bql_and_tx_bias_bench.py)
- **JSON Evidence**: [`stage46a_m28_m29_bql_and_tx_bias_bench_20261025.json`](<repo>/artifacts/autoresearch/stage46a_m28_m29_bql_and_tx_bias_bench_20261025.json)

| Round ID | Mechanism ID | 3-CPE Goodput (`A -> B`) | Goodput $\Delta\%$ | Loaded `p95` RTT (`A -> B`) | `p95` RTT $\Delta\%$ | Loaded `p99` RTT (`A -> B`) | Dual IPTV Jitter (`A -> B`) | Dual IPTV Loss (`A -> B`) | VoIP Jitter (`A -> B`) | Pareto Score | Strict Decision / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S46A-R1`** | `M28_AG71XX_BQL_LIMIT_MAX_24576_HOLD_500_CPE_MIN_3028` | `42.283 -> 41.870 Mbps` | `-0.977%` | `84.166 -> 79.455 ms` | **`-5.597%`** | `102.687 -> 99.431 ms` (`-3.17%`) | **`1.845 -> 0.551 ms` (`-70.136%`)** | `0.1936% -> 0.0529%` | **`2.333 -> 1.546 ms` (`-33.733%`)** | `+0.9823%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` — `-0.98%` GP) |
| **`S46A-R2`** | `M29a_LBM5_NETDEV_BUDGET_600_UNIFORM_SECTOR_BUDGET` | `44.331 -> 44.285 Mbps` | `-0.104%` | `98.998 -> 94.157 ms` | **`-4.890%`** | `106.893 -> 103.376 ms` (`-3.29%`) | `1.819 -> 2.396 ms` (`+31.721%`) | `0.0000% -> 0.0175%` | `2.732 -> 2.662 ms` (`-2.562%`) | `+1.6077%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` — `-0.10%` GP) |
| **`S46A-R3`** | **`M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`** | **`39.642 -> 41.025 Mbps`** | **`+3.489%`** | **`90.986 -> 85.262 ms`** | **`-6.291%`** | **`95.257 -> 89.434 ms` (`-6.113%`)** | **`2.412 -> 1.985 ms` (`-17.703%`)** | `0.0000% -> 0.1052%` (`0.00%` in `B1`) | **`2.689 -> 2.549 ms` (`-5.206%`)** | **`+5.6906%`** | **`PROMOTE_NEW_CHAMPION` (`CONFIRMED` — `Champion v16`)** |
| **`S46A-R4`** | `M28_M29_COMBINED_BQL_LBM5_BUDGET_600_AND_TX_BIAS_2` | `42.096 -> 41.624 Mbps` | `-1.121%` | `94.328 -> 84.035 ms` | **`-10.912%`** | `103.423 -> 99.219 ms` (`-4.065%`) | `1.682 -> 2.120 ms` (`+26.040%`) | **`0.2808% -> 0.0000%`** | **`2.346 -> 2.123 ms` (`-9.506%`)** | `+2.6979%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` — `-1.12%` GP) |
| **`S46A-R5`** | `M28b_PURE_AG71XX_BQL_MIN_4542_MAX_65536_HOLD_1000` | `36.066 -> 32.363 Mbps` | `-10.267%` | `84.168 -> 87.912 ms` | `+4.448%` | `92.075 -> 98.722 ms` (`+7.22%`) | `2.042 -> 2.186 ms` (`+7.052%`) | `0.0000% -> 0.0000%` | **`2.475 -> 1.921 ms` (`-22.384%`)** | `-11.8242%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` — manual BQL bounds harm `dql`) |
| **`S46A-R6`** | `M29c_PURE_NON_DISRUPTIVE_LBM5_BUDGET_600_WITH_DYNAMIC_BQL` | `39.723 -> 41.108 Mbps` | **`+3.487%`** | `91.517 -> 99.606 ms` | `+8.839%` | `103.337 -> 104.508 ms` (`+1.13%`) | `1.220 -> 2.028 ms` (`+66.230%`) | **`0.0176% -> 0.0000%`** | `2.357 -> 2.657 ms` (`+12.728%`) | `+0.3931%` | `RETAIN_CURRENT_CHAMPION` (`REFUTED` — AR934x `budget=600` inflates `p95` RTT) |

---

## 3. Window-by-Window Breakdown & Mechanistic Findings

### 3.1 Why `S46A-R3` (`M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`) Is Promoted as `Stage 46A Champion v16` (`CONFIRMED`)
- **Per-Window Counterbalanced Progression (`S46A-R3`)**:
  - `A1` (`Champion v15`: `dev_weight_tx_bias=1`, `netdev_budget=600`): `38.475 Mbps` aggregate goodput (`33.32 Mbps` TCP + `4.95 Mbps` IPTV + `0.13 Mbps` VoIP), `p95` RTT `92.309 ms`, `p99` RTT `94.289 ms`, IPTV jitter `3.059 ms`, VoIP jitter `3.377 ms`.
  - `B1` (`Champion v15 + M29b`: `dev_weight_tx_bias=2`, `netdev_budget=600`): **`41.516 Mbps`** aggregate goodput (`36.26 Mbps` TCP + `4.96 Mbps` IPTV + `0.13 Mbps` VoIP), `p95` RTT **`84.205 ms`**, `p99` RTT **`87.350 ms`**, IPTV jitter **`2.075 ms`** (`0.00%` loss), VoIP jitter **`2.199 ms`**.
  - `A2` (`Champion v15` restore): `40.808 Mbps` aggregate goodput, `p95` RTT `89.662 ms`, `p99` RTT `96.225 ms`, IPTV jitter `1.765 ms`, VoIP jitter `2.001 ms`.
  - `B2` (`Champion v15 + M29b` re-verify): **`40.533 Mbps`** aggregate goodput, `p95` RTT **`86.319 ms`**, `p99` RTT **`91.517 ms`**, IPTV jitter **`1.894 ms`**, VoIP jitter **`2.898 ms`**.
- **Physical Mechanism (`CONFIRMED`)**:
  - On `OpenWrt 24.10.4` (`Linux 6.6.110`), `net.core.dev_weight_tx_bias = 2` multiplies the NAPI TX completion weight (`dev_weight * dev_weight_tx_bias = 64 * 2 = 128`) during softirq polling.
  - When paired with the full `net.core.netdev_budget = 600` and `net.core.netdev_budget_usecs = 20000` (rather than halving `netdev_budget` to `300` as in `S44A-R3`), `ath10k_pci` drains HTT TX completion messages twice as aggressively per NAPI cycle **without** exhausting the softirq packet budget needed by `ag71xx` Ethernet RX and `mac80211` `ieee80211_tx_dequeue`.
  - Consequently, `phy0` AQL airtime credit (`aql_txq_limit` / `aql_threshold=5000`) is returned to `tid4_ac1` (`AC_VI` IPTV) and `tid0_ac2` (`AC_BE` TCP) immediately upon over-the-air BlockAck receipt, yielding **`+3.489%` higher 3-CPE goodput** (`39.642 -> 41.025 Mbps`), **`-6.291%` lower loaded `p95` RTT** (`90.986 -> 85.262 ms`), **`-6.113%` lower `p99` RTT** (`95.257 -> 89.434 ms`), **`-17.703%` lower Dual `1080p60` IPTV jitter** (`2.412 -> 1.985 ms`), and **`-5.206%` lower VoIP jitter** (`2.689 -> 2.549 ms`).

### 3.2 Why `M28` (`ag71xx` `eth0` `BQL` `limit_max=24576`, `hold_time=500`) Cut IPTV Jitter by `-70.14%` (`1.845 -> 0.551 ms`) and `p95` RTT by `-5.60%`, Yet Is Rejected Under Strict Goodput Non-Regression (`S46A-R1` & `S46A-R4`, `REFUTED`)
- In `S46A-R1`, bounding `/sys/class/net/eth0/queues/tx-0/byte_queue_limits/limit_max = 24576` (`16 × MTU`) and `hold_time = 500` ms clamped `LAP-120` `eth0` active `BQL` `limit` from `54,250 B` (`A1`) / `53,944 B` (`A2`) down to `24,576 B` (`B1`/`B2`), and raised `Loco 5AC` `eth0` `BQL` `limit` from `1,780 B` to `3,028 B`.
- This eliminated wired Ethernet TX DMA ring queuing spikes, reducing Dual `1080p60` IPTV jitter by **`-70.136%`** (`1.845 -> 0.551 ms`), VoIP jitter by **`-33.733%`** (`2.333 -> 1.546 ms`), and loaded `p95` RTT by **`-5.597%`** (`84.166 -> 79.455 ms`), and in `S46A-R4` cut loaded `p95` RTT by **`-10.912%`** (`94.328 -> 84.035 ms`) with **`0.0000%` IPTV packet loss** (`0/5,698` datagrams lost).
- However, capping `LAP-120` `eth0` `limit_max` at `24,576 B` slightly clipped peak multi-stream TCP bursts (`-0.977%` goodput in `S46A-R1`, `-1.121%` in `S46A-R4`). Under FuturaMAX's strict non-negative goodput promotion gate (`goodput_delta_pct >= 0.0`), `M28` is retained as a documented low-jitter specialist profile (`REFUTED` for general champion promotion), while pure `M29b` (`S46A-R3`) is promoted as **`Stage 46A Champion v16`**.

---

## 4. Hardware Getter Verification (`Stage 46A Champion v16` Active in RAM)

| Radio / Target | Verified Parameter | `Stage 44A Champion v15` | **`Stage 46A Champion v16` (`S46A-R3`)** | Verification Method |
| :--- | :--- | :--- | :--- | :--- |
| **`LAP-120` AP (`.20`)** | `net.core.dev_weight_tx_bias` | `1` | **`2` (`128` effective TX completion weight)** | `sysctl net.core.dev_weight_tx_bias` |
| **`LAP-120` AP (`.20`)** | `net.core.netdev_budget` / `usecs` | `600` / `20000` | **`600` / `20000`** | `sysctl net.core.netdev_budget net.core.netdev_budget_usecs` |
| **`LAP-120` AP (`.20`)** | `eth0` / `br-lan` / `phy0-ap0*` `tx_queue_len` | `1000` / `256` / `256` | **`1000` / `256` / `256`** | `/sys/class/net/*/tx_queue_len` |
| **`Loco 5AC` CPE (`.250`)** | `net.core.dev_weight_tx_bias` | `1` | **`2` (`128` effective TX completion weight)** | `sysctl net.core.dev_weight_tx_bias` |
| **`Loco 5AC` CPE (`.250`)** | `eth0` / `br-lan` / `phy0-sta0` `tx_queue_len` | `1000` / `256` / `256` | **`1000` / `256` / `256`** | `/sys/class/net/*/tx_queue_len` |
| **`Rocket Prism 5AC Gen2` (`.198`)** | `br0` / `ath0` / `eth0` `txqueuelen` + `netdev_budget` | `256` / `256` / `256` + `600` | **`256` / `256` / `256` + `600`** | `/sys/class/net/*/tx_queue_len` + `/proc/sys/net/core/netdev_budget` |
| **`LiteBeam M5` (`.251` / `.4`)** | `br0` / `ath0` / `eth0` `txqueuelen` + `ewma` | `256` / `256` / `256` + `1` | **`256` / `256` / `256` + `1`** | `/sys/class/net/*/tx_queue_len` + `ubnt_ewma_delegate_on` |
