<!-- doc-head: Wave 284 (2736A-2741A) nota 670 ES: validacion SMP del LTU-Lite .110 (Wave 276) y frente Pareto de Panel3 (Wave 266, solo modelo) -->
LTU-Lite .110 (2688A): la ronda 2 A1->B1->A2->B2 bajo la brecha de ocupacion CPU0/CPU1 un 75.31% en ambiente, con restauracion a los ~60s y 0 escrituras; es balance de CPU en reposo, no caudal.
CPE .80 (2689A): paridad MAC exacta (etiquetas HMAC) confirma que es una de las 3 estaciones del AP OpenWrt Panel1 .84 - antes era inferido.
Panel3 (2622A): frente Pareto SimPy+pymoo SOLO MODELO; el frente favorece fq_limit >= 2048 sobre la base 512; pick robusto rts 1024 / coverage class 1 / fq_limit 2048 con -57.89% modelado.
Wave offline: la meta scholar de D6 no se cumple; 3 hipotesis encoladas. Tablero :8787 banda 1536A..2741A HTTP 200.
<!-- /doc-head -->
# Reporte ejecutivo - Nota #670: SMP del LTU-Lite y Pareto de Panel3

**Wave 284 - Etapas 2736A-2741A - 2026-10-28 - 100% offline, lectura de artefactos locales; ningun equipo tocado.**

## Que se hizo

Se documentaron en la nota evergreen #670 dos resultados ya verificados por otras lanes: el ciclo SMP del LTU-Lite .110
(Wave 276) y el frente Pareto de Panel3 (Wave 266). Se encolaron 3 hipotesis, se escribio la nota y se corrieron
`hyperresearch sync` e `hyperresearch index build` (rc 0).

Aclaracion del pedido: cita STAGE2690A y STAGE2624A; los recibos reales son 2688A y 2689A (Wave 276) y 2622A (Wave 266).

## Wave 276 (2688A): ciclo SMP del LTU-Lite .110 (otra lane, en vivo, restaurado)

- La ronda 2 de un ciclo A1->B1->A2->B2 en RAM bajo la brecha de ocupacion CPU0/CPU1 un **75.31%**; las cuatro fases
  corrieron ~60 s, expiraron y se restauraron solas (todas verificadas), con todos los valores finales restaurados. 0
  escrituras de radio, 0 de flash, 0 lecturas o escrituras de /dev/ame. El guardia que fallo en la Wave 270 ya funciono.
- Alcance honesto: la medicion es la **brecha de CPU en reposo**; no se genero carga (sin goodput, sin afirmacion causal
  de RF). El 75.31% no es un resultado de caudal ni de latencia. El proximo paso es una prueba con carga.

## Wave 276 (2689A): dos de nuestras hipotesis encoladas, ejecutadas en solo lectura (otra lane)

- **W271-H1 confirmada**: el CPE .80 stock airOS 8 (WA.v8.7.25) tiene paridad MAC exacta con una de las 3 estaciones
  asociadas al AP OpenWrt Panel1 .84 (etiquetas HMAC, solo lectura). En la Wave 271 era una inferencia; ahora esta
  confirmada como identidad de asociacion (no es aceptacion de plano de datos). Panel1 es una celda hibrida confirmada.
- **W275-H2 ejecutada**: un muestreo a 1 Hz de la vista aqm de Panel3 durante ~32 s (30 muestras) dio delta de
  fq_overmemory 0; el mapeo exacto de memoria del contador sigue sin verificarse (como en la nota #667).

## Wave 266 (2622A): Pareto de Panel3 RTS x coverage class x fq_limit (SOLO MODELO)

- Busqueda SimPy + pymoo NSGA-II; clase de evidencia SIMULATED_MODEL_ONLY, 0 equipos tocados: son salidas de modelo, no
  medidas. Panel3: 210 configs, 105 factibles, frente Pareto real de 21 miembros, recall NSGA 1.0 contra la grilla
  exhaustiva. Todo el frente usa fq_limit >= 2048 (la base es 512).
- Pick robusto del escenario consistente: rts_threshold 1024, coverage class 1, fq_limit 2048, con una reduccion modelada
  del tx_failed del CPE lejano del 57.89% y 0 descartes fq. El contrato D3_live del propio recibo sigue sin cumplirse
  offline (necesita el admitter de Panel3 corriendo y un delta medido). El modelo recomienda, no promociona.

## D6 / D7 en esta wave

- Offline, sin llamada a scholar: la meta scholar de D6 **no se cumple** (0), como en las Waves 263 y 271. D7 (sync del
  vault rc 0, 0 PII) se cumple. 3 hipotesis encoladas (QUEUED_UNTESTED): W284-H1 (banco, con permiso: IRQ del .110 cpu1
  -> cpu0 bajo carga real; reemplaza a W278-H2), W284-H2 (banco, con permiso: validar en Panel3 el pick del modelo rts
  1024 / fq_limit 2048 vs la base 512), W284-H3 (solo lectura: airtime del .80 hibrido vs los dos CPE OpenWrt).

## Etapas 2737A a 2741A

- 2737A: tablero hasta 2741 con los recibos de las Waves 266, 276 y 284 en el feed; SOLO se verificaron limpias (sin
  IP/MAC/nombres) las 3 tarjetas nuevas y las 2 secciones nombradas, con HTTP 200. 2738A: este documento y la linea final de
  CURRENT_STATE.md; 2739A: MemoryMaster y filas CRLF; 2740A: pruebas; 2741A: gate.

## Limites y advertencias (honestas)

- **Sin campeon** y sin medicion nueva en esta wave; no se abrio ningun binario ni se uso la red.
- Verificacion en navegador real: NO realizada; se verifico por CLI con HTTP 200, banda servida y conteos de PII.
- PII (honesto): el tablero COMPLETO (feed 1536A..2741A y telemetria) todavia muestra IP, MAC y nombres de abonados
  reales en claro; _leaks sobre la pagina entera da [full IP, MAC address, radiography subscriber name]. Es solo localhost
  (127.0.0.1) y el escaner de apellidos no detecta todos los nombres. Este salto de banda 2705->2741 no agrego ninguna
  tarjeta con fuga nueva. Depurar el tablero entero es decision del operador, fuera del alcance de esta wave.

Recibos: `stage2736a_note670_ltu_smp_and_panel3_pareto_receipt.json`, `stage2737a_command_center_1536a_2741a_refresh_receipt.json`,
`stage2739a_memorymaster_ingest_receipt.json`, `stage2741a_wave284_opus2_gate.json`.
