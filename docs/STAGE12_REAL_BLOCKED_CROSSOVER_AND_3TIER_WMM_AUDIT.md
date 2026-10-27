<!-- doc-head: October24 offline Q-T real blocked crossover and three-tier audit -->
Eighteen frozen R16-R21 files extend the preserved89-record corpus to112 records.
Eighty-eight crossed rows represent24 matched within-link blocks; R17 has 16 sequential rows.
Exact paired effects remain conditional; Holm81 accepts no treatment-effect contrast.
Reported summaries conflict with saved blocks; both survive and new promotion abstains.
ACK/VI constraints are advisory, typed and opt-in; device access and liveR22 are excluded.
<!-- /doc-head -->

# Stage12: real blocked crossover and three-tier WMM audit

Research ID: `FMX-OFFLINE-WAVES-QRST-20261024`. Parent: the Stage12 control-authority and experimental-methodology deliverables in `artifacts/2026-09-20-forward-plan.html` and the current Q-T section of [BENCH_PLAN](BENCH_PLAN.md). This is a retrospective computational audit of saved physical data, without conducting a new physical experiment or a preregistration. The current source, frozen data, exact numerical checks and independent reviews define its acceptance boundary.

## What the saved data answer

**CONFIRMED within the frozen records:** R16 has genuine treatment-by-block IDs and crossover steps. Its asymmetric and symmetric packages both have lower received-ping block p95 than stock in all eight saved blocks. Their aggregate-goodput shifts remain uncertain. R19's unpaced marking package shows a substantial goodput cost, especially with both endpoints marking traffic to VI. Lower pacing rates in R20 reduce that observed cost; R21's micro-paced versions do not show a clear latency advantage over the zero-pps package. None of these observations certifies a portable mechanism or an operational setting.

**INCONCLUSIVE under the declared joint family:** all 81 paired signed-rank tests fail to reject after Holm81; the minimum adjusted p-value is 0.6328125. This does not prove zero effect. Four-block contrasts cannot reject a two-sided exact sign/rank null at 0.05 even before multiplicity; their marginal 95% exact shift confidence sets are the whole real line. R16's unadjusted p-values and marginal intervals are exploratory and cannot substitute for the declared family result.

**CONFIRMED data-quality limit:** every one of the 23 new windows has at least one discrepancy larger than 0.021 Mbps between reported summary goodput/directional values and the corresponding block means or directional sum. Both representations are preserved. Paired analyses use actual saved block values, while the controller abstains from promoting any new inconsistent package. No original measurement was rewritten to make these agree.

**UNKNOWN:** inter-block independence, treatment randomization, effective cipher/offload costs, actual pure-ACK classification, successful on-air TID/AC mapping, adequate washout, performance on additional links/sectors, and physical 3 km range. A programmed3000m coverage/timing setting is not a distance measurement. Nothing here accepts the M-P simulator as a physical predictor.

## Frozen acquisition boundary and units

All 18 source files were copied into the new owned `waves_qrst_20261024/inputs` directory before their contents were inspected: six JSON receipts, six matching TSVs and six bench recipes. The [manifest](../artifacts/autoresearch/waves_qrst_20261024/inputs_manifest.json) records source names, owned paths, byte counts, copy timestamps and SHA256 values. After copying, only the frozen copies were used. Recipes were read as text; none was imported or executed. Antigravity owns the live Round 22 bench, which was neither inspected nor contacted.

| Round | New primary windows | Crossed treatment rows | Matched block units | Other repetitions | Design boundary |
|---|---:|---:|---:|---:|---|
| R16 |3|24|8|0| Three arms; eight supplied sequences, not a literal two-arm ABBA design |
| R17 |4|0|0|16| Sequential repetitions; no crossover_step or counterbalanced schedule |
| R18 |4|16|4|0| Four-arm schedule; declared 3000 m timing/coverage |
| R19 |4|16|4|0| Four-arm three-tier marking comparison |
| R20 |4|16|4|0| Four-arm400pps AP /150pps both marking comparison |
| R21 |4|16|4|0| Four-arm50pps both /80pps AP marking comparison |
| Total |23|88|24|16| One physical AP/CPE link, not24 independent sectors |

