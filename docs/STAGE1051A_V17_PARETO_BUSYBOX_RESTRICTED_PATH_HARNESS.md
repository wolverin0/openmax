<!-- doc-head: Stage 1051A adversarial restricted-PATH harness for the v17 Pareto AQM/AQL BusyBox kits (offline) -->
<!-- /doc-head -->
# Stage 1051A: v17 Pareto BusyBox restricted-PATH harness

Offline only. No device is touched (`live_devices_touched=false`).

## What it proves
The v17 kits never call `stat tc timeout seq usleep iperf3 python python3`. Poison stubs for those
names are prepended to PATH; each appends to `$FMX_POISON_MARKER` and exits 127. A trap self-check
runs `sh -c 'stat x'` first (must exit 127 and write the marker), else the run is skipped.

## Shell discovery
`C:\Program Files\Git\bin\sh.exe`, then Git `usr/bin/sh.exe`, `sh`, `bash`; the first that honors the poison stubs wins (Git's `bin\sh.exe` re-prepends `/usr/bin`, defeating the trap, so `usr/bin/sh.exe` is used here). Never `C:\Windows\System32\bash.exe`
(WSL launcher: cannot see Windows paths, hangs). No suitable shell means `pytest.skip`. The resolved
shell is recorded as `shell_used` in the receipt.

## Kits under test
- `firmware/openwrt/common/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh`
- `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`

## Fake root (STOCK fixtures)
`tests/test_stage1051a_v17_pareto_busybox_restricted_path_harness.py` builds, per test, `aql_txq_limit`
(5000/12000 x4 + BC/MC 50000), `aqm` (fq_memory_limit 3145728, fq_limit 512, fq_quantum 300,
read-only fq_flows_cnt), `aql_threshold` 5000, `tcp_notsent_lowat` 4294967295, `default_qdisc`
pfifo_fast, `etc/`, and for PtP `sys/class/net/wlan0/{operstate,carrier}`.

## Cases (per kit)
1. `--dry-run`: exit 0, nothing written, tree unchanged.
2. `--apply`: exactly 4 AQL idx writes, 3 aqm writes, 3 scalar writes (10 rows), snapshot created.
3. Conditional guard: `aqm` removed gives 7 rows; `tcp_notsent_lowat` removed gives 9; exit 0, no file created.
4. `--verify`: champion table exit 0, stock table non-zero.
5. `--rollback`: trace re-emits STOCK AQL, aqm and scalar values; later `--verify` non-zero.
6. Faults: snapshot removed then `--rollback` non-zero; read-only AQL then `--apply` non-zero.
7. PtP: `operstate=down` with `--watchdog-seconds 2` expires, auto-rolls back, exit non-zero.
8. Poison marker empty after every successful run.

## Notes
- chmod is not enforced on Windows, so the read-only case is a recorded host skip there.
- Rollback restore is asserted from the write trace, since the PtP kit overwrites plain fake files.
- Trace file paths are matched by basename (`aql_txq_limit`, `aqm`, `aql_threshold`, `tcp_notsent_lowat`, `default_qdisc`).

## Run
`python -m pytest tests/test_stage1051a_v17_pareto_busybox_restricted_path_harness.py -q` then
`python tools/verify/build_stage1051a_1052a_v17_harness_receipts.py`.
Receipt: `artifacts/autoresearch/stage1051a_v17_pareto_restricted_path_harness.json`.
Absent kits give status DEFERRED; re-run the builder once both kits exist.
