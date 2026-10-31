<!-- doc-head: Stage 1080A | PtP + Guarida rollout decision matrix v17 | verdicts READY/NOT_READY/NO_CONTROLLED_EVIDENCE | DECISION_MATRIX_NOT_EXECUTED | owner Codex #1 (live lane) -->
# Stage 1080A - PtP and Guarida rollout decision matrix v17

Offline, fail-closed. Tool: `tools/autoresearch/ptp_and_guarida_rollout_decision_matrix_v17.py`.
Receipt: `artifacts/autoresearch/stage1080a_ptp_and_guarida_rollout_decision_matrix_v17.json`.
`execution_status` is `DECISION_MATRIX_NOT_EXECUTED`; owner Codex #1 (live lane). No target is production-ready
and `PRODUCTION_READY` is never emitted.

## Rule

Verdicts are computed from the 1009A signal set (`controlled_aa_valid`, `physical_workload_acceptance`,
`evidence_provenance_class`, plus `status`) read from the actual receipts, not from the word "live" in a filename.

- `READY`: `controlled_aa_valid` true AND `physical_workload_acceptance` is `ACCEPTED`.
- `NOT_READY`: an A/A attempt exists (`MEASURED_AA*`) or 1009A says NOT_READY, without valid acceptance.
- `NO_CONTROLLED_EVIDENCE`: read-only/passive observations, or blocked before any workload.

## Verdicts

| Target | Verdict | Basis |
| :--- | :--- | :--- |
| PowerBeam PtP .241 <-> .242 | NOT_READY | `stage906a_live_powerbeam_loss_diagnosis_and_aa.json` is MEASURED_AA with an invalid baseline (1009A); `stage931a_live_powerbeam_aql_notsent_holdout.json` is BLOCKED_PRECONDITIONS |
| WA Bench .20 | NO_CONTROLLED_EVIDENCE | `stage1021a_live_wa_tcless_statless_aql_notsent.json`: `controlled_aa_valid=false`, NOT_ACCEPTED, no workload generated |
| Guarida Panel1 .84 | NO_CONTROLLED_EVIDENCE | `stage955a_live_panel1_three_cpe_readonly_audit.json` read-only; `stage1022a_live_panel1_aqm_aql_readonly.json` read-only observation |
| LTU-Lite .110 | NO_CONTROLLED_EVIDENCE | `stage956a_live_ltu_lite_readonly_audit.json` read-only; `stage1023a_live_ltu_lite_readonly.json` read-only observation |

## Notes

- `stage1022a_live_panel1_aqm_aql_readonly.json` and `stage1023a_live_ltu_lite_readonly.json` are passive read-only observations
  (`NOT_APPLICABLE_PASSIVE_ONLY`); they are not controlled A/A evidence.
- `stage1021a_live_wa_tcless_statless_aql_notsent.json` is not purely read-only: it records one transient immediate
  apply, readback and native rollback, but no A/A workload (blockers: no qualified receiver, no workload, no 45s rollback proof).
- `stage1016a_wa_20_retest_spec.json` is a retest spec and no result file exists; a spec is not evidence.
- NO_CONTROLLED_EVIDENCE is distinct from NOT_READY: nothing was measured, versus a measurement that failed.
- Complements `stage1077a_ptp_and_guarida_prerollout_readiness_matrix.json` (not edited).
