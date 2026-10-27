<!-- doc-head: R57-R60 offline retry64, goodput parity and exact 16-block audit -->
R59/R60 nearly preserve observed mean GP; neither establishes equivalence or noninferiority.
R59 lowers retries with 15/16 p99 wins; R60 has five 16/16 wins but higher retries.
Scoped Holm500, full known855 and unresolved carryover assumptions remain distinct.
Offline report; independent acceptance and selector evaluation are separate evidence.
<!-- /doc-head -->

# R57-R60 retry64, goodput parity and 16-of-16 audit

This engineering report describes four saved LAP120-Loco195 crossover rounds. It makes no new radio measurement, deployment, controller actuation or Stage4/custom-MAC acceptance claim. **CONFIRMED within the frozen source:** R59 loses only about .01956% of mean total goodput and lowers the saved retry-events/packet ratio; R60 loses about .05840%, improves five QoE metrics in every matched block, and raises the retry ratio. **UNKNOWN:** equivalence/noninferiority, separated treatment-versus-carryover effects, effective timing authority and physical range. **HYPOTHESIS_NOT_DEMONSTRATED:** the proposed R58 long-retry to early A-MPDU loss to AP CUBIC-cwnd mechanism.

The authoritative inputs are the [AO dataset freeze](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ao_dataset_freeze.json), [normalized records](../artifacts/autoresearch/waves_ao_to_ar_20261024/normalized_r1_to_r60_measurements_20261024.json), [normalized block observations](../artifacts/autoresearch/waves_ao_to_ar_20261024/normalized_r16_to_r60_block_observations_20261024.json), [AP result](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_retry64_goodput_parity_analysis.json) and [AP build receipt](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_build_receipt.json). AP's implementation and this report require separate independent acceptance; passing the local tests does not supply that acceptance.

## Evidence and experimental unit

Twelve new frozen files comprise a JSON receipt, TSV summary and recipe per round. Recipes were read as text only. Each round has two arms and 16 genuine matched block IDs, with eight AB and eight BA sequences. Across R57-R60 this is eight arms, 128 treatment-by-block rows and **64 matched units**. There are six outcomes per round: total GP, p50, p95, p99, UL GP and Jain fairness. Thus 24 contrasts reuse those units to produce 384 outcome-pairs and 48 marginal confidence sets; these are not 384 separate experiments.

Each arm saves 160 attempted and 160 received RTT probes, for 1,280/1,280 overall. Every saved arm and block reports zero packet loss, zero station drops and restoration true. MAC block sums match window counts and the raw RTT chronology matches saved block arrays. These are source-consistency checks, not a new independent inspection of devices or restoration. All eight arms pass the four literal rational mean checks (GP/DL/UL/Jain), NumPy means and zero-ULP checks. Exact dyadic arithmetic eliminates those recorded-summary inconsistencies; it does not prove unbiased sampling, independence, randomization or radio stability beyond the saved observations.

The cumulative AO dataset contains 220 records (218 primary plus two auxiliary), 1,116 crossed rows, 470 matched IDs and 16 separate sequential R17 observations. The sequential rows are not promoted into crossover pairs. Old R1-R56 records and crossed prefixes remain preserved by the AO interfaces; no historical file was rewritten for this analysis.

## Declared context and actual package identity

All four new payloads explicitly save coverage class 0, distance 100, slot time 9 microseconds and ACK timeout 18 microseconds. Iteration/candidate distance and coverage declarations agree; available inner slot/ACK declarations also agree. Slot/ACK provenance is `ROOT_RECEIPT_ONLY`, with `effective_timing_independently_verified=False`. The original endpoint-state objects omit distance, and the frozen recipes contain no distance-keyword application call. These values are **saved declarations**, not readback proof, measured geographic separation or a demonstrated effective timing change. Historical R50's unknown distance/coverage remains unknown; it is never filled with the later 100/0 declarations.

The following target fields summarize the package, not an isolated retry intervention. BE values are AQL low/high microseconds, not TXOP/CWmin/CWmax/AIFS. The complete AP+CPE identity, including DSCP/queue/TSQ/FTX fields and optional unknowns, remains in the result.

