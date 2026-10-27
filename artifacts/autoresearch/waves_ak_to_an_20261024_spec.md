# Continuous Multi-Wave Autoresearch & Statistical Engineering Spec — Waves AK, AL, AM, AN (`2026-10-24`)

## Context & Strict Rules
- **Role**: Offline Research, Statistical Verification, & Controller Engineering Lane (`Codex`).
- **Safety Rule**: Work **100% offline** in the repository. Do NOT SSH into any radio (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, etc.), because the live bench lane is actively running physical `autoresearch` Round 57+ on `LAP-120` <-> `Loco195`.
- **Execution Mode**: Execute **Waves AK, AL, AM, and AN** end-to-end without stopping between waves until every deliverable, unit test, ledger entry, and master index entry is complete and `pytest -q` passes 100%.

---

## New Live Physical Bench Evidence to Ingest (`Rounds 48, 49, 50, 51, 52, 53, 54, 55, and 56` — 16-Block `AB/BA` Dyadic-Exact Zero-Loss Crossovers, `32` Windows per Round, `N=160` RTT per Arm, `0.0000%` Loss on BOTH Arms, and `0.0` ULP Float + `'0'` `Fraction` Block-Mean Discrepancy)

Nine new live physical rounds were completed on `LAP-120` (`OpenWrt 24.10.4`, `4-addr WDS AP`) <-> `Loco195` (`OpenWrt 24.10.4`, `4-addr WDS STA`), specifically designed to:
1. Extend `16`-block `AB/BA` dyadic-exact zero-loss (`0.0000%` loss on BOTH arms, `0.0` ULP block-mean discrepancy) qualification to **`3000 m` (`coverage_class=6`, slot `27 µs`)** and **`6000 m` (`coverage_class=13`, slot `48 µs`)** outdoor PtMP distances (`R48, R49, R52, R53`), and
2. Solve the goodput-preservation trade-off (`R45/R47` lost `6.43%` / `11.54%` total goodput under `BE=1100/2200`) by introducing the **High-Goodput Asymmetric AQL profile (`AP BE=1500/3000 µs`, `thresh=6000 µs`, `TSQ=200/100 KB` + `CPE BE=2100/4200 µs`, `thresh=8400 µs`, `TSQ=320/160 KB`)** across `R50, R51, R52, R53, R55, R56`:

1. **Round 48 (`FMX-AUTORESEARCH-LIVE-048-COVCLASS6-3KM-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r48_covclass6_3km_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r48_covclass6_3km_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) at **`3000 m` outdoor distance (`coverage_class=6`, slot `27 µs`, ACK/CTS `54 µs`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Arm A (`r48_iter0_stock_covclass6_3km_abba16_dyadic_zero_loss_wds_n160`)**:
     - `fmx_loss = 0.916850`, `total_bidir_goodput_mbps = 104.072265625` (`DL = 82.8935546875`, `UL = 21.1787109375`), `Jain = 0.728515625`, `p50/p95/p99 = 17.5085 / 53.78855 / 67.37005 ms`, `packet_loss_pct = 0.0%` (`160/160`), `mac_retry_rate = 0.2231560264178691%` (`1,226 / 549,391`).
   - **Arm B (`r48_iter1_asym_af3_fql2048_ftx1_retry53_covclass6_3km_abba16_dyadic_zero_loss_wds_n160` — `BE=1100/2200 + af=3 + fq_limit=2048 + ftx=1 + retry 5/3`)**:
     - **Decision**: **`KEEP` (`fmx_loss = 0.382895` vs `0.916850`, `-58.2%`)**
     - `total_bidir_goodput_mbps = 90.3056640625` (`DL = 56.4453125`, `UL = 33.8603515625`, `+59.9%` UL), `Jain = 0.843505859375`, `p50/p95/p99 = 6.2875 / 21.2222 / 28.54467 ms`, `packet_loss_pct = 0.0%` (`160/160`), **lower MAC retry rate (`0.21130999928195555% < 0.2231560264178691%`)**, `0.0` ULP delta, and **`16 / 16` block wins across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, exact two-sided sign test $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$)**.

2. **Round 49 (`FMX-AUTORESEARCH-LIVE-049-COVCLASS13-6KM-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r49_covclass13_6km_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r49_covclass13_6km_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) at **`6000 m` rural distance (`coverage_class=13`, slot `48 µs`, ACK/CTS `96 µs`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Arm A (`r49_iter0_stock_covclass13_6km_abba16_dyadic_zero_loss_wds_n160`)**:
     - `fmx_loss = 0.941921`, `total_bidir_goodput_mbps = 94.158203125` (`DL = 74.6611328125`, `UL = 19.4970703125`), `Jain = 0.73321533203125`, `p50/p95/p99 = 17.5085 / 55.4526 / 67.37005 ms`, `packet_loss_pct = 0.0%` (`160/160`), `mac_retry_rate = 0.1958635061634139%` (`977 / 498,817`).
   - **Arm B (`r49_iter1_asym_af1_fql2048_ftx1_retry53_covclass13_6km_abba16_dyadic_zero_loss_wds_n160` — `BE=1100/2200 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`)**:
     - **Decision**: **`KEEP` (`fmx_loss = 0.297347` vs `0.941921`, `-68.4%`)**
     - `total_bidir_goodput_mbps = 81.8125` (`DL = 49.3544921875`, `UL = 32.4580078125`, `+66.5%` UL), `Jain = 0.8602294921875`, `p50/p95/p99 = 5.9700 / 13.6770 / 22.1146 ms`, `packet_loss_pct = 0.0%` (`160/160`), **lower MAC retry rate (`0.18869308828452074% < 0.1958635061634139%`)**, `0.0` ULP delta, and **`16 / 16` block wins across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, exact two-sided sign test $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$)**.

