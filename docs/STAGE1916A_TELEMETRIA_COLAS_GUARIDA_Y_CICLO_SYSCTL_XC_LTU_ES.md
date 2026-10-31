<!-- doc-head: Wave 146 (1914A-1919A) carril 3. Telemetria read-only de colas en Guarida: Panel3 .83 (3 ventanas de 10 s, descarte presente siempre con intensidad variable), Panel1 .84 (3 CPEs sanos) y linea base de Panel2 .82 (7 de 22 CPEs, CPU 95 por ciento). Hallazgo clave: el contador 'no tx buffer' avanza igual que 'xmit_filtered', asi que la etiqueta no prueba agotamiento de buffer (corrige la lectura de la Wave 130). Mas un ciclo finito de 3 iteraciones con sysctls de red Linux reversibles en RAM en XC .198/.253 y LTU .110. Leer antes de tocar colas en Guarida. -->

# Stage 1916A: telemetria de colas en Guarida y ciclo sysctl XC/LTU

## 1. Alcance y seguridad

Carril 3, hardware real. Los AP de produccion `.84` (Panel1), `.83` (Panel3) y ahora `.82`
(Panel2) son solo-lectura: la guarda `assert_read_only` rechaza cualquier token de escritura antes
de abrir el socket. En los radios de banco `.198`, `.253` y `.110` solo se escribieron sysctls en
RAM bajo watchdog de 60 s en el equipo, con relectura final del valor original. Cero Flash, cero
RF, cero cambio de canal, cero GPIO, cero atpc, cero knobs PROTECTED. CPEs por octeto de IP.

## 2. Panel3 .83: el descarte esta siempre, la intensidad varia (1914A)

Tres ventanas contiguas de 10 s en una sola sesion con pausas en el propio equipo:

| Ventana | Enviadas | no tx buffer | Tasa | demasiados reintentos |
| :-- | :-- | :-- | :-- | :-- |
| W1 | 130 559 | 2 513 | 1,93 % | 63 |
| W2 | 25 731 | 1 845 | 7,17 % | 40 |
| W3 | 42 970 | 2 284 | 5,32 % | 6 |

La etiqueta automatica da RAFAGA (max/min mayor a 3,0), mientras que la Wave 130 dio CONTINUO
con tasas de 1,82 a 3,33 %. Como el corte de 3,0 es fijo, el dato estable es otro: en las 6
ventanas de 1818A y 1914A el descarte aparecio siempre, con tasas entre 1,8 y 7,2 %. Los sysctls
de cola no cambiaron entre capturas.

## 3. Semantica del contador: no prueba agotamiento de buffer

En cada ventana medida, 'no tx buffer' y `xmit_filtered` avanzaron exactamente lo mismo (Panel3:
2513/2513, 1845/1845, 2284/2284; Panel2: 15592/15592). El driver anota un mismo evento con los
dos nombres. Por eso la etiqueta sola no demuestra falta de memoria: pueden ser tramas filtradas,
por ejemplo hacia una estacion en ahorro de energia o en estado filtrado. Esto corrige la lectura
de la Wave 130, que hablaba de agotamiento sostenido. La causa real sigue abierta y requiere RE del
origen de athstats o del driver.

## 4. Panel1 .84: los 3 CPEs siguen sanos

cpe_41 MCS7 a -49 dBm, cpe_223 MCS8 a -48 dBm, cpe_80 MCS7 a -58 dBm, los tres NSS2, puerto de
bridge en forwarding, multicast_to_unicast activo. En 3 ventanas los fallos por paquete fueron 0 y
los reintentos por paquete no pasaron de 0,017.

## 5. Panel2 .82: linea base read-only

LiteAP AC en 5805 MHz, 20 MHz, firmware WA 8.7.25. Asociados 7 de los 22 CPEs esperados, CPU del
AP en 95 % y airtime 17,3 %. En una ventana de 10 s la tasa de 'no tx buffer' fue 2,02 %. El
cociente desde el arranque da 36,5 %, pero usa contadores de 32 bits que pueden haber dado la
vuelta en 7 dias de uptime, asi que se toma la ventana como dato valido. Los 15 CPEs ausentes no
se pueden nombrar desde el AP.

## 6. Ciclo finito de 3 iteraciones (1915A, STOP_MAX_ITERATIONS)

Procedencia: 1789A no aprobo ningun knob SAFE_RAM y 1758A/1759A solo trazan knobs del LTU, asi que
el ciclo usa sysctls genericos de la pila de red Linux de cada radio, nunca un knob del catalogo.

| Iter | Radio | Knob | Base -> B -> final | goodput cpe_41 | p95 | fmx_loss | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 | net.core.rmem_default | 131072 -> 163840 -> 131072 | 0,82 Mbps | 19,2 ms | 0,728 | keep |
| 2 | .253 | net.core.optmem_max | 10240 -> 20480 -> 10240 | 0,60 Mbps | 19,5 ms | 0,715 | keep |
| 3 | .110 | net.ipv4.tcp_fin_timeout | 60 -> 30 -> 60 | 1,35 Mbps | 11,9 ms | 0,604 | keep |

Las tres escrituras tomaron efecto y la relectura final devolvio el valor original. Estos sysctls
gobiernan los sockets de gestion de cada radio, no el camino de datos en bridge, asi que no se
espera ni se afirma efecto en el aire. La mejora de fmx_loss refleja la variacion del trafico
ambiente del enlace `.84` medido en paralelo, no al knob. cpe_80 se mantuvo en MCS7 sin perdida.

## 7. results.tsv

Se agregaron 3 filas finitas `s1915a_iter1_198`, `s1915a_iter2_253` y `s1915a_iter3_110`. Las
filas de waves anteriores quedaron intactas y el encabezado sigue siendo unico.

## 8. Verificacion

1914A pasa la auditoria estricta de 5 pilares y 1915A pasa
`enforce_5pillar_research_gate.py --require-live-hardware` sin senales de juego. Pilar E: claims
FMX-1914A y FMX-1915A en MemoryMaster. La suite `tests/test_stage1914a_to_1919a_suite.py` y el
gate `tools/verify/verify_stage1919a_wave146_opus1_gate.py` los escribieron dos workers codex
gpt-6-astra en paralelo; el carril los reviso y los corrio antes de reportar.

## 9. Limites

- Tres ventanas de 10 s describen este momento; falta una serie larga para el patron diario.
- Panel2 tiene una sola ventana; su cociente desde el arranque es solo referencia.
- Que anota el driver bajo 'no tx buffer' no se resuelve con contadores; requiere RE.
- Los radios de banco no tienen par aire; el ciclo prueba escritura y restauracion seguras.
- El ciclo cerro por STOP_MAX_ITERATIONS, no por alcanzar un objetivo.