| Round | Flows | Short/long retry | AP BE / CPE BE | AP/CPE AQL threshold microseconds | AP/CPE RC threshold | AP CoDel target/interval microseconds ; CPE |
| --- | ---: | --- | --- | --- | --- | --- |
| R57 | 8 | 5/3 | [1500, 3000] / [2100, 4200] | 6000 / 8400 | 28 / 28 | 10000/50000 ; 12000/60000 |
| R58 | 6 | 5/3 | [1750, 3500] / [2100, 4200] | 7000 / 8400 | 28 / 28 | 10000/50000 ; 12000/60000 |
| R59 | 6 | 6/4 | [1550, 3100] / [2100, 4200] | 6200 / 8400 | 24 / 24 | 10000/50000 ; 12000/60000 |
| R60 | 6 | 6/4 | [1520, 3040] / [2100, 4200] | 6080 / 8400 | 24 / 24 | 8000/40000 ; 10000/50000 |

All target rows use force_tx_status=1 and fq_limit=2048; AP/CPE fq_quantum is 256/300 bytes. Their endpoint asymmetry is intentional source identity. R59's CPE CoDel is **12000/60000 microseconds**, not the AP's 10000/50000; R60's CPE is **10000/50000**, not the AP's 8000/40000. Shared metadata or a marketing label cannot collapse these joint packages. DSCP steering metadata is not independent proof of effective EF-to-VO mapping.

## Saved arm means and pooled RTT quantiles

GP, DL and UL are Mbps; Jain is dimensionless. These display values are formatted directly from canonical normalized rows with Python `.6f`.

| Round | Arm | Total GP | DL GP | UL GP | Jain |
| --- | --- | ---: | ---: | ---: | ---: |
| R57 | A stock | 105.024414 | 85.674805 | 19.349609 | 0.714905 |
| R57 | B target | 99.201172 | 70.343750 | 28.857422 | 0.850830 |
| R58 | A stock | 105.181641 | 88.736328 | 16.445312 | 0.679321 |
| R58 | B target | 94.413086 | 70.186523 | 24.226562 | 0.808533 |
| R59 | A stock | 104.850586 | 88.293945 | 16.556641 | 0.681274 |
| R59 | B target | 104.830078 | 79.548828 | 25.281250 | 0.788147 |
| R60 | A stock | 105.356445 | 88.919922 | 16.436523 | 0.678772 |
| R60 | B target | 105.294922 | 80.058594 | 25.236328 | 0.786621 |

The next table uses canonical pooled RTT quantiles, formatted with Python `.4f`; each cell is A to B in milliseconds. A pooled quantile difference is not the mean or Hodges-Lehmann (HL) shift of 16 block quantiles.

| Round | p50 ms A to B | p95 ms A to B | p99 ms A to B |
| --- | ---: | ---: | ---: |
| R57 | 10.1015 to 7.1775 | 59.9739 to 21.7920 | 76.2034 to 34.7802 |
| R58 | 25.4815 to 6.7165 | 45.9721 to 20.2304 | 59.4287 to 32.6171 |
| R59 | 25.8510 to 7.1525 | 48.2084 to 19.8669 | 58.0531 to 40.2440 |
| R60 | 25.9935 to 7.0930 | 48.5614 to 18.7124 | 56.3697 to 25.5220 |

## Favorable blocks and the 16/16 claims

Higher GP/UL/Jain and lower RTT define a favorable block; all adverse blocks remain included. There are no equal blocks in these 24 contrasts. All 22 explicitly stated block-count claims agree with source blocks; R57/R58 GP had no explicit count claim and is reported rather than inferred.

| Round | GP | p50 | p95 | p99 | UL | Jain |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| R57 | 0/16 | 15/16 | 15/16 | 15/16 | 16/16 | 16/16 |
| R58 | 0/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |
| R59 | 9/16 | 16/16 | 16/16 | 15/16 | 16/16 | 16/16 |
| R60 | 11/16 | 16/16 | 16/16 | 16/16 | 16/16 | 16/16 |

R59 has four unanimous QoE outcomes and one p99 reversal. R60 has five unanimous QoE outcomes. R57 has three latency reversals, one for each RTT quantile, while R58 has none. Favorable counts alone ignore magnitude: R59 has 9/16 positive GP blocks and R60 has 11/16, yet their aggregate mean GP changes are both negative. Sixteen favorable signs yield an exact two-sided sign p=2/65536=.000030517578125 under the independent sign-exchangeability model; this is not a guaranteed physical repeatability probability.

## Near parity and retries are separate engineering criteria

