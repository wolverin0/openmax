<!-- doc-head: STAGE12_LTU_12X_AND_UPH_RUNTIME_CONTROLLER.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — `ubnt_poll_host.ko` (`cms_bias` / `voip_bias` / `netconf`) Mode B & LTU `4096-QAM` (`12x`) Runtime Optimizer Controller

**Study ID**: `FMX-STAGE12-UPH-MODE-B-AND-LTU-12X-RUNTIME-OPTIMIZER-20261024`  
**Task ID**: `T-SUB-GEM1-04`  
**Status**: Completed (100% Offline Controller, Diagnostic Verifier, & Guarida Recommendations)  
**Controller Implementation**: [`controller/ltu_12x_and_uph_runtime_optimizer.py`](../controller/ltu_12x_and_uph_runtime_optimizer.py)  
**Recommendations Artifact**: [`artifacts/firmware_re_xc_ltu/guarida_uph_and_ltu_12x_recommendations_20261024.json`](../artifacts/firmware_re_xc_ltu/guarida_uph_and_ltu_12x_recommendations_20261024.json)  
**Verification Suite**: [`tests/test_ltu_12x_and_uph_runtime_optimizer.py`](../tests/test_ltu_12x_and_uph_runtime_optimizer.py)

---

## 1. Epistemic Classification (`AGENTS.md` Section 2 & 6)

| Component / Finding | Epistemic Status | Verification Basis |
| :--- | :---: | :--- |
| `ubnt_poll_host.ko` `.rodata` (`60cadb35...`) and `.data` (`21c72f66...`) byte-identity across `WA.v8.7.25` and `XC.v8.7.25` | **CONFIRMED** | Direct ELF section hash and binary extraction in [`artifacts/firmware_re_xc_ltu/ubnt_poll_and_ltu_12x_deep_re_20261024.json`](../artifacts/firmware_re_xc_ltu/ubnt_poll_and_ltu_12x_deep_re_20261024.json) |
| `_retr_supression_levels` (`cms_bias = 0..9`, 280 bytes) & `_voip_dynamic_duration_levels` (`voip_bias = 0..9`, 120 bytes) | **CONFIRMED** | Decompiled 32-bit big-endian `.rodata` tables from `ubnt_poll_host.ko` |
| `ptmp_netconf` 104-byte profile (`down_dur`, `up_dur`, `cbp_duty_cycle_thresh`, `dl_per_thresh_nr`, `txop_qual_thresh_nr_nb`, etc.) | **CONFIRMED** | Decompiled `.data` `0x04a0` default and `.rodata` `0x0cf8` parser table |
| LTU `ame_core.ko` `table_ptpPwrRange` (`10..50 MHz` enabled vs `60/80/100 MHz` `(0, 0)`), `sensitivity`, `autoMcsAllSisoTbl`, `startThrd_4096=97%`, `stayThrd_4096=90%` | **CONFIRMED** | Extracted from `LTU.v2.3.4` (`AF-5XHD` / `LTU-Rocket` / `LTU-LR` / `LTU-Pro` / `LTU-Lite`) `ame_core.ko` |
| Physical-layer non-portability of `4096-QAM` (`12x`, `MCS 31`) to `QCA988x` (`802.11ac` VHT capped at `256-QAM` `MCS 9`) | **CONFIRMED** | Silicon boundary analysis (`QCA988x` baseband vs Ubiquiti custom `ame` FPGA/ASIC + `AME_EAB_*` + DPD) |
| Projected airtime-tax and p95 RTT reductions on `Panel2-Guarida` and `Panel3-Guarida` under `cms_bias`/`voip_bias` tuning | **INFERRED** | Analytical projection from decompiled `ubnt_poll_host.ko` retry-suppression and contention-window tables |

---

## 2. Part A — Stock `airOS 8` Mode B Runtime Optimizer (`ubnt_poll_host.ko`)

### 2.1 Why Default `cms_bias = 0` Suffers Under Weak-Edge CPEs
In stock `airOS 8` (`WA.v8.7.25` and `XC.v8.7.25`), the default `ptmp_netconf` profile initializes with `cms_bias = 0` (`CONFIRMED`):
- `dl_per_thresh_nr = 100%`, `ul_per_thresh_nr = 100%`, `ul_per_thresh_nb = 100%`
- `txop_qual_thresh_nr_nb = 20%`

