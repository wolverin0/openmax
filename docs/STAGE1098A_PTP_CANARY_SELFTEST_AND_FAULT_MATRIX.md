<!-- doc-head: Stage 1098A offline self-test and fault-injection matrix for the 1097A PtP canary verifier, synthetic fixtures only, no live claim -->

# Stage 1098A - PtP Canary Self-Test and Fault Matrix

Test: `tools/autoresearch/test_ptp_canary_verifier_selftest.py`
Receipt: `artifacts/autoresearch/stage1098a_ptp_canary_selftest_and_fault_matrix.json`

## Isolation
- Fixtures are written and read only under `tempfile.TemporaryDirectory()`.
- Every fixture dict carries `"synthetic_fixture": true`; session ids start `SYNTHETIC-`.
- Receipt carries no fixture markers, no `controlled_aa_valid` and no `physical_workload_acceptance`. It records only the matrix rows.

## Matrix (scenario -> expected verdict)
- clean pre/post -> `PASS`
- mtd5 sha changed -> `FAIL_MTD_CHANGED`
- aql readback missing BC/MC -> `FAIL_BCMC_MISSING`
- tx bitrate below explicit floor -> `FAIL_MCS_DEGRADED`
- ping 18/20 -> `FAIL_LOSS`
- ping 5/5 -> `INSUFFICIENT_PROBES`
- no floor supplied -> `SKIPPED_NO_FLOOR`
- post rollback marker -> `ROLLBACK_TRIGGERED`

## Caveats
- Captures are parsed offline; nothing here is a live claim.
- mtd check is invariance only; there is no reference hash in the repo.
- The WDS `phy*-ap0.sta1` fixture text is operator-pattern-derived, not a capture.
- The MCS floor is a parameter; the test floor is a test-only number, not a repo value.
