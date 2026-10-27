# Multi-Wave `/goal` Program: Waves BU, BV, BW, and BX (`R97` through `R102` `9 km` `bidir_2flow` `+7.04%` Goodput Crossover and Complete `bidir_8flow` Distance Curve `3 km, 6 km, 9 km, 12 km, 14 km`)

## 0. Hard Safety & Engineering Rules
1. **100% Offline Execution**: Do NOT SSH into or touch any radio or network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, or production). Work strictly on local repository files.
2. **Never Modify Prior Round Receipts (`R1..R96`)**: All SHA-256 bindings in `waves_a_to_d` through `waves_bq_to_bt` must remain 100% intact.
3. **Carry All Four Waves (`BU -> BV -> BW -> BX`) to Completion Without Stopping**: Execute continuously until `artifacts/autoresearch/waves_bu_to_bx_20261024/final_validation.json` is written and `pytest` passes 100%.

---

## 1. New Physical Receipts to Ingest (`R97` through `R102`)

All 6 rounds are `16`-block counterbalanced `AB/BA` crossovers (`32` 5-second windows per round, `N=160` RTT samples per arm, `0.0000%` packet loss on both arms, `0.0` ULP float and `'0'` `Fraction` block-mean discrepancy, and 4-address WDS `phy0-ap0.sta1` MAC retry telemetry) on `LAP-120` (`OpenWrt 24.10.4`) $\leftrightarrow$ `Loco195` (`OpenWrt 24.10.4`):

- **Round 97 (`FMX-AUTORESEARCH-LIVE-097-BIDIR-2FLOW-COVCLASS20-9000M-BE1800-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r97_bidir_2flow_covclass20_9000m_be1800_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r97_bidir_2flow_covclass20_9000m_be1800_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) at `9000 m` (`9.0 km`, `coverage_class=20, slot_time_us=69, ack_timeout_us=138`) with `AP BE=1800/3600 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 98 (`FMX-AUTORESEARCH-LIVE-098-BIDIR-8FLOW-COVCLASS6-3000M-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r98_bidir_8flow_covclass6_3000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r98_bidir_8flow_covclass6_3000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`) at `3000 m` (`3.0 km`, `coverage_class=6, slot_time_us=27, ack_timeout_us=54`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 99 (`FMX-AUTORESEARCH-LIVE-099-BIDIR-8FLOW-COVCLASS13-6000M-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r99_bidir_8flow_covclass13_6000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r99_bidir_8flow_covclass13_6000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`) at `6000 m` (`6.0 km`, `coverage_class=13, slot_time_us=48, ack_timeout_us=96`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 100 (`FMX-AUTORESEARCH-LIVE-100-BIDIR-8FLOW-COVCLASS20-9000M-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r100_bidir_8flow_covclass20_9000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r100_bidir_8flow_covclass20_9000m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`) at `9000 m` (`9.0 km`, `coverage_class=20, slot_time_us=69, ack_timeout_us=138`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 101 (`FMX-AUTORESEARCH-LIVE-101-BIDIR-8FLOW-COVCLASS27-12KM-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r101_bidir_8flow_covclass27_12km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r101_bidir_8flow_covclass27_12km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`) at `12000 m` (`12.0 km`, `coverage_class=27, slot_time_us=90, ack_timeout_us=180`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 102 (`FMX-AUTORESEARCH-LIVE-102-BIDIR-8FLOW-COVCLASS31-14KM-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r102_bidir_8flow_covclass31_14km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r102_bidir_8flow_covclass31_14km_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`) at `14000 m` (`14.0 km`, `coverage_class=31` exact `ath10k` hardware ceiling, `slot_time_us=102, ack_timeout_us=204`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

---

## 2. Four-Wave Deliverables (`Waves BU, BV, BW, BX`)

### Wave BU — Extend `orchestration/autoresearch/fmx_offline_data.py` Through `R102`
1. Extend `orchestration/autoresearch/fmx_offline_data.py` to ingest `R97..R102` while preserving all historical APIs byte-exact.
2. Add unit tests.

### Wave BV — Statistical Audit of `R97..R102`
1. Audit `R97..R102` using exact two-sided sign-flip randomization ($2^{16} = 65,536$ permutations), Wilcoxon signed-rank, paired Hodges–Lehmann $\hat{\Delta}_{\text{HL}}$, and paired BCa bootstrap (`10,000` resamples, `seed=20261024`).
2. Add unit tests.

### Wave BW — Extend Multi-Regime Selector & Promotion Gate Across `R1..R102`
1. Update `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `orchestration/autoresearch/fmx_structural_promotion_gate.py` to cover the complete `bidir_2flow`, `bidir_4flow`, `bidir_6flow`, `bidir_8flow`, `unidir_dl_2flow`, and `unidir_ul_2flow` matrix across `[100 m .. 14000 m]`.
2. Add unit tests.

### Wave BX — Create `docs/STAGE12_R97_TO_R102_COMPLETE_2FLOW_TO_8FLOW_14KM_MATRIX_AUDIT.md`, Update Master Docs, and Seal `artifacts/autoresearch/waves_bu_to_bx_20261024/final_validation.json`
1. Write `docs/STAGE12_R97_TO_R102_COMPLETE_2FLOW_TO_8FLOW_14KM_MATRIX_AUDIT.md`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
3. Write `artifacts/autoresearch/waves_bu_to_bx_20261024/final_validation.json` with SHA-256 bindings and verify `pytest` passes 100%.
