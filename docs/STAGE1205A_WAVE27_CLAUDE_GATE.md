<!-- doc-head: Stage 1205A Wave 27 Claude gate offline: valida receipts 1200A..1204A, docs, enlaces rotos, aislamiento de corpus y humo del simulador what-if y del pipeline zero-FP bilateral. -->
# Stage 1205A - Wave 27 Claude gate

Compuerta 100% offline y fail-closed (`raise SystemExit(1)`), sin radios ni SSH.

## Componentes
- Gate: `tools/verify/verify_stage1205a_wave27_claude_gate.py`.
- Suite: `tests/test_stage1200a_to_1205a_suite.py`.
- Receipt: `artifacts/verification/stage1205a_wave27_claude_gate.json`.

## Verificaciones
- Receipts 1200A..1204A en `artifacts/verification`: existen, no NUL, `CONFIRMED`, `live_devices_touched` false, cinco pilares.
- Exactamente un `docs/STAGE{stage}_*.md` por etapa 1200A..1205A mas los dos docs maestros, cada uno bajo 180 lineas con doc-head en la linea 1.
- Enlaces rotos: reejecuta `tools/verify/build_stage1001a_broken_link_repair_and_reaudit.py` y exige `broken_links_after` igual a 0.
- Aislamiento de corpus: 0 fixtures sinteticos en `artifacts/verification` y `artifacts/autoresearch`.
- Simulador: `simulate`, `pareto_front` sin puntos dominados y contrafactico (unilateral colisiona en el extremo lejano, bilateral lo evita).
- Pipeline: clasificacion dentro de las 5 vias, un blip de una ronda no queda confirmado, tarjetas PWO con `auto_approve` false.

## Estado honesto
- `CONFIRMED_LIVE_HARDWARE` sigue en 0; sin `PRODUCTION_READY`.
