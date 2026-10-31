<!-- doc-head: Stage 1124A BusyBox applet audit, restricted-PATH pytest and SHA256SUMS entry for the Stage 1123A health dump; offline, no live claim -->

# Stage 1124A - Health Dump Audit and Manifest

Receipt: `artifacts/autoresearch/stage1124a_health_dump_audit_and_manifest.json`
Test: `tests/test_stage1124a_health_dump_restricted_path.py`
Builder: `tools/verify/build_stage1123a_1124a_health_dump_receipts.py`

## Audit
- `audit_text` from `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py` returns 0 findings.
- `grep -c '|| true\||| :'` on the dump is 0; `sh -n` passes; 0 CR bytes.

## Restricted-PATH test
- Shell discovery follows Stage 1051A: Git `sh.exe` first, the shell whose poison trap fires, skip if none.
- Poison stubs for `stat`, `tc`, `timeout`, `seq`, `usleep` log to `FMX_POISON_MARKER`; the marker must stay empty.
- Full fake `--root` tree: every section is `status=ok`, exit 0, tree byte-identical before and after.
- Partial tree (optional files absent): sections report `status=absent`, exit 0, tree unchanged.
- Invalid `--peer` exits 65.

## Manifest
- `firmware/openwrt/pbe5ac_gen2_ptp_kit/SHA256SUMS`: one line appended for `fmx_ptp_v17_one_shot_health_dump.sh`.
- Format `<64 hex>  <name>`, two spaces, LF; 24 lines before, 25 after; every prior line byte-identical.
- The 19 `edf58be7` placeholder lines are untouched (not this stage's scope).
- `sha256sum -c --ignore-missing` on the new entry returns rc 0.
