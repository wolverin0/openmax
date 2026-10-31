<!-- doc-head: Wave12 exact saved-receipt reconciliation distinguishes catalog integrity from native and physical acceptance -->
All collection in this wave reads repository files only; no radio or network action occurs.
<!-- /doc-head -->

# Stage1095A post-audit master reconciliation

The catalog covers JSON receipt filenames for Stage1001A through Stage1094A, including saved Stage1079A..1090A entries when present. Every matching receipt remains separate. Duplicate stage numbers can represent distinct receipts and are not merged into independent benchmark windows.

The builder records each file's SHA256, size, mtime, declared stage, status, claimed evidence layer and physical-acceptance field. It reads bytes twice and checks the file mtime to detect changes during acquisition. A declared stage conflicting with its filename, duplicate JSON keys, nonfinite JSON constants, malformed JSON or a non-object receipt is a catalog error.

Missing historical IDs are `UNKNOWN`, not inferred successes or proof that work was never performed. The four new Stage1091A..1094A receipts are required inputs; their absence keeps this reconciliation incomplete.

| Layer | What the catalog establishes | What remains unproved |
|---|---|---|
| Repository bytes | Exact observed file identity and read stability | Publisher signatures, immutable storage or earlier contents |
| Saved native claims | The source receipt says it contains native/live evidence | Fresh collection, current radio health or route isolation |
| Saved offline results | The source status and evidence label are retained | Current tests or correctness of every historical dependency |
| New Wave12 checks | Inputs to the independent Stage1096A gate | Deployment permission or new physical RF acceptance |

Historical failure and incomplete statuses are preserved. Cataloging a `CONFIRMED` field never upgrades it to independent acceptance. Hardware fields omitted by an older receipt remain null; they are not silently replaced by false or zero.

Run the offline builder:

```powershell
python tools/verify/build_stage1095a_post_audit_master_reconciliation_1001a_1094a.py
```

The [receipt](../artifacts/autoresearch/stage1095a_post_audit_master_reconciliation_1001a_1094a.json) binds the exact catalog inputs. The [master gate](STAGE1096A_MASTER_WAVE12_CODEX1_GATE.md) separately verifies the nine-suite pytest evidence, V17 hashes, comparison matrix and documentation audit. No SSH, RF traffic, kit application, service restart, flash or device write is performed.
