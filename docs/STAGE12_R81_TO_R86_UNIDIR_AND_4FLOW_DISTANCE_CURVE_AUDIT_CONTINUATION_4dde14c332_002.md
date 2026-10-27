<!-- doc-head: STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT.md) | Part 2/3
<a id="stage12-r81-r86-direction-aware-unidirectional-and-four-flow-distance-audit"></a> [Stage12 R81-R86: direction-aware unidirectional and four-flow distance audit](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_001.md#stage12-r81-r86-direction-aware-unidirectional-and-four-flow-distance-audit) | <a id="actual-corpus-units-and-raw-descriptives"></a> [Actual corpus, units and raw descriptives](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_001.md#actual-corpus-units-and-raw-descriptives) | <a id="direction-aliases-source-period-mapping-and-recipe-evidence"></a> [Direction aliases, source period mapping and recipe evidence](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_001.md#direction-aliases-source-period-mapping-and-recipe-evidence) | <a id="station-retry-event-rate"></a> [Station retry-event rate](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_001.md#station-retry-event-rate) | <a id="exact-tests-family-scope-and-paired-bca"></a> [Exact tests, family scope and paired BCa](STAGE12_R81_TO_R86_UNIDIR_AND_4FLOW_DISTANCE_CURVE_AUDIT_CONTINUATION_4dde14c332_001.md#exact-tests-family-scope-and-paired-bca)

<!-- stage822a-payload-begin -->
| Round | Metric | Exact95% set | Exact99.9% set | Paired BCa95% sensitivity |
| --- | --- | --- | --- | --- |
| R81 | goodput_rx_mbps | (-3.5, -2) | (-4, -1.5] | UNAVAILABLE: ZERO_JACKKNIFE_VARIATION |
| R81 | p50_rtt_ms | (-11.7275, -5.661) | (-15.1005, -3.2245) | [-11.30325, -5.768994658] |
| R81 | p95_rtt_ms | (-14.419375, -6.611) | (-17.01015, -2.398625) | [-14.20915, -7.074525] |
| R81 | p99_rtt_ms | (-14.32728, -5.10512) | [-17.416675, -0.111725) | [-14.078335, -5.441755025] |
| R81 | wds_mac_retry_rate | (-0.0001867861741, 0.0003622265346) | (-0.0004210200907, 0.0006431520091) | [-0.0001549247278, 0.0003476144357] |
| R82 | goodput_rx_mbps | (-1.59375, 0.8984375) | (-2.5, 2.1015625) | [-1.426106507, 0.8515625] |
| R82 | p50_rtt_ms | (-2.9525, -1.527) | (-3.75975, -1.0095) | [-2.91225, -1.574] |
| R82 | p95_rtt_ms | (-7.87305, -1.9958) | [-15.939875, -0.36105) | [-7.627868458, -2.36325] |
| R82 | p99_rtt_ms | (-9.088125, -2.069165) | (-22.049975, 0.24898) union (0.24898, 0.52084) | [-8.667886087, -2.363661059] |
| R82 | wds_mac_retry_rate | [0, 0] | [0, 0] | UNAVAILABLE: CONSTANT_BOOTSTRAP_DISTRIBUTION |
| R83 | goodput_rx_mbps | [-2.1015625, -0.3359375] | (-2.71875, 1.8984375] | [-2.100203856, -0.40625] |
| R83 | p50_rtt_ms | (-14.667, -10.57175) | (-16.811, -8.8275) | [-14.2915, -10.701] |
| R83 | p95_rtt_ms | (-24.7208, -12.997075) | (-34.386475, -7.60245) | [-24.58835, -13.4133] |
| R83 | p99_rtt_ms | [-27.1033, -13.971355) | (-39.14253, -5.715585) | [-26.80001, -14.84783] |
| R83 | ul_goodput_mbps | (7.4453125, 9.765625) | (6.09375, 10.7890625) | [7.5, 9.6875] |
| R83 | jain_fairness | (0.091796875, 0.119140625) | (0.07958984375, 0.130859375) | [0.09423828125, 0.1176757812] |
| R83 | wds_mac_retry_rate | (-0.0004127238296, 0.0002186939605) | (-0.001165680438, 0.0007364120457) | [-0.0003709971092, 0.0002142173295] |
| R84 | goodput_rx_mbps | (-1.796875, -0.21875) | (-2.96875, 0.4453125) | [-1.75, -0.25] |
| R84 | p50_rtt_ms | [-16.55725, -11.865) | (-19.343, -10.14025) | [-16.379, -12.09075] |
| R84 | p95_rtt_ms | (-24.4553, -13.7039) | (-29.355425, -10.531425) | [-23.170575, -14.1718] |
| R84 | p99_rtt_ms | (-25.248655, -14.123625) | (-31.295125, -9.72217) | [-24.355635, -14.2753375] |
| R84 | ul_goodput_mbps | (6.3984375, 8.6015625] | [5.3515625, 9.609375) | [6.453125, 8.59375] |
| R84 | jain_fairness | (0.0869140625, 0.119140625) | (0.07275390625, 0.1303710938) | [0.08837890625, 0.1176757812] |
| R84 | wds_mac_retry_rate | (-4.883250549e-05, 0.0003236647111) | (-0.0002976839826, 0.0005189726433) | [-3.533966476e-05, 0.0003468574246] |
| R85 | goodput_rx_mbps | [-2.640625, -0.1953125) | [-4.6015625, 1.8984375] | [-2.546875, -0.3046875] |
| R85 | p50_rtt_ms | (-23.1395, -14.9855) | [-25.50225, -10.7705) | [-22.742125, -15.185] |
| R85 | p95_rtt_ms | (-32.207325, -24.0663) | (-36.21425, -20.52105] | [-31.8479, -24.45285] |
| R85 | p99_rtt_ms | (-32.9376, -23.052995) | [-37.44948, -18.6763) | [-32.4656775, -23.38786] |
| R85 | ul_goodput_mbps | (4.453125, 7.90625] | [2.6484375, 9.15625] | [4.453125, 7.500041269] |
| R85 | jain_fairness | [0.068359375, 0.1108398438] | [0.046875, 0.1259765625] | [0.068359375, 0.109375] |
| R85 | wds_mac_retry_rate | (-0.000694391581, 0.0001480316523) | (-0.001523093499, 0.00128389754) | [-0.000628579855, 0.0001317654761] |
| R86 | goodput_rx_mbps | (-2.3515625, -2.3125) union (-2.3125, 0.0859375) | [-3.40625, 1.515625) | [-2.25, 0.0546875] |
| R86 | p50_rtt_ms | [-18.87425, -13.9285) | (-22.69925, -11.92725) | [-18.61786311, -14.12375] |
| R86 | p95_rtt_ms | (-29.473, -20.7891] | [-35.09225, -18.452775) | [-29.482125, -21.8976625] |
| R86 | p99_rtt_ms | (-32.321565, -22.341775) | (-40.01885, -18.41058] | [-31.79079, -22.5416725] |
| R86 | ul_goodput_mbps | (4.515625, 8.1875) | (3.0546875, 9.953125) | [4.6953125, 7.859375] |
| R86 | jain_fairness | [0.07177734375, 0.1186523438] | [0.052734375, 0.1455078125] | [0.072265625, 0.1155205179] |
| R86 | wds_mac_retry_rate | (-0.000363523893, 0.0006215162621) | (-0.001019852433, 0.001061442398] | [-0.0002946783707, 0.0005971881174] |

Paired BCa reuses the accepted unchanged implementation: one common10000x16index matrix from PCG64/default_rng(seed20261024), strict-less+half-tie z0,16leave-one-pair-out HL acceleration and linear empirical quantiles. Arms are never independently resampled. Index SHA256: `aa3c5705a22b5d7a54493d120a2b4c6a0235afec46f3bd4d8ba6d40b0b804a70`. Constant/boundary/nonfinite/zero-jackknife cases remain explicitly unavailable with intervalNone; no fabricated fallback. BCa is approximate conditional sensitivity and never replaces exact rank/HL/Holm source-bound promotion.

## Applicable strict source conditions and R85 claim

Unidirectional applicable outcomes remain three RTT metrics plus active GP (represented by the one total-GP hypothesis). Bidirectional applicable outcomes remain five QoE metrics. The GP floor and direct favorable HL/rank/Holm500 remain distinct checks; no unanimity, health, history, direction or source requirement is waived. Observed structural loss must be strictly<2%, while the historical operator<=2% projection is separately labeled. Neither is a statistical noninferiority/equivalence test.

| Round | Exact GP loss% | Loss% | Required applicable wins | All applicable16/16 | Direct rank-HL Holm500 | GP<2% | Necessary observed conjunction | Aggregate retry lower |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| R81 | 4400/1737 | 2.533103 | 16/15/13/0 | False | False | False | False | False |
| R82 | 26800/68089 | 0.393602 | 15/14/12/6 | False | False | True | False | False |
| R83 | 50300/53511 | 0.939994 | 16/15/15/16/16 | False | True | True | False | True |
| R84 | 59000/48897 | 1.206618 | 16/16/16/16/16 | True | True | True | True | False |
| R85 | 1045/672 | 1.555060 | 16/16/16/16/16 | True | True | True | True | True |
| R86 | 6200/5243 | 1.182529 | 16/16/16/16/16 | True | True | True | True | False |

R85requested strict claim evaluates to necessary observed conjunction=True; GP<2%=True, applicable16/16=True, favorable direct rank-HL/Holm500=True. Failed unanimity metrics: none. This is an actual computed result, not an assumption from the title; it remains separate from the coordinator-owned controller/structural health/provenance checks.

## Period and carryover assumptions

Full block+period+current+lag design estimability is retained. Restricted block+period+current coefficients are only named descriptive point estimates under no differential carryover/unmodeled block-period response. AB/BA balance proves neither randomization, independent blocks, washout nor temporal stability. Raw sign-flip p-values are not automatically nuisance-adjusted causal p-values.

| Round | Metric | Restricted direct | Restricted period | Rank/columns | AB/BA |
| --- | --- | --- | --- | --- | --- |
| R81 | goodput_rx_mbps | -2.75 | -0.125 | 18/18 | 8/8 |
| R81 | p50_rtt_ms | -8.683375 | 1.71 | 18/18 | 8/8 |
| R81 | p95_rtt_ms | -10.37149063 | 2.634234375 | 18/18 | 8/8 |
| R81 | p99_rtt_ms | -9.666498125 | 2.809846875 | 18/18 | 8/8 |
| R81 | wds_mac_retry_rate | 8.60260499e-05 | -9.700870861e-05 | 18/18 | 8/8 |
| R82 | goodput_rx_mbps | -0.26171875 | -0.3984375 | 18/18 | 8/8 |
| R82 | p50_rtt_ms | -2.2985 | -0.2134375 | 18/18 | 8/8 |
| R82 | p95_rtt_ms | -5.74089375 | -3.844225 | 18/18 | 8/8 |
| R82 | p99_rtt_ms | -6.95287875 | -5.204845 | 18/18 | 8/8 |
| R82 | wds_mac_retry_rate | 0 | 0 | 18/18 | 8/8 |
| R83 | goodput_rx_mbps | -0.982421875 | -0.646484375 | 18/18 | 8/8 |
| R83 | p50_rtt_ms | -12.59746875 | -0.44609375 | 18/18 | 8/8 |
| R83 | p95_rtt_ms | -19.24140937 | 2.909446875 | 18/18 | 8/8 |
| R83 | p99_rtt_ms | -21.09993188 | 4.688139375 | 18/18 | 8/8 |
| R83 | ul_goodput_mbps | 8.5234375 | -0.126953125 | 18/18 | 8/8 |
| R83 | jain_fairness | 0.1052856445 | -0.0009155273438 | 18/18 | 8/8 |
| R83 | wds_mac_retry_rate | -0.0001318347878 | 0.0003313535573 | 18/18 | 8/8 |
| R84 | goodput_rx_mbps | -1.15234375 | 0.046875 | 18/18 | 8/8 |
| R84 | p50_rtt_ms | -14.33528125 | -1.21434375 | 18/18 | 8/8 |
| R84 | p95_rtt_ms | -19.18587187 | -2.784134375 | 18/18 | 8/8 |
| R84 | p99_rtt_ms | -19.76612438 | -2.856876875 | 18/18 | 8/8 |
| R84 | ul_goodput_mbps | 7.5234375 | -0.466796875 | 18/18 | 8/8 |
| R84 | jain_fairness | 0.1028442383 | -0.006042480469 | 18/18 | 8/8 |
| R84 | wds_mac_retry_rate | 0.0001183069446 | 0.0001201586533 | 18/18 | 8/8 |
| R85 | goodput_rx_mbps | -1.428710938 | 0.5537109375 | 18/18 | 8/8 |
| R85 | p50_rtt_ms | -18.93396875 | -0.12271875 | 18/18 | 8/8 |
| R85 | p95_rtt_ms | -28.26638438 | 0.472478125 | 18/18 | 8/8 |
| R85 | p99_rtt_ms | -28.10017687 | 0.262395625 | 18/18 | 8/8 |
| R85 | ul_goodput_mbps | 6.0390625 | -0.05078125 | 18/18 | 8/8 |
| R85 | jain_fairness | 0.08929443359 | -0.001403808594 | 18/18 | 8/8 |
| R85 | wds_mac_retry_rate | -0.0002114452513 | -0.0003260227669 | 18/18 | 8/8 |
| R86 | goodput_rx_mbps | -1.029296875 | -0.27734375 | 18/18 | 8/8 |
| R86 | p50_rtt_ms | -16.5019375 | 1.37475 | 18/18 | 8/8 |
| R86 | p95_rtt_ms | -25.41247187 | 4.365034375 | 18/18 | 8/8 |
| R86 | p99_rtt_ms | -27.68139437 | 5.994506875 | 18/18 | 8/8 |
| R86 | ul_goodput_mbps | 6.409179688 | -0.8134765625 | 18/18 | 8/8 |
| R86 | jain_fairness | 0.09649658203 | -0.01165771484 | 18/18 | 8/8 |
| R86 | wds_mac_retry_rate | 0.0001117107448 | 0.000188583084 | 18/18 | 8/8 |

## Contextual packages, not a causal distance or AF curve

### four flow declared distance points

| Round | Regime | Declared m | Control GP | Target GP | Target UL | Target p95 | GP loss% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R64 | bidir_4flow | 100 | 106.532227 | 105.895508 | 20.701172 | 19.9715 | 0.597677 |
| R83 | bidir_4flow | 3000 | 104.513672 | 103.531250 | 20.505859 | 19.5319 | 0.939994 |
| R84 | bidir_4flow | 6000 | 95.501953 | 94.349609 | 19.150391 | 16.1647 | 1.206618 |
| R86 | bidir_4flow | 9000 | 87.041992 | 86.012695 | 17.787109 | 14.5426 | 1.182529 |

R83 changed target coordinates from the first point: [0].distance_meters, [1].distance_meters. Changed control coordinates: [0].distance_meters, [1].distance_meters.
R84 changed target coordinates from the first point: [0].distance_meters, [1].distance_meters. Changed control coordinates: [0].distance_meters, [1].distance_meters.
R86 changed target coordinates from the first point: [0].distance_meters, [1].distance_meters. Changed control coordinates: [0].distance_meters, [1].distance_meters.

### six flow 7500m distinct packages

| Round | Regime | Declared m | Control GP | Target GP | Target UL | Target p95 | GP loss% |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R77 | bidir_6flow | 7500 | 91.781250 | 89.922852 | 22.309570 | 18.3723 | 2.024813 |
| R80 | bidir_6flow | 7500 | 90.556641 | 86.743164 | 15.325195 | 18.3825 | 4.211151 |
| R85 | bidir_6flow | 7500 | 91.875000 | 90.446289 | 21.220703 | 20.3104 | 1.555060 |

R80 changed target coordinates from the first point: [0].airtime_flags, [0].aql_by_ac[2][0], [0].aql_by_ac[2][1], [0].aql_threshold_us, [1].airtime_flags. Changed control coordinates: none.
R85 changed target coordinates from the first point: [0].aql_by_ac[2][0], [0].aql_by_ac[2][1], [0].aql_threshold_us. Changed control coordinates: none.

The four-flow points span historical R64at100m and new R83/R84/R86at3000/6000/9000m as declared contexts. Full endpoint states, timing, controls and rounds differ; neither interpolation nor an isolated AQL/distance effect is identified. R77/R80/R85 are three separate7500m six-flow package comparisons. R85 APBE1550/3100 is not the old1520/3040 or1540/3080 package. No crossround block pairing, isolated AF mechanism, generic outdoor range, superior-radio claim or sector extrapolation follows. Unmeasured regime/distance cells remain unmeasured.

## Reproducible software evidence and authority

The old BF functions and55test AST bodies are preserved exactly, with before-extension source snapshots. BJ is an explicit additive campaign (`--campaign BJ` / build_analysis_bj), not a default rewrite of old artifacts. Exact rank/CI/mean engines and paired_bca_hl are reused unchanged. [Methods](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_methods.md) describes definitions; [focused host tests](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_focused_tests_6.json) records132PASS/0FAIL/SKIP/exit0/guard0 before the current inference. The first109PASS/4FAIL is preserved with exact source: two new Jain-scope omissions and two unsupported raw-observation-duplicate assumptions. No criterion was lowered.

The first actual CLI stopped because an exact-equality crosscheck exposed one-ULP rounding in the legacy binomial float tail when a pair difference is zero. The independent integer-combinatorial probabilities are R82GP9949/16384=0.60723876953125 and R85GP1941/16384=0.11846923828125. A BJ-only sign facade now emits those exact fractions, retaining the old float value/delta as diagnostics and cross-checking all65536assignments. Rank, mean, HL, confidence-set engines and old source artifacts are unchanged; no numeric tolerance was widened. The deterministic regression preserved127PASS/2FAIL before correction and132PASS after; [diagnostic](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_exact_crosscheck_failure.json), [RED receipt](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_focused_tests_5_sign_RED.json) and the complete before-fix snapshots remain. Previous source/dependency freezes and first raw plots are retained, with new current freeze/descriptives files rather than overwrites.

Actual current CLI evidence is [wave_bj_cli_run_2.json](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_cli_run_2.json); first failed CLI remains [wave_bj_cli_run_1.json](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bj_cli_run_1.json). Installed software: python 3.12.4, numpy 1.26.4, scipy 1.17.1, matplotlib 3.10.1. No dependency was installed or online bibliography verified. Applied local guidance: [statistical-analysis](../.agents/skills/statistical-analysis/SKILL.md), [experimental-design](../.agents/skills/experimental-design/SKILL.md), [scientific-critical-thinking](../.agents/skills/scientific-critical-thinking/SKILL.md). Their citation metadata is local/offline attribution only. Actual model/effort is not exposed and is not invented.

Final independent statistical/report acceptance, actual BKcontext choices, the fresh complete-suite receipt and the separate final seal belong to coordinator-owned evidence; no pending review or matrix is assumed passed here. No device/network/SSH/target execution, live bench/daemon/monitor operation, recipe import/execution, install/global configuration, firmware/protected-partition write, actuator or R87+content access occurred. E2 remains NOT_ACCEPTED; Stage4/custom MAC, physical recovery and production gates remain unchanged.


## Final integrated software acceptance

This coordinator-authored section supersedes the initial body's pending integration statements. [Independent BI normalization review](../artifacts/autoresearch/waves_bi_to_bl_20261024/review_wave_bi.json), [independent BJ numerical replay](../artifacts/autoresearch/waves_bi_to_bl_20261024/review_wave_bj.json), [independent design-rank replay](../artifacts/autoresearch/waves_bi_to_bl_20261024/review_wave_bj_design.json) and [independent BK integration review](../artifacts/autoresearch/waves_bi_to_bl_20261024/review_wave_bk.json) have no open material findings. The initial163 numeric table rows were independently matched with source-bound results before this appendix. This is offline software acceptance; physical/causal acceptance and automatic_execution_allowed remainFalse.

For precise preservation counts, [the independent source contract](../artifacts/autoresearch/waves_bi_to_bl_20261024/review_wave_bj_source_contract.json) verifies21 legacy source function ASTs and19 test/helper function ASTs. Those test definitions account for55 legacy collected parameterized cases;55 is not a count of distinct function definitions.

The actual [BK matrix](../artifacts/autoresearch/waves_bi_to_bl_20261024/wave_bk_evaluation.json) evaluates66 explicit regime/distance cells over10 source views,18 new direct comparisons and12 structural profiles. Counts are {"ABSTAIN": 47, "BLOCKED": 6, "ELIGIBLE_OFFLINE_STRICT_CONTEXT": 13}. These are saved declared contexts, including abstention and qualified negatives; no unmeasured cell is interpolated.

<!-- stage822a-payload-end -->
