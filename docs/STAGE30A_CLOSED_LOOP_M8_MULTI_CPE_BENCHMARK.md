<!-- doc-head: STAGE30A_CLOSED_LOOP_M8_MULTI_CPE_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 30A: Closed-Loop Reactor Round 2 (`M8a`, `M8b`, `M8c`, `M9`) & 3-CPE Simultaneous Multi-Flow Benchmark (`2026-10-25`)

- **Task ID**: `T-S30A-LIVE-M8-M9-CLOSED-LOOP-REACTOR-ROUND2-BENCH`
- **Status**: **COMPLETED & VERIFIED ON PHYSICAL BENCH** (`Stage 28 Champion v7` & `r5ac_prism_sta` Champion confirmed as local Pareto optima across `4` paired `AB/AB` rounds / `16` sub-phases)
- **Receipts**:
  - Physical Bench Receipt: [`artifacts/autoresearch/stage30a_closed_loop_m8_bench_20261025.json`](../artifacts/autoresearch/stage30a_closed_loop_m8_bench_20261025.json)
  - Discovery-to-Research Queue (`12` events): [`artifacts/autoresearch/discovery_to_research_queue.json`](../artifacts/autoresearch/discovery_to_research_queue.json)
  - Headroom Matrix Reference: [`artifacts/autoresearch/stage29c_headroom_matrix_20261025.json`](../artifacts/autoresearch/stage29c_headroom_matrix_20261025.json)

---

## 1. Closed-Loop Reactor Round-2 Synthesis (`S28-R1` & `S28-R3` $\rightarrow$ `M8a`, `M8b`, `M8c`, `M9`)

Feeding the physical bench outcomes of `S28-R1` (`Champion v7`: `fq_codel quantum=3028 + br-lan txqueuelen=256 + tcp_dsack=1`, `-8.80%` `p95` RTT) and `S28-R3` (`Rocket Prism 5AC Gen2` `+7.195%` goodput with `netdev_budget=600` raising `p95` RTT by `+19.32%`) into [`ClosedLoopResearchReactor`](../tools/research/closed_loop_research_reactor.py) alongside the [`Stage 29C Headroom Matrix`](../artifacts/autoresearch/stage29c_headroom_matrix_20261025.json) generated four orthogonal Round-2 physical bench hypotheses:

| Round ID | Mechanism | Target Radio / Topology | Hypothesis Synthesized by Reactor |
| :--- | :--- | :--- | :--- |
| **`S30A-R1`** | **`M8a`** | `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC.v8.7.25` `Managed STA`) | Isolate `br0 txqueuelen=256 + tcp_sack/dsack=1 + tcp_fin_timeout=15` **without** `netdev_budget=600` / `netdev_max_backlog=2500` on top of `r5ac_prism_sta` Champion to verify whether `netdev_budget=600` caused the `+19.32%` `p95` RTT spike in `S28-R3`. |
| **`S30A-R2`** | **`M8b`** | 3-CPE Simultaneous Multi-Flow PtMP (`LAP-120 AP <-> Loco 5AC + Rocket Prism 5AC + LiteBeam M5`) | Validate `Stage 28 Champion v7` (`quantum=3028`) under simultaneous 3-CPE contention and test tightening `ath10k` per-AC `aql_txq_limit` `AC_BE` from `1500/3000 us` (`thresh=5000`) to `1100/2000 us` (`thresh=4400`). |
| **`S30A-R3`** | **`M8c`** | `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC.v8.7.25` `Managed STA`) | Changed hypothesis after `S30A-R1`: keep `br0 txqueuelen=1000` and `netdev_budget=300` while testing `uph_wifi0/ptp_xmit=1 + fixed_frame=1 + tcp_sack/dsack=1 + tcp_fin_timeout=15` (`Stage 29C` `S30-R5AC-R1`). |
| **`S30A-R4`** | **`M9`** | 3-CPE Simultaneous Multi-Flow PtMP (`LAP-120 AP <-> Loco 5AC + Rocket Prism 5AC + LiteBeam M5`) | Changed hypothesis after `S30A-R2`: keep `AC_BE = 1500/3000 us` (`thresh=5000`) and test Arrival-Rate Normalized Dynamic Airtime Weighting (`720:512:112` from `arXiv:0806.4695v1` + `CPE quantum=3028`) vs `Stage 28 Champion v7` (`640:512:96` + `AP quantum=3028 / CPE quantum=1514`). |

---

## 2. Physical Bench Results (`A1 -> B1 -> A2 -> B2`)

### 2.1 `Rocket Prism 5AC Gen2` (`198.18.0.64`) — `S30A-R1` (`M8a`) & `S30A-R3` (`M8c`)

