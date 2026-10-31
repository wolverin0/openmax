<!-- doc-head: Stage 1003A content-based reclassifier of 298 declared-CONFIRMED UNKNOWN receipts; offline; histogram derived from receipt; PENDING/UNKNOWN not forced -->
<!-- /doc-head -->
# Stage 1003A - UNKNOWN provenance content reclassifier

Evidence class: PROVENANCE_RECLASSIFICATION (offline, `live_devices_touched: false`).

## Scope

- source: `artifacts/autoresearch/stage887a_empirical_vs_simulated_evidence_audit.json` (`per_receipt`)
- UNKNOWN rows in 887A: 869; processed here: 298
- selection: `evidence_class == UNKNOWN` and `declared_status == CONFIRMED` (the 980A backlog UNKNOWN count)
- the remaining UNKNOWN rows never declared CONFIRMED and stay untouched

## Rules (receipt content, not filename)

- `SIMULATED_MODEL_ONLY`: SimPy/pymoo/analytic/offline-model marker in title, attribution or labels
- `CONFIRMED_LIVE_HARDWARE`: >=3 numeric measurement records in lists + live device IP + hardware attribution + live flag not False
- `PENDING_LIVE_RETEST`: claims live windows/rounds or numeric goodput/latency without the above evidence
- `CONFIRMED_STATIC_BINARY`: SGMT/xtensa/patch/squashfs markers + sha256 hashes, no live-result claim
- `UNKNOWN`: none of the signals (plan/index/protocol stub); kept as is

## Histogram

- `CONFIRMED_LIVE_HARDWARE`: 20
- `CONFIRMED_STATIC_BINARY`: 38
- `SIMULATED_MODEL_ONLY`: 19
- `PENDING_LIVE_RETEST`: 115
- `UNKNOWN`: 106
- total: 298 (reconciles to processed 298)

## Output

- builder: `tools/verify/build_stage1003a_unknown_provenance_content_reclassifier.py`
- receipt: `artifacts/autoresearch/stage1003a_unknown_provenance_content_reclassifier.json`
- per-receipt rows stored: 298 (cap 400); each has file, new_class, claimed_metric, signals, reason
- test: `tests/test_stage1003a.py`

## Caveat

- Offline content triage. LIVE_HARDWARE here means the receipt itself embeds numeric measurement records + device IP + hardware attribution; it is not an independent retest. PENDING_LIVE_RETEST needs a physical re-measurement before any live-bench citation. UNKNOWN is kept, not forced.
- Next: `docs/STAGE1004A_PENDING_LIVE_RETEST_QUEUE.md` queues the PENDING subset.
