<!-- doc-head: Stage792A seven-suite offline787..792 gate with frozen provenance and explicit limits -->
Local software validation is separate from DHCP, RF, reliability and800-stage acceptance.
<!-- /doc-head -->

# Stage792A

Parent: fixed787A..792A offline RE1 support in BENCH_PLAN.
Run `python tools/verify/verify_stage792a_codex_787a_to_792a_gate.py`.
Each stage has its own script, JSON, compact initial-header doc and dedicated suite.
The seventh suite checks the consolidated contracts. No hardware, network,
producer/helper/firmware execution, DHCP probes, configuration, channel change,
flash, deployment, remote access or RF load is performed.

## Reproducible local gate

Each invocation gets an exclusive artifacts/verification/stage792a/run_NNN folder.
Retain actual subprocess commands, stdout/stderr, exits, JUnit and before/after pins.
Run only the seven explicit pytest files, with addopts cleared and xunit1 file
attributes required. All seven files need nonzero collected cases, no unexpected
file, skip, failure or error, and a real zero child exit. Missing suites, reviews,
frozen copies, invalid manifests, drift or malformed containers cannot pass.
No absent-file fallback invokes an unscoped pytest or recursively runs this gate.
PYTEST_ADDOPTS/PYTEST_PLUGINS are removed from child environment by the capture helper.

Independent787..791 reviews must explicitly PASS with empty blocking findings
and bind the current four stage deliverables, three analysis dependencies and
source manifest. Every manifest must match the receipt and its frozen copy hashes.
Original source paths are diagnostic; immutable copies define the analyzed cutoff.
Source-origin changes are recorded separately and never silently repinned.
This is neither current runtime proof nor authenticated historical acquisition.
The final792 receipt cannot hash itself or be required by its own inner pytest;
its creation/pin and independent792 review are checked after the run.

Run the literal second command:
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
Its zero exit is wiring/budget evidence only, not every receipt's five-pillar
scientific acceptance. Historical529 findings and530's205PASS/2FAIL remain in791.
No inherited failures are overwritten or reclassified as passing this new queue.

PASS_LOCAL_TOOLING_ONLY/exit0 requires all local checks and revision-bound reviews.
Other outcomes retain INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE/exit1 with exact gaps.
Even a local pass leaves physical acceptance UNKNOWN, E2 NOT_ACCEPTED and800
readiness HOLD_EVIDENCE_GAPS. No fixture count or hypothetical bound promotes RF.
787 is conditional nominal-channel efficiency,788 is an uncalibrated two-ray/AWGN
capacity integral,789 cannot prove runtime DHCP eradication,790 cannot establish
20h zero-outage surveillance, and791's catalog is filename presence only.
All six new documents stay below200 lines with one initial paired doc-head.
Decision: KEEP verified local tools and unresolved empirical evidence explicitly.
