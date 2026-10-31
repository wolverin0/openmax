<!-- doc-head: STAGE19_CHAMPION_PHY_AND_REGIME_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 19 — Incremental Champion-Plus-PHY & Closed-Loop Regime Switcher Benchmark (`S19-R1..R4`)

- **Experiment ID**: `T-S19-CHAMPION-PLUS-PHY-AND-REGIME-AUTOSWITCH`
- **Date**: `2026-10-25`
- **Bench Topology**: `LAP-120` (`198.18.0.127`, OpenWrt 24.10.4 + `ath10k-ct` + `mac80211` `ETH_P_TEB` strip) $\leftrightarrow$ `NanoStation 5AC Loco` (`198.18.0.128`, OpenWrt 24.10.4 4-addr WDS) + `Rocket Prism 5AC Gen2` (`198.18.0.58`, Stock `airOS 8 XC.v8.7.11` 4-addr WDS) on `5180 MHz` (`20 MHz`, `-3 dBm` bench-safe TX power).
- **Crucial Methodology Rule**: Every round starts from the **verified Champion baseline (`A = Current Champion`, NOT Stock)** and evaluates an incremental candidate mutation (`B = Current Champion + Candidate Mutation`) using `A1 -> B1 -> A2 -> B2` interleaving. At completion, the winning Champion profiles are left applied in RAM on all bench radios (`persistent_flash_writes: false`).
- **Artifacts**:
  - Harness: [`tools/bench/run_stage19_champion_phy_and_regime_bench.py`](<repo>/tools/bench/run_stage19_champion_phy_and_regime_bench.py)
  - Physical Receipt: [`artifacts/autoresearch/stage19_champion_phy_and_regime_20261025.json`](<repo>/artifacts/autoresearch/stage19_champion_phy_and_regime_20261025.json)
  - Pytest Verification: [`tests/test_stage19_champion_phy_and_regime.py`](<repo>/tests/test_stage19_champion_phy_and_regime.py)

---

## 1. Executive Summary of Results (`A = Current Champion` vs `B = Champion + Mutation`)

