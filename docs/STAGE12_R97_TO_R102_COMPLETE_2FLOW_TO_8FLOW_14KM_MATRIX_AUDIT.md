<!-- doc-head: Offline R97-R102 source and conditional eligibility audit -->
6available saved rounds; missing identities remain explicit UNKNOWN.
Joint210-member Holm500 family reused exactly; no per-group reset.
Cumulative source revision is R102; all physical acceptance stays open.
Existing strict GP/QoE, source, health and history conjunction is unchanged.
Complete DL curve and universal matrix qualification are not accepted.
Suite:4419PASS/3FAIL/13ERR; overall task HOLD.
<!-- /doc-head -->

# R97-R102: offline saved-source audit

## Outcome

**HOLD — mandatory full-suite acceptance is not met.** Source analysis and implementation are independently reviewed; T-PB-CODEX-02 must not be marked complete.

**CONFIRMED (local source arithmetic/software):** 6 available new rounds, 12 arms, 192 block windows and 96 matched pairs were authenticated. Cumulative revision R102: 304 records, 2460 crossed windows, 1142 matched pairs plus16 sequential observations. New direct contrasts in this group: 42. The group is a view of the single prespecified210-member family; no statistic or multiplicity adjustment is recalculated here.

Conditional strict eligible **new** rounds at the final accepted R134 snapshot: none. Other saved rounds remain blocked with their exact reasons below. Missing JSON/TSV identities: none in this group. A recipe alone is not a measurement.

The proposed universal distance matrix is **REFUTED as a claim about this saved corpus**: final98 declared cells have15 conditionally eligible contexts,40 blocked and43 abstentions. These are14 distance/class pairs across7 workloads, including distinct12km/class26 and12km/class27 declarations. The historical72-cell API remains intact. None of these counts establish outdoor performance, physical range, safe deployment or independent sector acceptance.

## Source and acceptance contract

Parent: Stage12 control-authority and experimental methodology in [original forward plan](../artifacts/2026-09-20-forward-plan.html) and the current BENCH_PLAN. The [frozen offline contract](../artifacts/autoresearch/waves_bq_to_cf_20261024/prespecified_contract.json), [input inventory](../artifacts/autoresearch/waves_bq_to_cf_20261024/input_inventory.json) and [114-file union manifest](../artifacts/autoresearch/waves_bq_to_cf_20261024/inputs_manifest.json) govern the audit. Frozen JSON/TSV/recipe bytes are authenticated; acquisition recipes are AST provenance and were never imported or executed. R110-R113 have only recipes, not JSON/TSV measurements. No unrecorded arm, distance knot or result was fabricated.

Keep strict structural observed GP loss `<2%` separate from the historical operator `<=2%` utility. Retain applicable16/16 paired outcomes, favorable direct rank/HL/Holm500, source/health/history guards and no actuation. Bidirectional profiles require three latency outcomes, UL and Jain; unidirectional profiles require three latency outcomes and the proven active-direction GP alias. Directional Jain and inactive throughput are inapplicable, not extra successes. No statistical noninferiority claim follows from an observed GP budget.

**CONFIRMED (declared source context):**1000m/class2 uses saved15/30us slot/ACK;12km/class26 uses87/174us and remains distinct from class27/90/180us. Class31 is the requested conservative advice ceiling, **UNKNOWN** as an independently measured silicon or installed-build maximum. Historical class33 remains literal and is blocked for current advice. Effective timing, actual RF separation and individual-knob causality remain **UNKNOWN**.

R115's unique recipe retains an older filename while its contents declare1km/class2. R134's filename says CPE BE2650, but saved candidate policy and commit identify3150/6300. Full source-bound policy values prevail over filenames. UL8 hammer stays separate from UL2; RTS literal off/256 and AP ACK-clocking booleans remain explicit endpoint policy identity. TSQ, rate-control and VO policy fields are retained without assuming their effective runtime application.

## Saved observations and strict result

Positive delta below means higher target GP in the archived means. This table is a local replay, not a newly performed wireless experiment.

