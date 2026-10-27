# Waves AC, AD, AE, and AF — Ingestion, Exact-Rational Audit & Promotion Evaluation of Frozen `R33..R42`

## Hard Rules
- **100% OFFLINE ONLY**: Never SSH into or touch any live device (`LAP-120`, `Loco195`, `Rocket198`, `10.10.100.*`, `192.168.100.*`, `192.168.200.*`).
- Work exclusively on frozen repository artifacts (`R1..R42`), Python code, unit tests, and documentation.
- Do NOT touch or read `lap120_loco195_r43*` or higher (`R43+` will be running live on the bench while you work offline on frozen `R1..R42`).
- Do NOT stop between waves — execute Waves AC, AD, AE, and AF end-to-end until all tests pass 100%.

## Background: Ten New Frozen Live Physical `autoresearch` Receipts (`R33..R42`)
While Waves Y–AB were running, the physical bench completed Rounds 33 through 42 (`10` new rounds, `32` new iteration arms, `208` new crossed block rows across `80` new matched within-link blocks):
1. `artifacts/autoresearch/lap120_loco195_r33_covclass6_3km_certified_wds_20261024.json` (`4x4` Williams crossover at `3000m` outdoor distance, `coverage_class=6`, slot `27us`, `bidir_6flow`, `4` arms, `16` block rows):
   - `Arm B` (`r33_iter1_asym_r16_covclass6_3km_n40`, `af=3`) won `KEEP` (`fmx_loss = 0.285940` vs `0.954795` Stock), `102.925 Mbps`, `p50/p95/p99 = 6.630 / 14.971 / 26.345 ms` (`4/4` blocks won).
2. `artifacts/autoresearch/lap120_loco195_r34_covclass6_af3_synthesis_certified_wds_20261024.json` (`4x4` Williams crossover at `3000m` outdoor distance, `coverage_class=6`, testing `af=3 + fq_limit=2048 + ftx=1` and `+ retry 5/3`, `4` arms, `16` block rows):
   - `Arm B` (`af=3, fql=8192, ftx=0`) achieved `KEEP` (`fmx_loss = 0.389104`, `103.550 Mbps`), and `Arm D` (`af=3, fql=2048, ftx=1, retry=5/3`) won overall `KEEP` (`fmx_loss = 0.306280`, `p50/p95/p99 = 7.801 / 14.939 / 29.648 ms`).
3. `artifacts/autoresearch/lap120_loco195_r35_covclass13_6km_certified_wds_20261024.json` (`4x4` Williams crossover at `6000m` rural distance, `coverage_class=13`, slot `48us`, `4` arms, `16` block rows):
   - `Arm C` (`r35_iter2_asym_af1_fql2048_ftx1_covclass13_6km_n40`) won overall `KEEP` (`fmx_loss = 0.342483` vs `0.875563` Stock), `94.425 Mbps`, `p50/p95/p99 = 7.323 / 22.495 / 23.444 ms` (`4/4` blocks won).
4. `artifacts/autoresearch/lap120_loco195_r36_12flow_heavy_bidir_certified_wds_20261024.json` (`4x4` Williams crossover under `bidir_12flow`, `-P 6 --bidir`, `4` arms, `16` block rows):
   - Preserved negative/OOM evidence per `AGENTS.md` Section 12.1–12.2: `iperf3 -s` on 64 MB `AR9342` (`Loco195`) was OOM-killed during `Arm A` (`Stock 5000/12000, fq_limit=8192`) after `17,166` frames (`goodput = 0.0`, `CRASH`), while `wpa_supplicant`/`hostapd` (`oom_score_adj=-900`) stayed 100% associated (`40/40` pings at `1.50 ms`).
5. `artifacts/autoresearch/lap120_loco195_r37_8flow_heavy_bidir_certified_wds_20261024.json` (`4x4` Williams crossover under `bidir_8flow`, `-P 4 --bidir`, with per-window `iperf3` OOM guard and **exact `0.0` `Fraction`/float delta across all 4 block means `goodput`, `DL`, `UL`, `Jain`**, `4` arms, `16` block rows):
   - `Arm B` (`r37_iter1_asym_r16_8flow_bidir_n40`, `af=3`) won `KEEP` (`fmx_loss = 0.376922` vs `1.070836` Stock), `107.2000 Mbps`, `p50/p95/p99 = 8.236 / 23.426 / 27.637 ms` (`4/4` blocks won).
