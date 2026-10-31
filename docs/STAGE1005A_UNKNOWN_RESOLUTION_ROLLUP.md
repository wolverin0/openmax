<!-- doc-head: Stage 1005A rollup of UNKNOWN provenance resolution (298 processed) and net corpus class totals vs 887A; offline; honest remaining UNKNOWN/PENDING -->
<!-- /doc-head -->
# Stage 1005A - UNKNOWN resolution rollup

Evidence class: PROVENANCE_RECLASSIFICATION (offline, `live_devices_touched: false`).

## Moved from UNKNOWN

- processed: 298 declared-CONFIRMED UNKNOWN receipts
- `CONFIRMED_LIVE_HARDWARE`: 20
- `CONFIRMED_STATIC_BINARY`: 38
- `SIMULATED_MODEL_ONLY`: 19
- `PENDING_LIVE_RETEST`: 115
- remain `UNKNOWN`: 106
- resolved into a bucket: 192
- UNKNOWN rows out of scope (never declared CONFIRMED): 571

## Net corpus totals (887A original -> net)

- `CONFIRMED_STATIC_BINARY`: 116 -> 154
- `SIMULATED_MODEL_ONLY`: 58 -> 77
- `UNKNOWN`: 869 -> 677
- `UNREADABLE`: 12 -> 12
- `CONFIRMED_LIVE_HARDWARE`: 131 -> 151
- `PENDING_LIVE_RETEST`: 0 -> 115
- total: 1186 (equals 887A receipts scanned)
- `CONFIRMED_LIVE_BENCH` (887A) and `CONFIRMED_LIVE_HARDWARE` are the same class

## Sources and output

- `artifacts/autoresearch/stage887a_empirical_vs_simulated_evidence_audit.json`
- `artifacts/autoresearch/stage1003a_unknown_provenance_content_reclassifier.json`
- `artifacts/autoresearch/stage1004a_pending_live_retest_queue.json`
- builder: `tools/verify/build_stage1005a_unknown_resolution_rollup.py`; test: `tests/test_stage1005a.py`

## Caveat

- Only the 298 declared-CONFIRMED UNKNOWN receipts were reclassified; the other UNKNOWN rows stay UNKNOWN. LIVE_HARDWARE count includes receipt-embedded measurements only; PENDING_LIVE_RETEST is not confirmed.
