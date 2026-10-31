<!-- doc-head: Stage 1037A wa-v16 kit: stat-less, tc-less BusyBox field kit (default_qdisc + AQL via debugfs, snapshot/verify/rollback); offline-authored, no live device touched. -->
<!-- /doc-head -->
# Stage 1037A: wa-v16 stat-less / tc-less BusyBox kit

Status: CONFIRMED (offline). Live devices touched: none. Evidence class: `STATLESS_TCLESS_FIELD_KIT`.

## Files

- Kit: `firmware/openwrt/common/fmx_wa_v16_statless_tcless_busybox_kit.sh`
- Receipt builder: `tools/verify/build_stage1037a_wa_v16_kit_receipt.py`
- Receipt: `artifacts/autoresearch/stage1037a_wa_v16_statless_tcless_busybox_kit.json`
- Auditor the kit must pass with zero findings: `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py`
- Predecessor (read-only reference, untouched): `firmware/openwrt/common/fmx_wa_v15_368window_field_kit.sh`

## Target

OpenWrt 24.10.4 on 8 MB BusyBox radios (.20 / .241). POSIX sh, `set -eu`, LF only. Runs under BusyBox
ash and Git Bash sh. No bashisms. No `|| true` / `|| :` anywhere: every command failure propagates.

## Modes and options

- `--dry-run` (default): prints the plan, writes nothing.
- `--apply`: preflight, snapshot the pre-apply state, write AQL, `default_qdisc`, persistence files, then run the verify.
- `--verify`: readback compare; exit non-zero on any mismatch.
- `--rollback`: restore from the snapshot, confirm by readback, then remove the snapshot.
- `--root DIR`: prefix for every system path (default empty, meaning `/`). The offline-test linchpin.
- `--phy NAME`: default `phy0`. The phy index renumbers after module reload.
- Env `FMX_WRITE_TRACE=FILE`: every write appends `path<TAB>value`.

## Real AQL format (cited)

Source: `artifacts/autoresearch/stage955a_live_panel1_three_cpe_readonly_audit.json`, the `raw` field of the
`aql_txq_limit` readback (about line 62). Header row, then four AC rows with a double tab, then a single-value row:

```
AC	AQL limit low	AQL limit high
VO	300		600
VI	1000		2000
BE	1500		3000
BK	500		1000
BC/MC	50000
```

`BC/MC` is a single value, constant 50000 across all three captured states. It is readback-verify only:
the kernel rejects ac index >= 4, so the kit never writes it.

Champion target: VO 300/600, VI 1000/2000, BE 1500/3000, BK 500/1000.

## What it writes

- `$ROOT/sys/kernel/debug/ieee80211/$PHY/aql_txq_limit`: per-AC `echo "<idx> <low> <high>"`, idx VO=0 VI=1 BE=2 BK=3.
- `$ROOT/proc/sys/net/core/default_qdisc`: `fq_codel`, via `cat`/`echo` (not the sysctl applet).
- `$ROOT/etc/sysctl.d/99-fmx-v16.conf`: `net.core.default_qdisc=fq_codel`, persistence for the next boot.
- `$ROOT/etc/hotplug.d/ieee80211/99-fmx-v16-aql`: re-applies the four AQL writes when a phy appears (uses `$DEVICENAME`).
- `$ROOT/etc/fmx-v16-snapshot/{aql,qdisc,fp}`: pre-apply readback table, pre-apply qdisc, md5 fingerprint.

It never calls UCI, ifup or iw, and never touches firmware or services.

## The tc-less limit

Without the traffic-control applet the kit cannot set fq_codel `quantum`, `target` or `interval`, and cannot
replace a qdisc on an existing netdev. v16 therefore sets `default_qdisc=fq_codel`, which only affects
netdevs created AFTER the write (new interfaces after a reload or reboot). Interfaces that already exist keep
their current qdisc until they are recreated. AQL is applied live through debugfs and persisted through the
hotplug script. Anything that needs fq_codel parameters stays out of scope for this kit.

## The stat-less replacement

v15 used `stat -c '%u:%a:%h'` to demand a root-owned mode-700 snapshot dir and mode-600, single-link files.
v16 replaces those checks with:

- `umask 077` plus `mkdir -m 700` when the dir is created (mode is set at creation, not re-read).
- `[ -f "$f" ] && [ ! -L "$f" ]` for each snapshot file (regular, not a symlink).
- An `md5sum` content fingerprint (`fp`, written last, so it doubles as a completeness marker), recomputed
  before reuse and before rollback. A truncated or edited snapshot fails the check.
- `id -u` = 0 on a real device (skipped when `--root` is set).

Residual risk: owner, mode and hardlink count are not re-read after creation. A same-uid attacker who rewrites
`aql` and `fp` consistently is not detected; the threat model here is accident and corruption, not a hostile root.

## Verify

`--verify` reads the AQL file with `cat` and parses with `awk '$1=="VO"{...}'` (awk default field splitting
collapses the double tab). It asserts VO/VI/BE/BK equal the target, `grep -q '^BC/MC'` confirms the format,
`default_qdisc` reads back `fq_codel`, and both persistence files exist. Any mismatch exits non-zero.

## Rollback

The snapshot is a `cat` of the pre-apply readback table. Rollback parses its rows and re-emits idx/low/high
writes, restores the old `default_qdisc`, removes the two persistence files, confirms by readback, then removes
the snapshot. On a readback mismatch it keeps the snapshot and exits non-zero. A second `--apply` with an
existing valid snapshot reuses it, so the original pre-apply state is never overwritten.

## Offline emulation caveat

With a non-empty `--root` the AQL file is a regular file, which cannot interpret a debugfs command. The kit
then rewrites the matching row in place so `--verify` is meaningful. With the default empty root it performs
the real `echo "<idx> <low> <high>"`. The write-trace line is identical in both cases.

## Offline test recipe

1. Build a fake root with a stock-style AQL table (5000/12000 rows plus `BC/MC`) and a `default_qdisc` file.
2. `--dry-run`: no trace file, no `etc` dir created.
3. `--apply`, then `--verify` (exit 0), then `--rollback` (table restored, snapshot and persistence files gone).
4. `--verify` after rollback exits 1.
5. Assert the trace shows only idx 0..3 writes (never idx 4 or BC/MC).

## Not covered

- No real BusyBox or on-device run. Only Git Bash sh and `sh -n` were exercised.
- Whether the hardware accepts these AQL values under load is a live-bench question, not answered here.
- Existing kits (v13/v14/v15/ltu_v21) and every `SHA256SUMS` file are unchanged.