6. `artifacts/autoresearch/lap120_loco195_r38_8flow_af3_synthesis_certified_wds_20261024.json` (`4x4` Williams crossover under `bidir_8flow`, `-P 4 --bidir`, with **exact `0.0` `Fraction`/float delta across all 4 block means**, `4` arms, `16` block rows):
   - `Arm B` won `KEEP` (`fmx_loss = 0.502723` vs `0.996033` Stock), while `Arm C` (`af=3, fql=2048, ftx=1`) hit `107.8000 Mbps` (`29.9500 UL`, `Jain = 0.834900`, `p99 = 45.522 ms`).
7. `artifacts/autoresearch/lap120_loco195_r39_unidir_ul_2flow_certified_wds_20261024.json` (`4x4` Williams crossover under `unidir_ul_2flow`, `-P 2 -R`, with **exact `0.0` `Fraction`/float delta across all 4 block means**, `4` arms, `16` block rows):
   - `Arm B` (`r39_iter1_sym_hybrid_unidir_ul_2flow_n40`, Symmetric Hybrid `BE=1800/3600`) won `KEEP` (`fmx_loss = 0.271379` vs `0.497788` Stock), `64.1250 Mbps` UL, `p50/p95/p99 = 4.241 / 7.338 / 10.077 ms` (`4/4` blocks won).
8. `artifacts/autoresearch/lap120_loco195_r40_abba16_all4_exact_holm500_wds_20261024.json` (`16`-block counterbalanced `AB/BA` crossover under `bidir_6flow`, `2` arms, `32` block rows, `N=160` RTT per arm, **exact `0.0` `Fraction`/float delta across all 4 block means**):
   - `Arm B` (`r40_iter1_asym_af1_fql2048_ftx1_abba16_exact_wds_n160`) won `KEEP` (`fmx_loss = 0.390359` vs `0.792498` Stock), `107.618750 Mbps`, `0.0000%` loss (`160/160` vs Stock `159/160`), beating Stock in `16/16` blocks on `p50, p95, UL, Jain` ($p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$) and `15/16` on `p99`.
9. `artifacts/autoresearch/lap120_loco195_r41_abba16_retry53_all4_exact_holm500_wds_20261024.json` (`16`-block counterbalanced `AB/BA` crossover under `bidir_6flow`, `2` arms, `32` block rows, `N=160` RTT per arm):
   - **BOTH `Arm A` (`Stock`) and `Arm B` (`r41_iter1_asym_af1_fql2048_ftx1_retry53_abba16_exact_wds_n160`) have `0.0000%` packet loss (`160/160` pings each), exact `0.0` `Fraction`/float delta across all 4 block means (`goodput_mbps`, `dl_mbps`, `ul_mbps`, `jain_index`), exact numpy quantiles, and `> 579,000` WDS MAC frames (`0.1885%` retry on `Arm B` vs `0.2314%` on `Arm A`)!**
   - **`Arm B` beat `Arm A` in ALL `16 / 16` blocks across ALL 5 contrasts (`p50_rtt_ms`, `p95_rtt_ms`, `p99_rtt_ms`, `ul_goodput_mbps`, and `bidir_jain_fairness` — `100%` unanimity, exact permutation $p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$ on every contrast!)**
10. `artifacts/autoresearch/lap120_loco195_r42_abba16_retry74_all4_exact_zero_loss_holm500_wds_20261024.json` (`16`-block counterbalanced `AB/BA` crossover under `bidir_6flow`, `2` arms, `32` block rows, `N=160` RTT per arm, **exact `0.0` `Fraction`/float delta across all 4 block means**):
    - `Arm B` (`r42_iter1_asym_af1_fql2048_ftx1_retry74_abba16_exact_zero_loss_wds_n160`) achieved `107.287500 Mbps`, `0.0000%` loss (`160/160` vs Stock `159/160`), and also beat `Arm A` in **ALL `16 / 16` blocks across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$)**!

