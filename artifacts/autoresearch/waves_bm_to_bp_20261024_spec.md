# Multi-Wave `/goal` Program: Waves BM, BN, BO, and BP (`R87` through `R92` Pure-DL `< 2.0%` Goodput-Preserving Crossover, `12 km` & `14 km` (`coverage_class=31` Hardware Ceiling) `bidir_4flow`/`bidir_6flow`, and Multi-Distance `bidir_2flow` Grid)

## 0. Hard Safety & Engineering Rules
1. **100% Offline Execution**: Do NOT SSH into or touch any radio or network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, or production). Work strictly on local repository files.
2. **Never Modify Prior Round Receipts (`R1..R86`)**: All SHA-256 bindings in `waves_a_to_d` through `waves_bi_to_bl` must remain 100% intact.
3. **Carry All Four Waves (`BM -> BN -> BO -> BP`) to Completion Without Stopping**: Execute continuously until `artifacts/autoresearch/waves_bm_to_bp_20261024/final_validation.json` is written and `pytest` passes 100%.

---

## 1. New Physical Receipts to Ingest (`R87` through `R92`)

All 6 rounds are `16`-block counterbalanced `AB/BA` crossovers (`32` 5-second windows per round, `N=160` RTT samples per arm, `0.0000%` packet loss on both arms, `0.0` ULP float and `'0'` `Fraction` block-mean discrepancy, and 4-address WDS `phy0-ap0.sta1` MAC retry telemetry) on `LAP-120` (`OpenWrt 24.10.4`) $\leftrightarrow$ `Loco195` (`OpenWrt 24.10.4`):

- **Round 87 (`FMX-AUTORESEARCH-LIVE-087-UNIDIR-DL-2FLOW-BE1900-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r87_unidir_dl_2flow_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r87_unidir_dl_2flow_be1900_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `unidir_dl_2flow` (`-P 2`, `active_flow_count=2`, `bidirectional=False`) at `100 m` (`coverage_class=0, slot_time_us=9, ack_timeout_us=18`) with `AP BE=1900/3800 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 88 (`FMX-AUTORESEARCH-LIVE-088-BIDIR-4FLOW-COVCLASS27-12KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r88_bidir_4flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r88_bidir_4flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`) at `12000 m` (`12.0 km`, `coverage_class=27, slot_time_us=90, ack_timeout_us=180`).

- **Round 89 (`FMX-AUTORESEARCH-LIVE-089-BIDIR-4FLOW-COVCLASS31-14KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r89_bidir_4flow_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r89_bidir_4flow_covclass33_15km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`) at `14000 m` (`14.0 km`, `coverage_class=31` — exact `ath10k` hardware ceiling `[0, 31]`, `slot_time_us=102, ack_timeout_us=204`).

- **Round 90 (`FMX-AUTORESEARCH-LIVE-090-COVCLASS31-14KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r90_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r90_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at `14000 m` (`14.0 km`, `coverage_class=31` — exact `ath10k` hardware ceiling `[0, 31]`, `slot_time_us=102, ack_timeout_us=204`).

- **Round 91 (`FMX-AUTORESEARCH-LIVE-091-BIDIR-2FLOW-COVCLASS6-3000M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r91_bidir_2flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r91_bidir_2flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) at `3000 m` (`3.0 km`, `coverage_class=6, slot_time_us=27, ack_timeout_us=54`).

- **Round 92 (`FMX-AUTORESEARCH-LIVE-092-BIDIR-2FLOW-COVCLASS13-6000M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r92_bidir_2flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r92_bidir_2flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) at `6000 m` (`6.0 km`, `coverage_class=13, slot_time_us=48, ack_timeout_us=96`).

---

## 2. Four-Wave Deliverables (`Waves BM, BN, BO, BP`)

### Wave BM — Extend `orchestration/autoresearch/fmx_live_dataset.py` Through `R92` (`185` Normalized Rows)
1. Extend `orchestration/autoresearch/fmx_live_dataset.py` to ingest `R87..R92` (`12` new arm rows -> `185` total rows across `R1..R92`).
2. Add unit tests in `tests/test_fmx_live_dataset.py`.

### Wave BN — Extend `orchestration/autoresearch/fmx_statistical_audit.py` Through `R92`
1. Extend `orchestration/autoresearch/fmx_statistical_audit.py` to audit `R87..R92` using exact two-sided sign-flip randomization ($2^{16} = 65,536$ permutations), Wilcoxon signed-rank, paired Hodges–Lehmann $\hat{\Delta}_{\text{HL}}$, and paired BCa bootstrap (`10,000` resamples, `seed=20261024`).
2. Add unit tests in `tests/test_fmx_statistical_audit.py`.

### Wave BO — Extend `orchestration/autoresearch/fmx_pareto_decomposer.py` & `controller/airmax_aql_autotuner.py` Across the Complete `(distance_m, active_flow_count, direction)` Matrix
1. Update `orchestration/autoresearch/fmx_pareto_decomposer.py` and `controller/airmax_aql_autotuner.py` so the context-aware selector incorporates the exact `ath10k` hardware ceiling `coverage_class = 31` (`14000 m`, `slot=102 us, ack=204 us`), the pure-DL goodput-preserving profile (`R87`, `AP BE=1900/3800`), and the multi-distance `bidir_2flow` and `bidir_4flow` grids.
2. Add unit tests in `tests/test_fmx_pareto_decomposer.py` and `tests/test_airmax_aql_autotuner.py`.

### Wave BP — Create `docs/STAGE12_R87_TO_R92_COVCLASS31_CEILING_AND_FULL_MATRIX_AUDIT.md`, Update Master Docs, and Seal `artifacts/autoresearch/waves_bm_to_bp_20261024/final_validation.json`
1. Write `docs/STAGE12_R87_TO_R92_COVCLASS31_CEILING_AND_FULL_MATRIX_AUDIT.md`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
3. Write `artifacts/autoresearch/waves_bm_to_bp_20261024/final_validation.json` with SHA-256 bindings and verify `pytest` passes 100%.
