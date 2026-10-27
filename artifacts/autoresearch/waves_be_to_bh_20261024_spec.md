# Multi-Wave `/goal` Program: Waves BE, BF, BG, and BH (`R76` through `R80` Complete 11-Point `100 m .. 15 km` Distance Curve & Strict `< 2.0%` Goodput-Preserving `16/16` Selector)

## 0. Hard Safety & Engineering Rules
1. **100% Offline Execution**: Do NOT SSH into or touch any radio or network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, or production). Work strictly on local repository files.
2. **Never Modify Prior Round Receipts (`R1..R75`)**: All SHA-256 bindings in `waves_a_to_d` through `waves_ba_to_bd` must remain 100% intact.
3. **Carry All Four Waves (`BE -> BF -> BG -> BH`) to Completion Without Stopping**: Execute continuously until `artifacts/autoresearch/waves_be_to_bh_20261024/final_validation.json` is written and `pytest` passes 100%.

---

## 1. New Physical Receipts to Ingest (`R76` through `R80`)

All 5 rounds are `16`-block counterbalanced `AB/BA` crossovers (`32` 5-second windows per round, `N=160` RTT samples per arm, `0.0000%` packet loss on both arms, `0.0` ULP float and `'0'` `Fraction` block-mean discrepancy, and 4-address WDS `phy0-ap0.sta1` MAC retry telemetry) on `LAP-120` (`OpenWrt 24.10.4`) $\leftrightarrow$ `Loco195` (`OpenWrt 24.10.4`):

