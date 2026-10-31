<!-- doc-head: Stage1173A records the full existing Stage1001A..1172A offline test inventory, native exits and retained failures -->
<!-- /doc-head -->

# Stage1173A — Full offline pytest matrix

The runner inventories every existing `test_stage*.py` whose stage numbers lie entirely in1001A..1172A. The1174A suite runs separately, preventing recursive gates. Individual contract files remain included alongside consolidated suites; totals count testcase executions, not unique experiments.

```powershell
node ../wezbridge/scripts/heavy-slot.cjs run -- python tools/verify/run_stage1173a_full_pytest_1001a_to_1172a.py --attempt matrix1
```

Each immutable attempt retains source/data bindings before and after, original input bytes, per-file argv, exits, logs and JUnit. Any failed, empty, errored or skipped test, source drift, missing input, unexpected data mutation or offline-guard event blocks the matrix. Fresh output is `artifacts/verification/stage1173a_full_pytest_1001a_to_1172a.json`; earlier attempts are preserved.

The execution review covers only local static producers, disposable shell fixtures and transport mocks. Git `sh.exe` precedes other shells on PATH. An inherited Python guard denies socket operations and direct network executables; its Popen subclass remains compatible with Windows asyncio.

Known byte-determinism tests regenerate only1031A..1036A,1055A..1060A,1085A..1090A,1107A..1108A local outputs. These changes are recorded, not erased. Data changes outside that reviewed set block acceptance. Current source bytes and captured outputs must replay exactly.

A clean offline suite does not establish live radio access, RF performance, production readiness or zero false positives. Missing native evidence stays missing. The final JSON contains actual results and limitations; this document does not predeclare a pass.
