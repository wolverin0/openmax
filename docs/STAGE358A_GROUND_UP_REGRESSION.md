<!-- doc-head: Stage358A local353..358 regression gate and evidence boundaries -->
Seven explicit pytest files and the literal repository gate; no radio actions.
<!-- /doc-head -->

# Stage358A

Parent: fixed353A..358A offline RE1/control-boundary queue.
Run `python tools/verify/run_stage358a_ground_up_regression.py`.
Each stage has its own script, JSON, compact document and dedicated pytest file.
The seventh suite checks their shared no-hardware and evidence contracts.
The runner never invokes an unscoped pytest when a suite is absent.

Tests use disposable files, saved modules, finite simulations and pinned native
SquashFS host tools. No device code, SSH, ping, flash, radio configuration or
hardware acquisition is invoked. Native host decompression is explicitly distinct
from prohibited execution of the held firmware/modules or target commands.

Each invocation gets an exclusive numbered directory under
artifacts/verification/stage358a. Stdout, stderr, commands, actual process exits,
JUnit cases, before/after input hashes and revision-bound353..357 reviews are
retained. A missing/failed/stale review prevents closure. Skips, zero tests,
missing files, source drift, process failure or missing JUnit cannot pass.
PYTEST_ADDOPTS/PYTEST_PLUGINS are removed from the child environment and configured
addopts is overridden. xunit1 file attributes must cover all seven exact suites;
missing/unexpected files or absent file attributes prevent a partial-collection pass.
Failures are not overwritten by a retry; an evidence-led changed fix requires a
new invocation. No runner executes itself recursively from its own unit tests.

The literal second command is:
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
Its exit and output are captured separately. This command checks repository wiring
and document budgets. It does not validate every receipt, physical provenance or
five-pillar scientific acceptance. Stage357 retains that distinction explicitly.

The final JSON is the source for exact pass/fail/skip counts and qualified status.
353 conditional source timing is not QCA988x5/10MHz runtime support. 354 retry
plans emit no native188B WMI payload. 355 is an uncalibrated AirSelect-inspired
fluid model. 356 saved evidence consistency never approves a flash or guarantees
zero bricks. 357 file coverage is not350 accepted experiments. E2 NOT_ACCEPTED.
Decision: KEEP verified local tooling; physical/regulatory acceptance remains open.
