# Continuous Multi-Wave Autoresearch & Statistical Engineering Spec — Waves AO, AP, AQ, AR (`2026-10-24`)

## Context & Strict Rules
- **Role**: Offline Research, Statistical Verification, & Controller Engineering Lane (`Codex`).
- **Safety Rule**: Work **100% offline** in the repository. Do NOT SSH into any radio (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, etc.), because the live bench lane is actively running physical `autoresearch` Round 61+ on `LAP-120` <-> `Loco195`.
- **Execution Mode**: Execute **Waves AO, AP, AQ, and AR** end-to-end without stopping between waves until every deliverable, unit test, ledger entry, and master index entry is complete and `pytest -q` passes 100%.

---

## New Live Physical Bench Evidence to Ingest (`Rounds 57, 58, 59, and 60` — 16-Block `AB/BA` Dyadic-Exact Zero-Loss Crossovers, `32` Windows per Round, `N=160` RTT per Arm, `0.0000%` Loss on BOTH Arms, `0.0` ULP Float + `'0'` `Fraction` Block-Mean Discrepancy, and Explicit `coverage_class=0, distance_m=100, slot_time_us=9, ack_timeout_us=18` Context)

Four new live physical rounds (`R57, R58, R59, R60`) were completed on `LAP-120` (`OpenWrt 24.10.4`, `4-addr WDS AP`) <-> `Loco195` (`OpenWrt 24.10.4`, `4-addr WDS STA`) to resolve the remaining `100 m` (`coverage_class=0`) goodput-preservation, MAC-retry-rate, and `16/16` tail-latency (`p99`) questions identified in Wave AL/AM:

