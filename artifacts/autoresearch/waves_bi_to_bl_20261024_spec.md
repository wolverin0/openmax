# Multi-Wave `/goal` Program: Waves BI, BJ, BK, and BL (`R81` through `R86` Unidirectional Bulk DL/UL Crossovers, Multi-Distance `bidir_4flow` Grid, & `7500 m` Strict `< 2.0%` Goodput-Preserving `16/16` Receipt)

## 0. Hard Safety & Engineering Rules
1. **100% Offline Execution**: Do NOT SSH into or touch any radio or network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, or production). Work strictly on local repository files.
2. **Never Modify Prior Round Receipts (`R1..R80`)**: All SHA-256 bindings in `waves_a_to_d` through `waves_be_to_bh` must remain 100% intact.
3. **Carry All Four Waves (`BI -> BJ -> BK -> BL`) to Completion Without Stopping**: Execute continuously until `artifacts/autoresearch/waves_bi_to_bl_20261024/final_validation.json` is written and `pytest` passes 100%.

---

## 1. New Physical Receipts to Ingest (`R81` through `R86`)

All 6 rounds are `16`-block counterbalanced `AB/BA` crossovers (`32` 5-second windows per round, `N=160` RTT samples per arm, `0.0000%` packet loss on both arms, `0.0` ULP float and `'0'` `Fraction` block-mean discrepancy, and 4-address WDS `phy0-ap0.sta1` MAC retry telemetry) on `LAP-120` (`OpenWrt 24.10.4`) $\leftrightarrow$ `Loco195` (`OpenWrt 24.10.4`):

- **Round 81 (`FMX-AUTORESEARCH-LIVE-081-UNIDIR-DL-2FLOW-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r81_unidir_dl_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r81_unidir_dl_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `unidir_dl_2flow` (`-P 2`, `active_flow_count=2`, `bidirectional=False`) at `100 m` (`coverage_class=0, slot_time_us=9, ack_timeout_us=18`).

- **Round 82 (`FMX-AUTORESEARCH-LIVE-082-UNIDIR-UL-2FLOW-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r82_unidir_ul_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r82_unidir_ul_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `unidir_ul_2flow` (`-P 2 -R`, `active_flow_count=2`, `bidirectional=False`) at `100 m` (`coverage_class=0, slot_time_us=9, ack_timeout_us=18`).

- **Round 83 (`FMX-AUTORESEARCH-LIVE-083-BIDIR-4FLOW-COVCLASS6-3000M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r83_bidir_4flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r83_bidir_4flow_covclass6_3000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`) at `3000 m` (`3.0 km`, `coverage_class=6, slot_time_us=27, ack_timeout_us=54`).

- **Round 84 (`FMX-AUTORESEARCH-LIVE-084-BIDIR-4FLOW-COVCLASS13-6000M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r84_bidir_4flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r84_bidir_4flow_covclass13_6000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`) at `6000 m` (`6.0 km`, `coverage_class=13, slot_time_us=48, ack_timeout_us=96`).

- **Round 85 (`FMX-AUTORESEARCH-LIVE-085-COVCLASS16-7500M-BE1550-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r85_covclass16_7500m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r85_covclass16_7500m_be1550_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at `7500 m` (`7.5 km`, `coverage_class=16, slot_time_us=57, ack_timeout_us=114`) with `AP BE=1550/3100 + CPE BE=2100/4200 + af=1 + retry 6/4`.

- **Round 86 (`FMX-AUTORESEARCH-LIVE-086-BIDIR-4FLOW-COVCLASS20-9000M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r86_bidir_4flow_covclass20_9000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r86_bidir_4flow_covclass20_9000m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`) at `9000 m` (`9.0 km`, `coverage_class=20, slot_time_us=69, ack_timeout_us=138`).

---

## 2. Four-Wave Deliverables (`Waves BI, BJ, BK, BL`)

### Wave BI — Extend `orchestration/autoresearch/fmx_live_dataset.py` Through `R86` (`173` Normalized Rows)
1. Extend `orchestration/autoresearch/fmx_live_dataset.py` to ingest `R81..R86` (`12` new arm rows -> `173` total rows across `R1..R86`).
2. Add unit tests in `tests/test_fmx_live_dataset.py`.

### Wave BJ — Extend `orchestration/autoresearch/fmx_statistical_audit.py` Through `R86`
1. Extend `orchestration/autoresearch/fmx_statistical_audit.py` to audit `R81..R86` using exact two-sided sign-flip randomization ($2^{16} = 65,536$ permutations), Wilcoxon signed-rank, paired Hodges–Lehmann $\hat{\Delta}_{\text{HL}}$, and paired BCa bootstrap (`10,000` resamples, `seed=20261024`).
2. Add unit tests in `tests/test_fmx_statistical_audit.py`.

### Wave BK — Extend `orchestration/autoresearch/fmx_pareto_decomposer.py` & `controller/airmax_aql_autotuner.py` for Unidirectional Bulk (`unidir_dl_2flow`, `unidir_ul_2flow`) & Multi-Distance `bidir_4flow`
1. Update `orchestration/autoresearch/fmx_pareto_decomposer.py` and `controller/airmax_aql_autotuner.py` so the context-aware selector handles both unidirectional (`unidir_dl_2flow`, `unidir_ul_2flow`) and bidirectional (`bidir_2flow, bidir_4flow, bidir_6flow, bidir_8flow`) regimes across the 11-point distance curve (`100 m .. 15 km`).
2. Add unit tests in `tests/test_fmx_pareto_decomposer.py` and `tests/test_airmax_aql_autotuner.py`.

### Wave BL — Create `docs/STAGE12_R81_TO_R86_UNIDIR_AND_MULTIDISTANCE_4FLOW_AUDIT.md`, Update Master Docs, and Seal `artifacts/autoresearch/waves_bi_to_bl_20261024/final_validation.json`
1. Write `docs/STAGE12_R81_TO_R86_UNIDIR_AND_MULTIDISTANCE_4FLOW_AUDIT.md`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
3. Write `artifacts/autoresearch/waves_bi_to_bl_20261024/final_validation.json` with SHA-256 bindings and verify `pytest` passes 100%.
