<!-- doc-head: Stage266A qualified saved counterbalanced comparison leaderboard -->
One inventory preserves family, endpoint, workload and provenance limitations.
<!-- /doc-head -->

# Stage266A

Parent: reproducible experiments and evidence synthesis. The question is which
saved counterbalanced comparisons can be recomputed without double counting
cumulative summaries or confusing families, endpoints and workloads.

Run `python tools/bench/export_cumulative_autoresearch_leaderboard.py`.
Outputs under `artifacts/autoresearch/`:
- `stage266a_cumulative_leaderboard.json`: complete comparisons and exclusions.
- `stage266a_cumulative_leaderboard.md`: complete comparison table.
- `stage266a_cumulative_leaderboard_receipt.json`: source/output pins and coverage.

Cutoff is stage number <=266, not wall-clock file order. Every matching top-level
stage JSON is inventoried, including rejected/unsupported schemas and simulations.
WA .20/.250, Panel1 .84, XC .198, 2XC .253, XM .20 and LTU .110 remain separate;
joint XC+2XC measurements are one stratum, not two independent replications.
Endpoint labels derive from named source campaigns, not live identity checks.
No ABAB windows means NO_QUALIFYING_SAVED_ABAB, even if a receipt says ABAB.

Accepted arrays must contain observed A/B/A/B order, finite nonnegative goodput
and p95, valid RTT order, no 999 sentinel, and sufficient samples when reported.
Means and percentage changes are recomputed from windows. Bulk TCP versus aggregate
goodput retains its metric basis. Identical round IDs and metric fingerprints are deduplicated,
with all source paths, SHA256 and JSON pointers retained.
Reconstructed A/B arrays retain real pointers to both arrays and their context.
Fingerprint equality is not proof of identical acquisition, controls or topology.
Unresolved topologies remain a separate group and are not assigned by IP alone.

The descriptive table sorts within family by saved goodput contrast. It is not
a global champion ranking or controlled cross-topology comparison. A within-round
goodput/tail guard does not establish Triple-Play acceptance, statistical power,
actuator success or RF causality. Jitter/loss and missing metrics remain in JSON.
Two repeated windows per arm do not support a strong confidence claim.
`scientific-critical-thinking` informs evidence-unit and confounding qualification.
Stop at local export and parser validation; no SSH, native runner, RF load or flash.