The [112-record normalized output](../artifacts/autoresearch/waves_qrst_20261024/normalized_r1_to_r21_measurements_20261024.json) retains110 primary windows and two earlier summary-only validations. The original 89 records retain their exact fields and joint-policy identities; the earlier R15 count discrepancy is not filled with a fabricated record. Legacy APIs continue to return58,85 and89 records. New records preserve their original reported summaries, raw RTT membership, typed ACK/VI controls, reported CPU medians, repetition-level CPU samples and source pointers.

The [block output](../artifacts/autoresearch/waves_qrst_20261024/normalized_r16_to_r21_block_observations_20261024.json) keeps crossed and sequential rows in separate collections. A unit key is `(round_id, block_index)`; a crossed observation also has the supplied `crossover_step` and treatment ID. Reused R17 indices 0..3 are not pairing evidence. The loader rejects missing/boolean IDs, duplicate units, inconsistent ping membership/counts, impossible quantiles and conflicting declarations. It rejects URLs/UNC paths before filesystem probes and completes genuinely missing local-input checks as `UNKNOWN_LOCAL_ARTIFACT_ABSENT`.

R19 stock and R21 stock each retain a 9/10 received-ping block:39/40 received pings at window level and 2.5% recorded loss. No lossful row was dropped. Window restoration flags are retained as window evidence and never copied into unknown per-block restoration/station-drop fields. Zero MAC TX packet denominators yield an unknown retry fraction; reported zero is not accepted as zero PER or zero MAC retries.

## Paired statistical contract

[Wave R analysis](../artifacts/autoresearch/waves_qrst_20261024/wave_r_real_crossover_analysis.json) and [methods](../artifacts/autoresearch/waves_qrst_20261024/wave_r_methods.md) retain every planned contrast and the explicit retrospective analysis choices. There are 27 within-round treatment pairs across R16/R18/R19/R20/R21, each evaluated for total goodput, block p95 and block p99:81 primary exact signed-rank tests with global Holm81. Per-outcome Holm27 is labeled secondary exploratory output. Exact sign tests provide a named sensitivity analysis. Pooled received-ping analysis is a separate 33-test Mann-Whitney family with Holm33; it is not evidence from 33 independently randomized physical trials.

Every paired outcome is treatment minus control within the supplied block ID. Repeated values in a multi-observation arm are aggregated within block, not counted as more experimental units. Signed-rank probabilities enumerate the exact conditional sign distribution with tie-aware midranks and Wilcox zero removal. The sign test conditions on the nonzero signs. Walsh terms estimate the paired pseudomedian; the n(n+1)/2 terms are derived values, not new independent blocks.

Exact shift confidence sets invert the same signed-rank test over all Walsh breakpoints and intervening cells. The output retains open/closed endpoints, isolated accepted points and any disconnected components; the earlier conservative hull is also retained. Null endpoints mean negative/positive infinity. All81 Bonferroni simultaneous confidence sets span the real line at these sample sizes. A finite marginal interval cannot be advertised as a family-adjusted physical confidence interval.

These exact calculations still require independent, appropriately symmetric location-shift block differences for their usual location interpretation; the sign test has its own nonzero-sign null. Counterbalanced IDs do not prove these assumptions. The design audit retains all arms while computing period/sequence/lag diagnostics; other arms are excluded only from each explicit two-arm numerical contrast. No C/D observations are relabeled as controlA.

### Representative paired effects

The following shifts are Walsh pseudomedians from saved blocks. Positive goodput favors treatment; negative p95 favors treatment. Every shown contrast has Holm81 p>=0.6328125. For n4, the marginal 95% exact confidence set is unbounded; numerical shifts describe this dataset and do not establish a precise population effect.

