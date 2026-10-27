<!-- doc-head: STAGE12_UNIFIED_PTMP_MAC_QOE_CONTROLLER.md preserved document content -->
<!-- /doc-head -->


# Stage 12 — Unified PtMP MAC & QoE Closed-Loop Controller (`R116..R133` Physical Bench Laws + 4-Pillar Synthesis)

- **Task ID**: `T-ORCA-GEM1-04` (`orca:gemini-lane1`)
- **Controller Module**: [`controller/unified_ptmp_mac_qoe_controller.py`](../controller/unified_ptmp_mac_qoe_controller.py)
- **Verification Test Suite (`4/4 PASS`)**: [`tests/test_unified_ptmp_mac_qoe_controller.py`](../tests/test_unified_ptmp_mac_qoe_controller.py)
- **Safety Gate**: `automatic_execution_allowed = False` (100% offline/advisory; requires operator & Canary gate approval before live execution).

---

## 1. Executive Summary & Epistemic Ledger

This document synthesizes the hardware-verified physical bench laws from **`R116..R133`** (`LAP-120` $\leftrightarrow$ `Loco5AC` 16-block counterbalanced AB/BA crossovers across `1 km .. 14 km`) with our Stage 7–12 multi-CPE controllers into a single deterministic **Unified PtMP MAC & QoE Controller** ([`controller/unified_ptmp_mac_qoe_controller.py`](../controller/unified_ptmp_mac_qoe_controller.py)):

1. **Pillar 1 — Dynamic `RTS/CTS` Hysteresis & `K=4` Soft-TDMA Return-ACK Clocking (`R122..R133` + Stage 7.3)**:
   - **Why Static `rts=256` Hurts Single-Uploader Throughput (`R122..R127` `CONFIRMED ON BENCH`)**: When only `active_ul_cpes == 1` is transmitting on the sector, enabling `iw phy phy0 set rts 256` cuts MAC retry rate by **`-74.9% to -77.8%`** (`1.442% -> 0.330%` at `12 km`, `p95 = 11.46..15.27 ms` vs `44.91..68.87 ms`), **but** pays a deterministic `RTS + SIFS + CTS + SIFS + 2\tau(d)` handshake tax on every A-MPDU that grows with coverage class from **`-7.01%` (`1 km`) to `-19.73%` (`14 km`)**.
   - **Why Dynamic `rts=off` Wins for Single Uploader & Low Retry Rate (`R128..R133` `CONFIRMED ON BENCH`)**: Keeping `rts=off` when `active_ul_cpes == 1` and `mac_retry_rate < 4.0%` completely eliminates the `7.0%..19.7%` RTS handshake tax (`100.07 vs 102.00 Mbps` at `3 km`, `92.31 vs 93.21 Mbps` at `6 km`) while cutting `p50` RTT by **`-61.8%`** (`6.48 vs 16.95 ms`) and `p95` RTT by **`-59.5%`** (`22.99 vs 56.69 ms`).
   - **Closed-Loop Hysteresis Rule**:
     - **ENGAGE (`rts=256` + `K=4` Soft-TDMA Return-ACK Clocking)**: Whenever `active_ul_cpes >= 2` **OR** `sector_mac_retry_rate_pct >= 4.0%`.
     - **HOLD (`[2.0%, 4.0%)` Deadband)**: Retain `rts=256` when `previous_rts_enabled == True` and `2.0% <= sector_mac_retry_rate_pct < 4.0%` to prevent rapid mode flapping.
     - **RELEASE (`rts=off`, `K=1`)**: Whenever `active_ul_cpes <= 1` **AND** `sector_mac_retry_rate_pct < 2.0%` (`< 4.0%` when already `off`).
2. **Pillar 2 — Concave-Logarithmic `CPE BE` Scaling (`2100 .. 4100 µs` across `100 m .. 14 km`, `R116..R121` `CONFIRMED ON BENCH`)**:
   - Eliminates the single-CPE uplink BDP starvation dip observed with static `2100/4200 µs` (`R108/R109`) by scaling `cpe_be_low_us` along the verified concave-logarithmic curve (`2100 µs` at `100 m` $\rightarrow$ `2650 µs` at `1 km` $\rightarrow$ `3150 µs` at `3 km` $\rightarrow$ `3550 µs` at `6 km` $\rightarrow$ `3800 µs` at `9 km` $\rightarrow$ `3950 µs` at `12 km` $\rightarrow$ `4100 µs` at `14 km`), paired with `TSQ = 1 MB` (`tcp_limit_output_bytes = 1048576`), `CPE codel = 16/80 ms`, `CPE rc_per_thresh = 50%`, `AP BE = 1900/3800 µs` (`codel = 10/50 ms`, `RC = 24%`), `airtime_flags = 1`, `fq_limit = 2048`, `force_tx_status = 1`, and `retry = 7/4`.
