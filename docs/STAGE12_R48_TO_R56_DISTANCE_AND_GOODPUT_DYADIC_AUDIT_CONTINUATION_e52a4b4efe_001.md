<!-- doc-head: STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT.md) | Part 1/2
<a id="period-carryover-and-the-causal-boundary"></a> [Period, carryover and the causal boundary](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_002.md#period-carryover-and-the-causal-boundary) | <a id="descriptive-pareto-interpretation-and-selector-boundary"></a> [Descriptive Pareto interpretation and selector boundary](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_002.md#descriptive-pareto-interpretation-and-selector-boundary) | <a id="auxiliary-ak-modeling-is-enabling-evidence"></a> [Auxiliary AK modeling is enabling evidence](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_002.md#auxiliary-ak-modeling-is-enabling-evidence) | <a id="validation-preserved-failures-and-what-remains-unknown"></a> [Validation, preserved failures and what remains unknown](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_002.md#validation-preserved-failures-and-what-remains-unknown)

<!-- stage822a-payload-begin -->

Eighteen saved arms pass rational/NumPy zero-ULP means and 2880/2880 pings.
All42 stated favorable-block counts match; significance remains outcome-specific.
R50 loses1.25107465% GP and passes the observed2% floor, but retry increases.
54 scoped tests and831 complete-known tests are distinct multiplicity scopes.
Coverage is programmed timing; carryover, physical range and actuation remain unproven.


# Stage12 — R48–R56 distance and goodput dyadic audit

Date: 2026-10-24. Parent: `FMX-OFFLINE-WAVES-AK-AN-20261024`, supporting the Stage12 control-boundary and experiment-methodology deliverables. This report describes **saved evidence and offline computation**. It does not authorize a canary, certify physical distance, or establish an independent-sector performance gain.

The central result is a real tradeoff. R50 retains 107.6826171875Mbps against its own 109.046875Mbps control, a loss of exactly `34925/27916` percent, or **1.251074652529%**. Its p50/p95/p99, UL and Jain outcomes each improve in all16 matched blocks and pass the scoped rank Holm500 audit. However, its counter-derived retry fraction increases. Passing the observed GP floor is therefore a narrower fact than satisfying the pre-existing lower-retry selector contract, statistical noninferiority, or physical acceptance.

The [canonical AL analysis](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_distance_goodput_dyadic_analysis.json) and [independent AL review](../artifacts/autoresearch/waves_ak_to_an_20261024/review_wave_al.json) govern the numerical statements below. Source receipts take precedence over the narrative specification. This report itself still requires the coordinator's separate documentary acceptance.

## Evidence, identity and preservation

Only the27 frozen R48–R56 JSON/TSV/recipe files were used as new measurement inputs. They were copied before inspection and are bound by [inputs_manifest.json](../artifacts/autoresearch/waves_ak_to_an_20261024/inputs_manifest.json), SHA256 `88c7b54b781e53b9747d704ea75a880f85984aa4a335fe36c06f8042bb5c9bef`. Recipes were read as text provenance, never imported or executed. No original R48–R56 pointer or R57+ content was opened for this audit; no device, network, radio, daemon or bench-process operation was performed.

| Bound evidence | SHA256 / scope |
| --- | --- |
| [Canonical AL result](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_distance_goodput_dyadic_analysis.json) | `192767dae80129691b57eaeba1a7ca8323f8106bdfe2679c52b4a1071a5a5b6e` |
| [AL build receipt](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_build_receipt.json) | `7da8356f8c6ceed7b3677f9342387b228443b52ce08c5e54468cd484974cff88` |
| [Independent numerical check](../artifacts/autoresearch/waves_ak_to_an_20261024/review_wave_al_independent_numerical_checks.json) | `01b0e6eb16411bc150b9d31b04fb0d843efe909ad60e52e323f8c9e5bf207192` |
| [Independent design check](../artifacts/autoresearch/waves_ak_to_an_20261024/review_wave_al_independent_design_checks.json) | `e7aa75ccb773e2b0c23abd7aa3b94b77babafeac9fa3df089ef81704829228d4` |
| [Independent AL acceptance](../artifacts/autoresearch/waves_ak_to_an_20261024/review_wave_al.json) | `94b959ff1d14677eb5f7c2e2b326bc3d33ce73f4fd7655190d1734c4e0068ebd`, PASS_WITH_LIMITS |
| [R56 normalized records](../artifacts/autoresearch/waves_ak_to_an_20261024/normalized_r1_to_r56_measurements_20261024.json) | `80d3411da9765c3fd42461e03f2411e4ba660857112d15b0972c7547e8ea705a` |
| [R56 normalized blocks](../artifacts/autoresearch/waves_ak_to_an_20261024/normalized_r16_to_r56_block_observations_20261024.json) | `ba3eb333663729d1f0f763356a66bfe9b274eb1310011bcd1c06a1edaea6d32e` |

The additive corpus contains212 records:210 primary plus two auxiliary,988 crossed arm/block observations in406 round-scoped matched IDs, and16 separate R17 sequential rows. The previous194 record dictionaries,700 crossed rows and16 sequential rows remain unchanged. The new campaign contributes18 arms,288 arm/block observations and144 matched block IDs.

The initial AL calculation actually used normalizer build1 SHA`65365d40a53d0a811831a26c0ff37d5c8d279d97a08987240360465b3585b45f`. Its exact archived source is retained. The final normalizer SHA`a40a52df2b17c05045a6a77935d1d27ae5635c903083d7f2550c9b6f02ea9e50` adds integrity/parser/output-preflight guards; fresh serialization reproduces the same two canonical dataset files byte for byte. The receipt records both versions honestly rather than rewriting which code produced the calculation. Prior AG–AJ artifacts and the established normalizer were not modified.

## What the rounds actually vary

Each round has16 genuine matched blocks, with eight AB and eight BA sequences and32 arm/block observations. Every arm saves160 attempted and160 received ICMP samples. Counts below concern the same saved link, not160 independent sectors or16 independently deployed networks.

| Round | Workload | Declared timing context | Target AP/CPE BE low/high, µs | Target AF | Retry limits |
| --- | --- | --- | --- | ---: | --- |
| R48 | bidir6, `-P3 --bidir` | class6 /3000m | `1100/2200` / `2200/4400` | 3 | 5/3 |
| R49 | bidir6 | class13 /6000m | `1100/2200` / `2200/4400` | 1 | 5/3 |
| R50 | bidir6 | **UNKNOWN** | `1500/3000` / `2100/4200` | 1 | 7/4 |
| R51 | bidir6 | **UNKNOWN** | `1500/3000` / `2100/4200` | 1 | 5/3 |
| R52 | bidir6 | class6 /3000m | `1500/3000` / `2100/4200` | 3 | 5/3 |
| R53 | bidir6 | class13 /6000m | `1500/3000` / `2100/4200` | 1 | 5/3 |
| R54 | bidir2, `-P1 --bidir` | **UNKNOWN** | `1800/3600` / `1800/3600` | 1 | 5/3 |
| R55 | bidir4, `-P2 --bidir` | **UNKNOWN** | `1500/3000` / `2100/4200` | 1 | 5/3 |
| R56 | bidir2 | **UNKNOWN** | `1500/3000` / `2100/4200` | 1 | 5/3 |

All listed targets declare `fq_limit=2048` and `force_tx_status=1`. The high-GP asymmetric package has AP threshold6000µs, `tcp_limit_output_bytes=204800`, `tcp_notsent_lowat=102400`; CPE threshold8400µs and327680/163840bytes respectively. Those are200/100KiB and320/160KiB, not invented decimal KB. R48/R49 instead have thresholds4500/9000µs and AP196608/98304bytes, CPE262144/131072bytes. R54 has symmetric threshold7200µs and262144/131072bytes at both endpoints. Full policy IDs preserve every remaining recorded coordinate; these packages cannot be collapsed into a single BE value or attributed to one knob.

Class6/13 and3000/6000m are shared payload/treatment/knob declarations backed by the frozen distance-application recipe. The original endpoint-state objects omit the timing field; this provenance is disclosed by the normalizer. **CONFIRMED:** programmed timing declaration. **UNKNOWN:** actual geographic separation and physical range performance. R50/R51/R54/R55/R56 do not record the narrated100m/class0 context, so both fields remain `None`. No baseline distance or coverage is imputed.

## Saved outcomes across all nine rounds

The following display tables round GP/DL/UL to six decimal places and Jain to six places for readability. They are not inputs to equality checks: the exact literals, full binary64 values, block values and policy identities remain in the pinned JSON.

| Round / arm | Total GP, Mbps | DL, Mbps | UL, Mbps | Jain |
| --- | ---: | ---: | ---: | ---: |
| R48 stock | 103.506836 | 87.425781 | 16.081055 | 0.677917 |
| R48 target | 90.305664 | 64.586914 | 25.718750 | 0.843506 |
| R49 stock | 94.123047 | 79.417969 | 14.705078 | 0.679077 |
| R49 target | 81.812500 | 57.323242 | 24.489258 | 0.860229 |
| R50 stock | 109.046875 | 91.797852 | 17.249023 | 0.681580 |
| R50 target | 107.682617 | 81.702148 | 25.980469 | 0.788330 |
| R51 stock | 108.011719 | 91.255859 | 16.755859 | 0.677734 |
| R51 target | 102.666992 | 77.742188 | 24.924805 | 0.790649 |
| R52 stock | 103.355469 | 87.568359 | 15.787109 | 0.674744 |
| R52 target | 97.826172 | 74.125977 | 23.700195 | 0.789795 |
| R53 stock | 94.956055 | 79.513672 | 15.442383 | 0.687073 |
| R53 target | 89.906250 | 66.731445 | 23.174805 | 0.809509 |
| R54 stock | 107.269531 | 95.641602 | 11.627930 | 0.620056 |
| R54 target | 103.513672 | 90.639648 | 12.874023 | 0.639282 |
| R55 stock | 108.599609 | 94.174805 | 14.424805 | 0.649841 |
| R55 target | 104.104492 | 83.531250 | 20.573242 | 0.732239 |
| R56 stock | 107.217773 | 95.562500 | 11.655273 | 0.620117 |
| R56 target | 102.988281 | 88.974609 | 14.013672 | 0.653748 |

| Round | Stock p50 / p95 / p99, ms | Target p50 / p95 / p99, ms |
| --- | --- | --- |
| R48 | 24.9490 /51.7817 /61.0842 | 6.2875 /21.2222 /28.5447 |
| R49 | 27.8440 /52.9303 /63.3893 | 5.9700 /13.6770 /22.1146 |
| R50 | 24.4545 /47.2005 /55.2480 | 7.7650 /24.4283 /31.6652 |
| R51 | 23.3805 /44.4436 /54.2596 | 7.6760 /21.9304 /40.4810 |
| R52 | 22.8675 /44.5859 /51.1681 | 7.0745 /22.4833 /30.3566 |
| R53 | 27.7800 /50.9025 /58.9099 | 6.6475 /16.7597 /29.9678 |
| R54 | 11.4530 /20.9250 /26.4502 | 7.0905 /16.9486 /21.5480 |
| R55 | 19.2915 /33.8893 /43.1979 | 7.6540 /21.0097 /32.7946 |
| R56 | 10.5010 /20.3092 /24.8703 | 5.9715 /13.9067 /18.7355 |

Every one of these18 arms reports loss0, drops0, restorationTrue,160/160 received pings and chronological concatenation of its actual block RTT arrays. All288 block observations remain present. This is **2,880/2,880 saved ping samples**, not proof of zero loss under every future load. Positive MAC packet denominators and exact block-to-window counter sums are verified. Retry-events/packet is not silently renamed PER or packet loss.

| Round | Observed total-GP loss vs own stock | Stock retry, % | Target retry, % | Target retry lower? |
| --- | ---: | ---: | ---: | --- |
| R48 | 12.753913% | 0.223156 | 0.211310 | Yes |
| R49 | 13.079206% | 0.195864 | 0.188693 | Yes |
| R50 | **1.251075%** | 0.193832 | 0.206532 | **No** |
| R51 | 4.948284% | 0.212317 | 0.200649 | Yes |
| R52 | 5.349786% | 0.216893 | 0.230125 | **No** |
| R53 | 5.318044% | 0.206809 | 0.200630 | Yes |
| R54 | 3.501329% | 0.198436 | 0.176489 | Yes |
| R55 | 4.139165% | 0.186969 | 0.194447 | **No** |
| R56 | 3.944768% | 0.168919 | 0.184398 | **No** |

Only R50 passes the observed2% GP-preservation floor among these nine comparisons. Its exact target retry ratio is`1254/607169`, exceeding stock`1301/671200`; printed percentages are not the comparison inputs. R52/R55/R56 also raise retry. No adverse result is removed because its recipe called the treatment KEEP.

## Specification discrepancies and source priority

The four explicitly audited stock-GP discrepancies are nonzero source-literal differences, not merely a choice of float reduction order:

| Stock arm | Specification, Mbps | Frozen source, Mbps | Source minus specification |
| --- | ---: | ---: | --- |
| R48 | 104.072265625 | **103.5068359375** | `-579/1024`Mbps |
| R49 | 94.158203125 | **94.123046875** | `-9/256`Mbps |
| R52 | 103.3564453125 | **103.35546875** | `-1/1024`Mbps |
| R53 | 94.9599609375 | **94.9560546875** | `-1/256`Mbps |

The detailed saved DL/UL, Jain and RTT tables above likewise override the spec's prose examples. The42 specified **win counts** are confirmed; this does not validate every narrated summary value. R50's loss is1.251074652529%, not the literal1.2502%. The specification's100m/class0 narrative for five rounds is unsupported by the frozen declarations and remains UNKNOWN. The FMX objective named`fmx_loss` is a composite objective, not measured ICMP packet loss; a decrease in that objective cannot be described as packet-loss reduction when both measured arms have loss0.

## Exact paired inference and multiplicity

The [family recipe](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_family_recipe.json), SHA`256b31a78331b4a30f07c678a20a795855dff6192a2e506b057c5c0c76dc533e`, was frozen before new outcome computation. This was a **retrospective analysis plan**, not preregistration before physical acquisition. Its primary family is nine rounds times six outcomes: total GP, p50, p95, p99, UL and Jain. All54 contrasts, including adverse GP effects, are retained.

| Family | Known hypotheses | Declared size | Treatment of unknown tests |
| --- | ---: | ---: | --- |
| Primary new exact rank | 54 | 500 | 446 explicit p=1 padding hypotheses |
| Complete-known exact rank | 777 prior +54 new =831 | 831 | No padding; not all project research tests |
| Secondary mean sign-flip | 54 | 500 | 446 explicit p=1 padding hypotheses; separate statistic |

Scoped Holm500 is not a project-wide500-test claim. **Holm500 is inapplicable to the complete-known831 scope.** The primary scoped family rejects45/54 nulls; rejections include adverse outcomes and are not45 improvements. The complete831 family has96 rejections across old and new hypotheses. The secondary mean family also has45 rejections; agreement does not create independent replication.

For each actual16-pair contrast, all`2^16=65536` sign assignments are enumerated. Rank uses signed doubled midranks with zeros accounted for; the sign diagnostic uses positive-minus-negative counts; the arithmetic-mean test uses exact integer sums after converting the supplied finite float differences to binary Fractions. These are **three different statistics on the same observations**. Two extreme assignments give two-sided p`2/65536=0.000030517578125`; a claim of15 favorable signs alone instead gives sign p`34/65536`, not automatically the signed-rank or mean p-value.

The54 contrasts reuse the same144 actual block IDs across outcomes, yielding864 outcome-specific paired records. That does not mean864 independent physical experiments. Source-decimal subtraction before ranking is a separate sensitivity; no rank or mean p-value changes for these54 contrasts. No source value is silently rounded to manufacture ties or significance.

### Favorable-block counts and the five requested QoE outcomes

Counts below are improvements among16 matched blocks: lower p50/p95/p99, higher UL/Jain. The bracketed value is scoped **rank** Holm500 q where a non-unanimous result matters. All42 counts explicitly stated in the specification match; the remaining three counts are reported as measured without attributing an unstated claim.

| Round | p50 | p95 | p99 | UL | Jain | All five direct scoped-rank outcomes pass? |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| R48 | 16 | 16 | 16 | 16 | 16 | Yes |
| R49 | 16 | 16 | 16 | 16 | 16 | Yes |
| R50 | 16 | 16 | 16 | 16 | 16 | Yes |
| R51 | 16 | 15 (`.0417480`) | 14 (`.262085`) | 16 | 16 | No |
| R52 | 16 | 16 | 15 (`.0279541`) | 16 | 16 | Yes |
| R53 | 16 | 16 | 16 | 16 | 16 | Yes |
| R54 | 16 | 15 (`.454193`) | 14 (`1`) | 10 (`1`) | 15 (`1`) | No |
| R55 | 16 | 15 (`.0694275`) | 15 (`.138245`) | 16 | 16 | No |
| R56 | 16 | 16 | 15 (`.0279541`) | 14 (`.110840`) | 16 | No |

Every unanimous listed contrast has scoped rank q`.0152587890625`; its complete-known831 q is`.02490234375`. Non-unanimous contrasts retain their actual magnitudes/ranks and must be read individually. The existence of15 favorable blocks, a lower pooled p95, or a recipe KEEP label cannot replace the complete outcome conjunction.

### Effect estimates and exact confidence sets
<!-- stage822a-payload-end -->
