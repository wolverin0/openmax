<!-- doc-head: Stage 1112A | read-only provenance-honesty audit of stage1001a-1111a receipts | synthetic-disguised-as-live count and warnings | offline -->
# Stage 1112A - zero-synthetic and provenance-honesty audit (1001A-1111A)

Tool: `tools/verify/audit_stage1112a_zero_synthetic_and_provenance_honesty_1001a_1111a.py`.
Test: `tools/verify/test_audit_stage1112a_zero_synthetic_and_provenance_honesty.py`.
Receipt: `artifacts/autoresearch/stage1112a_zero_synthetic_and_provenance_honesty_1001a_1111a.json`.
Read-only: edits no receipt; `--write-receipt` writes only the 1112A receipt. `live_devices_touched=false`.

## Hard failure: synthetic disguised as live

A receipt whose `evidence_class` or `evidence_provenance_class` is in
`{CONFIRMED_LIVE_HARDWARE, CONFIRMED_LIVE_BENCH, FIELD_CANARY, PRODUCTION_ACCEPTED}` AND any of:

- `"synthetic_fixture": true` anywhere;
- `session_id` / `peer_id` starting `SYNTHETIC-` anywhere;
- top-level `live_devices_touched == false` (top level only: `pillar_c` carries a benign nested false in every five-pillar receipt);
- a nested (non-root) `evidence_class` in `{SYNTHETIC_SELFTEST, SIMULATED_MODEL_ONLY, LOOPBACK_SELFTEST_ONLY}`.

A hit is the finding; the classifier is never tuned to hide it.

## Warning only

`LIVE_CLASS_WITHOUT_SIGNALS`: `status == CONFIRMED`, a live class, and no `controlled_aa_valid` /
`physical_workload_acceptance` key anywhere. Many live receipts predate the 1009A signal set.

## Schema families

Reuses `family()` from `tools/verify/audit_stage1079a_duplicate_claim_ids_and_evidence_classes.py`
(the 1027A/1079A family logic): FIVE_PILLAR, LIVE_READONLY, PROVENANCE_RE, OTHER.

## Result at build time

corpus 102 receipts; families FIVE_PILLAR 67, PROVENANCE_RE 23, OTHER 7, LIVE_READONLY 5;
6 receipts carry a live class; `disguised_count` = 0; no `LIVE_CLASS_WITHOUT_SIGNALS` warnings.
The corpus grows as other lanes add receipts; rerun the tool for the current count.

## Self-test

`python -m pytest tools/verify/test_audit_stage1112a_zero_synthetic_and_provenance_honesty.py` covers a clean live
receipt, four synthetic-disguised variants that must be caught, a clean synthetic receipt, and the warning path.
