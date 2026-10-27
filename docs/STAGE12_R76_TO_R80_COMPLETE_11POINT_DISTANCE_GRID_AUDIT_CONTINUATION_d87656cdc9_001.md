<!-- doc-head: STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md continuation 1 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT.md) | Part 1/3
<a id="gp-unanimity-and-source-narrative-audit"></a> [GP, unanimity and source narrative audit](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT_CONTINUATION_d87656cdc9_002.md#gp-unanimity-and-source-narrative-audit) | <a id="period-sequence-and-r77-block14"></a> [Period, sequence and R77 block14](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT_CONTINUATION_d87656cdc9_002.md#period-sequence-and-r77-block14) | <a id="eleven-declared-contexts-observed-workload-coverage-and-af-comparison"></a> [Eleven declared contexts, observed workload coverage and AF comparison](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT_CONTINUATION_d87656cdc9_002.md#eleven-declared-contexts-observed-workload-coverage-and-af-comparison) | <a id="implementation-validation-and-authority-limits"></a> [Implementation, validation and authority limits](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT_CONTINUATION_d87656cdc9_002.md#implementation-validation-and-authority-limits) | <a id="final-integrated-software-acceptance"></a> [Final integrated software acceptance](STAGE12_R76_TO_R80_COMPLETE_11POINT_DISTANCE_GRID_AUDIT_CONTINUATION_d87656cdc9_003.md#final-integrated-software-acceptance)

<!-- stage822a-payload-begin -->

Saved paired-block evidence, exact inference and paired BCa sensitivity; declared timing is not physical range.
R76/R78 meet necessary observed strict conditions; R77/R79/R80 retain statistical or unanimity/GP gaps.
Independent software evidence is integrated below; no actuator, universal AF rule or wireless acceptance is established.

# Stage12 R76-R80: eleven declared timing contexts and AF-package audit

The new frozen evidence supports a qualified answer rather than the requested universal claim. R76 and R78 have all five QoE outcomes favorable in16/16 matched blocks, favorable exact signed-rank/HL evidence after scoped Holm500, and observed mean GP loss below2%. R77 loses2.024813% GP and has15/16 UL/Jain wins; R79 has15/16 p95/p99 wins; R80 loses4.211151% GP and has15/16 UL/Jain wins. These are necessary observed conditions, not controller, causal, hardware, physical-range or production acceptance. No equivalence/noninferiority test was substituted for the mean-GP floor.

The primary result is [wave_bf_eleven_distance_and_af_ablation_analysis.json](../artifacts/autoresearch/waves_be_to_bh_20261024/wave_bf_eleven_distance_and_af_ablation_analysis.json), with [source/input/build bindings](../artifacts/autoresearch/waves_be_to_bh_20261024/wave_bf_build_receipt.json) and [implementation freeze](../artifacts/autoresearch/waves_be_to_bh_20261024/wave_bf_freeze.json). Both requested report filenames contain identical bytes. Independent acceptance belongs to the coordinator; this report does not accept its own implementation.

## Scope, actual source identity and descriptives

The current canonical corpus has260 records (258primary+2auxiliary),1756crossed treatment-by-block rows,790round-scoped matched IDs, and16separate unpaired R17 sequential rows. The new contribution is10arms,160treatment-by-block rows,80matched IDs and1600saved RTT probes. The spec161-record total is refuted. Source R76 is1500m/class3, not the contradictory4.5km goal label. Frozen JSON/TSV and recipe text are retained; recipes were never imported or executed.

The source-bound paired outcome plot was generated before inferential results. It shows every saved block and marks R77block14 without removing it: [35-panel paired descriptives](../artifacts/autoresearch/waves_be_to_bh_20261024/wave_bf_paired_descriptives.png); underlying values and assumptions are in [wave_bf_preinference_descriptives.json](../artifacts/autoresearch/waves_be_to_bh_20261024/wave_bf_preinference_descriptives.json). Outlier labels do not prove an RF cause.

Means below use canonical `.6f`; latency uses canonical Python `.4f`, preserving display rounding independently of exact criteria. GP/DL/UL units are Mbps, latency ms, Jain unitless.

| Round | Arm | GP | DL | UL | Jain | Saved mean loss% | Drops |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R76 | Stock | 108.916016 | 92.729492 | 16.186523 | 0.669434 | 0.0 | 0 |
| R76 | Target | 107.405273 | 82.994141 | 24.411133 | 0.770630 | 0.0 | 0 |
| R77 | Stock | 91.781250 | 76.005859 | 15.775391 | 0.698792 | 0.0 | 0 |
| R77 | Target | 89.922852 | 67.613281 | 22.309570 | 0.796448 | 0.0 | 0 |
| R78 | Stock | 85.142578 | 70.492188 | 14.650391 | 0.699036 | 0.0 | 0 |
| R78 | Target | 84.433594 | 63.226562 | 21.207031 | 0.800720 | 0.0 | 0 |
| R79 | Stock | 74.355469 | 63.592773 | 10.762695 | 0.661682 | 0.0 | 0 |
| R79 | Target | 74.943359 | 57.861328 | 17.082031 | 0.768555 | 0.0 | 0 |
| R80 | Stock | 90.556641 | 79.211914 | 11.344727 | 0.640442 | 0.0 | 0 |
| R80 | Target | 86.743164 | 71.417969 | 15.325195 | 0.705261 | 0.0 | 0 |

| Round | Stock p50 | Target p50 | Stock p95 | Target p95 | Stock p99 | Target p99 |
| --- | --- | --- | --- | --- | --- | --- |
| R76 | 21.5415 | 6.8415 | 46.0764 | 21.7318 | 51.4749 | 31.5208 |
| R77 | 28.1275 | 6.1760 | 52.7351 | 18.3723 | 68.9768 | 33.3807 |
| R78 | 30.0795 | 5.7650 | 51.9545 | 15.7771 | 55.5358 | 23.7261 |
| R79 | 24.6025 | 5.1585 | 51.3813 | 14.2464 | 65.6910 | 18.9780 |
| R80 | 24.7945 | 6.0665 | 45.3536 | 18.3825 | 56.1220 | 27.8459 |

All40recorded GP/DL/UL/Jain means equal source-decimal rational block means, binary-rational means and NumPy means with zero ULP error. Every arm retains160/160 RTTs, chronological concatenation and exact arm/block MAC-counter sums. Saved restoration is true, saved mean loss/drops zero; this is saved-source health evidence, not a new independent device readback.

| Round | Declared m | Class | Slot us | ACK us | Recipe coverage literals | Effective/physical proof |
| --- | --- | --- | --- | --- | --- | --- |
| R76 | 1500 | 3 | 18 | 36 | 0,3 | False / False |
| R77 | 7500 | 16 | 57 | 114 | 0,16 | False / False |
| R78 | 10500 | 23 | 78 | 156 | 0,23 | False / False |
| R79 | 13500 | 30 | 99 | 198 | 0,30 | False / False |
| R80 | 7500 | 16 | 57 | 114 | 0,16 | False / False |

Shared payload/treatment/knob declarations are validated; endpoint timing omissions and recipe errors/readback limits remain. Class3/16/23/30 maps to saved slot/ACK18/36,57/114,78/156,99/198. A literal coverage command or reset-to0 in recipe text is not execution, effective firmware timing, GPS, geographic distance, regulatory authority or outdoor range evidence. R75class33 remains the narrow unverified saved-source label, not a general driver-validity claim.

## Counter-rate estimand and retries

The seventh outcome is each block's saved AP WDS retry-events delta divided by its positive TX-packet delta on declared `phy0-ap0.sta1`. No reported-rate fallback, zero-denominator imputation, pooled-rate substitution or missing-block deletion is allowed. The interface is named by the frozen recipe, not an independent AP/peer hardware identity check. Retry events per packet are not PER, unique packet loss, failed-subframe probability or retransmitted-byte fraction.

| Round | Arm | TX packets | Retry events | Exact arm-summed fraction | Rate% |
| --- | --- | --- | --- | --- | --- |
| R76 | Stock | 677595 | 1274 | 1274/677595 | 0.188018 |
| R76 | Target | 615109 | 1105 | 1105/615109 | 0.179643 |
| R77 | Stock | 558922 | 1202 | 601/279461 | 0.215057 |
| R77 | Target | 504481 | 1327 | 1327/504481 | 0.263043 |
| R78 | Stock | 518741 | 1053 | 1053/518741 | 0.202991 |
| R78 | Target | 472195 | 1005 | 201/94439 | 0.212836 |
| R79 | Stock | 468743 | 2060 | 2060/468743 | 0.439473 |
| R79 | Target | 432748 | 1391 | 1391/432748 | 0.321434 |
| R80 | Stock | 579347 | 1681 | 1681/579347 | 0.290154 |
| R80 | Target | 528642 | 2031 | 677/176214 | 0.384192 |

Arm-summed retry rate is lower for R76 and R79, higher for R77/R78/R80. None of the five paired per-block retry signed-rank tests survives scoped Holm500. That does not contradict the separate arm-summed comparisons: weighting by packet counts changes the estimand. No retry significance or lower-retry requirement was silently transferred into or out of the preexisting five-QoE gate.

## Experimental unit, exact statistics and multiplicity

Each round has16explicit matched block IDs with8AB/8BA sequences. Pings/order statistics are not independent physical trials. No block number is paired across rounds. The30ordinary metrics plus5retry-rate outcomes create35primary tests and560paired metric differences. Each exact mean sensitivity enumerates65536integer signed sums of the provided finite binary64 differences; rank/sign are separately checked. Source-decimal differences (exact rational counter ratios for retry) are separately preserved to expose precision/tie sensitivity.

Family definitions were fixed before outcome computation in [wave_bf_family_and_bootstrap_recipe.json](../artifacts/autoresearch/waves_be_to_bh_20261024/wave_bf_family_and_bootstrap_recipe.json). Primary scoped Holm500 has35known rank tests+465unknown p1 tests. Mean-flip Holm500 is a separate35+465 sensitivity family. Prior945rank hypotheses are retained unchanged, giving complete known enumerated980; calling this complete Holm500 would be inapplicable. It is not every research hypothesis in the project. Signs are diagnostic, not a post-hoc replacement primary family.

All effects are target minus stock. Lower is favorable for latency and retry; higher for GP/UL/Jain. These are conditional symmetric-shift/sign-exchangeability analyses, not automatically randomization-valid causal tests. The following table keeps rank, sign and mean distinct.

| Round | Metric | Wins /16 | HL | Rank p | Sign p | Mean-flip p | Rank Holm500 | Rank Holm980 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R76 | goodput_rx_mbps | 3 | -1.49609375 | 0.0009765625 | 0.021270752 | 0.000946044922 | 0.462890625 | 0.716796875 |
| R76 | p50_rtt_ms | 16 | -12.66425 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R76 | p95_rtt_ms | 16 | -19.1897 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R76 | p99_rtt_ms | 16 | -19.103825 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R76 | ul_goodput_mbps | 16 | 8.296875 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R76 | jain_fairness | 16 | 0.1015625 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R76 | wds_mac_retry_rate | 10 | -9.04877287e-05 | 0.495422363 | 0.454498291 | 0.476470947 | 1 | 1 |
| R77 | goodput_rx_mbps | 7 | -0.52734375 | 0.216186523 | 0.803619385 | 0.102539062 | 1 | 1 |
| R77 | p50_rtt_ms | 16 | -22.580375 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R77 | p95_rtt_ms | 16 | -30.0252875 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R77 | p99_rtt_ms | 16 | -29.3293375 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R77 | ul_goodput_mbps | 15 | 7.25390625 | 0.000305175781 | 0.000518798828 | 0.000274658203 | 0.145263672 | 0.23223877 |
| R77 | jain_fairness | 15 | 0.104980469 | 6.10351562e-05 | 0.000518798828 | 6.10351562e-05 | 0.029296875 | 0.0482177734 |
| R77 | wds_mac_retry_rate | 8 | 9.33233479e-05 | 0.528167725 | 1 | 0.429260254 | 1 | 1 |
| R78 | goodput_rx_mbps | 6 | -0.8515625 | 0.0594787598 | 0.454498291 | 0.109436035 | 1 | 1 |
| R78 | p50_rtt_ms | 16 | -22.8375 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R78 | p95_rtt_ms | 16 | -32.8730625 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R78 | p99_rtt_ms | 16 | -32.628665 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R78 | ul_goodput_mbps | 16 | 6.203125 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R78 | jain_fairness | 16 | 0.0981445312 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R78 | wds_mac_retry_rate | 6 | 0.000108643107 | 0.528167725 | 0.454498291 | 0.537139893 | 1 | 1 |
| R79 | goodput_rx_mbps | 7 | -0.0390625 | 0.979949951 | 0.803619385 | 0.639221191 | 1 | 1 |
| R79 | p50_rtt_ms | 16 | -20.687375 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R79 | p95_rtt_ms | 15 | -36.7113 | 6.10351562e-05 | 0.000518798828 | 6.10351562e-05 | 0.029296875 | 0.0482177734 |
| R79 | p99_rtt_ms | 15 | -37.2083075 | 6.10351562e-05 | 0.000518798828 | 6.10351562e-05 | 0.029296875 | 0.0482177734 |
| R79 | ul_goodput_mbps | 16 | 6.31640625 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R79 | jain_fairness | 16 | 0.106445312 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R79 | wds_mac_retry_rate | 11 | -0.000888461461 | 0.0739135742 | 0.210113525 | 0.0476379395 | 1 | 1 |
| R80 | goodput_rx_mbps | 0 | -3.30859375 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R80 | p50_rtt_ms | 16 | -18.2485 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R80 | p95_rtt_ms | 16 | -23.1912375 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R80 | p99_rtt_ms | 16 | -22.690995 | 3.05175781e-05 | 3.05175781e-05 | 3.05175781e-05 | 0.0152587891 | 0.0294494629 |
| R80 | ul_goodput_mbps | 15 | 4.234375 | 0.000579833984 | 0.000518798828 | 0.000244140625 | 0.275421143 | 0.427337646 |
| R80 | jain_fairness | 15 | 0.0676269531 | 0.000152587891 | 0.000518798828 | 0.000122070312 | 0.0727844238 | 0.117492676 |
| R80 | wds_mac_retry_rate | 4 | 0.000827468264 | 0.0041809082 | 0.0768127441 | 0.0036315918 | 1 | 1 |

## Exact confidence sets and paired BCa sensitivity

The exact95% and99.9% sets invert the conditional signed-rank test over Walsh breakpoints, preserving component unions and open/closed endpoints. They are marginal, not simultaneous500/980-test intervals. The HL pseudomedian uses136derived Walsh averages of16paired differences; those136terms are not independent samples.

<!-- stage822a-payload-end -->
