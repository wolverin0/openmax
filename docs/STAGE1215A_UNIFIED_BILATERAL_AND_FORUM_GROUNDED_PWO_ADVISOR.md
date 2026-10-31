<!-- doc-head: STAGE1215A_UNIFIED_BILATERAL_AND_FORUM_GROUNDED_PWO_ADVISOR.md one offline recommend-only PWO advisory engine combining stages 1200A 1206A 1208A 1212A 1213A -->
# Stage 1215A Unified Bilateral and Forum-Grounded PWO Advisor

Status: CONFIRMED (offline, `live_devices_touched=false`). Evidence class `UNIFIED_BILATERAL_FORUM_GROUNDED_PWO_ADVISOR`.
Code: `tools/uisp/unified_bilateral_and_forum_grounded_pwo_advisor.py`. Test: `tests/test_stage1215a_unified_advisor.py`.
Receipt: `artifacts/verification/stage1215a_unified_pwo_advisor.json`.

## What it does
`advise(snapshot, graph=None)` runs the existing engines end to end and returns one dict. It imports them and modifies none.

| Section | Source module |
| :--- | :--- |
| `backbone` | `tools/uisp/full_3tier_backbone_and_sg01_guard_engine.py` (cascade, `sg01_guard`) |
| `channel` | `tools/uisp/bilateral_whatif_channel_simulator_and_pareto_ranker.py` (`simulate`, `pareto_front`, counterfactual) |
| `symptom_matches` | `tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py` (9 classes) |
| `ltu_capability_corrections` | `tools/uisp/pwo_ltu_binary_capabilities_and_frame_reconciler.py` (imported defensively, `present` flag) |
| `coverage_gap_cards` | `tools/uisp/pwo_coverage_gap_rules_stall_eth_disconnect.py` (imported defensively) |
| `pwo_cards` | unified list of all of the above |

## Snapshot keys (all optional)
`fault`, `proposed_actions`, `symptoms` (list of signals for the matcher), `telemetry` (for the 1213A rules), `link_id`, `requested_width_mhz`.

## Guards
- Every card is forced `recommend_only=True`, `auto_approve=False`; an assert re-checks the final list.
- Width is fixed at 20 MHz: only 20 MHz candidates are simulated; a requested other width is reported as `requested_width_rejected`.
- SG-01: each proposed action passes `sg01_guard`; a vetoed action becomes a `sg01_veto` card saying it is not recommended. Remediation steps that mention PoE or power are dropped unless they begin with a read-only verb (check, verify, measure and similar).
- A missing optional module yields `present=false` and an error string, never a crash.

## Limits
- Channel and CPE data are the 1200A model placeholders, not live readings.
- `.ko` attributions are static or community-derived (see `docs/STAGE1208A_COMMUNITY_SYMPTOM_AND_KO_ROOT_CAUSE_PWO_MATCHER.md`).
- Keyword scrubbing of power steps is a heuristic.
