<!-- doc-head: Stage 1216A offline master docs sync: indexes Wave 29 (1212A..1217A) PWO LTU binary/frame reconciler, 3 coverage-gap rules, 1187A constants reconciliation, unified advisor; compacted Wave 17-22 in CURRENT_STATE (176 -> 155 lines). Read to see what changed and the doc budget. -->
# Stage 1216A: master docs sync (Wave 29)

Offline documentation only. No live device touched. Evidence class `DOC_SYNC`.

## Scope
- `docs/CURRENT_STATE.md`: appended `## Wave 29 sync (Stage 1216A, 2026-10-27)`.
- `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`: same section appended.
- Both files stay under the 180-line budget with the doc-head on line 1.

## Compaction
CURRENT_STATE was at 176 lines, with no room for an append. The sections `Wave 17-19 sync`, `Wave 20 sync` and `Wave 22 sync` were merged in place into one `Wave 17-22 sync` block. Every distinct fact was kept: cohort INCOMPLETE and NO_GO, the open `aql_threshold` 24000 vs 12000 decision, `BLOCKED_ACCESS` for 1135A, the matrix gaps, and all receipt and doc paths.

| File | Lines before | Lines after |
| :--- | :--- | :--- |
| `docs/CURRENT_STATE.md` | 176 | 155 |
| `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md` | 145 | 150 |

## Wave 29 content
- 1212A: `tools/uisp/pwo_ltu_binary_capabilities_and_frame_reconciler.py` (`ltuRules.js` 1024-QAM vs `ame_core.ko` 4096-QAM MCS31 at 10-50 MHz, off at 60-100 MHz; frame 2/4/8 ms vs 2/2.5/4/5 ms).
- 1213A: `tools/uisp/pwo_coverage_gap_rules_stall_eth_disconnect.py` (silent-stall RC-04/10, eth speed/CRC flap, CPE disconnect-storm RC-17/18/19).
- 1214A: `tools/re/reconcile_stage1187a_binary_constants_audit.py` (missing-poll 30 s vs 30 min are two timers; penaltyThreshold 25 vs 60).
- 1215A: `tools/uisp/unified_bilateral_and_forum_grounded_pwo_advisor.py`.
- 1217A: gate `tools/verify/verify_stage1217a_wave29_claude_gate.py`, suite `tests/test_stage1212a_to_1217a_suite.py`.

## Receipt
`artifacts/verification/stage1216a_master_docs_sync.json`.

Honest state unchanged: `CONFIRMED_LIVE_HARDWARE` stays 0; no `PRODUCTION_READY` claim.
