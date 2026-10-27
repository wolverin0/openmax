<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage900A — Post-audit live execution gate

2026-10-27. Overall **INCOMPLETE**, acceptance **NOT_ACCEPTED**.
No deployment is authorized. No target firmware, qdisc or RF configuration was changed.

| Stage | Actual outcome |
| --- | --- |
| 897A | Native WA preflight and unchanged-kit dry-run; unsupported verify; apply blocked |
| 898A | No WA A/A, discovery or holdout acquisition |
| 899A | PowerBeam16 measured baseline windows; Rocket read-only; gate safety REJECT |
| 900A | Hash-bound native replay, regression tests and honest physical blocker ledger |

## Deterministic local checks

The gate validates source/receipt/native capture hashes, frozen producer revision,
pre/post configuration equality and acquisition identities. It recomputes receiver
bytes, actual RTT arrays, sent/received counts and normalized receipt bytes from native
SSH output for every PowerBeam window. The hardened Flent parser and nearest-rank
percentiles independently parse those same outputs. Adapter evaluation must equal the
original result at the frozen gate/schema revision; source drift fails verification.
Post-cohort health verifies unchanged configuration and absence of owned temporary
files/processes. Docs must have one paired line1 doc-head and fewer than180 lines.

## Acceptance boundary

PowerBeam A/A has8 measured pairs,457179136 receiver bytes,261/320 ping replies.
Raw gate **REJECT** is due to packet loss before paired statistical inference.
Adapter **PASS_NO_PROMOTION** is retained literally. Statistical calibration is
**NOT_ACCEPTED**: paired_blocks_count0 means its default effects/CI/p fields are not
estimated results. Local replay can pass while this physical criterion remains open.

WA .20 lacks tc/ath0/native board_revision, has incompatible AQL labels, and the kit
implements3028/2.5ms/50ms rather than requested1514/5ms/100ms. It has no --verify mode.
.195 timed out; .251 native identity is Rocket2AC airOS rather than an OpenWrt STA;
.250 is ROSSSH/MikroTik. No identity/profile guard was bypassed to force application.
No disjoint WA holdout, full qdisc readback, exclusive RF path proof or Rocket peer
control exists. Those are physical blockers, not fixture failures to erase.

## Reproduction and retained evidence

Local-only commands, with no automatic hardware workload on import:

```text
python -m pytest tests/test_stage897a_to_900a_suite.py tests/test_stage897_900_gate_adapter.py tests/test_chatgpt_audit_1afaeb7_regressions.py
python tools/verify/verify_stage900a_post_audit_live_execution_gate.py --validation artifacts/verification/stage897a_to900a_validation.json
```

Gate exits2 for physical INCOMPLETE even if all local checks pass.
[Gate receipt](../artifacts/autoresearch/stage900a_post_audit_live_execution_gate.json)
contains exact local check outcomes, replay summaries and validation counts.
[Validation](../artifacts/verification/stage897a_to900a_validation.json) binds test logs,
JUnit output and independent review. Initial six adapter API failures and invalid
fractional-interval acquisition remain preserved; subsequent checks do not erase them.

Next: resolve native WA STA access and kit/profile compatibility; freeze fresh matched
WA A/A/discovery/holdout protocols and obtain independent acceptance. Do not relabel
the existing lossy PowerBeam baseline control as successful WA treatment or calibration.
