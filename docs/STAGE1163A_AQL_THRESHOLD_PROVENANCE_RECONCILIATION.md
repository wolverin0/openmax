<!-- doc-head: STAGE1163A_AQL_THRESHOLD_PROVENANCE_RECONCILIATION.md authority decision record for aql_threshold provenance over-citation and value divergence -->
# Stage 1163A AQL Threshold Provenance Reconciliation

Status: DECISION RECORD (Wave #28, coordinator/futuramax-agy). Docs only. `live_devices_touched=false`.

## Finding
- The mac80211.ko reverse engineering (opencode Stages 1104A and 1105A) shows the `aql_threshold` write grammar is UNKNOWN.
- Both v17 kits, `fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh` and `fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`, carry a line-4 header that OVER-CITES Stage 1031A.
- Stage 1031A lists only the `aql_threshold` debugfs file name. It never states the write grammar.
- The value diverges: `12000` in the kits versus `24000` in champion v17. The divergence is UNRESOLVED and is NOT resolvable by the RE.

## Decision
- Reconcile in docs ONLY.
- DO NOT edit the v17 kit `.sh` files or any `SHA256SUMS`. Codex #2 owns them during live RF execution.
- This document is the durable record. Stage 1209A made zero edits to the kits or to `SHA256SUMS`.

## Recommended header wording (NOT applied)
For Codex #2 to apply later, after live RF execution ends, together with regenerating the affected `SHA256SUMS`:

> aql_threshold: debugfs file name only is listed in Stage 1031A; the write grammar is UNKNOWN (mac80211.ko RE, Stages 1104A/1105A). The value 12000 is an untested candidate; champion v17 uses 24000. Divergence unresolved. Verify on a bench unit before any fleet use.

## Open items
- Determine the real write grammar and a valid value on a bench unit, then pick 12000, 24000 or another value on evidence.
- Until then, treat any `aql_threshold` write by the kits as unverified.

## Related
- `docs/STAGE1209A_COMMUNITY_SYMPTOM_AND_KO_ROOT_CAUSE_PWO_MATCHER.md`
