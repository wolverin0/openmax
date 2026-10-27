<!-- doc-head: Offline R1-R9 regime models, per-AC sensitivity and adaptive selection -->
All58 saved windows are normalized with endpoint, sample and source provenance.
Native NSGA-II/III cover three regimes; bidirectional surrogate errors exceed mean baselines.
Native per-AC SimPy has worse held-out R7-R9 errors than its uniform structural comparator.
Adaptive selection is a bounded offline heuristic over observed policy pairs, without actuation.
Missing historical files close as UNKNOWN_LOCAL_ARTIFACT_ABSENT; no physical acceptance follows.
<!-- /doc-head -->

# Stage12 — multiflow, per-AC model and audit

Waves E–H deliver an offline implementation and a qualified negative prediction result. The richer models do **not** demonstrate an improvement in prediction accuracy or wireless performance. Their datasets retain failures and errors; candidate generation and adaptive selection remain disconnected from devices.

The parent is `FMX-OFFLINE-WAVES-EFGH-20261024` in [BENCH_PLAN](BENCH_PLAN.md), supporting Stage12 control-authority and experimental-methodology research. Antigravity owns live execution. This program read local files, ran host numerical libraries and disposable tests, and did not import or execute the acquisition recipes, contact radios/network devices, use SSH, install dependencies or execute target firmware.

## E: normalized evidence

The [input manifest](../artifacts/autoresearch/waves_efgh_20261024/inputs_manifest.json) binds nine receipts and nine frozen acquisition recipes by SHA256. The [normalized dataset](../artifacts/autoresearch/waves_efgh_20261024/normalized_r1_to_r9_measurements_20261024.json) contains all58 windows. Counts R1..R9 are **8,5,7,7,6,7,6,6,6**. Receipt experiment identities determine rounds, independently of input path order.

| Regime | Rounds | Windows | Recorded workload and endpoint treatment |
| --- | --- | ---: | --- |
| `bulk_unidirectional` | R1–R4 |27 | Two parallel DL TCP flows; AP changes. CPE baseline policy is unrecorded. |
| `bidir_2flow` | R5–R6 |13 | One DL and one UL TCP flow; separate AP/CPE policies, including asymmetric pairs. |
| `bidir_6flow` | R7–R9 |18 | Three DL and three UL TCP flows; R8/R9 include symmetric per-AC packages and R9 DSCP treatment. |

Workloads and applied endpoint roles are bound to the frozen recipes, not inferred from headline summaries. Reading those recipes does not prove effective firmware state. The normalizer preserves VO/VI/BE/BK order, both low/high limits, threshold, FQ quantum, raw RC, RTS and declared DSCP flags. Omitted optional RIFS/PSHACK/aggregation controls remain unknown. Bulk CPE policy remains `None`; no stock values are invented.

R1–R4 retain two receiver-goodput samples per window. R5–R9 report two repetitions but do not retain the raw directional samples; their sample tuple stays empty and DL/UL means stay separate. No two-point confidence interval is fabricated. R6 stock records105.825 Mbps in its observation versus105.83 serialized total and105.82 from rounded direction means; bounded serialization differences are flagged, not silently repaired. Reported latency quantiles are retained where arrays rounded to0.01 ms produce differences up to0.005 ms.

MAC retry-events/tx-packets in R3–R9 is validated against its counters. It is neither PER nor a measurement of both endpoints' wireless retries. R1/R2's reported TCP proxy stays separate. RTTs are sparse subsamples of a sequential single-link window, not independent experimental repetitions or well-resolved p99 evidence.

Five windows report5% packet loss: R6 iter1, R7 iter1, and R8 iter1/4/5. They remain in normalization and prediction diagnostics. Reported restoration and zero drops are recorded claims, not independently reacquired acceptance. Negative observations cannot be discarded when constructing the adaptive policy pool.

