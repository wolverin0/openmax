<!-- doc-head: Stage 1123A read-only statless/tcless BusyBox health dump for the pbe5ac v17 PTP kit; offline, parseable by the Stage 1121A canary monitor, no live claim -->

# Stage 1123A - PTP v17 One-Shot Health Dump

Script: `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_ptp_v17_one_shot_health_dump.sh`
Builder: `tools/verify/build_stage1123a_1124a_health_dump_receipts.py`
Receipt: `artifacts/autoresearch/stage1123a_ptp_v17_one_shot_health_dump.json`

## Contract
- POSIX `/bin/sh` (BusyBox ash), `set -u` only, LF only, no bashisms.
- READ-ONLY: `cat`, `sha256sum` and an integer `ping` only. It never writes debugfs, proc or sysfs.
- No `stat`, `tc`, `timeout`, `seq`, `usleep`; ping is `ping -c 20 -i 1 -W 2 "$PEER"`.
- Options: `--root DIR` (or env `FMX_ROOT`) prefixes every read path; `--phy`, `--iface`, `--peer`.
- Test-only env: `FMX_PING_OUTPUT` (canned ping text), `FMX_SURVEY_FILE` (canned survey dump).

## Output (for the Stage 1121A canary monitor)
- `FMX_HEALTH_DUMP_BEGIN version=1 stage=1123A phy=.. iface=.. peer=.. root=..`
- Per section: `FMX_SECTION <name> status=<ok|absent>`, raw lines, `FMX_END <name>`.
- `FMX_HEALTH_DUMP_END ok=N absent=M`.
- Sections: `station_dump`, `aqm`, `aql_txq_limit`, `aql_threshold`, `default_qdisc`,
  `tcp_notsent_lowat`, `survey_dump`, `mtd_sha`, `ping`.

## Sources
- Station files: `sys/kernel/debug/ieee80211/<phy>/netdev:<iface>/stations/*/` and `.../<phy>/stations/*/`.
- `mtd_sha`: `dev/mtdblock0`, `dev/mtdblock1`, `dev/mtdblock5`, each guarded by `[ -r ]`.
- Live (no `--root`) additionally runs `iw dev <iface> station dump` and `survey dump` when `iw` exists.

## Exit codes
- 0 healthy read; absent optional files are reported as `status=absent`, never an error.
- 64 usage error; 65 invalid `--phy`, `--iface`, `--peer` or missing `--root` directory.

## Scope
- Offline authoring only; no device was touched. Existing watchdogs and other scripts are unchanged.
