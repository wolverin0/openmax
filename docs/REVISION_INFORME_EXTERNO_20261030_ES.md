<!-- doc-head: Revision del informe externo del operador (openMAX_Investigacion_rendimiento_2026-10-30.docx, W365): veredicto verificado por el orquestador; los repos y commits citados son reales; lo nuevo verificado (peso NAPI de ag71xx, alineacion IP tras tags DSA, firmware ath10k-ct NRCC), lo que ya estaba hecho en FuturaMAX y lo que queda sin verificar -->
Que cubre: el veredicto sobre el informe externo del 30/10, punto por punto: nuevo, ya hecho o sin verificar, y que se hace con cada uno.
Estado: resumen offline de las notas verificadas del orquestador (W365). El .docx no se copia al repo.
Siguiente: docs/STAGE3025A_X05_X06_X07_ES.md (X06 resuelto offline, specs A/B de X05 y X07).
Leer cuando: antes de abrir un experimento a partir de ese informe o de citar sus cifras.
<!-- /doc-head -->
# Revision del informe externo del 30/10

**Fuente:** `T:\openMAX_Investigacion_rendimiento_2026-10-30.docx`, informe externo que trajo el operador.

**Veredicto:** los repos y commits que cita **existen**. Eso lo diferencia del informe LLM de 2026-08, que inventaba fuentes.

## 1. Nuevo y verificado (no estaba en FuturaMAX)

| Id | Punto | Estado | Que se hace |
| :-- | :-- | :-- | :-- |
| X05 | Peso NAPI del driver ag71xx (interno del driver) | Nunca barrido. Solo se probaron dev_weight, tx_bias y BQL | Spec A/B en banco, 32 contra 64 (Stage 3025A) |
| X06 | Alineacion del header IP detras de tags DSA (commit f091230) | Condicional: solo aplica si hay un switch DSA con tag antepuesto en el camino ag71xx | Se resuelve offline leyendo el DTS de cada placa (Stage 3025A) |
| X07 | Firmware ath10k-ct NRCC | Cero menciones en el repo. Candela los llama `full-nrcc-community-22` y `full-htt-mgt-nrcc-community-22`, no "diet" | Spec A/B en banco: full-community-22 contra full-nrcc-community-22, en una CPE con un par |

## 2. Ya hecho en FuturaMAX (no se repite)

- **Memoria y OOM:** min_free_kbytes, fq_memory_limit y los guardas de RAM.
- **Colas:** AQL por AC y aql_threshold, fq_quantum y fq_limit, CAKE y diffserv4, tx_queue_len, BQL.
- **NAPI y red:** netdev_budget y budget_usecs, GRO, napi_defer_hard_irqs, packet steering, flow offloading, dev_weight y tx_bias.
- **Metodo:** A/A con correccion de Sidak (Stage 889A), la regla de decision que se usa en todos los A/B.

## 3. Sin verificar

- **Cifras del informe:** 273 -> 284 Mbps y 743 -> 855 Mbps. Son de otra plataforma, no de AR9342/QCA988x, y no se pueden trasladar. No se citan como esperables aca.

## 4. Lo primero que propone el orquestador

1. **X01, provenance:** unir cada imagen y kit con su arbol, config y sha antes de comparar firmware.
2. **X02, rebuild reproducible de FMX-0011:** que A y B salgan del mismo arbol (v24.10.4, 78b23a26) y la misma config. Es lo que necesita X05.

## 5. Reglas al usar este informe

- **Etiquetas:** cada punto lleva CONFIRMED / INFERRED / UNKNOWN / REFUTED segun la evidencia propia, no segun el informe.
- **Ambito:** nada del informe se aplica en produccion. X05 y X07 son solo de banco y siguen las precondiciones de flasheo (backup y hash de mtd0/1/4/5).
- **Cifras:** las del informe no se usan como objetivo. El objetivo sale del A/A y del ABBA propios.
