# Continuous Multi-Wave Autoresearch & Statistical Engineering Spec — Waves AS, AT, AU, AV (`2026-10-24`)

## Context & Strict Rules
- **Role**: Offline Research, Statistical Verification, & Controller Engineering Lane (`Codex`).
- **Safety Rule**: Work **100% offline** in the repository. Do NOT SSH into any radio (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, etc.), because the live bench lane is actively running physical `autoresearch` Round 66+ on `LAP-120` <-> `Loco195`.
- **Execution Mode**: Execute **Waves AS, AT, AU, and AV** end-to-end without stopping between waves until every deliverable, unit test, ledger entry, and master index entry is complete and `pytest -q` passes 100%.

---

## New Live Physical Bench Evidence to Ingest (`Rounds 61, 62, 63, 64, and 65` — 16-Block `AB/BA` Dyadic-Exact Zero-Loss Crossovers, `32` Windows per Round, `N=160` RTT per Arm, `0.0000%` Loss on BOTH Arms, and `0.0` ULP Float + `'0'` `Fraction` Block-Mean Discrepancy)

Five new live physical rounds (`R61, R62, R63, R64, R65`) were completed on `LAP-120` (`OpenWrt 24.10.4`, `4-addr WDS AP`) <-> `Loco195` (`OpenWrt 24.10.4`, `4-addr WDS STA`) to extend the **`AP BE=1520/3040 (codel=8/40ms) + CPE BE=2100/4200 (codel=10/50ms) + long_retry_limit=4`** breakthrough (`< 2.0%` strict goodput-preservation threshold + `16/16` block wins across all 5 contrasts) to **`3000 m` (`covclass=6`), `6000 m` (`covclass=13`), `bidir_8flow`, `bidir_4flow`, and `retry 5/4`**:

1. **Round 61 (`FMX-AUTORESEARCH-LIVE-061-COVCLASS6-3KM-BE1520-2100-CODEL8-RC24-AF3-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r61_covclass6_3km_be1520_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r61_covclass6_3km_be1520_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) at **`3000 m` outdoor distance (`coverage_class=6, slot_time_us=27, ack_timeout_us=54`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Result**: **`KEEP` (`fmx_loss = 0.322344` vs `0.752240` Stock, `-57.1%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold at `3000 m`: `103.2314453125 Mbps` vs `104.548828125 Mbps` Stock (`-1.260065%` total goodput delta, preserving `98.7399%` of Stock goodput vs `-5.35%` in `R52`!)**,
     - **`UL = 26.4560546875 Mbps` vs `17.806640625 Mbps` Stock (`+48.6%` UL), `Jain = 0.8077392578125`**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 6.9425` vs `27.7365 ms`, `p95 = 17.7264` vs `46.2777 ms`, `p99 = 27.8940` vs `51.0350 ms`, `UL`, `Jain`, exact two-sided sign test $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$)**, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

2. **Round 62 (`FMX-AUTORESEARCH-LIVE-062-COVCLASS13-6KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r62_covclass13_6km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r62_covclass13_6km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) at **`6000 m` rural distance (`coverage_class=13, slot_time_us=48, ack_timeout_us=96`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Result**: **`KEEP` (`fmx_loss = 0.262533` vs `0.806695` Stock, `-67.5%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold at `6000 m`: `94.294921875 Mbps` vs `95.08203125 Mbps` Stock (`-0.827821%` total goodput delta — under `< 1.0%`, preserving `99.1722%` of Stock goodput vs `-5.32%` in `R53`!)**,
     - **`UL = 24.6181640625 Mbps` vs `16.1630859375 Mbps` Stock (`+52.3%` UL), `Jain = 0.81353759765625`**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 6.2745` vs `27.2965 ms`, `p95 = 14.2683` vs `47.3927 ms`, `p99 = 23.7384` vs `58.2518 ms`, `UL`, `Jain`, $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}}$)**, `5/16` blocks won on total goodput, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

