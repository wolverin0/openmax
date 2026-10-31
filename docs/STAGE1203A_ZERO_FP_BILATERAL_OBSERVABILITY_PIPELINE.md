<!-- doc-head: Stage 1203A Spanish operator recommendation cards for Guarida, Almafuerte and Edificio Principal from the 1202A pipeline, recommend-only, offline -->

# Stage 1203A - Operator Recommendation Cards (ES)

Spanish operator cards built from the 1202A pipeline output. Offline model: recommend-only,
no device writes, nothing auto-approved.

## Files

- Receipt: `artifacts/verification/stage1203a_operator_recommendation_cards_es.json`
- Source pipeline: `tools/uisp/zero_false_positive_bilateral_observability_pipeline.py`
- Stage 1202A doc: `docs/STAGE1202A_ZERO_FP_BILATERAL_OBSERVABILITY_PIPELINE.md`

## Card fields

Each card has `situacion`, `clasificacion`, `evidencia` (2 rondas consecutivas confirmadas,
5 sondeos por ronda), `recomendacion` (modo SOLO_SUGERENCIA, `auto_aprobar` false),
`compuertas` (the 6 WirelessExperimentGates) and `ancho_fijo_mhz` 20.

## Cards

| Id | Sitio | Clasificacion |
| :--- | :--- | :--- |
| ES-GUA-01 | Guarida | POP_WIDE_POWER_OR_SWITCH_EVENT |
| ES-GUA-02 | Guarida | BILATERAL_COLLOCATED_CHANNEL_COLLISION |
| ES-GUA-03 | Guarida (Panel2) | SINGLE_SECTOR_RF_INTERFERENCE |
| ES-GUA-04 | Guarida (Panel3) | SINGLE_CPE_ALIGNMENT_OR_FOLIAGE_DROP |
| ES-ALM-01 | Almafuerte | UPSTREAM_PTP_BACKHAUL_CONGESTION |
| ES-EDP-01 | Edificio Principal | UPSTREAM_PTP_BACKHAUL_CONGESTION |

## Honesty

Evidence comes from crafted model snapshots, not live readings. The Edificio Principal
link is absent from the 1181A graph, so ES-EDP-01 is a model card reusing the congestion
scenario. The gates are listed for PWO to check; none were evaluated here.
