<!-- doc-head: Stage 1109A global SHA256SUMS coverage of the v16/v17 kits in common and pbe5ac_gen2_ptp_kit manifests; offline, no live claim -->

# Stage 1109A - Global v16/v17 SHA256SUMS Coverage

Builder: `tools/verify/build_stage1109a_global_v16_v17_sha256sums_coverage.py`
Verifier: `tools/verify/verify_stage1109a_global_v16_v17_sha256sums_coverage.py`
Receipt: `artifacts/autoresearch/stage1109a_global_v16_v17_sha256sums_coverage.json`

## Scope (operator-authorized edit of exactly two manifests)
- `firmware/openwrt/common/SHA256SUMS`: v16 WA kit, v17 WA kit, `99-fmx-wa-universal-champion-v17`.
- `firmware/openwrt/pbe5ac_gen2_ptp_kit/SHA256SUMS`: v16 PBE kit, v17 PBE kit, `fmx_ptp_rollback_watchdog_v17.sh`.
- No script file was edited; only the two manifests and the receipt are written.

## Edit discipline
- Line format is `<64 hex>  <name>`: two spaces, name relative to the manifest directory, no leading `*`, LF only.
- Upsert: named entries are replaced or appended; every other line is preserved byte-for-byte, order kept, no re-sort.
- Hashes are computed from the files at write time, then the manifest is re-read and asserted.
- `common/SHA256SUMS` was untracked with only the v16 line; this is its first authored version.

## Verifier
- Asserts each of the 6 entries is present and equals the file's current sha256.
- Runs `sha256sum -c --ignore-missing` in each manifest directory, scoped to the 6 names; rc must be 0.
- Feeds the check over stdin as bytes, because text mode would send CRLF on Windows.

## Placeholder anomaly (reported, not modified)
- 19 lines in the pbe5ac manifest share the hash prefix `edf58be7`, a placeholder stamp.
- Re-stamping them is Codex #2's scope; the verifier prints a WARNING and does not fail.

## Evidence
- `evidence_class` is `SHA256SUMS_COVERAGE`; `live_devices_touched` is false.
- Claim id: `FMX-STAGE1109A-GLOBAL-V16-V17-SHA256SUMS-COVERAGE`.
