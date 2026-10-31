<!-- doc-head: Stage1137A revision-bound execution of eight requested offline suites; failures remain failures -->
No live collector, radio, SSH command or Orca pane is contacted by this runner.
<!-- /doc-head -->

# Stage1137A consolidated pytest matrix

The exact suites are 1085A..1090A, 1091A..1096A, 1097A..1102A, 1103A..1108A,
1109A..1114A, 1115A..1120A, 1121A..1126A and 1127A..1132A.

Each invocation retains argv, exit status, stdout/stderr, JUnit XML and recomputed
counts. Empty, failed, skipped, missing or changed evidence cannot become PASS.
The source/test/kit inventory and complete original input archives are verified.
Top-level autoresearch and verification receipts and the matching docs are scoped
explicitly; mixed receipt locations are supported.

The 1085A..1090A and 1107A..1108A test fixtures regenerate only local static-analysis
receipts/docs. Their original bytes are archived first. Other input changes fail
closed. This does not authorize a producer that contacts hardware.

Python children inherit connection and network-executable guards. The subprocess
guard preserves the Popen class needed by Windows asyncio. Guards are additional
checks, not proof that every arbitrary shell program is safe.

```powershell
python tools/verify/run_stage1137a_consolidated_pytest_1085a_1132a.py --attempt matrix1
```

The new receipt is artifacts/verification/stage1137a_consolidated_pytest_1085a_1132a.json.
Historical ath10k-absence clauses may be refuted by later extracted modules.
The runner preserves that failure and never removes modules or changes old tests.
No matrix result certifies RF, apply, rollback, calibration or production readiness.
