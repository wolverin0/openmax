<!-- doc-head: Stage 1132A Wave 16 Claude gate over Stages 1127A to 1131A (offline, fail-closed): cohort invariant, independent GO/NO_GO recompute, corpus isolation, link audit -->

# Stage 1132A - Wave 16 Claude gate

Gate: `tools/verify/verify_stage1132a_wave16_claude_gate.py`
Suite: `tests/test_stage1127a_to_1132a_suite.py`
Receipt: `artifacts/verification/stage1132a_wave16_claude_gate.json`
Claim id: `FMX-STAGE1132A-WAVE16-CLAUDE-GATE`.

Offline only, no SSH, no devices. A failed check exits nonzero (`SystemExit(1)`) and the receipt says `FAILED`.
The receipt write retries up to 3 times if the file comes back all-NUL.

## Receipt locations (mixed this wave)
- `artifacts/verification/`: `stage1127a_ptp_live_18pair_cohort_completeness.json`, `stage1129a_master_pytest_matrix_1103a_1126a.json`, `stage1132a_wave16_claude_gate.json`.
- `artifacts/autoresearch/`: `stage1128a_ptp_production_go_no_go_dossier.json`, `stage1130a_master_docs_sync_through_1132a.json`, `stage1131a_guarida_and_ptp_production_rollout_runbook_es.json`.

## Checks
1. Receipts 1127A-1131A: exist, not all-NUL, `status` CONFIRMED, `live_devices_touched` false, pass `audit_stage_receipt_5pillars`.
2. Docs 1127A-1132A: exist, under 180 lines, line 1 starts with `<!-- doc-head:`.
3. Master docs `docs/CURRENT_STATE.md` and `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`: same budget and doc-head.
4. 1127A invariant: no receipt may claim `cohort_status == "COMPLETE"` with `observed_pairs < expected_pairs`; the three values are recorded.
5. 1128A: the GO/NO_GO verdict is recomputed independently from 1009A, 1077A, 1080A and 1113A verdicts, the 1127A `cohort_status` and the 1112A `disguised_count`. The result must equal the dossier verdict, it is `NO_GO` unless every input is READY, and `PRODUCTION_READY` must not appear.
6. 1129A: every claude-owned suite has rc 0; other-lane suites are recorded, not required green.
7. Corpus isolation across `artifacts/autoresearch/*.json` and `artifacts/verification/*.json`: no exact `"synthetic_fixture": true`, no `session_id` starting `SYNTHETIC-`.
8. Link audit: runs `tools/verify/build_stage1001a_broken_link_repair_and_reaudit.py`; the receipt must show `broken_links_after` at most 4 (external Codex #1 docs).
9. Pinned self-tests (rc 0, skips count as pass): `tests/test_stage1127a_cohort_stats.py`, `tests/test_stage1122a_ptp_canary_monitor_fault_matrix.py`, `tests/test_stage1124a_health_dump_restricted_path.py`.

## Notes
- Step 8 rewrites the 1001A receipt and its doc as a side effect of that builder.
- The 1128A verdict key and the 1129A suite layout are read tolerantly (`verdict`, `go_no_go_verdict`, `go_no_go`, `dossier_verdict`; dicts with `rc` plus `owner`).
- Run: `python tools/verify/verify_stage1132a_wave16_claude_gate.py`, then `pytest tests/test_stage1127a_to_1132a_suite.py -q`.
