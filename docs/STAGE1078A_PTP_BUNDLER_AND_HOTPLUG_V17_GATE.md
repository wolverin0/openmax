<!-- doc-head: Stage 1078A | fail-closed offline gate for 1073A-1077A (PtP cohort bundler, champion v17 hotplug, pre-rollout matrix) | no live devices -->
<!-- /doc-head -->
# Stage 1078A - PtP bundler and hotplug v17 gate

Offline, fail-closed gate (`SystemExit(1)` on any failure). Gate: `tools/verify/verify_stage1078a_ptp_bundler_and_hotplug_v17_gate.py`.
Receipt: `artifacts/autoresearch/stage1078a_ptp_bundler_and_hotplug_v17_gate_receipt.json` (status `CONFIRMED` iff every check passes).
Suite: `tests/test_stage1073a_to_1078a_suite.py`. Pattern mirrors `tools/verify/verify_stage1054a_v17_pareto_kits_gate.py`.

## Checks

1. Receipts 1073A-1077A exist, are not all-NUL, have status `CONFIRMED`, `live_devices_touched` is `false`, and pass `audit_stage_receipt_5pillars`.
2. Docs 1073A-1078A exist, are under 180 lines and start with `<!-- doc-head:`.
3. Isolation invariants: no file under `artifacts/autoresearch/` contains `"synthetic_fixture": true` and no `session_id` starts with `SYNTHETIC-` (synthetic data may live only in 1074A tmp fixtures, never in the corpus).
4. 1074A self-test: `python -m pytest tools/autoresearch/test_ptp_cohort_provenance_bundler_selftest.py -q` returns 0.
5. 1076A restricted-PATH test: `python -m pytest tests/test_stage1076a_champion_v17_restricted_path.py -q` returns 0 (a skip counts as pass and is recorded).
6. Champion v17 `firmware/openwrt/common/99-fmx-wa-universal-champion-v17`: exists, no CRLF, `audit_text` reports 0 findings, zero `|| true`, and its current sha256 differs from `replaced_sha256` in the 1075A receipt (the edit landed).
7. 1077A matrix `artifacts/autoresearch/stage1077a_ptp_and_guarida_prerollout_readiness_matrix.json`: every `readiness_verdict` is one of `READY_FOR_ROLLBACK_TEST`, `NOT_READY`, `NO_EVIDENCE`; no `PRODUCTION_READY`; `execution_status` is `MATRIX_NOT_EXECUTED`.

## Receipt

Carries `all_gates_passed`, `failures`, `functional_checks`, `five_pillar_compliance` and claim id `FMX-STAGE1078A-PTP-BUNDLER-AND-HOTPLUG-V17-GATE`. The write retries up to 3 times against all-NUL corruption.

## Run

`python tools/verify/verify_stage1078a_ptp_bundler_and_hotplug_v17_gate.py`, then `python -m pytest tests/test_stage1049a_to_1054a_suite.py tests/test_stage1073a_to_1078a_suite.py -q`.
