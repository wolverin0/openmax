<!-- doc-head: Stage1092A reconciles exact V17 kit hashes with saved producer declarations and a scoped observed manifest -->
Distribution manifests and publisher signatures are not generated or changed.
<!-- /doc-head -->

# Stage1092A V17 hashes and manifest

The verifier reads exactly three current shell files: the PowerBeam V17 Pareto kit, WA V17 Pareto kit and `99-fmx-wa-universal-champion-v17`. It records file size and SHA256 and rejects missing, empty, all-NUL, CRLF or aliased kit paths.

Expected hashes come from saved Stage1049A, Stage1050A, Stage1075A and Stage1076A producer receipts. Both the declared path and digest must match. These historical declarations are not regenerated to make a mismatch disappear.

Existing `firmware/openwrt/common/SHA256SUMS` and PowerBeam-kit `SHA256SUMS` are parsed without modification. Missing V17 entries remain explicitly uncovered; a stale matching entry is a failure. Duplicate or unsafe manifest paths and malformed SHA256 records are rejected.

The command writes a separate, scoped `v17_SHA256SUMS.observed.txt` under `artifacts/verification/wave12_stage1091_1092/`. Its complete three-entry content is derived from current kit bytes and checked again during receipt replay. This is an observed integrity snapshot, not a signed distribution manifest or independent known-good firmware attestation.

```powershell
python tools/verify/verify_stage1092a_v17_kits_sha256_and_manifest.py
```

The result is `artifacts/autoresearch/stage1092a_v17_kits_sha256_and_manifest.json`. `hashes_verified` can be true while `existing_distribution_manifest_coverage` remains false. `release_ready` remains false and publisher authentication remains `NOT_ESTABLISHED`.

`build()` only reads local files. `replay_receipt()` recomputes hashes, exact prior-declaration checks and observed-manifest bytes rather than trusting stored pass flags. No kit, actuator, SSH, network, signing or radio operation is executed.

Five-pillar scope is limited to saved evidence and deterministic local verification; no new binary reverse engineering, literature retrieval, RF experiment, optimizer or durable-memory write is claimed.
