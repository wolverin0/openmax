<!-- doc-head: Stage530A offline525..530 master gate with retained repository findings -->
Seven explicit suites, revision-bound independent reviews and the literal repo gate.
Tool validation, repository policy and physical acceptance have separate outcomes.
<!-- /doc-head -->

# Stage530A — master evidence gate

Parent: fixed525A..530A offline RE1/control-boundary reconciliation in BENCH_PLAN.
Run `python tools/verify/verify_stage530a_codex_530stage_master_gate.py`.
The runner creates an exclusive artifacts/verification/stage530a/run_NNN directory.
It retains actual commands, stdout/stderr, exits, JUnit cases and before/after hashes.
Failures survive subsequent runs. No producer, radio, target code, firmware,
SSH, ping, configuration, patch, flash or load acquisition is executed.

Each525..529 receipt is checked against its held implementation/dependencies/doc.
Declared original sources are also pinned before/after this run. Changes since
the stage cutoff and changes during this run are separate INCOMPLETE findings;
neither is repaired by rewriting evidence or repeating acquisition producers.
Each independent review must bind the four current stage deliverables and have
an explicit PASS verdict with an explicit empty blocking_findings list.
Seven exact pytest files must all appear in xunit1 JUnit, with at least one case
each, no unexpected files, no missing file attributes, no skips/errors/failures,
and a real zero process exit. Missing files never trigger unscoped pytest.
The final530 receipt cannot include its own hash or require itself inside pytest;
its creation, pin and independent530 review are checked after this runner.

The second child command is literal:
`python tools/verify/enforce_5pillar_research_gate.py --check-repo`.
That command checks repository wiring. A zero exit does not authenticate every
receipt, validate every scientific pillar or establish physical acceptance.

Stage529's entire scoped JSON/Markdown inventory is a bounded held-file cutoff,
including labeled historical/vendor deviations. It is not a transactional live
snapshot or proof of500/530 completed experiments. Its self-exclusion and the
later-created530 files are explicit; this gate separately checks its own docs.
No historical/vendor documents are rewritten to manufacture global compliance.

Exit0 requires all local checks AND Stage529 PASS_SCOPED_STRUCTURAL_POLICY.
Exit1 with VALIDATED_TOOLING_WITH_REPOSITORY_FINDINGS means pytest and wiring
passed, but Stage529 retained FAIL/UNASSESSED findings. Missing/stale evidence,
drift or failed checks have a distinct INCOMPLETE_OR_FAILED_LOCAL_EVIDENCE status.
Exact counts and policy findings are in the JSON, not copied into this document.

525 separates24.83Mbps aggregate and9.96Mbps UL profiles and the unrelated R45
pktlog delta.526 distinguishes register text from firmware-load/ABI causality.
527 recomputes6.453125dB and a cumulative99.1972% counter ratio, not storm rate.
528 finds38 dcxo/tcxo symbols (11bbp_rf_dcxo),12 direct windows vs144 cumulative
claims, loopback probe/default risks and no DCXO-to-OTA causal proof.
All are saved/static evidence with qualifications. E2 remains NOT_ACCEPTED.
Decision: KEEP reproducible local audits; no new hardware or performance acceptance.
