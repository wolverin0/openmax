<!-- doc-head: Stage 1163A analysis-only reconciliation of opencode Stages 1103A..1108A against the two v17 kits: Stage 1031A over-citation, UNKNOWN aql_threshold write path, unresolved 24000 vs 12000 value; nothing applied, patch recommended as text -->
# Stage 1163A - opencode 1103A..1108A vs v17 kits reconciliation

Verifier: `tools/verify/verify_stage1163a_opencode_1103a_1108a_v17_reconciliation.py`
Receipt: `artifacts/verification/stage1163a_opencode_1103a_1108a_v17_reconciliation.json`
Self-test: `tests/test_stage1163a_v17_reconciliation.py`

## 1. Ownership boundary

Analysis only. This stage edits neither v17 kit, no `SHA256SUMS`, and never changes `aql_threshold`.
The receipt proves it: `files_edited` is empty, `sha256sums_touched` and `aql_threshold_value_changed`
are false, and a before/after sha256 of both kits plus every `SHA256SUMS*` under `firmware/` is equal.

Kits: `firmware/openwrt/common/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh` and
`firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`.

## 2. Findings

| id | label | finding |
| :--- | :--- | :--- |
| F1 | CONFIRMED | both kits, line 4, cite Stage 1031A for `aql_threshold plain u32`; Stage 1031A binds no such write grammar (Stage 1105A C6) |
| F2 | UNKNOWN | the `aql_threshold` debugfs write grammar is proven nowhere in the corpus (Stage 1105A C5) |
| F3 | OPEN_DECISION | champion-v17 keeps 24000, both kits write 12000; the RE does not say which is right |

Primary-source correction: the Stage 1031A receipt does contain the string `aql_threshold` on four lines,
but only as a debugfs file-name literal in the field list. It has zero write grammar for it, so the
over-citation conclusion stands; only the literal wording "zero mentions" does not.

## 3. Recommended patch (not applied)

Header comment only, same text for both kits. Replace lines 4-5 with these four lines:

```
# write_syntax_source: Stage 1031A (aql_txq_limit "<ac-idx 0..3> <low> <high>",
#   aqm "fq_limit N" / "fq_memory_limit N" / "fq_quantum N"). Read-table format: Stage 955A.
# aql_threshold_write_syntax: UNKNOWN provenance (Stage 1105A C5/C6: Stage 1031A lists the file
#   name only, no write grammar). The 12000 value is unreconciled vs champion-v17 24000.
```

No runtime change, but kit bytes change, so `SHA256SUMS` needs a re-sign.
`apply_status` is `DEFERRED_PENDING_OWNER_AUTHORITY`; owner is codex2 (re-sign) with futuramax-agy as authority.

## 4. Open decision

`aql_threshold` 24000 (champion) versus 12000 (kit) is UNRESOLVED; the RE shows the write path UNKNOWN.
It belongs to the operator/orchestrator and is not settled here.

## 5. opencode suite state

`tests/test_stage1103a_to_1108a_suite.py` is another lane's. The brief expected 3 failed/41 passed; the
run recorded in the receipt is `45 passed`, so the 1105A/1106A/1108A contracts pass at this checkout.
Recorded as observed, not gated.
