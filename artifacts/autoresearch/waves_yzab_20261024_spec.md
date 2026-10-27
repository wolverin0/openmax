# Waves Y, Z, AA, and AB — Certified WDS MAC & Exact Block-Mean Crossover Audit (`R27..R32`)

## Hard Rules
- **100% OFFLINE ONLY**: Never SSH into or touch any live device (`LAP-120`, `Loco195`, `Rocket198`, `10.10.100.*`, `192.168.100.*`).
- Work exclusively on frozen repository artifacts (`R1..R32`), Python code, unit tests, and documentation.
- Do NOT stop between waves — execute Waves Y, Z, AA, and AB end-to-end until all tests pass 100%.

## Background: Six New Certified Live Physical `autoresearch` Receipts (`R27..R32`)
The live bench has completed Rounds 27, 28, 29, 30, 31, and 32 on `LAP-120` <-> `Loco195` (`OpenWrt 24.10.4`, `5180 MHz`, `VHT20`, `wds=1`), specifically engineered to resolve EVERY audit and promotion gate identified in `STAGE12_LOWER_MAC_HOOKS_AND_12BLOCK_CROSSOVER_AUDIT.md`:
1. `artifacts/autoresearch/lap120_loco195_r27_certified_wds_crossover_20261024.json` (`4x4` Williams crossover, `16` windows, `N=40` RTT per arm, `bidir_6flow`):
   - `reported == np.mean(blocks)` (`0.000 Mbps` discrepancy), chronological `raw_rtts_ms`, and real 4-addr WDS `phy0-ap0.sta1` MAC counters (`135,727..152,188` frames per arm).
   - `Arm C` (`r27_iter2_asym_af1_fql2048_ftx1_n40`) won `KEEP` (`fmx_loss = 0.358817` vs `0.625432` Stock), `105.250 Mbps` (`79.825 DL / 25.425 UL`), `0.222%` MAC retry rate, `p50/p95/p99 = 7.136 / 19.635 / 30.636 ms`.
2. `artifacts/autoresearch/lap120_loco195_r28_abba12_certified_wds_20261024.json` (`12`-block counterbalanced Williams crossover, `36` windows, `N=120` RTT per arm, `407k..486k` WDS MAC frames per arm, `bidir_6flow`):
   - Both `Arm B` (`r28_iter1_asym_af1_fql2048_ftx1_abba12_wds_n120`, `KEEP`, `fmx_loss = 0.302751`, `105.175 Mbps`, `p50/p95/p99 = 6.867 / 16.655 / 26.266 ms`) and `Arm C` (`r28_iter2_asym_af1_fql2048_ftx1_retry53_abba12_wds_n120`, `fmx_loss = 0.363827`, `99.908 Mbps`, `p50/p95/p99 = 6.727 / 17.878 / 33.903 ms`) beat Stock (`Arm A: r28_iter0_stock_wmm_baseline_abba12_wds_n120`, `104.242 Mbps`, `p50/p95/p99 = 17.855 / 44.362 / 73.112 ms`) in **all `12 / 12` blocks across all 10 contrasts (`p50, p95, p99, UL, Jain`, `100%` unanimity, exact Wilcoxon signed-rank and sign-test $p = 2/4096 = 0.00048828125$)**.
3. `artifacts/autoresearch/lap120_loco195_r29_abba14_holm324_wds_20261024.json` (`14`-block counterbalanced `AB/BA` crossover, `28` windows, `N=140` RTT per arm, `522k..573k` WDS MAC frames per arm, exact `7/7` period balance):
   - Designed to break the `12`-block discrete permutation floor ($2/4096 = 0.000488 > \alpha_{\text{Holm324}} = 0.0001543$).
   - `Arm B` (`r29_iter1_asym_af1_fql2048_ftx1_abba14_wds_n140`, `KEEP`, `fmx_loss = 0.440893`) beat Stock (`Arm A`, `fmx_loss = 2.094274`) in **`14 / 14` blocks on `p50`, `p95`, `UL`, and `Jain` ($p = 2/2^{14} = 2/16384 = 0.0001220703125 < \alpha_{\text{Holm324}} = 0.0001543$)** and `13 / 14` blocks on `p99` ($p_{rank} = 0.00024414$), while eliminating packet loss (`140/140` pings vs Stock `134/140`).