| Round and treatment versus control | Blocks | Goodput shift Mbps | Block-p95 shift ms | Exact p: goodput / p95 |
|---|---:|---:|---:|---|
| R16 asymmetric versus stock |8|+0.700|-23.255|0.546875 /0.0078125 |
| R16 symmetric versus stock |8|+0.050|-20.979|1.000000 /0.0078125 |
| R16 symmetric versus asymmetric |8|-0.425|+1.901|0.640625 /0.4609375 |
| R18 BE1900 versus BE1800, both threshold7200 |4|-0.350|+8.327|0.375 /0.375 |
| R19 unpaced VI AP versus VO-only |4|-13.750|-6.500|0.125 /0.625 |
| R19 unpaced VI both versus VO-only |4|-31.175|-16.433|0.125 /0.125 |
| R20 VI400pps AP versus VO-only |4|-11.400|-6.706|0.125 /0.25 |
| R20 VI150pps both versus VO-only |4|-9.825|-8.369|0.125 /0.125 |
| R21 VI50pps both versus0pps |4|-3.300|+3.499|0.125 /0.375 |
| R21 VI80pps AP versus0pps |4|-1.150|+5.642|0.5 /0.625 |

R16 asymmetric-minus-stock marginal 95% exact p95 shift set is the open interval(-31.28,-16.4535)ms; the total-goodput shift set is(-1.7,3.2)Mbps. R16 p95 improvements occur in 8/8 saved blocks, with exact unadjusted sign p 0.0078125. This is a conditional within-link signal; the joint family remains inconclusive and the observation does not establish that asymmetry itself caused the gain independently of the rest of each package.

R18's specified BE comparison changes only BE low/high on both endpoints, from1800/3600 to1900/3800, while both thresholds remain 7200 us and both declared timing distances remain 3000 m. Its p99 shift is +10.455 ms with exact p 0.625. It provides no accepted causal benefit for BE1900. Other round/package differences are not isolated single-knob mechanisms.

![Saved raw block outcomes](../artifacts/autoresearch/waves_qrst_20261024/real_crossover_block_outcomes.svg)

Each plotted line is one matched block within its round. The [plot script](../artifacts/autoresearch/waves_qrst_20261024/wave_t_make_figure.py) and [figure receipt](../artifacts/autoresearch/waves_qrst_20261024/wave_t_figure_receipt.json) bind the original block output. Values are not replaced by inconsistent window summaries. Plotting was retrospective descriptive visualization, not prospective test selection.

### Period, sequence and carryover

The saved labels are design claims to inspect. R16 contains three treatments in three periods and eight blocks with repeated sequences, so its name`abba` is not a two-treatment ABBA schedule. R18-R21 use the same four-sequence Latin/Williams-style schedule. Period counts, actual ordered sequences, directed prior-treatment transitions and categorical current/lag design ranks are reported explicitly. R16's 8 sequences cannot give equal counts of every treatment in each of 3 periods; do not describe it as perfectly balanced.

The stated categorical diagnostic matrix with block, period, current treatment and categorical lag has rank 14/14 in R16 and 13/13 in each four-arm round. There are only 10 and 3 residual degrees of freedom respectively before adding additional structure. Sequence is fixed within a block; an independent sequence fixed effect is aliased with block fixed effects. Full column rank in the stated simplified matrix permits an algebraic fit, not a credible no-carryover or randomized treatment estimate. The recipes' waits and saved step ordering do not prove washout, clock synchronization or effective transition completion.

### Conditional pings and R17 CPU/cipher

