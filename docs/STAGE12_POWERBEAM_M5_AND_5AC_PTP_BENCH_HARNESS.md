<!-- doc-head: STAGE12_POWERBEAM_M5_AND_5AC_PTP_BENCH_HARNESS.md preserved document content -->
<!-- /doc-head -->

# Stage 12: PowerBeam M5 300 (`XW.v6.3.2`) & PowerBeam 5AC (`WA.v8.7.25`) PtP/PtMP Bench Qualification Harness

- **Status**: `QUALIFIED_OFFLINE_HARNESS` (`automatic_execution_allowed=False`, `live_ssh_allowed=False`, `auto_flash_allowed=False`)
- **Controller Implementation**: [`controller/powerbeam_m5_and_5ac_bench_harness.py`](../controller/powerbeam_m5_and_5ac_bench_harness.py)
- **Generated Bench Plan Artifact**: [`artifacts/qca988x/powerbeam_m5_5ac_bench_plan_20261024.json`](../artifacts/qca988x/powerbeam_m5_5ac_bench_plan_20261024.json) (`plan_sha256: 926ac9c0e3d2685ed3ca7f09d5dc002f994aec85bcf5f0f5cb009ea284b210ec`)
- **Verification Suite**: [`tests/test_powerbeam_m5_and_5ac_bench_harness.py`](../tests/test_powerbeam_m5_and_5ac_bench_harness.py)

---

## 1. Hardware Inventory & Architecture Boundary

| Unit ID | Model | Family | SoC & Radio | Stock Firmware | Supported Channel Widths (MHz) | Role in Battery |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PBE-M5-300-A` | PowerBeam M5 300 | `XW` (`0xe4b5`) | `AR9342` (`535 MHz` MIPS 74Kc) integrated `802.11n` 2x2 MIMO | `XW.v6.3.2` | `{5, 10, 20, 30, 40}` (`HT5..HT40`) | PtP AP / Mixed PtMP Legacy STA #1 |
| `PBE-M5-300-B` | PowerBeam M5 300 | `XW` (`0xe4b5`) | `AR9342` (`535 MHz` MIPS 74Kc) integrated `802.11n` 2x2 MIMO | `XW.v6.3.2` | `{5, 10, 20, 30, 40}` (`HT5..HT40`) | PtP STA / Mixed PtMP Legacy STA #2 |
| `PBE-5AC-A` | PowerBeam 5AC | `WA` (`0xe7f9`) | `AR9342` + `QCA988x hw2.0` (`0x4100016c`) `802.11ac` Wave 1 2x2 | `WA.v8.7.25` | `{5, 10, 20, 30, 40, 80}` (`VHT10..80`, `5 MHz` cabled `PB-030`) | PtP AP / Mixed PtMP AC Sector AP |
| `PBE-5AC-B` | PowerBeam 5AC | `WA` (`0xe7f9`) | `AR9342` + `QCA988x hw2.0` (`0x4100016c`) `802.11ac` Wave 1 2x2 | `WA.v8.7.25` | `{5, 10, 20, 30, 40, 80}` (`VHT10..80`, `5 MHz` cabled `PB-030`) | PtP STA / Mixed PtMP AC STA |

### Explicit Channel-Width Schema (`{5, 10, 20, 30, 40, 80}` MHz)
- [`validate_powerbeam_channel_width_mhz`](../controller/powerbeam_m5_and_5ac_bench_harness.py) enforces explicit integer channel widths in `{5, 10, 20, 30, 40, 80}` MHz and never defaults to `40 MHz`.
- Any attempt to configure `80 MHz` on `XW` (`PowerBeam M5 300` `802.11n`) is rejected immediately (`ValueError`).
- For `30 MHz` non-standard `airOS` links (`PBE-M5-PTP-30MHZ`), [`PowerBeamBlockSample.to_gatekeeper_run_metrics`](../controller/powerbeam_m5_and_5ac_bench_harness.py) computes the exact spectral efficiency $\text{goodput\_per\_mhz} = \text{goodput\_mbps} / 30.0$ and bridges it losslessly into [`RegressionGatekeeper`](../analysis/regression_gate/gatekeeper.py).

---

## 2. Six-Experiment Paired `A/B/A/B/A/B` Qualification Battery

Each experiment executes `6` paired blocks (`12` total runs: `[A, B, A, B, A, B]`) evaluated by [`RegressionGatekeeper.evaluate_paired`](../analysis/regression_gate/gatekeeper.py) (`min_blocks_for_keep=4`, `min_blocks_for_promote=6`, `alpha=0.05`, exact $2^6 = 64$ sign-flip permutation test + 2,000-draw paired bootstrap 95% CI):

| Experiment ID | Family | Width (MHz) | Arm A `goodput/MHz` | Arm B `goodput/MHz` | Gain (%) | `p99` Delta (%) | `paired_p` | Gate Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `PBE-M5-PTP-20MHZ` | `XW` | `20` | `3.9317` | `4.4408` | `+12.95%` | `-68.58%` | `0.0312` | `PROMOTE` |
| `PBE-M5-PTP-30MHZ` | `XW` | `30` | `3.6150` | `4.0550` | `+12.17%` | `-68.64%` | `0.0312` | `PROMOTE` |
| `PBE-5AC-PTP-20MHZ` | `WA` | `20` | `5.9233` | `6.7500` | `+13.96%` | `-68.20%` | `0.0312` | `PROMOTE` |
| `PBE-5AC-PTP-40MHZ` | `WA` | `40` | `6.0700` | `6.8733` | `+13.23%` | `-68.67%` | `0.0312` | `PROMOTE` |
| `PBE-5AC-PTP-80MHZ` | `WA` | `80` | `3.9133` | `4.4633` | `+14.05%` | `-69.92%` | `0.0312` | `PROMOTE` |
| `PBE-MIXED-AC-N-PTMP-20MHZ` | `WA+XW` | `20` | `3.4283` | `4.7483` | `+38.50%` | `-74.59%` | `0.0312` | `PROMOTE` |

### Null-Calibration (`A/A` Replay Audit)
- Replaying `200` randomized 6-block `A/A` baseline trials via [`run_aa_null_replay_validation`](../analysis/regression_gate/gatekeeper.py) yields `false_positive_rate = 0.0` (`passes_null_calibration = True`).

---

## 3. Rollback Watchdog & Protected Partition Boundaries

- [`evaluate_rollback_watchdog`](../controller/powerbeam_m5_and_5ac_bench_harness.py) enforces a `<15.0s` automatic rollback to Stock Arm A if any candidate block exhibits:
  - `firmware_resets > 0`
  - `loss_pct > 5.0%`
  - `p99_lat_ms > 80.0 ms`
  - `reassociation_time_s > 20.0 s`
  - Loss of L2 `4addr: on` / `ETH_P_TEB` transparency (`l2_4addr_bridge_alive=False`).
- Protected flash partitions (`u-boot`, `u-boot-env`, `EEPROM`, `ART`) are strictly read-only.
