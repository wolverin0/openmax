<!-- doc-head: Stage 1030A consumer gate for 1025A..1029A: BusyBox applet audit, AQL Pareto calibration, post-audit index/sync docs; offline, fail-closed. -->
<!-- /doc-head -->
# Stage 1030A - BusyBox Applet Audit & AQL Pareto Gate

Offline, fail-closed consumer gate over Stages 1025A..1029A. No live devices touched.

## Files
- Gate: `tools/verify/verify_stage1030a_busybox_applet_audit_and_aql_pareto_gate.py`
- Suite: `tests/test_stage1025a_to_1030a_suite.py`
- Receipt: `artifacts/autoresearch/stage1030a_busybox_applet_audit_and_aql_pareto_gate_receipt.json`

## Checks
1. Receipts 1025A..1029A exist, are not all-NUL, `status == CONFIRMED`, `live_devices_touched is False`, and pass `audit_stage_receipt_5pillars`.
2. Docs 1025A..1030A plus `docs/CURRENT_STATE.md` and `docs/RESEARCH_LEDGER.md`: under 180 lines, line 1 starts with a doc-head opening.
3. `audit_text` from `tools/verify/audit_stage1025a_shell_kits_busybox_applet_compatibility.py` flags all 8 applets on a positive fixture (stat, timeout, usleep, seq, tc, iperf3, python3, ping -i 0.2) and zero findings on a negative fixture.
4. 1025A receipt `findings_total` is an int >= 0 (CONFIRMED means the audit completed, not zero findings).
5. `calibrate(seed=0, pop_size=12, n_gen=5)` run twice gives the identical `pareto_front`; `reference == [300,600,1000,2000,1500,3000,500,1000]`; every point has low < high per AC.
6. 1027A: `sum(class_counts.values()) == len(snapshot_files)`; each `CONFIRMED_LIVE_HARDWARE` stage's cited receipt really has `controlled_aa_valid == true`; no `PRODUCTION_READY` value.
7. Unit tests of 1025A and 1026A pass via `python -m pytest`.
8. `tools/verify/build_stage1001a_broken_link_repair_and_reaudit.py` re-run; `broken_links_after == 0` in `artifacts/autoresearch/stage1001a_broken_link_repair_and_reaudit.json`.

## Run
`python tools/verify/verify_stage1030a_busybox_applet_audit_and_aql_pareto_gate.py` then `python -m pytest tests/test_stage1025a_to_1030a_suite.py -q`.
