<!-- doc-head: Stage 1040A proof that both v16 kits have zero Stage 1025A BusyBox-applet findings and no masked failures -->
<!-- /doc-head -->
# Stage 1040A: v16 kits, 1025A zero findings

Offline static audit. Builder: `tools/verify/build_stage1039a_to_1041a_v16_adversarial_receipts.py`.

## Method
- `from tools.verify.audit_stage1025a_shell_kits_busybox_applet_compatibility import audit_text`, run on the
  content of both v16 kits; per-kit `findings_total` must be 0.
- Extra check the 1025A auditor lacks: count of `|| true` and `|| :` (masked failures) must be 0 per kit.
- 1025A `classify_target` keys on `*field_kit.sh`; v16 names classify as `UNCLASSIFIED` (WARNING-class),
  but a WARNING-class audit with zero findings is still zero.

## Kits
- `firmware/openwrt/common/fmx_wa_v16_statless_tcless_busybox_kit.sh`
- `firmware/openwrt/pbe5ac_gen2_ptp_kit/fmx_pbe5ac_v16_statless_tcless_busybox_kit.sh`

## Result
Receipt `artifacts/autoresearch/stage1040a_v16_kits_1025a_zero_findings.json` records per kit
`findings_total`, `masked_failure_count`, `target_class`. Status `CONFIRMED` only when both are 0 for both
kits; `DEFERRED` if a kit is absent (re-run the builder).
