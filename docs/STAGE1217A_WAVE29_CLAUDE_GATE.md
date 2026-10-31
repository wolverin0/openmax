<!-- doc-head: Stage 1217A Wave 29 Claude gate + consolidated suite: validates pinned receipts 1212A..1216A, docs 1212A..1217A + master docs (<180 lines, doc-head), broken links 0, corpus isolation, smoke-imports the PWO LTU reconciler, coverage-gap rules, 1187A constants reconciliation and unified advisor. Offline, fail-closed. -->
# Stage 1217A: Wave 29 Claude gate

100% offline, fail-closed (`SystemExit(1)`). No live device touched.

## Files
- Gate: `tools/verify/verify_stage1217a_wave29_claude_gate.py`
- Suite: `tests/test_stage1212a_to_1217a_suite.py`
- Receipt: `artifacts/verification/stage1217a_wave29_claude_gate.json` (claim `FMX-STAGE1217A-WAVE29-CLAUDE-GATE`)

## Receipts checked (`artifacts/verification`)
- `stage1212a_pwo_ltu_binary_reconciler.json`
- `stage1213a_pwo_coverage_gap_rules.json`
- `stage1214a_binary_constants_reconciliation.json`
- `stage1215a_unified_pwo_advisor.json`
- `stage1216a_master_docs_sync.json`

Each must exist, not be NUL-corrupt, have `status == "CONFIRMED"`, `live_devices_touched` False and pass the 5-pillar audit.

## Other gates
- Docs: exactly one `docs/STAGE{n}_*.md` for 1212A..1217A, plus both master docs; each under 180 lines with doc-head on line 1.
- Broken links: runs `tools/verify/build_stage1001a_broken_link_repair_and_reaudit.py`; `broken_links_after` must be 0.
- Corpus isolation: no `synthetic_fixture` true or `SYNTHETIC-` session ids in `artifacts/verification` and `artifacts/autoresearch`.
- Smoke imports: LTU reconciler (4096-QAM on at 50 MHz, off at 60/80/100; binary frame list contains 2.5), coverage-gap rules (3 ids, stall card recommend-only), constants reconcile (`missing_poll_timer` not the same constant as `penalty_threshold`), unified advisor (all PWO cards `auto_approve` False).

The orchestrator runs the gate and suite after all stage authors finish.
