# Offline Program Specification: Waves AG, AH, AI, and AJ (R43 to R47 Dyadic-Exact Zero-Loss 16-Block AB/BA Audits & Multi-Regime Selector)

## Hard Safety & Scope Rules
- Work **100% offline** in the repository. Do NOT SSH into any radio or network device (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, etc.).
- Do NOT stop, restart, or touch any background daemon or bench process (including the 72h monitor and the live bench runner).
- Preserve all existing tests and modules (`1,826+` repository tests and `832+` autoresearch tests must remain 100% green).

## New Physical Bench Artifacts Available on Disk (`R43` through `R47`)
Five new 16-block counterbalanced `AB/BA` crossover receipts (`32` 5-second windows per round = `160` new windows, `N=160` RTT samples per arm, `80` new matched `AB/BA` blocks) are saved in `artifacts/autoresearch/`:
1. **Round 43 (`FMX-AUTORESEARCH-LIVE-043-UNIDIR-DL-2FLOW-ABBA16-ALL4-EXACT-HOLM500-WDS-N160`)**:
   - File: `artifacts/autoresearch/lap120_loco195_r43_unidir_dl_2flow_abba16_all4_exact_holm500_wds_20261024.json`
   - TSV: `artifacts/autoresearch/lap120_loco195_r43_unidir_dl_2flow_abba16_all4_exact_holm500_wds_results.tsv`
   - Regime: `unidir_dl_2flow` (`iperf3 -P 2`, `active_flow_count=2`, `bidirectional=False`).
   - `Arm A` (`r43_iter0_stock_unidir_dl_2flow_abba16_exact_wds_n160`) vs `Arm B` (`r43_iter1_sym_hybrid_unidir_dl_2flow_abba16_exact_wds_n160`: Symmetric Hybrid `BE=1800/3600`, `af=3, fq_limit=8192, ftx=0, retry=7/4`).
   - Result: `0.0000%` loss on both arms (`160/160`), `['0', '0', '0', '0']` `Fraction` block-mean delta, `108.000000 Mbps` DL (`KEEP`, `fmx_loss=0.455202` vs `0.529035` Stock), lower MAC retry rate (`0.198821%` vs `0.210506%`), `16/16` block wins on `p50_rtt_ms` ($p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$) and `14/16` on `p95_rtt_ms`.
2. **Round 44 (`FMX-AUTORESEARCH-LIVE-044-UNIDIR-DL-2FLOW-SYMAF1-RETRY53-ABBA16-DYADIC-EXACT-WDS-N160`)**:
   - File: `artifacts/autoresearch/lap120_loco195_r44_unidir_dl_2flow_symaf1_retry53_abba16_dyadic_wds_20261024.json`
   - TSV: `artifacts/autoresearch/lap120_loco195_r44_unidir_dl_2flow_symaf1_retry53_abba16_dyadic_wds_results.tsv`
   - Regime: `unidir_dl_2flow` (`iperf3 -P 2`, `active_flow_count=2`, `bidirectional=False`).
   - `Arm A` (`r44_iter0_stock_unidir_dl_2flow_abba16_dyadic_wds_n160`) vs `Arm B` (`r44_iter1_sym_hybrid_af1_fql2048_ftx1_retry53_unidir_dl_2flow_abba16_dyadic_wds_n160`: Symmetric Hybrid `BE=1800/3600 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`).
   - Result: `0.0000%` loss on both arms (`160/160`), **dyadic-exact `[0.0, 0.0, 0.0, 0.0]` IEEE-754 `float` AND `['0', '0', '0', '0']` `Fraction` block-mean deltas (0 ULP error)**, `105.750000 Mbps` DL (`KEEP`, `fmx_loss=0.419131` vs `0.537215` Stock), `16/16` block wins on BOTH `p50_rtt_ms` AND `p95_rtt_ms` ($p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}}$ on both) plus `14/16` on `p99_rtt_ms`.
