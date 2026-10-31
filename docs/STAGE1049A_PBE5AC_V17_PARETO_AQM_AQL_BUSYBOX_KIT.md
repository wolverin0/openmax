<!-- doc-head: Stage 1049A PBE5AC Gen2 PtP v17 Pareto AQM+AQL tc-less BusyBox kit (.241 <-> .242): purpose, 5 target files, Stage 1031A write syntax, caveats, offline test evidence -->
<!-- /doc-head -->
# Stage 1049A - PBE5AC PtP v17 Pareto AQM+AQL kit

Kit: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`
Receipt: `artifacts/autoresearch/stage1049a_pbe5ac_v17_pareto_aqm_aql_busybox_kit.json`
Builder: `tools/verify/build_stage1049a_pbe5ac_v17_kit_receipt.py`

Offline-authored. No device, SSH or bake was touched (`live_devices_touched=false`).
Extends the v16 kit `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh`.

## tc-less and stat-less

The kit uses no `tc`, no `stat`, no `timeout`/`seq`/`usleep`/`iperf3`/`python`/`uci`/`iw`
and no `|| true`. POSIX `/bin/sh` with `set -eu`, `umask 077`. Stage 1025A
`audit_text` reports 0 findings. Integrity of the snapshot is an `md5sum` manifest.

## Usage

```
sh fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh [--dry-run|--apply|--verify|--rollback]
   [--root DIR] [--iface IF] [--phy PHY] [--dfs] [--watchdog-seconds N]
```

Defaults: `--dry-run`, `--iface phy2-sta0`, `--phy phy2`, empty root (real system).
`--dfs` selects a 120 s link watchdog instead of 45 s; `--watchdog-seconds N` overrides both.
`--apply` snapshots, writes, then polls `$ROOT/sys/class/net/$IFACE/operstate` (`up`) and
`carrier` (`1`). If the link is not up before the window ends the kit auto-rolls back and
exits non-zero. `--verify` and `--rollback` exit non-zero on any mismatch.

## Target files (5; 2 conditional)

| File | Write | Condition |
| :--- | :--- | :--- |
| `$ROOT/sys/kernel/debug/ieee80211/$PHY/aql_txq_limit` | `0 500 1000`, `1 1500 3000`, `2 3000 6000`, `3 1500 3000` | always |
| `$ROOT/sys/kernel/debug/ieee80211/$PHY/aql_threshold` | `12000` | always |
| `$ROOT/sys/kernel/debug/ieee80211/$PHY/aqm` | `fq_limit 2048`, `fq_memory_limit 4194304`, `fq_quantum 1514` | only if file exists |
| `$ROOT/proc/sys/net/ipv4/tcp_notsent_lowat` | `131072` | only if file exists |
| `$ROOT/proc/sys/net/core/default_qdisc` | `fq_codel` | always |

`BC/MC` is read-back verify only (format support). It is never written.
No persistence files (sysctl.d, hotplug) are installed: the changes are runtime only.

## Write syntax (write_syntax_source: Stage 1031A)

From `docs/STAGE1031A_MAC80211_AQL_DEBUGFS_WRITE_SYNTAX_RE.md`: `aql_txq_limit` takes a
NUMERIC ac index 0..3 (`VO/VI/BE/BK` names are only read-table row labels; the name form
is refuted). `aql_threshold` is a plain u32. `aqm` takes three separate writes
`fq_limit %u`, `fq_memory_limit %u`, `fq_quantum %u`. Read format source: Stage 955A.
Stock `aqm` per 955A/1031A: `fq_limit 512`, `fq_memory_limit 3145728`.

## Provenance

`pareto_provenance: "operator-supplied wave #10 calibration"` (live Pareto calibration).
The vector is not in any receipt and is not derived from Stage 1026A (SIMULATED_MODEL_ONLY).

## Caveats

- `tcp_notsent_lowat` only affects TCP that the radio itself originates. On a bridged/WDS
  radio it is a host/endpoint knob and does not shape forwarded traffic.
- `default_qdisc` only affects netdevs created after the write.
- No hardware effect is claimed; the values are operator-supplied.

## Offline emulation (`--root` non-empty)

A plain file cannot re-render debugfs. With a non-empty `--root` the kit rewrites the
rendered row in place (`VO/VI/BE/BK` row for the idx, or the `RW fq_xxx N` line). With
an empty root it does the literal Stage 1031A `echo` writes. The `FMX_WRITE_TRACE` line
(`path<TAB>value`) is identical in both modes. Rollback re-emits writes parsed from the
snapshot (AQL rows to `idx low high`, `RW fq_xxx N` to `fq_xxx N`); scalars are cat-back.

## Offline test evidence

Fake root with stock AQL 5000/12000 x4 + `BC/MC 50000`, aqm `RW fq_memory_limit 3145728`,
`RW fq_limit 512`, `RW fq_quantum 300`, `R fq_flows_cnt 4096`, `aql_threshold 5000`,
`tcp_notsent_lowat 4294967295`, `default_qdisc pfifo_fast`:

- dry-run: tree unchanged, trace empty.
- apply + verify: all PASS (exit 0); tampered value makes verify exit 1.
- rollback: tree byte-identical to the pre-apply state.
- `operstate=down` + `--watchdog-seconds 2`: auto-rollback, exit non-zero, tree restored.
- aqm and tcp_notsent_lowat absent: apply and rollback still succeed.
