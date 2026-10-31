<!-- doc-head: Stage929A exact WA kit copied to live .20; four real modes captured, native admission blocked without profile writes -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage929A — Live WA kit transaction admission

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE** for actual SSH reads, file copy
and entrypoint exits. Status **BLOCKED_NATIVE_APPLY_PRECONDITIONS**; configuration
acceptance **NOT_ACCEPTED**. Attribution: external controller and Linux/mac80211.

## Exact copy and native target

Target only198.18.0.43, root via the documented credential accessor. Native board
is `ubnt,lap-120`, OpenWrt24.10.4/kernel6.6.110, AR9342rev2, interface `phy0-ap0`,
PHY `phy0`, driver `ath10k_pci`, firmware `10.1-ct-8x-__fW-022-ecad3248`.
No other host, production panel, core device or protected partition was accessed.

The unchanged15471-byte canonical kit was streamed to `/tmp/fmx_wa_v13.sh`, with
symlink/nonregular-file guards and a unique backup of any prior regular file.
Remote SHA256 matches the saved source snapshot:
`821a9aa83fcf030d4ebdcd67fb7ae9648e3bfe1dcbbab39df5fc38e841d44fd1`.
The requested RAM copy remains available. Its prior-copy backup path, if created,
is recorded in the receipt. No persistent installation was performed.

## Four actual invocations

All modes used the copied file and `--qdisc-mode auto`; each invocation checked its
remote hash first. A unique identity/state path was selected but no trusted identity
contract was published because native admission/recovery requirements were unmet.

| Mode | Actual native exit | Actual result |
| --- | ---: | --- |
| `--dry-run` | 0 | PLANNED; qdisc backend UNSELECTED; runtime UNKNOWN |
| `--apply` | 65 | FAILED_PRECONDITION missing tool: stat |
| `--verify` | 65 | FAILED_PRECONDITION missing tool: stat |
| `--rollback` | 65 | FAILED_PRECONDITION missing tool: stat |

These are real command executions, not successful apply/verify/rollback transactions.
The missing-tool guard fires before identity, snapshot creation or queue setters.
Auto mode is supported by the source; no backend was actually selected in these
rejected invocations. Kernel-default fq_codel is not an active-root-qdisc proof.

## Remaining native blockers

- `stat` is unavailable in the target's native command path.
- `ubus call system board` has no `board_revision`; the kit requires a real revision.
- Native AQL has an `AC AQL limit low AQL limit high` header and BC/MC row; the
  current parser accepts only its narrower four-AC grammar/header.
- No independent45s restoration proof exists for this kit/target. The separate
  failed Stage907A PowerBeam probe is not evidence of successful WA recovery.

No revision, getter or identity fingerprint was fabricated. Before/after boot,
AQL, pktlog, BQL, tx_queue_len, relevant sysctls and default-qdisc snapshots match
exactly. No identity, transaction state or lock was created; profile writes were0.
The .20 runtime-write lease is **RELEASED**.

## Reproducible evidence

[Producer](../tools/autoresearch/run_stage929a_live_wa_field_kit_transaction.py),
[receipt](../artifacts/autoresearch/stage929a_live_wa_field_kit_transaction.json),
[argv/exit log](../artifacts/verification/stage929a/execution.json).
Producer exit2 denotes physical preconditions incomplete. The exact copied source,
executed producer revision, actual command outputs and final native readbacks are
hash-bound. Current parser metadata was replayed from unchanged captures without
repeating hardware commands. Pure admission/hash/path checks are local evidence only.

Next: provide compatible native identity/getters and independently verified recovery
before publishing a trusted contract. Fixing the missing tool alone does not qualify
the native AQL parser, hardware revision or configuration acceptance.