The user explicitly permits missing historical files to complete their check as `UNKNOWN_LOCAL_ARTIFACT_ABSENT`. LTU2.4.0 attribution is recorded that way and does not gate E–H. Its scientific cause has not been discovered by this permission.

## F: regime surrogate and multi-objective search

[Optimizer source](../orchestration/autoresearch/fmx_doe_and_pymoo_optimizer.py) fits three separate RBF ridge models. Each endpoint contributes23 fixed-scale features, including unknown/presence indicators; AP+CPE gives46. Fixed ridge0.2 and length scale0.75 define the study. Goodput, latency, achieved direction ratio, fairness and retry outcomes are not predictor features. This avoids using held-out outcomes as covariates.

Round nuisance means are learned from training rows only. An unseen round uses the training regime mean. The policy holdout removes the entire core AP+CPE package across rounds/regimes, grouping more conservatively than optional-field equality; the round holdout removes an entire round. Both methods predict all58 windows. Neither method resolves time/environment confounding, adaptive selection or transport to another link.

Errors below are goodput Mbps / p95 ms / p99 ms, rounded for display. The baseline is the same-regime training mean for the same held-out targets.

| Holdout | Regime | Surrogate RMSE | Mean-baseline RMSE |
| --- | --- | --- | --- |
| Core policy | Bulk |8.222 /7.556 /8.244 |22.459 /9.304 /10.673 |
| Core policy | Bidir2 |1.353 /4.255 /3.955 |1.293 /3.912 /3.671 |
| Core policy | Bidir6 |11.656 /17.420 /30.065 |9.534 /16.639 /26.357 |
| Whole round | Bulk |26.714 /9.102 /10.594 |27.982 /9.944 /11.694 |
| Whole round | Bidir2 |1.255 /4.636 /3.712 |1.205 /3.683 /3.440 |
| Whole round | Bidir6 |9.915 /19.852 /27.619 |9.477 /18.136 /27.052 |

Both bidirectional models underperform the mean baseline on all three targets under both holdouts. Bulk's lower policy-held-out error includes known-round nuisance information that the regime-mean baseline does not receive, so it does not isolate the benefit of policy interpolation. Its whole-round goodput error remains substantial. These results do not support validated bidirectional predictions or a physical optimum.

The [Pareto dataset](../artifacts/autoresearch/waves_efgh_20261024/pareto_r1_to_r9_candidates_20261024.json) contains actual native pymoo NSGA-II and NSGA-III runs for each regime: population40,24 generations, seed20261024. Search dimensions choose a declared AQL/optional-control profile package per endpoint, then finite FQ/raw-RC/DSCP levels. Low/high/threshold dependencies stay intact; AP/CPE combinations may differ. Domains contain480,6750 and36864 combinations respectively. The frontier is an approximation, not a global optimality certificate.

The six runs return79 proposal rows;74 rows describe joint combinations not previously measured. Rows across algorithms are not claimed as distinct policies. A support radius0.9 to a reported-stable reference is a model geometry constraint, not a device-safe range or probability of stability. Any exact same-regime joint pair with a known loss/drop/restoration failure is excluded from proposals. All58 windows still contribute to calibration diagnostics. Outputs explicitly disable automatic execution and physical qualification. Unseen DSCP treatment metadata checks both endpoints.

## G: native per-AC SimPy sensitivity model

[Simulator source](../tools/sim/fmx_simpy_ptmp_aql_rc_sim.py) adds per-sender/peer/AC pending airtime, separate DL/AP and UL/CPE policies, and per-flow queues. Pending airtime includes in-flight packets. Admission uses the AC's high/low limits and the sender's total threshold. The shared server uses declared VO/VI/BE/BK weights4/3/2/1 and bounded deficit-assisted flow round robin. This is a model rule, not a reproduction of EDCA, Linux FQ, firmware rate control or proprietary TDMA.