3. **Round 45 (`FMX-AUTORESEARCH-LIVE-045-BIDIR-6FLOW-RETRY74-ABBA16-DYADIC-EXACT-ZERO-LOSS-WDS-N160`)**:
   - File: `artifacts/autoresearch/lap120_loco195_r45_bidir_6flow_retry74_abba16_dyadic_zero_loss_wds_20261024.json`
   - TSV: `artifacts/autoresearch/lap120_loco195_r45_bidir_6flow_retry74_abba16_dyadic_zero_loss_wds_results.tsv`
   - Regime: `bidir_6flow` (`iperf3 -P 3 --bidir`, `active_flow_count=6`, `bidirectional=True`).
   - `Arm A` (`r45_iter0_stock_bidir_6flow_abba16_dyadic_zero_loss_wds_n160`) vs `Arm B` (`r45_iter1_asym_af1_fql2048_ftx1_retry74_bidir_6flow_abba16_dyadic_zero_loss_wds_n160`: Asymmetric AQL `BE=1100/2200` AP / `BE=2200/4400` CPE + `af=1 + fq_limit=2048 + ftx=1 + retry 7/4`).
   - Result: **`0.0000%` packet loss on BOTH `Arm A` (`160/160`) AND `Arm B` (`160/160`)**, **dyadic-exact `[0.0, 0.0, 0.0, 0.0]` IEEE-754 `float` AND `['0', '0', '0', '0']` `Fraction` block-mean deltas (0 ULP error)**, **lower MAC retry rate on `Arm B` (`0.196166% < 0.206276%` across `543,926` WDS frames)**, and **ALL `16 / 16` blocks won across ALL 5 contrasts (`p50_rtt_ms`, `p95_rtt_ms`, `p99_rtt_ms`, `ul_goodput_mbps`, `bidir_jain_fairness`, $p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$ on all 5)**!
4. **Round 46 (`FMX-AUTORESEARCH-LIVE-046-UNIDIR-UL-2FLOW-SYMAF1-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - File: `artifacts/autoresearch/lap120_loco195_r46_unidir_ul_2flow_abba16_dyadic_zero_loss_wds_20261024.json`
   - TSV: `artifacts/autoresearch/lap120_loco195_r46_unidir_ul_2flow_abba16_dyadic_zero_loss_wds_results.tsv`
   - Regime: `unidir_ul_2flow` (`iperf3 -P 2 -R`, `active_flow_count=2`, `bidirectional=False`).
   - `Arm A` (`r46_iter0_stock_unidir_ul_2flow_abba16_dyadic_zero_loss_wds_n160`) vs `Arm B` (`r46_iter1_sym_hybrid_af1_fql2048_ftx1_retry53_unidir_ul_2flow_abba16_dyadic_zero_loss_wds_n160`).
   - Result: `0.0000%` loss on both arms (`160/160`), **dyadic-exact `[0.0, 0.0, 0.0, 0.0]` IEEE-754 `float` AND `['0', '0', '0', '0']` `Fraction` block-mean deltas**, `KEEP` (`fmx_loss=0.164971` vs `0.290949` Stock, `-43.3%` loss reduction, `p50/p95/p99 = 4.8735 / 8.7682 / 10.9333 ms` vs Stock `5.6450 / 15.1341 / 24.3045 ms`, `15/16` blocks won on `p95` and `p99`).
5. **Round 47 (`FMX-AUTORESEARCH-LIVE-047-BIDIR-8FLOW-AF3-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - File: `artifacts/autoresearch/lap120_loco195_r47_bidir_8flow_af3_abba16_dyadic_zero_loss_wds_20261024.json`
   - TSV: `artifacts/autoresearch/lap120_loco195_r47_bidir_8flow_af3_abba16_dyadic_zero_loss_wds_results.tsv`
   - Regime: `bidir_8flow` (`iperf3 -P 4 --bidir`, `active_flow_count=8`, `bidirectional=True`).
   - `Arm A` (`r47_iter0_stock_bidir_8flow_abba16_dyadic_zero_loss_wds_n160`) vs `Arm B` (`r47_iter1_asym_af3_fql2048_ftx1_retry53_bidir_8flow_abba16_dyadic_zero_loss_wds_n160`: Asymmetric AQL + `af=3 + fq_limit=2048 + ftx=1 + retry 5/3`).
   - Result: **`0.0000%` packet loss on BOTH `Arm A` (`160/160`) AND `Arm B` (`160/160`)**, **dyadic-exact `[0.0, 0.0, 0.0, 0.0]` IEEE-754 `float` AND `['0', '0', '0', '0']` `Fraction` block-mean deltas (0 ULP error)**, **lower MAC retry rate on `Arm B` (`0.177066% < 0.200613%` across `486,824` WDS frames)**, **`+60.7%` UL goodput (`32.568` vs `20.271 Mbps`), `Jain = 0.908081` vs `0.719727`, `p50/p95/p99 = 7.8945 / 22.3271 / 28.8927 ms` vs Stock `11.7820 / 61.0839 / 71.2442 ms` (`-63.4%` `p95`, `-59.4%` `p99`)**, and **ALL `16 / 16` blocks won across ALL 5 contrasts (`p50_rtt_ms`, `p95_rtt_ms`, `p99_rtt_ms`, `ul_goodput_mbps`, `bidir_jain_fairness`, $p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$ on all 5)**!

---

## Wave AG — Extend `orchestration/autoresearch/fmx_offline_data.py` & Tests Through `R47` (`194` Total Records, `262` Matched Blocks)
1. Extend `ROUND_SPECS` in `orchestration/autoresearch/fmx_offline_data.py` to ingest `R43, R44, R45, R46, R47` (`10` new arms -> `194` total records across `R1..R47`, `700` crossed block rows across `262` matched blocks).
2. Add a new dyadic-exact IEEE-754 float AND rational `Fraction` audit helper in `fmx_offline_data.py` (or `fmx_r43_to_r47_dyadic_zero_loss_audit.py`) that verifies whether a record has **both** `Fraction` delta == `'0'` AND `float` delta == `0.0` (`0` ULP error vs `np.mean`) across all 4 block means (`goodput_mbps`, `dl_mbps`, `ul_mbps`, `jain_index`), certifying `R44, R45, R46, R47` as `DYADIC_FLOAT_AND_RATIONAL_EXACT_ZERO_ULP`.
3. Update `tests/test_fmx_offline_data.py` to verify all `194` records (`R1..R47`), `700` crossed rows, `262` matched blocks, and the `0.0` float + `'0'` `Fraction` deltas on `R44, R45, R46, R47`.

## Wave AH — Exact Sign-Flip & Carryover Audit for `R43..R47` (`analysis/statistics/fmx_r43_to_r47_dyadic_zero_loss_audit.py`)
1. Implement `analysis/statistics/fmx_r43_to_r47_dyadic_zero_loss_audit.py` and `tests/test_fmx_r43_to_r47_dyadic_zero_loss_audit.py`:
   - Perform the exact $2^{16} = 65,536$ sign-flip permutation audit and period-adjusted carryover/period-balance audit (`8` `AB` blocks vs `8` `BA` blocks) for `R43, R44, R45, R46, R47`.
   - Prove that in **`R45` (`bidir_6flow`)** and **`R47` (`bidir_8flow`)**, `Arm B` achieves `16/16` block wins across all 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}} = 0.00010$), `0.0%` packet loss on BOTH control and candidate (`160/160` pings each), lower MAC retry rate (`0.196166% < 0.206276%` in `R45`; `0.177066% < 0.200613%` in `R47`), and `0.0` float / `'0'` `Fraction` block-mean discrepancy!
   - Prove that in **`R44` (`unidir_dl_2flow`)**, `Arm B` achieves `16/16` block wins on BOTH `p50_rtt_ms` and `p95_rtt_ms` ($p = 2/65536 = 0.000030517578125 < \alpha_{\text{Holm500}}$) with `0.0%` loss on both arms and `0.0` float / `'0'` `Fraction` discrepancy.
   - Prove that in **`R46` (`unidir_ul_2flow`)**, `Arm B` achieves `-42.1%` lower `p95` and `-55.0%` lower `p99` (`15/16` blocks won on `p95` and `p99`, $p = 34/65536 = 0.0005188$) with `0.0%` loss on both arms, while explicitly recording the UL goodput vs retry trade-off (`58.04` vs `65.28 Mbps`, retry `4.70%` vs `1.56%`) vs `R39` (`sym_hybrid` with `af=3, retry=7/4` which achieved `64.13 Mbps` UL and `0.21%` retry).