4. `artifacts/autoresearch/lap120_loco195_r30_2flow_bidir_certified_wds_20261024.json` (`4x4` Williams crossover under `bidir_2flow` (`-P 1 --bidir`), `16` windows, `N=40` RTT per arm):
   - `Arm C` (`r30_iter2_asym_af1_fql2048_ftx1_2flow_bidir_n40`) won `KEEP` (`fmx_loss = 0.248607` vs `0.580620` Stock), `105.100 Mbps` (`77.975 DL / 27.125 UL`, `Jain = 0.810`), `163,346` WDS MAC frames (`0.171%` retry), `p50/p95/p99 = 7.021 / 16.088 / 16.971 ms` (`4/4` blocks won).
5. `artifacts/autoresearch/lap120_loco195_r31_unidir_dl_2flow_certified_wds_20261024.json` (`4x4` Williams crossover under `unidir_dl_2flow` (`-P 2`), `16` windows, `N=40` RTT per arm):
   - Confirms regime-adaptive policy selection: under `unidir_dl_2flow`, Symmetric Hybrid (`Arm B: r31_iter1_sym_hybrid_unidir_dl_2flow_n40`, `BE=1800/3600`) won `KEEP` (`fmx_loss = 0.320723` vs `0.436603` Stock), achieving **`108.250 Mbps` (`5.41 bits/s/Hz`)**, `163,115` WDS MAC frames (`0.181%` retry), and `p50/p95/p99 = 8.424 / 21.273 / 23.314 ms` (`4/4` blocks won vs Stock).
6. `artifacts/autoresearch/lap120_loco195_r32_abba16_holm500_wds_20261024.json` (`16`-block counterbalanced `AB/BA` crossover, `32` windows, `N=160` RTT per arm, `593k..653k` WDS MAC frames per arm, exact `8/8` period balance):
   - **Zero packet loss (`160/160` pings on both Stock and Treatment)** so every single block RTT quantile uses full `10/10` ping samples without loss attrition!
   - `Arm B` (`r32_iter1_asym_af1_fql2048_ftx1_abba16_wds_n160`, `KEEP`, `fmx_loss = 0.405706`) beat Stock (`Arm A`, `fmx_loss = 0.883754`) in **`16 / 16` blocks on `p50`, `UL` (`+58.4%`), and `Jain` ($p = 2/2^{16} = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$)** and **`15 / 16` blocks on `p95` and `p99`** ($p_{rank} \le 0.00009155$).

## Required Deliverables Across Waves Y, Z, AA, and AB

### Wave Y — Corpus Ingestion & Certified WDS Schema Verification (`R1..R32`)
1. Update `orchestration/autoresearch/fmx_offline_data.py` so `load_normalized_records()` ingests `R27, R28, R29, R30, R31, and R32` (`151` total records across `R1..R32`) and `load_crossed_block_records()` extracts all block rows from `R16..R32` (`328` crossed block rows across `108` matched within-link blocks!).
2. Verify and assert in `tests/test_fmx_offline_data.py` that for all `20` arms in `R27..R32`:
   - `block_mean_consistent == True` (`abs(reported - np.mean(blocks)) == 0.0` for `goodput_mbps`, `dl_mbps`, `ul_mbps`, and `jain_index`),
   - `raw_rtts_matches_blocks == True` (`list(raw_rtts_ms) == [v for b in blocks for v in b['rtts_ms']]`), and
   - `mac_tx_packets_delta > 0` (no `zero_MAC_denominator` flags anywhere in `R27..R32`).

