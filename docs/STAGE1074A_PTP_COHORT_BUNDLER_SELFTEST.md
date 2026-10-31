<!-- doc-head: 1074A synthetic self-test of gatekeeper verdicts on bundler-built fixtures -->
<!-- /doc-head -->

# Stage 1074A: PtP cohort bundler self-test

Scope: `SYNTHETIC_SELFTEST`. This proves the gatekeeper's arithmetic and verdict machinery; it certifies nothing about any radio.

Test: `tools/autoresearch/test_ptp_cohort_provenance_bundler_selftest.py`.
Receipt: `artifacts/autoresearch/stage1074a_ptp_cohort_bundler_selftest.json`.
Run: `python -m pytest tools/autoresearch/test_ptp_cohort_provenance_bundler_selftest.py -q`.

## Isolation

- Every fixture is written under `tempfile.TemporaryDirectory()` passed as `evidence_root`; never under `artifacts/`.
- Every `session_id` and `peer_id` starts with `SYNTHETIC-`; every raw receipt has `"synthetic_fixture": true`.
- Stage receipts never contain those identities or any `controlled_aa_valid` / `physical_workload_acceptance` key.

## Cases and observed verdicts (real `RegressionGatekeeper` API)

| Case | Fixture | Verdict |
| --- | --- | --- |
| 1 | 6-pair A/A, all `SYNTHETIC`, no treatment contrast | `REJECT` |
| 2 | 6-pair A/B discovery, `BENCH_EXECUTED`, no holdout; `validate_run_provenance(...) == []` | `KEEP_FOR_REPLICATION` |
| 3 | Discovery + holdout + `BENCH_REPLICATED` receipt; `validate_holdout_evidence(...) == []` | `PROMOTE` |
| 4a | Case 3 fixture with every run `SYNTHETIC` | `SYNTHETIC_PASS` |
| 4b | Case 3 fixture with one `SYNTHETIC` run among physical ones | `INCONCLUSIVE` (not `PROMOTE`) |

Case 3 uses disjoint run ids, sessions and time windows, one `peer_id`, the candidate fingerprint on every B arm,
and a frozen plan created before the first discovery window with a single-member family.

## Reading the result

`KEEP_FOR_REPLICATION` and `PROMOTE` here mean the gatekeeper accepted well-formed hash-bound synthetic
fixtures. They are verdicts on isolated synthetic fixtures, never physical promotion. Cases 4a/4b prove the
boundary: synthetic or mixed-state evidence cannot reach `PROMOTE`.

Fixtures are built by `build_window_receipt` and `build_replication_receipt` from
`tools/autoresearch/ptp_cohort_provenance_and_gatekeeper_bundler.py`.
