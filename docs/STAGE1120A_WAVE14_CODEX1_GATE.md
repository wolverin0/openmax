<!-- doc-head: Wave14 fail-closed offline transaction, passive telemetry, five-suite and shell audit gate -->
Local verification and physical acceptance are reported separately.
<!-- /doc-head -->

# Stage1120A — Wave14 Codex1 gate

The gate verifies the four Stage1115A..1118A results, the exact Stage1119A ledger, their source bindings and fresh tests. It performs no SSH, radio connection, shell-kit application or proprietary device-node operation.

| Required check | Offline contract |
|---|---|
| WA/Panel1 transaction verifier | Native-backed known fields, explicit missing baseline fields, blocked native admission and labelled offline fault injection |
| LTU passive evaluator | Saved snapshot identities/epochs/counter coverage and provisional, uncalibrated thresholds; no invented zero false-positive result |
| Five-suite matrix | Exact requested suites, complete original input archives, literal argv, native integer exit codes, nonempty clean JUnit and matching logs |
| V16/V17 shell audit | Exact current inventory, hashes, zero forbidden command/masking tokens and zero CRLF |
| Reconciliation ledger | Exact seven-input replay with no historical claim promoted into a new measurement |
| Fresh gate pytest | Current source/doc/test hashes plus actual command, exit, stdout log, JUnit and independently recomputed counts |

An absent or failed mandatory check produces `INCOMPLETE` and a nonzero CLI exit. Missing native snapshot fields are a correct fail-closed planner result; they never become a claim that a complete V17 transaction was admitted or executed.

```powershell
python tools/verify/verify_stage1120a_wave14_codex1_gate.py --validation artifacts/verification/wave14_final/local_validation.json
```

Passing all local checks yields `OFFLINE_WAVE14_VERIFIED_PHYSICAL_PENDING`. The output still records `physical_ready=false`, `physical_acceptance=NOT_ACCEPTED` and `deployment_authorized=false`.

The test receipt binds this gate, its helper, upstream sources, documentation and `tests/test_stage1115a_to_1120a_suite.py`. Failed, skipped, empty, drifted or unbound test evidence cannot close the gate. Earlier failed attempts remain archived rather than being relabelled.

Output: `artifacts/autoresearch/stage1120a_wave14_codex1_gate.json`. Offline model restoration is not a native watchdog rehearsal; sparse passive telemetry is not production threshold calibration.