For R59, mean GP changes from 104.8505859375 to 104.830078125 Mbps, a difference of minus 21/1024 Mbps. The exact loss percentage is **700/35789%=0.01955908239962%**, so the literal less-than-.02% claim passes. Preservation is **3578200/35789%=99.98044091760038%**. For R60, 105.3564453125 to 105.294921875 Mbps gives minus 63/1024 Mbps and **1260/21577%=0.05839551374148%** loss; preservation is **2156440/21577%=99.94160448625851%**. Both pass an observed <=2% GP-loss threshold. Neither produces a statistical equivalence or noninferiority result: no margin-based equivalence/noninferiority test or confidence bound is being claimed.

R59 GP exact rank p=.99139404296875, sign p=.803619384765625 and mean-flip p=.96356201171875. R60 gives rank p=.811126708984375, sign p=.210113525390625 and mean-flip p=.90447998046875. These nonsignificant tests do not establish GP equality. Positive HL shifts of .00390625 and .25 Mbps respectively also do not override the negative arithmetic mean changes; the estimands differ.

The following ratios use **saved retry events divided by saved TX packets**, not PER or uniquely lost packets. Fractions are computed from summed counts, not averages of per-block ratios. Percentages are displayed to six decimals.

| Round | Arm | Retry events / TX packets | Ratio as percent |
| --- | --- | ---: | ---: |
| R57 | A stock | 1088 / 635900 | 0.171096% |
| R57 | B target | 833 / 536701 | 0.155207% |
| R58 | A stock | 839 / 650510 | 0.128976% |
| R58 | B target | 760 / 527038 | 0.144202% |
| R59 | A stock | 1243 / 646204 | 0.192354% |
| R59 | B target | 1119 / 592452 | 0.188876% |
| R60 | A stock | 1168 / 651152 | 0.179374% |
| R60 | B target | 1242 / 595618 | 0.208523% |

R57 and R59 decrease this ratio. R58 and R60 increase it. For example, R59 uses 1243/646204 to 1119/592452, whereas R60 uses 1168/651152 to 1242/595618. Zero ICMP loss can coexist with increased MAC retries. No count here identifies A-MPDU subframe loss, retry exhaustion or a TCP congestion-control trajectory.

## Exact inference, multiplicity and tail exceptions

The [family recipe](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_family_recipe.json) was frozen before AP outcome computation, after data collection. This is a retrospective specified analysis, not experimental preregistration. The primary family contains 24 exact signed-rank tests plus 476 explicit p=1 placeholders for scoped500 sensitivity. The separate mean-flip family has its own 24 tests plus 476 placeholders. Binomial sign tests are diagnostics on the same observations, not extra independent experiments. The complete **known enumerated** crossover scope contains 831 prior hypotheses plus these 24 = **855**; a complete Holm500 claim is therefore inapplicable. Known855 does not mean every research hypothesis in the entire project is enumerated.

For each contrast, all 65,536 sign assignments are enumerated. Rank uses doubled midranks with ties/zeros; mean-flip uses exact integer signed sums of the supplied finite binary-float pair differences, without a floating tail tolerance. Source-decimal subtraction sensitivity changes none of these 24 rank/mean conclusions. All p-values below are two-sided. HL is B minus A in the metric's units; negative RTT HL is favorable. Holm values apply to the rank test, not to the sign or mean test.

| Round | Metric | HL B minus A | Exact rank p | Scoped Holm500 | Complete known Holm855 |
| --- | --- | ---: | ---: | ---: | ---: |
| R57 | GP | -5.74609375 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R57 | p50 | -9.94512500 | 6.103515625e-05 | 0.0294189453125 | 0.0454711914062 |
| R57 | p95 | -29.60736250 | 6.103515625e-05 | 0.0294189453125 | 0.0454711914062 |
| R57 | p99 | -29.50428750 | 0.000213623046875 | 0.102325439453 | 0.155944824219 |
| R57 | UL | 9.52734375 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R57 | Jain | 0.13623047 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R58 | GP | -10.29296875 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R58 | p50 | -19.69162500 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R58 | p95 | -25.58985000 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R58 | p99 | -26.53952000 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R58 | UL | 7.72656250 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R58 | Jain | 0.12744141 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R59 | GP | 0.00390625 | 0.991394042969 | 1 | 1 |
| R59 | p50 | -18.14537500 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R59 | p95 | -25.05387500 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R59 | p99 | -26.19638250 | 9.1552734375e-05 | 0.0439453125 | 0.0676574707031 |
| R59 | UL | 8.65625000 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R59 | Jain | 0.10644531 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R60 | GP | 0.25000000 | 0.811126708984 | 1 | 1 |
| R60 | p50 | -19.77150000 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R60 | p95 | -28.29435000 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R60 | p99 | -29.24369750 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R60 | UL | 8.64843750 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |
| R60 | Jain | 0.10571289 | 3.0517578125e-05 | 0.0152587890625 | 0.025634765625 |

