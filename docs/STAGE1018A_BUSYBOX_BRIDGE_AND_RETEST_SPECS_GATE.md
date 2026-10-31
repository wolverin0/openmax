<!-- doc-head: Stage 1018A | offline consumer gate for 1013A..1017A (BusyBox nc/uhttpd bridge sink adapter, WA readback validator, three retest specs) | status CONFIRMED when gate passes | live_devices_touched false -->
<!-- /doc-head -->
# Stage 1018A - BusyBox Bridge and Retest Specs Gate

Offline, fail-closed consumer gate plus consolidated pytest suite for Stages 1013A..1018A. No device is touched; no built command is ever executed.

## Files

- Gate: `tools/verify/verify_stage1018a_busybox_bridge_and_retest_specs_gate.py`
- Suite: `tests/test_stage1013a_to_1018a_suite.py`
- Receipt: `artifacts/autoresearch/stage1018a_busybox_bridge_and_retest_specs_gate_receipt.json`

## Checks

1. Receipts 1013A..1017A exist, are not all-NUL, have status CONFIRMED, `live_devices_touched` false, and pass `audit_stage_receipt_5pillars`.
2. Docs 1013A..1018A exist, are under 180 lines, and start with a doc-head comment.
3. `workloads/busybox_nc_uhttpd_bridge_sink_adapter.py`: `build_commands` argv are statically inspected. Every argv[0] basename must be in nc, dd, awk, wget, uhttpd, sh, cat, command, and no token may contain iperf3, python or stat. `parse_dd_transfer` must give a rate on a full dd output and none on records-only output.
4. `tools/qca988x/validate_wa_tcless_statless_profile_readback.py`: champion text yields `CHAMPION_APPLIED`; `pfifo_fast` is rejected; stock AQL 5000/12000 yields `STOCK_NOT_APPLIED`.
5. Unit tests of 1013A and 1014A run via subprocess pytest (return code 0).
6. Spec invariants for 1015A..1017A: cited queue rows are a non-empty subset of `artifacts/autoresearch/stage1004a_pending_live_retest_queue.json`, measurement tool paths exist, `execution_status` is `SPEC_ONLY_NOT_EXECUTED`, no value equals PRODUCTION_READY, `flashing_mandate` is non-empty, every acceptance criterion has a source.

## Constraints

The operator constraint (no iperf3, no python, no stat on the target) is enforced as an executable check in item 3. Receipt writes retry 3 times against all-NUL corruption.
