<!-- doc-head: Stage 1249A Opus 5.5 in-place hardening of the Opus 4.8 topology engines 1181A/1182A/1200A/1202A/1206A: the Stage 1242A hardened logic is wired into the original function names, 28/28 live probes correct, frozen 4.8 baseline kept for differential history and rollback; offline simulated model only, CONFIRMED_LIVE_HARDWARE stays 0. -->
# Stage 1249A: in-place Opus 5.5 hardening of the Opus 4.8 topology engines

100% offline, recommend-only, stdlib only. No live device touched. Doc stage for code stage 1248A.
Wave 34 (1242A/1243A) found 27 defects in the 4.8 topology engines and shipped hardened replacements beside them.
Wave 35 wires those replacements INTO the original modules, so the original function names now behave correctly.

## Files
- Hardened logic and probes: `tools/uisp/opus55_hardened_bilateral_rf_and_sg01_engine.py` (1242A module).
- Receipt: `artifacts/verification/stage1248a_inplace_topology_and_sg01_upgrade.json` (claim `FMX-STAGE1248A-INPLACE-TOPOLOGY-AND-SG01-UPGRADE`).
- Regenerate: `python tools/uisp/opus55_hardened_bilateral_rf_and_sg01_engine.py --write-inplace-receipt --legacy-run-json <pytest summary>`.
- Frozen baseline: `tools/uisp/opus48_baseline/` (pre-edit copies, sha256 in `MANIFEST.json`, loader `load_opus48`). Never edited.

## Architecture
- The five live modules `import` the 1242A module and delegate. The 1242A module must therefore NOT import them.
- Its "Opus 4.8 side" (`eng`, `sim`, `bb`, `peer`, `pl`) is now a lazy handle on the frozen baseline (`load_opus48`),
  resolved on first attribute access, so importing any live module never loads the baseline.
- The live PWO bridge is resolved lazily inside `run_pipeline_hardened`; no top-level import of a live 4.8 module remains.
- Loading a frozen copy makes Python set `tools.uisp.<name>` to it, so `from tools.uisp import X` would return the FROZEN
  module. `_restore_live_package_attrs()` points those attributes back at the live module after each baseline load.
- Import check: each of the six modules is imported FIRST in a fresh interpreter (`import_cycle_check` in the receipt, all ok).

## Probes
- `run_differential_probes()` is unchanged in ids and findings: 4.8 side = frozen baseline, 28/28 `opus48_failed` and `opus55_correct`.
- `run_live_probes() -> list[dict]` replays the SAME input of every probe against the LIVE entrypoints through a namespace
  (`_HARD` for the differential run, `_live_namespace()` for the live run), with the same correctness predicate.
  Entry keys: `id`, `finding_id`, `live_target` (`tools/uisp/<module>.py::<function>`), `live_in_scope`, `live_correct`, `live_observed`.
  A crashing live entrypoint counts as `live_correct=False`. Result: 28/28 correct. Control: the frozen baseline run through
  the same predicates is correct 0/28, so the predicates discriminate.

## What changed per module
| module | entrypoint | finding ids | change |
| :--- | :--- | :--- | :--- |
| 1181A `bilateral_site_topology_and_blast_radius_engine` | `evaluate_channel_change` | 08-13 | mask + isolation link budget, blast counted once (Guarida 32), NaN/dangling id -> `ValueError`; `guard_mhz` accepted and ignored |
| 1182A `on_tower_peer_buddy_and_anomaly_disambiguator` | `disambiguate`, `_ids`, `PeerBuddyHysteresis` | 17-20 | disjoint anonymous ids, membership-based all-down, power-first when the whole PoP is down, 2-round hysteresis class re-exported |
| 1200A `bilateral_whatif_channel_simulator_and_pareto_ranker` | `_centers`, `_collateral`, `simulate` | 14-16 | 802.11ac grid per width, collateral from vetoed radio ids, `depends_on_placeholder`/`requires_survey` on every candidate |
| 1202A `zero_false_positive_bilateral_observability_pipeline` | `classify_signal`, `_round_hits`, `run_pipeline` | 21-26 | fail-closed probe quorum, bad signals dropped, power/weather over `cpe_id`, observed width honoured, confidence = streak minimum |
| 1206A `full_3tier_backbone_and_sg01_guard_engine` | `sg01_guard`, `cascading_blast_radius` | 01-07, 27 | structured fail-closed SG-01, cycle-safe redundancy-aware cascade, `print`/`export`/`traceroute` read-only |

