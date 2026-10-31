<!-- doc-head: Stage1138A fail-closed readonly/dry-run receipts and consolidated-test gate -->
The gate reads local evidence only; its execution never connects to a device.
<!-- /doc-head -->

# Stage1138A Wave17 gate

Mandatory inputs are the exact 1133A, 1134A and 1135A receipts, their independently
replayed 1136A readiness record, and all eight requested suites from 1137A.
Any failed authentication, missing native state, bad exit, changed configuration,
unverified upload, stale hash, missing test or failed suite blocks acceptance.

The gate delegates native replay to the readonly readiness verifier, compares its
complete deterministic output, and requires its explicit live-receipt verdict.
Receipt presence or a title containing CONFIRMED is never sufficient.

Fresh gate-test evidence binds current source/docs, literal argv, zero native
exit, the log and JUnit. Counts are recomputed; empty, skipped, failed, stale or
unbound test evidence is rejected. Historical matrix failures remain failures.

```powershell
python tools/verify/verify_stage1138a_wave17_codex1_gate.py --validation artifacts/verification/wave17_final/local_validation.json
```

Output is artifacts/verification/stage1138a_wave17_codex1_gate.json. Exit1 and
INCOMPLETE preserve every unresolved mandatory criterion. Passing local tests
does not alter an authentication denial or establish RF/production readiness.

No gate code opens an AME device node, uploads a kit, runs a shell kit or retries
credentials. Dry-run cannot prove apply/rollback safety; sparse LTU observations
cannot calibrate zero false positives. Physical acceptance remains NOT_ACCEPTED.
