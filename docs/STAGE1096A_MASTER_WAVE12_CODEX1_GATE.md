<!-- doc-head: Wave12 fail-closed master gate validates current pytest, V17 kit hashes and scoped documentation evidence offline -->
Local verification never grants physical acceptance or deployment authority.
<!-- /doc-head -->

# Stage1096A master Wave12 gate

This gate consumes the exact Stage1091A..1095A receipts. It never runs a kit or contacts a radio. A missing, failed, empty, skipped, malformed, changed or unbound mandatory result prevents closure.

| Required check | Evidence |
|---|---|
| Master pytest matrix | All nine requested suites, actual process exit, logs and JUnit counts, current source bindings |
| V17 kit identity | The three exact current kit files match independent saved expected SHA256 declarations |
| Scoped checksum manifest | Observed snapshot manifest has exactly the three current hashes; it is not a signed or published release |
| v15/v16/v17 comparison | Static kit source identity and deterministic matrix replay; runtime guarantees stay separate |
| Documentation | Stage1001A..1078A scoped local links, fragments, strict fewer-than-220-line budget and initial doc-head policy |
| Reconciliation | Exact current Stage1001A..1094A catalog, no malformed/conflicting entries or missing required new receipt |
| This gate's tests | Fresh Stage1091A..1096A pytest invocation, actual exit, log, JUnit and current source/doc/test hashes |

Legacy broad `SHA256SUMS` files may omit V17. The gate does not silently rewrite them or claim signatures, publication or broad release coverage. Missing or mismatched independent expected kit hashes fail the V17 identity check.

HTTP links are not fetched in this offline wave. Zero broken links means the audited local links and fragments, not independently verified external web availability.

```powershell
python tools/verify/verify_stage1096a_master_wave12_codex1_gate.py --validation artifacts/verification/wave12_final/local_validation.json
```

The [gate receipt](../artifacts/autoresearch/stage1096a_master_wave12_codex1_gate.json) separates offline completion from physical acceptance. Its default without fresh bound test evidence remains incomplete. Earlier failures and source drift are retained rather than repinned away.

The [reconciliation](STAGE1095A_POST_AUDIT_MASTER_RECONCILIATION_1001A_1094A.md) catalogs historical statuses without promoting them. Saved ICMP, static rollback code, PHY rates or interface counters do not substitute for measured disjoint A/A/discovery/holdout cohorts, UDP application QoE or an autonomous rollback rehearsal.