Eight of 33 pooled-ping MWU contrasts have Holm33 p<0.05. All 33 are retained, including non-rejections. These are conditional comparisons of received RTT samples and can reflect serial dependence, lost-packet censoring and block/period structure. Tail intervals use1999 seeded empirical bootstrap resamples per window at q 0.95 and 0.99; they are not independent-block or sector-level confidence intervals. With n=40 received pings, the chance of even observing a value beyond a true iid99th percentile is only1-0.99^40≈33.1%; with n=80 it is≈55.2%. A narrow empirical p99 bootstrap interval cannot repair sparse-tail information.

R17 preserves all 16 sequential repetition-level CPU observations. Comparing the same named symmetric package under recorded WPA2 versus open mode, the recomputed AP busy medians are 83.35% and 89.055% (open-minus-WPA2:+5.705 percentage points); softirq medians are 53.64% and 53.595% (-0.045 percentage points). Reported rounded medians are retained separately. These load fractions are not isolated cipher cycles, throughput-normalized crypto cost, effective hardware offload evidence, or a randomized crossover. There is one sequential window for each policy/cipher combination, so time, queue behavior and offered-load response remain confounded. No paired p-value is fabricated from the reused sequential repetition indices.

Exact two-sided p floors are 0.125 for n4 and 0.0078125 for n8 without zeros. At least6 such blocks are needed merely to make an unadjusted p<=0.05 attainable; at least 12 are needed to cross the first Holm81 threshold in the most favorable sign pattern. These are attainability limits, not 80% power or a sample-size recommendation. No observed-power calculation or invented effect size is supplied. A future fixed replication would need an operator-approved estimand, practically important effect, independent-unit definition, uncertainty assumptions and matching power analysis; this report does not authorize it.

## Advisory controller and control boundary

[Controller source](../controller/adaptive_aql_regime_controller.py) accepts the full corpus through:

```python
from orchestration.autoresearch.fmx_offline_data import load_all21_measurements
from controller.adaptive_aql_regime_controller import AdaptiveAQLRegimeController

records, source_refs = load_all21_measurements()
controller = AdaptiveAQLRegimeController(records, include_three_tier=True)
```

`include_three_tier=False` is the compatible default; all 23 new rows remain opt-in. With opt-in, selectors support`ap_ack_pps`,`cpe_ack_pps`,`ap_tcp_ack_vi`,`cpe_tcp_ack_vi` as exact optional constraints. Omitted means unconstrained; explicitNone matches unknown only;0/False means declared disabled. Integers are exact integers, not booleans or numeric strings. Burst size is also part of the complete joint-package identity even though it is not an independent selector knob. CPU metrics and observed outcomes never enter a policy ID.

Legacy unknown-ACK packages are canonicalized consistently in opt-in mode so old negative evidence cannot be evaded by a new schema alias. Default legacy package IDs, selections and hysteresis remain compatible. Exact constraints apply before support thresholds, candidate ranking and hysteresis. No field is independently synthesized into a new endpoint package; the result is a complete observed package or an explicit abstention. The [executed examples](../artifacts/autoresearch/waves_qrst_20261024/wave_s_offline_examples.json) and [S methods](../artifacts/autoresearch/waves_qrst_20261024/wave_s_methods.md) retain actual source IDs and exclusion reasons.

All 23 new inconsistent summaries are visible as unusable evidence for promotion, including the two genuine loss negatives. A summary mismatch is not relabeled as wireless loss or instability. Requests for known 0/False/50/True ACK declarations abstain with this real corpus; an explicit unknown query can still select a previously supported R1-R15 unknown-ACK package, which is not acceptance of a new R16-R21 treatment. Valid disposable fixtures verify the new constraint paths independently of this physical-data limitation.

| Behavior | Layer / boundary |
|---|---|
| Snapshot integrity, block pairing, inference, exact-package filtering | External offline analysis/controller |
| nft packet marking and rate/burst policy described in frozen recipes | Linux networking; source declaration/readback text |
| FQ/CoDel and per-AC AQL declarations | Linux/mac80211 configuration context |
| Effective firmware queues, CCMP offload, on-air ACK/TID/AC behavior | UNKNOWN from these artifacts |
| Proprietary airMAX TDMA behavior or hardware acceleration | Not measured or modified by this program |

