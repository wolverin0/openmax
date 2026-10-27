# Multi-Wave `/goal` Program: Waves BQ, BR, BS, and BT (`R93` through `R96` `14 km` (`coverage_class=31` Hardware Ceiling) `AP BE=1550/3100 + af=1` `bidir_6flow` Crossover and Complete `bidir_2flow` Distance Curve `9 km, 12 km, 14 km`)

## 0. Hard Safety & Engineering Rules
1. **100% Offline Execution**: Do NOT SSH into or touch any radio or network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, or production). Work strictly on local repository files.
2. **Never Modify Prior Round Receipts (`R1..R92`)**: All SHA-256 bindings in `waves_a_to_d` through `waves_bm_to_bp` must remain 100% intact.
3. **Carry All Four Waves (`BQ -> BR -> BS -> BT`) to Completion Without Stopping**: Execute continuously until `artifacts/autoresearch/waves_bq_to_bt_20261024/final_validation.json` is written and `pytest` passes 100%.

---

## 1. New Physical Receipts to Ingest (`R93` through `R96`)

All 4 rounds are `16`-block counterbalanced `AB/BA` crossovers (`32` 5-second windows per round, `N=160` RTT samples per arm, `0.0000%` packet loss on both arms, `0.0` ULP float and `'0'` `Fraction` block-mean discrepancy, and 4-address WDS `phy0-ap0.sta1` MAC retry telemetry) on `LAP-120` (`OpenWrt 24.10.4`) $\leftrightarrow$ `Loco195` (`OpenWrt 24.10.4`):

- **Round 93 (`FMX-AUTORESEARCH-LIVE-093-COVCLASS31-14KM-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r93_covclass31_14km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r93_covclass31_14km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at `14000 m` (`14.0 km`, `coverage_class=31` exact `ath10k` hardware ceiling, `slot_time_us=102, ack_timeout_us=204`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 94 (`FMX-AUTORESEARCH-LIVE-094-BIDIR-2FLOW-COVCLASS20-9000M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r94_bidir_2flow_covclass20_9000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r94_bidir_2flow_covclass20_9000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) at `9000 m` (`9.0 km`, `coverage_class=20, slot_time_us=69, ack_timeout_us=138`).

- **Round 95 (`FMX-AUTORESEARCH-LIVE-095-BIDIR-2FLOW-COVCLASS27-12KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r95_bidir_2flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r95_bidir_2flow_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) at `12000 m` (`12.0 km`, `coverage_class=27, slot_time_us=90, ack_timeout_us=180`).

- **Round 96 (`FMX-AUTORESEARCH-LIVE-096-BIDIR-2FLOW-COVCLASS31-14KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r96_bidir_2flow_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r96_bidir_2flow_covclass31_14km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) at `14000 m` (`14.0 km`, `coverage_class=31` exact `ath10k` hardware ceiling, `slot_time_us=102, ack_timeout_us=204`).

---

## 2. Four-Wave Deliverables (`Waves BQ, BR, BS, BT`)

### Wave BQ — Extend `orchestration/autoresearch/fmx_offline_data.py` Through `R96`
1. Extend `orchestration/autoresearch/fmx_offline_data.py` to ingest `R93..R96` while preserving all historical APIs byte-exact.
2. Add unit tests.

### Wave BR — Statistical Audit of `R93..R96`
1. Audit `R93..R96` using exact two-sided sign-flip randomization ($2^{16} = 65,536$ permutations), Wilcoxon signed-rank, paired Hodges–Lehmann $\hat{\Delta}_{\text{HL}}$, and paired BCa bootstrap (`10,000` resamples, `seed=20261024`).
2. Add unit tests.

### Wave BS — Extend Multi-Regime Selector & Promotion Gate Across `R1..R96`
1. Update `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `orchestration/autoresearch/fmx_structural_promotion_gate.py` to cover the complete `bidir_2flow`, `bidir_4flow`, `bidir_6flow`, `bidir_8flow`, `unidir_dl_2flow`, and `unidir_ul_2flow` matrix across `[100 m .. 14000 m]`.
2. Add unit tests.

### Wave BT — Create `docs/STAGE12_R93_TO_R96_COMPLETE_2FLOW_4FLOW_6FLOW_DISTANCE_MATRIX_AUDIT.md`, Update Master Docs, and Seal `artifacts/autoresearch/waves_bq_to_bt_20261024/final_validation.json`
1. Write `docs/STAGE12_R93_TO_R96_COMPLETE_2FLOW_4FLOW_6FLOW_DISTANCE_MATRIX_AUDIT.md`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
3. Write `artifacts/autoresearch/waves_bq_to_bt_20261024/final_validation.json` with SHA-256 bindings and verify `pytest` passes 100%.
