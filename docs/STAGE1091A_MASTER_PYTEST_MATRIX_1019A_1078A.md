<!-- doc-head: Stage1091A records nine offline pytest suites with per-suite JUnit, exit codes and frozen source inputs -->
No SSH, radio, RF workload or actuator-kit execution belongs to this matrix.
<!-- /doc-head -->

# Stage1091A master pytest matrix

The runner executes exactly the nine requested suites: 1019A..1024A, 1025A..1030A, 1031A..1036A, 1037A..1042A, 1049A..1054A, 1055A..1060A, 1061A..1066A, 1067A..1072A and 1073A..1078A.

Each row records its actual Python argv, process exit, timeout state, stdout/stderr log, JUnit XML, testcase counts and SHA256 bindings. Empty, skipped, failing, missing or unbound results cannot pass. Counts measure testcase executions, not physical experiments or independent RF samples.

Source/test/kit bytes are captured before and after the complete run. Static local import dependencies and matching stage producers are included. Source drift prevents acceptance. Every pre-run source, relevant receipt and document is archived by SHA256 before tests start.

The 1031A..1036A and 1055A..1060A suites deliberately execute local reverse-engineering producer scripts twice. Their receipt/document changes are recorded separately as expected generated outputs; this does not waive test failures or permit changing source code, kits, saved native observations or unrelated receipts.

The test processes inherit a Python startup guard that rejects socket connections and direct SSH/network executable launches. This guard is additional containment, not a claim that arbitrary shell programs are sandboxed. The selected tests and local producers are reviewed for offline scope before execution.

Run under the machine-wide heavy-job semaphore:

```powershell
node ../wezbridge/scripts/heavy-slot.cjs run -- python tools/verify/run_stage1091a_master_pytest_matrix_1019a_1078a.py --attempt baseline
```

Existing attempt directories are never reused. The latest receipt is `artifacts/autoresearch/stage1091a_master_pytest_matrix_1019a_1078a.json`; each attempt retains its own immutable result, inputs, logs and XML under `artifacts/verification/wave12_stage1091_1092/`.

`replay_receipt()` checks the literal nine suite identities, current source bindings, command/log/XML bindings, recomputed counts and verdicts. A baseline failure remains visible when a later authorized repair is tested in another attempt. Prior receipts are not silently repinned.

All evidence is attributed to the external controller. No pass certifies production rollout, live association, packet loss, goodput, latency, watchdog restoration, physical board compatibility or publisher authenticity.
