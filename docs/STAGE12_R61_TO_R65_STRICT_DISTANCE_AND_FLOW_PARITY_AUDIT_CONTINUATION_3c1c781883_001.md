<!-- doc-head: STAGE12_R61_TO_R65_STRICT_DISTANCE_AND_FLOW_PARITY_AUDIT.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R61_TO_R65_STRICT_DISTANCE_AND_FLOW_PARITY_AUDIT.md) | Part 1/2
<a id="period-and-carryover-boundary"></a> [Period and carryover boundary](STAGE12_R61_TO_R65_STRICT_DISTANCE_AND_FLOW_PARITY_AUDIT_CONTINUATION_3c1c781883_002.md#period-and-carryover-boundary) | <a id="historical-package-comparisons-and-range-claims"></a> [Historical package comparisons and range claims](STAGE12_R61_TO_R65_STRICT_DISTANCE_AND_FLOW_PARITY_AUDIT_CONTINUATION_3c1c781883_002.md#historical-package-comparisons-and-range-claims) | <a id="enabling-implementation-acceptance-and-reproducibility"></a> [Enabling implementation, acceptance and reproducibility](STAGE12_R61_TO_R65_STRICT_DISTANCE_AND_FLOW_PARITY_AUDIT_CONTINUATION_3c1c781883_002.md#enabling-implementation-acceptance-and-reproducibility)

<!-- stage822a-payload-begin -->

AT is independently reviewed; actual AU selects only observed supported contexts.
All40 saved means are dyadic/zeroULP; all1600 saved probes received.
Declared timing is not measured outdoor/rural range or effective radio proof.
Exact scoped500 and complete known885 remain distinct; no actuation is enabled.


# R61-R65 strict distance and flow parity audit

The frozen evidence supports four qualified positive observed profiles and one important negative. **R61, R62, R64 and R65** each lose less than2% observed mean total goodput and improve p50/p95/p99/UL/Jain in every one of16 matched blocks. **R63** has a small positive observed mean GP change and four unanimous QoE outcomes, but p50 improves only15/16. It therefore **does not meet strict five-outcome unanimity**. Statistical significance, a KEEP label or positive GP cannot create an exception to that rule. These are offline source-bound observations and necessary conditions, not the full AU source/history promotion decision or new physical acceptance.

The [frozen specification](../artifacts/autoresearch/waves_as_to_av_20261024_spec.md), [prespecified contract](../artifacts/autoresearch/waves_as_to_av_20261024/prespecified_contract.json), [AS dataset freeze](../artifacts/autoresearch/waves_as_to_av_20261024/wave_as_dataset_freeze.json), [canonical records](../artifacts/autoresearch/waves_as_to_av_20261024/normalized_r1_to_r65_measurements_20261024.json), [canonical crossed observations](../artifacts/autoresearch/waves_as_to_av_20261024/normalized_r16_to_r65_block_observations_20261024.json) and [AT result](../artifacts/autoresearch/waves_as_to_av_20261024/wave_at_strict_distance_and_flow_analysis.json) bind this report. Code and numerical acceptance, documentary acceptance and controller acceptance remain separate; this report does not accept its own implementation.

## Corpus, source quality and experimental units

The new evidence comprises15 frozen copies: one JSON, TSV and recipe per round. Only those R61-R65 copies and authorized prior offline evidence were read. This task explicitly supersedes the earlier no-R61 boundary; it authorizes no R66+ raw read, recipe execution, device access, SSH, networking, installation or bench/daemon operation.

The cumulative corpus is **230 records:228 primary plus two auxiliary,1276 crossed rows across550 round-scoped matched IDs, and16 separate R17 sequential rows**. The prior220 records,1116 crossed rows and16 sequential rows remain preserved. New evidence is ten arms,160 treatment-by-block rows and80 matched IDs, not160 independent randomized experiments. Each arm contains16 genuine recorded AB/BA blocks and160 RTT probes. All1600 attempted probes were received; saved window and block loss/drop/restoration fields remain zero/zero/true. This is saved-source health evidence, not independent device or physical restoration verification.

All40 GP/DL/UL/Jain arm means agree with their16 block means as exact decimal Fractions and binary64/NumPy values, with zero ULP discrepancy. MAC window counters equal block sums; pooled raw RTT arrays preserve block chronology. Dyadic exactness removes recorded arithmetic discrepancies. It does not establish unbiased measurement, independent sectors, random assignment, an invariant shift or successful washout. No lossful or adverse block is silently dropped.

Six outcomes per round produce30 contrasts,480 outcome-pairs and60 marginal confidence sets. The same80 matched IDs are reused across outcomes. Individual RTT probes and136 Walsh terms per16-pair contrast are derived observations, not extra experimental units. The sixteen sequential R17 rows remain outside genuine crossover pairing.

## Programmed timing declarations and control boundary

The following are strictly typed shared declarations in **payload, iteration and candidate_knobs**. All four fields occur in all three views for each new arm; slot/ACK provenance is `SHARED_PAYLOAD_TREATMENT_KNOBS`. This differs from the prior R57-R60 `ROOT_RECEIPT_ONLY` slot/ACK provenance, which is not rewritten.

| Round | Active flows | Declared distance_m | coverage_class | slot_time_us | ack_timeout_us |
| --- | ---: | ---: | ---: | ---: | ---: |
| R61 | 6 | 3000 | 6 | 27 | 54 |
| R62 | 6 | 6000 | 13 | 48 | 96 |
| R63 | 8 | 100 | 0 | 9 | 18 |
| R64 | 4 | 100 | 0 | 9 | 18 |
| R65 | 6 | 100 | 0 | 9 | 18 |

The observed positive necessary-condition combinations are six-flow at declared100/3000/6000 (newR65/R61/R62, alongside the accepted earlierR60 at100) and four-flow at declared100 only (R64). **Four-flow at3000 or6000 was not measured here.** Eight-flow at declared100 is R63 and fails strict p50 unanimity; no other eight-flow distance cell is established. This is not a full Cartesian flow-by-distance qualification, and no missing combination inherits a result or context.

Original AP/CPE endpoint snapshots omit distance/class/slot/ACK. Normalized context credits the explicit shared declarations rather than pretending those omitted endpoint fields were read back. For R61/R62 the frozen recipe AST contains `apply_r33_state_with_distance` with literal3000/6000 and restoration100; R63-R65 contain no distance-application call. Reading a call as text is neither execution nor proof that its effect reached firmware.

`effective_timing_independently_verified=False` and `physical_distance_verified=False` remain explicit. The specification's words outdoor3000m and rural6000m do not provide independently measured geographic separation or environmental evidence. Those real-range descriptions remain **UNKNOWN**, while the saved timing contexts are usable as explicit offline context labels. No inference of propagation range, GPS sync, TDMA, WMM/EDCA authority or regulatory permission is made. Earlier unknown R50/R55 context remains unknown instead of being filled from later100/class0 data.

## Joint AP/CPE packages

BE values below are AQL low/high microseconds, not TXOP, CWmin/CWmax or AIFS. All targets use AP CoDel8000/40000 microseconds and CPE10000/50000, with AP/CPE fq_quantum256/300bytes, fq_limit2048 and force_tx_status1. Full packages, including non-BE AQL, TSQ, DSCP and unknown fields, remain in the source-bound policy identities. A package comparison does not isolate a single knob.

| Round | AP BE / CPE BE AQL | AP/CPE AQL threshold us | AP/CPE RC threshold | Short/long retry |
| --- | --- | --- | --- | --- |
| R61 | [1520, 3040] / [2100, 4200] | 6080 / 8400 | 24 / 24 | 6/4 |
| R62 | [1520, 3040] / [2100, 4200] | 6080 / 8400 | 24 / 24 | 6/4 |
| R63 | [1520, 3040] / [2100, 4200] | 6080 / 8400 | 24 / 24 | 6/4 |
| R64 | [1520, 3040] / [2100, 4200] | 6080 / 8400 | 24 / 24 | 6/4 |
| R65 | [1520, 3040] / [2100, 4200] | 6080 / 8400 | 22 / 22 | 5/4 |

R61/R63 use the source airtime policy for their declared six-/eight-flow contexts; R62/R64 use their own source airtime package. R65 changes both short retry and RC threshold versus the older R60 package. Therefore neither the R65-vs-R60 comparison nor the earlier retry5/3 comparisons isolate long retry or short retry alone. Declared DSCP steering is not independent proof of effective EF-to-VO mapping.

## All ten saved arm means

Total GP, DL and UL are Mbps; Jain is dimensionless. Every value is formatted from the canonical normalized row using Python `.6f` without repairing the source.

| Round | Arm | Total GP | DL GP | UL GP | Jain |
| --- | --- | ---: | ---: | ---: | ---: |
| R61 | A stock | 104.548828 | 86.742188 | 17.806641 | 0.696960 |
| R61 | B target | 103.231445 | 76.775391 | 26.456055 | 0.807739 |
| R62 | A stock | 95.082031 | 78.918945 | 16.163086 | 0.696655 |
| R62 | B target | 94.294922 | 69.676758 | 24.618164 | 0.813538 |
| R63 | A stock | 104.973633 | 84.856445 | 20.117188 | 0.724487 |
| R63 | B target | 105.027344 | 76.248047 | 28.779297 | 0.829895 |
| R64 | A stock | 106.532227 | 93.625977 | 12.906250 | 0.635315 |
| R64 | B target | 105.895508 | 85.194336 | 20.701172 | 0.729492 |
| R65 | A stock | 105.245117 | 89.268555 | 15.976562 | 0.673584 |
| R65 | B target | 104.050781 | 80.062500 | 23.988281 | 0.774658 |

The following pooled RTT quantiles use canonical Python `.4f`, with each cell A stock to B target in milliseconds. They are not the arithmetic mean of block quantiles or the HL shift of block differences.

| Round | p50 ms A to B | p95 ms A to B | p99 ms A to B |
| --- | ---: | ---: | ---: |
| R61 | 27.7365 to 6.9425 | 46.2777 to 17.7264 | 51.0350 to 27.8940 |
| R62 | 27.2965 to 6.2745 | 47.3927 to 14.2683 | 58.2518 to 23.7384 |
| R63 | 12.0400 to 7.1230 | 54.3759 to 26.1690 | 64.4340 to 33.7415 |
| R64 | 19.5050 to 7.6600 | 37.3292 to 19.9715 | 52.7258 to 23.0616 |
| R65 | 24.3945 to 7.3315 | 45.4724 to 19.2464 | 51.4304 to 29.0071 |

All ten full-precision total-GP literals in the specification match actual source means. All five signed percentage displays match their stated six-decimal rounding, but are not asserted exactly equal to the rational change. All30 specification latency displays match canonical `.4f`. Rounded labels do not replace raw source values in inference or qualification.

## Observed GP preservation and the positive R63 mean

Loss below means100*(stock-target)/stock. Positive loss is adverse; negative loss is an observed gain. The fractions are exact percentages, not ratio fractions that still need multiplying by100.

| Round | Exact GP loss percentage | Observed loss percentage | Preserved stock GP | GP favorable blocks |
| --- | --- | ---: | ---: | ---: |
| R61 | 67450/53529 | 1.260064638% | 98.739935362% | 3/16 |
| R62 | 20150/24341 | 0.827821371% | 99.172178629% | 5/16 |
| R63 | -5500/107493 | -0.051166122% | 100.051166122% | 9/16 |
| R64 | 65200/109089 | 0.597677126% | 99.402322874% | 5/16 |
| R65 | 122300/107771 | 1.134813633% | 98.865186367% | 7/16 |

All five pass the literal observed structural predicate GP loss **<2%**; the unchanged historical operator **<=2%** boundary remains a separate contract. R63's exact mean gain is **5500/107493 percent=0.051166122445182476%**, from104.9736328125 to105.02734375Mbps, with9/16 positive GP blocks. This is a positive descriptive arithmetic mean, not a statistically demonstrated throughput gain. Its exact rank p=.889556884765625, sign p=.803619384765625 and mean-flip p=.903350830078125 all remain nonsignificant. Scoped500 and full885 GP adjusted p-values are1.

R61/R62/R64/R65 retain their adverse GP outcomes. Counts3/5/5/7 favorable blocks do not disappear because the arithmetic mean loss is below2%. R61's unadjusted adverse GP rank p=.006072998046875 becomes1 after the declared broad correction; no equivalence or noninferiority follows either from that correction or from a nonsignificant GP test. All five within-round GP contrasts have adjusted p=1 in the scoped500 and complete885 families. The observed <2% engineering threshold is not a margin-based noninferiority confidence claim.

## Win profiles and the R63 contradiction

Higher total GP/UL/Jain and lower RTT define favorable differences. There are no equal blocks in these contrasts. All29 explicitly stated win-count claims match source; the R61 GP count3/16 is reported because the spec did not state it.

| Round | GP | p50 | p95 | p99 | UL | Jain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R61 | 3/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| R62 | 5/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| R63 | 9/16 | 15/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| R64 | 5/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| R65 | 7/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |

R61/R62/R64/R65 each satisfy five16/16 QoE profiles. R63 has **p5015/16** and p95/p99/UL/Jain16/16. It passes the observed GP-preservation condition but fails strict five-outcome unanimity. The user narrative simultaneously asks strict R63 qualification and states15/16 p50; the latter is confirmed by data. The qualified negative is retained without changing thresholds, inventing an exception mode, transferring a statistic from another round or adding an unrequested controller rule.

For R63p50, exact signed-rank and mean-flip tails are4/65536=.00006103515625; the exact binomial sign tail is34/65536=.000518798828125. Its rank Holm500 q=.029052734375 and complete885 q=.04583740234375 pass .05. **That significance does not create a sixteenth favorable block.** The other24 QoE contrasts are unanimous and have exact rank/sign/mean p=2/65536=.000030517578125 under the sign-exchangeability model. A sign count, rank statistic and arithmetic mean statistic are different tests, not interchangeable interpretations of the same p-value.

AT emits only source-observed necessary profile conditions. AU must still verify external pins, full identities, context, matched units, source health/history and direct statistical gates. A raw source KEEP or a passed necessary-condition record is not actual source-independent AU promotion. The actual AU matrix is reported below; its independent acceptance remains separate from AT and this report.

## Actual AU matrix and observed-context selection

The [actual AU evaluation](../artifacts/autoresearch/waves_as_to_av_20261024/wave_au_evaluation.json) and [AU build receipt](../artifacts/autoresearch/waves_as_to_av_20261024/wave_au_build_receipt.json) contain39 direct comparisons,33 context selectors and14 structural profiles. These are offline evaluations of pinned saved evidence, not39 physical experiments or14 deployed profiles. Explicit queries and round scopes remain in the matrix. Final AU acceptance is governed by its independent review and final campaign seal, not by this report's description of its results.

In `strict_goodput_preservation`, explicit known six-flow declared100 selects historicalR60; newR65 is also directly eligible but does not displace R60 under the existing p95 ranking. Declared3000 selects R61 and declared6000 selects R62. Four-flow declared100 selects R64. These observed combinations do not cover four-flow3000/6000 or every Cartesian flow-by-distance cell. The generic six-flow strict and directional queries remain blocked by context ambiguity; they do not silently assume100. Known6000 directional mode continues to select historicalR49 under the unchanged p95 ranking, rather than automatically replacing it with R62.

R63 strict remains blocked by p5015/16 despite its positive arithmetic GP change and significant rank result. Its known100 eight-flow strict and directional queries are blocked; old unknown-context eight-flow observations do not fill this cell. All new retry fractions increase. The six-flow-only `strict_goodput_AND_lower_retry` selector retains R59; R61/R62/R65 fail its lower-retry predicate. R63/R64 are outside that mode's six-flow eligibility and return no evaluated utility. The structural wrapper's inherited missing-utility GP flag for those unsupported modes is **not a measured GP failure**: their actual observed GP floors remain as reported above. The unchanged all-five strict contract has no p50 exception.

The historical operator GP boundary remains `<=2%`, while the separately named literal structural profile checks `<2%`. Neither engineering boundary is a GP equivalence or noninferiority test. Old strict lower-retry contracts are not relaxed, unknown earlier context is not retrofilled, and no source KEEP string or controller result enables a device action.

## Retry fractions from counters

These ratios are retry events divided by saved TX packets, not PER, uniquely lost packets or A-MPDU subframes. Fractions are derived from summed counts, not an average of block ratios. Every target's fraction increases, even though every target's absolute retry-event numerator decreases.

| Round | Arm | Retry events / TX packets | Ratio as percent |
| --- | --- | ---: | ---: |
| R61 | A stock | 1285 / 634465 | 0.202533% |
| R61 | B target | 1169 / 571212 | 0.204653% |
| R62 | A stock | 1045 / 579009 | 0.180481% |
| R62 | B target | 1003 / 519551 | 0.193051% |
| R63 | A stock | 993 / 629822 | 0.157664% |
| R63 | B target | 934 / 576519 | 0.162007% |
| R64 | A stock | 1247 / 674978 | 0.184747% |
| R64 | B target | 1194 / 621159 | 0.192221% |
| R65 | A stock | 1301 / 653263 | 0.199154% |
| R65 | B target | 1227 / 594227 | 0.206487% |

Reduced absolute retry counts therefore cannot support a lower retry-rate claim. In particular, R65 retry5/4 does not establish a lower fraction against its own stock control. Retry direction is preserved as a diagnostic and Pareto cost, without silently adding or removing it from an existing named strict contract. Zero saved ICMP loss can coexist with additional lower-layer retries. These counters do not identify early A-MPDU drops, TCP CUBIC cwnd or a firmware-control mechanism.

## Exact inference and multiplicity

The [family recipe](../artifacts/autoresearch/waves_as_to_av_20261024/wave_at_family_recipe.json) was frozen before AT numerical computation, after RF collection and operator narrative. It is a retrospective specified analysis, not experimental preregistration. Primary rank30 plus470 explicit unknown p=1 placeholders form scoped500. A separate exact mean-flip30 plus470p1 family is a sensitivity family. Sign tests are diagnostics on the same observations. The prior855 primary hypotheses remain unchanged; the complete known primary scope is**885**, so a complete Holm500 statement is inapplicable. Known885 is not an exhaustive count of all project research tests.

Each contrast uses all65536 sign assignments. Mean-flip enumeration scales exact Fractions of finite binary-float pair differences to a common integer denominator and uses no tail epsilon. Signed rank uses doubled midranks with ties/zeros and is checked against the audited DP engine. Independent source-decimal subtraction sensitivity changes none of the30 rank or mean-flip results. All p-values below are two-sided, and HL is B minus A in outcome units.

<!-- stage822a-payload-end -->