UDP/ICMP packets strictly below256 modeled bytes receive EF46 when the declared steering flag is enabled. Mapping EF micro packets to VO is an **unverified model assumption**. The retained nft recipe sets DSCP; it does not independently establish the effective TID/AC mapping. TCP and256-byte packets do not enter this micro rule. Model packet length is not an inferred wire/header trace.

The [prediction grid](../artifacts/autoresearch/waves_efgh_20261024/wave_g_predictions_20261024.json) covers128 scenarios:1..16 peers × two AQL profiles × steering off/on × per-AC/uniform variants, with three replications each. Synthetic traffic supplies six TCP flows per peer sharing120 Mbps sector load, plus small ICMP/UDP probes. All four ACs are implemented and tested; the grid's bulk is BE and steered probes exercise VO, without inventing observed VI/BK shares. WA/XC efficiency1, SXT/LBM5 efficiency0.5, collision0.1, weights, jitter, profiles and horizon are declared assumptions.

Every run enforces finite packet/event/flow/horizon caps and packet/queued-airtime conservation. Caps abort rather than certify completion. A seed-role overlap found during implementation was preserved, reproduced and repaired using disjoint integer blocks; paired variants intentionally share random streams while separate replications use disjoint role seeds.

Throughput counts post-warmup completed TCP payload; probe goodput is separate. Latency uses completed micro-packet queue/service time plus a training-only phenomenological RTT anchor. It is not a two-leg trace or TCP feedback model. Censored packets and cohort boundaries remain explicit. With probes configured but none completed, latency stays missing rather than borrowing bulk latency. Monte Carlo intervals describe variation conditional on this model, excluding model, parameter and transport uncertainty.

### R7–R9 matched held-out result

The [validation dataset](../artifacts/autoresearch/waves_efgh_20261024/wave_g_heldout_validation_20261024.json) evaluates all18 R7–R9 windows, removing each complete joint policy across the same-regime rounds. Both variants use identical remaining training IDs, target layouts, offered loads, horizons and paired random streams. Four lossful held-out windows remain in the error table. A regression changes held-out outcomes and confirms predictions do not change.

| Model | Goodput RMSE Mbps | p95 RMSE ms | p99 RMSE ms |
| --- | ---: | ---: | ---: |
| Per-AC/EF model |9.801 |26.063 |37.716 |
| Structural pooled/uniform comparator |9.602 |25.864 |37.361 |

The per-AC model is worse on all three targets. No tuning was applied to turn this negative result into a pass. The comparator collapses AC admission to BE and uses uniform flow visits with its corresponding feature projection. It is a matched structural comparator, not bit-identical legacy A-D code. Both representation and scheduler differ, so the comparison cannot isolate the causal effect of AC differentiation or DSCP.

## H: offline adaptive selection

[Controller source](../controller/adaptive_aql_regime_controller.py) provides `AdaptiveAQLRegimeController(records).select(active_flow_count, ul_dl_ratio, mac_retry_fraction, previous=None)`. It ranks complete observed AP+CPE pairs. Importing the module performs no file IO, and there is no actuator, shell command, service, network transport or executable DSCP rule.

Inputs use an observed **achieved UL/DL ratio**, not offered demand or UL fraction. Two flows with ratio0 select the bulk regime; two with positive ratio select bidirectional2; six with positive ratio select bidirectional6. Zero flow returns `IDLE`. Unsupported counts, direction states or ratio envelopes return `ABSTAIN`. Invalid/nonfinite telemetry raises a validation error. Retry input is bounded to[0,1]; retry-event ratios above1 require a different telemetry contract rather than clipping.

The higher-is-preferred objective is explicit:

```text
G/100 - p95/20 - 0.25*p99/20 - 0.25*directional_mismatch
 - (0.05 + 0.5*input_retry)*directional_BE_high/12000
 - 0.25*input_retry*directional_raw_RC/256 - 0.01*directional_FQ/1514
```

