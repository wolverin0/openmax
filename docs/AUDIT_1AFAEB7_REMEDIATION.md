<!-- doc-head: Audit1afaeb7 remediation, offline acceptance and blocked target-execution experiment -->
<!-- /doc-head -->

# Audit1afaeb7 remediation handoff

Audit base:1afaeb7712161068044238755166dff3a7043248. No radio, RF, flash,
DHCP/firewall on devices, reboot or target-firmware execution was authorized or performed.

## Findings and execution paths

| Finding | Current fix and scope | Residual acceptance |
| --- | --- | --- |
| A01/A02 | WA v13 defaults PLANNED; explicit identity, snapshot, native readback, rollback; supported fq_codel tokens. Generator consumes maintained helper. Old v11/v12 actuators retired. | Native tc/kernel behavior, power-cut restoration and RF UNKNOWN. |
| A03 | PB060 requires observed controls, config binding, independent receipt and disjoint identities/windows; invalid control invalidates campaign. | Actual primary acquisition/instrument trust remains required. |
| A04 | Historical callable Flent parser marks missing replies INVALID, preserves actual sent/received counts and separates receiver/sender rates. | No demonstrated connection to recent native bench runners; do not attribute all campaigns to this parser. |
| A05 | One strict evaluate/evaluate_paired path, explicit width, finite/range checks, unique paired IDs and whole-baseline drift. | Other saved-data auditors retain their own declared scope. |
| A06 | Objective frozen before acquisition: latency with capacity non-inferiority, capacity with QoE constraints, robustness; interval guards. | Capability discovery needs its separate witness. |
| A07 | Correct single-step Sidak naming; resolution preflight, exact/binomial sign flips and conservative Monte Carlo bound. Alpha is not relaxed. | No claim of unlimited sequential search error control. Independent confirmation plan/family is required. |
| A08 | Immutable source classification and SYNTHETIC_PASS; synthetic fixture consumers cannot physically promote. | Saved historical fixtures are not new measurements. |
| A09/SGMT | Inspection separate from validation; board/EOF/version/range/overlap checks; raw0 encoding; no acceptance assert; complete optional image identity binding. | Unbound composition stays offline; actual target decoder/loading/execution UNKNOWN. |
| A10 | Acquisition bytes, readback width/config, counters, peer denominator, dataset labels, chronology and discovery health bound to confirmation. | Receipt integrity/arithmetic does not authenticate an instrument or execute a radio. |
| A11 | README links route to a real public index, pinned software dependencies and a reproducible core command. | Private reports, raw and vendor binaries remain private. |

The generic gate is canonical for its controller consumers. The R71-R75 exact-Holm
saved-data auditors are independent; this remediation does not invalidate their results.
PB060, PowerBeam and several controller builders are offline fixture generators.
SGMT constructors817/879 are offline; the RAM canary preparer prepares a plan, not a live run.
The WA helper is an invocable actuator tested only with command stubs; its generator is offline.
PB070's old boolean predicate is hypothetical metadata, not a physical capability witness.

## Reproduce

`python tools/verify/verify_chatgpt_audit_1afaeb7.py`

Requirements: Python3.12, requirements-audit.txt, POSIX bash/coreutils.
The command runs public synthetic fixtures and software contracts. Private firmware
checks are separate via --private and require held inputs; none are acquired automatically.
Original external audit and local red/green receipts remain preserved privately.
The initial unmodified proposed suite reproduced24 failures; extra adversarial cases
were added for actual receipt tampering, unhealthy discovery/sentinels and overlapping windows.
Independent reviews covered the WA transaction, SGMT and measurement/statistical guards.

## Claims and authority

| Claim | Classification |
| --- | --- |
| Default-no-write, invalid data rejection, SGMT bounds/codec vectors, rollback failure handling | Demonstrated offline with synthetic data/command stubs. |
| WA344 windows,78.51Mbps peak,-86.37% loadedp50; LTU264 windows; PtP25.47Mbps | Imported historical summaries. Original run IDs/date/raw linkage not established by packaging: UNAVAILABLE_TO_THIS_REVIEW. |
| Guarida v10 and1000-window scorecard | Uncalibrated modeled data; not a new physical window count. |
| Exact target patch running, universal board compatibility, native DHCP persistence, field gain | UNKNOWN in this review. |

States: SYNTHETIC / STATIC_VERIFIED / BENCH_EXECUTED / BENCH_REPLICATED /
FIELD_CANARY / PRODUCTION_ACCEPTED. Copying a report cannot supply a higher source state.
No fixture PASS is field/production acceptance. No gain percentages are added across experiments.

## One next physical experiment: inert target-execution canary

Status: BLOCKED_PENDING_OPERATOR_AUTHORIZATION_AND_EXACT_WITNESS.
Question: does the coprocessor execute the exact modified target image, without fallback?
Use one isolated, exact board/revision/kernel/driver/firmware/role, unchanged legal RF
settings, and original/sham-repack/inert-canary arms. Freeze whole-image hashes,
ABI/site/preimage, acquisition schedule and a target-side witness before acquisition.
The witness must demonstrate execution of the changed path; file presence, reassociation
or unmount alone is insufficient. Do not change scheduling, rates, DFS, calibration or ART.
Capture loader/target identity, fallback checks, control witness, health and timestamped raw.
A sham must not emit the canary witness. Restore and verify the original running target,
not only filesystem contents; watchdog and independent recovery must already be accepted.
Missing identity, witness, sham discrimination, health or restoration is a failure.
No physical canary script was executed or authorized by this software task.
