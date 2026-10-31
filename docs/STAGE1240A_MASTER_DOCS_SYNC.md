<!-- doc-head: Stage 1240A offline master docs sync: indexes Wave 33 (1236A..1241A) 117-thread KB matcher reconciliation, RC-12 ethernet physical-layer attribution, unified advisor with 1190A/1191A diagnostics, whatsappbot PWO contract bundle exporter, Spanish integration guide, gate. Read to see what changed and the doc budget. -->
# Stage 1240A: master docs sync (Wave 33)

Offline documentation only. No live device touched. Evidence class `DOC_SYNC`.

## Scope
- `docs/CURRENT_STATE.md`: appended `## Wave 33 sync (Stage 1240A, 2026-10-27)`.
- `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md`: same section appended.
- Both files stay under the 180-line budget with the doc-head on line 1. No compaction was needed.

| File | Lines before | Lines after |
| :--- | :--- | :--- |
| `docs/CURRENT_STATE.md` | 155 | 161 |
| `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md` | 150 | 156 |

## Wave 33 content
- 1236A: 117-thread KB matcher reconciliation and RC-12 ethernet physical-layer attribution; `eab_driver.ko` stays the kernel surface (backward-compatible `ko_root_cause`).
- 1237A: unified advisor proof with Stage 1190A/1191A binary diagnostics.
- 1238A: drop-in PWO JSON contract bundle exporter `tools/uisp/pwo_whatsappbot_contract_exporter.py` for whatsappbot-final (no writes there).
- 1239A: Spanish master integration guide (doc-only).
- 1241A: gate `tools/verify/verify_stage1241a_wave33_claude_gate.py`, suite `tests/test_stage1236a_to_1241a_suite.py`.

## Receipt
`artifacts/verification/stage1240a_master_docs_sync.json`.

Honest state unchanged: `CONFIRMED_LIVE_HARDWARE` stays 0; no `PRODUCTION_READY` claim.
