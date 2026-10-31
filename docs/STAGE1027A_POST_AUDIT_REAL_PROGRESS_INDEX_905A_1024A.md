<!-- doc-head: Stage 1027A offline post-audit real-progress index of stages 905A..1024A with strict evidence-class separation; no device touched -->
<!-- /doc-head -->
# Stage 1027A - post-audit real progress index 905A..1024A

Evidence class: `POST_AUDIT_PROGRESS_INDEX` (offline, `live_devices_touched: false`), status CONFIRMED.

Receipt: `artifacts/autoresearch/stage1027a_post_audit_real_progress_index_905a_1024a.json`.
Builder: `tools/verify/build_stage1027a_to_1029a_post_audit_progress_index.py`.

## Snapshot

Taken once at `2026-10-27T13:01:12.154844+00:00` over `artifacts/autoresearch/stage*.json` for 905A..1024A:
115 receipts (sorted list stored in the receipt as `snapshot_files`). Receipts the live lane
writes after that instant are NOT classified here.

## Class counts

| Class | Count |
| --- | ---: |
| `CONFIRMED_LIVE_HARDWARE` | 0 |
| `CONFIRMED_STATIC_BINARY` | 48 |
| `LOOPBACK_SELFTEST_ONLY` | 1 |
| `SIMULATED_MODEL_ONLY` | 8 |
| `EXECUTABLE_RETEST_SPEC` | 3 |
| `OFFLINE_AUDIT_OR_GATE` | 37 |
| `PENDING_LIVE_RETEST` | 18 |
| `UNREADABLE` | 0 |
| `UNKNOWN` | 0 |

Sum of counts equals the snapshot size (115).

## Rules

- Each receipt is classified by its own `evidence_class` first, then its own `evidence_provenance_class`,
  then the 887A heuristic classifier (`tools/verify/build_stage887a_empirical_vs_simulated_evidence_audit.py`).
- `CONFIRMED_LIVE_HARDWARE` needs top-level `controlled_aa_valid == true`, a truthy `physical_workload_acceptance`
  and a live `evidence_provenance_class`. A receipt that shows live observations but misses that rule is
  `PENDING_LIVE_RETEST`, never promoted.
- A file that is all NUL is `UNREADABLE` (a defect flag, not an evidence class).
- Nothing here is `PRODUCTION_READY`; no radio, AP or CPE was touched.

## Cited inputs (not redone)

- `artifacts/autoresearch/stage1003a_unknown_provenance_content_reclassifier.json`
- `artifacts/autoresearch/stage1004a_pending_live_retest_queue.json`
- `artifacts/autoresearch/stage887a_empirical_vs_simulated_evidence_audit.json`
- `artifacts/autoresearch/stage888a_historical_receipts_reclassification.json`

Claim id: `FMX-STAGE1027A-POST-AUDIT-PROGRESS-INDEX`.
