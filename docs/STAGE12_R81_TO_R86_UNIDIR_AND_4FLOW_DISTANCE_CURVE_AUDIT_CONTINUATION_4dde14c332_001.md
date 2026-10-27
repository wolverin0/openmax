<!-- doc-head: STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT.md) | Part 1/3
<a id="applicable-strict-source-conditions-and-r85-claim"></a> [Applicable strict source conditions and R85 claim](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#applicable-strict-source-conditions-and-r85-claim) | <a id="period-and-carryover-assumptions"></a> [Period and carryover assumptions](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#period-and-carryover-assumptions) | <a id="contextual-packages-not-a-causal-distance-or-af-curve"></a> [Contextual packages, not a causal distance or AF curve](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#contextual-packages-not-a-causal-distance-or-af-curve) | <a id="four-flow-declared-distance-points"></a> [four flow declared distance points](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#four-flow-declared-distance-points) | <a id="six-flow-7500m-distinct-packages"></a> [six flow 7500m distinct packages](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#six-flow-7500m-distinct-packages) | <a id="reproducible-software-evidence-and-authority"></a> [Reproducible software evidence and authority](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#reproducible-software-evidence-and-authority) | <a id="final-integrated-software-acceptance"></a> [Final integrated software acceptance](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_002.md#final-integrated-software-acceptance)

<!-- stage822a-payload-begin -->

Frozen saved evidence: unidirectional DL/UL and bidirectional four/six-flow packages.
38distinct exact contrasts; activeGP aliases total only after both-arm/all-block proof.
Directional Jain/inactive throughput are not inference outcomes; raw values remain.
Declared timing and software checks do not establish physical range, causality or actuation.

# Stage12 R81-R86: direction-aware unidirectional and four-flow distance audit

This analysis answers the source-bound question without treating constant inactive throughput or directional Jain as favorable evidence. R81/R82 each contribute five distinct outcomes: total GP, three RTT quantiles and station retry-event/TX-packet rate. R83/R84/R85/R86 each contribute seven: total GP, three RTT quantiles, UL GP, Jain fairness and retry rate. Active-direction GP is the same hypothesis as total GP only after exact equality and inactive zero are proved in both arms and all blocks; there are38tests, not42or extra alias tests.

The authoritative numerical result is [wave_bj_unidir_and_multidistance_4flow_analysis.json](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_unidir_and_multidistance_4flow_analysis.json), with [source-bound build receipt](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_build_receipt.json), [pre-computation family plan](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_family_and_bootstrap_recipe.json) and [current own implementation freeze](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_implementation_freeze_2.json). The coordinator independently reviews the implementation/report; an author-owned PASS is not independent or physical acceptance. Both requested report filenames contain identical bytes.

## Actual corpus, units and raw descriptives

Canonical counts are272records (270primary+2auxiliary),1948crossed treatment-by-block rows,886round-scoped matched IDs and16separate R17 sequential observations. Twelve new arms add192windows/96matched IDs and1920saved RTT probes. The spec173total is refuted. Sixteen actual matched blocks per round are the units; pings and136derived Walsh averages are not independent trials. No crossround block pairing is performed.

Source-bound raw paired outcomes and declared assumptions were plotted before inference: [paired descriptives](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_paired_descriptives_2.png) and [underlying values/assumptions](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_preinference_descriptives_2.json). The four inapplicable unidirectional panels are labeled rather than fabricated. Every adverse block remains in primary analysis.

Tables use canonical means `.6f` and Python canonical RTT `.4f` displays, without changing underlying source precision or acceptance criteria. GP/DL/UL are Mbps; RTT is ms; Jain is unitless.

| Round | Arm | GP | DL | UL | Raw Jain | Saved mean loss% | Saved drops |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R81 | Stock | 108.562500 | 108.562500 | 0.000000 | 0.500000 | 0.0 | 0 |
| R81 | Target | 105.812500 | 105.812500 | 0.000000 | 0.500000 | 0.0 | 0 |
| R82 | Stock | 66.493164 | 0.000000 | 66.493164 | 0.500000 | 0.0 | 0 |
| R82 | Target | 66.231445 | 0.000000 | 66.231445 | 0.500000 | 0.0 | 0 |
| R83 | Stock | 104.513672 | 92.531250 | 11.982422 | 0.627319 | 0.0 | 0 |
| R83 | Target | 103.531250 | 83.025391 | 20.505859 | 0.732605 | 0.0 | 0 |
| R84 | Stock | 95.501953 | 83.875000 | 11.626953 | 0.636230 | 0.0 | 0 |
| R84 | Target | 94.349609 | 75.199219 | 19.150391 | 0.739075 | 0.0 | 0 |
| R85 | Stock | 91.875000 | 76.693359 | 15.181641 | 0.690186 | 0.0 | 0 |
| R85 | Target | 90.446289 | 69.225586 | 21.220703 | 0.779480 | 0.0 | 0 |
| R86 | Stock | 87.041992 | 75.664062 | 11.377930 | 0.647217 | 0.0 | 0 |
| R86 | Target | 86.012695 | 68.225586 | 17.787109 | 0.743713 | 0.0 | 0 |

| Round | Stock p50 | Target p50 | Stock p95 | Target p95 | Stock p99 | Target p99 |
| --- | --- | --- | --- | --- | --- | --- |
| R81 | 17.1045 | 8.5105 | 33.6601 | 24.0693 | 42.7934 | 29.9641 |
| R82 | 6.4630 | 4.7040 | 15.8351 | 9.1558 | 22.4415 | 10.6355 |
| R83 | 19.7340 | 6.4165 | 40.8560 | 19.5319 | 53.8050 | 23.6425 |
| R84 | 20.1650 | 6.9485 | 39.6937 | 16.1647 | 47.7989 | 19.7489 |
| R85 | 26.7820 | 7.0525 | 47.9007 | 20.3104 | 54.8207 | 24.0878 |
| R86 | 22.1595 | 5.3275 | 41.6517 | 14.5426 | 48.9123 | 15.9234 |

Source checks:48exact Fraction means=True,48zero-ULP means=True, all12arms160received=True, all12chronological RTT pools=True, all12MAC pools equal block sums=True. These values report the actual audit; false source claims would remain false rather than be repaired by tolerance.

Saved window health and actual per-block health are different provenance. R81/R82 raw blocks omit an `observation` dictionary and per-block restoration/station-drop assertions; top-level block RTT/loss/counters are retained. Those missing health facts remain unknown, not inherited from a healthy arm or invented by this statistical audit. Source window restoration/loss/drops are shown above; this is not a new device readback or a controller eligibility decision.

## Direction aliases, source period mapping and recipe evidence

| Round | Regime | Flows | Declared m | Class | Slot/ACK us |
| --- | --- | --- | --- | --- | --- |
| R81 | unidir_dl_2flow | 2 | 100 | 0 | 9/18 |
| R82 | unidir_ul_2flow | 2 | 100 | 0 | 9/18 |
| R83 | bidir_4flow | 4 | 3000 | 6 | 27/54 |
| R84 | bidir_4flow | 4 | 6000 | 13 | 48/96 |
| R85 | bidir_6flow | 6 | 7500 | 16 | 57/114 |
| R86 | bidir_4flow | 4 | 9000 | 20 | 69/138 |

R81: active `dl_goodput_mbps` equals total GP in both arms and all32source blocks, while inactive `ul_goodput_mbps` is explicit zero. The canonical representation is independently checked against those same arm/block identities. GP is one hypothesis with a semantic alias, not two p-values. Raw directional Jain and inactive-direction numbers are retained but are inapplicable to QoE inference.

R82: active `ul_goodput_mbps` equals total GP in both arms and all32source blocks, while inactive `dl_goodput_mbps` is explicit zero. The canonical representation is independently checked against those same arm/block identities. GP is one hypothesis with a semantic alias, not two p-values. Raw directional Jain and inactive-direction numbers are retained but are inapplicable to QoE inference.

The R81/R82 frozen recipes contain direct window command AST with `-P 2`; only R82 additionally has `-R`, and neither uses `--bidir` for that window. No recipe is imported or executed. Named helper calls and literal coverage/reset commands remain source declarations, with execution/effective firmware/physical timing proof false. The R83/R84 four-flow class6/13 contexts must not be relabeled as the historical six-flow coverage aliases.

R81/R82 raw periods are `step_in_block`1/2. BI preserves the literal and field name and maps to canonical `crossover_step`0/1 by exact subtraction of one only in those two rounds. Every original block_index is retained. BJ checks all source-to-canonical roundtrips, rejects conflicting/mixed/malformed period fields and never generates pair IDs from list order. R83-R86 retain their explicit raw0/1 crossover_step.

Distance100/3000/6000/7500/9000 and slot/ACK/class are saved shared declarations, not geographic separation or independently effective timing. Class0/6/13/16/20 labels correspond to saved9/18,27/54,48/96,57/114,69/138microseconds. Recipe text is not execution or readback, and no historical unknown context is filled from a class default.

## Station retry-event rate

Each block rate is saved retry-events delta divided by its positive typed TX-packet denominator on declared AP WDS `phy0-ap0.sta1`. Missing/zero denominators are unavailable and cannot be imputed or silently removed. The declared interface is recipe provenance, not independent AP/peer hardware identity. Retry events per packet are not PER, unique packet loss or subframe failure probability. Arm-summed rate and the paired per-block rate are distinct estimands.

| Round | Arm | TX packets | Retry events | Exact aggregate fraction | Rate% |
| --- | --- | --- | --- | --- | --- |
| R81 | Stock | 763414 | 1803 | 1803/763414 | 0.236176 |
| R81 | Target | 740915 | 1815 | 363/148183 | 0.244967 |
| R82 | Stock | 65644 | 0 | 0 | 0.000000 |
| R82 | Target | 64952 | 0 | 0 | 0.000000 |
| R83 | Stock | 666632 | 1632 | 204/83329 | 0.244813 |
| R83 | Target | 604538 | 1413 | 1413/604538 | 0.233732 |
| R84 | Stock | 606121 | 1295 | 1295/606121 | 0.213654 |
| R84 | Target | 549470 | 1238 | 619/274735 | 0.225308 |
| R85 | Stock | 562338 | 1448 | 724/281169 | 0.257496 |
| R85 | Target | 516046 | 1220 | 610/258023 | 0.236413 |
| R86 | Stock | 547861 | 1287 | 1287/547861 | 0.234914 |
| R86 | Target | 499247 | 1226 | 1226/499247 | 0.245570 |

## Exact tests, family scope and paired BCa

Each of38contrasts retains16matched differences and all65536sign assignments. Two-sided Wilcoxon signed-rank, binomial sign and exact integer-sum mean sign flips are distinct statistics. Signed-rank uses midranks for ties and excludes zeros; integer mean sums are derived from Fraction.from_float differences without a tail tolerance. Exact source-decimal or counter-rational sensitivity is retained separately to expose precision/tie differences.

The primary scoped family contains38known rank hypotheses+462unknown p1 tests, bound500. A separately declared mean-flip38+462family is sensitivity only. Prior980accepted rank hypotheses remain unchanged, so complete known enumerated rank scope is1018, not500 and not every project research test. No inapplicable Jain/inactive-direction test or duplicate GP alias is added to the family.

| Round | Metric | Wins/16 | HL | Rank p | Sign p | Mean p | Rank Holm500 | Rank Holm1018 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R81 | goodput_rx_mbps | 0 | -3 | 6.103515625e-05 | 6.103515625e-05 | 6.103515625e-05 | 0.02935791016 | 0.04937744141 |
| R81 | p50_rtt_ms | 16 | -8.563625 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R81 | p95_rtt_ms | 15 | -10.802475 | 0.0001525878906 | 0.0005187988281 | 0.0001220703125 | 0.07278442383 | 0.1197814941 |
| R81 | p99_rtt_ms | 13 | -10.5379175 | 0.0005798339844 | 0.02127075195 | 0.0007019042969 | 0.2754211426 | 0.4348754883 |
| R81 | wds_mac_retry_rate | 9 | 5.632924474e-05 | 0.7057189941 | 0.8036193848 | 0.4945678711 | 1 | 1 |
| R82 | goodput_rx_mbps | 6 | -0.375 | 0.638671875 | 0.6072387695 | 0.6336669922 | 1 | 1 |
| R82 | p50_rtt_ms | 15 | -2.242625 | 6.103515625e-05 | 0.0005187988281 | 6.103515625e-05 | 0.02935791016 | 0.04937744141 |
| R82 | p95_rtt_ms | 14 | -4.686175 | 0.0004272460938 | 0.004180908203 | 0.0003356933594 | 0.2033691406 | 0.3302612305 |
| R82 | p99_rtt_ms | 12 | -4.992605 | 0.001312255859 | 0.07681274414 | 0.0008544921875 | 0.6220092773 | 0.9697570801 |
| R82 | wds_mac_retry_rate | 0 | 0 | 1 | 1 | 1 | 1 | 1 |
| R83 | goodput_rx_mbps | 3 | -1.06640625 | 0.01538085938 | 0.02127075195 | 0.08386230469 | 1 | 1 |
| R83 | p50_rtt_ms | 16 | -12.513125 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R83 | p95_rtt_ms | 15 | -18.3235875 | 6.103515625e-05 | 0.0005187988281 | 6.103515625e-05 | 0.02935791016 | 0.04937744141 |
| R83 | p99_rtt_ms | 15 | -20.160355 | 9.155273438e-05 | 0.0005187988281 | 9.155273438e-05 | 0.04376220703 | 0.07269287109 |
| R83 | ul_goodput_mbps | 16 | 8.62890625 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R83 | jain_fairness | 16 | 0.1059570312 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R83 | wds_mac_retry_rate | 9 | -9.534721028e-05 | 0.4954223633 | 0.8036193848 | 0.5458374023 | 1 | 1 |
| R84 | goodput_rx_mbps | 3 | -1.34765625 | 0.01327514648 | 0.02127075195 | 0.009429931641 | 1 | 1 |
| R84 | p50_rtt_ms | 16 | -14.247 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R84 | p95_rtt_ms | 16 | -18.4719875 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R84 | p99_rtt_ms | 16 | -19.3527825 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R84 | ul_goodput_mbps | 16 | 7.625 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R84 | jain_fairness | 16 | 0.1040039062 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R84 | wds_mac_retry_rate | 7 | 0.0001391074636 | 0.4637451172 | 0.8036193848 | 0.2476196289 | 1 | 1 |
| R85 | goodput_rx_mbps | 4 | -1.41796875 | 0.02667236328 | 0.1184692383 | 0.07025146484 | 1 | 1 |
| R85 | p50_rtt_ms | 16 | -19.547375 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R85 | p95_rtt_ms | 16 | -28.31115 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R85 | p99_rtt_ms | 16 | -27.756355 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R85 | ul_goodput_mbps | 16 | 6.12890625 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R85 | jain_fairness | 16 | 0.09301757812 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R85 | wds_mac_retry_rate | 10 | -0.000228625369 | 0.3483886719 | 0.454498291 | 0.4809570312 | 1 | 1 |
| R86 | goodput_rx_mbps | 6 | -1.0390625 | 0.07391357422 | 0.454498291 | 0.08090209961 | 1 | 1 |
| R86 | p50_rtt_ms | 16 | -15.9855 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R86 | p95_rtt_ms | 16 | -25.193575 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R86 | p99_rtt_ms | 16 | -27.2349675 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R86 | ul_goodput_mbps | 16 | 6.22265625 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R86 | jain_fairness | 16 | 0.09423828125 | 3.051757812e-05 | 3.051757812e-05 | 3.051757812e-05 | 0.01525878906 | 0.03060913086 |
| R86 | wds_mac_retry_rate | 8 | 0.0001865222451 | 0.5618896484 | 1 | 0.6298217773 | 1 | 1 |

Exact95%/99.9% confidence sets invert the conditional signed-rank test and preserve endpoint inclusion, component unions and unboundedness. They are marginal shift/symmetry acceptance sets, not simultaneous500/1018-test intervals, not causal effects and not distribution-free guarantees from merely counterbalanced blocks.

<!-- stage822a-payload-end -->
