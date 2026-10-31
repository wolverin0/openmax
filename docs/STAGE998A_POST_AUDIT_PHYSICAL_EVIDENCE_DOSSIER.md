<!-- doc-head: Stage998A bounded post-audit saved-evidence dossier; reference integrity is not physical authentication -->
<!-- /doc-head -->

# Stage998A — Post-audit physical-evidence dossier

Status **RECONCILIATION_COMPLETE_WITH_PHYSICAL_BLOCKERS**. This is local evidence reconciliation, with no hardware access.
Provenance: **EVIDENCE_RECONCILIATION_ONLY**, attributed to the external controller.

## Exact scope

Stage filename numbers885..997, primary JSON files directly in artifacts/autoresearch
and artifacts/verification: **98 files**,
**92 stage numbers**. This is not an audit
of all repository receipts or proof that1000 physical experiments occurred.
Latest required inputs missing: `[]`.
Source snapshot stable: `True`.

| Saved-reference classification | Files |
| --- | ---: |
| DECLARED_MODEL_ONLY | 10 |
| DECLARED_STATIC_BINARY | 33 |
| DECLARED_STATIC_BINARY_WITH_NATIVE_REFERENCES | 3 |
| IMPORTED_SAVED_NATIVE_REFERENCE_INTEGRITY_VERIFIED | 8 |
| SAVED_NATIVE_REFERENCE_INTEGRITY_VERIFIED | 15 |
| UNKNOWN_REFERENCE_ORIGIN | 29 |

## What was checked

Every selected primary file is pinned by SHA256/bytes and parsed with duplicate-key
and nonfinite-number rejection. Hash-bound references are checked within the repository,
with bounded recursive traversal. Naked paths, status tokens, device IP strings and
metric names do not qualify a capture reference. Failures and unreadable files remain.
Declared classes are retained separately; importing capture data does not turn a model
into a hardware result. Source changes during the scan fail reconciliation stability.

The saved-reference graph contains220
unique capture files and237
saved transport rows. These counts are not independent experiments or positive tests.
Matching saved hashes establish reference integrity only. They do not authenticate
physical origin, guarantee truthful instruments or constitute a new hardware retest.
Historical host-key trust metadata is retained without inventing prior pinning.

## Post-audit boundary

The structured ledger retains saved negative outcomes, partial telemetry, failed
preconditions and source drift. Core facts include899A lossy baseline A/A,906A239/240
responses,907A failed autonomous rollback plus separate manual recovery, and929A/954A
real mode invocations rejected before setters.932A file/container checks do not prove
currently executing firmware bytes.953A tool bootstrap is not a multiflow benchmark.
Passive CPE/LTU observations and local Flent rejection are not zero-FP calibration.
The999A reconciliation summarizes these boundaries without converting UNKNOWN to zero.

## Artifacts

[Builder](../tools/verify/build_stage998a_post_audit_physical_evidence_dossier.py),
[JSON dossier](../artifacts/autoresearch/stage998a_post_audit_physical_evidence_dossier.json).
Run `python tools/verify/build_stage998a_post_audit_physical_evidence_dossier.py --write`
only after the latest input receipts are stable. Default execution prints a summary
and does not write the final dossier. Model/static/live declarations remain scoped.

Physical acceptance **NOT_ACCEPTED**; zero-false-positive calibration **UNKNOWN**.
No deployment, hardware gain, complete CPE coverage or automatic recovery is approved.
