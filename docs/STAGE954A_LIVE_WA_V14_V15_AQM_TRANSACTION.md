<!-- doc-head: Stage954A actual WA v14/v15 entrypoints, exact RAM copies and unchanged native AQM; apply blocked -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage954A — WA v14/v15 native transaction checks

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE**.
Status **BLOCKED_NATIVE_APPLY_PRECONDITIONS**, acceptance **NOT_ACCEPTED**.
Attribution: external SSH controller; Linux/mac80211 native readbacks.

## Actual execution on 198.18.0.43

Exact canonical scripts were copied to private RAM paths and checked by native
SHA256. Optional backups preserve any preexisting regular copy; symlinks are rejected.

| Profile | RAM path | Actual SHA256 |
| --- | --- | --- |
| wa-v14 | `/tmp/fmx_wa_v14.sh` | `be945751ae03796401d61ed1404c2909a5f60bd4eb04d581a8e082b0da77ab63` |
| wa-v15 | `/tmp/fmx_wa_v15.sh` | `16a926bbce576bae0bc8a1621fb12bbdbfebef134e3a008dfc80dcb77d82a9d7` |

Each exact native entrypoint used `--qdisc-mode auto`:

| Profile | --dry-run | --apply | --verify | --rollback |
| --- | ---: | ---: | ---: | ---: |
| wa-v14 | 0 | 65 | 65 | 65 |
| wa-v15 | 0 | 65 | 65 | 65 |

All six mutation/verification entrypoints returned
`FAILED_PRECONDITION missing tool: stat`. Both dry-runs reported PLANNED with
runtime UNKNOWN. These are actual invocations, not successful configuration apply,
verification or rollback. The controller exits2 for physical acceptance blocked.

## Native admission and readbacks

The fresh ubus identity lacks board_revision. The native AQL getter has an
`AC AQL limit low AQL limit high` header plus BC/MC, incompatible with these kits'
four-row strict grammar. No revision, getter, identity capability or snapshot was
fabricated. Independently qualified45s recovery for either profile is absent.
No trusted identity/state was published; final absence checks succeeded.

Native `phy0/aqm` settings before/after each profile remained:

| Internal setting | Before | After v14 | After v15 |
| --- | ---: | ---: | ---: |
| fq_quantum | 3028 | 3028 | 3028 |
| fq_limit | 512 | 512 | 512 |
| fq_memory_limit | 3145728 | 3145728 | 3145728 |

Read-only fq_flows_cnt4096 and fq_collisions79 were also unchanged in these captures.
All saved AQL, pktlog, BQL, tx_queue_len, sysctl, boot and identity readbacks match.
Natural counters are compared separately from RW settings to avoid conflating traffic
with configuration drift. AQL is per AC, not per TID. mac80211 iTXQ AQM is distinct
from the active interface-root qdisc; kernel default fq_codel is not root-profile proof.

## Evidence and limits

[Producer](../tools/autoresearch/run_stage954a_live_wa_v14_v15_aqm_transaction.py),
[receipt](../artifacts/autoresearch/stage954a_live_wa_v14_v15_aqm_transaction.json),
[raw evidence and exact sources](../artifacts/verification/stage954a/).
Before/after native observations, copy hashes and all eight results are retained.
Only the two requested RAM script copies and optional backups were written.
No queue/sysctl/RF/service/firmware configuration was changed. No performance gain
or successful profile application is claimed. `.20` lease is **RELEASED**.
