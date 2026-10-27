<!-- doc-head: STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT.md) | Part 2/2
<a id="stage12--r48r56-distance-and-goodput-dyadic-audit"></a> [Stage12 — R48–R56 distance and goodput dyadic audit](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#stage12--r48r56-distance-and-goodput-dyadic-audit) | <a id="evidence-identity-and-preservation"></a> [Evidence, identity and preservation](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#evidence-identity-and-preservation) | <a id="what-the-rounds-actually-vary"></a> [What the rounds actually vary](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#what-the-rounds-actually-vary) | <a id="saved-outcomes-across-all-nine-rounds"></a> [Saved outcomes across all nine rounds](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#saved-outcomes-across-all-nine-rounds) | <a id="specification-discrepancies-and-source-priority"></a> [Specification discrepancies and source priority](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#specification-discrepancies-and-source-priority) | <a id="exact-paired-inference-and-multiplicity"></a> [Exact paired inference and multiplicity](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#exact-paired-inference-and-multiplicity) | <a id="favorable-block-counts-and-the-five-requested-qoe-outcomes"></a> [Favorable-block counts and the five requested QoE outcomes](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#favorable-block-counts-and-the-five-requested-qoe-outcomes) | <a id="effect-estimates-and-exact-confidence-sets"></a> [Effect estimates and exact confidence sets](STAGE12_R48_TO_R56_DISTANCE_AND_GOODPUT_DYADIC_AUDIT_CONTINUATION_e52a4b4efe_001.md#effect-estimates-and-exact-confidence-sets)

<!-- stage822a-payload-begin -->

The audit reports54 paired Hodges–Lehmann Walsh pseudomedians and108 marginal exact signed-rank inversion sets:95% and99.9% for every contrast. All108 are finite here. They are not simultaneous confidence sets for500 or831 hypotheses. The interpretation assumes independent symmetric/sign-exchangeable block differences and, for a common shift interpretation, suitable effect invariance; source IDs alone do not prove those assumptions.

R50 examples illustrate the difference between an observed budget and an inferential statement. Numerical endpoints below are display-rounded; exact floating representations, open/closed endpoints and all components are retained in the artifact.

| R50 outcome | Paired HL | Marginal95% acceptance set | Marginal99.9% acceptance set |
| --- | ---: | --- | --- |
| Total GP, Mbps | -1.1953125 | `(-2.40625, -0.359375]` | `[-3.390625, 0.3515625]` |
| p95, ms | -20.6996375 | `[-26.85685, -13.88305)` | `[-33.721775, -9.699775)` |
| UL, Mbps | 9.046875 | `{7.09375} ∪ [7.140625, 10.1484375]` | `[5.5546875, 11.1015625)` |
| Jain | 0.111083984375 | `(0.08935546875, 0.123046875)` | `(0.07470703125, 0.1337890625)` |

The disconnected UL95% set is preserved, not replaced by its convex hull. R50's observed mean GP ratio passes the2% budget, but this is not a prespecified statistical noninferiority analysis: no accepted noninferiority margin/test on independent physical replication is supplied. The broader99.9% GP set includes zero; that does not erase the observed GP cost or turn it into equivalence.

## Period, carryover and the causal boundary

All nine schedules match their actual source steps, with eight AB and eight BA blocks and balanced treatment appearances by period. Independent Fraction Gaussian elimination confirms rank18 for19 columns in the full intercept+block+period+current-treatment+lag-treatment design. Current and differential lag effects are not separately estimable. Counterbalancing does not resolve this structural alias.

A separately named **no-differential-carryover** model has18/18 rank. Its source-decimal direct/period coefficients are computed exactly and cross-checked against least squares; all54 outcome fits are reported as restricted, descriptive point estimates. Dropping lag is an assumption, not a discovery that carryover is zero. The audit provides no invented period-adjusted p-values from the raw paired sign flips.

Within-round matching controls a recorded block and defines a conditional treatment-package contrast. It does not by itself identify a separated causal mechanism, randomization, washout or stable treatment effect. Cross-round target comparisons have an even narrower status: they are descriptive summaries without common matched units or randomized allocation between packages. Neither level establishes an outdoor range or sector-wide improvement.

## Descriptive Pareto interpretation and selector boundary

The AL Pareto view compares only matching **declared** workload, flow count, direction, coverage, timing distance, cipher context and peer labels. Missing context values remain unknown; matching two `None` values is not proof that their unrecorded RF contexts were equal.

- R45/R50/R51 are shown together only in the saved bidir6, unknown-distance/class context. Their endpoint packages differ. R50 retains more GP; R45's latency/UL-oriented tradeoffs are not converted into a common-policy causal effect.
- R48/R52 share the class6/3000m timing context, and R49/R53 the class13/6000m context. Higher target GP in a later round does not constitute a paired improvement over the earlier target: controls, schedules and packages are separate.
- R55's bidir4 and R56's bidir2 contexts remain separate. The symmetric R54 package is not renamed the asymmetric high-GP package.

The nine requested target points remain nondominated within their small, six-objective observed groups when GP/UL/Jain are maximized and three RTT quantiles minimized. This means competing costs remain, not that there is a globally optimal or qualified policy. There is no new/old package pooling or individual AQL/AF/retry causal attribution.

AL's `promotion_evidence` is a source-bound projection of direct rank/HL/Holm500 evidence for the independently implemented AM selector. It does not select, promote or actuate. Legacy STRICT/DIRECTIONAL contracts retain their existing common lower-retry requirement; R50's adverse retry therefore cannot be hidden behind the GP-floor fact. Separately named new operator Pareto contracts, if implemented, must retain their own frozen definitions, health/provenance/history gates and explicit adverse costs. This report does not pre-accept their output or rewrite legacy semantics.

## Auxiliary AK modeling is enabling evidence

The [independent AK review](../artifacts/autoresearch/waves_ak_to_an_20261024/review_wave_ak.json) accepts its dataset/model boundaries with limits, not a calibrated radio model. The [AK model summary](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_ak_models_summary.json) preserves nine non-estimable full carryover models and nine explicitly restricted descriptive OLS fits. Round/block random intercepts are a proposed structure, **not an accepted fitted mixed-effects distribution**.

The grouped surrogate holds out a round and every full endpoint package appearing in its test set from all training rounds. Exact context, training-only encoders/scalers and the same training-mean baseline are used. Of46 folds, eight predict29 windows,31 report unsupported training features and seven have no leak-free support. Conditional errors are:

| Held-out outcome | Surrogate RMSE | Training-mean RMSE |
| --- | ---: | ---: |
| Total GP, Mbps | 24.705718 | 24.412940 |
| p95, ms | 14.180500 | 14.415686 |
| p99, ms | 14.962919 | 15.291725 |

GP prediction is worse than the baseline; modest RTT-error differences apply only to supported windows. Poor fit and unsupported folds remain visible. No heldout accuracy for all212 records or independent sectors is implied. The16 returned proposals are disabled, exact observed packages from43 GP/p95/p99 empirical frontier rows. That three-objective inventory is distinct from AL's six-objective descriptive view; it is not an accepted policy, synthesized optimizer candidate, latency/UL/Jain/retry conjunction or actuator.

## Validation, preserved failures and what remains unknown

The [AL final focused receipt](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_final_tests.json) records29PASS, zero failures/skips, exit0 on pinned source/tests. The first focused run retained22PASS/1FAIL: AH's campaign-specific validator correctly rejected R48, so AL received its own explicit R48–R56 pairing boundary instead of mutating AH or relabeling IDs. The [first failure](../artifacts/autoresearch/waves_ak_to_an_20261024/wave_al_synthetic_tests_1.json), changed-hypothesis checks and an unsuccessful optional historical-source reconstruction remain preserved. No prior failure is rescored as passing.

The independent coordinator checked54 contrasts,864 source pairs,162 rank/sign/mean tails,54 HL estimates,108 confidence sets with25,524 membership probes,54 restricted period estimates and nine exact rational designs. It imported no AL implementation under review for the numerical oracle. That external review is distinct from this report's authorship. AK's32 dataset and68 model tests are separately source-bound; a repository-wide acceptance claim belongs only to the coordinator's eventual final validation, not to these focused counts.

Methodological guidance came from four local skills: [statistical-analysis](../.agents/skills/statistical-analysis/SKILL.md), [experimental-design](../.agents/skills/experimental-design/SKILL.md), [statistical-power](../.agents/skills/statistical-power/SKILL.md) and [scientific-critical-thinking](../.agents/skills/scientific-critical-thinking/SKILL.md). Their online bibliography and example version claims were not verified online. Actual software versions are recorded in the artifact; no dependency was installed. The exact16-block p floor is a conditional detectability fact, not observed/post-hoc power or an independent-sector sample-size guarantee.

Remaining factual limits are concrete: effective lower-layer hook authority, unrecorded timing in five rounds, physical3km/6km performance, independent health verification, washout/randomization, separable carryover and independent-sector reproducibility are not established. These unknowns do not require new RF experiments to close this offline report. They prevent physical, causal or production claims from being inferred from it. AM evaluation and AN documentary/final-suite acceptance remain separate coordinator-owned work; no hardware action follows automatically.
<!-- stage822a-payload-end -->
