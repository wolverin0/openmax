<!-- doc-head: STAGE24E_M2_ADAPTIVE_RTS_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 24E — Physical Mechanism `M2` (`PB-021` EVM-vs-Retry Hidden-Node Classifier & Adaptive RTS/CTS Gate) Benchmark

- **Task ID**: `T-S24E-M2-EVM-RETRY-ADAPTIVE-RTS-BENCH`
- **Completed UTC**: `2026-10-25T15:47:33Z`
- **Status**: `PASS_STAGE24E_M2_ADAPTIVE_RTS_COMPLETE`
- **Receipt**: [`artifacts/autoresearch/stage24e_m2_adaptive_rts_20261025.json`](../artifacts/autoresearch/stage24e_m2_adaptive_rts_20261025.json)
- **Runner**: [`tools/bench/run_stage24e_m2_adaptive_rts_bench.py`](../tools/bench/run_stage24e_m2_adaptive_rts_bench.py)

---

## 1. Incremental Champion-as-Baseline Methodology

Every round in Stage 24E starts strictly from our verified **Stage 24C Champion v4** profile (`A = Current Champion v4`, never reverting to Stock as baseline) and tests Mechanism `M2` (`PB-021` EVM-vs-Retry Hidden-Node Classifier & Zero-Overhead Adaptive RTS/CTS Gate from [`docs/STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md`](./STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md)) using `A1 -> B1 -> A2 -> B2` interleaving on the physical 4-radio 5 GHz PtMP bench (`5180 MHz / 20 MHz`, `LAP-120` AP `198.18.0.81` + `NanoStation 5AC Loco` `198.18.0.67` + `Rocket Prism 5AC Gen2` `198.18.0.64` + `LiteBeam M5` `198.18.0.52`). All operations are 100% RAM-only (`persistent_flash_writes: false`):

1. **Case 1 (`S24E-R1` — Single-CPE Clean-SNR Regime, `active_busy_cpes == 1` and `EVM <= -20 dB`)**:
   - Explicitly disabling RTS/CTS (`iw phy phy0 set rts off`) on both `LAP-120` and `Loco 5AC` vs threshold `2347` to avoid any residual RTS/CTS handshake overhead (`44..60 us` per TXOP) when only a single station is active on a clean link.
2. **Case 2 (`S24E-R2` — 3-CPE Multi-Station Contention Regime, `active_busy_cpes >= 2`)**:
   - Enabling Adaptive RTS/CTS at `512 B` (`iw phy phy0 set rts 512` on OpenWrt `LAP-120` & `Loco 5AC`, `iwpriv ath0 protmode 1; iwconfig ath0 rts 512` on `Rocket Prism 5AC`, and `/proc/athrtscts=1; iwpriv ath0 protmode 1` on `LiteBeam M5`) combined with Mechanism `M1` Dynamic Responsible-Airtime weight updates (`W_i = round(W_contract / (1 + 2.5 * PER_i))`) on top of Stage 24C 3-CPE All-Champion v4.

---

## 2. Physical Benchmark Results (`A1 -> B1 -> A2 -> B2`)

| Round | Control Arm `A` (Stage 24C Champion v4) | Treatment Arm `B` (Champion v4 + Mechanism `M2` Adaptive RTS/CTS) | Arm `A` Goodput | Arm `B` Goodput | Goodput $\Delta$ | Arm `A` `p95` RTT | Arm `B` `p95` RTT | `p95` RTT $\Delta$ | Decision |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`S24E-R1`** (1-CPE Clean-SNR Regime) | Stage 24C 1-CPE Champion v4 (`rts 2347`) | Stage 24C 1-CPE Champion v4 + **`iw phy phy0 set rts off`** | `60.43 Mbps` | **`73.64 Mbps`** | **`+21.87%`** | `19.54 ms` | `19.79 ms` | `+1.27%` | **`KEEP_NEW_CHAMPION`** |
| **`S24E-R2`** (3-CPE Multi-Station Contention) | Stage 24C 3-CPE All-Champion v4 (`640:512:96`, per-AC AQL `750..1500/1500..3000`, `thresh=5000`, AirBBR, `RTS=off`) | Stage 24C 3-CPE All-Champion v4 + **`M2` Adaptive RTS/CTS `512 B`** + **`M1` Dynamic Responsible-Airtime Weights** (`600..604:512:96`) | `56.79 Mbps` | **`59.76 Mbps`** | **`+5.24%`** | `110.40 ms` | **`64.06 ms`** | **`-41.98%`** | **`KEEP_NEW_CHAMPION`** |

---

## 3. Key Findings & Promotion to `Champion v5`

1. **`S24E-R1` (`1-CPE Clean-SNR Regime: iw phy phy0 set rts off` — `KEEP_NEW_CHAMPION`)**:
   - Explicitly enforcing `iw phy phy0 set rts off` on both `LAP-120` and `Loco 5AC` under 1-CPE clean-SNR conditions (`active_busy_cpes == 1`) delivered **`73.641 Mbps` (`+21.87%` vs `60.427 Mbps` control mean)** at an essentially identical `p95` RTT (`19.791 ms` vs `19.543 ms`, `+1.27%`), eliminating the transient `A1` throughput dip (`44.673 Mbps`, `p99=50.088 ms`) and clamping `p99` RTT to `21.84..27.21 ms`.
2. **`S24E-R2` (`3-CPE Contention Regime: M2 Adaptive RTS/CTS 512B + M1 Dynamic Responsible-Airtime Weights` — `KEEP_NEW_CHAMPION`)**:
   - Under simultaneous 3-CPE heterogeneous load (`Loco 5AC` + `Rocket Prism 5AC` + `LiteBeam M5`), enabling `rts 512` across the sector when `active_busy_cpes >= 2` alongside `M1` dynamic Responsible-Airtime weight adjustment (`Loco 5AC` `640 -> 600..604` based on live `1.6%..2.7%` retry ratio) simultaneously boosted aggregate 3-CPE goodput by **`+5.24%` (`56.785 -> 59.761 Mbps`, reaching `60.557 Mbps` / `3.028 Mbps/MHz` in `B2`)** AND slashed worst-case sector `p95` RTT by **`-41.98%` (`110.404 -> 64.060 ms`)**.
   - Without RTS/CTS protection (`A1`), multi-station collisions spiked `Loco 5AC` `p95` RTT to `150.179 ms` (`p99 = 172.538 ms`) and `LiteBeam M5` `p95` RTT to `145.037 ms` (`p99 = 299.389 ms`). With `M2` Adaptive RTS/CTS `512 B` active (`B1` and `B2`), worst-case sector `p95` RTT stayed tightly bounded at **`60.630 ms` (`B1`) and `67.490 ms` (`B2`)**, with `p99` RTT cut by more than `3.8x` (`299.389 -> 72.241..73.801 ms`).
3. **Final Live RAM State (`Champion v5`)**:
   - All 4 bench radios (`LAP-120` AP, `NanoStation 5AC Loco` STA, `Rocket Prism 5AC Gen2` STA, and `LiteBeam M5` STA) were verified at completion and left in the winning **Stage 24E Champion v5** RAM state (`persistent_flash_writes: false`).
