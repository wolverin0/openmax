<!-- doc-head: Stage 1042A offline gate + consolidated suite for the v16 statless/tcless BusyBox kits (1037A..1041A); fail-closed, no live devices. -->
<!-- /doc-head -->
# Stage 1042A - v16 statless/tcless kits gate

Offline consumer gate for Stages 1037A..1041A. No SSH, no live devices, no firmware baking.

## Files

- Gate: `tools/verify/verify_stage1042a_v16_statless_tcless_kits_gate.py`
- Suite: `tests/test_stage1037a_to_1042a_suite.py`
- Receipt: `artifacts/autoresearch/stage1042a_v16_statless_tcless_kits_gate_receipt.json`
- Kits: `firmware/openwrt/common/fmx_wa_v16_statless_tcless_busybox_kit.sh`, `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh`
- Harness test (1039A): `tests/test_stage1039a_v16_busybox_restricted_path_harness.py`

## Gate checks (fail-closed, `SystemExit(1)` on any failure)

1. Receipts 1037A..1041A exist, not all-NUL, `status == "CONFIRMED"`, `live_devices_touched is False`, pass `audit_stage_receipt_5pillars`.
2. Docs 1037A..1042A exist, under 180 lines, line 1 starts with a doc-head opening.
3. Both v16 kits exist, contain no CR bytes, and `sh -n` returns 0 (skipped and recorded when `sh` is absent).
4. Bashism scan (non-comment lines): no `[[`, `function `, `declare `, `local -`, `=(`, `$'`, or `==` inside `[ ]`.
5. The 1025A auditor `audit_text` returns zero findings for each kit; `|| true` / `|| :` count is 0.
6. `python -m pytest tests/test_stage1039a_v16_busybox_restricted_path_harness.py -q` returns 0 (a skip for no-sh counts as pass and is recorded as `harness_1039a_skipped`).
7. The 1040A receipt records findings 0 for both kits; every 1041A matrix row has `pass == true`.

## Receipt

`status` is CONFIRMED only when every check passes, otherwise FAILED with `failures`. Also carries `all_gates_passed`, `functional_checks`, `five_pillar_compliance` and `pillar_e_memory_master_claim_id` (`FMX-STAGE1042A-V16-STATLESS-TCLESS-KITS-GATE`). The write retries 3 times against all-NUL corruption.

## Run

- `python tools/verify/verify_stage1042a_v16_statless_tcless_kits_gate.py`
- `python -m pytest tests/test_stage1037a_to_1042a_suite.py -q`
