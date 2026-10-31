<!-- doc-head: Stage 1241A Wave 33 Claude gate: offline fail-closed validation of receipts 1236A/1237A/1238A/1240A, docs 1236A..1241A, master docs, broken-link re-audit, corpus isolation, matcher RC-12 and contract exporter smoke checks, plus the consolidated suite. -->
# Stage 1241A: Wave 33 Claude gate

100% offline, fail-closed (`SystemExit(1)`). No live device touched.

## Files
- Gate: `tools/verify/verify_stage1241a_wave33_claude_gate.py`.
- Suite: `tests/test_stage1236a_to_1241a_suite.py`.
- Receipt: `artifacts/verification/stage1241a_wave33_claude_gate.json` (claim `FMX-STAGE1241A-WAVE33-CLAUDE-GATE`).

## Checks
- Receipts pinned in `artifacts/verification`: 1236A, 1237A, 1238A, 1240A (1239A is doc-only, no receipt). Each exists, is not NUL, `status` CONFIRMED, `live_devices_touched` false, 5-pillar compliant.
- Docs: exactly one `docs/STAGE{stage}_*.md` for 1236A..1241A plus both master docs, each under 180 lines with doc-head on line 1.
- Broken links: runs `tools/verify/build_stage1001a_broken_link_repair_and_reaudit.py`; `broken_links_after` must be 0.
- Corpus isolation over `artifacts/verification` and `artifacts/autoresearch` (no synthetic fixtures).
- Matcher smoke: 9 symptom classes; ethernet 100M to 10M symptom keeps `ko_root_cause` `eab_driver.ko` and carries a `physical_root_cause`.
- Exporter smoke: `export_contract_bundle()` has `schema_version`, 6 sections, invariants recommend_only true, auto_approve false, fixed width 20 MHz; `validate_bundle` valid.

## Run (orchestrator)
`pytest tests/test_stage1181a_to_1186a_suite.py tests/test_stage1200a_to_1205a_suite.py tests/test_stage1206a_to_1211a_suite.py tests/test_stage1212a_to_1217a_suite.py tests/test_stage1236a_to_1241a_suite.py -q`

Honest state unchanged: `CONFIRMED_LIVE_HARDWARE` stays 0; no `PRODUCTION_READY` claim.
