<!-- doc-head: Wave141 auditoria estatica y ledger de evidencia primaria sin promocion -->
Inventario local de gates y clasificacion trazable por fila del TSV.
Las lagunas de evidencia impiden declarar cobertura completa de cuatro clases.
<!-- /doc-head -->

# Stage1886A — Gates históricos y evidencia viva frente a simulación

Fecha: 2026-10-28. Atribución: `external controller`.
Alcance: lectura local de fuentes y recibos guardados, cero SSH, sin cambios de dispositivos.

## Inventario de gates — CONFIRMED

Stage1884A analiza por AST 232 archivos históricos de `tools/verify` cuyo nombre contiene `gate`.
El corte es anterior a Stage1884; incluye archivos sin número. Guarda ruta, hash, comparación y línea.
No importa ni ejecuta esos gates. Los archivos posteriores quedan fuera del inventario histórico.
El builder capturado declara literalmente `RECEIPT_FEED_MAX=1883`.
Se encontraron seis requisitos de igualdad exacta, dos mínimos monotónicos y cinco comparaciones para revisión.

| Gate | Umbral exacto | Inferencia con 1883 |
|---|---:|---|
| Stage1607A | 1620 | REJECT |
| Stage1643A | 1650 | REJECT |
| Stage1691A | 1691 | REJECT |
| Stage1721A | 1721 | REJECT |
| Stage1745A | 1745 | REJECT |
| Stage1805A | 1805 | REJECT |

Stage1829A exige un mínimo de 1829 y Stage1883A un mínimo de 1883.
Ambos aceptan 1883 en la comparación analizada. Esta compatibilidad es `INFERRED`, no ejecución del gate completo.
Los cinco casos ambiguos permanecen `REVIEW`. No se modifica ninguna condición histórica.
La revisión corrigió el analizador para que `assert True` y fallos condicionales anidados no se interpreten como rechazo incondicional.

## Ledger por fila — CONFIRMED con lagunas explícitas

Stage1885A captura 48 filas de `artifacts/autoresearch/results.tsv`, 10953 bytes, más la cabecera.
Resuelve 47 filas a un recibo primario. Conserva hash de cada fila, JSON pointer de iteración y hashes de fuentes y capturas nativas.
La reproducción verifica ese prefijo y el catálogo de fuentes capturado; las publicaciones posteriores no cambian la resolución.
La selección de iteración usa su identificador, nunca la posición supuesta del arreglo.

| Clase solicitada | Filas |
|---|---:|
| CONFIRMED_LIVE_PAIRED_PASS | 2 |
| LIVE_SINGLE_WINDOW_DISCARD | 0 |
| LIVE_HOLDOUT_REJECTED | 2 |
| SIMPY_OFFLINE_ONLY | 0 |
| Sin clase aplicable o evidencia suficiente (`null`) | 44 |

Las dos filas pareadas son Stage1542A, iteraciones 2 y 3: aceptación exploratoria guardada del experimento, sin promoción.
La iteración 1 tiene cuatro ventanas adquiridas, pero comparación inválida por Triple-Play incompleto.
Stage1837A aporta dos holdouts rechazados. Sus decisiones de ronda siguen pendientes de revisión independiente en la fuente.
Las métricas se cotejan también en `rounds[].summary.B`; los campos sin cotejo disponible se enumeran como no verificados.
Stage1656A solo midió A1 y falló antes del candidato: no es un descarte de candidato en ventana única.
Stage1860A registra descarte pareado sin holdout; las cuatro clases solicitadas no incluyen ese caso.
Las observaciones ambientales WA/XC/LTU no establecen mejora causal ni pase pareado.
Los preflights bloqueados, los baselines sin enlace exacto y la fuente ausente quedan visibles.
La ausencia de filas `SIMPY_OFFLINE_ONLY` en esta captura no demuestra ausencia de simulaciones en el proyecto.

## Verificación y límites

Stage1887A registra ingestión y lectura posterior en MemoryMaster, scope `project:futuramax`.
Stage1888A conserva pytest, XML, log, código de salida y hashes vinculados a cada intento.
El primer intento tuvo 36 pases y un fallo por un recibo primario publicado concurrentemente; sus entradas están archivadas.
La reparación fija el catálogo de fuentes para reproducir la misma captura aunque aparezcan recibos posteriores.
La revisión final exige recalcular también las etiquetas ACCEPT/REJECT del snapshot y prueba el rechazo de una etiqueta adulterada.
La suite bloquea conexiones de red y prueba evidencia contradictoria, ambigüedad, cambios de hash y métricas alteradas.
Stage1889A valida integridad local, cinco pilares declarados con su alcance real, privacidad y contrato documental.
La cobertura de las cuatro clases es un criterio separado: las 44 filas sin clase impiden cierre completo.
El estado esperado con integridad válida es `BLOCKED_CLASSIFICATION_GAPS`, no un PASS de hardware.
Los recibos históricos y los gates auditados se conservan intactos; solo se generan productos de esta auditoría.
La evidencia física nueva, la promoción, la reparación de gates históricos y la aceptación de producción siguen `NOT_ESTABLISHED`.

Artefactos principales: `stage1884a_historical_gate_band_pin_audit_receipt.json`,
`stage1885a_live_vs_sim_champion_evidence_ledger_receipt.json` y `stage1889a_wave141_astra6_gate.json`.
