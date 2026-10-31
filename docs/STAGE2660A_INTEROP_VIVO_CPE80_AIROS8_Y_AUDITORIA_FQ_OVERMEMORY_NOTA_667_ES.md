<!-- doc-head: Wave 271 (2658A-2663A) nota 667 ES: CPE .80 en airOS 8 junto al AP OpenWrt .84 y auditoria del contador fq_overmemory exportado -->
CPE .80: airOS 8 WA.v8.7.25 confirmado; su asociacion al AP OpenWrt .84 es inferida, ningun recibo la liga a la tercera estacion.
fq_overmemory: plano todo el dia en Panel1; en Panel3 solo un minuto quieto, el contador siguio creciendo antes y despues.
Rotulos de debugfs invertidos en upstream segun 2628A; el mapeo del backport que corre no esta verificado, causa UNKNOWN.
D6 no se cumple: wave offline, ninguna llamada a scholar; 3 hipotesis encoladas. Tablero :8787 banda 1536A..2663A HTTP 200.
<!-- /doc-head -->
# Reporte ejecutivo - Nota #667: CPE .80 en airOS 8 y auditoria de fq_overmemory

**Wave 271 - Etapas 2658A-2663A - 2026-10-28 - 100% offline (esta wave no toco ningun equipo ni uso la red).**

## Que se hizo

Se escribio la nota evergreen #667 sobre los dos hallazgos de la Wave 267 (Etapas 2628A a 2633A, otra lane), leyendo
sus recibos y el historial de tools/observability/telemetry.db en modo solo lectura. Se corrieron `hyperresearch sync` e
`hyperresearch index build` (ambos devolvieron 0), el tablero :8787 se amplio a 1536A..2663A y se agrego una linea al
final de CURRENT_STATE.md.

Titular honesto: **dos de las tres afirmaciones del pedido quedan matizadas** y el contrato D6 no se cumple. Sin campeon.

## (A) CPE .80: airOS 8 junto al AP OpenWrt .84

- CONFIRMADO (lectura autenticada de 2628A): el CPE de Panel1 terminado en .80 responde WA.v8.7.25, plataforma no
  OpenWrt, 0 escrituras de radio. El demonio lo registra como OBSERVED_NON_OPENWRT y no lo cuenta como nodo OpenWrt.
- INFERIDO, no probado: que este asociado en vivo al AP OpenWrt .84. El AP muestra 3 estaciones asociadas (Wave 267 y
  2610A), la radiografia pone al .80 entre los tres CPE activos de Panel1 y los otros dos (.41, .223) son OpenWrt.
  Ningun recibo liga la tercera estacion al .80: los ids de estacion son anonimos y los sondeos RF usan link-local.
- Si se confirma, Panel1 es un caso hibrido en vivo (CPE airOS 8 sobre AP OpenWrt), justo lo que protege la regla del
  admitidor hibrido fijo (R01). En 2610A las tres estaciones de Panel1 tuvieron 0 % de perdida en las dos rondas.

## (B) Contador fq_overmemory exportado

- Ronda 1 de la Wave 267: sin muestra previa (delta nulo). Ronda 2: incremento cero en Panel1 (59,69 s) y en Panel3
  (59,65 s). **Un solo cero calculado por AP**, no dos rondas seguidas.
- Historial en telemetry.db de 14:23 a 15:34 UTC: Panel1 quedo en 4055 en las 48 muestras. Panel3 subio de 7020 a 9304,
  con deltas por minuto distintos de cero antes y despues de las rondas de la Wave 267 (166 a las 15:07; 117, 10 y 115
  entre 15:23 y 15:29); a las 15:38 iba en 9554. El cero de la ronda 2 fue un minuto quieto.
- En ambos AP el contador fq_overlimit exportado quedo en 0 y fq_limit en 512 en todas las muestras. El uso de memoria
  fq fue 0 en Panel1; en Panel3 fue distinto de cero en 27 de 48 muestras, con pico de 1080960 bytes, un tercio del
  limite de 3 MiB (una muestra por minuto: un pico corto se puede perder).

## (C) Rotulos invertidos y la hipotesis H3 de la Wave 268

- Segun la lectura de fuentes primarias de 2628A (urls y sha256 registrados; no se releyeron en esta wave offline), el
  debugfs de mac80211 en upstream imprime el campo interno overmemory bajo el rotulo fq_overlimit y el campo overlimit
  bajo fq_overmemory. Los AP corren kernel 6.6.110 con backports de mac80211 6.12.52-r1; el mapeo exacto en ese backport
  no esta verificado, asi que la causa queda UNKNOWN.
- Si el mapeo de upstream vale en los AP, lo que crece en Panel3 son descartes por el limite fq_limit de 512 y el
  contador de memoria es 0; el pico de memoria muestreado lejos del limite encaja con esa lectura sin probarla.
- La hipotesis W268-H3 leia el contador como presion de memoria: queda reemplazada (no editada) por W271-H2 y W271-H3.

## (D) Contrato D6 en esta wave

- Antes (cola del reactor): 9 claims verificados en vivo en bloques previos; las 3 hipotesis de la Wave 268 siguen sin
  probar. Despues: **0 claims verificados** (wave offline, ninguna llamada a scholar) y 3 hipotesis encoladas: meta no
  cumplida. El archivo del orquestador sigue mostrando D6 en la ronda 1 de 2 y registra la Wave 268 como CONFIRMED.
- W271-H1: ligar la tercera estacion de Panel1 al .80 por MAC de radio (solo lectura) y comparar su perdida y RTT con los
  dos CPE OpenWrt. Sin escrituras.
- W271-H2 (primero en banco, con permiso del operador): un cambio acotado de fq_memory_limit en RAM deberia mover el
  contador fq_overlimit exportado si los rotulos estan invertidos.
- W271-H3 (depende de H2): un cambio acotado de fq_limit en Panel3 baja el crecimiento del contador sin empeorar el RTT.

## Etapas 2659A a 2663A

- 2659A: tablero hasta 2663, HTTP 200, 0 apellidos y 0 alias en la pagina, secciones de orquestador y Antes/Despues sin
  IP ni MAC, y la tarjeta 2658A con su veredicto TARGET_NOT_MET.
- 2660A: este documento y la linea final de CURRENT_STATE.md (197 lineas).
- 2661A: dos claims en MemoryMaster y filas CRLF en results.tsv; 2662A: suite de pruebas; 2663A: gate.

## Aclaraciones del pedido

- El pedido dice que el .80 esta asociado en vivo al AP .84: es una inferencia, no un hallazgo de la Wave 267.
- El pedido dice cero en dos rondas seguidas: fue un cero calculado por AP, y Panel3 siguio creciendo.
- El pedido exige 100% offline y a la vez claims verificados por scholar: lo segundo necesita red.
- El nombre de la nota tiene 84 caracteres; hyperresearch corta el id del vault a 80.

## Limites y advertencias (honestas)

- **Sin campeon**, sin medicion nueva en esta wave; no se abrio ningun binario ni se uso la red.
- Verificacion en navegador real: NO realizada; se verifico por CLI con HTTP 200, banda servida y conteos de PII.

Recibos: `stage2658a_note667_cpe80_and_fq_overmemory_receipt.json`, `stage2659a_command_center_1536a_2663a_refresh_receipt.json`,
`stage2661a_memorymaster_ingest_receipt.json`, `stage2663a_wave271_opus2_gate.json`.
