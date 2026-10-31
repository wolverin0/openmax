<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 1145A | static audit of LTU-Lite SG-LTU-01 passive fence: zero writes to /dev/ame* | live receipts 1023A/1117A/1135A read-only and zero-synthetic check | offline -->
# Stage 1145A - LTU-Lite passive telemetry and safety fence audit

Tool: `tools/verify/audit_ltulite_passive_telemetry_and_safety_fence.py`.
Test: `tests/test_stage1145a_ltulite_passive_safety_fence.py`.
Receipt: `artifacts/verification/stage1145a_ltulite_passive_telemetry_and_safety_fence.json`.
Offline only: no SSH, no device. `live_devices_touched=false`. Target of the audited receipts: LTU-Lite 198.18.0.63.

## Fence rule

The LTU safe kit audits `/dev/ame*` with zero touches. Reads (`cat`, inspect) are allowed; any write is a
FENCE VIOLATION: redirect (`>`, `>>`, `3>`), `exec N>`, `dd of=`, `tee`, `cp`/`mv`/`install` onto the node, or a
write through a variable assigned a `/dev/ame*` path. Comment lines are ignored.

## Scope scanned

`firmware/ltu_safe_kit/*.sh` and `firmware/openwrt/common/fmx_ltu_*.sh`.

## Receipt checks

`artifacts/autoresearch/stage1023a_live_ltu_lite_readonly.json`,
`artifacts/autoresearch/stage1117a_consolidated_pytest_1079a_1108a.json`,
`artifacts/verification/stage1135a_live_ltu_lite_110_calibrated_snapshot.json`.
Each must be valid JSON, carry no true write/deploy flag (`target_configuration_writes`,
`remote_files_uploaded`, `proprietary_device_node_access`, `deployment_authorized`), open no device node, and hold no
synthetic marker (the 1112A rule: `synthetic_fixture=true`, `SYNTHETIC-` session or peer id, nested synthetic class,
or any of these under a live evidence class).

## Result

- `fence_status`: COMPLIANT, `fence_violations`: 0, `scripts_scanned`: 22.
- Only `fmx_ltu_v21_276window_field_kit.sh` names `/dev/ame*`, inside a comment ("zero touches").
- Synthetic markers: 0 across the three receipts.
- 1023A: `READONLY_NATIVE_LTU_COUNTER_OBSERVATIONS`, class `CONFIRMED_LIVE_HARDWARE`, config writes false.
- 1117A: status `CONSOLIDATED_MATRIX_FAILED` (offline pytest matrix); reported as its own honest failure, not a fence issue.
- 1135A: status `BLOCKED_ACCESS`, SSH password rejected, 0 snapshots acquired. It records `network_attempted=true` with
  `ssh_executed=false`; read as "no remote command ran", noted in the receipt.

## Limits

Line-based regex, not a shell parser: heredoc or `eval` bodies are scanned as plain text, and a quoted ` # ` inside a
line can hide a trailing write. Upgrade to a real shell parser if false results appear.
`status=CONFIRMED` means the audit completed; the verdict is `fence_status`.
Claim id: `FMX-STAGE1145A-LTU-LITE-PASSIVE-SAFETY-FENCE-AUDIT` (not ingested).
