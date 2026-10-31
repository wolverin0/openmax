<!-- doc-head: Stage957A actual passive-telemetry replay must fail closed as a Flent application workload -->
<!-- /doc-head -->

# Stage957A — Flent fail-closed validation

2026-10-27. Local pure replay of hash-bound Stage955A/956A native inputs.
This stage does not initiate SSH, application traffic, ping or device writes.

## Expected outcome

Pass the native passive telemetry dictionaries in their original schema to the
actual `FlentWorkloadOrchestrator.synthesize_report`. Interface counters, CPU ticks
and IRQ observations must not be renamed into application receiver goodput, actual
sent/received ICMP counts or latency arrays. Missing workload evidence must produce
INVALID, null aggregate goodput and null fleet RTT percentiles for both Panel1 CPEs
and LTU. This is a successful guard check, not a successful physical benchmark.

The receipt provenance refers to its bound live input telemetry only. Validation
execution is LOCAL_PURE_REPLAY and physical_workload_executed is false. A passive
capture cannot establish controlled A/A, discovery/holdout replication, a candidate
gain, production acceptance or a zero false-positive rate.

## Disposable local contract fixtures

Five labelled checks cover: complete numeric positive control retaining physical
UNKNOWN; absent measurements; sender-only throughput; all-lost ping never becoming
zero RTT; and latency-array/count mismatch. Fixture numbers are not radio evidence
or a calibrated RF model. No core Flent source is modified.

[Verifier](../tools/verify/verify_stage957a_live_telemetry_flent_fail_closed.py),
[receipt](../artifacts/autoresearch/stage957a_live_telemetry_flent_fail_closed.json).
The receipt binds the exact Flent source revision and both native-stage receipts.
Stage958A can replay these checks without contacting a device. Promotion remains
unauthorized and zero_false_positive remains UNKNOWN regardless of local PASS.

Actual invocation `--check` exited0: Panel1 and LTU native telemetry both produced
INVALID workload reports with null aggregate goodput and null fleet RTT percentiles.
All five disposable local contract checks passed. No pytest count or executed
physical Flent/multiflow benchmark is claimed by this verifier.
Source/data bindings are retained; no additional955A..957A work follows the newer
operator queue995A..1000A.