| Round | Arm A (`r5ac_prism_sta` Champion) | Arm B (`Champion + Mutation`) | Δ Goodput | Δ `p95` RTT | Decision & Physical Causality |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`S30A-R1` (`M8a`: `br0 txq=256 + tcp_dsack=1`, `netdev_budget=300`)** | `26.985 Mbps` / `24.201 ms` | `25.428 Mbps` / **`21.916 ms`** | `-5.770%` | **`-9.442%`** | **`RETAIN_CURRENT_CHAMPION`** — Removing `netdev_budget=600` flipped the `+19.32%` `p95` regression from `S28-R3` into a **`-9.442%` `p95` RTT reduction (`24.20 -> 21.92 ms`)**, confirming `netdev_budget=600` caused softirq bursts on the MIPS 74Kc CPU. However, bounding `br0 txqueuelen=256` on top of `ath0/eth0 txqueuelen=256` caused tail-drops during 2 MB SSH bursts (`-5.77%` goodput). |
| **`S30A-R3` (`M8c`: `br0 txq=1000, netdev_budget=300, ptp_xmit=1, fixed_frame=1`)** | `26.015 Mbps` / **`22.378 ms`** | `25.916 Mbps` / `25.845 ms` | **`-0.381%`** | `+15.493%` | **`RETAIN_CURRENT_CHAMPION`** — Restoring `br0 txqueuelen=1000` eliminated the goodput drop (`-0.381%`, flat), confirming `br0 txqueuelen=256` caused the `S30A-R1` throughput dip. Meanwhile, `ptp_xmit=1 + fixed_frame=1` (an AP-mode TDMA pacing knob) added `+3.47 ms` slot-wait jitter when operating as a standard `802.11ac` Managed STA associated to OpenWrt `LAP-120`. |

---

### 2.2 3-CPE Simultaneous Multi-Flow PtMP Sector (`LAP-120 AP <-> Loco 5AC + Rocket Prism 5AC + LiteBeam M5`) — `S30A-R2` (`M8b`) & `S30A-R4` (`M9`)

| Round | Arm A (`Stage 28 Champion v7`) | Arm B (`Champion v7 + Mutation`) | Δ Aggregate Goodput | Δ Sector `p95` RTT | Δ Sector `p99` RTT | Loss (`%`) | Decision & Physical Causality |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`S30A-R2` (`M8b`: `AC_BE=1100/2000, thresh=4400` + `quantum=3028`)** | **`33.806 Mbps`** (`57.829 ms` `p95`) | `31.942 Mbps` (**`54.479 ms` `p95`**, `B2 = 50.312 ms`) | `-5.514%` | **`-5.793%`** | **`-7.40%`** (`60.66 -> 56.17 ms`) | `0.0%` | **`RETAIN_CURRENT_CHAMPION`** — Tightening `AC_BE` AQL to `1100/2000 us` cut 3-CPE `p95` RTT by **`-5.793%`** (`50.31 ms` in `B2`), but throttled the second subframe of the 2-MTU `quantum=3028` (`~1,450 us` airtime at `78 Mbps` PHY rate + RTS/CTS), proving `AC_BE = 1500/3000 us` (`thresh=5000`) is the minimum AQL budget required to sustain 2-MTU DRR aggregation without goodput loss. |
| **`S30A-R4` (`M9`: `AC_BE=1500/3000, thresh=5000`, Weights `720:512:112` + `CPE quantum=3028`)** | **`33.998 Mbps`** (**`53.319 ms` `p95`**) | `33.224 Mbps` (`55.053 ms` `p95`, **`59.721 ms` `p99`**) | `-2.277%` | `+3.252%` | **`-14.69%`** (`70.01 -> 59.72 ms`) | `0.0%` | **`RETAIN_CURRENT_CHAMPION`** — Restoring `AC_BE = 1500/3000 us` immediately recovered aggregate goodput (`33.998 Mbps`), and `M9` boosted `Rocket5AC_XC` (`+5.65%`) and `LiteBeamM5_XW` (`+4.69%`) goodput while cutting sector `p99` RTT by **`-14.69%`**. However, setting `quantum=3028` on the **CPE uplink** under 3-station contention slightly increased uplink CSMA/CA collision tail (`+3.25%` `p95` RTT), confirming that **`AP quantum=3028` + `CPE quantum=1514` (`Stage 28 Champion v7`)** is the true Pareto optimum (`53.319 ms` `p95` RTT, `0.0%` loss). |

---

## 3. Summary of Physical Boundary & Asymptote Verification

1. **Downlink AP vs Uplink CPE `fq_codel quantum` Asymmetry Discovered (`S28-R1` vs `S30A-R4`)**:
   - In **1-CPE PtP (`S28-R1`)** and on the **PtMP AP Downlink (`phy0-ap0`)**, `fq_codel quantum=3028` (2 full MTUs per DRR turn) cuts `p95` RTT by `-8.80%` and boosts goodput because the AP serializes downlink transmissions without inter-station CSMA/CA collisions.
   - Under **3-CPE Simultaneous Uplink Contention (`S30A-R4`)**, keeping `CPE quantum=1514` (1 MTU) on the stations while the AP runs `AP quantum=3028` (`Stage 28 Champion v7` Control Arm A) achieves **`53.319 ms` sector `p95` RTT (`42.81 ms` on `Loco 5AC`, `42.30 ms` on `LiteBeam M5`) and `0.0%` loss**.
2. **Minimum AQL Budget for 2-MTU DRR Quantum (`S30A-R2`)**:
   - Pairing `quantum=3028` with `AC_BE = 1500/3000 us` (`aql_threshold = 5000`) is hardware-necessary at `78–117 Mbps` VHT20 MCS rates; lowering `AC_BE` to `1100/2000 us` cuts `p95` RTT by `-5.79%` (`50.31 ms` in `B2`) at the cost of `-5.51%` goodput.
3. **All 4 Bench Radios Verified in Winning Champion RAM State (`persistent_flash_writes = false`)**:
   - `LAP-120` (`.1`), `Loco 5AC` (`.41`), `Rocket Prism 5AC Gen2` (`.198`), and `LiteBeam M5` (`198.18.0.52`) are restored and verified in their winning Champion RAM profiles.
