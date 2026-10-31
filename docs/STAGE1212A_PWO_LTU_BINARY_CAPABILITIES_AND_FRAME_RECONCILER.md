<!-- doc-head: Stage1212A offline reconciler of PWO LTU max modulation and frame-duration options against ame_core.ko static RE, emitting recommend-only rule specs and validation vectors -->
<!-- /doc-head -->

# Stage1212A - PWO LTU binary capabilities and frame reconciler

Evidence class `PWO_LTU_BINARY_RECONCILER`. Offline, `live_devices_touched=false`, status CONFIRMED. Module `tools/uisp/pwo_ltu_binary_capabilities_and_frame_reconciler.py`, receipt `artifacts/verification/stage1212a_pwo_ltu_binary_reconciler.json`, test `tests/test_stage1212a_ltu_reconciler.py`.

Provenance: Stage 1187A Sec5 (PWO vs binary discrepancy) and Stage 12/249A (RC-13, RC-22). Facts are static `ame_core.ko` RE (LTU v2.3.1 and v2.4.2), not live measurements.

## Discrepancy 1: max modulation
- PWO `ltuRules.js:getLTUCapabilities` reports `1024-QAM (10x)` for non-Wave LTU.
- Binary: `4096-QAM (12x, MCS 31)` exists only in 2x2 MIMO tables.
- Enabled at 10/20/30/40/50 MHz; zeroed in `table_ptpPwrRange` at 60/80/100 MHz.
- Entry needs `startThrd_4096=97` percent, stay needs `stayThrd_4096=90` percent.
- TX backoff: 16 dBm LTU-Rocket, 10-12 dBm LTU-Lite/Pro/LR.

## Discrepancy 2: frame duration
- PWO lists 2/4/8 ms.
- Binary immediates (RC-22): 2000/2500/4000/5000 us, i.e. 2/2.5/4/5 ms.
- 8 ms has no binary immediate; 2.5 and 5 ms are missing from PWO.

## API
- `reconcile_ltu_capabilities()` returns the `qam` and `frame_durations` blocks.
- `validation_vectors()` returns vectors, each with expected, actual and pass: 30 MHz may advertise 12x, 60 MHz must not, 2.5 ms is valid, 8 ms is not.
- `pwo_rule_spec()` returns an advisory spec with `recommend_only=True`, `auto_approve=False`, `code_change_applied=False`.
- `main --write-receipt` writes the receipt with a NUL self-check retried 3 times.

## Boundaries
Review only. `whatsappbot-final` is not modified; PWO owners decide whether to adopt the spec.
