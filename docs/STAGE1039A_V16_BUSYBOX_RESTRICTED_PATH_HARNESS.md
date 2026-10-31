<!-- doc-head: Stage 1039A adversarial restricted-PATH harness for the v16 stat-less/tc-less BusyBox kits (offline) -->
<!-- /doc-head -->
# Stage 1039A: v16 BusyBox restricted-PATH harness

Offline only. No device is touched (`live_devices_touched=false`).

## What it proves
The v16 kits never call `stat tc timeout seq usleep iperf3 python python3`. Poison stubs for those
names are prepended to PATH; each appends to `$FMX_POISON_MARKER` and exits 127. A trap self-check
runs `sh -c 'stat x'` first (must exit 127 and write the marker), else the run is skipped.

## Kits under test
- `firmware/openwrt/common/fmx_wa_v16_statless_tcless_busybox_kit.sh`
- `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh`

## Harness
`tests/test_stage1039a_v16_busybox_restricted_path_harness.py` builds a fake `--root` per test
(`proc/sys/net/core/default_qdisc`, `sys/kernel/debug/ieee80211/phy0/aql_txq_limit`, `etc/`, and
`sys/class/net/wlan0/{operstate,carrier}` for PBE) with a STOCK table (5000/12000 + `BC/MC 50000`).
The CHAMPION state is pre-rendered from the kit's own traced AQL writes plus its persistence files.

## Cases
1. `--dry-run`: exit 0, empty `FMX_WRITE_TRACE`, tree unchanged.
2. `--apply`: snapshot, idx/low/high writes VO=0 VI=1 BE=2 BK=3, `etc/sysctl.d/` persistence.
3. `--verify`: champion exit 0, stock exit non-zero.
4. `--rollback`: stock restored; later `--verify` non-zero.
5. Faults: snapshot removed then `--rollback` non-zero; read-only AQL (file and dir) then `--apply` non-zero.
6. PBE: `operstate=down` with `--watchdog-seconds 2` expires, auto-rolls back, exit non-zero.
7. Poison marker empty after every successful run.

## Findings about the kits (not defects of the harness)
- The WA kit emulates AQL row writes under `--root`; the PBE kit does not, so its plain fake file is
  overwritten by the last `put`. PBE restore is therefore asserted from the rollback write trace.
- A read-only file alone does not fault the WA offline emulation (it replaces the file via `mv`); the
  test makes the parent dir read-only too.
- On Windows/Git Bash chmod is not enforced, so the read-only case is SKIPPED there (host skip, recorded).

## Run
`python -m pytest tests/test_stage1039a_v16_busybox_restricted_path_harness.py -q` then
`python tools/verify/build_stage1039a_to_1041a_v16_adversarial_receipts.py`.
Receipt: `artifacts/autoresearch/stage1039a_v16_busybox_restricted_path_harness.json`.
If a kit is absent the receipt status is `DEFERRED`; re-run the builder once both kits exist.
