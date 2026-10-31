<!-- doc-head: Stage 1052A Stage 1025A BusyBox applet auditor zero-findings proof for both v17 kits (offline) -->
<!-- /doc-head -->
# Stage 1052A: v17 kits 1025A zero findings

Offline only. No device is touched (`live_devices_touched=false`).

## What it proves
Both v17 kits pass the Stage 1025A BusyBox applet-compatibility auditor with `findings_total == 0`,
and contain no masked failures (`|| true` or `|| :`), which would hide a failed write.

## Kits
- `firmware/openwrt/common/fmx_wa_v17_pareto_aqm_aql_busybox_kit.sh`
- `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v17_pareto_aqm_aql_busybox_kit.sh`

## Method
`audit_text` from `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py` runs on
each kit's text. The builder also counts `|| true` and `|| :` occurrences; both must be 0.
The per-kit result (target class, findings, masked count) is recorded in the receipt.

## Run
`python tools/verify/build_stage1051a_1052a_v17_harness_receipts.py`.
Receipt: `artifacts/autoresearch/stage1052a_v17_kits_1025a_zero_findings.json`.
If either kit is absent the status is DEFERRED; re-run the builder once both exist.
