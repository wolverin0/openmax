<!-- doc-head: Stage 1079A | ledger hygiene audit of stage905a-1078a receipts | duplicate claim ids NOT present; one additive evidence_class edit on stage1036a | offline -->
# Stage 1079A - duplicate claim ids and evidence classes audit

Offline, audit-first. Tool: `tools/verify/audit_stage1079a_duplicate_claim_ids_and_evidence_classes.py`.
Receipt: `artifacts/autoresearch/stage1079a_duplicate_claim_ids_and_evidence_classes.json`.
No device is touched (`live_devices_touched=false`).

## Usage

- `--dry-run` (default): prints the report, edits nothing, writes no receipt.
- `--apply`: performs the single additive edit below and writes the receipt.

## Premise check

The directive assumed a duplicate-claim-id defect for stages 949A/950A/951A and a missing class on 1036A.
Both were checked against the receipts:

- Duplicate claim ids: NOT present. `duplicate_claim_ids` is `[]` (only real non-null string collisions count).
- 949A/950A/951A each have TWO coexisting receipts with distinct slugs (six files), and all six
  `pillar_e_memory_master_claim_id` values are null. No duplicate string exists, so no de-dup action is taken.
  These are the `COEXISTING_DISTINCT_SLUGS` entries in `artifacts/autoresearch/stage_supersession_registry.json`.
- `pillar_e_memory_master_claim_id` is NOT populated on these RE-schema receipts, because a future 5-pillar audit would misread it.

## Normalization policy (additive-only, non-fabricating)

Exactly one edit under `--apply`: add a top-level `evidence_class` to
`artifacts/autoresearch/stage1036a_openwrt_aql_write_and_fq_codel_re_gate.json`, equal to its existing
`evidence_provenance_class` (`STATIC_OFFLINE_RECEIPT_CROSS_CHECK`). The existing key and every other byte are untouched,
and an existing `evidence_class` is never overwritten. The receipt records pre/post sha256 of that file.

## Report

For each receipt numbered 905A-1078A the tool emits `file`, `schema_family`
(`FIVE_PILLAR`, `PROVENANCE_RE`, `LIVE_READONLY`, `OTHER`), `evidence_class`, `evidence_provenance_class`,
`pillar_e_memory_master_claim_id`. Aggregates: `duplicate_claim_ids`, `missing_both_classes`, `descriptive_classes`.

- `evidence_class=None` on about 104 receipts is NORMAL: RE/live/gate schemas carry `evidence_provenance_class` instead.
- Descriptive classes (about 56 distinct values) are labelled ACCEPTABLE and are not rewritten.
- `missing_both_classes` lists receipts with neither key (9 at run time, e.g. 1065A-1072A gates); reported only, not edited,
  because the policy allows no fabricated values.

## Integrity assertions

- File count before == after (173 observed at run time; the directive expected 172, other lanes add receipts).
- Under `--apply` only the stage1036a sha256 changes across all `stage*.json`; 0 deletions or additions.
