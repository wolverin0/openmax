<!-- doc-head: STAGE12_CERTIFIED_WDS_HOLM500_AND_REGIME_PROMOTION_AUDIT.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_CERTIFIED_WDS_HOLM500_AND_REGIME_PROMOTION_AUDIT.md) | Part 1/2
<a id="period-transition-and-carryover-design-limits"></a> [Period, transition and carryover design limits](STAGE12_CERTIFIED_WDS_HOLM500_AND_REGIME_PROMOTION_AUDIT_CONTINUATION_ef1262203a_002.md#period-transition-and-carryover-design-limits) | <a id="regime-selector-and-structural-promotion-boundary"></a> [Regime selector and structural promotion boundary](STAGE12_CERTIFIED_WDS_HOLM500_AND_REGIME_PROMOTION_AUDIT_CONTINUATION_ef1262203a_002.md#regime-selector-and-structural-promotion-boundary) | <a id="verification-preserved-failures-and-disposition"></a> [Verification, preserved failures and disposition](STAGE12_CERTIFIED_WDS_HOLM500_AND_REGIME_PROMOTION_AUDIT_CONTINUATION_ef1262203a_002.md#verification-preserved-failures-and-disposition)

<!-- stage822a-payload-begin -->

Eighteen frozen R27-R32 inputs yield 150 records and 332 crossed rows in 106 matched IDs.
All 19 new arms retain chronology and positive MAC denominators; only four pass literal means.
R32 and pooled 46-block results survive the declared conservative family of 500.
R28-C p99 is 11/12 and R29 p99 is 12/14; n4 exact intervals remain unbounded.
Actual canary promotions are zero; source gates, regime limits and Stage4 remain binding.
701 research tests pass; broader offline suite has 1695 PASS, five skips and zero failures.


# Stage12 saved WDS campaign, exact Holm500 audit and regime promotion gate

Research ID: `FMX-OFFLINE-WAVES-YZAB-20261024`. Parent: original Stage12 control-authority, experimental-methodology and custom-MAC feasibility-boundary deliverables in `artifacts/2026-09-20-forward-plan.html`, with the current course in [BENCH_PLAN](BENCH_PLAN.md). The [full frozen specification](../artifacts/autoresearch/waves_yzab_20261024/inputs/waves_yzab_20261024_spec.md) was read in full. This is a retrospective audit of saved single-link observations and an offline implementation. It does not run another physical experiment or establish current device state.

## Outcome and acceptance boundary

**CONFIRMED computationally:** the requested normalizer, exact statistical audit, source-pinned structural gate and regime selector are implemented. All 595 previous research cases plus 106 new cases pass: **701/701, zero failures/errors/skips, exit 0**. Independent Y, Z and AA reviews accept the code and calculations with limits. The broader first-party offline suite records **1695 PASS, five skipped, zero failures/errors, exit 0**. The skips and exclusions are explicit below; literal unfiltered pytest is not claimed.

**CONFIRMED from saved blocks:** R32's five latency/UL/Jain contrasts and the corresponding pooled 46-block contrasts survive the complete enumerated known crossover family conservatively completed to 500. Four R29 contrasts survive the scoped 324 analysis but not the 500 analysis. This conditional statistical evidence is stronger than the preceding U-X broad-family result.

**REFUTED:** the supplied 151-record/328-row/108-block counts, all-arm literal summary equality, R28-C p99 unanimity and R29's claimed 13/14 p99 count. The actual totals are **150 records, 332 crossed treatment rows in 106 matched round/block IDs, plus 16 separate R17 sequential rows**. Fifteen of 19 new arms fail literal recorded-decimal mean equality; four R31 arms pass. The campaign label “certified” is not a successful gate result.

**Actual promotion result: zero.** All three requested regimes return `BLOCKED` under the stated conjunctive conditions. Broad statistical support does not replace failed exact source checks, and R31's four-block evidence cannot satisfy the necessary exact significance gate. Positive disposable fixtures can return `PROMOTED_CERTIFIED_CANARY`; that label means conditional offline eligibility and always keeps automatic execution and physical safety qualification false. No physical canary, deployment, new RF treatment or Stage4 success is accepted.

## Frozen inputs and actual experimental units

The [input manifest](../artifacts/autoresearch/waves_yzab_20261024/inputs_manifest.json) binds 18 files copied before content inspection: six JSON receipts, six TSVs and six recipes. The specification was also copied locally. Analysis used those copies and unchanged U-X outputs; original new receipts were not reopened. Recipes were inspected as text/AST and never imported or executed. No radio/network-device/SSH operation, online installation, raw assembly/hex dump, credential output, flash or deployment belongs to this delivery.

| Round | Arms | Treatment rows | Matched round/block IDs | Recorded workload |
|---|---:|---:|---:|---|
| R27 | 4 | 16 | 4 | `-P 3 --bidir`: six directional flows |
| R28 | 3 | 36 | 12 | `-P 3 --bidir`: six directional flows |
| R29 | 2 | 28 | 14 | `-P 3 --bidir`: six directional flows |
| R30 | 4 | 16 | 4 | `-P 1 --bidir`: two directional flows |
| R31 | 4 | 16 | 4 | `-P 2`, no bidir: two DL flows |
| R32 | 2 | 32 | 16 | `-P 3 --bidir`: six directional flows |
| New total | 19 | 144 | 54 | Three explicit regimes |
| Combined with U-X | 150 records | 332 | 106 | R17's 16 sequential rows remain separate |

The specification's alternative pooled header of 42 blocks conflicts with its own listed rounds: R27+R28+R29+R32 supplies **4+12+14+16=46**, which is the actual pooled analysis. Records contain 148 primary windows and two earlier auxiliary validations. A treatment row is not an independent ping or a new sector; `(round_id, block_index)` is the pairing key.

The [schema7 corpus](../artifacts/autoresearch/waves_yzab_20261024/normalized_r1_to_r32_measurements_20261024.json) preserves all 131 previous records exactly, including their classes/fields/policy identities when rehydrated. The [block corpus](../artifacts/autoresearch/waves_yzab_20261024/normalized_r16_to_r32_block_observations_20261024.json) preserves 188 old crossed rows and all 16 R17 rows, adding 144 rows with actual counter fields. Earlier loader APIs stay fixed. New `load_all32_measurements()` / `load_normalized_records()` return `(records, source_refs)`; `load_all32_block_observations()` / `load_crossed_block_records()` return separate `crossed`, `sequential`, and `source_refs` collections. The CLI adds `--all-rounds32`; output rules prohibit overwriting frozen inputs or live receipt paths.

## Source checks: chronology and counters pass, literal means do not

`CertifiedWDSMeasurement` extends the existing typed six-hook record with explicit `block_mean_consistent`, `raw_rtts_matches_blocks` and `certified_wds_evidence`. Its class name identifies the saved campaign, not independent acceptance. It retains source receipt/recipe hashes, AP/CPE state dictionaries, exact rational deltas, ordinary numpy deltas, per-block MAC counts/rates, interface provenance and quality flags.

Literal equality is evaluated as `Fraction(str(reported))*n == sum(Fraction(str(block_value)))`, using the canonical recorded decimal numbers. This excludes irrelevant binary floating-point noise but applies **no tolerance** to genuine source rounding. All four quantities—total goodput, DL, UL and Jain—must pass. For example, R27 total goodput is exactly consistent in decimal arithmetic even though numpy shows about 1.4e-14 floating noise; its Jain mean still differs genuinely. R28 stock total differs from its recorded block mean by about 0.000666667 Mbps.

All 19 new windows pass the inherited general 0.021 Mbps consistency check, the exact concatenated RTT membership check and positive window/block MAC denominator checks. They also preserve exact MAC count sums. This is real progress in source usability over the previous U-X windows. It does **not** make the stricter literal equality flag true. Only R31's four arms pass that conjunction; the other 15 remain false. A separately named rounding-compatible diagnostic (Mbps 0.001, Jain 0.00055) describes serialization precision only and is never substituted for certification or controller acceptance. Neither source means nor scores were repaired.

All six frozen recipes name `phy0-ap0.sta1`; the retained provenance says exactly that, rather than claiming an independent device-side counter audit. The acquisition pipeline can also read the parent interface. Positive saved counts are not proof of exclusive per-station accounting, precision of firmware TX completion or bounded lower-layer queues. Retry fractions retain reported precision and exact counter ratios; TCP retransmissions are not MAC PER.

The following are **reported window summaries from the frozen data**, not rewritten block means. The full corpus retains both representations.

| Round | Arm | Reported goodput Mbps | Reported p50 / p95 / p99 ms | MAC TX packets | Literal four-mean pass |
|---|---|---:|---|---:|---|
| R27 | `iter0` | 104.925 | 26.058 / 41.086 / 50.396 | 163155 | False |
| R27 | `iter1` | 105.575 | 7.546 / 21.055 / 36.514 | 150059 | False |
| R27 | `iter2` | 105.25 | 7.136 / 19.635 / 30.636 | 148421 | False |
| R27 | `iter3` | 96.95 | 6.382 / 24.785 / 36.105 | 135727 | False |
| R28 | `iter0` | 105.766 | 26.188 / 48.434 / 55.589 | 486619 | False |
| R28 | `iter1` | 105.175 | 6.867 / 16.655 / 26.266 | 444602 | False |
| R28 | `iter2` | 97.2 | 7.873 / 22.094 / 26.551 | 407408 | False |
| R29 | `iter0` | 106.15 | 23.79 / 49.492 / 65.337 | 573458 | False |
| R29 | `iter1` | 104.793 | 6.681 / 27.134 / 37.355 | 522041 | False |
| R30 | `iter0` | 106.475 | 10.89 / 23.261 / 24.884 | 169297 | False |
| R30 | `iter1` | 104.85 | 8.442 / 17.018 / 19.082 | 162990 | False |
| R30 | `iter2` | 105.1 | 7.021 / 16.088 / 16.971 | 163346 | False |
| R30 | `iter3` | 100.45 | 7.941 / 16.642 / 19.368 | 156935 | False |
| R31 | `iter0` | 110 | 17.221 / 28.106 / 31.24 | 193209 | True |
| R31 | `iter1` | 108.25 | 8.424 / 21.273 / 23.314 | 189422 | True |
| R31 | `iter2` | 105.25 | 11.067 / 22.212 / 24.818 | 184299 | True |
| R31 | `iter3` | 103.75 | 7.693 / 20.962 / 29.128 | 181746 | True |
| R32 | `iter0` | 105.344 | 24.916 / 51.847 / 63.478 | 653623 | False |
| R32 | `iter1` | 105.219 | 6.773 / 22.974 / 32.883 | 593523 | False |

These source values supersede the specification's narrative values for this audit. For example, R28 stock reports 105.766 Mbps rather than 104.242, and R28-C reports 97.2 rather than 99.908. A saved `KEEP` or `fmx_loss` result is an objective evaluation under that recipe, not independent promotion evidence.

Recorded loss remains present: R27 stock receives 39/40, R28 stock 119/120 and R29 stock 134/140 pings. R32 stock and treatment both receive 160/160, with ten received samples per block. Lossful control blocks are retained in paired inference; no ping positions become synthetic pairs. Positive target window restoration is a saved report, not independent recovery acceptance, and unknown per-block health remains unknown.

## Exact statistical method and explicit multiplicity scopes

The [Z implementation](../analysis/statistics/fmx_r27_to_r32_certified_wds_audit.py) computes exact two-sided conditional signed-rank and sign probabilities, Walsh paired Hodges-Lehmann shifts and exact signed-rank inversion sets. Tied absolute ranks receive midranks and exact zero differences are disclosed under the Wilcox zero rule. Integer rank-sum dynamic programming counts the conditional distribution; it does not enumerate 2^46 sign vectors. At 46 nonzero blocks the counted space is 70,368,744,177,664 assignments.

The [family recipe](../artifacts/autoresearch/waves_yzab_20261024/wave_z_families_precomputation.json) was frozen before outcome computation. The operator already supplied desired outcomes, so this remains retrospective and exploratory, not prospective preregistration. All 23 within-round arm pairs are evaluated on six inherited metrics (total goodput, p50, p95, p99, UL, Jain): 138 hypotheses. Five explicitly requested pooled outcomes bring the known new scope to 143. The unchanged previous 324 crossover hypotheses plus these 143 form an enumerated known scope of 467; this is not a claim to enumerate every research hypothesis in the project.

For round-local `Holm10`, R28 supplies ten named B/C-versus-stock contrasts. R27/R29/R30/R31/R32 and the pool supply five requested contrasts each, with five explicit p=1 placeholders. Scoped 324/500 sensitivity families use all 143 new hypotheses and p=1 completion. The complete known scope is also corrected at 467 and conservatively completed to 500. A 324-size family cannot cover 467 known members. Placeholder values are a stated conservative completion, not fabricated tested hypotheses; separately reported Bonferroni `M*p` bounds avoid implying an unavailable measured catalog.

| Family | Actually known hypotheses | Declared size | Explicit p=1 placeholders | Rejections at 0.05 |
|---|---:|---:|---:|---:|
| `local_R27_bound10` | 5 | 10 | 5 | 0 |
| `local_R28_bound10` | 10 | 10 | 0 | 10 |
| `local_R29_bound10` | 5 | 10 | 5 | 5 |
| `local_R30_bound10` | 5 | 10 | 5 | 0 |
| `local_R31_bound10` | 5 | 10 | 5 | 0 |
| `local_R32_bound10` | 5 | 10 | 5 | 5 |
| `local_POOLED_R27_R28_R29_R32_bound10` | 5 | 10 | 5 | 5 |
| `new_known143_bound324` | 143 | 324 | 181 | 14 |
| `new_known143_bound500` | 143 | 500 | 357 | 10 |
| `complete_known467_bound467` | 467 | 467 | 0 | 10 |
| `complete_known467_bound500` | 467 | 500 | 33 | 10 |

R28's ten specified signed-rank contrasts pass its local family even though C-p99 is not unanimous. R29's p50/p95/UL/Jain raw p=0.0001220703125 gives scoped324 adjusted p=0.038330078125, but complete-known500 p=0.059814453125. R32's five requested outcomes give complete-known500 adjusted values approximately 0.0151062, 0.0300293 and 0.0449524, depending on the metric. The complete-known500 ten rejections are the five R32 contrasts and five pooled contrasts; no broad R28/R29 treatment acceptance is substituted for them.

The specification's block-count assertions are checked against actual saved p99 pairs:

| Contrast | Claimed favorable blocks | Actual favorable blocks | Worse block IDs | Exact rank p | Exact sign p |
|---|---:|---:|---|---:|---:|
| R28 `iter2` p99 | 12 | 11 | 4 | 0.0009765625 | 0.00634765625 |
| R29 `iter1` p99 | 13 | 12 | 3, 5 | 0.0006103515625 | 0.012939453125 |

All other requested R28/R29/R32 favorable-count assertions match their saved blocks. The claim that every pooled p is below 1e-12 is false for p99: exact rank p is about 3.126388e-12 and its sign p is about 5.100190e-9. Both remain small enough for the stated broad procedures. Sign sensitivity and signed-rank inference are not interchangeable.

The exact calculations are conditional on independent sign-exchangeable/symmetric differences. A common-shift interpretation also requires a stable location model. A pairing ID or a deterministic Williams/AB-BA schedule does not establish these assumptions. A root sensitivity analysis replacing binary subtraction with canonical source-decimal subtraction changes three **non-significant** raw rank values: R28 stock-to-B goodput 0.119140625 to 0.1162109375, R28 B-to-C UL 0.4130859375 to 0.3759765625, and R30 symmetric-to-retry5/3 UL 0.375 to 0.5. No requested favorable count, corrected rejection or promotion outcome changes. The accepted numerical API remains exact conditional on its provided finite float differences; source quantization/tie sensitivity is not hidden.

## Pooled 46-block answer, uncertainty and throughput tradeoffs

The recorded **complete** stock and AF1/FQ2048/FTX1/retry7/4 AP/CPE package IDs match across R27/R28/R29/R32, as do recorded workload, flow count, direction, encryption label, topology and timing-distance context. Missing timing distance and unverified effective radio/cipher state remain unknown. Round IDs are retained in every pair and round-specific results remain available. The pooled result is conditional on cross-round compatibility and exchangeability; it does not prove a homogeneous causal effect or authorize transfer to another workload or link.

| Pooled outcome | Favorable blocks | Exact signed-rank p | Exact sign p | Paired HL shift | Complete-known500 adjusted p |
|---|---:|---:|---:|---:|---:|
| `p50_rtt_ms` | 46/46 | 2.84217094304e-14 | 2.84217094304e-14 | -18.458 | 1.42108547152e-11 |
| `p95_rtt_ms` | 45/46 | 1.42108547152e-13 | 1.33582034323e-12 | -24.5915 | 7.06279479346e-11 |
| `p99_rtt_ms` | 42/46 | 3.12638803734e-12 | 5.10019049216e-09 | -24.512 | 1.55068846652e-09 |
| `ul_goodput_mbps` | 46/46 | 2.84217094304e-14 | 2.84217094304e-14 | 8.7 | 1.42108547152e-11 |
| `jain_fairness` | 46/46 | 2.84217094304e-14 | 2.84217094304e-14 | 0.10735 | 1.42108547152e-11 |

Negative latency shifts favor the treatment; positive UL/Jain shifts favor it. These are shifts of block statistics, not independent ping-level treatment effects. The following are **marginal** exact confidence sets, not simultaneous confidence intervals for all 500 hypotheses. Values are displayed to 12 significant digits; the JSON retains full float endpoints and open/closed flags. The isolated Jain95 atom and its gap are preserved rather than replaced with a misleading interval hull.

| Pooled outcome | Marginal 95% exact set | Marginal 99.9% exact set |
|---|---|---|
| `p50_rtt_ms` | `[-20.174, -16.511]` | `(-21.7235, -15.2235)` |
| `p95_rtt_ms` | `(-28.0625, -20.851]` | `[-30.6475, -18.0225)` |
| `p99_rtt_ms` | `[-28.6135, -19.7495)` | `(-31.4515, -16.2195)` |
| `ul_goodput_mbps` | `[8, 9.35]` | `(7.5, 9.85)` |
| `jain_fairness` | `{0.0997} union [0.0998, 0.11535]` | `(0.09355, 0.12085)` |

For n=4, the minimum nonzero exact two-sided sign-assignment p is 2/16=0.125. Consequently both 95% and 99.9% inversion sets are the entire real line; the requested finite sets cannot be manufactured. R28/R29/R32 and pooled 46 have finite marginal sets at both levels. Raising the confidence level does not eliminate limited experimental replication or unproven independence.

Aggregate goodput remains a separately audited tradeoff, outside the five pooled claims:

| Primary saved package comparison | Total GP paired HL Mbps | p95 paired HL ms | p99 paired HL ms | Raw total-GP rank p |
|---|---:|---:|---:|---:|
| R27 iter2 vs stock | 0.125 | -21.36 | -19.8055 | 1 |
| R28 iter1 vs stock | -0.65 | -29.099 | -29.682 | 0.119140625 |
| R29 iter1 vs stock | -1.2 | -19.206 | -17.6795 | 0.00537109375 |
| R30 iter2 vs stock | -1.15 | -6.95 | -7.0065 | 0.125 |
| R31 iter1 vs stock | -2 | -8.7935 | -6.69675 | 0.25 |
| R32 iter1 vs stock | 0.1 | -24.78975 | -25.43125 | 0.84130859375 |

R31's symmetric package is not throughput-dominant simply because it was labeled KEEP: its saved total/DL paired HL is -2 Mbps versus stock. Its reported 108.25 Mbps divided by the **declared nominal** 20 MHz is 5.4125 goodput bits/s/Hz; that arithmetic is not PHY efficiency, independent RF verification or a portable sector capacity result. No equivalence/noninferiority margin was specified for goodput, and a non-significant test does not establish negligible loss.

![Saved paired WDS blocks and Holm500](../artifacts/autoresearch/waves_yzab_20261024/certified_wds_blocks_and_holm500.svg)

The [standard Matplotlib script](../artifacts/autoresearch/waves_yzab_20261024/wave_ab_make_figure.py) and [figure receipt](../artifacts/autoresearch/waves_yzab_20261024/wave_ab_figure_receipt.json) bind the source analysis and both SVG/PNG artifacts. Each plotted observation is an actual treatment-minus-stock block value; no summary repair or simulation enters the figure.
<!-- stage822a-payload-end -->
