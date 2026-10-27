<!-- doc-head: Stage529A repository-wide held-stage JSON and Markdown integrity audit -->
Strict local syntax, identity, header and line metrics retain historical and cross-lane findings.
<!-- /doc-head -->

# Stage529A

Parent: fixed525A..530A offline reconciliation queue in BENCH_PLAN.
Run `python tools/autoresearch/build_stage529a_500stage_cross_lane_artifact_integrity_gate.py`.
Exit0 means the scoped audit policy has no findings or unassessed inputs; exit1
retains findings/incomplete evidence. A generated receipt is not a compliance pass.

## Scope and fixed policy

Walk the whole local repository, including ignored artifacts, firmware, research,
third-party/reference clones and Markdown outside docs. Exclude only .git,
node_modules, .venv, venv, __pycache__ and .pytest_cache directory names.
Do not follow symlink/reparse entries. They remain reported, not traversed.
The output receipt cannot hash itself and is the single explicit self exclusion.
Stage530 outputs created after this scan are checked separately by its master gate.

All Markdown gets UTF8/hash/line/header metrics. The audit policy is strictly fewer
than220 lines and one paired doc-head at line1 with at most six summary lines.
Actual comments in fenced code or inline-code examples are excluded from active
header counting. Third-party and archived/reference roles are reported separately;
their policy deviations are not assertions that upstream docs are defective.
The strict all-scoped policy still reports those deviations, without editing files.

Every local JSON file within the read budget is examined to find stage declarations
even when its basename is generic. Stage-named files and JSON under stage-named
directories remain candidates if parsing fails or identity is absent. Duplicate
keys, nonfinite numbers and invalid JSON fail closed. Recognized stage envelopes,
command captures and raw data snapshots are distinguished. A minimal structural
envelope checks stage identity and known container types; it is not a universal
versioned domain schema, five-pillar research acceptance or native provenance.
Unknown schemas stay UNASSESSED. Missing letter suffixes are compatible, while
different numeric IDs or explicit conflicting suffixes are findings.

## Bounds and interpretation

At most600000 directory entries,25000 candidate files,32MiB per file and2GiB total
read bytes including rechecks bound one run. Failed reads conservatively charge
their reserved cap. Limit/read/decode issues are explicit and prevent a complete
pass. Other JSON files are counted as examined non-stage inputs, not experiments.
The captured Markdown/stage-JSON hashes are rechecked before return. Source drift
is reported; concurrent work is preserved. The inventory is a held-file cutoff,
not a transactionally immutable archive or acceptance of500/530 experiments.

Current525..528 receipts and the local policy/helper bytes are independently pinned.
The scanner performs no import/execution of acquisition producers, no networking,
radio access, firmware extraction, flash, publication or mass document rewrite.
Final counts and exact locations live in the JSON. Master530 separates pytest and
repository wiring success from repository-wide schema/header/budget findings.
Decision: KEEP the auditor; preserve every finding and unresolved schema.
