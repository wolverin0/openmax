<!-- doc-head: Stage 1004A prioritized hardware-retest queue for PENDING_LIVE_RETEST receipts from 1003A; offline plan only; no measurement performed -->
<!-- /doc-head -->
# Stage 1004A - PENDING_LIVE_RETEST queue

Evidence class: PROVENANCE_RECLASSIFICATION (offline, `live_devices_touched: false`).

## What it is

- input: `artifacts/autoresearch/stage1003a_unknown_provenance_content_reclassifier.json`
- pending receipts queued: 115 (stored 115, cap 400)
- with a claimed numeric metric: 107
- each row: receipt, claimed_metric_if_any, suggested_measurement, priority_score, gap, rank

## Priority score

- +3 claims live windows/rounds, +2 champion named in filename, +2 claimed numeric metric
- +1 live device IP seen, +1 hardware attribution; ties by stage number descending

## Score histogram

- score 9: 11 receipts
- score 8: 8 receipts
- score 7: 6 receipts
- score 6: 29 receipts
- score 5: 5 receipts
- score 4: 11 receipts
- score 3: 39 receipts
- score 2: 6 receipts

## Output

- builder: `tools/verify/build_stage1004a_pending_live_retest_queue.py`
- receipt: `artifacts/autoresearch/stage1004a_pending_live_retest_queue.json`
- test: `tests/test_stage1004a.py`

## Caveat

- Queue only; no measurement performed. Suggested measurements need operator approval before touching any radio.
