<!-- doc-head: Stage1200A offline bilateral what-if channel simulator and exact 3-objective Pareto ranker built on the 1181A engine -->
<!-- /doc-head -->

# Stage1200A - Bilateral what-if channel simulator and Pareto ranker

Evidence class `BILATERAL_WHATIF_CHANNEL_SIMULATION`. Offline model only: no device, UISP or NMS call, `live_devices_touched=false`, status `CONFIRMED` means built and exercised offline.

## Module

`tools/uisp/bilateral_whatif_channel_simulator_and_pareto_ranker.py`, stdlib only, imports `evaluate_channel_change` from `tools/uisp/bilateral_site_topology_and_blast_radius_engine.py` (1181A).

## Public API

- `simulate(graph, link_id, widths=(20,40,80), band_mhz=(5180,5825))` returns candidates with `center_mhz`, `width_mhz`, `is_dfs`, `cac_penalty_s`, `bilateral_overlap`, `blast_radius_cpes`, `dfs_outage_risk`.
- `pareto_front(candidates)` returns the exact non-dominated set minimizing the three objectives and sets `dominated` on every candidate.
- `counterfactual_unilateral_vs_bilateral(graph, link_id)` compares a Guarida-only optimizer with the Site A union Site B evaluation.
- `main(argv=None)` with `--write-receipt` writes the 1200A and 1201A receipts.

## Model

- DFS centers 5260..5720 MHz need CAC: `cac_penalty_s` 120. UNII-1 5180..5240 and UNII-3 5745..5825 are non-DFS: 45.
- `dfs_outage_risk` = `cac_penalty_s`/120, times 1.0 for DFS and 0.1 for non-DFS.
- `bilateral_overlap` is the 1181A `interference_cost`, which already checks both PtP ends.
- Co-located Almafuerte .60 radio is a placeholder (sector at 5200/20 MHz, 12 CPEs) added by `canonical_graph`.

## Blast-radius refinement of 1181A

Guarida serves 32 CPEs TOTAL = Panel1 .84 (3+1=4) + Panel2 (22) + Panel3 (6). 1181A `blast_radius_cpes` returned 64 because `customer_counts` holds a `guarida` entry (32) next to the three panel entries (32). The simulator uses the non-double-counted 32 plus collateral CPEs of Almafuerte radios the candidate collides with. Receipt field `blast_radius_model_note` records this.

## Counterfactual result

- Unilateral pick (Guarida .61 near end only): 5180/20 MHz, collides with the Almafuerte co-located radio at 5200 MHz (`unilateral_collides_at_far_end=true`).
- Bilateral pick: 5240/20 MHz, no veto at either end (`bilateral_avoids_collision=true`).

## Receipts and tests

- `artifacts/verification/stage1200a_bilateral_whatif_channel_simulator.json`
- `tests/test_stage1200a_whatif_simulator.py` (pareto non-domination, counterfactual, DFS/non-DFS CAC, no double count).