Each change carries a one-line `# Wave 35 (OPUS48-TOPO-NN): ...` comment in the code.

## Compatibility notes
- Public names, signatures and legacy output keys are kept; keys are only added.
- `evaluate_channel_change` adds `min_margin_db`, `depends_on_placeholder`, `requires_survey`, `unsurveyed_ends`, `model_assumptions`;
  vetoes keep `reason` and `overlapping_channel` and gain `radio_id`, `direction`, `margin_db`. `interference_cost` is now
  the excess-margin fraction (saturating at 20 dB) times the CPEs of each vetoed radio; zero when nothing is vetoed.
- Widths must be 20/40/80/160 MHz and every radio needs a tower and a channel; other input raises `ValueError`.
- `cascading_blast_radius` keeps `fault`, `downstream_cpes`, `affected_sites` (DFS order), `path`; it adds `affected_nodes`,
  `redundant_survivors`, `fault_kind`. `affected_sites` now lists only nodes that are really down.
- `sg01_guard` keeps `vetoed`/`reason`; it adds `verb` and `protected_targets`. `READ_ONLY_VERBS` is the 1242A frozenset and
  `PROTECTED_TOKENS` is unchanged (consumed by the 1238A exporter); the protected set itself is derived from the backbone graph.
- `run_pipeline` adds `dropped_signals`. A signal REQUIRES `probes_positive` (int 0..5); `demo_snapshots()` now sets it.
- `canonical_graph` colocated radio and the 1206A uplink radios carry `"placeholder": true`.
- `run_pipeline` keeps `counterfactual_1200a` evidence through a `classify` hook passed to the hardened pipeline.

## Legacy assertions changed (7, all classified as bugs by a Wave 34 finding)
| test | finding | old -> new |
| :--- | :--- | :--- |
| `test_stage1181a_bilateral_engine::test_clear_channel_allowed_and_blast_union` | 08 | `blast_radius_cpes == 64` -> `== 32` |
| `test_stage1181a_bilateral_engine::test_blast_union_dedupes_sites_across_towers` | 08 | `== 64` -> `== 32` |
| `test_stage1181a_bilateral_engine::test_guard_band_edge` | 10 | 5706 vetoed -> allowed with the margin within 1 dB of 5705 |
| `test_stage1182a_peer_buddy::test_all_down_with_spike_low_confidence_self_interference` | 20 | `CO_SITE_SELF_INTERFERENCE` -> `POP_POWER_OR_WEATHER_EVENT` (confidence still < 0.7) |
| `test_stage1200a_whatif_simulator::test_blast_radius_not_double_counted` | 08 | engine blast at 5500 `> 32` -> `== 32` |
| `test_stage1202a_zero_fp_pipeline::test_two_round_signal_confirmed_but_gap_breaks_streak` | 21 | signal now carries `probes_positive: 5` |
| `test_stage1202a_zero_fp_pipeline::test_bad_input_rejected` | 23 | `ValueError` out of `run_pipeline` -> signal dropped and listed |

No test was deleted and no other assertion was weakened. Legacy run of the 1181A..1241A suites: 537 passed, 13 failed;
the 13 failures are exactly the pre-existing 1218A..1223A ones of another lane (no new failure).
Running those suites also rewrites the 1181A/1182A/1200A/1201A and wave gate receipts under `artifacts/`; their content now
reflects the hardened modules (for example blast 32), not the 4.8 values.

## Rollback
Copy the frozen file back over the live one, for example
`tools/uisp/opus48_baseline/src/tools.uisp.full_3tier_backbone_and_sg01_guard_engine.py.frozen` ->
`tools/uisp/full_3tier_backbone_and_sg01_guard_engine.py`. The 1242A module stays valid either way (its 4.8 side is the
frozen baseline), but `run_live_probes()` then correctly reports the reverted entrypoints as not correct. Revert the 7 test
assertions above together with the module.

## Limits
- All link-budget numbers are model assumptions A1..A7 of the 1242A module (mask breakpoints not re-verified, airMAX is not 802.11).
- Placeholder radios are still hard-coded by id plus a `placeholder` marker; a survey flag would replace both.
- Evidence class `OPUS55_INPLACE_TOPOLOGY_AND_SG01_UPGRADE`: offline simulated model; `CONFIRMED_LIVE_HARDWARE` stays 0.
