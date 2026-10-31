<!-- doc-head: Stage1076A static 1025A audit and restricted-PATH harness for the fail-closed champion v17 hotplug -->
Proves `firmware/openwrt/common/99-fmx-wa-universal-champion-v17` is BusyBox-clean, free of `|| true`, and boot-safe.
<!-- /doc-head -->

# Stage1076A - Champion v17 audit and restricted-PATH test

## Static audit

`audit_text` from `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py` returns 0 findings (no stat, tc, timeout, seq, usleep, iperf3, python, fractional ping). `|| true` / `|| :` count is 0, no CR bytes, `set -u` present and no `set -e` (a hotplug that aborts halfway leaves the radio half-configured).

## Restricted-PATH test

`tests/test_stage1076a_champion_v17_restricted_path.py` reuses the Stage 1051A shell discovery (Git `sh.exe` first, the shell whose poison trap actually fires, skip if none) and its poison stubs (stat, tc, timeout, seq, usleep, iperf3, python, python3).

Against a fake `FMX_ROOT` tree it asserts, via `FMX_WRITE_TRACE`:

- four `aql_txq_limit` writes `0 500 1000`, `1 1500 3000`, `2 3000 6000`, `3 1500 3000`
- three `aqm` writes `fq_limit 2048`, `fq_memory_limit 4194304`, `fq_quantum 1514`
- one `default_qdisc` write `fq_codel`, and `aql_threshold` stays `24000` (the v17 kit writes `12000`; discrepancy recorded in Stage1075A)
- both `FMX_ROOT` and `--root DIR` are honoured
- with the debugfs tree absent: exit 0, nothing written, tree unchanged (boot-safety)
- the poison marker stays empty

Run: `python -m pytest tests/test_stage1076a_champion_v17_restricted_path.py -q`.

Receipt: `artifacts/autoresearch/stage1076a_champion_v17_audit_and_restricted_path.json` (builder `tools/verify/build_stage1075a_1076a_champion_v17_receipts.py`).