|Round|Workload|Declared m/class|Stock GP Mbps|Target GP Mbps|Delta GP %|Strict result|
|---|---|---|---:|---:|---:|---|
|R97|bidir_2flow|9000/20|52.287109|55.968750|+7.041201|BLOCKED|
|R98|bidir_8flow|3000/6|59.597656|63.825195|+7.093465|BLOCKED|
|R99|bidir_8flow|6000/13|68.450195|71.218750|+4.044626|BLOCKED|
|R100|bidir_8flow|9000/20|57.444336|58.818359|+2.391922|BLOCKED|
|R101|bidir_8flow|12000/27|49.181641|50.156250|+1.981653|BLOCKED|
|R102|bidir_8flow|14000/31|68.912109|68.381836|-0.769492|BLOCKED|

Blocking reasons are preserved from the actual strict gate:

- R97: NOT_16_OF_16_FAVORABLE_jain_fairness, NOT_16_OF_16_FAVORABLE_ul_goodput_mbps, NO_DIRECT_FAVORABLE_HOLM500_jain_fairness, NO_DIRECT_FAVORABLE_HOLM500_ul_goodput_mbps.
- R98: CONTROL_SOURCE_CRASH_OR_DISQUALIFICATION, NOT_16_OF_16_FAVORABLE_jain_fairness, NOT_16_OF_16_FAVORABLE_ul_goodput_mbps, NO_DIRECT_FAVORABLE_HOLM500_jain_fairness, NO_DIRECT_FAVORABLE_HOLM500_ul_goodput_mbps.
- R99: CONTROL_SOURCE_CRASH_OR_DISQUALIFICATION, NOT_16_OF_16_FAVORABLE_ul_goodput_mbps, NO_DIRECT_FAVORABLE_HOLM500_ul_goodput_mbps.
- R100: CONTROL_SOURCE_CRASH_OR_DISQUALIFICATION, NOT_16_OF_16_FAVORABLE_p50_rtt_ms, NOT_16_OF_16_FAVORABLE_ul_goodput_mbps, NO_DIRECT_FAVORABLE_HOLM500_ul_goodput_mbps.
- R101: CONTROL_SOURCE_CRASH_OR_DISQUALIFICATION, NOT_16_OF_16_FAVORABLE_ul_goodput_mbps, NO_DIRECT_FAVORABLE_HOLM500_ul_goodput_mbps.
- R102: CONTROL_SOURCE_CRASH_OR_DISQUALIFICATION, NOT_16_OF_16_FAVORABLE_ul_goodput_mbps, NO_DIRECT_FAVORABLE_HOLM500_ul_goodput_mbps.

## Statistical verification and limits

The whole task contains210 distinct contrasts/3360 paired values,65536 assignments per exact null space, exact95% and99.9% confidence sets, and10000 paired BCa resamples with seed20261024/PCG64/common indices. Primary rank family:210 known plus290 p=1 padding in500; mean-flip sensitivity is a separate500 family. The complete known family is1268, not a truncated500 family. Primary Holm500 rejects131/210; rejection alone cannot satisfy the full acceptance conjunction.

Independent replay checked630 exact tails,420 confidence sets at106456 membership probes, literal-Fraction sensitivity, period adjustment and all families. SciPy reproduced208 finite BCa intervals; R128/R134 retry intervals remain UNAVAILABLE from zero jackknife variation. BCa is sensitivity only and is never a promotion input. The16 AB/BA blocks are the unit;160 RTTs per arm and136 Walsh averages are not extra independent replications. Conditional block exchangeability remains unproven.

The proposed seven-point pureDL surface has **0/7 strictly qualified knots** at the final snapshot. PureDL1km is absent; prior R83 is bidirectional4flow3km, not pureDL1km. R81 already failed GP. R103-R107 retain their positive/negative saved mean changes but fail active-GP unanimity/direct support. No point is relabeled or interpolated to obtain certification.

Saved control disqualification flags in R96,R98-R102,R131-R133 stay in the gate; the combined reason name does not establish that a physical crash occurred. Missing block-level health fields in unidirectional receipts stay unknown; saved aggregate restoration is not independent device health evidence.

## Validation, provenance and decision

