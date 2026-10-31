<!-- doc-head: Stage1075A fail-closed upgrade of the boot hotplug 99-fmx-wa-universal-champion-v17 (offline, no device touched) -->
Operator-ordered edit of `firmware/openwrt/common/99-fmx-wa-universal-champion-v17`; replaced sha256 `651a64a9...c09d`.
<!-- /doc-head -->

# Stage1075A - Champion v17 fail-closed upgrade

## What changed

| Before | After |
|---|---|
| 22 error-swallowing `|| true` suffixes | 0; every write is `if [ -w FILE ]; then printf ... > FILE; fi` |
| `echo 4000 > aql_txq_limit` (one token) | four 1031A writes `0 500 1000`, `1 1500 3000`, `2 3000 6000`, `3 1500 3000` |
| `tc qdisc replace ... fq_codel` | aqm writes `fq_limit 2048`, `fq_quantum 1514`, `fq_memory_limit 4194304` plus `default_qdisc` = `fq_codel` |
| fixed `/` paths | `FMX_ROOT` or `--root DIR` (default empty), `FMX_PHY` (default `phy0`), `FMX_WRITE_TRACE` hook |

AQL values and the `ac low high` syntax come from `firmware/openwrt/common/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh` (Stage 1031A: a single token fails the 3-token sscanf).

## Why `set -u` and not `set -e`

A hotplug that aborts halfway leaves the radio half-configured. The original tolerated every failure; boot-safety is kept by the existence guard (missing debugfs or proc file means skip, exit 0), not by hiding errors. `set -u` catches typos in variable names only.

## Dropped tc parameters

`target 2000us`, `interval 40000us` and `ecn` have no tc-less debugfs path: recorded as `DROPPED_NO_TCLESS_PATH`. `limit` maps to `fq_limit`, `quantum` to `fq_quantum`; `flows 1024` has no 1031A equivalent and is not carried.

## aql_threshold discrepancy

The hotplug keeps `aql_threshold` at `24000` (unchanged); the v17 kit writes `12000`. Not reconciled here; operator decision.

## Kept behaviour

`sysctl -w` and `iw phy $PHY set rts off` stay (1025A does not flag them), behind `command -v` guards and skipped under an offline root. Optional helpers run only if executable.

## Follow-up

`common/SHA256SUMS` is NOT touched; it must be re-signed by Codex #2 / the operator because this file's sha changed.

Receipt: `artifacts/autoresearch/stage1075a_champion_v17_fail_closed_upgrade.json`, built by `tools/verify/build_stage1075a_1076a_champion_v17_receipts.py`.
