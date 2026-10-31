<!-- doc-head: Stage 1204A master docs sync offline: indexa Wave 27 (1200A..1205A) en CURRENT_STATE y el indice maestro; sin radios ni SSH. -->
# Stage 1204A - Master docs sync (Wave 27)

Sincroniza `docs/CURRENT_STATE.md` y `docs/MASTER_RESEARCH_AND_AUTORESEARCH_INDEX.md` con la Wave 27.

## Alcance
- 1200A/1201A: simulador what-if bilateral y ranker de Pareto (20/40/80 MHz, 5180-5825, penalizacion DFS CAC); prueba de que el cambio unilateral solo-Guarida colisiona en Almafuerte .60 y la Union Bilateral lo evita.
- 1202A: pipeline de observabilidad bilateral zero-FP (clasificacion en 5 vias, confirmacion AP-local en 2 rondas, tarjetas PWO recommend-only).
- 1203A: tarjetas de recomendacion para el operador en espanol.
- 1205A: compuerta Wave #27.

## Garantias
- Cada archivo maestro queda por debajo de 180 lineas, LF, sin CR, rutas en codigo en linea.
- Estado honesto: `CONFIRMED_LIVE_HARDWARE` sigue en 0; sin `PRODUCTION_READY`.

## Evidencia
- Receipt: `artifacts/verification/stage1204a_master_docs_sync.json`.
