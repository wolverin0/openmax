# Continuous Multi-Wave Autoresearch & Statistical Engineering Spec — Waves BA, BB, BC, BD (`2026-10-24`)

## Context & Strict Rules
- **Role**: Offline Research, Statistical Verification, & Controller Engineering Lane (`Codex`).
- **Safety Rule**: Work **100% offline** in the repository. Do NOT SSH into any radio (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, etc.), because the live bench lane is actively running physical `autoresearch` Round 76+ on `LAP-120` <-> `Loco195`.
- **Execution Mode**: Execute **Waves BA, BB, BC, and BD** end-to-end without stopping between waves until every deliverable, unit test, ledger entry, and master index entry is complete and `pytest -q` passes 100%.

---

## New Live Physical Bench Evidence to Ingest (`Rounds 71, 72, 73, 74, and 75` — 16-Block `AB/BA` Dyadic-Exact Zero-Loss Crossovers, `32` Windows per Round, `N=160` RTT per Arm, `0.0000%` Loss on BOTH Arms, and `0.0` ULP Float + `'0'` `Fraction` Block-Mean Discrepancy)

Five new live physical rounds (`R71, R72, R73, R74, R75`) were completed on `LAP-120` (`OpenWrt 24.10.4`, `4-addr WDS AP`) <-> `Loco195` (`OpenWrt 24.10.4`, `4-addr WDS STA`) to extend the **distance curve to `12000 m` (`covclass=27`) and `15000 m` (`covclass=33`)** under `< 2.0%` strict goodput preservation AND `16/16` across all 5 contrasts, and to refine `bidir_2flow` (`R71`) and `bidir_8flow` (`R72, R74`):