3. **Round 50 (`FMX-AUTORESEARCH-LIVE-050-BIDIR-6FLOW-BE1500-2100-RETRY74-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r50_bidir_6flow_be1500_2100_retry74_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r50_bidir_6flow_be1500_2100_retry74_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) under `bidir_6flow` (`-P 3 --bidir`, `100 m`, `covclass=0`) testing **High-Goodput Asymmetric AQL (`AP BE=1500/3000 + CPE BE=2100/4200 + af=1 + fq_limit=2048 + ftx=1 + retry 7/4`)**.
   - **Arm A (`r50_iter0_stock_bidir_6flow_abba16_dyadic_zero_loss_wds_n160`)**:
     - `fmx_loss = 0.787512`, `total_bidir_goodput_mbps = 109.046875` (`DL = 91.7978515625`, `UL = 17.2490234375`), `Jain = 0.6815185546875`, `p50/p95/p99 = 17.1695 / 44.30375 / 60.53495 ms`, `packet_loss_pct = 0.0%` (`160/160`), `mac_retry_rate = 0.193001%`.
   - **Arm B (`r50_iter1_asym_be1500_2100_af1_fql2048_ftx1_retry74_bidir_6flow_abba16_dyadic_zero_loss_wds_n160`)**:
     - **Decision**: **`KEEP` (`fmx_loss = 0.412961` vs `0.787512`, `-47.6%`)**
     - **`total_bidir_goodput_mbps = 107.6826171875` vs `109.046875` Stock (`-1.2502%` total goodput delta — well inside the `< 2.0%` strict goodput-preservation threshold!)**, `DL = 81.7021484375`, `UL = 25.98046875` (`+50.6%` UL), `Jain = 0.788330078125`, `p50/p95/p99 = 7.7650 / 24.4283 / 31.66522 ms`, `packet_loss_pct = 0.0%` (`160/160`), `0.0` ULP delta, and **`16 / 16` block wins across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, exact two-sided sign test $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$)**.

4. **Round 51 (`FMX-AUTORESEARCH-LIVE-051-BIDIR-6FLOW-BE1500-2100-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r51_bidir_6flow_be1500_2100_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r51_bidir_6flow_be1500_2100_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover (`bidir_6flow`, `100 m`, `BE=1500/2100 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`).
   - **Result**: **`KEEP` (`fmx_loss = 0.440758` vs `0.754213` Stock)**, `102.6669921875 Mbps` (`UL = 26.8662109375`, `+48.8%` UL, `Jain = 0.8065185546875`), **lower MAC retry rate (`0.200649% < 0.212317%`)**, `0.0%` loss on both arms (`160/160`), `0.0` ULP delta, `16/16` block wins on `p50, UL, Jain` ($p = 0.00003052 < \alpha_{\text{Holm500}}$) and `15/16` on `p95`.

5. **Round 52 (`FMX-AUTORESEARCH-LIVE-052-COVCLASS6-3KM-BE1500-2100-AF3-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r52_covclass6_3km_be1500_2100_af3_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r52_covclass6_3km_be1500_2100_af3_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **`3000 m` (`coverage_class=6`)** with `BE=1500/2100 + af=3 + fq_limit=2048 + ftx=1 + retry 5/3`.
   - **Result**: **`KEEP` (`fmx_loss = 0.385599` vs `0.737239` Stock)**, lifting `3000 m` total goodput from `90.31 Mbps` (`R48`) to **`97.826171875 Mbps` (`-5.35%` vs `103.3564453125 Mbps` Stock)**, `UL = 27.6005859375 Mbps` (`+50.1%` UL), `Jain = 0.789794921875`, `p50/p95/p99 = 6.9935 / 19.86935 / 32.02267 ms`, `0.0%` loss on both arms (`160/160`), `0.0` ULP delta, and **`16/16` block wins on `p50, p95, UL, Jain` ($p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p99`.

6. **Round 53 (`FMX-AUTORESEARCH-LIVE-053-COVCLASS13-6KM-BE1500-2100-AF1-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r53_covclass13_6km_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r53_covclass13_6km_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **`6000 m` (`coverage_class=13`)** with `BE=1500/2100 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`.
   - **Result**: **`KEEP` (`fmx_loss = 0.325549` vs `0.846235` Stock, `-61.5%`)**, lifting `6000 m` total goodput from `81.81 Mbps` (`R49`) to **`89.90625 Mbps` (`-5.32%` vs `94.9599609375 Mbps` Stock)**, `UL = 27.6240234375 Mbps` (`+50.1%` UL), `Jain = 0.80950927734375`, `p50/p95/p99 = 6.6475 / 16.7597 / 29.96776 ms`, **lower MAC retry rate (`0.200630% < 0.206809%`)**, `0.0%` loss on both arms (`160/160`), `0.0` ULP delta, and **`16 / 16` block wins across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$)**.

7. **Round 54 (`FMX-AUTORESEARCH-LIVE-054-BIDIR-2FLOW-SYMAF1-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r54_bidir_2flow_symaf1_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r54_bidir_2flow_symaf1_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) with `sym_hybrid` (`BE=1800/3600 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`).
   - **Result**: **`KEEP` (`fmx_loss = 0.284898` vs `0.355048` Stock)**, `103.513671875 Mbps`, **lower MAC retry rate (`0.176489% < 0.198436%`)**, `0.0%` loss on both arms (`160/160`), `0.0` ULP delta, `16/16` block wins on `p50` (`7.0905` vs `11.4530 ms`, $p = 0.00003052 < \alpha_{\text{Holm500}}$) and `15/16` on `p95, Jain`.

8. **Round 55 (`FMX-AUTORESEARCH-LIVE-055-BIDIR-4FLOW-BE1500-2100-AF1-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r55_bidir_4flow_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r55_bidir_4flow_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`) with `BE=1500/2100 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`.
   - **Result**: **`KEEP` (`fmx_loss = 0.388350` vs `0.583682` Stock)**, `104.1044921875 Mbps` (`UL = 22.8427734375`, `+42.6%` UL, `Jain = 0.7618408203125`), `p50/p95/p99 = 8.4140 / 22.41935 / 26.86983 ms`, `0.0%` loss on both arms (`160/160`), `0.0` ULP delta, `16/16` block wins on `p50, UL, Jain` ($p = 0.00003052 < \alpha_{\text{Holm500}}$) and `15/16` on `p95, p99`.

9. **Round 56 (`FMX-AUTORESEARCH-LIVE-056-BIDIR-2FLOW-BE1500-2100-AF1-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r56_bidir_2flow_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r56_bidir_2flow_be1500_2100_af1_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`) with `BE=1500/2100 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`.
   - **Result**: **`KEEP` (`fmx_loss = 0.236885` vs `0.339393` Stock, `-30.2%`)**, `102.98828125 Mbps` (`UL = 14.013671875`, `+20.2%` UL, `Jain = 0.65374755859375`), `p50/p95/p99 = 5.9715 / 13.9067 / 18.73555 ms` vs Stock `10.5010 / 20.3092 / 24.87032 ms`, `0.0%` loss on both arms (`160/160`), `0.0` ULP delta, and **`16/16` block wins on `p50, p95, Jain` ($p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p99` and `14/16` on `UL`.

---

## Wave AK — Dataset, Multi-Factor Model, Surrogate, & Evidence Bundle Expansion (`R1..R56` = `212` Records, `988` Crossed Rows Across `406` Matched Blocks)
1. Update `orchestration/autoresearch/fmx_live_dataset.py` to ingest **`R48, R49, R50, R51, R52, R53, R54, R55, and R56`** (`18` new records: `16`-block `AB/BA` dyadic-exact zero-loss rounds, expanding the canonical dataset from `194` to **`212` records across `56` live physical rounds `R1..R56`**).
2. Update `analysis/statistics/fmx_crossed_mixed_effects.py` so the block-level crossed mixed-effects dataset includes all `32` windows (`16` matched blocks) from each of `R48..R56`, expanding the block-level table from `700` to **`988` crossed rows across `406` matched blocks**.
3. Update `orchestration/autoresearch/fmx_surrogate_optimizer.py` and `orchestration/autoresearch/fmx_evidence_bundle.py` (plus tests `tests/test_fmx_live_dataset.py`, `tests/test_fmx_crossed_mixed_effects.py`, `tests/test_fmx_surrogate_optimizer.py`, `tests/test_fmx_evidence_bundle.py`) to reflect the `212`-record / `56`-round corpus and the new `AP BE=1500/3000 + CPE BE=2100/4200` High-Goodput Asymmetric AQL family.

## Wave AL — Distance- & Goodput-Preserving Dyadic Zero-Loss Audit (`R48..R56`)
1. Create `analysis/statistics/fmx_r48_to_r56_distance_goodput_dyadic_audit.py` and `tests/test_fmx_r48_to_r56_distance_goodput_dyadic_audit.py`:
   - Perform an exact rational (`fractions.Fraction`) and IEEE-754 float audit across `R48, R49, R50, R51, R52, R53, R54, R55, R56`:
     - Verify `0.0` ULP float discrepancy and `'0'` `Fraction` discrepancy on all 4 block-mean metrics (`dl_goodput_mbps`, `ul_goodput_mbps`, `total_bidir_goodput_mbps`, `bidir_jain_fairness`) across all `18` arms (`288` block windows).
     - Verify `0.0%` packet loss (`160/160` pings received) on BOTH Arm A and Arm B across all `9` rounds (`2,880 / 2,880` total ICMP samples with `0` drops!).
     - Audit the `16 / 16` block-win rounds across all 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$): **`R48` (`3000 m`), `R49` (`6000 m`), `R50` (`bidir_6flow`, `BE=1500/2100 + retry 7/4`), and `R53` (`6000 m`, `BE=1500/2100 + retry 5/3`)**, plus the `16/16` latency/fairness block-win profiles in `R51, R52, R54, R55, R56`.
     - Quantify the exact Pareto trade-off between **Directional Latency/UL Dominance (`BE=1100/2200`: `R45, R48, R49`)** and **High-Goodput Asymmetric AQL (`BE=1500/2100`: `R50, R51, R52, R53, R55, R56`)**, explicitly proving that **`R50` (`107.682617 Mbps` vs `109.046875 Mbps` Stock, `-1.2502%` total goodput delta)** passes the strict `< 2.0%` goodput-preservation threshold while winning `16/16` blocks across all 5 contrasts!
2. Write the comprehensive engineering report `docs/STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT.md`.

## Wave AM — Pareto-Mode & Distance-Aware Dyadic Policy Selector Update (`fmx_multi_regime_dyadic_selector.py`)
1. Extend `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `tests/test_fmx_multi_regime_dyadic_selector.py`:
   - Upgrade the selector to support both:
     - **Distance classes**: `100 m` (`covclass=0`), `3000 m` (`covclass=6`), and `6000 m` (`covclass=13`), and
     - **Operator Pareto Objective Mode**:
       - `strict_goodput_preservation` (`max_total_goodput_drop_pct <= 2.0%`): selects **`R50` (`BE=1500/2100 + af=1 + retry 7/4`, `-1.2502%` goodput delta, `16/16` across all 5 contrasts)** for `bidir_6flow` at `100 m`, and exposes the `BE=1500/2100` Pareto frontier (`R52` at `3000 m`, `R53` at `6000 m`, `R55` at `bidir_4flow`, `R56` at `bidir_2flow`).
       - `directional_latency_ul_dominance` (`max_total_goodput_drop_pct <= 15.0%` with `+40%..+80%` UL gain and `16/16` block wins): selects `R45` (`bidir_6flow`), `R47` (`bidir_8flow`), `R48` (`3000 m`), `R49` (`6000 m`), `R50/R51/R52/R53/R55/R56` as appropriate.
   - Update `orchestration/autoresearch/fmx_structural_promotion_gate.py` and `tests/test_fmx_structural_promotion_gate.py` so `R50` is verified as passing **BOTH** the strict `< 2.0%` total goodput-preservation gate (`-1.2502%`) AND `16/16` block wins across all 5 contrasts ($p = 0.00003052 < \alpha_{\text{Holm500}}$) with `0.0%` loss and `0.0` ULP discrepancy.

## Wave AN — Synchronization of Master Index, Ledgers, Docs Map, and Full Test Suite
1. Update:
   - `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`
   - `docs/CURRENT_STATE.md`
   - `docs/RESEARCH_LEDGER.md`
   - `docs/EXPERIMENTS.md`
   - `docs/DECISIONS.md`
   - `docs/DOCS-MAP.md`
2. Run the full repository test suite (`pytest -q`) and write a machine-verifiable validation receipt to `artifacts/autoresearch/waves_ak_to_an_20261024/final_validation.json`.
