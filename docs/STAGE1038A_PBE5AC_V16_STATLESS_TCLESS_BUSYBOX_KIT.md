<!-- doc-head: Stage 1038A PBE5AC Gen2 PtP v16 statless/tcless BusyBox field kit (.241 <-> .242): modes, flags, AQL/qdisc design, watchdog auto-rollback; offline-authored, no device touched. -->
<!-- /doc-head -->
# Stage 1038A - PBE5AC v16 statless/tcless BusyBox kit

- Kit: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh`
- Builder: `tools/verify/build_stage1038a_pbe5ac_v16_kit_receipt.py`
- Receipt: `artifacts/autoresearch/stage1038a_pbe5ac_v16_statless_tcless_busybox_kit.json`
- Auditor: `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py` (zero findings required)
- Evidence class: `STATLESS_TCLESS_FIELD_KIT`; status `CONFIRMED`; `live_devices_touched = false`.

## Scope

PtP PowerBeam 5AC Gen2 link `.241` <-> `.242`, OpenWrt 24.10.4, 8 MB BusyBox.
Authored and tested 100% offline against a fake `--root` tree. No SSH, no device, no bake.
Existing kits and `SHA256SUMS` under `firmware/openwrt/pbe5ac_gen2_ptp_kit/` are untouched; this is a new file only.

## Design (same core as the WA v16 contract)

- POSIX `sh` with `set -eu`; runs under ash and Git Bash sh; no bashisms; LF newlines only.
- Zero `|| true` / `|| :`; every failure is handled or fatal.
- Statless: `umask 077`, `mkdir -m 700`, `[ -f ] && [ ! -L ]` trust checks, `md5sum` manifest.
- Tcless: no `uci`, `iw` or qdisc tool. Default qdisc via `$ROOT/etc/sysctl.d/99-fmx-pbe5ac-v16.conf`
  plus a live write to `$ROOT/proc/sys/net/core/default_qdisc`.
- AQL via debugfs echo to `$ROOT/sys/kernel/debug/ieee80211/$PHY/aql_txq_limit`, one write per AC index `0 1 2 3`.
- Persistence: `$ROOT/etc/hotplug.d/ieee80211/99-fmx-pbe5ac-v16` rewrites AQL when a phy is added (phy renumbers after module reload).
- Every path carries the `--root` prefix; `--root ""` (default) means the real device.
- `FMX_WRITE_TRACE`: when set to a file, each knob write appends `path<TAB>value`.

## AQL values

Target per AC (idx 0..3): low `1500`, high `2000` (PtP champion lineage, Stage 699A ledger `AQL 1500/2000`).
Real readback format, from `artifacts/autoresearch/stage955a_live_panel1_three_cpe_readonly_audit.json` raw `aql_txq_limit`:

```
AC<TAB>AQL limit low<TAB>AQL limit high
VO<TAB>300<TAB><TAB>600
VI<TAB>1000<TAB><TAB>2000
BE<TAB>1500<TAB><TAB>3000
BK<TAB>500<TAB><TAB>1000
BC/MC<TAB>50000
```

The `BC/MC` row is read back and compared to `50000` by `--verify`; it is never written.
AC index map: `VO=0`, `VI=1`, `BE=2`, `BK=3`.

## Flags

| Flag | Meaning |
| :--- | :--- |
| `--dry-run` | Default. Preflight (read-only) and print the plan; writes nothing. |
| `--apply` | Snapshot, write, then watchdog; auto-rollback if the link does not come up. |
| `--verify` | Read back AQL rows, `BC/MC`, qdisc, persist files and link; exit non-zero on any mismatch. |
| `--rollback` | Restore the snapshot (md5-checked), then delete it. |
| `--root DIR` | Prefix for every path. |
| `--iface IF` | Default `phy2-sta0`. |
| `--phy PHY` | Default `phy2` (configurable; phy renumbers after reload). |
| `--dfs` | 120 s watchdog window instead of 45 s. |
| `--watchdog-seconds N` | Override the window (positive integer, max 9999); e.g. `2` for the offline harness. |

Exit codes: `0` ok, `1` failure (including watchdog expiry after a clean auto-rollback), `2` rollback itself failed (snapshot kept), `64` usage.

## Link state and watchdog

No `iw`: link is up when `$ROOT/sys/class/net/$IFACE/operstate` reads `up` and `$ROOT/sys/class/net/$IFACE/carrier` reads `1`.
The loop uses no `seq`, `timeout` or `usleep`:

```
i=0; while [ "$i" -lt "$WD" ]; do <link up? break>; sleep 1; i=$((i+1)); done
```

If the window expires, the kit restores the snapshot and exits non-zero.
`--apply` does not read AQL back (a plain `--root` file cannot emulate debugfs); run `--verify` after it.

## Snapshot

`$ROOT/etc/fmx-pbe5ac-v16.snapshot` (mode 700) holds `aql`, `qdisc`, `phy`, prior sysctl.d and hotplug files, and an `md5sum` manifest.
A second `--apply` is refused until `--rollback` removes it. Rollback uses the phy saved in the snapshot.

## Offline test outcomes (fake root, `--watchdog-seconds 2`)

- `operstate=up`: `--dry-run` rc 0 (no writes); `--apply` rc 0; `--verify` rc 0 (9 PASS lines); `--rollback` rc 0, original AQL rows and `pfifo_fast` restored.
- `operstate=down`: `--apply` waits 2 s, auto-rolls back (original AQL rows and qdisc restored, persist files removed), exit rc 1.
- Auditor: `audit_text` on the kit returns `findings: []`.

## Not covered

No device run, no real debugfs semantics, no ash on a real radio; BusyBox `md5sum -c` is assumed present (default applet set).