Because the non-retry PER threshold is set to `100%`, the scheduler allows weak-edge CPEs (`RSSI <= -70 dBm` or severe hidden-node collisions) to consume the full `max_ret_rounds = 15` (`max_ret_NF_rounds = 20`) retry budget during low-MCS drops before suppressing retries or clamping their TXOP duration.

### 2.2 Decompiled `_retr_supression_levels` (`cms_bias = 0..9`) & `_voip_dynamic_duration_levels` (`voip_bias = 0..9`) (`CONFIRMED`)
Writing `N` (`0..9`) to `/proc/sys/dev/uph_wifi0/cms_bias` overwrites the 7 retry-suppression fields in `ptmp_netconf`:

| `cms_bias` | `dl_rate_ratio_nr` | `dl_per_nr` (%) | `ul_rate_ratio_nb` | `ul_per_nb` (%) | `ul_rate_ratio_nr` | `ul_per_nr` (%) | `txop_qual_nr_nb` (%) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0 (Default)** | 0 | **100%** | 0 | **100%** | 0 | **100%** | **20%** |
| **4 (`Panel3`)** | 17 | **70%** | 17 | **70%** | 26 | **70%** | **65%** |
| **6 (`Panel2`)** | 26 | **70%** | 26 | **70%** | 34 | **65%** | **70%** |
| **9 (Max)** | 34 | **50%** | 34 | **50%** | 45 | **50%** | **75%** |

Writing `N` (`0..9`) to `/proc/sys/dev/uph_wifi0/voip_bias` adjusts the dynamic TDMA frame shortening thresholds (`_voip_dynamic_duration_levels`):
- **`voip_bias = 0` (Default)**: Requires `11` high-contention STAs before clamping frame duration to `20.0 ms` DL / `10.0 ms` UL.
- **`voip_bias = 4` (`Panel3-Guarida` Recommended)**: Triggers at `3` contending STAs, clamping frame duration to `15.0 ms` DL / `7.5 ms` UL.
- **`voip_bias = 6` (`Panel2-Guarida` Recommended)**: Triggers at `5` contending STAs, clamping frame duration to `15.0 ms` DL / `7.5 ms` UL.

### 2.3 Guarida Mode B Sector Recommendations (`INFERRED` Runtime Gain from `CONFIRMED` Tables)

| Parameter | `Panel2-Guarida` (`22 CPEs`, `20 MHz`, Mode B) | `Panel3-Guarida` (`6 CPEs`, `20 MHz`, Mode B) |
| :--- | :--- | :--- |
| **Recommended `cms_bias`** | **`6`** (`dl_per=70%`, `ul_per=65%`, `txop_qual=70%`) | **`4`** (`dl_per=70%`, `ul_per=70%`, `txop_qual=65%`) |
| **Recommended `voip_bias`** | **`6`** (`5 STAs -> 15ms DL / 7.5ms UL`) | **`4`** (`3 STAs -> 15ms DL / 7.5ms UL`) |
| **Recommended `daprot` / `atpc`** | `daprot = 2`, `atpc = "1 -52 4 22"` | `daprot = 1`, `atpc = "1 -52 4 22"` |
| **`netconf` Frame Timing** | `down_dur 10000`, `up_dur 6000`, `up_dur_gap 300`, `cbp_duty_cycle_thresh 15` | `down_dur 8000`, `up_dur 6500`, `up_dur_gap 400`, `cbp_duty_cycle_thresh 18` |
| **Per-STA Priority Clamping (`sta_priority`)** | Clamp `FRANCO_Debora` (`-70 dBm`) & `Marilina SEVERO` (`-74 dBm`) to **`0`** (`Low`); promote healthy links to **`2`** (`High`) | Set `GALEANO_Rocio` (`10 dB` chain delta) to **`1`** (`Medium`); healthy links to **`2`** (`High`) |
| **Projected Airtime-Tax / p95 RTT Reduction** | **`-38.84%` airtime tax / `-38.0%` p95 RTT** (`INFERRED`) | **`-31.80%` airtime tax / `-30.0%` p95 RTT** (`INFERRED`) |
| **Automatic Execution Allowed** | `false` | `false` |

---

## 3. Part B — LTU `ame_core.ko` `4096-QAM` (`12x`, `MCS 31`) 6-Gate Diagnostic & Runtime Optimizer

