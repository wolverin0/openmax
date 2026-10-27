# Continuous Multi-Wave Autoresearch & Statistical Engineering Spec — Waves AW, AX, AY, AZ (`2026-10-24`)

## Context & Strict Rules
- **Role**: Offline Research, Statistical Verification, & Controller Engineering Lane (`Codex`).
- **Safety Rule**: Work **100% offline** in the repository. Do NOT SSH into any radio (`LAP-120`, `Loco195`, `Rocket198`, `omarchygwy`, etc.), because the live bench lane is actively running physical `autoresearch` Round 71+ on `LAP-120` <-> `Loco195`.
- **Execution Mode**: Execute **Waves AW, AX, AY, and AZ** end-to-end without stopping between waves until every deliverable, unit test, ledger entry, and master index entry is complete and `pytest -q` passes 100%.

---

## New Live Physical Bench Evidence to Ingest (`Rounds 66, 67, 68, 69, and 70` — 16-Block `AB/BA` Dyadic-Exact Zero-Loss Crossovers, `32` Windows per Round, `N=160` RTT per Arm, `0.0000%` Loss on BOTH Arms, and `0.0` ULP Float + `'0'` `Fraction` Block-Mean Discrepancy)

Five new live physical rounds (`R66, R67, R68, R69, R70`) were completed on `LAP-120` (`OpenWrt 24.10.4`, `4-addr WDS AP`) <-> `Loco195` (`OpenWrt 24.10.4`, `4-addr WDS STA`) to complete the **5-point distance curve (`100 m`, `3000 m`, `4500 m`, `6000 m`, `9000 m`)** and **4-point flow-density curve (`2, 4, 6, 8` flows)** under `< 2.0%` strict goodput preservation:

