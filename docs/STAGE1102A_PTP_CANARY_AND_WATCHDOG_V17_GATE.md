<!-- doc-head: Stage 1102A offline fail-closed gate for the PtP canary verifier + v17 watchdog wave (1097A..1102A); receipts, docs, watchdog lint, self-tests, corpus isolation -->
# Stage 1102A - PtP canary and watchdog v17 gate

100% offline, fail-closed (`SystemExit(1)`). Gate: `tools/verify/verify_stage1102a_ptp_canary_and_watchdog_v17_gate.py`.
Receipt: `artifacts/autoresearch/stage1102a_ptp_canary_and_watchdog_v17_gate_receipt.json`.
Suite: `tests/test_stage1097a_to_1102a_suite.py`.

## Checks

1. Receipts 1097A..1101A: exist, not all-NUL, `CONFIRMED`, `live_devices_touched` False, 5-pillar compliant.
2. Docs 1097A..1102A: exist, under 180 lines, line 1 `<!-- doc-head:`.
3. Master docs `docs/CURRENT_STATE.md` and `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`: same limits.
4. Watchdog `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_rollback_watchdog_v17.sh`: LF only, `sh -n`
   (skipped and recorded if no sh), `audit_text` zero findings, no `|| true` / `|| :`, snapshot name
   `fmx-pbe5ac-v17-snapshot` (hyphen, never the dotted form).
5. 1098A self-test: `tools/autoresearch/test_ptp_canary_verifier_selftest.py` rc 0.
6. 1100A restricted-PATH test: `tests/test_stage1100a_watchdog_v17_restricted_path.py` rc 0 (skip counts, recorded).
7. Corpus isolation: no file under `artifacts/autoresearch/` has a synthetic-fixture flag or a `SYNTHETIC-`
   session id; the 1098A receipt has no `controlled_aa_valid` / `physical_workload_acceptance` key.
8. 1101A checklist: `CHECKLIST_NOT_EXECUTED`, no readiness claim, LiteBeam `NO_EVIDENCE`.

## Notes

- The receipt write retries 3 times against all-NUL corruption.
- Checklist under test: `docs/STAGE1101A_PTP_PRODUCTION_CUTOVER_ZERO_TOUCH_CHECKLIST.md`.
- Passing this gate is not a readiness statement; live execution stays with Codex #1.
