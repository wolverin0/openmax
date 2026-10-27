<!-- doc-head: Stage268A complete available231..268 pytest execution and explicit coverage gaps -->
Missing suites and recorded failures prevent full-range acceptance even when available tests pass.
<!-- /doc-head -->

# Stage268A

Parent: reproducible release verification. Question: what actually passes in the
requested231..268 range, and which stage tests cannot be found?

Run `python tools/verify/run_stage268a_release_regression.py`.
`--list` inventories only; it does not execute or import test modules.
The runner selects all test files naming a stage in231..268, expands combined
stage ranges, and includes the existing Stage232 preflight fixture suite by its
legacy filename. Presence of a suite does not mean that stage's release was accepted.
The runner includes its own pure unit tests; they never invoke a recursive run.

It executes one argv-based pytest command, captures stdout/stderr and exit code,
and reads exact tests/failures/errors/skips from JUnit. Then it executes literally
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
Every attempt has a new directory under `artifacts/verification/stage268a/`.
No failed run is overwritten. A timeout or absent executable is not an invented exit.
The receipt is `artifacts/autoresearch/stage268a_full_pytest_and_gate_receipt.json`.

Selected older suites are local JSON/ELF-analysis checks; some rerun deterministic
offline dissection generators. No native device runner, SSH or RF test is selected.
The seven legacy dissection receipts are copied before the run and checked after it.
Newly discovered unreviewed suites block execution until their side effects are reviewed.
Missing stage numbers are listed. A green available subset cannot close missing
coverage: `full_requested_range_accepted` remains false and CLI returns1.
The repo gate checks wiring/compact core docs; it does not prove every receipt
scientifically compliant or repair Stage263/264 findings.

No production, hardware, flash, release publication or external message occurs.
