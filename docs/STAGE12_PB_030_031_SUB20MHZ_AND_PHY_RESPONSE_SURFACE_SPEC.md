<!-- doc-head: STAGE12_PB_030_031_SUB20MHZ_AND_PHY_RESPONSE_SURFACE_SPEC.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — `PB-030` (`5/10 MHz` Cabled Loop) & `PB-031` (`LDPC/BCC/STBC/SGI/CCA` Response Surface) Specification

- **Date**: 2026-10-24
- **Gates**: `PB-030` & `PB-031` (`automatic_execution_allowed = False`, awaiting `PB-020` cabled bench execution)
- **Orchestrator & Compiler**: [`controller/pb_030_031_phy_response_surface_harness.py`](../controller/pb_030_031_phy_response_surface_harness.py)
- **Generated Experiment Matrix**: [`artifacts/qca988x/pb_030_031_experiment_matrix.json`](../artifacts/qca988x/pb_030_031_experiment_matrix.json)
- **Verification Test Suite**: [`tests/test_pb_030_031_phy_response_surface_harness.py`](../tests/test_pb_030_031_phy_response_surface_harness.py)

---

## 1. Objective & Physical-Limit Equations (`PB-030` & `PB-031`)

Every run in `PB-030` and `PB-031` is evaluated with explicit channel-width normalization (`channel_width_mhz` $\in \{5, 10, 20, 40\}$ MHz, never dividing by a hard-coded `40 MHz`) and three spectral efficiency ratios:

$$\eta_{\text{goodput}} = \frac{G_{\text{application}}}{B} \quad (\text{bits/s/Hz}), \qquad \eta_{\text{PHY}} = \frac{R_{\text{nominal PHY}}}{B}, \qquad \eta_{\text{MAC}} = \frac{G_{\text{application}}}{R_{\text{nominal PHY}}}$$

along with the implementation-gap diagnostic $\Gamma$ (dB):

$$\Gamma_{\text{dB}} = 10 \log_{10}\!\left(\frac{\mathrm{SNR}_{\text{linear}}}{2^{\eta_{\text{goodput}}} - 1}\right)$$

---

## 2. `PB-030`: `5/10/20/40 MHz` Cabled Loop & Spectral Efficiency Matrix

Narrowing the QCA988x clock/channel filter from `20 MHz` to half-rate (`10 MHz`) and quarter-rate (`5 MHz`) lowers the thermal noise floor by `+3.01 dB` and `+6.02 dB` respectively while scaling symbol duration (`4.0 us` $\rightarrow$ `8.0 us` $\rightarrow$ `16.0 us`).

| Coaxial Attenuation | `5 MHz` (`goodput/MHz`) | `10 MHz` (`goodput/MHz`) | `20 MHz` (`goodput/MHz`) | `40 MHz` (`goodput/MHz`) | Optimal Spectral Efficiency Mode |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **`50 dB`** (High SNR) | `6.5816` (`32.91` Mbps) | `6.5892` (`65.89` Mbps) | `6.5854` (`131.71` Mbps) | `7.6000` (`304.00` Mbps) | `40 MHz` / `20 MHz` (high absolute capacity) |
| **`70 dB`** (Mid-Low SNR) | `5.8920` (`29.46` Mbps) | `4.8442` (`48.44` Mbps) | `4.0767` (`81.53` Mbps) | `3.5270` (`141.08` Mbps) | `5/10 MHz` gain `+20%..+44%` in `goodput/MHz` |
| **`84 dB`** (Deep Fade / Edge) | `2.0414` (`10.21` Mbps) | `1.2775` (`12.78` Mbps) | `0.6932` (`13.86` Mbps) | `0.8000` (`32.00` Mbps floor) | `5/10 MHz` sustain higher MCS & $+3..6$ dB link margin |

---

## 3. `PB-031`: Controlled PHY/BB Parameter Response-Surface Treatments (`N=6` Paired Blocks)

| Treatment ID | Knob Under Test | Baseline (`Arm A`) | Candidate (`Arm B`) | `goodput/MHz` Delta | `p99` Delta | Paired `p`-Value | Gatekeeper Verdict |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| **`PB-031-H1`** | `fec_mode` (`18 dB` SNR) | `BCC` (`20 MHz`) | `LDPC` (`20 MHz`) | **`+13.25%`** | `-12.92%` | `0.0312` | **`PROMOTE`** |
| **`PB-031-H2`** | `sgi_enabled` (Long multipath) | `SGI 400 ns` | `LGI 800 ns` | **`+9.15%`** | `-25.25%` | `0.0312` | **`PROMOTE`** |
| **`PB-031-H3`** | `stbc_enabled` (Rank-1 fade) | `STBC Off` | `2x1 STBC On` | **`+16.35%`** | `-25.67%` | `0.0312` | **`PROMOTE`** |
| **`PB-031-H4`** | `cca_ed_threshold_dbm` (Neg. Ctrl) | `-78 dBm` | `-62 dBm` | `+7.32%` | **`+60.52%`** | `0.0005` | **`REJECT` (`p99` violation)** |
