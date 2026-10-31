<!-- doc-head: Wave 85 (1548A-1553A) carril 3. Telemetria fisica real: LTU .110, XC .198/.253 (ubnt_poll noack_mode en RAM con watchdog 60s), y Panel1-Guarida .84 solo-lectura (A1-B1-A2-B2 hacia 3 CPEs reales). Hallazgos: cpe_80 degradado, .200.91 ausente, fila simulada corregida en results.tsv, plan Panel3 6-CPE con compuertas. Leer antes de tocar Panel3 o el bench LTU/XC. -->

# Stage 1550A: telemetria viva de Guarida Panel1, plan Panel3 6-CPE y bench LTU/XC

## 1. Alcance y seguridad

Carril 3, hardware real, cero red simulada. Tres radios de banco (`.110` LTU-Lite, `.198`
Rocket Prism 5AC Gen2, `.253` Rocket 2AC Prism) y el AP de produccion `.84` (Panel1-Guarida,
LiteAP ac, OpenWrt 24.10.4). Sobre `.84` todo fue solo-lectura: la guarda
`stage1548_1549_live_common.assert_read_only` rechaza antes de abrir socket cualquier `uci set`,
`iw ... set`, `tc` de cambio, `wifi`, redireccion a archivo o reinicio de servicio. Cero
escrituras a Flash, cero arranque de RF, cero reinicio de `ame_drv`. Las escrituras en RAM a
`.198`/`.253` se hicieron bajo un watchdog de 60 s en el propio equipo y se verificaron
restauradas. Los nombres de abonado y las coordenadas GPS se redactan en origen; las estaciones
se rotulan solo por octeto de IP (`cpe_41`, `cpe_223`, `cpe_80`, `cpe_200_91`).

## 2. Panel1-Guarida .84 vivo (1549A, solo-lectura)

AP en canal 48 (5240 MHz, 20 MHz), ruido -109 dBm. Perfil de cola AQL por AC medido en vivo y
coincidente con el documentado: VO 300/600, VI 1000/2000, BE 1500/3000 us; `aql_threshold` 4000
us; contabilidad de airtime por estacion activa (`AIRTIME_TX`). El AP reporta solo airtime de TX
(rx duration 0). El equipo no tiene binario `tc`.

Tres CPEs asociados y un hallazgo real importante:

| Estacion | TX phy | MCS | RSSI | ICMP perdida | Lectura |
| :-- | :-- | :-- | :-- | :-- | :-- |
| cpe_41  | 144,4 Mbps | 7 | -50,5 dBm | 0 % | sano |
| cpe_223 | 173,3 Mbps | 8 | -48,5 dBm | 0 % | sano |
| cpe_80  | 6,5 Mbps | 0 | -52 dBm | 100 % | degradado del lado del cliente |

`cpe_80` cayo de 144,4 Mbps (213A) a 6,5 Mbps MCS0, con 16 % de tramas TX fallidas y 100 % de
perdida ICMP en una de las ventanas. Es una degradacion real del enlace del abonado; esta etapa
es solo-lectura y no se tomo ninguna accion. `cpe_200_91` (el cuarto CPE pendiente) no aparece en
la tabla de estaciones y no responde ping: sigue sin asociar.

El AP reinicio hace unas 6 horas (uptime 5,9 h), por lo que el soak de 72 h que 580A exige antes
de Panel3 vuelve a empezar de cero.

## 3. Bench LTU/XC .110/.198/.253 (1548A, telemetria fisica)

- `.110` LTU-Lite: AP-PtMP con `ptmp_max_cpe=4` ya puesto, RF en reposo, 0 CPE asociado. El
  tratamiento SQ (4) contra 64 necesita un CPE asociado y un ASIC arrancable con temperatura
  verificada; no se cumplen, asi que no se aplico (crash honesto, sin encender RF). Se leyeron
  en 4 ventanas contrabalanceadas los parametros de `ame_core`, procfs, CPU y softirq.
- `.253` (Rocket 2AC Prism, sysid 0xe2f2) y `.198` (Rocket Prism 5AC Gen2, sysid 0xe7e9): control
  A1-B1-A2-B2 de `noack_mode` (ubnt_poll, `/proc/sys/dev/uph_wifi0/noack_mode`) en RAM. Cada
  comando guardado capturo su propio valor, escribio B (la relectura confirma que la escritura
  tomo efecto) y restauro ese valor bajo el watchdog de 60 s. Hallazgo: `noack_mode` es un knob
  gestionado por el firmware que varia entre lecturas por si solo (en `.253` se observo 0 y 1 sin
  intervencion), por lo que no hay una linea base fija. Sin par over-the-air no se produce
  goodput en estos radios.

