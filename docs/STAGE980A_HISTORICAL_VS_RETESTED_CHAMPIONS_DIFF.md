<!-- doc-head: Stage 980A historical vs retested champions diff; declared CONFIRMED vs CONFIRMED_LIVE_BENCH vs retest backlog; counts derived from 887A/888A/945A; offline -->
# Stage 980A - historical vs retested champions diff

Evidence class: CURATION_AUDIT (offline). Counts are derived from the 887A per-receipt list, cross-checked with 888A and 945A.

Total receipts classified: 1186.

## Class totals (all receipts)

- CONFIRMED_LIVE_BENCH: 131
- CONFIRMED_STATIC_BINARY: 116
- SIMULATED_MODEL_ONLY: 58
- UNKNOWN: 869
- UNREADABLE: 12

## Declared CONFIRMED, by actual evidence class

- Declared CONFIRMED (all receipts): 529
  - CONFIRMED_LIVE_BENCH: 126
  - CONFIRMED_STATIC_BINARY: 65
  - SIMULATED_MODEL_ONLY: 40
  - UNKNOWN: 298
  - UNREADABLE: 0
- Actually CONFIRMED_LIVE_BENCH: 126
- Static-binary only (runtime UNKNOWN): 65
- In retest backlog (UNKNOWN + SIMULATED): 338

## Champion-named receipts (filename heuristic)

- Receipts with 'champion' in name: 105
- Declared CONFIRMED among them: 72
  - CONFIRMED_LIVE_BENCH: 5
  - CONFIRMED_STATIC_BINARY: 13
  - SIMULATED_MODEL_ONLY: 1
  - UNKNOWN: 53
  - UNREADABLE: 0
- Backlog entries that are champion-named: 54

## Retest backlog (945A)

- Backlog total: 338; by class: {'SIMULATED_MODEL_ONLY': 40, 'UNKNOWN': 298}
- On roadmap: 123
- 945A stored rows: 200 (cap 200); backlog not in stored matrix: 138

## Cross-checks

- 888a_declared_confirmed_not_physical: 338
- 945a_backlog_total: 338
- 887a_derived_backlog: 338
- all_three_agree: True
- 945a_rows_stored: 200
- 945a_row_cap: 200
- 945a_stored_rows_all_in_backlog: True
- backlog_not_in_stored_matrix: 138
- 888a_class_totals_match_887a: True

## Caveat

UNKNOWN means not auto-classifiable from the receipt, not 'false'. A backlog entry needs a provenance fiche or physical retest before any live-bench citation; the 200-row 945A matrix is capped.

Receipt: artifacts/autoresearch/stage980a_historical_vs_retested_champions_diff.json
Builder: tools/verify/build_stage980a_historical_vs_retested_champions_diff.py
