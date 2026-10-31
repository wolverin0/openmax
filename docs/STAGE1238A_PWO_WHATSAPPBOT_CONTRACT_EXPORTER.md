<!-- doc-head: Stage1238A offline validated schema-versioned PWO contract bundle (pwo-contract-1.0) combining 3-tier SG-01, bilateral what-if, peer buddy AQM, symptom/.ko, LTU tables and coverage-gap rules for whatsappbot-final ingestion -->
<!-- /doc-head -->

# Stage1238A - PWO whatsappbot-final contract bundle exporter

Evidence class `PWO_WHATSAPPBOT_CONTRACT_BUNDLE`. Offline, `live_devices_touched=false`, status CONFIRMED. Module `tools/uisp/pwo_whatsappbot_contract_exporter.py`, receipt `artifacts/verification/stage1238a_pwo_whatsappbot_contract_bundle.json`, test `tests/test_stage1238a_contract_exporter.py`. Claim `FMX-STAGE1238A-PWO-WHATSAPPBOT-CONTRACT-BUNDLE`.

The bundle is DATA ONLY. The exporter writes solely the futuraMAX receipt above; it never writes inside whatsappbot-final, makes no live call and recommends nothing auto-approved. The receipt is the bundle plus the standard receipt envelope.

## Public API
- `export_contract_bundle() -> dict`: `schema_version` (`pwo-contract-1.0`), `generated_at`, `sections`, `invariants`, `validation`.
- `validate_bundle(bundle) -> dict`: `{valid, errors}`; enforces schema, invariants and semantic checks.
- `main --write-receipt`: validates, then writes the receipt (3x NUL/readback self-check, LF).

## Sections
- `backbone`: `tools/uisp/full_3tier_backbone_and_sg01_guard_engine.py` tiers, hops, CPE counts, cascading blast radius per node/hop, SG-01 probes (disable/power-cycle PoE vetoed, read-only allowed).
- `channel`: `tools/uisp/bilateral_whatif_channel_simulator_and_pareto_ranker.py` 20 MHz candidates, Pareto front, unilateral vs bilateral counterfactual.
- `peer_buddy_aqm`: `tools/uisp/on_tower_peer_buddy_and_anomaly_disambiguator.py` three classifications and fq_codel feed-forward samples (0/25/50/75 percent drop).
- `symptom_diagnostics`: `tools/uisp/community_symptom_and_ko_root_cause_pwo_matcher.py` 9 symptom classes with `.ko` cards.
- `ltu_capability_tables`: `tools/uisp/pwo_ltu_binary_capabilities_and_frame_reconciler.py` 4096-QAM on 10-50 MHz, frames 2/2.5/4/5 ms.
- `coverage_gap_rules`: `tools/uisp/pwo_coverage_gap_rules_stall_eth_disconnect.py` 3 rule ids with sample evaluations.

Each module is imported defensively; `validation.module_presence` records `present`, `built` and any error per section.

## Invariants
`recommend_only=True`, `auto_approve=False`, `fixed_width_mhz=20`, `sg01_backbone_poe_protected=True`. `validate_bundle` also rejects any nested `auto_approve` not False, `recommend_only` not True, `live_devices_touched` not False, missing sections, non-20 MHz channel candidates, wrong LTU tables, and failing SG-01 probes.

## Honest limits
Models and crafted probes, not live radio evidence. `.ko` attribution is static RE plus community KB. Operator approval is required for every recommendation.