Queue/RC/direction/FQ costs are **ASSUMED_POLICY_COST** defining a heuristic, not learned causal effects. Repeated observations average within round, then across rounds. Only complete observed endpoint pairs are returned; fields are not synthesized or mixed. Optional previous-state hysteresis revalidates identity/admission and recomputes scores for the current input. Returned metadata is detached from internal state.

Quality admission requires zero loss, reported restoration, no drops and consistent finite metadata. A known negative observation invalidates the whole same-regime AP+CPE pair, including otherwise eligible duplicates from another round. This rule closes an independent-review failure in which a zero-loss duplicate concealed a known5%-loss observation. Negative source identities/reasons remain visible. Prior failing source, examples and review are preserved; unit success for the old revision did not override that finding.

The [offline examples](../artifacts/autoresearch/waves_efgh_20261024/wave_h_offline_examples.json) retain source references and show selected, idle and unsupported states. Without a previous policy, selection maximizes its declared finite-pool score. Hysteresis can retain an admitted previous pair when the alternative's score advantage is at most the configured margin, default0.05. Neither behavior is a global optimum, predictive performance guarantee or authorization to deploy settings. Numeric DSCP metadata preserves the unknown effective EF-to-VO mapping.

## Reproduction and acceptance boundary

Using the existing local environment from the repository root:

```powershell
python -B -m orchestration.autoresearch.fmx_offline_data
python -B -m orchestration.autoresearch.fmx_doe_and_pymoo_optimizer --all-rounds
python -B -m tools.sim.fmx_simpy_ptmp_aql_rc_sim --wave-g --replications 3
```

The simulator uses exclusive creation or exact replay matching to preserve differing old outputs; the initial seed-defective results are retained under `wave_g_before_seed_repair/`. Generated files stay in owned artifact paths, excluding frozen inputs and original live receipts. The old R1/R2 APIs remain available; their previously generated datasets are preserved rather than silently recalibrated.

Software versions are recorded with the datasets: Python3.12.4, NumPy1.26.4, SciPy1.17.1, pymoo0.6.2 and SimPy4.1.2. The local experimental-design, pymoo, hypothesis-generation, statistical-analysis/power, SimPy and aeon skills inform the methods and evidence limits. Sparse RTT summaries do not justify an aeon classifier. The skills' declared bibliography is retained in the [earlier methods audit](STAGE12_AUTORESEARCH_STATISTICAL_AND_CAUSAL_AUDIT.md), without an online lookup.

[Final verification](../artifacts/autoresearch/waves_efgh_20261024/final_validation.json) binds final sources, data, focused pure offline tests and separate reviews. [E/F review](../artifacts/autoresearch/waves_efgh_20261024/wave_ef_review.md), [G review](../artifacts/autoresearch/waves_efgh_20261024/wave_g_independent_review.json) and [H final review](../artifacts/autoresearch/waves_efgh_20261024/wave_h_independent_final_review.json) distinguish implementation acceptance from physical acceptance. Preserved failures include normalization serialization/metadata, CPE-only unseen-DSCP reporting, replication seed overlap, mutable controller outputs and known-failed-policy readmission. The requested implementation can pass with a negative model result; no unsupported physical result is relabeled successful.

| Research check | Result and decision |
| --- | --- |
| E: represent every saved window without invented samples/context | **CONFIRMED** by source comparison and strict fixtures; KEEP normalization tooling. |
| F: richer regime model improves bidirectional holdout prediction | **REFUTED in these diagnostics** versus the stated mean baseline; REJECT an accuracy-improvement claim, retain exploratory outputs. Bulk added policy value remains INCONCLUSIVE. |
| G: per-AC/EF structure lowers matched R7–R9 RMSE | **REFUTED in this model comparison** on all three targets; REJECT the improvement hypothesis, retain the model and negative dataset. |
| H: finite-pool selector respects telemetry/support/negative-evidence boundaries | **CONFIRMED_SOFTWARE** after separate review and repair; KEEP the offline selector. Wireless benefit and physical qualification remain UNKNOWN. |