R57 p99 is a material exception: 15/16 favorable blocks give rank **14/65536**, sign **34/65536** and mean **10/65536**. Rank Holm500 **.102325439453125** fails .05. R59 p99 also has 15/16 favorable blocks, but rank and mean are **6/65536** and sign remains **34/65536**. Its rank Holm500 **.0439453125** passes .05; complete known855 **.067657470703125** does not. Neither a favorable HL nor the scoped significance turns 15/16 into 16/16. R57 p50/p95 rank p=4/65536 and scoped q=.0294189453125, distinct from their sign p=34/65536. All unanimous outcomes have rank q=.0152587890625 in scoped500; an adverse unanimous GP difference is significant in the adverse direction, not a throughput gain.

The result retains exact 95% and 99.9% marginal Walsh signed-rank acceptance sets, with endpoint conventions, possible punctures and components. They are not silently replaced by a connected hull, and are not simultaneous 500- or 855-test intervals. The [methods](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_methods.md) explain the conditional symmetry/shift and independent-block assumptions. No confidence statement treats 1,280 RTT probes as 1,280 independent crossover trials.

## Period balance and unresolved carryover

All four saved schedules conform to their planned 32 positions, with eight AB and eight BA blocks. The full block-fixed-effect + period + current-treatment + lag-treatment matrix has **rank 18 for 19 columns** in every round. Current and lag effects are not separately estimable. Schedule balance is not random assignment or washout verification.

The audit additionally reports an identified restricted block + period + current-treatment model, rank 18/18, under the named assumption of **no differential carryover or unmodeled block-by-period response**. Its point estimates are descriptive conditional estimates. Raw-difference sign-flip p-values are not relabeled as nuisance-adjusted or separated causal p-values. A changed joint queue/retry/TSQ package does not identify the effect of an individual hook.

## Historical comparisons and R58 mechanism boundary

R57 and R47 are both labeled bidirectional eight-flow, but their target packages differ. R47 target GP/DL/UL is 95.375977/62.807617/32.568359 Mbps; R57 is 99.201172/70.343750/28.857422. R47 target p99 is 28.8927 ms versus R57 34.7802 ms. R57 has larger BE AQL and changed non-BE limits, thresholds, CoDel and TSQ fields; R47 timing context is unknown while R57 records 0/100/9/18 declarations. This is a descriptive tradeoff, not evidence that changing BE alone improved GP or that R57 dominates R47.

R50 target GP/DL/UL is 107.682617/81.702148/25.980469 Mbps, compared with the R59/R60 table above. R50 target p50/p95/p99 is 7.7650/24.4283/31.6652 ms. R59 has lower p95 but higher p99 than that historical target; R60 has lower p95 and p99. R50 uses retry7/4 and RC28; R59/R60 use retry6/4 and RC24, alongside other queue/TSQ changes. The old unknown timing context is not a matched control. No old/new pairing, cross-round mechanism p-value, universal Pareto dominance or physical range gain follows from these values.

The R58 hypothesis is that lowering long retry 4 to 3 causes earlier A-MPDU subframe loss, which reduces AP CUBIC cwnd and DL goodput. The frozen R58 receipt has aggregate GP/DL/UL, RTT, MAC retry counts, retransmits and health; the audit identifies **no direct named A-MPDU-subframe/drop or CUBIC/cwnd trajectory field**. This limited field search is not proof that all possible instrumentation is absent.

The historical R50 to R51 comparison changes **both short and long retry on both endpoints**. R50 to R58 also changes AP BE AQL, AQL threshold, TSQ limits and declared timing context; R51 to R58 changes queue/TSQ/context while retaining retry5/3. These are not isolated long-retry controls. Aggregate lossless pings or count-derived retry fractions cannot identify early subframe dropping or congestion-control causality. The mechanism remains **HYPOTHESIS_NOT_DEMONSTRATED**, without a new RF experiment or target command being requested by this report.

## Selector contracts and auxiliary models

The [prespecified contract](../artifacts/autoresearch/waves_ao_to_ar_20261024/prespecified_contract.json) distinguishes three new operator Pareto contracts from legacy selector rules. They share bound provenance, identity, context, healthy control and target, exact dyadic mean/ULP consistency and direct statistical checks. Retry is an explicit diagnostic/Pareto dimension unless the named contract requires its reduction.