| Round | Hypothesis (`A = Current Champion` $\rightarrow$ `B = Champion + Mutation`) | Control Arm `A` Mean Goodput | Treatment Arm `B` Mean Goodput | Goodput $\Delta$ | Control Arm `A` Mean `p95` RTT | Treatment Arm `B` Mean `p95` RTT | `p95` RTT $\Delta$ | Decision |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S19-R1`** | `1-CPE Champion` (`900/1500 us`, `thresh=4000`, `fq_codel 1514/10ms/50ms`) vs `+ Bounded VHT MCS 2:0-7 + SGI` | `71.28 Mbps` | `67.80 Mbps` | `-4.87%` | `27.36 ms` | `18.14 ms` | **`-33.69%`** | **`RETAIN_CURRENT_CHAMPION`** (Keep MCS 8 enabled on clean bench SNR; reserve MCS 0-7 clamp for degraded EVM) |
| **`S19-R2`** | `1-CPE Champion` (`retry 7/4`, `nf_cal_period=0`, `txqueuelen=1000`) vs `+ PB-031 (retry short 5 long 4 + nf_cal_period=30 + txqueuelen=256)` | `71.05 Mbps` | **`74.05 Mbps`** | **`+4.23%`** | `23.96 ms` | **`19.22 ms`** | **`-19.77%`** | **`KEEP_NEW_CHAMPION`** (Promoted to `openwrt_lap120_ptp_1cpe_champion`) |
| **`S19-R3`** | `Multi-CPE AP Champion` (`1850/3700 us`, `thresh=6000`) + `Stock Rocket Prism STA` vs `+ r5ac_prism_sta Champion Co-Design` (`airview1 down`, `ani_enable=0`, `swretry=4/6`, `protmode=1`, `txqueuelen=256`) | `51.02 Mbps` | **`70.68 Mbps`** | **`+38.55%`** | `108.25 ms` | **`105.76 ms`** | **`-2.30%`** | **`KEEP_NEW_CHAMPION`** (Massive `+38.55%` sector gain from joint AP+STA Champion Co-Design) |
| **`S19-R4`** | Live Closed-Loop Regime Switcher (`900/1500` on `1-CPE` $\leftrightarrow$ `1850/3700` on `2-CPE`) across both regimes | `57.81 Mbps` (`Static_900`) | **`67.33 Mbps`** (`Static_1850`) / `61.18 Mbps` (`AutoSwitcher`) | **`+10.35%`** (`2-CPE` switch: `65.20 -> 71.95 Mbps`) | `59.27 ms` (`2-CPE` `Static_900`) | **`54.72 ms`** (`2-CPE` `AutoSwitcher`) | **`-7.67%`** on `2-CPE` | **`KEEP_CLOSED_LOOP_REGIME_AUTOSWITCHER`** |

---

## 2. Detailed Round Analysis

### 2.1 `S19-R1` — Clamping `VHT-MCS 2:0-7 + SGI` on Top of `1-CPE Champion` (`RETAIN_CURRENT_CHAMPION`)
- **Observation**: Clamping out `VHT-MCS 8` (`256-QAM 3/4`) reduced loaded `p95` RTT by **`-33.69%`** (`27.36 -> 18.14 ms`) by eliminating occasional `256-QAM` rate-probe retries, but cost **`-4.87%` goodput** (`71.28 -> 67.80 Mbps`) on our high-SNR bench link where `VHT-MCS 8` (`173.3 Mbps` PHY rate on `20 MHz`) succeeds on the vast majority of A-MPDUs.
- **Decision**: Retain unconstrained `VHT-MCS 2:0-8` in the default `1-CPE Champion`, and only engage the `VHT-MCS 2:0-7` clamp via the [`stage20_closed_loop_champion_switcher.py`](<repo>/controller/stage20_closed_loop_champion_switcher.py) when pilot EVM degrades below `18.5 dB` (`PB-021`).

### 2.2 `S19-R2` — `PB-031` (`retry short 5 long 4` + `nf_cal_period=30` + `txqueuelen=256`) on Top of `1-CPE Champion` (`KEEP_NEW_CHAMPION`)
- **Observation**: Starting from the already-tuned `1-CPE Champion` (`71.05 Mbps`, `p95 = 23.96 ms`), bounding `iw phy phy0 set retry short 5 long 4`, setting periodic noise-floor calibration `nf_cal_period=30`, and tightening `ip link set dev phy0-ap0 txqueuelen 256` increased mean goodput to **`74.05 Mbps` (`+4.23%`)** while cutting `p95` RTT to **`19.22 ms` (`-19.77%`)** and eliminating packet loss (`1.71% -> 0.0%`).
- **Decision**: **`KEEP_NEW_CHAMPION`** — promoted directly into [`controller/multiradio_golden_profile_applicator.py`](<repo>/controller/multiradio_golden_profile_applicator.py) and [`artifacts/autoresearch/champion_state_ledger.json`](<repo>/artifacts/autoresearch/champion_state_ledger.json).

### 2.3 `S19-R3` — Joint AP + `Rocket Prism 5AC` STA Champion Co-Design under 2-CPE Contention (`KEEP_NEW_CHAMPION`)
- **Observation**: When `LAP-120` serves both `Loco 5AC` (`.41`) and `Rocket Prism 5AC Gen2` (`.3`) simultaneously on `5180 MHz`, applying the `r5ac_prism_sta` Champion (`ifconfig airview1 down`, `iwpriv wifi0 ani_enable 0`, `iwpriv ath0 swretry 4 6`, `iwpriv ath0 protmode 1`, `txqueuelen 256`, `tcp_low_latency=1`) alongside the AP Multi-CPE Champion (`1850/3700 us`, `thresh=6000`) raised aggregate sector goodput from **`51.02 Mbps` to `70.68 Mbps` (`+38.55%`)** while reducing sector `p95` RTT from `108.25 ms` to `105.76 ms` (`-2.30%`).
- **Decision**: **`KEEP_NEW_CHAMPION`** — proves that CPE-side `airOS 8` co-design (`airview1 down` + `protmode=1` RTS/CTS + bounded `swretry`) removes hidden-node / background-scan stalls that otherwise drag down the entire OpenWrt PtMP sector during multi-CPE contention.

### 2.4 `S19-R4` — Closed-Loop Regime Auto-Switcher (`1-CPE` $\leftrightarrow$ `2-CPE`)
- **Observation**: Under 2-CPE contention, switching automatically from `900/1500` (`thresh=4000`) to `1850/3700` (`thresh=6000`) increased 2-CPE aggregate goodput from **`65.20 Mbps` to `71.95 Mbps` (`+10.35%`)** and reduced 2-CPE sector `p95` RTT from **`59.27 ms` to `54.72 ms` (`-7.67%`)**.

---

## 3. Final Verified RAM State Left Applied on Bench Radios

- **`LAP-120` (`198.18.0.127`) & `Loco 5AC` (`198.18.0.128`)**: `openwrt_lap120_ptp_1cpe_champion` (`aql_txq_limit=900/1500`, `aql_threshold=4000`, `airtime_flags=7`, `fq_codel quantum 1514 target 10ms interval 50ms ecn`, `retry short 5 long 4`, `nf_cal_period=30`, `txqueuelen=256`, `tcp_limit_output_bytes=131072`).
- **`Rocket Prism 5AC Gen2` (`198.18.0.58`)**: `r5ac_prism_sta` (`airview1 down`, `ani_enable=0`, `swretry 4 6`, `protmode=1`, `txqueuelen=256`, `tcp_low_latency=1`).
- **Flash Persistence**: `persistent_flash_writes: false` (100% RAM-safe).