Fresh scoped suite: **4419 PASS, 3 FAIL, 13 errors, 5 held skips, exit1**,105 explicitly assessed first-party paths; no offline guard denial. This is the preserved pre-repair unified suite covering all four groups; no passing current full-suite result is claimed. Unowned/new GEM test filenames were inventoried only and excluded from collection; the held research/live-Rocket/Flent boundaries remain explicit. It is not a literal unfiltered repository-wide pytest claim.

Independent accepted evidence: [raw dataset replay](../artifacts/autoresearch/waves_bq_to_cf_20261024/review_dataset.json), [rounded TSV replay](../artifacts/autoresearch/waves_bq_to_cf_20261024/review_tsv.json), [numerical replay](../artifacts/autoresearch/waves_bq_to_cf_20261024/review_statistics.json), [selector review](../artifacts/autoresearch/waves_bq_to_cf_20261024/review_root_selector.json), [revision binding review](../artifacts/autoresearch/waves_bq_to_cf_20261024/review_revision_projections.json) and [versioned matrix replay](../artifacts/autoresearch/waves_bq_to_cf_20261024/review_root_matrix.json). Source-owner test runs are enabling evidence, not self-acceptance. All failed preparations, RED tests, path-guard failures and their changed hypotheses remain in the bundle.

[Descriptives frozen before inference](../artifacts/autoresearch/waves_bq_to_cf_20261024/stats_preinference_descriptives.json); [paired saved-data plot](../artifacts/autoresearch/waves_bq_to_cf_20261024/stats_paired_descriptives.png); [four versioned matrix receipts](../artifacts/autoresearch/waves_bq_to_cf_20261024/integration_matrix.json); [fresh test receipt](../artifacts/autoresearch/waves_bq_to_cf_20261024/full_suite_run_1.json); [group final validation](../artifacts/autoresearch/waves_bu_to_bx_20261024/final_validation.json); [combined final validation](../artifacts/autoresearch/waves_bq_to_cf_20261024/final_validation.json).

**Decision:** KEEP the source-bound offline integration and conservative advice gates. REJECT blanket matrix/DL-curve certification from the supplied corpus. Physical improvement, runtime control authority, independent recovery and deployment acceptance remain INCONCLUSIVE. E2 remains NOT_ACCEPTED; automatic_execution_allowed=false; no radio, flash, network-device or GEM source modification was performed by this task. Behavior belongs to offline external-controller analysis.

There is no required physical operator action for this offline deliverable. Queue closure uses task_board complete followed by claim-next for codex:term_a6309070. An empty queue means wait for a new assignment, with no background acquisition and no automatic E2 restart.

## Required external acceptance blocker

The first full suite is preserved at4419PASS/3FAIL/13ERR/5held skips,exit1. One owned failure was repaired: catalog source s015 now points to its byte-identical immutable before_pb01 document, retaining the original SHA/id/line anchors and candidate claims; all40 catalog tests pass. The13 local C fixture cases subsequently passed after the observed WSL service recovery, with original timeouts/assertions and no service restart. These focused results do not become a fabricated passing full suite.

Two legacy failures reproduce standalone with no Autoresearch module imports: `analysis/metrics/test_schema.py::test_run_sample_auto_computations` assumes implicit40MHz; `analysis/regression_gate/test_gatekeeper.py::test_keep_clear_winner` expects KEEP from four unpaired samples. GEM1 must reconcile the current contracts/fixtures while retaining explicit width and paired/A-A safety requirements. The operator prohibited GEM1/GEM2 file modifications; this task does not change those files or relax their checks. After reconciliation, refresh the explicit suite boundary and run the full suite before closure.

See [external blockers](../artifacts/autoresearch/waves_bq_to_cf_20261024/external_blockers.json), [owned pin repair](../artifacts/autoresearch/waves_bq_to_cf_20261024/catalog_repair_validation.json), [standalone reproduction](../artifacts/autoresearch/waves_bq_to_cf_20261024/diagnostic_external_legacy_baseline.json) and [recovered local fixture](../artifacts/autoresearch/waves_bq_to_cf_20261024/diagnostic_local_micro_worker_after_WSL_recovery.json). Preserve task HOLD; final validation records the incomplete mandatory gate, not completion.