## Required Deliverables Across Waves AC, AD, AE, and AF

### Wave AC — Corpus Ingestion & Exact-Rational Verification (`R1..R42`)
1. Update `orchestration/autoresearch/fmx_offline_data.py` so `load_normalized_records()` ingests `R33..R42` (`182` total records across `R1..R42`) and `load_crossed_block_records()` extracts all block rows from `R16..R42` (`540` crossed block rows across `186` matched within-link blocks!).
2. Verify and assert in `tests/test_fmx_offline_data.py` that:
   - All `18` arms in `R37, R38, R39, R40, R41, and R42` satisfy **exact `0.0` `Fraction` and float equality** across all 4 block means (`goodput_mbps`, `dl_mbps`, `ul_mbps`, and `jain_index`), chronological `raw_rtts_ms`, and `mac_tx_packets_delta > 0`.
   - `R36` (`bidir_12flow` OOM crash under Stock) is preserved accurately with its failure/crash metadata intact.
   - In `R41`, both `Arm A` and `Arm B` satisfy `packet_loss_pct == 0.0` (`160/160` pings), exact `0.0` `Fraction` equality on all 4 block means, exact numpy quantile equality, and `mac_tx_packets_delta > 0`.

### Wave AD — Statistical Audit of `R33..R42` (`analysis/statistics/fmx_r33_to_r42_exact_holm500_audit.py`)
1. Implement `analysis/statistics/fmx_r33_to_r42_exact_holm500_audit.py` and `tests/test_fmx_r33_to_r42_exact_holm500_audit.py`:
   - Audit all contrasts in `R33, R34, R35, R36, R37, R38, R39, R40, R41, and R42` using exact Wilcoxon signed-rank and exact binomial sign tests, Hodges-Lehmann location shifts, and exact Walsh confidence intervals under `Holm10`, `Holm324`, and `Holm500`.
   - Specifically verify:
     - `R40` (`16/16` blocks won on `p50, p95, UL, Jain`, `15/16` on `p99`),
     - `R41` (`16/16` blocks won on **ALL 5 contrasts** `p50, p95, p99, UL, Jain`, $p = 0.000030517578125 < \alpha_{\text{Holm500}}$, `0.0%` loss on both arms, `0.0` `Fraction` delta on all 4 block means),
     - `R42` (`16/16` blocks won on **ALL 5 contrasts** `p50, p95, p99, UL, Jain`, $p = 0.000030517578125 < \alpha_{\text{Holm500}}$ at `107.2875 Mbps`),
     - Pooled `bidir_6flow` at `100m` across `R27 + R28 + R29 + R32 + R40 + R41 + R42` (`94` matched within-link blocks!).

### Wave AE — Regime-Adaptive Controller & Exact-Gate Evaluation (`controller/optimizer/wmm_regime_policy.py`)
1. Update `controller/optimizer/wmm_regime_policy.py` and `tests/test_wmm_regime_policy.py` to incorporate the `R33..R42` evidence:
   - Evaluate `R41` (which satisfies `0.0` `Fraction` discrepancy on all 4 block means, `0.0%` packet loss on both arms, `> 579k` WDS MAC frames with lower retry rate than Stock, and `16/16` block wins across all 5 contrasts under `Holm500`) and `R42` (`107.2875 Mbps`, `16/16` block wins across all 5 contrasts under `Holm500`) against the promotion gates, while preserving all scientific/control-boundary caveats (`within_link_repetitions_not_independent_sector_trials`, etc.).
   - Add regime mappings for `covclass6_3km` (`R33, R34`), `covclass13_6km` (`R35`), `bidir_8flow` (`R37, R38`), and `unidir_ul_2flow` (`R39`).

### Wave AF — Engineering Report, Master Index Sync & Full Offline Regression Suite
1. Write `docs/STAGE12_R33_TO_R42_EXACT_RATIONAL_16OF16_HOLM500_AUDIT.md` and `artifacts/autoresearch/waves_ac_to_af_20261024/final_validation.json`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/RESEARCH_LEDGER.md`, `docs/DECISIONS.md`, and `docs/DOCS-MAP.md`.
3. Run the full offline pytest suite and verify `0` failures.
