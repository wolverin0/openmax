<!-- doc-head: STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT.md continuation 2 of 3; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT.md) | Part 2/3
<a id="r71-r75-seven-distance-and-eight-flow-audit"></a> [R71-R75 seven-distance and eight-flow audit](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_001.md#r71-r75-seven-distance-and-eight-flow-audit) | <a id="source-units-health-and-exact-means"></a> [Source units, health and exact means](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_001.md#source-units-health-and-exact-means) | <a id="typed-declared-contexts-and-complete-packages"></a> [Typed declared contexts and complete packages](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_001.md#typed-declared-contexts-and-complete-packages) | <a id="canonical-means-and-pooled-latency"></a> [Canonical means and pooled latency](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_001.md#canonical-means-and-pooled-latency) | <a id="exact-gp-budgets-and-all-favorable-block-counts"></a> [Exact GP budgets and all favorable-block counts](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_001.md#exact-gp-budgets-and-all-favorable-block-counts) | <a id="every-stated-numerical-claim-and-retained-discrepancy"></a> [Every stated numerical claim and retained discrepancy](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_001.md#every-stated-numerical-claim-and-retained-discrepancy) | <a id="is-r74-the-highest-eight-flow-gp-gain"></a> [Is R74 the highest eight-flow GP gain?](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_003.md#is-r74-the-highest-eight-flow-gp-gain) | <a id="implementation-evidence-and-limits"></a> [Implementation evidence and limits](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_003.md#implementation-evidence-and-limits) | <a id="actual-bc-decisions-and-ba-model-limits"></a> [Actual BC decisions and BA model limits](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_003.md#actual-bc-decisions-and-ba-model-limits) | <a id="full-suite-evidence-and-preserved-host-fixture-failure"></a> [Full-suite evidence and preserved host-fixture failure](STAGE12_R71_TO_R75_SEVEN_DISTANCE_AND_EIGHT_FLOW_AUDIT_CONTINUATION_e7424c6156_003.md#full-suite-evidence-and-preserved-host-fixture-failure)

<!-- stage822a-payload-begin -->

- `{"actual_favorable":13,"claimed_favorable":14,"equal":0,"matches":false,"mean_flip_p":0.00439453125,"metric":"p95_rtt_ms","rank_holm500":1.0,"rank_p":0.004180908203125,"round_id":"R71","sign_p":0.021270751953125}`
- `{"actual_favorable":11,"claimed_favorable":14,"equal":0,"matches":false,"mean_flip_p":0.018890380859375,"metric":"p99_rtt_ms","rank_holm500":1.0,"rank_p":0.0506591796875,"round_id":"R71","sign_p":0.210113525390625}`
- `{"actual":-0.42574947710899375,"actual_exact":"-1832/4303","claim_is_rounded_not_exact_source":true,"claimed_display_literal":"-0.425750","difference_from_display":"9/17212000","display_precision":6,"metric":"signed_GP_change_percent","round_id":"R72","rounded_matches":false}`

Exact underlying source values govern; a small display discrepancy is distinct
from failure of a GP floor or scientific assumption. A matching eight-decimal
`0.00003052` display corresponds to2/65536 when all16 signs are favorable,
not a universal p-value for every latency contrast. Holm significance and
unanimity are distinct predicates.

## Retry diagnostics and declared policy

All target endpoints declare short/long retry6/4. Actual retry rates are summed
retry events divided by TX packets, not PER, unique lost frames or A-MPDU
subframe counts. Lower numerators alone do not prove lower rates.

| Round | Arm | Retry events / TX packets | Retry fraction percent |
| --- | --- | --- | --- |
| R71 | A | 1168 / 672012 | 0.173806 |
| R71 | B | 1214 / 639856 | 0.189730 |
| R72 | A | 1184 / 635885 | 0.186197 |
| R72 | B | 1286 / 579607 | 0.221874 |
| R73 | A | 936 / 497727 | 0.188055 |
| R73 | B | 880 / 449654 | 0.195706 |
| R74 | A | 1032 / 638909 | 0.161525 |
| R74 | B | 1075 / 569292 | 0.188831 |
| R75 | A | 821 / 463701 | 0.177054 |
| R75 | B | 891 / 419434 | 0.212429 |

No specific counter rate or lower-retry claim is invented where the new spec
does not state one. Count-derived diagnostics are retained regardless of
whether a six-flow-only retry utility supports that workload. Unsupported
two/eight-flow modes are not measured GP failures and gain no hidden exception.

## Exact conditional rank, sign, mean and Walsh sets

The family recipe was frozen before this lane computed outcomes, after
physical collection and a user narrative; it is retrospective specified
analysis, not prospective experimental preregistration. Thirty primary rank
tests plus470 unknownp1 placeholders form scoped500. A separate30-test exact
mean-flip family has its own470p1 padding. Prior915 hypotheses remain unchanged;
complete-known945 is not a complete500 family or every project research test.

Each contrast enumerates all65536 assignments on finite binary64 differences.
Mean flips use exact scaled integers from Fraction.from_float, without epsilon
tail comparisons. Midrank/tie/zero rank and sign tails agree with the accepted
DP engine; source-decimal subtraction is separately retained as sensitivity.
Binomial sign, signed rank and mean flips test different statistics. HL is the
Walsh pseudomedian of block differences, not a pooled-quantile difference.

| Round | Metric | HL B minus A | Rank p | Sign p | Mean-flip p | Rank Holm500 | Rank Holm945 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R71 | GP | -1.87109375 | 0.00173950195312 | 0.0768127441406 | 0.00140380859375 | 0.829742431641 | 1 |
| R71 | p50 | -3.70187500 | 9.1552734375e-05 | 0.000518798828125 | 9.1552734375e-05 | 0.0438537597656 | 0.0701293945312 |
| R71 | p95 | -2.87787500 | 0.00418090820312 | 0.0212707519531 | 0.00439453125 | 1 | 1 |
| R71 | p99 | -2.89266000 | 0.0506591796875 | 0.210113525391 | 0.0188903808594 | 1 | 1 |
| R71 | UL | 3.25000000 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R71 | Jain | 0.03906250 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R72 | GP | -0.37109375 | 0.236083984375 | 0.803619384766 | 0.408081054688 | 1 | 1 |
| R72 | p50 | -12.13350000 | 6.103515625e-05 | 0.000518798828125 | 6.103515625e-05 | 0.0293579101562 | 0.0473022460938 |
| R72 | p95 | -33.49406250 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R72 | p99 | -35.08823500 | 6.103515625e-05 | 0.000518798828125 | 6.103515625e-05 | 0.0293579101562 | 0.0473022460938 |
| R72 | UL | 9.12500000 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R72 | Jain | 0.11254883 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R73 | GP | -0.94140625 | 0.107299804688 | 0.454498291016 | 0.0700073242188 | 1 | 1 |
| R73 | p50 | -22.10687500 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R73 | p95 | -37.78522500 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R73 | p99 | -40.05428000 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R73 | UL | 6.20312500 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R73 | Jain | 0.10522461 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R74 | GP | 0.01953125 | 0.990234375 | 0.803619384766 | 0.690612792969 | 1 | 1 |
| R74 | p50 | -11.66162500 | 0.000152587890625 | 0.000518798828125 | 0.000152587890625 | 0.0729370117188 | 0.115661621094 |
| R74 | p95 | -25.01607500 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R74 | p99 | -23.72135750 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R74 | UL | 10.92578125 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R74 | Jain | 0.13403320 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R75 | GP | -1.10156250 | 0.0249633789062 | 0.210113525391 | 0.0216979980469 | 1 | 1 |
| R75 | p50 | -24.34887500 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R75 | p95 | -45.84037500 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R75 | p99 | -46.75046000 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R75 | UL | 5.50781250 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |
| R75 | Jain | 0.09594727 | 3.0517578125e-05 | 3.0517578125e-05 | 3.0517578125e-05 | 0.0152587890625 | 0.0283813476562 |

Scoped rank500 rejects22; separate
mean500 rejects22; complete
known945 rank rejects179
including history. These are hypothesis counts, not independent experiments.
Only primary rank evidence enters the source-pinned promotion projection;
mean/sign results cannot substitute into it.

All60 marginal exact95% and99.9% acceptance sets below retain component
boundaries and open/closed endpoints in the machine result; display does not
replace the exact stored endpoints or make simultaneous500/945 intervals.
Independent symmetric sign-exchangeability and a defensible shift model are
unproven assumptions. Arithmetic exactness does not remove confounding.

| Round | Metric | Marginal95% set | Marginal99.9% set |
| --- | --- | --- | --- |
| R71 | GP | (-2.859375, -0.8046875) | (-3.65625, 0.21875) |
| R71 | p50 | (-5.09675, -2.30325) | (-6.26425, -0.77775) |
| R71 | p95 | (-5.921675, -0.7758) | (-10.822525, 0.429475) |
| R71 | p99 | (-6.37907, 0.09661) | (-13.531705, 1.55961) union (1.55961, 1.596915) |
| R71 | UL | [2.34375, 3.8984375] | [1.5, 4.6171875) |
| R71 | Jain | (0.029296875, 0.04736328125] | [0.02294921875, 0.0556640625] |
| R72 | GP | (-1.4453125, 0.3046875] | (-2.5859375, 2.15625) |
| R72 | p50 | [-15.32, -9.38125) | (-19.18875, -5.983) |
| R72 | p95 | (-40.555675, -25.957425] | (-46.659225, -18.158925] |
| R72 | p99 | (-42.62708, -25.53683) | (-47.879595, -15.820215) |
| R72 | UL | [7.5, 10.3046875] | (5.6015625, 11.203125) |
| R72 | Jain | (0.0927734375, 0.12744140625] | (0.0712890625, 0.1396484375) |
| R73 | GP | (-2.5, 0.2578125) | (-5.3984375, 1.2109375) |
| R73 | p50 | [-24.748, -18.858) | (-27.749, -16.26625) |
| R73 | p95 | (-40.735825, -34.283375) | (-47.6216, -30.088725) |
| R73 | p99 | (-41.699105, -36.265365] | (-49.08032, -31.8987] |
| R73 | UL | [4.359375, 8.203125) | [3.0078125, 9.5] |
| R73 | Jain | (0.07958984375, 0.12939453125) | [0.06201171875, 0.14599609375] |
| R74 | GP | (-0.9609375, 1.2421875) | (-1.7578125, 2.9453125) |
| R74 | p50 | (-12.9935, -6.718) | (-13.7705, -3.662) |
| R74 | p95 | (-31.6136, -19.1426) | (-36.47355, -13.26995) |
| R74 | p99 | [-32.786265, -16.06189) | (-36.784275, -7.87575) union (-7.87575, -6.970075) |
| R74 | UL | (9.90625, 10) union (10, 12.25) | (9.25, 14.1484375) |
| R74 | Jain | (0.12255859375, 0.150390625) | (0.11083984375, 0.1689453125) |
| R75 | GP | (-2.15625, -0.1015625) | (-3.15625, 0.75) |
| R75 | p50 | (-27.37625, -21.15275) | (-29.749, -17.007) |
| R75 | p95 | (-50.418375, -40.98295] | (-54.647075, -36.8522) |
| R75 | p99 | [-52.21274, -42.41833) | (-58.32701, -38.688975] |
| R75 | UL | (3.90625, 7.046875] | (2.5, 8.5546875] |
| R75 | Jain | (0.0732421875, 0.123046875) | (0.05419921875, 0.14208984375) |

## Period and carryover identification

Every actual16-block schedule is8AB/8BA. The full block+period+current+lag
model is rank18/19: current treatment and differential carryover are aliased.
Restricted rank18/18 direct and period point estimates explicitly assume no
differential carryover. Exact source-decimal sequence means agree with least
squares, but no raw sign-flip p-value becomes a nuisance-adjusted causal test.

| Round | Full rank / columns | Restricted rank / columns | GP direct / period | p95 direct / period |
| --- | --- | --- | --- | --- |
| R71 | 18 / 19 | 18 / 18 | -1851/1024 / -199/1024 | -60880949999999999/16000000000000000 / 27717549999999983/16000000000000000 |
| R72 | 18 / 19 | 18 / 18 | -229/512 / -275/512 | -52708384999999993/1600000000000000 / 18800274999999979/8000000000000000 |
| R73 | 18 / 19 | 18 / 18 | -705/512 / -399/512 | -151295087499999983/4000000000000000 / -323896874999999/1000000000000000 |
| R74 | 18 / 19 | 18 / 18 | 63/256 / -217/512 | -80627360000000013/3200000000000000 / 7625599999999983/16000000000000000 |
| R75 | 18 / 19 | 18 / 18 | -583/512 / -3/8 | -731999399999999897/16000000000000000 / 34103700000000003/16000000000000000 |

## Seven observed declared-distance profiles

<!-- stage822a-payload-end -->
