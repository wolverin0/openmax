<!-- doc-head: Stage1207A cascading blast-radius proof per backbone tier and SG-01 veto proof for the backbone PoE power-cycle -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1207A - Cascading blast-radius proof

Evidence class `FULL_3TIER_BACKBONE_AND_SG01_GUARD`. Offline, `live_devices_touched=false`. Receipt `artifacts/verification/stage1207a_cascading_blast_radius_proof.json`, produced from `tools/uisp/full_3tier_backbone_and_sg01_guard_engine.py` (Stage 1206A).

## Fault cascade (DAG traversal, not hardcoded)

- `edificio_principal` or `hop-ep-almafuerte`: 32 CPEs, path EP, Almafuerte, Guarida, Panel.
- `almafuerte` or `hop-almafuerte-guarida`: 32 CPEs (all Guarida).
- `guarida`: 32 CPEs.
- `panel1`: 4, `panel2`: 22, `panel3`: 6.

## SG-01 veto proof

Vetoed: `ether2-sw-poe200` power_cycle, `198.18.0.79` poe_off, `198.18.0.80` disable, `198.18.0.2` interface `ether2-sw-poe200` reboot_switch. Allowed: a PtP `set_channel` action. Receipt field `sg01_all_backbone_poe_actions_vetoed` is true.

## Verification

`tests/test_stage1206a_backbone.py` (8 tests) covers cascade, veto, allow and the first-class link evaluation.