### 3.1 Silicon Boundary: Why `4096-QAM` (`12x`) Cannot Run on `QCA988x` (`CONFIRMED`)
- **`QCA9880` / `QCA9882` (`airMAX AC`)**: Hardwired IEEE 802.11ac VHT PHY/baseband silicon whose constellation mapper and LDPC/Viterbi decoder top out at **`256-QAM` (`8x`, VHT MCS 9)**.
- **Ubiquiti LTU (`AF-5XHD`, `LTU-Rocket`, `LTU-LR`, `LTU-Pro`, `LTU-Lite`)**: Runs `ame_core.ko` over Ubiquiti's custom **`ame` FPGA/ASIC radio engine**, which implements custom equalizer/symbol recovery (`AME_EAB_*`) and Digital Pre-Distortion (DPD) required to achieve the `~-40 dB` (`1.0%`) EVM floor of **`4096-QAM` (`12x`, LTU MCS 31)**.

### 3.2 The 6 Deterministic Gates for LTU `4096-QAM` (`12x`, `MCS 31`) (`CONFIRMED` from `ame_core.ko`)

[`diagnose_and_tune_ltu_12x_link()`](../controller/ltu_12x_and_uph_runtime_optimizer.py) evaluates every candidate link against all 6 hardware/firmware gates extracted from `ame_core.ko`:

1. **Gate 1 — Silicon Capability (`GATE_1_SILICON_HARDWIRED_256QAM`)**:
   - Rejects `QCA988x` / `802.11ac` hardware (capped at `256-QAM` `MCS 9`) and requires `Ubiquiti-AME-LTU` baseband.
2. **Gate 2 — Channel Bandwidth Ceiling (`GATE_2_BANDWIDTH_EXCEEDS_50MHZ`)**:
   - In `ame_core.ko:table_ptpPwrRange`, row index 7 (`4096-QAM`) is populated for `10, 20, 30, 40, 50 MHz` (`-66..-56 dBm` min, `-56..-54 dBm` max) and **explicitly zeroed to `(0, 0)` at `60, 80, and 100 MHz`**.
   - Any LTU link running at `80 MHz` or `100 MHz` is firmware-clamped to `1024-QAM` (`10x`, `MCS 23`). Controller recommends narrowing to `40 MHz` or `50 MHz` (`ame_cfg.sh RF bandwidth 40`).
3. **Gate 3 — `2x2 MIMO` Spatial Stream Requirement (`GATE_3_SISO_OR_CHAIN_IMBALANCE`)**:
   - `autoMcsAllSisoTbl` caps SISO links at `(23, 0)` (`1024-QAM` `10x`). `4096-QAM` (`(31, 1)`) only exists in `autoMcsOthersTbl` and requires balanced `2x2 MIMO` (`chain_imbalance_db <= 4.0 dB`).
4. **Gate 4 — PA Linearity & Conducted TX Power Backoff (`GATE_4_PA_EVM_BACKOFF_EXCEEDED`)**:
   - `mcs_txpwr_freq_ptp` and `af_ltu*_mcs_txpwr_freq` enforce strict conducted TX power ceilings for `4096-QAM`:
     - `AF-5XHD` / `LTU-Rocket`: **`16.0 dBm`**
     - `LTU-LR` (`5150–5350 MHz` low-band): **`12.0 dBm`**
     - `LTU-Lite` / `LTU-Pro` / `LTU-LR` (`5470–5875 MHz` high-band): **`10.0 dBm`**
   - Exceeding this ceiling compresses the PA and blocks `12x` entry unless TX power is backed off (`ame_cfg.sh RF txpwr <cap>`).
5. **Gate 5 — Minimum Sensitivity, PTP Target RSSI, & CINR (`GATE_5_INSUFFICIENT_RSSI` / `GATE_5B_INSUFFICIENT_CINR`)**:
   - Enforces `ame_core.ko:sensitivity` (`-66 dBm` @ `10 MHz`, `-63 dBm` @ `20 MHz`, `-61 dBm` @ `30 MHz`, `-59 dBm` @ `40 MHz`, `-58 dBm` @ `50 MHz`) and `CINR >= 32.0 dB`.
6. **Gate 6 — `autoMcsCeiling` & Codeword Pass-Rate Hysteresis (`GATE_6_AUTOMCS_CEILING_CLAMPED` / `GATE_6B_START_THRD_4096_NOT_MET`)**:
   - Requires `autoMcsCeiling == 31` (`mcs_ceiling_toggle_txpwr`) and enforces `ame_core.ko` hysteresis:
     - **Entry threshold**: `startThrd_4096 = 97%` (`codeword_pass_rate_1024qam_pct >= 97.0%`)
     - **Sustain threshold**: `stayThrd_4096 = 90%` (`codeword_pass_rate_1024qam_pct >= 90.0%`)