- `strict_goodput_preservation`: observed GP loss <=2% plus all five QoE outcomes favorable in 16/16 blocks and the common direct statistical gates.
- `directional_latency_ul_dominance`: observed GP loss <=15%, UL increase relative to its same-round control >=40%, all five unanimous QoE outcomes and common gates; it is not total-GP noninferiority.
- `strict_goodput_AND_lower_retry`: recorded bidirectional six-flow context only; observed GP loss <=2%, strictly lower count-derived retry fraction, unanimous **p50, p95, UL and Jain**, with common direct statistical requirements. It exposes p99 separately and does not silently require p99 unanimity.

The third contract is why R59's four unanimous outcomes and lower retries are meaningfully different from R60's five unanimous outcomes and higher retries. Existing legacy strict rules retaining all five QoE outcomes are not rewritten. The actual [AQ matrix](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_aq_evaluation.json), bound by [build efb3335f](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_aq_build_receipt.json), contains 18 direct comparisons, 30 context selectors and four structural profiles. Source queries and their explicit round scopes are retained in that JSON, rather than assumed to span every historical round.

For the declared distance100/class0 bidirectional six-flow context, the actual offline selector chooses **R60** under `strict_goodput_preservation` and `directional_latency_ul_dominance`, and **R59** under `strict_goodput_AND_lower_retry`. R59's strict-all-five structural profile is BLOCKED by `NOT_16_OF_16_FAVORABLE_p99_rtt_ms`; its four-outcome retry-preserving profile is eligible. R60's strict-all-five profile is eligible, while its retry-preserving profile is BLOCKED by `TARGET_MAC_RETRY_FRACTION_NOT_LOWER`. These different outcomes follow distinct named contracts; none rescues R59 as unanimous-five or treats R60 retries as reduced.

For the four-outcome contract, p99 is always exposed as source-checked wins/HL/exact rank/Holm evidence, or explicitly UNKNOWN if those checks cannot complete. The p99 diagnostic is not a hidden four-metric-profile veto. A result's offline eligibility is not hardware action, physical qualification, total-GP noninferiority or source-independent acceptance. AQ's separate final independent review and final seal govern its acceptance; this report records the actual matrix without pre-accepting it.

AO's frozen auxiliary model build reports 117 supported validation windows and 39 predicted folds, with three unsupported and eight no-support folds. Reported GP/p95/p99 RMSE is 13.2450/14.1085/16.8323, versus mean-baseline 13.0564/14.6702/17.4149: **GP remains worse than baseline**. It reports 16 disabled observed-only proposals and 47 empirical-frontier rows. These enabling outputs, grouped support limits and a corrected list/tuple parser do not validate a physical optimum or replace the direct paired audit. The [AO model freeze](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ao_models_freeze.json) and [build](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ao_models_build_receipt.json) are independently accepted **PASS_WITH_LIMITS** by [review 7a60932e](../artifacts/autoresearch/waves_ao_to_ar_20261024/review_wave_ao.json). That review reuses 139 unchanged hash-bound owner tests and adds fresh byte-identical current/historical dataset replays, 117 prediction reconstructions, list/tuple invariance, leakage/context/quarantine checks and bundle tamper rejection. It accepts the offline enabling implementation with those limits, not wireless improvement or the report author's separate AP statistical implementation.

## Reproducibility and remaining limits

AP source/tests are frozen with [33 passing focused tests](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_focused_tests_1.json), no failures or skips, and [one successful actual CLI execution](../artifacts/autoresearch/waves_ao_to_ar_20261024/wave_ap_actual_run_1.json). Python 3.12.4, NumPy 1.26.4 and SciPy 1.17.1 are the recorded local versions. No unchanged broad suite was rerun by the report author. The family recipe, original inputs, exact results and negative outcomes remain immutable. Local scientific-skill guidance was used offline; its bibliographic entries were not verified online.

The important open boundaries are effective runtime timing/WMM authority, independence and carryover, genuine mechanism telemetry, context transfer, statistical GP noninferiority and representative-sector generalization. This source-bound offline audit neither closes Stage4 nor claims production qualification, GPS/TDMA behavior, increased physical range or a causal retry-to-CUBIC mechanism. Root retains independent report acceptance, AQ final review/sealing and integration; the actual AQ matrix above does not authorize a device action.