3. **Pillar 3 — Per-CPE Distance & Mixed-MCS `airtime_weight` + `Deficit:BE` Rescue (`Stage 7.4` & `Stage 8A`)**:
   - Assigns per-station DRR `airtime_weight` (`144..512`), detects negative `Deficit: BE` starvation spirals (`deficit_be_us < -10,000 µs`, e.g., `-67,099 µs`), and steers small interactive/TCP-ACK packets (`<= 160B`) into `WMM AC_VO` (`DSCP EF`, `Deficit: VO +256 µs`).
4. **Pillar 4 — Closed-Loop Per-CPE ATPC (`<= -48 dBm` AP LNA Ceiling) & MCS Ceiling (`1..14 km`, `T-ORCA-GEM1-03`)**:
   - Steps down close-in CPE TX power so `AP RX RSSI <= -48.0 dBm` (`-52.0 dBm` target) to prevent AP AGC desensitization, and caps per-CPE VHT MCS (`0..9`, `NSS 1..2`) according to usable CINR, distance timing guard, chain imbalance, and PA EVM linearity.

---

## 2. Empirical Hardware Anchor Table (`R116..R131` Physical Bench Receipts)

All rows below are **CONFIRMED ON BENCH** (`16-Block Counterbalanced AB/BA Crossovers`, `32 windows`, `N=160` RTT samples per arm, `0.0%` packet loss on both arms):

| Run ID | Regime & Flows | Distance / CovClass | Slot / ACK_TO ($\mu\text{s}$) | `CPE BE` ($\mu\text{s}$) | `RTS` Mode | Stock Goodput (Mbps) | Tuned Goodput (Mbps) | Goodput Ratio | Stock $\rightarrow$ Tuned MAC Retry (%) | Verdict & Physical Law |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`R116`** | `unidir_ul_2flow` | `1,000 m` (`cov=2`) | `15 / 30 µs` | `2650 / 5300` | `off` | `59.19` | **`59.26`** | **`1.0012` (`+0.12%`)** | `1.102% -> 0.812%` | **`KEEP` (`p95 = 10.98 vs 43.64 ms`, `16/16` wins)** |
| **`R117`** | `unidir_ul_2flow` | `3,000 m` (`cov=6`) | `27 / 54 µs` | `3150 / 6300` | `off` | `60.46` | **`59.43`** | **`0.9830` (`98.3%`)** | `1.592% -> 1.409%` | **`KEEP` (Recovers `R109` `-8.44%` UL dip)** |
| **`R118`** | `unidir_ul_2flow` | `6,000 m` (`cov=13`) | `48 / 96 µs` | `3550 / 7100` | `off` | `53.14` | **`52.23`** | **`0.9829` (`98.3%`)** | `0.966% -> 0.973%` | **`KEEP` (`98.3%` UL parity at `6 km`)** |
| **`R119`** | `unidir_ul_2flow` | `9,000 m` (`cov=20`) | `69 / 138 µs` | `3800 / 7600` | `off` | `48.30` | **`50.02`** | **`1.0356` (`+3.56%`)** | `1.356% -> 1.460%` | **`KEEP` (`+3.56%` UL goodput gain at `9 km`)** |
| **`R120`** | `unidir_ul_2flow` | `12,000 m` (`cov=26`) | `87 / 174 µs` | `3950 / 7900` | `off` | `47.40` | **`47.68`** | **`1.0059` (`+0.59%`)** | `0.808% -> 0.875%` | **`KEEP` (`+0.59%` UL goodput gain at `12 km`)** |
| **`R121`** | `unidir_ul_2flow` | `14,000 m` (`cov=31`) | `102 / 204 µs` | `4100 / 8200` | `off` | `47.51` | **`46.77`** | **`0.9844` (`98.4%`)** | `0.826% -> 0.929%` | **`KEEP` (`98.4%` UL parity at `14 km` max covclass)** |
| **`R123`** | `unidir_ul_8flow` | `1,000 m` (`cov=2`) | `15 / 30 µs` | `2650 / 5300` | `256` | `55.16` | `51.29` | `0.9299` (`-7.01%`) | **`1.030% -> 0.229%` (`-77.8%`)** | Quantifies `7.01%` single-CPE RTS tax (`p95 = 11.46 ms`) |
| **`R122`** | `unidir_ul_8flow` | `3,000 m` (`cov=6`) | `27 / 54 µs` | `3150 / 6300` | `256` | `52.33` | `47.97` | `0.9167` (`-8.33%`) | **`1.060% -> 0.253%` (`-76.1%`)** | Quantifies `8.33%` single-CPE RTS tax (`p95 = 15.27 ms`) |
| **`R124`** | `unidir_ul_8flow` | `6,000 m` (`cov=13`) | `48 / 96 µs` | `3550 / 7100` | `256` | `50.24` | `43.40` | `0.8639` (`-13.61%`) | **`1.406% -> 0.345%` (`-75.5%`)** | Quantifies `13.61%` single-CPE RTS tax (`p95 = 12.66 ms`) |
| **`R125`** | `unidir_ul_8flow` | `9,000 m` (`cov=20`) | `69 / 138 µs` | `3800 / 7600` | `256` | `48.81` | `40.52` | `0.8302` (`-16.98%`) | **`1.358% -> 0.333%` (`-75.5%`)** | Quantifies `16.98%` single-CPE RTS tax (`p95 = 13.52 ms`) |
| **`R126`** | `unidir_ul_8flow` | `12,000 m` (`cov=26`) | `87 / 174 µs` | `3950 / 7900` | `256` | `45.81` | `37.66` | `0.8221` (`-17.79%`) | **`1.442% -> 0.330%` (`-77.1%`)** | Quantifies `17.79%` single-CPE RTS tax (`p95 = 13.30 ms`) |
| **`R127`** | `unidir_ul_8flow` | `14,000 m` (`cov=31`) | `102 / 204 µs` | `4100 / 8200` | `256` | `44.49` | `35.71` | `0.8027` (`-19.73%`) | **`1.344% -> 0.338%` (`-74.9%`)** | Quantifies `19.73%` single-CPE RTS tax (`p95 = 14.12 ms`) |
| **`R129`** | `unidir_ul_8flow` | `3,000 m` (`cov=6`) | `27 / 54 µs` | `3150 / 6300` | **`off`** | `102.00` | **`100.07`** | **`0.9811` (`98.1%`)** | `0.017% -> 0.008%` | **`KEEP` (`rts=off` eliminates `8.33%` RTS tax at `N_ul=1`)** |
| **`R130`** | `unidir_ul_8flow` | `6,000 m` (`cov=13`) | `48 / 96 µs` | `3550 / 7100` | **`off`** | `93.21` | **`92.31`** | **`0.9904` (`99.0%`)** | `0.015% -> 0.005%` | **`KEEP` (`p50 = 6.48 vs 16.95 ms`, `p95 = 22.99 vs 56.69 ms`, `16/16` wins)** |