### Wave Z — Certified Statistical Audit of `R27..R32` (`Holm10`, `Holm324`, `Holm500`, and Pooled `R28+R29+R32` `N=42` Matched Blocks)
1. Implement `analysis/statistics/fmx_r27_to_r32_certified_wds_audit.py` and `tests/test_fmx_r27_to_r32_certified_wds_audit.py`:
   - Audit `R27` (`4x4`), `R28` (`12`-block `N=120`), `R29` (`14`-block `N=140`), `R30` (`bidir_2flow` `4x4`), `R31` (`unidir_dl_2flow` `4x4`), and `R32` (`16`-block `N=160` with `0%` loss on both arms).
   - Compute exact paired Wilcoxon signed-rank and sign-test p-values, Hodges-Lehmann estimators, exact finite Walsh 95% and 99.9% confidence intervals, and multiplicity adjustments under `Holm10` (round-local), `Holm324` (`324`-knob catalog), and `Holm500` (`500`-hypothesis family) for:
     a) `R28` (`12/12` blocks won across all 10 contrasts, $p = 0.00048828$),
     b) `R29` (`14/14` blocks won on `p50, p95, UL, Jain`, $p = 0.00012207 < \alpha_{\text{Holm324}}$),
     c) `R32` (`16/16` blocks won on `p50, UL, Jain`, $p = 0.00003052 < \alpha_{\text{Holm500}}$, `15/16` on `p95/p99`, `0%` loss on both arms), and
     d) **Pooled Certified `bidir_6flow` Crossover (`R27 + R28 + R29 + R32`, `N = 4 + 12 + 14 + 16 = 46` matched within-block pairs comparing `asym_af1_fql2048_ftx1` vs `stock_wmm_baseline`)**, reporting exact paired sign/Wilcoxon p-values across `46` blocks ($p \sim 10^{-13}$!).

### Wave AA — Regime-Adaptive Controller Promotion (`PROMOTED_CERTIFIED_CANARY`)
1. Update `controller/optimizer/wmm_regime_policy.py` and `orchestration/autoresearch/fmx_Structural_Promotion_Gate`:
   - Now that `R27, R28, R29, R30, R31, and R32` satisfy:
     - `block_mean_consistent == True`,
     - `raw_rtts_matches_blocks == True`,
     - `mac_tx_packets_delta > 0` (`phy0-ap0.sta1` WDS MAC denominator),
     - `Holm324` and `Holm500` multiplicity survival ($p = 0.00012207$ in `R29`, $p = 0.00003052$ in `R32`, and $p < 10^{-12}$ pooled across `N=46` blocks), and
     - Regime validation across `bidir_6flow` (`R27, R28, R29, R32`), `bidir_2flow` (`R30`), and `unidir_dl_2flow` (`R31`),
   - Promote the regime-adaptive policy selector in `controller/optimizer/wmm_regime_policy.py`:
     - Under `bidir_6flow` and `bidir_2flow`: promote `asym_airtime_tx_fq2048_ftx1` (`AP BE=3600/2/3/7, CPE BE=1800/3/5/7, airtime_flags=1, fq_limit=2048, force_tx_status=1`) to `PROMOTED_CERTIFIED_CANARY` (with optional ultra-tight tail profile `retry 5/3` from `R28 Arm C`).
     - Under `unidir_dl_2flow`: promote `sym_hybrid_txop1800_q3600` (`BE=1800/2/3/7, quantum=3600`) to `PROMOTED_CERTIFIED_CANARY` based on `R31 Arm B` (`108.250 Mbps`, `4/4` blocks won).
2. Add comprehensive unit tests in `tests/test_wmm_regime_policy.py`.

### Wave AB — Comprehensive Engineering Report & Master Index Synchronization
1. Write `docs/STAGE12_CERTIFIED_WDS_HOLM500_AND_REGIME_PROMOTION_AUDIT.md` and `artifacts/autoresearch/waves_yzab_20261024/final_validation.json`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/RESEARCH_LEDGER.md`, `docs/DECISIONS.md`, and `docs/DOCS-MAP.md` to reflect `R1..R32` (`151` normalized records, `328` crossed block rows across `108` matched blocks) and the `Holm324`/`Holm500` promotion.
3. Run the entire pytest suite and verify `0` failures.
