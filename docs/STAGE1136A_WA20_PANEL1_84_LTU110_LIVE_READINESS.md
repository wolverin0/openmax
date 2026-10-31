<!-- doc-head: Stage1136A pure replay of WA20, Panel1 and LTU fresh read-only receipts with fail-closed live readiness -->
<!-- /doc-head -->

# Stage1136A fresh read-only readiness

The verifier reads only the exact Stage1133A, 1134A and 1135A JSON receipts and their bound local evidence. It never opens an SSH connection or executes a radio command.

`local_integrity_passed` means the recorded receipts can be independently replayed. An honest authentication denial may satisfy that structural condition. It does not count as a completed live observation.

`live_receipts_verified` requires both actual V17 dry-runs to complete with source/upload hashes, complete native before/after readbacks, unchanged configuration/identity and closed transports. It also requires two complete, comparable fresh LTU passive snapshots from the supplied-account acquisition.

Missing files, denied access, incomplete native getters, state or identity changes, wrong endpoints, unsupported execution modes, configuration writes, proprietary node access and evidence/source drift all block that live verification.

The `.20` and `.84` dry-runs are not apply, verify or rollback executions. The single authorized `/tmp` kit upload is distinguished from configuration or persistent writes. Panel1 station output remains scoped to the specifically requested interface.

LTU sparse data cannot establish production alarm thresholds, false-positive rates, application goodput or absence of firmware bugs. Those claims remain false/null even if passive collection succeeds.

`physical_ready`, `production_thresholds_validated` and deployment authority remain false. The current `.110` authentication rejection prevents a successful three-target live readiness result.

Run the pure verifier:

```powershell
python tools/verify/verify_wa20_panel1_84_ltu110_live_readiness.py
```

Exit 2 preserves incomplete live readiness. The exported result separates structural replay checks from the outstanding native observations.

[Receipt](../artifacts/verification/stage1136a_wa20_panel1_84_ltu110_live_readiness.json) · [Verifier](../tools/verify/verify_wa20_panel1_84_ltu110_live_readiness.py)
