<!-- doc-head: Stage 1127A offline auditor of the live PtP A/B cohort: pairs observed vs expected, provenance, counterbalance, supplementary stats -->
Offline only. No device, no SSH. Result at snapshot time: INCOMPLETE (0 of 18 pairs).
<!-- /doc-head -->

# Stage 1127A - PtP live 18-pair cohort completeness auditor

Tool: `tools/verify/verify_ptp_live_18pair_cohort_completeness.py`. Receipt: `artifacts/autoresearch/stage1127a_ptp_live_18pair_cohort_completeness.json` (`evidence_class` `PTP_LIVE_COHORT_COMPLETENESS_AUDIT`, `execution_status` `AUDIT_ONLY`). Tests: `tests/test_stage1127a_cohort_stats.py`.

## What it does

1. Takes ONE snapshot (`snapshot_timestamp` plus the globbed file list) of `stage1019a_live_*.json`, `stage1020a_*.json`, `stage1044a..1047a` receipts in `artifacts/autoresearch/` and raw run files in `artifacts/verification/stage104[4-7]a/raw/`. It never re-globs during the run.
2. `expected_pairs` is a parameter (`--expected-pairs`, default 18, provenance "operator directive wave #16").
3. `missing_receipts` names `stage1044a..stage1047a` when no receipt file exists for them.
4. Run records are any nested dicts with `arm` in A/B and an integer `block_index`. A PAIR is a `block_index` that has both an A-arm and a B-arm record.
5. Records carrying `evidence_state`, `arm`, `block_index` and `raw_sha256` go to `validate_run_provenance` from `analysis.regression_gate.gatekeeper` (imported, never edited), which includes the raw receipt SHA-256 match. Files without those fields report `PROVENANCE_FIELDS_ABSENT`.
6. `counterbalance_status` is separate: `COUNTERBALANCED`, `NOT_COUNTERBALANCED`, `INSUFFICIENT_BLOCKS` or `ORDER_UNKNOWN`, from whether the first arm alternates across paired blocks (A1->B1->A2->B2).
7. Zero synthetic generators: the 1112A rule (no `synthetic_fixture`, no `SYNTHETIC-` ids, no nested `SYNTHETIC_SELFTEST` or `SIMULATED_MODEL_ONLY`).

`cohort_status` is `COMPLETE` only when observed pairs reach expected pairs and no required receipt is missing; `NO_LIVE_RECEIPTS` when nothing is present; otherwise `INCOMPLETE`.

## Supplementary statistics

Pure stdlib, computed only when `observed_pairs >= 4`; otherwise `{status: INSUFFICIENT_PAIRS, n}`.

- Hodges-Lehmann: median of Walsh averages of the paired B-minus-A differences.
- Mann-Whitney U: exact null distribution when n, m <= 20 with no ties, otherwise normal approximation with tie and continuity correction.
- Holm-Bonferroni across the tested metrics (goodput, p95, p99, loss, Jain).

The live data gives INSUFFICIENT_PAIRS, so the math is proven on textbook fixtures in `tests/test_stage1127a_cohort_stats.py` (HL of 1,2,3,4 is 2.5; U for 1,2,3 vs 4,5,6 is 0 with exact p 0.1; Holm rejects 2 of 4 for p 0.01/0.04/0.03/0.005 at alpha 0.05).

## Disclaimer

The canonical promotion test is the paired sign-flip / Sidak family (977A). HL, MWU and Holm are SUPPLEMENTARY descriptors, NOT a second gate.

## Observed at snapshot

- Present: `stage1019a_live_powerbeam_busybox_triple_play.json`, `stage1020a_powerbeam_discovery_holdout_evaluation.json` (both blocked, zero A/B pairs, no run records), plus one raw A-arm record (block 0) under `artifacts/verification/stage1044a/raw/`.
- Absent: `stage1044a`, `stage1045a`, `stage1046a`, `stage1047a` receipts (Codex #2 may still be writing them).
- `observed_pairs` 0, `cohort_status` INCOMPLETE, `provenance_status` PROVENANCE_FIELDS_ABSENT, `counterbalance_status` INSUFFICIENT_BLOCKS, synthetic violations 0.

Re-run after the live receipts land: `python tools/verify/verify_ptp_live_18pair_cohort_completeness.py --write-receipt`.
