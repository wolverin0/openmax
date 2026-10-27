<!-- doc-head: 936A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# PowerBeam and LTU adversarial command-stub evidence

Software-only adversarial tests: PASS.

Fresh pytest: 139 passed, 0 failures, 0 errors, 0 skipped.
All shell entrypoint and test bytes are pinned before execution and checked afterwards.
Defaults, supported transactions and blocked legacy entrypoints have distinct contracts.
Tests use disposable uci/tc/sysfs/sysctl command stubs; no host or device knob is changed.
Fault cases reject unsupported defaults, failed getters, false readbacks and failed restoration.
The static provenance enum describes source/software evidence only, not native binary acceptance.
Zero live windows. Physical acceptance: UNKNOWN.
