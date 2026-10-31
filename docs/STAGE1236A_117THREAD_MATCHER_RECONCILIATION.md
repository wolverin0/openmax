<!-- doc-head: Stage 1236A reconciles the 1208A matcher and 1215A advisor with the complete 117-thread community KB; RC-12 physical enrichment, 1190A/1191A diagnostics; 100% offline -->

# Stage 1236A - 117-thread matcher reconciliation

Status: `CONFIRMED` (offline, `live_devices_touched=false`). Receipt: `artifacts/verification/stage1236a_117thread_matcher_reconciliation.json`.

## Edited modules (additive only)
- `tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py`
- `tools/uisp/unified_bilateral_and_forum_grounded_pwo_advisor.py`

## KB ingest
`artifacts/research/ubiquiti_community_m_ac_ltu_field_issues_kb.json` is read read-only (117 threads: 58 airMAX AC, 9 airMAX M, 50 LTU). The built-in fallback is kept. `load_kb` now also returns `kb_thread_total`, declared and actual per-class counts, and RC ids per class.

| Class | Threads | `ko_root_cause` |
| :--- | :--- | :--- |
| `ptmp_single_cpe_tx_rate_collapse` | 6 | `ubnt_poll_host.ko` |
| `silent_traffic_stall_while_associated` | 17 | `ubnt_poll_host.ko` |
| `dfs_false_trigger` | 22 | `ath10k_core.ko` |
| `m5_on_ac_mixed_mode_airtime_starvation` | 10 | `ubnt_poll_host.ko` |
| `ethernet_100m_to_10m_negotiation_drop` | 12 | `eab_driver.ko` |
| `ltu_modulation_stuck_4x_6x` | 9 | `ame_core.ko` |
| `ltu_cpe_disconnect_storm` | 18 | `ame_core.ko` |
| `ltu_auto_frequency_atpc_glitch` | 9 | `ame_core.ko` |
| `ltu_udp_iptv_latency_spike` | 10 | `ame_core.ko` |
| `other_field_issue` (KB only) | 4 | none, not a matcher class |

Counts sum to 117. The matcher keeps its 9 canonical classes.

## RC-12 (ethernet) enrichment
`ko_root_cause` stays `eab_driver.ko` (the kernel surface that reports the link-speed change). New fields: `physical_root_cause` = `rc` RC-12, `layer` physical, `components` cable, PoE_injector, water_ingress, switch_port, `disambiguation` OnTowerPeerBuddy (rules out RF); `physical_root_cause_note`; confidence raised from the 0.2 placeholder to 0.55.

## Unified advisor (1215A) additions
New `mechanism_diagnostic` card field and top-level `mechanism_diagnostics`:
- 1190A: `ubnt_poll_host_check_sta` frees the node via `ieee80211_free_node` at 120000 ms and does not call `ieee80211_kick_node`; silent stall shape, support INFERRED. Source `docs/STAGE1190A_UPH_PTMP_RATE_COLLAPSE_AND_SILENT_STALL_RE.md`.
- 1191A: `ame_core.ko` 2.4.2 `mcsDnThreshold_timer=1` versus `mcsUpThreshold_timer=90`, a 90x hysteresis; sticky modulation and disconnect storm shape. Source `docs/STAGE1191A_LTU_MODULATION_ATPC_AND_DISCONNECT_STORM_RE.md`.

## Backward compatibility
`tests/test_stage1206a_to_1211a_suite.py` and `tests/test_stage1212a_to_1217a_suite.py` unmodified and green (37 passed, 0 failed).
All cards remain `recommend_only=True`, `auto_approve=False`.