3. **Round 63 (`FMX-AUTORESEARCH-LIVE-063-BIDIR-8FLOW-BE1520-2100-CODEL8-RC24-AF3-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r63_bidir_8flow_be1520_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r63_bidir_8flow_be1520_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under heavy **`bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`, `distance_m=100, coverage_class=0, slot_time_us=9, ack_timeout_us=18`)**.
   - **Result**: **`KEEP` (`fmx_loss = 0.440726` vs `0.912218` Stock, `-51.7%`)**:
     - **Achieves POSITIVE total goodput gain over Stock (`105.02734375 Mbps` vs `104.9736328125 Mbps` Stock = `+0.051166%` gain, winning `9 / 16` matched blocks on total goodput!)**,
     - **`UL = 28.779296875 Mbps` vs `20.1171875 Mbps` Stock (`+43.1%` UL), `Jain = 0.82989501953125`**,
     - **Wins `16 / 16` blocks on `p95` (`26.1690` vs `54.3759 ms`), `p99` (`33.7415` vs `64.4340 ms`), `UL`, and `Jain` ($p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p50` (`7.1230` vs `12.0400 ms`), `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

4. **Round 64 (`FMX-AUTORESEARCH-LIVE-064-BIDIR-4FLOW-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r64_bidir_4flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r64_bidir_4flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under **`bidir_4flow` (`-P 2 --bidir`, `active_flow_count=4`, `distance_m=100, coverage_class=0, slot_time_us=9, ack_timeout_us=18`)**.
   - **Result**: **`KEEP` (`fmx_loss = 0.319706` vs `0.675974` Stock, `-52.7%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold (`105.8955078125 Mbps` vs `106.5322265625 Mbps` Stock = `-0.597677%` total goodput delta, preserving `99.4023%` of Stock goodput!)**,
     - **`UL = 20.701171875 Mbps` vs `12.90625 Mbps` Stock (`+60.4%` UL), `Jain = 0.7294921875`**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 7.6600` vs `19.5050 ms`, `p95 = 19.9715` vs `37.3292 ms`, `p99 = 23.0616` vs `52.7258 ms`, `UL`, `Jain`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `5/16` blocks won on total goodput, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

5. **Round 65 (`FMX-AUTORESEARCH-LIVE-065-BIDIR-6FLOW-BE1520-2100-CODEL8-RC22-RETRY54-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r65_bidir_6flow_be1520_2100_codel8_rc22_retry54_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r65_bidir_6flow_be1520_2100_codel8_rc22_retry54_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_6flow` (`-P 3 --bidir`, `distance_m=100, coverage_class=0, slot_time_us=9, ack_timeout_us=18`) testing `retry 5/4` (`short_retry=5, long_retry=4`) + `rc_per_thresh=22%`.
   - **Result**: **`KEEP` (`fmx_loss = 0.345877` vs `0.747727` Stock, `-53.7%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold (`104.05078125 Mbps` vs `105.2451171875 Mbps` Stock = `-1.134814%` delta, winning `7/16` blocks on total goodput)**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 7.3315` vs `24.3945 ms`, `p95 = 19.2464` vs `45.4724 ms`, `p99 = 29.0071` vs `51.4304 ms`, `UL = 23.988281` vs `15.976562 Mbps` `+50.1%`, `Jain = 0.77465820` vs `0.67358398`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

---

## Wave AS — Dataset, Multi-Factor Model, Surrogate, & Evidence Bundle Expansion (`R1..R65` = `230` Records, `1,276` Crossed Rows Across `550` Matched Blocks)
1. Update `orchestration/autoresearch/fmx_live_dataset.py` to ingest **`R61, R62, R63, R64, and R65`** (`10` new records: `16`-block `AB/BA` dyadic-exact zero-loss rounds with explicit `distance_m, coverage_class, slot_time_us, ack_timeout_us`, expanding the canonical dataset from `220` to **`230` records across `65` live physical rounds `R1..R65`**).
2. Update `analysis/statistics/fmx_crossed_mixed_effects.py` so the block-level crossed mixed-effects dataset includes all `32` windows (`16` matched blocks) from each of `R61..R65`, expanding the block-level table from `1,116` to **`1,276` crossed rows across `550` matched blocks**.
3. Update `orchestration/autoresearch/fmx_surrogate_optimizer.py` and `orchestration/autoresearch/fmx_evidence_bundle.py` (plus tests `tests/test_fmx_live_dataset.py`, `tests/test_fmx_crossed_mixed_effects.py`, `tests/test_fmx_surrogate_optimizer.py`, `tests/test_fmx_evidence_bundle.py`) to reflect the `230`-record / `65`-round corpus while preserving byte-for-byte replay of `R56` and `R60` historical interfaces.

## Wave AT — Exact Rational & Zero-ULP Audit of `R61..R65` (`< 2.0%` Strict Goodput Preservation + `16/16` Across All 5 Contrasts at `3000 m`, `6000 m`, and `bidir_4flow`, Plus Positive `+0.0512%` Total Goodput Gain under `bidir_8flow`)
1. Create `analysis/statistics/fmx_r61_to_r65_strict_distance_and_flow_audit.py` and `tests/test_fmx_r61_to_r65_strict_distance_and_flow_audit.py`:
   - Perform an exact rational (`fractions.Fraction`) and IEEE-754 float audit across `R61, R62, R63, R64, R65`:
     - Verify `0.0` ULP float discrepancy and `'0'` `Fraction` discrepancy on all 4 block-mean metrics across all `10` arms (`160` block windows).
     - Verify `0.0%` packet loss (`160/160` pings received) on BOTH Arm A and Arm B across all `5` rounds (`1,600 / 1,600` total ICMP samples with `0` drops).
     - Prove that with `R61` (`3000 m`, `-1.260065%` delta, `16/16` across all 5 contrasts), `R62` (`6000 m`, `-0.827821%` delta, `16/16` across all 5 contrasts), `R64` (`bidir_4flow`, `-0.597677%` delta, `16/16` across all 5 contrasts), and `R65` (`bidir_6flow`, `-1.134814%` delta, `16/16` across all 5 contrasts), **ALL three distance classes (`100 m`, `3000 m`, `6000 m`) and medium/heavy flow regimes (`bidir_4flow`, `bidir_6flow`) now pass the strict `< 2.0%` total goodput-preservation threshold AND win `16 / 16` blocks across all 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, while `R63` (`bidir_8flow`) achieves **positive `+0.051166%` total goodput gain (`9/16` blocks won on total goodput) and `16/16` on `p95, p99, UL, Jain`**.
2. Write the comprehensive engineering report `docs/STAGE12_R61_TO_R65_STRICT_DISTANCE_AND_FLOW_PARITY_AUDIT.md`.

## Wave AU — Multi-Regime Selector & Promotion Gate Upgrade (`R61` at `3000 m`, `R62` at `6000 m`, `R63` at `bidir_8flow`, `R64` at `bidir_4flow` Qualified Under `strict_goodput_preservation`)
1. Update `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `orchestration/autoresearch/fmx_structural_promotion_gate.py` (plus `tests/test_fmx_multi_regime_dyadic_selector.py` and `tests/test_fmx_structural_promotion_gate.py`):
   - Upgrade `strict_goodput_preservation` (`< 2.0%` total goodput drop + `16/16` across all 5 contrasts) so it now qualifies:
     - `100 m` (`covclass=0`), `bidir_6flow`: **`R60`** (`-0.058395%` goodput delta, `11/16` total-goodput wins, `16/16` across all 5 contrasts) and **`R65`** (`-1.134814%` goodput delta, `7/16` total-goodput wins, `16/16` across all 5 contrasts),
     - `3000 m` (`covclass=6`), `bidir_6flow`: **`R61`** (`-1.260065%` goodput delta, `16/16` across all 5 contrasts, replacing `R52`'s `-5.35%`),
     - `6000 m` (`covclass=13`), `bidir_6flow`: **`R62`** (`-0.827821%` goodput delta, `16/16` across all 5 contrasts, replacing `R53`'s `-5.32%`),
     - `100 m` (`covclass=0`), `bidir_4flow`: **`R64`** (`-0.597677%` goodput delta, `16/16` across all 5 contrasts, replacing `R55`),
     - And under `bidir_8flow`: **`R63`** (`+0.051166%` positive total goodput gain, `9/16` total-goodput wins, `16/16` on `p95, p99, UL, Jain`, `15/16` on `p50`).

## Wave AV — Synchronization of Master Index, Ledgers, Docs Map, and Full Test Suite
1. Update:
   - `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`
   - `docs/CURRENT_STATE.md`
   - `docs/RESEARCH_LEDGER.md`
   - `docs/EXPERIMENTS.md`
   - `docs/DECISIONS.md`
   - `docs/DOCS-MAP.md`
2. Run the full repository test suite (`pytest -q`) and write a machine-verifiable validation receipt to `artifacts/autoresearch/waves_as_to_av_20261024/final_validation.json`.
