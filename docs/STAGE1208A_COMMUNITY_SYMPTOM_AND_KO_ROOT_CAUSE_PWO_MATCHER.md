<!-- doc-head: STAGE1208A_COMMUNITY_SYMPTOM_AND_KO_ROOT_CAUSE_PWO_MATCHER.md offline matcher of community symptom classes to decompiled .ko root causes -->
# Stage 1208A Community Symptom and .ko Root Cause PWO Matcher

Status: CONFIRMED (offline, `live_devices_touched=false`). Evidence class `COMMUNITY_SYMPTOM_KO_PWO_MATCHER`.

## What it does
`tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py` maps a telemetry/forum signal to one of the 9 canonical Ubiquiti community field classes, then to a decompiled .ko root cause, and emits a PWO recommend-only card.

## Public API
- `match_symptom(signal)` returns `symptom_class`, `ko_root_cause`, `confidence`, `remediation_steps`, `pwo_card`.
- `load_kb(path=None)` reads `artifacts/research/ubiquiti_community_m_ac_ltu_field_issues_kb.json` read-only; on absence or mismatch returns the built-in fallback. `kb_source` is `file` or `builtin_fallback`.
- `all_symptom_classes()` returns the 9 keys.
- `main --write-receipt` writes `artifacts/verification/stage1208a_community_symptom_ko_pwo_matcher.json` and `artifacts/verification/stage1209a_ko_grounded_pwo_cards.json`.

## Mapping
- `ptmp_single_cpe_tx_rate_collapse` -> `ubnt_poll_host.ko`
- `silent_traffic_stall_while_associated` -> `ubnt_poll_host.ko`
- `dfs_false_trigger` -> `ath10k_core.ko`
- `m5_on_ac_mixed_mode_airtime_starvation` -> `ubnt_poll_host.ko`
- `ethernet_100m_to_10m_negotiation_drop` -> `eab_driver.ko` (low confidence placeholder; the KB lists no .ko root cause, class other)
- `ltu_modulation_stuck_4x_6x` -> `ame_core.ko`
- `ltu_cpe_disconnect_storm` -> `ame_core.ko`
- `ltu_auto_frequency_atpc_glitch` -> `ame_core.ko`
- `ltu_udp_iptv_latency_spike` -> `ame_core.ko`

## Honesty and safety
- `attribution_basis` is `decompiled_ko + community_kb (static)`: a model from static decompilation and community correlation, not a live repro.
- Every card has `recommend_only=True` and `auto_approve=False`; no card can auto-approve.
- Confidence is capped at 0.9 and is a heuristic, not a measured probability.

## Verification
Self-test `tests/test_stage1208a_symptom_matcher.py`: 9 classes resolve to a .ko and a recommend-only card, no auto-approve, bogus KB path falls back cleanly.
Companion doc: `docs/STAGE1209A_COMMUNITY_SYMPTOM_AND_KO_ROOT_CAUSE_PWO_MATCHER.md`.
