<!-- doc-head: Stage 1129A per-file pytest matrix for stages 1103A-1126A; claude-owned suites gate the receipt, other-lane suites recorded as-is -->
<!-- /doc-head -->

# Stage 1129A - master pytest matrix 1103A-1126A

- Tool: `tools/verify/run_stage1129a_master_pytest_matrix_1103a_1126a.py`; receipt `artifacts/verification/stage1129a_master_pytest_matrix_1103a_1126a.json`; evidence class `MASTER_PYTEST_MATRIX`.
- Discovery: every `tests/test_stage11*.py` whose parsed stage number is in 1103..1126. `tests/test_stage1100a_watchdog_v17_restricted_path.py` (claude-owned) sits below the range and is not in the matrix.
- Isolation: each file runs in its own pytest subprocess with a 600 s timeout, so one hang cannot sink the matrix.
- Record per file: `file`, `rc`, `passed`, `failed`, `skipped`, `duration_s`, `owner`.

## Ownership and gating

- `claude`: `tests/test_stage1109a_to_1114a_suite.py`, `tests/test_stage1121a_to_1126a_suite.py`, `tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py`, `tests/test_stage1124a_health_dump_restricted_path.py`.
- `other_lane`: everything else; each row carries `note: "concurrent lane, may be mid-flight"`.
- Receipt `status` depends ONLY on the claude-owned rows all being rc 0. Other-lane results never fail this stage.

## Result (run 2026-10-27)

- claude: 4 files, 4 rc 0, 31 passed, 0 failed, 0 skipped. Status CONFIRMED.
- other_lane: 4 files, 3 rc 0, 163 passed, 15 failed. The failures are all in `tests/test_stage1103a_to_1108a_suite.py` (29 passed, 15 failed), a concurrent lane suite; recorded as-is, not diagnosed here.
- Scope: offline only; no live device touched. No `PRODUCTION_READY` claim.
