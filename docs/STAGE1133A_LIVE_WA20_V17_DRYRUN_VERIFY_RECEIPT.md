<!-- doc-head: Stage1133A one fresh WA20 authentication attempt rejected; no remote dry-run or configuration write -->
Saved source review and local shell validation are distinct from unavailable target readbacks.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1133A — WA20 V17 dry-run verification

The approved target was `198.18.0.43`, account `ubnt`. One fresh Paramiko authentication attempt used the operator-provided credential in process memory only. Authentication was rejected with `AuthenticationException`.

| Criterion | Actual result |
|---|---|
| Authentication | FAILED; no alternative account or credential tried |
| Remote commands / `/tmp` upload | Zero / none |
| Remote dry-run exit | UNKNOWN / NOT_EXECUTED |
| Native board, PHY and interface identity | UNKNOWN; the supplied NanoBeam label was not confirmed |
| AQM, AQL, threshold and TCP readbacks | UNKNOWN / NOT_COLLECTED |
| Before/after equality | NOT_EVALUATED |
| Configuration, firmware or RF writes | None |
| SSH client lifecycle | Closed after the rejected attempt |

The exact local WA V17 kit SHA256 was `c52d63a481bbe9d8ecd0f8c0ebb5e1361cadf83316de231c5ea443a7df63e8db`. Its `--dry-run` branch was reviewed before connection: it prints the plan and invokes only pure target-format helpers, then exits. A local invocation with `C:/Program Files/Git/bin/sh.exe` returned exit0; this does not establish target execution.

The runner permits only the named `/tmp/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh` file, requires a regular non-symlink target, reuses identical existing bytes, refuses a differing file, and uses exclusive creation for a new file. Successful readback would compare identity/boot/interface state, AQL including BC/MC, AQM RW values, threshold, TCP setting and snapshot presence. Dynamic AQM traffic counters are excluded. This code path was not reached on the radio. Any kit-byte change, including comments, requires a new explicit source review; only the reviewed SHA256 is accepted.

The [receipt](../artifacts/verification/stage1133a_live_wa20_v17_dryrun_verify_receipt.json) binds the [fresh acquisition record](../artifacts/verification/1133a/acquisition.json), runner and kit. The [source/local-shell review](../artifacts/verification/stage1133a/source_and_local_dryrun_review.json) and [20 parent-review contract checks](../artifacts/verification/stage1133a/local_contract_checks_parent_review.json) retain their separate scope. A local verification-driver path error is preserved; it caused no additional network attempt.

The exact collector used for the attempts is archived separately from the later analysis-only corrections. The [lineage](../artifacts/verification/stage1133a/acquisition_source_lineage.json) binds its original bytes and both unchanged raw acquisition records. `network_attempted` and `target_contact_attempted` are true for `.20`, while `authenticated_target_access` and `hardware_access` are false. No successful target session is inferred from an authentication rejection.

`BLOCKED_OR_INCOMPLETE_NATIVE_DRYRUN` is the required result. No saved Stage1021 data replace missing fresh measurements, and no applied V17 profile, production readiness or RF performance is claimed. The process-only credential is absent from the source and receipts. A corrected access path requires a new explicit acquisition, not an automatic retry of this one.
