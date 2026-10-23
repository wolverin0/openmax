<!-- doc-head: PREPROD1 public evidence and retained raw provenance -->
Accepted prepared-bench P1 evidence preserves counts and SHA256 provenance.
Original raw receipts remain local and unchanged.
Projections cannot replace hash-bound execution prerequisites.
Bench qualification and production readiness are separate outcomes.
<!-- /doc-head -->

The current recorded outcome is in the [bench result](../preprod1_bench_result_20261022.json); the [preserved results index](../preprod1_preserved_results_20261022.json) retains earlier failures. The [final acceptance](../preprod1_final_acceptance_20261023.json) records the independently accepted full prepared-bench P1 result. Its scope uses temporary E86 AP userspace compatibility; production remains forbidden.

Each `*.public.json` is a separate whitelist projection. It retains the original path, size and SHA256, selected status flags, packet counts and fixed target labels. It omits command output, neighbor tables, foreign probes, credentials and raw management-frame contents. The original files are retained locally; their historical hashes are unchanged. `index.json` and the completed-addition indexes map those originals to projections. A projection is explicitly neither byte-identical to its source nor a replacement for a runtime prerequisite.

The static projection producer and its original tests are preserved beside their receipts. Later integration adds only recognized outcome tokens and cleanup-error counts. Host launch timestamps use a monotonic clock; packet timestamps use the AP capture clock. Relative phases within each domain are meaningful; the clocks are not asserted to share UTC.

A public checkout can inspect the controller, source patches, fixture tests, independent reports and projected evidence. Physical execution remains fail closed without the exact locally retained prerequisite archive, pinned private executable/build inputs, scoped access and an exact-plan independent review. Private firmware, backups, raw management captures and executable wpad images are excluded from publication.

[PREPROD2 readiness](../preprod_guarida_readiness_20261022.json) is a separate offline package result. Its public dry-run kit is self-contained for local recording tests; target rollback and physical power/TFTP recovery remain unqualified. `GO=false`, production execution disabled and no selected deployment candidate remain binding. The bench-scoped XC compatibility executable is not automatically a production candidate.