- **Round 76 (`FMX-AUTORESEARCH-LIVE-076-COVCLASS3-1500M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r76_covclass3_1500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r76_covclass3_1500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at **`1500 m` (`1.5 km`, `coverage_class=3, slot_time_us=18, ack_timeout_us=36`)**.
  - Arms: `Arm A` (`Stock OpenWrt 24.10.4` at `covclass=3`) vs `Arm B` (`AP BE=1520/3040 codel=8/40ms + CPE BE=2100/4200 codel=10/50ms + RC=24% + af=1 + fq_limit=2048 + ftx=1 + retry 6/4`).
  - Result: **`KEEP` (`fmx_loss = 0.386001` vs `0.754236` Stock, `-48.8%`)**, passing `< 2.0%` strict goodput preservation (`107.405273` vs `108.916016 Mbps`, `-1.387071%` delta), **strictly lower MAC retry rate (`0.179643% < 0.188018%`)**, AND **`16/16` across ALL 5 contrasts (`p50=6.8415 ms`, `p95=21.7318 ms`, `p99=31.5208 ms`, `UL=+50.8%`, `Jain=0.77062988`)**!

- **Round 77 (`FMX-AUTORESEARCH-LIVE-077-COVCLASS16-7500M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r77_covclass16_7500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r77_covclass16_7500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at **`7500 m` (`7.5 km`, `coverage_class=16, slot_time_us=57, ack_timeout_us=114`)**.
  - Arms: `Arm A` (`Stock OpenWrt 24.10.4` at `covclass=16`) vs `Arm B` (`AP BE=1520/3040 codel=8/40ms + CPE BE=2100/4200 codel=10/50ms + RC=24% + af=1 + fq_limit=2048 + ftx=1 + retry 6/4`).
  - Result: **`KEEP` (`fmx_loss = 0.362316` vs `0.924380` Stock, `-60.8%`)**, `16/16` on `p50, p95, p99`, `15/16` on `UL (+41.4%)` and `Jain (0.79644775)`, `-2.0248%` goodput delta due to a single Block 14 RF spike (addressed by Round 80 `BE=1540/2100 + af=3 + retry 6/4` at `7500 m`).

- **Round 78 (`FMX-AUTORESEARCH-LIVE-078-COVCLASS23-10500M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r78_covclass23_10500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r78_covclass23_10500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at **`10500 m` (`10.5 km`, `coverage_class=23, slot_time_us=78, ack_timeout_us=156`)**.
  - Arms: `Arm A` (`Stock OpenWrt 24.10.4` at `covclass=23`) vs `Arm B` (`AP BE=1520/3040 codel=8/40ms + CPE BE=2100/4200 codel=10/50ms + RC=24% + af=1 + fq_limit=2048 + ftx=1 + retry 6/4`).
  - Result: **`KEEP` (`fmx_loss = 0.281530` vs `0.835910` Stock, `-66.3%`)**, preserving **`99.1673%` of Stock goodput (`84.433594` vs `85.142578 Mbps` = `-0.832702%` delta, `6/16` total-goodput wins!)** AND **`16/16` block wins across ALL 5 contrasts (`p50=5.7650 ms`, `p95=15.7771 ms`, `p99=23.7261 ms`, `UL=+44.8%`, `Jain=0.80072021`)**!

- **Round 79 (`FMX-AUTORESEARCH-LIVE-079-COVCLASS30-13500M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r79_covclass30_13500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r79_covclass30_13500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at **`13500 m` (`13.5 km`, `coverage_class=30, slot_time_us=99, ack_timeout_us=198`)**.
  - Arms: `Arm A` (`Stock OpenWrt 24.10.4` at `covclass=30`) vs `Arm B` (`AP BE=1520/3040 codel=8/40ms + CPE BE=2100/4200 codel=10/50ms + RC=24% + af=1 + fq_limit=2048 + ftx=1 + retry 6/4`).
  - Result: **`KEEP` (`fmx_loss = 0.236443` vs `0.897392` Stock, `-73.6%`)**, achieving **`+0.790648%` HIGHER total goodput than Stock (`74.943359` vs `74.355469 Mbps`, `7/16` total-goodput wins!)**, **strictly lower MAC retry rate (`0.321434% < 0.439473%`, `-26.9%`)**, `16/16` on `p50 (5.1585 ms), UL (+58.7%), Jain (0.76855469)`, and `15/16` on `p95 (14.2464 ms)` and `p99 (18.9780 ms)`.

- **Round 80 (`FMX-AUTORESEARCH-LIVE-080-COVCLASS16-7500M-BE1540-2100-CODEL8-RC24-AF3-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
  - File: `artifacts/autoresearch/lap120_loco195_r80_covclass16_7500m_be1540_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
  - Runner: `tools/bench/run_live_autoresearch_r80_covclass16_7500m_be1540_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
  - Regime & Distance: `bidir_6flow` (`-P 3 --bidir`, `active_flow_count=6`) at **`7500 m` (`7.5 km`, `coverage_class=16, slot_time_us=57, ack_timeout_us=114`)**.
  - Arms: `Arm A` (`Stock OpenWrt 24.10.4` at `covclass=16`) vs `Arm B` (`AP BE=1540/3080 codel=8/40ms + CPE BE=2100/4200 codel=10/50ms + RC=24% + af=3 + fq_limit=2048 + ftx=1 + retry 6/4`).
  - Result: **`KEEP` vs Stock (`fmx_loss = 0.351923` vs `0.776391` Stock, `-54.7%`)**, `16/16` on `p50 (6.0665 ms), p95 (18.3825 ms), p99 (27.8459 ms)`, `15/16` on `UL (+35.1%, 15.325195 vs 11.344727 Mbps)` and `Jain (0.70526123 vs 0.64044189)`, and `86.743164` vs `90.556641 Mbps` (`-4.211%`), proving that at `>= 6000 m` (`slot_time_us >= 48 us`) `af=1` (`R77`: `89.922852 Mbps`, `UL=22.309570 Mbps`, `Jain=0.79644775`) strictly dominates `af=3` (`R80`: `86.743164 Mbps`) by `+3.18 Mbps` total goodput and `+6.98 Mbps` UL goodput because `AIRTIME_RX_ENABLED` (`bit 1`) double-charges long-slot RX frames!

---

## 2. Four-Wave Deliverables (`Waves BE, BF, BG, BH`)

### Wave BE — Extend `orchestration/autoresearch/fmx_live_dataset.py` Through `R80` (`161` Normalized Rows)
1. Extend `orchestration/autoresearch/fmx_live_dataset.py` to ingest `R76..R80` (`10` new arm rows -> `161` total rows across `R1..R80`).
2. Verify provenance (`coverage_class` commands in `R76..R80` runner scripts: `3, 16, 23, 30, 16`), exact dyadic `Fraction` / `0.0` ULP block-mean equality, `0.0000%` packet loss (`160/160`), and `phy0-ap0.sta1` WDS MAC retry deltas.
3. Add unit tests in `tests/test_fmx_live_dataset.py`.

### Wave BF — Extend `orchestration/autoresearch/fmx_statistical_audit.py` Through `R80`
1. Extend `orchestration/autoresearch/fmx_statistical_audit.py` to audit `R76..R80` using exact two-sided sign-flip randomization ($2^{16} = 65,536$ permutations), Wilcoxon signed-rank, paired Hodges–Lehmann $\hat{\Delta}_{\text{HL}}$, and paired BCa bootstrap (`10,000` resamples, `seed=20261024`) across all 5 contrasts (`p50, p95, p99, UL, Jain`) plus total bidirectional goodput and WDS MAC retry rate.
2. Add unit tests in `tests/test_fmx_statistical_audit.py`.

### Wave BG — Extend `orchestration/autoresearch/fmx_pareto_decomposer.py` & `controller/airmax_aql_autotuner.py` for the Complete 11-Point Distance Curve (`100 m .. 15 km` at `1.5 km` Steps)
1. Update `orchestration/autoresearch/fmx_pareto_decomposer.py` and `controller/airmax_aql_autotuner.py` so the distance-aware selector covers all **11 verified outdoor distances** (`100 m` cov=0, `1500 m` cov=3, `3000 m` cov=6, `4500 m` cov=10, `6000 m` cov=13, `7500 m` cov=16, `9000 m` cov=20, `10500 m` cov=23, `12000 m` cov=27, `13500 m` cov=30, `15000 m` cov=33) across `bidir_2flow, bidir_4flow, bidir_6flow, bidir_8flow`.
2. Add unit tests in `tests/test_fmx_pareto_decomposer.py` and `tests/test_airmax_aql_autotuner.py`.

### Wave BH — Create `docs/STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md`, Update Master Docs, and Seal `artifacts/autoresearch/waves_be_to_bh_20261024/final_validation.json`
1. Write `docs/STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
3. Write `artifacts/autoresearch/waves_be_to_bh_20261024/final_validation.json` with SHA-256 bindings and verify `pytest` passes 100%.
