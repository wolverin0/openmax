# Multi-Wave Offline Autoresearch Specification: Waves BY, BZ, CA, CB (`R103..R107` Complete 7-Point `unidir_dl_2flow` Distance Sweep `100m..14km`)

**Mode**: 100% OFFLINE REPOSITORY EXECUTION ONLY.
**Hard Safety Rule**: Do NOT SSH into, ping, flash, or interact with any network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, or production). Do NOT modify any historical `R1..R107` JSON/TSV receipt files under `artifacts/autoresearch/`.

## New Certified Physical Receipts Available (`R103..R107` — `16`-Block Counterbalanced `AB/BA` Dyadic-Exact Zero-Loss Crossovers, `32` Windows per Round, `N=160` RTT per Arm, `0.0000%` Loss on BOTH Arms, and `0.0` ULP Float + `'0'` `Fraction` Block-Mean Discrepancy)

1. **Round 103 (`FMX-AUTORESEARCH-LIVE-103-UNIDIR-DL-2FLOW-COVCLASS6-3000M-BE1900-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - Receipt: `artifacts/autoresearch/lap120_loco195_r103_unidir_dl_2flow_covclass6_3000m_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - Regime: `unidir_dl_2flow` (`-P 2`, `3000 m` / `3.0 km`, `coverage_class=6`, `slot_time_us=27`, `ack_timeout_us=54`)
   - Result: `Arm B` (`AP BE=1900/3800 + CPE BE=2100/4200 + af=1 + retry 6/4`) won **`KEEP` (`fmx_loss = 0.283717` vs `0.589785` Stock, `-51.9%`)**, preserving **`99.7435%` of Stock pure-DL goodput (`82.012695` vs `82.223633 Mbps` = `-0.256541% < 0.3%`)**, strictly lower MAC retry rate (`0.442500% < 0.606147%`), and **`16/16` block wins on `p50 (5.6735 vs 20.0435 ms)`, `p95 (14.2124 vs 33.0657 ms)`, and `p99 (17.3329 vs 37.1037 ms)`**.

2. **Round 104 (`FMX-AUTORESEARCH-LIVE-104-UNIDIR-DL-2FLOW-COVCLASS13-6000M-BE1900-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - Receipt: `artifacts/autoresearch/lap120_loco195_r104_unidir_dl_2flow_covclass13_6000m_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - Regime: `unidir_dl_2flow` (`-P 2`, `6000 m` / `6.0 km`, `coverage_class=13`, `slot_time_us=48`, `ack_timeout_us=96`)
   - Result: `Arm B` won **`KEEP` (`fmx_loss = 0.306452` vs `0.778712` Stock, `-60.6%`)**, achieving **HIGHER pure-DL goodput than Stock (`+0.756467%`: `61.914062` vs `61.449219 Mbps`)**, strictly lower MAC retry rate (`0.637920% < 0.644714%`), and **`16/16` block wins on `p50 (4.9315 vs 22.9250 ms)`, `p95 (10.6352 vs 39.8551 ms)`, and `p99 (14.0510 vs 43.5881 ms)`**.

3. **Round 105 (`FMX-AUTORESEARCH-LIVE-105-UNIDIR-DL-2FLOW-COVCLASS20-9000M-BE1900-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - Receipt: `artifacts/autoresearch/lap120_loco195_r105_unidir_dl_2flow_covclass20_9000m_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - Regime: `unidir_dl_2flow` (`-P 2`, `9000 m` / `9.0 km`, `coverage_class=20`, `slot_time_us=69`, `ack_timeout_us=138`)
   - Result: `Arm B` won **`KEEP` (`fmx_loss = 0.265431` vs `0.697145` Stock, `-61.9%`)**, achieving **HIGHER pure-DL goodput than Stock (`+1.377255%`: `59.806641` vs `58.994141 Mbps`)**, strictly lower MAC retry rate (`0.511242% < 0.533059%`), and **`16/16` block wins on `p50 (4.3220 vs 20.0225 ms)`, `p95 (9.3142 vs 35.4075 ms)`, and `p99 (12.9573 vs 40.5163 ms)`**.

4. **Round 106 (`FMX-AUTORESEARCH-LIVE-106-UNIDIR-DL-2FLOW-COVCLASS27-12KM-BE1900-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - Receipt: `artifacts/autoresearch/lap120_loco195_r106_unidir_dl_2flow_covclass27_12km_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - Regime: `unidir_dl_2flow` (`-P 2`, `12000 m` / `12.0 km`, `coverage_class=27`, `slot_time_us=90`, `ack_timeout_us=180`)
   - Result: `Arm B` won **`KEEP` (`fmx_loss = 0.240704` vs `0.731004` Stock, `-67.1%`)**, preserving **`99.0188%` of Stock pure-DL goodput (`57.256836` vs `57.824219 Mbps` = `-0.981217% < 1.0%`)**, strictly lower MAC retry rate (`0.507104% < 0.562451%`), and **`16/16` block wins on `p50 (3.9275 vs 21.4345 ms)`, `p95 (9.3215 vs 38.1248 ms)`, and `p99 (12.5401 vs 46.9421 ms)`**.

5. **Round 107 (`FMX-AUTORESEARCH-LIVE-107-UNIDIR-DL-2FLOW-COVCLASS31-14KM-BE1900-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - Receipt: `artifacts/autoresearch/lap120_loco195_r107_unidir_dl_2flow_covclass31_14km_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - Regime: `unidir_dl_2flow` (`-P 2`, `14000 m` / `14.0 km`, `coverage_class=31`, `slot_time_us=102`, `ack_timeout_us=204`)
   - Result: `Arm B` won **`KEEP` (`fmx_loss = 0.233203` vs `0.701938` Stock, `-66.8%`)**, preserving **`98.2556%` of Stock pure-DL goodput (`54.014648` vs `54.973633 Mbps` = `-1.744444% < 2.0%`)**, strictly lower MAC retry rate (`0.610569% < 0.620507%`), and **`16/16` block wins on `p50 (3.6750 vs 21.1820 ms)`, `p95 (9.0590 vs 38.6196 ms = 4.26x lower)`, and `p99 (11.8829 vs 41.9857 ms = 3.53x lower)`**.

## Required Deliverables Across Waves BY–CB

1. **Wave BY — Extend `fmx_offline_data.py` & `fmx_dyadic_crossover_verifier.py` through `R1..R107`**:
   - Add SHA-256 bindings and schema normalization for `R103..R107`.
   - Verify exact dyadic `Fraction` block means (`0` discrepancy) and `16/16` paired block contrasts across `R103..R107`.
   - Add `tests/test_autoresearch_wave_by_r103_to_r107_ingest.py`.

2. **Wave BZ — Complete 7-Point `unidir_dl_2flow` Distance Surface (`100m, 1km, 3km, 6km, 9km, 12km, 14km`: `R81, R83, R103, R104, R105, R106, R107`)**:
   - Extend `orchestration/autoresearch/fmx_distance_slot_surface.py` and `fmx_multi_regime_dyadic_selector.py` so `unidir_dl_2flow` is certified across all 7 primary distance knots (`100m..14000m`, `coverage_class = 0, 2, 6, 13, 20, 27, 31`) with strictly `< 2.0%` goodput delta (including higher goodput than Stock at `6 km` and `9 km` and strictly lower MAC retry rate at every distance!).
   - Add `tests/test_autoresearch_wave_bz_unidir_dl_2flow_7point_surface.py`.

3. **Wave CA — Update Promotion Gate, Pareto Decomposer, and Advisory Facade (`R1..R107`)**:
   - Update `fmx_structural_promotion_gate.py`, `fmx_pareto_decomposer.py`, and `controller/airmax_aql_autotuner.py` through `R107`.
   - Add `tests/test_autoresearch_wave_ca_r107_facade.py`.

4. **Wave CB — End-to-End Validation Bundle & Stage 12 Audit Report (`R103..R107`)**:
   - Generate `artifacts/autoresearch/waves_by_to_cb_20261024/final_validation.json` and `docs/STAGE12_R103_TO_R107_UNIDIR_DL_2FLOW_14KM_DISTANCE_SURFACE_AUDIT.md`.
   - Synchronize `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
   - Run the complete offline autoresearch pytest suite and ensure `0` failures.