## Wave AI — Multi-Regime Dyadic Promotion Gate & Selector (`orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py`)
1. Implement `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `tests/test_fmx_multi_regime_dyadic_selector.py`:
   - Build a deterministic, zero-network offline regime policy selector and structural promotion auditor across `bidir_6flow`, `unidir_dl_2flow`, `unidir_ul_2flow`, `bidir_8flow`, `covclass6_3km`, and `covclass13_6km` using `R27..R47`.
   - Evaluate `R45` and `R47` under both a strict goodput-preservation threshold (`<= 2%` total goodput loss) and a directional QoE/UL-fairness threshold, and compare `R45` and `R47` (`0.0%` control loss, `0.0` ULP dyadic means, lower MAC retry, `16/16` across all 5 contrasts) against `R41` and `R42`.

## Wave AJ — Documentation & Stage 12 Dyadic Audit Report
1. Generate `docs/STAGE12_R43_TO_R47_DYADIC_ZERO_ULP_HOLM500_AUDIT.md` and `artifacts/autoresearch/waves_ag_to_aj_20261024/final_validation.json`.
2. Update `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`, `docs/CURRENT_STATE.md`, `docs/DECISIONS.md`, `docs/RESEARCH_LEDGER.md`, `docs/EXPERIMENTS.md`, and `docs/DOCS-MAP.md`.
3. Run the complete offline pytest suite and verify `0` failures.
