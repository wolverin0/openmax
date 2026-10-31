<!-- doc-head: Stage 1186A Wave 25 Claude gate offline: valida receipts 1181A..1184A, docs, aislamiento de corpus y humo de los tres modulos bilateral/peer-buddy/PWO. -->
# Stage 1186A - Wave 25 Claude gate

Compuerta 100% offline y fail-closed (`raise SystemExit(1)`), sin radios ni SSH.

## Archivos

- Gate: `tools/verify/verify_stage1186a_wave25_claude_gate.py`
- Suite: `tests/test_stage1181a_to_1186a_suite.py`
- Receipt: `artifacts/verification/stage1186a_wave25_claude_gate.json`
- Guia: `docs/STAGE1185A_CONCIENCIA_BILATERAL_DE_SITIO_PTP_Y_PWO_ARQUITECTURA_ES.md`

## Receipts fijados (todos en `artifacts/autoresearch/`)

- 1181A `stage1181a_bilateral_site_topology_graph.json`
- 1182A `stage1182a_on_tower_peer_buddy_disambiguator.json`
- 1183A `stage1183a_pwo_bilateral_recommendation_bridge.json`
- 1184A `stage1184a_master_docs_sync_through_1186a.json`

Cada uno: existe, no es NUL, `status=="CONFIRMED"`, `live_devices_touched` es `False`, 5 pilares conformes.

## Chequeos

- Docs 1181A..1186A y docs maestros: menos de 180 lineas y doc-head en la linea 1.
- Aislamiento de corpus en `artifacts/autoresearch` y `artifacts/verification`
  (sin `"synthetic_fixture": true` ni `"session_id": "SYNTHETIC-`).
- Humo bilateral: un canal que solapa a un hermano co-sitio da `allowed=False`, `vetoes` y `blast_radius_cpes` mayor que 0.
- Humo Peer Buddy: `CO_SITE_SELF_INTERFERENCE`; `aqm_feed_forward(50.0)` con `recommend_only=True`.
- Humo puente PWO: `auto_approve=False`, NO-CHANGE ante veto y guarda de ancho 20 MHz.
- Reintento 3 veces ante escritura de receipt corrupta (todo NUL).

## Honestidad

Todo es modelo offline; las recomendaciones son solo sugerencias para aprobacion humana.
Claim id: `FMX-STAGE1186A-WAVE25-CLAUDE-GATE`.