The frozen marking expression uses small TCP packet length and a rate/burst limiter; a label saying`pure ACK` is not proof that only ACK-flag packets were classified. An nft rate rule can limit which packets get marked rather than dropping or shaping all TCP ACK traffic. Effective packet classifications, hardware-queue admission and measured ACK rates are unverified. `ap_ack_pps`/`cpe_ack_pps` preserve the declared rule rates, not confirmed on-air ACK pacing.

## Verification, scientific guidance and disposition

Final verification and separate Q/R/S/documentary review receipts are linked by [final validation](../artifacts/autoresearch/waves_qrst_20261024/final_validation.json). The [combined pytest receipt](../artifacts/autoresearch/waves_qrst_20261024/focused_pytest_run_1.json) records the actual exit code, counts, selected offline suites, environment and current source hashes. The fresh combined run passed **501 tests**, with zero failures, errors or skips, exit0, across14 pure offline suites:411 prior M-P cases plus40 Q,24 R and26 S cases. Independent Q and S reviewers executed123 and112 affected tests respectively; the independent R reviewer used this combined current-revision run and a separate brute-force oracle. No full-suite rerun was needed after documentation-only edits.

Q's missing-file handling and the new output directory initially failed; both actual failures remain in the owned artifacts, followed by targeted regressions and corrected checks. R's initial analysis dependency hash was stale after Q's output-boundary fix; that artifact and receipt are preserved, and the result was regenerated under the actual dependency version. Independent review is separate from implementation. Source/static/numerical acceptance does not imply deployment, physical wireless acceptance, recovery qualification or effective firmware control.

The seven requested local scientific skills materially guided this report: [experimental-design](../.agents/skills/experimental-design/SKILL.md) for units, counterbalancing and pseudoreplication; [statistical-analysis](../.agents/skills/statistical-analysis/SKILL.md) for retrospective families, effects and uncertainty; [statistical-power](../.agents/skills/statistical-power/SKILL.md) for discreteness/attainability and avoiding observed power; [scientific-critical-thinking](../.agents/skills/scientific-critical-thinking/SKILL.md) for confounding and source-to-claim limits; [hypothesis-generation](../.agents/skills/hypothesis-generation/SKILL.md) for rival explanations and explicit evidence boundaries; [pymoo](../.agents/skills/pymoo/SKILL.md) and [simpy](../.agents/skills/simpy/SKILL.md) for keeping optimizer output, numerical verification and physical model validation distinct. No new optimizer/simulation run was needed for Q-T; the existing M-P physical predictor rejection and disabled candidates remain in force.

Local skill metadata requests this reference: Kassis,T., Agarwal,V., He,Y., Patel,D., and Brueckner,A.M.(2026), *Scientific Agent Skills: A Library of Procedural Knowledge for Research Agents*, arXiv:2609.00065, DOI10.48550/arXiv.2609.00065. It is transcribed from installed SKILL.md metadata and was not independently verified online under the operator's offline instruction. This attribution is not validation of the scientific findings.

**Disposition:** KEEP the tested offline normalizer, exact statistical tooling and constrained advisory representation. Preserve the observed R16 latency signal and R19-R21 tradeoffs as conditional exploratory results. Do not claim a family-accepted gain, a proven crypto mechanism, no carryover, a3km deployment result or a safe active ACK setting. Data-quality abstention remains binding for all 23 new windows. Historical local binaries absent from this work finish`UNKNOWN_LOCAL_ARTIFACT_ABSENT` checks without blocking. No radio access, online install, target execution, flash, deployment, commit/push or live Round 22 action occurred or is queued. The requested offline scope ends with revision-bound artifacts and reviews; a new physical experiment would be a separate operator-controlled task.