1. **Round 71 (`FMX-AUTORESEARCH-LIVE-071-BIDIR-2FLOW-BE1350-2200-CODEL6-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r71_bidir_2flow_be1350_2200_codel6_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r71_bidir_2flow_be1350_2200_codel6_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) under **`bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`, `distance_m=100, coverage_class=0, slot_time_us=9, ack_timeout_us=18`)** testing `AP BE=1350/2700 (codel=6/30ms) + CPE BE=2200/4400 (codel=10/50ms) + RC=24% + af=1 + retry 6/4`.
   - **Result**: **`KEEP` (`fmx_loss = 0.292893` vs `0.357351` Stock, `-18.0%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold under `bidir_2flow`: `103.3251953125 Mbps` vs `105.1328125 Mbps` Stock (`-1.719365%` delta)**,
     - **Wins `16 / 16` blocks on `UL` (`13.7509765625` vs `10.6337890625 Mbps`, `+29.3%`) and `Jain` (`0.65008544921875` vs `0.6112060546875`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p50` (`8.2045` vs `11.0040 ms`), `14/16` on `p95/p99`, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

2. **Round 72 (`FMX-AUTORESEARCH-LIVE-072-BIDIR-8FLOW-BE1520-2100-CODEL7-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r72_bidir_8flow_be1520_2100_codel7_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r72_bidir_8flow_be1520_2100_codel7_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under **`bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`, `distance_m=100, coverage_class=0`)** testing `AP BE=1520/3040 (codel=7/35ms) + CPE BE=2100/4200 (codel=9/45ms) + RC=24% + af=1 + retry 6/4`.
   - **Result**: **`KEEP` (`fmx_loss = 0.488328` vs `1.057312` Stock, `-53.8%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold (`104.6064453125 Mbps` vs `105.0537109375 Mbps` Stock = `-0.425750%` delta, winning `7/16` blocks on total goodput!)**,
     - **Wins `16 / 16` blocks on `p95` (`25.4994` vs `64.3635 ms`), `UL` (`28.1630859375` vs `19.34765625 Mbps`, `+45.6%`), and `Jain` (`0.8240966796875`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p50` (`8.8125` vs `22.5395 ms`) and `p99`, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

3. **Round 73 (`FMX-AUTORESEARCH-LIVE-073-COVCLASS27-12KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r73_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r73_covclass27_12km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **extreme long-haul rural distance `12000 m` (`12 km`, `coverage_class=27, slot_time_us=90, ack_timeout_us=180`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Result**: **`KEEP` (`fmx_loss = 0.248838` vs `0.959506` Stock, `-74.1%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold at `12 km`: `80.5263671875 Mbps` vs `81.9033203125 Mbps` Stock (`-1.681193%` delta, winning `6/16` blocks on total goodput!)**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 5.7590` vs `28.7460 ms`, `p95 = 14.0745` vs `56.0230 ms`, `p99 = 17.3245` vs `66.3467 ms`, `UL = 20.5126953125` vs `14.3046875 Mbps` `+43.4%`, `Jain = 0.80535888671875` vs `0.7022705078125`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

4. **Round 74 (`FMX-AUTORESEARCH-LIVE-074-BIDIR-8FLOW-BE1510-2150-CODEL5-VO900-RC24-AF3-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r74_bidir_8flow_be1510_2150_codel5_vo900_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r74_bidir_8flow_be1510_2150_codel5_vo900_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under **`bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`, `distance_m=100, coverage_class=0`)** testing `AP VO=900/1800 BE=1510/3020 codel=5/25ms + CPE VO=900/1800 BE=2150/4300 codel=7/35ms + RC=24% + af=3 + retry 6/4`.
   - **Result**: **`KEEP` (`fmx_loss = 0.453080` vs `0.887490` Stock, `-48.9%`)**:
     - **Achieves POSITIVE total goodput gain over Stock (`+0.234151%`, `105.3466796875 Mbps` vs `105.1005859375 Mbps` Stock — highest 8-flow goodput gain in the corpus!)**,
     - **Wins ALL `16 / 16` blocks on `p95` (`25.1795` vs `50.8688 ms`), `p99` (`37.5843` vs `66.0379 ms`), `UL` (`30.255859375` vs `18.9677734375 Mbps`, `+59.5%`), and `Jain` (`0.8463134765625` vs `0.71014404296875`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p50` (`8.3210` vs `10.2480 ms`), `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

5. **Round 75 (`FMX-AUTORESEARCH-LIVE-075-COVCLASS33-15KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r75_covclass33_15km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r75_covclass33_15km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **upper-limit rural sector distance `15000 m` (`15 km`, `coverage_class=33, slot_time_us=108, ack_timeout_us=216`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Result**: **`KEEP` (`fmx_loss = 0.265059` vs `1.051607` Stock, `-74.8%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold at `15 km`: `76.0615234375 Mbps` vs `77.2001953125 Mbps` Stock (`-1.474960%` delta, winning `5/16` blocks on total goodput!)**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 5.5935` vs `31.2330 ms`, `p95 = 15.1496` vs `63.1889 ms`, `p99 = 18.6245` vs `70.0342 ms`, `UL = 20.1640625` vs `14.625 Mbps` `+37.9%`, `Jain = 0.818115234375` vs `0.72149658203125`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

---

## Wave BA — Dataset, Multi-Factor Model, Surrogate, & Evidence Bundle Expansion (`R1..R75` = `250` Records, `1,596` Crossed Rows Across `710` Matched Blocks)
1. Update `orchestration/autoresearch/fmx_live_dataset.py` to ingest **`R71, R72, R73, R74, and R75`** (`10` new records: `16`-block `AB/BA` dyadic-exact zero-loss rounds with explicit `distance_m, coverage_class, slot_time_us, ack_timeout_us`, expanding the canonical dataset from `240` to **`250` records across `75` live physical rounds `R1..R75`**).
2. Update `analysis/statistics/fmx_crossed_mixed_effects.py` so the block-level crossed mixed-effects dataset includes all `32` windows (`16` matched blocks) from each of `R71..R75`, expanding the block-level table from `1,436` to **`1,596` crossed rows across `710` matched blocks**.
3. Update `orchestration/autoresearch/fmx_surrogate_optimizer.py` and `orchestration/autoresearch/fmx_evidence_bundle.py` (plus tests `tests/test_fmx_live_dataset.py`, `tests/test_fmx_crossed_mixed_effects.py`, `tests/test_fmx_surrogate_optimizer.py`, `tests/test_fmx_evidence_bundle.py`) to reflect the `250`-record / `75`-round corpus while preserving byte-for-byte replay of `R56`, `R60`, `R65`, and `R70` historical interfaces.

## Wave BB — Exact Rational & Zero-ULP 7-Point Distance Curve (`100 m`, `3 km`, `4.5 km`, `6 km`, `9 km`, `12 km`, `15 km`) & 8-Flow Positive-Goodput Audit (`R71..R75`)
1. Create `analysis/statistics/fmx_r71_to_r75_seven_distance_and_flow_audit.py` and `tests/test_fmx_r71_to_r75_seven_distance_and_flow_audit.py`:
   - Perform an exact rational (`fractions.Fraction`) and IEEE-754 float audit across `R71, R72, R73, R74, R75`:
     - Verify `0.0` ULP float discrepancy and `'0'` `Fraction` discrepancy on all 4 block-mean metrics across all `10` arms (`160` block windows).
     - Verify `0.0%` packet loss (`160/160` pings received) on BOTH Arm A and Arm B across all `5` rounds (`1,600 / 1,600` total ICMP samples with `0` drops).
     - Verify the complete **7-Point Distance Curve (`100 m` `R60`, `3000 m` `R61`, `4500 m` `R70`, `6000 m` `R62`, `9000 m` `R69`, `12000 m` `R73`, `15000 m` `R75`) where EVERY distance class passes `< 2.0%` strict goodput preservation AND wins `16 / 16` blocks across ALL 5 contrasts (`p50, p95, p99, UL, Jain`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**!
2. Write the comprehensive engineering report `docs/STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT.md`.

## Wave BC — Multi-Regime Selector & Promotion Gate Upgrade (`12000 m` `R73` & `15000 m` `R75` Qualified Under `strict_goodput_preservation`)
1. Update `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `orchestration/autoresearch/fmx_structural_promotion_gate.py` (plus `tests/test_fmx_multi_regime_dyadic_selector.py` and `tests/test_fmx_structural_promotion_gate.py`):
   - Extend `DISTANCE_CLASSES` to cover all 7 verified distances (`{100: 0, 3000: 6, 4500: 10, 6000: 13, 9000: 20, 12000: 27, 15000: 33}`), qualifying **`R73`** at `12000 m` (`covclass=27`, `-1.681193%` delta, `16/16` across all 5 contrasts) and **`R75`** at `15000 m` (`covclass=33`, `-1.474960%` delta, `16/16` across all 5 contrasts) under `strict_goodput_preservation`, and recording `R71` (`bidir_2flow`), `R72` (`bidir_8flow`), and `R74` (`bidir_8flow` `+0.234151%` positive goodput gain + `16/16` on `p95, p99, UL, Jain`).

## Wave BD — Synchronization of Master Index, Ledgers, Docs Map, and Full Test Suite
1. Update:
   - `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`
   - `docs/CURRENT_STATE.md`
   - `docs/RESEARCH_LEDGER.md`
   - `docs/EXPERIMENTS.md`
   - `docs/DECISIONS.md`
   - `docs/DOCS-MAP.md`
2. Run the full repository test suite (`pytest -q`) and write a machine-verifiable validation receipt to `artifacts/autoresearch/waves_ba_to_bd_20261024/final_validation.json`.