## 4. Medicion OTA real sobre .84 (A1-B1-A2-B2)

Sin inyeccion de trafico. El goodput sale de los contadores `tx_bytes` del propio AP por ventana
(trafico ambiente del abonado) y el RTT/jitter de ICMP desde el AP hacia cada CPE. Esquema
contrabalanceado A = cpe_41, B = cpe_223:

| Fila (results.tsv) | goodput | p50 | p95 | jitter | perdida | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| s1548a_g84_cpe41_real  | 0,02 Mbps | 1,62 ms | 19,0 ms | 7,3 ms | 0 % | keep |
| s1548a_g84_cpe223_real | 0,62 Mbps | 2,02 ms | 21,5 ms | 9,6 ms | 0 % | discard |
| s1548a_g84_cpe80_real  | 0,01 Mbps | sin respuesta | sin respuesta | sin respuesta | 100 % | crash |

El goodput es bajo porque es trafico ambiente, no una carga Triple-Play inyectada; la relevancia
esta en RTT, jitter, perdida y RSSI reales. `cpe_80` da crash medido (MCS0, 100 % de perdida), no
simulado.

## 5. Correccion de results.tsv

La fila `baseline_guarida` (114,60 Mbps, 2,3 ms) era un valor simulado del pick balanceado de
1512A marcado como campeon vivo. Se elimino y se reemplazo por las tres filas reales medidas
arriba. Las filas de otros carriles (D1/D2/D3, waves 83/84/91) no se tocaron y el encabezado
sigue siendo unico.

## 6. Plan de migracion Panel3-Guarida (6 CPE)

Veredicto go/no-go: NO_GO hoy. Compuertas evaluadas contra evidencia viva y modelo 1513A:

| Compuerta | Estado | Motivo |
| :-- | :-- | :-- |
| G1 soak Panel1 72 h | FAIL | AP reinicio hace 5,9 h |
| G2 enlaces Panel1 sanos | FAIL | cpe_80 degradado |
| G3 contabilidad airtime | PASS | AIRTIME_TX activo |
| G4 perfil AQL | PASS | VO 300/600, VI 1000/2000, BE 1500/3000 us |
| G5 inventario Panel3 | FAIL | 243A midio 3 de 6 CPE |
| G6 watchdog armable | FAIL | 1513A fsm_armable_now false |
| G7 go del operador | PENDING | no dado en esta wave |

El receipt 1549A incluye el runbook de 7 pasos (T-24h a T+72h) con una condicion de aborto por
paso: snapshot solo-lectura del AP `.83` y sus 6 CPE, ensayo en banco con un LiteBeam 5AC y uno
LR en WDS, export de config y imagen stock para rollback, armado del watchdog doble 60 s no-DFS /
120 s DFS, aplicacion del perfil de cola de Panel1, verificacion a T+10min y soak de 72 h.

## 7. Verificacion

`tests/test_stage1548a_to_1553a_suite.py` reparsea los receipts contra sus capturas crudas, prueba
la guarda solo-lectura, la anonimizacion (ningun apellido sobrevive) y la correccion de
results.tsv. El gate `tools/verify/enforce_5pillar_research_gate.py ... --require-live-hardware`
pasa en 1548A de forma honesta (evidence_class LIVE_HARDWARE, 0 gamed_signals). Pilares: A knobs
s017/s020/s029/s032/s040 (ubnt_poll_host.ko, captura .198); B reactor cerrado; C A1-B1-A2-B2 con
watchdog 60 s; D comparacion pareada de p95; E claim FMX-1548A en MemoryMaster. Skills K-Dense
(statistical-analysis, karpathy-autoresearch) citadas desde su SKILL.md, no descargadas.

## 8. Limites

- Ningun radio de banco tiene par OTA; su goodput no se mide. Los numeros OTA vienen del enlace
  vivo `.84` a sus CPE reales.
- El goodput de `.84` es trafico ambiente del abonado, no una carga Triple-Play inyectada.
- `cpe_80` esta degradado del lado del cliente; hace falta una visita o accion fuera de esta wave.
- La RF de `.110` no se encendio a proposito, asi que el tratamiento SQ contra 64 queda pendiente.
- El histograma de MCS no esta expuesto en este AP; solo la ultima tasa TX/RX por estacion.