1. **Round 66 (`FMX-AUTORESEARCH-LIVE-066-BIDIR-2FLOW-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r66_bidir_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r66_bidir_2flow_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block counterbalanced `AB/BA` crossover (`32` windows, `N=160` RTT per arm) under **`bidir_2flow` (`-P 1 --bidir`, `active_flow_count=2`, `distance_m=100, coverage_class=0, slot_time_us=9, ack_timeout_us=18`)**.
   - **Result**: **`KEEP` (`fmx_loss = 0.270646` vs `0.329286` Stock, `-17.8%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold under `bidir_2flow`: `104.857421875 Mbps` vs `105.466796875 Mbps` Stock (`-0.577789%` total goodput delta, preserving `99.4222%` of Stock goodput vs `-3.56%` in `R54`!)**,
     - **Achieves STRICTLY LOWER MAC retry rate than Stock (`0.204942% < 0.218933%` across `657,258` WDS frames!)**,
     - **`p50 = 7.5550` vs `9.8325 ms`, `p95 = 15.9123` vs `20.4620 ms`, `p99 = 20.8612` vs `22.8671 ms`, `UL = 12.669921875` vs `10.8046875 Mbps` (`+17.3%`), `Jain = 0.63494873046875`**, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

2. **Round 67 (`FMX-AUTORESEARCH-LIVE-067-BIDIR-8FLOW-BE1480-2100-CODEL7-RC24-AF3-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r67_bidir_8flow_be1480_2100_codel7_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r67_bidir_8flow_be1480_2100_codel7_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover under **`bidir_8flow` (`-P 4 --bidir`, `active_flow_count=8`, `distance_m=100, coverage_class=0`)** testing tighter `AP BE=1480/2960 + codel=7/35ms`.
   - **Result**: **`KEEP` (`fmx_loss = 0.737484` vs `0.959063` Stock, `-23.1%`)**:
     - **`102.4248046875 Mbps` vs `104.9306640625 Mbps` Stock (`-2.388110%` delta), proving that `AP BE=1520/3040` (`R63`, `+0.051166%` positive goodput gain) is the exact lower knee of the `< 2.0%` goodput-preservation frontier under 8-flow saturation!**
     - **Wins `16 / 16` blocks on `UL` (`28.6259765625` vs `19.974609375 Mbps`, `+43.3%`) and `Jain` (`0.836669921875` vs `0.7227783203125`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)** plus `15/16` on `p50` (`7.5735` vs `11.3615 ms`), `p95` (`35.5737` vs `57.1379 ms`), and `p99`, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

3. **Round 68 (`FMX-AUTORESEARCH-LIVE-068-COVCLASS10-4500M-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r68_covclass10_4500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r68_covclass10_4500m_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **intermediate rural distance `4500 m` (`coverage_class=10, slot_time_us=39, ack_timeout_us=78`)** under `bidir_6flow` (`-P 3 --bidir`) with `BE=1520/2100 + af=1`.
   - **Result**: **`KEEP` (`fmx_loss = 0.345301` vs `0.899044` Stock, `-61.6%`)**:
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 6.7655` vs `28.5935 ms`, `p95 = 18.0907` vs `53.8395 ms`, `p99 = 30.9303` vs `62.8196 ms`, `UL = 23.375` vs `16.26171875 Mbps` `+43.7%`, `Jain = 0.785888671875`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `97.6884765625 Mbps` vs `99.82421875 Mbps` Stock (`-2.139503%` delta), `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

4. **Round 69 (`FMX-AUTORESEARCH-LIVE-069-COVCLASS20-9KM-BE1520-2100-CODEL8-RC24-AF1-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r69_covclass20_9km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r69_covclass20_9km_be1520_2100_codel8_rc24_af1_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **long-haul rural distance `9000 m` (`coverage_class=20, slot_time_us=69, ack_timeout_us=138`)** under `bidir_6flow` (`-P 3 --bidir`).
   - **Result**: **`KEEP` (`fmx_loss = 0.312179` vs `0.863526` Stock, `-63.8%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold at `9000 m`: `86.94921875 Mbps` vs `87.509765625 Mbps` Stock (`-0.640554%` total goodput delta — under `< 0.65%`, preserving `99.3594%` of Stock goodput!)**,
     - **Achieves STRICTLY LOWER MAC retry rate than Stock at `9000 m` (`0.180486% < 0.236996%`, `-23.8%` fewer MAC retries across `492,006` WDS frames!)**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 6.5035` vs `25.6865 ms`, `p95 = 17.3422` vs `48.2106 ms`, `p99 = 23.8512` vs `64.0352 ms`, `UL = 20.9306640625` vs `14.7548828125 Mbps` `+41.9%`, `Jain = 0.78778076171875` vs `0.69488525390625`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `5/16` blocks won on total goodput, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

5. **Round 70 (`FMX-AUTORESEARCH-LIVE-070-COVCLASS10-4500M-BE1560-2100-CODEL8-RC24-AF3-RETRY64-ABBA16-DYADIC-ZERO-LOSS-WDS-N160`)**:
   - **Artifact**: `artifacts/autoresearch/lap120_loco195_r70_covclass10_4500m_be1560_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_20261024.json`
   - **Runner**: `tools/bench/run_live_autoresearch_r70_covclass10_4500m_be1560_2100_codel8_rc24_af3_retry64_abba16_dyadic_zero_loss_wds_n160_20261024.py`
   - **Design**: `16`-block `AB/BA` crossover at **intermediate rural distance `4500 m` (`coverage_class=10, slot_time_us=39, ack_timeout_us=78`)** under `bidir_6flow` (`-P 3 --bidir`) testing `AP BE=1560/3120 + af=3 + retry 6/4`.
   - **Result**: **`KEEP` (`fmx_loss = 0.358082` vs `0.804490` Stock, `-55.5%`)**:
     - **Passes the `< 2.0%` strict goodput-preservation threshold at `4500 m`: `98.314453125 Mbps` vs `99.8134765625 Mbps` Stock (`-1.501825%` delta, improving `R68`'s `-2.1395%` across the `< 2.0%` boundary and winning `6/16` blocks on total goodput!)**,
     - **Wins ALL `16 / 16` blocks across ALL 5 contrasts (`p50 = 7.8660` vs `24.2130 ms`, `p95 = 21.4968` vs `48.6396 ms`, `p99 = 27.3518` vs `55.8146 ms`, `UL = 23.2509765625` vs `17.087890625 Mbps` `+36.1%`, `Jain = 0.7822265625` vs `0.697998046875`, $p = 0.00003052 < \alpha_{\text{Holm500}}$)**, `0.0000%` loss on both arms (`160/160`), and `0.0` ULP delta!

---

## Wave AW — Dataset, Multi-Factor Model, Surrogate, & Evidence Bundle Expansion (`R1..R70` = `240` Records, `1,436` Crossed Rows Across `630` Matched Blocks)
1. Update `orchestration/autoresearch/fmx_live_dataset.py` to ingest **`R66, R67, R68, R69, and R70`** (`10` new records: `16`-block `AB/BA` dyadic-exact zero-loss rounds with explicit `distance_m, coverage_class, slot_time_us, ack_timeout_us`, expanding the canonical dataset from `230` to **`240` records across `70` live physical rounds `R1..R70`**).
2. Update `analysis/statistics/fmx_crossed_mixed_effects.py` so the block-level crossed mixed-effects dataset includes all `32` windows (`16` matched blocks) from each of `R66..R70`, expanding the block-level table from `1,276` to **`1,436` crossed rows across `630` matched blocks**.
3. Update `orchestration/autoresearch/fmx_surrogate_optimizer.py` and `orchestration/autoresearch/fmx_evidence_bundle.py` (plus tests `tests/test_fmx_live_dataset.py`, `tests/test_fmx_crossed_mixed_effects.py`, `tests/test_fmx_surrogate_optimizer.py`, `tests/test_fmx_evidence_bundle.py`) to reflect the `240`-record / `70`-round corpus while preserving byte-for-byte replay of `R56`, `R60`, and `R65` historical interfaces.

## Wave AX — Exact Rational & Zero-ULP 5-Point Distance Curve (`100 m`, `3000 m`, `4500 m`, `6000 m`, `9000 m`) & 4-Point Flow Curve (`2, 4, 6, 8` Flows) Audit (`R66..R70`)
1. Create `analysis/statistics/fmx_r66_to_r70_five_distance_and_flow_curve_audit.py` and `tests/test_fmx_r66_to_r70_five_distance_and_flow_curve_audit.py`:
   - Perform an exact rational (`fractions.Fraction`) and IEEE-754 float audit across `R66, R67, R68, R69, R70`:
     - Verify `0.0` ULP float discrepancy and `'0'` `Fraction` discrepancy on all 4 block-mean metrics across all `10` arms (`160` block windows).
     - Verify `0.0%` packet loss (`160/160` pings received) on BOTH Arm A and Arm B across all `5` rounds (`1,600 / 1,600` total ICMP samples with `0` drops).
     - Verify the complete **5-Point Distance Curve under `< 2.0%` strict goodput preservation AND `16/16` across all 5 contrasts (`p50, p95, p99, UL, Jain`)**:
       - `100 m` (`covclass=0`, `R60`): `-0.058395%` goodput delta + `16/16` across all 5 contrasts,
       - `3000 m` (`covclass=6`, `R61`): `-1.260065%` goodput delta + `16/16` across all 5 contrasts,
       - `4500 m` (`covclass=10`, `R70`): `-1.501825%` goodput delta + `16/16` across all 5 contrasts (improving `R68`'s `-2.139503%`),
       - `6000 m` (`covclass=13`, `R62`): `-0.827821%` goodput delta + `16/16` across all 5 contrasts,
       - `9000 m` (`covclass=20`, `R69`): `-0.640554%` goodput delta + **strictly lower MAC retry rate (`0.180486% < 0.236996%`, `-23.8%`)** + `16/16` across all 5 contrasts!
2. Write the comprehensive engineering report `docs/STAGE12_R66_TO_R70_FIVE_DISTANCE_AND_FLOW_CURVE_AUDIT.md`.

## Wave AY — Multi-Regime Selector & Promotion Gate Upgrade (`4500 m` `R70` & `9000 m` `R69` Qualified Under `strict_goodput_preservation`, Plus `R66` under `bidir_2flow` Goodput & Retry Preservation)
1. Update `orchestration/autoresearch/fmx_multi_regime_dyadic_selector.py` and `orchestration/autoresearch/fmx_structural_promotion_gate.py` (plus `tests/test_fmx_multi_regime_dyadic_selector.py` and `tests/test_fmx_structural_promotion_gate.py`):
   - Extend the distance-aware selector to cover all 5 verified distances (`100 m`, `3000 m`, `4500 m`, `6000 m`, `9000 m`), qualifying **`R70`** at `4500 m` (`covclass=10`, `-1.501825%` delta, `16/16` across all 5 contrasts) and **`R69`** at `9000 m` (`covclass=20`, `-0.640554%` delta, strictly lower MAC retry rate `0.180486% < 0.236996%`, and `16/16` across all 5 contrasts) under `strict_goodput_preservation`, and recording **`R66`** (`bidir_2flow`, `-0.577789%` goodput delta + strictly lower MAC retry rate `0.204942% < 0.218933%`).

## Wave AZ — Synchronization of Master Index, Ledgers, Docs Map, and Full Test Suite
1. Update:
   - `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`
   - `docs/CURRENT_STATE.md`
   - `docs/RESEARCH_LEDGER.md`
   - `docs/EXPERIMENTS.md`
   - `docs/DECISIONS.md`
   - `docs/DOCS-MAP.md`
2. Run the full repository test suite (`pytest -q`) and write a machine-verifiable validation receipt to `artifacts/autoresearch/waves_aw_to_az_20261024/final_validation.json`.