---

## 3. Unified Controller Output Matrix (`1.0 km .. 14.0 km`)

Generated by [`evaluate_unified_1km_to_14km_bench_matrix()`](../controller/unified_ptmp_mac_qoe_controller.py):

| Distance $d$ | Cov. Class | Slot / ACK_TO ($\mu\text{s}$) | `AP BE` ($\mu\text{s}$) | Concave-Log `CPE BE` ($\mu\text{s}$) | Single-Uploader (`N_ul=1, retry<4%`) `RTS` / `K` / Tax Saved | Multi-Uploader (`N_ul=8` or `retry>=4%`) `RTS` / `K` / $N_{\text{eff}}$ | Max AP RX After ATPC |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1,000 m** | `2` | `15 / 30 µs` | `1900 / 3800` | **`2650 / 5300`** | **`rts=off` / `K=1` / `+7.01%` saved** | **`rts=256` / `K=4` / $N_{\text{eff}}=3.17$** | `-52.0 dBm` (`<= -48 dBm`) |
| **3,000 m** | `6` | `27 / 54 µs` | `1900 / 3800` | **`3150 / 6300`** | **`rts=off` / `K=1` / `+8.33%` saved** | **`rts=256` / `K=4` / $N_{\text{eff}}=3.17$** | `-53.0 dBm` (`<= -48 dBm`) |
| **6,000 m** | `13` | `48 / 96 µs` | `1900 / 3800` | **`3550 / 7100`** | **`rts=off` / `K=1` / `+13.61%` saved** | **`rts=256` / `K=4` / $N_{\text{eff}}=3.17$** | `-55.0 dBm` (`<= -48 dBm`) |
| **9,000 m** | `20` | `69 / 138 µs` | `1900 / 3800` | **`3800 / 7600`** | **`rts=off` / `K=1` / `+16.98%` saved** | **`rts=256` / `K=4` / $N_{\text{eff}}=3.17$** | `-55.0 dBm` (`<= -48 dBm`) |
| **12,000 m** | `27` | `90 / 180 µs` | `1900 / 3800` | **`3950 / 7900`** | **`rts=off` / `K=1` / `+17.79%` saved** | **`rts=256` / `K=4` / $N_{\text{eff}}=3.17$** | `-55.0 dBm` (`<= -48 dBm`) |
| **14,000 m** | `31` | `102 / 204 µs` | `1900 / 3800` | **`4100 / 8200`** | **`rts=off` / `K=1` / `+19.73%` saved** | **`rts=256` / `K=4` / $N_{\text{eff}}=3.17$** | `-55.0 dBm` (`<= -48 dBm`) |

---

## 4. Verification Receipt

- `pytest tests/test_unified_ptmp_mac_qoe_controller.py`: **`4/4 PASSED` (`100%`)**
