<!-- doc-head: Stage1201A concrete Almafuerte .60 to Guarida .61 counterfactual proof that a Guarida-only optimizer collides at the far end while the bilateral union avoids it -->
<!-- /doc-head -->

# Stage1201A - Almafuerte <-> Guarida what-if proof

Evidence class `BILATERAL_WHATIF_PROOF`. Offline model, `live_devices_touched=false`. Produced by `main --write-receipt` of `tools/uisp/bilateral_whatif_channel_simulator_and_pareto_ranker.py`.

## Proof

Link `ptp-almafuerte60-guarida61`, chain Edificio Principal -> Almafuerte .60 -> Guarida .61, 20 MHz candidates.

| Optimizer | Channel | Overlap | Blast CPEs | DFS risk |
| :--- | :--- | :--- | :--- | :--- |
| Unilateral (Guarida only) | 5180 | 6.0 | 44 | 0.0375 |
| Bilateral (A union B) | 5240 | 0.0 | 32 | 0.0375 |

- The unilateral pick passes every Guarida .61 check but sits 20 MHz from the Almafuerte co-located radio at 5200 MHz, inside the 40 MHz threshold (20 MHz width plus 20 MHz guard).
- The bilateral pick is the lowest-overlap, lowest-risk channel allowed at both ends.
- Placeholder data: the Almafuerte co-located radio and its 12 CPEs are model inputs, not survey readings.

## Pareto front

Over all 69 candidates (widths 20/40/80) the front has one member: 5240/20 MHz dominates every other candidate on all three objectives. The receipt stores it under `pareto_front`.

## Blast-radius model

Guarida = Panel1 (4) + Panel2 (22) + Panel3 (6) = 32 CPEs. 1181A returned 64 by also adding the `guarida` entry; see `blast_radius_model_note` in the receipt.

## Receipt

`artifacts/verification/stage1201a_almafuerte_guarida_whatif_proof.json`, claim `FMX-STAGE1201A-ALMAFUERTE-GUARIDA-WHATIF-PROOF`.
