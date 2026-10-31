<!-- doc-head: Stage1134A jump timeout yielded no authenticated route; target84 never connected and no remote writes occurred -->
The attempt records the missing access layer without substituting historical Panel1 telemetry.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1134A — Panel1 V17 dry-run through the approved jump

The authorized route was `198.18.0.77` account `root`, forwarding only to `198.18.0.7:22` account `root`. The one fresh jump connection attempt returned `TimeoutError`; no successful authentication was recorded. The exception alone does not establish which connection/authentication subphase timed out. No direct-target fallback was attempted.

| Criterion | Actual result |
|---|---|
| Jump authentication | NOT_ESTABLISHED; connection timeout |
| Connection to `.84` | NOT_ATTEMPTED because the jump was unavailable |
| Commands on jump / Panel1 | Zero / zero |
| `/tmp` upload / remote dry-run | NOT_EXECUTED / NOT_EXECUTED |
| `iw dev phy0-ap0 station dump` | NOT_EXECUTED; no station count inferred |
| Fresh native identity and queue readbacks | UNKNOWN / NOT_COLLECTED |
| Configuration, persistent, firmware or RF changes | None |
| SSH clients and forwarding handles | Closed; forwarding channel was never created |

The same source-reviewed kit as Stage1133A is pinned by SHA256. Only `--dry-run` is permitted by the acquisition path. A `/tmp` upload is the sole authorized ephemeral-file exception; the code refuses symlinks, non-regular targets and different existing bytes, and verifies any new upload by readback. No upload was reached during this attempt.

If access were available, before/after captures would include boot/interface identity, AQM RW configuration, AQL including BC/MC, `aql_threshold`, `tcp_notsent_lowat`, default qdisc and snapshot presence. The passive station command has the exact `phy0-ap0` scope; an empty dump would not prove all AP-VLAN stations absent.

The [receipt](../artifacts/verification/stage1134a_live_panel1_84_v17_dryrun_receipt.json) binds the [actual jump-attempt record](../artifacts/verification/1134a/acquisition.json). Its pure replay rejects false success and wrong endpoints. Historical Stage1022 identity, queue settings and client associations are not presented as fresh results.

The [collector lineage](../artifacts/verification/stage1133a/acquisition_source_lineage.json) preserves the exact executed source before analysis-only corrections; raw acquisitions are unchanged. Here `network_attempted` is true for the jump, but `target_contact_attempted`, `authenticated_target_access` and `hardware_access` are false for `.84`. Commands or uploads cannot be accepted without a fully authenticated approved route.

The outcome is `BLOCKED_OR_INCOMPLETE_NATIVE_DRYRUN`, with physical acceptance `NOT_ACCEPTED`. No alternative jump, account or credential was tried. No protected endpoint, core, PoE switch, PowerBeam bench or proprietary device node was accessed.