1. **Round 57 (`FMX-AUTORESEARCH-LIVE-057-BIDIR-8FLOW-BE1500-2100-AF3-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r57_bidir_8flow_be1500_2100_af3_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r57_bidir_8flow_be1500_2100_af3_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) under heavy **`bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`, `coverage_class=0, distance_m=100`)** testing `AP BE=1500/3000 + CPE BE=2100/4200 + af=3 + fq_limit=2048 + ftx=1 + retry 5/3`.
   - **Result**: **`KEEP` (`fmx_loss = 0.402138` vs `1.039300` Stock, `-61.3%`)**, lifting `bidir_8flow` total goodput from `95.375977 Mbps` (`R47`) to **`99.201171875 Mbps` (`-5.54%` vs `105.0244140625 Mbps` Stock)**, `UL = 28.857421875 Mbps` (`+49.1%` UL), `Jain = 0.850830078125`, `p50/p95/p99 = 7.1775 / 21.7920 / 34.7802 ms`, **strictly lower MAC retry rate (`0.155207% < 0.171096%` across `536,701` WDS frames)**, `0.0000%` loss on both arms (`160/160`), `0.0` ULP delta, and **`16/16` block wins on `UL` and `Jain`** ($p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$) plus `15/16` on `p50, p95, p99`.

2. **Round 58 (`FMX-AUTORESEARCH-LIVE-058-BIDIR-6FLOW-BE1750-2100-AF1-RETRY53-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r58_bidir_6flow_be1750_2100_af1_retry53_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r58_bidir_6flow_be1750_2100_af1_retry53_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_6flow` (`-P 3 --bidir`, `coverage_class=0, distance_m=100`) testing `AP BE=1750/3500 + CPE BE=2100/4200 + af=1 + fq_limit=2048 + ftx=1 + retry 5/3`.
   - **Result**: **`KEEP` (`fmx_loss = 0.375652` vs `0.800392` Stock, `-53.1%`)**, `94.4130859375 Mbps` (`UL = 24.2265625`, `+47.3%` UL, `Jain = 0.80853271484375`), `p50/p95/p99 = 6.7165 / 20.2304 / 32.6171 ms` vs Stock `25.4815 / 45.9721 / 59.4287 ms`, `0.0000%` loss on both arms (`160/160`), `0.0` ULP delta, and **`16 / 16` block wins across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}}$)**.
   - **Diagnostic Mechanism Discovered**: Comparing `R50` (`long_retry_limit=4` in `retry 7/4`, `DL=81.70 Mbps`, `tot=107.68 Mbps`) against `R51` and `R58` (`long_retry_limit=3` in `retry 5/3`, `DL=70.19 Mbps`, `tot=94.41 Mbps`) proved that lowering `long_retry_limit` from `4` to `3` drops A-MPDU subframes earlier under 6-flow bidirectional saturation, triggering TCP CUBIC `cwnd` backoff on the AP (`DL`).

3. **Round 59 (`FMX-AUTORESEARCH-LIVE-059-BIDIR-6FLOW-BE1550-2100-RC24-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r59_bidir_6flow_be1550_2100_rc24_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r59_bidir_6flow_be1550_2100_rc24_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_6flow` (`-P 3 --bidir`, `coverage_class=0, distance_m=100`) testing **`AP BE=1550/3100 (TSQ=256/128KB, rc_per_thresh=24%) + CPE BE=2100/4200 (TSQ=320/160KB, rc_per_thresh=24%) + af=1 + fq_limit=2048 + ftx=1 + retry 6/4 (short_retry=6, long_retry=4)`**.
   - **Result**: **`KEEP` (`fmx_loss = 0.418820` vs `0.814435` Stock, `-48.6%`)**:
     - **Preserved `99.9804%` of Stock total goodput (`104.830078125 Mbps` vs `104.8505859375 Mbps` Stock = `-0.019559%` total goodput delta — winning `9 / 16` matched blocks on total goodput!)**,
     - **Achieved STRICTLY LOWER MAC retry rate than Stock (`0.188876% < 0.192354%` across `592,452` WDS frames — eliminating the retry-rate cost of `R50`!)**,
     - **Won `16 / 16` blocks on `p50` (`7.1525` vs `25.8510 ms`), `p95` (`19.8669` vs `48.2084 ms`), `UL` (`25.281250` vs `16.556641 Mbps`, `+52.7%` UL), and `Jain` (`0.78814697` vs `0.68127441`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p99`, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

4. **Round 60 (`FMX-AUTORESEARCH-LIVE-060-BIDIR-6FLOW-BE1520-2100-CODEL8-RC24-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r60_bidir_6flow_be1520_2100_codel8_rc24_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r60_bidir_6flow_be1520_2100_codel8_rc24_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under `bidir_6flow` (`-P 3 --bidir`, `coverage_class=0, distance_m=100`) testing **`AP BE=1520/3040 (codel=8/40ms, TSQ=240/120KB, rc_per_thresh=24%) + CPE BE=2100/4200 (codel=10/50ms, TSQ=320/160KB, rc_per_thresh=24%) + af=1 + fq_limit=2048 + ftx=1 + retry 6/4`**.
   - **Result**: **`KEEP` (`fmx_loss = 0.319029` vs `0.807983` Stock, `-60.5%`)**:
     - **Preserved `99.9416%` of Stock total goodput (`105.294921875 Mbps` vs `105.3564453125 Mbps` Stock = `-0.058395%` total goodput delta — winning **`11 / 16` matched blocks on total goodput!**)**,
     - **Won ALL `16 / 16` blocks across ALL 5 primary contrasts (`p50 = 7.0930` vs `25.9935 ms`, `p95 = 18.7124` vs `48.5614 ms`, `p99 = 25.5220` vs `56.3697 ms`, `UL = 25.236328` vs `16.436523 Mbps` `+53.5%`, `Jain = 0.78662109` vs `0.67877197`, exact two-sided sign test $p = 2/65536 = 0.00003052 < \alpha_{\text{Holm500}} = 0.00010$ across all 5 contrasts!)**,
     - **`0.0000%` packet loss on both arms (`160/160`) and `0.0` ULP dyadic float/`Fraction` discrepancy**!

---

## Wave AO — Dataset, Multi-Factor Model, Surrogate, & Evidence Bundle Expansion (`R1..R60` = `220` Records, `1,116` Crossed Rows Across `470` Matched Blocks)
1. Update `orchestration/autoresearch/fmx_live_dataset.py` to ingest **`R57, R58, R59, and R60`** (`8` new records: `16`-block `AB/BA` dyadic-exact zero-loss rounds with explicit `coverage_class=0, distance_m=100`, expanding the canonical dataset from `212` to **`220` records across `60` live physical rounds `R1..R60`**).
2. Update `analysis/statistics/fmx_crossed_mixed_effects.py` so the block-level crossed mixed-effects dataset includes all `32` windows (`16` matched blocks) from each of `R57..R60`, expanding the block-level table from `988` to **`1,116` crossed rows across `470` matched blocks**.
3. Update `orchestration/autoresearch/fmx_surrogate_optimizer.py` and `orchestration/autoresearch/fmx_evidence_bundle.py` (plus tests `tests/test_fmx_live_dataset.py`, `tests/test_fmx_crossed_mixed_effects.py`, `tests/test_fmx_surrogate_optimizer.py`, `tests/test_fmx_evidence_bundle.py`) to reflect the `220`-record / `60`-round corpus and the new `retry 6/4 + rc_per_thresh=24%` (`R59, R60`) profiles.

## Wave AP — Exact Rational & Zero-ULP Audit of `R57..R60` (`99.98%` / `99.94%` Goodput Preservation, Lower MAC Retry Rate in `R59`, and `16/16` Across All 5 Contrasts + `11/16` Total-Goodput Wins in `R60`)
1. Create `analysis/statistics/fmx_r57_to_r60_retry64_goodput_parity_audit.py` and `tests/test_fmx_r57_to_r60_retry64_goodput_parity_audit.py`:
   - Perform an exact rational (`fractions.Fraction`) and IEEE-754 float audit across `R57, R58, R59, R60`:
     - Verify `0.0` ULP float discrepancy and `'0'` `Fraction` discrepancy on all 4 block-mean metrics across all `8` arms (`128` block windows).
     - Verify `0.0%` packet loss (`160/160` pings received) on BOTH Arm A and Arm B across all `4` rounds (`1,280 / 1,280` total ICMP samples with `0` drops) and explicit `coverage_class=0, distance_m=100` context.
     - Audit the `long_retry_limit=4` (`retry 6/4`) + `rc_per_thresh=24%` breakthrough in `R59` and `R60`:
       - Prove that **`R59`** achieves **simultaneous `< 0.02%` total goodput delta (`-0.019559%`, `9/16` blocks won on total goodput) AND strictly lower MAC retry rate (`0.188876% < 0.192354%`) AND `16/16` block wins on `p50, p95, UL, Jain` ($p = 0.00003052 < \alpha_{\text{Holm500}}$)**.
       - Prove that **`R60`** achieves **simultaneous `-0.058395%` total goodput delta (`11/16` blocks won on total goodput!) AND `16 / 16` block wins across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**.
2. Write the comprehensive engineering report `docs/STAGE12_R57_TO_R60_RETRY64_GOODPUT_PARITY_AND_16OF16_AUDIT.md`.

## Wave AQ — Multi-Regime Selector & Promotion Gate Upgrade (`R59` Retry-Dominant & `R60` `16/16` 5-Contrast + `11/16` Goodput-Winning Profiles at `100 m`)
1. Update `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `orchestration/autoresearch/fmx_structural_promotion_gate.py` (plus `tests/test_fmx_multi_regime_dyadic_selector.py` and `tests/test_fmx_structural_promotion_gate.py`):
   - Incorporate `R57, R58, R59, R60` with their explicit `coverage_class=0, distance_m=100` context so `100 m` (`covclass=0`) has accredited distance/coverage context.
   - Expose:
     - **`R60`** as the `strict_goodput_preservation` `16/16` 5-contrast (`p50, p95, p99, UL, Jain`) + `11/16` total-goodput-block-winning (`-0.0584%` delta) profile at `100 m` (`bidir_6flow`),
     - **`R59`** as the `strict_goodput_AND_lower_retry` profile (`-0.0196%` goodput delta, `9/16` total-goodput block wins, `0.188876% < 0.192354%` MAC retry rate, `16/16` on `p50, p95, UL, Jain`), and
     - **`R57`** alongside `R47` under `bidir_8flow` (`99.20 Mbps`, lower MAC retry rate `0.155207% < 0.171096%`, `16/16` on `UL, Jain`).

## Wave AR — Synchronization of Master Index, Ledgers, Docs Map, and Full Test Suite
1. Update:
   - `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`
   - `docs/CURRENT_STATE.md`
   - `docs/RESEARCH_LEDGER.md`
   - `docs/EXPERIMENTS.md`
   - `docs/DECISIONS.md`
   - `docs/DOCS-MAP.md`
2. Run the full repository test suite (`pytest -q`) and write a machine-verifiable validation receipt to `artifacts/autoresearch/waves_ao_to_ar_20261024/final_validation.json`.
