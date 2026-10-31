<!-- doc-head: Stage 1237A proof that the upgraded unified PWO advisor runs end to end with the 117-thread KB and 1190A/1191A diagnostics, recommend-only; 100% offline -->

# Stage 1237A - unified advisor 117-thread proof

Status: `CONFIRMED` (offline, `live_devices_touched=false`). Receipt: `artifacts/verification/stage1237a_unified_advisor_117thread_proof.json`.

## What was run
`python -m tools.uisp.unified_bilateral_and_forum_grounded_pwo_advisor --write-1237a` runs `advise()` on the sample snapshot plus a silent-stall and a disconnect-storm symptom, with the 117-thread KB loaded by `tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py`.

## Observed
- `kb_source` file, `kb_thread_count` 117.
- Every card `recommend_only=True`, `auto_approve=False`; fixed width 20 MHz; SG-01 veto still emitted.
- Symptom cards for silent stall (1190A) and disconnect storm (1191A) carry `mechanism_diagnostic`; the top-level advice carries `mechanism_diagnostics` with both stages.
- Ethernet card keeps `eab_driver.ko`, confidence 0.55, and carries the RC-12 `physical_root_cause`.

## Backward compatibility
- `tests/test_stage1206a_to_1211a_suite.py` plus `tests/test_stage1212a_to_1217a_suite.py`: 37 passed, 0 failed (unmodified).
- With `tests/test_stage1208a_symptom_matcher.py` and `tests/test_stage1215a_unified_advisor.py`: 48 passed, 0 failed.

## Limits
Static-binary attributions and community correlation only; no live repro. The 1190A and 1191A mechanisms are INFERRED, not observed on hardware.
