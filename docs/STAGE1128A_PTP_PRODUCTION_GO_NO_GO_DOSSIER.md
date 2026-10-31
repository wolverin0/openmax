<!-- doc-head: Stage 1128A offline GO/NO_GO dossier for production PtP (LB-5AC, PBE-5AC) and Panel1-Guarida .84; current result NO_GO for all -->
Dossier only. No device touched. `status` CONFIRMED means "dossier generated", never GO.
<!-- /doc-head -->

# Stage 1128A - PtP production GO/NO_GO dossier

Tool: `tools/verify/ptp_production_go_no_go_dossier_generator.py`. Receipt: `artifacts/autoresearch/stage1128a_ptp_production_go_no_go_dossier.json` (`evidence_class` `PTP_GO_NO_GO_DOSSIER`, `execution_status` `DOSSIER_ONLY`).

## Inputs (read-only)

- Verdicts: `artifacts/autoresearch/stage1009a_ptp_powerbeam_litebeam_production_readiness_audit.json`, `stage1077a_ptp_and_guarida_prerollout_readiness_matrix.json`, `stage1080a_ptp_and_guarida_rollout_decision_matrix_v17.json`, `stage1113a_operator_executive_ptp_and_guarida_readiness_brief.json`. Each target uses the receipts that cover it; non-covering receipts are listed in `verdicts_not_applicable_in`.
- `disguised_count` from `stage1112a_zero_synthetic_and_provenance_honesty_1001a_1111a.json`.
- `cohort_status` and `provenance_status` from the 1127A receipt `stage1127a_ptp_live_18pair_cohort_completeness.json`.
- Abort criteria and open decisions from `stage1101a_ptp_production_cutover_zero_touch_checklist.json` and `stage1125a_ptp_production_canary_monitoring_and_abort_criteria.json` (loss over 2 percent, p99 over 40 ms, chain imbalance over 6 dB, watchdog auto-rollback). Unresolved 1101A decisions count as blockers.

## Rule

`GO` only if EVERY applicable verdict is exactly `READY`, AND cohort is `COMPLETE`, AND `disguised_count` is 0, AND 1127A provenance is `CLEAN`, AND no 1101A decision is unresolved. Otherwise `NO_GO` with `blocking_reasons[]` citing receipt files.

## Targets and current result

| Target | Decision | Verdicts |
|---|---|---|
| PtP PBE-5AC (PowerBeam, .241/.242) | NO_GO | NOT_READY in 1009A, 1077A, 1080A, 1113A |
| PtP LB-5AC (LiteBeam) | NO_GO | NO_EVIDENCE in 1009A, 1077A, 1113A |
| Panel1-Guarida (.84) | NO_GO | NO_CONTROLLED_EVIDENCE in 1080A, 1113A |

Shared blockers: cohort INCOMPLETE (0 of 18 pairs, `stage1044a..stage1047a` absent), provenance PROVENANCE_FIELDS_ABSENT, four unresolved 1101A open decisions.

## What would flip each target

- The 1009A signal set present and passing on live receipts: `controlled_aa_valid`, `physical_workload_acceptance`, `evidence_provenance_class`.
- A 1073A bundler output built from the real live cohort (`tools/autoresearch/ptp_cohort_provenance_and_gatekeeper_bundler.py`; its own receipt is a synthetic self-test and proves machinery only).
- Cohort completion: 18 pairs, 1127A COMPLETE and provenance CLEAN.
- Re-issued verdict receipts reading `READY` (existing receipts are never edited).

Re-run: `python tools/verify/ptp_production_go_no_go_dossier_generator.py --write-receipt`, after refreshing 1127A.
