<!-- doc-head: Wave 100 (1638A-1640A) sintesis ES: feed del Command Center :8787 ampliado a 1536A..1650A con LITBASE Xtensa 0x009bb000 (binario estatico, stage1591A/1632A) y el sweet-spot WMM BE=1200/2400us (live, p95=4.189ms, 99.56% TCP, fmx_loss=0.6494405), nota #621, scholar honesto 0/3 este wave + EDCA reusado de Wave 94, y las discrepancias del prompt corregidas contra las fuentes primarias -->
# Reporte ejecutivo - Sweet-spot WMM (4.19 ms), LITBASE Xtensa y nota #621

**Wave 100 - Etapas 1638A-1640A - 2026-10-27 - 100% offline (0 SSH, 0 escritura a radios).**

## Que se hizo

Se amplio la banda del feed del Command Center :8787 de 1536A..1620A a 1536A..1650A y se agregaron dos
hallazgos de Wave 92/95 y Wave 93, cada uno con su clase de evidencia. Se ingreso la sintesis del
sweet-spot WMM y la ley de resolucion LITBASE como nota #621 (evergreen); el vault paso de 620 a 621.

## Etapa 1638A - banda 1650, LITBASE y sweet-spot

- **LITBASE Xtensa = 0x009bb000** (CONFIRMED_STATIC_BINARY): la pagina de literales absolutos se resuelve
  como `target = 0x009bb000 + (imm16 - 0x10000) * 4`. stage1591A ajusta esa pagina de forma unica
  (0x009bb000 con ~4326 aciertos en el pool) y stage1632A la registra con `"validated": true`.
- **Sweet-spot WMM** (CONFIRMED_LIVE_HARDWARE, stage1596A): VO=300/600, BE=1200/2400 us, DSCP EF/CS6 ->
  prioridad 262, con **p95=4.189 ms** y goodput **19.94 vs 20.03 Mbps (99.56% de capacidad TCP)**,
  fmx_loss=0.6494405. Es una medicion en vivo, no una promocion: el estado del recibo 1596A es
  PARTIAL_BLOCKED_FIRMWARE_CANARY (aceptacion fw2 no cumplida) y la fila keep dice "no production
  promotion".

Se sincronizaron `champion_state_ledger.json` y `agent_task_board.json`. Recibo
`artifacts/autoresearch/stage1638a_command_center_8787_wave83_93_95_live_sync.json`. Wave 83
(1536A/1537A) y Wave 92 (1590A/1591A) ya aparecen por inclusion de banda.

## Etapa 1639A - por que relajar BE recupera el caudal (nota #621)

Wave 91 habia puesto AC_BE en un presupuesto de airtime muy chico (600/1200 us) y perdio alrededor de
-11% TCP: un TXOP corto limita cuanto se puede agregar en un A-MPDU, asi que el overhead de PHY y ACK se
amortiza sobre menos tramas y baja el caudal. Relajar BE a 1200/2400 us le da lugar al agregado y
recupera el TCP al 99.56%; mantener AC_VO ajustado (300/600 us) deja la voz sin inanicion (EF p95=4.189
ms). El resultado es un punto optimo: casi toda la capacidad TCP sin sacrificar la latencia de cola de
voz.

- **recall-first (vault + MemoryMaster):** 6 de 6 consultas con aciertos (A-MPDU 13, airtime BE/VO 20,
  l32r 6, LITBASE 4, voz 3, TXOP 1). MemoryMaster aporto el crossover WMM/TCP-ACK (Round 19) y la
  sintesis EDCA de Wave 94 (nota #620).
- **scholar-mcp (jev-1.14.0, motor vivo P=0.91):** 0 de 3 principios verificados este wave (A-MPDU
  P=0.26, TXOP P=0.01, pool de literales Xtensa P=0.02): negativos honestos, no forzados. La priorizacion
  por categoria de acceso de EDCA se reusa por cita de Wave 94 (nota #620, P=0.97 en vivo), no se
  re-corrio. La ley LITBASE se apoya en la RE de binario estatico.

La sintesis se ingreso como **nota #621** (evergreen); el vault paso a 621 notas. Recibo
`artifacts/autoresearch/stage1639a_sweetspot_wmm_and_xtensa_litbase_note621.json`.

## Discrepancias del prompt corregidas contra las fuentes primarias (honesto)

El enunciado de Wave 100 cito datos que NO coinciden con los recibos; se registraron en el recibo 1638A
(`prompt_discrepancies`) y se usaron los valores reales, sin reconciliar en silencio:

- **fmx_loss=0.3357 (enunciado) -> 0.6494405 (real).** 0.3357 no coincide con ninguna fila de results.tsv
  ni recibo; la fila keep del sweet-spot (WAVE93_STAGE1596A_ITER3, gp 19.94, p95 4.189) es 0.6494405.
- **LITBASE citado en 1608A/1609A -> real en 1591A + 1632A.** 0x009bb000 no esta en 1608A/1609A (1608A es
  la refutacion de libubnt.so, 1609A son los callers l32r); esta en 1591A y 1632A.
- **"NEW CHAMPION keep" -> keep con "no production promotion" + 1596A PARTIAL_BLOCKED_FIRMWARE_CANARY.**
  La promocion queda como decision del operador.
- **Fila keep elegida:** el tablero muestra ITER3 (ultima keep, fmx 0.649) por orden y por designacion del
  enunciado; la keep ITER1 tiene fmx_loss mas bajo (0.405) pero peor p95 (4.60) - marcado, no resuelto.

## Etapa 1640A - reconstruccion y verificacion en vivo :8787

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero; el daemon :8787 (hot-reload
del operador) tomo el cambio. `curl http://127.0.0.1:8787/FUTURAMAX_COMMAND_CENTER.html` responde
**HTTP 200** y sirve el badge `RECIBOS 1536A-1650A`, el LITBASE `0x009bb000` y el item
`Sweet-Spot WMM p95 4.19ms` etiquetado `CONFIRMED_LIVE_HARDWARE`.

## Limites y advertencias (honestas)

- **Verificacion en navegador real: NO realizada** (Claude-in-Chrome no conecta, sin Playwright); se
  verifico por CLI (HTTP 200 + bytes servidos) y balance de etiquetas.
- El sweet-spot es una medicion en vivo con aceptacion fw2 PENDIENTE (canary) y sin promocion a
  produccion. La re-confirmacion A1->B1->A2->B2 y la aceptacion fw2 siguen pendientes.
- La ley LITBASE es binario estatico; el grounding scholar de los principios dio negativo honesto este
  wave (0/3), apoyado en el recall del vault.

## Que sigue (abierto, decision del operador)

- Confirmar de donde salio fmx_loss=0.3357 y decidir la promocion del sweet-spot tras re-test en vivo.
- Verificacion visual en navegador del feed ampliado.

Recibos: `stage1638a_command_center_8787_wave83_93_95_live_sync.json`,
`stage1639a_sweetspot_wmm_and_xtensa_litbase_note621.json`, `stage1643a_wave100_opus48_gate.json`.
