<!-- doc-head: STAGE1209A_COMMUNITY_SYMPTOM_AND_KO_ROOT_CAUSE_PWO_MATCHER.md the 9 ko-grounded recommend-only PWO cards -->
# Stage 1209A KO-Grounded PWO Cards

Status: CONFIRMED (offline, `live_devices_touched=false`). Receipt: `artifacts/verification/stage1209a_ko_grounded_pwo_cards.json`.

## Scope
Stage 1209A publishes the 9 .ko-grounded PWO cards produced by the Stage 1208A matcher `tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py`. One card per canonical symptom class; each card carries `ko_root_cause`, `confidence`, `remediation_steps`, `recommend_only=True`, `auto_approve=False`.

## Cards
- `ptmp_single_cpe_tx_rate_collapse` -> `ubnt_poll_host.ko`
- `silent_traffic_stall_while_associated` -> `ubnt_poll_host.ko`
- `dfs_false_trigger` -> `ath10k_core.ko`
- `m5_on_ac_mixed_mode_airtime_starvation` -> `ubnt_poll_host.ko`
- `ethernet_100m_to_10m_negotiation_drop` -> `eab_driver.ko` (placeholder, confidence 0.2; physical-layer first)
- `ltu_modulation_stuck_4x_6x` -> `ame_core.ko`
- `ltu_cpe_disconnect_storm` -> `ame_core.ko`
- `ltu_auto_frequency_atpc_glitch` -> `ame_core.ko`
- `ltu_udp_iptv_latency_spike` -> `ame_core.ko`

## Limits
- Attribution basis: `decompiled_ko + community_kb (static)`. Not a live repro; community threads are unverified by live hardware.
- Cards are advice for a human operator in PWO; nothing is applied automatically.

## Related
- `docs/STAGE1208A_COMMUNITY_SYMPTOM_AND_KO_ROOT_CAUSE_PWO_MATCHER.md`
- `docs/STAGE1163A_AQL_THRESHOLD_PROVENANCE_RECONCILIATION.md`
- `tests/test_stage1208a_symptom_matcher.py`
