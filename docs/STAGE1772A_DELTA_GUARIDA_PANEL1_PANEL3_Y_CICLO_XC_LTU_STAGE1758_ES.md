<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 122 (1770A-1775A) carril 3. Delta read-only de Guarida: Panel1 .84 (cpe_41, cpe_223, cpe_80 siguen en VHT-MCS7/8 con bridge en forwarding y multicast_to_unicast) y Panel3 .83 (ningun CPE offline se sumo; contadores athstats en 11 s). Ciclo finito 3 iteraciones A1-B1-A2-B2 (STOP_MAX_ITERATIONS) con knobs queue/sysctl reversibles en RAM y watchdog 60s en XC .198/.253 y LTU .110 (RF apagada), mas OTA read-only en .84. Solo el knob de LTU traza a Stage 1758A. -->

# Stage 1772A: delta de Guarida Panel1/Panel3 y ciclo XC/LTU con knobs de Stage 1758A

## 1. Alcance y seguridad

Carril 3, hardware real, sin simulacion. Los AP de produccion `198.18.0.7` (Panel1) y
`198.18.0.6` (Panel3) son solo-lectura: la guarda `assert_read_only` rechaza antes de abrir el
socket cualquier `uci set`, `iw ... set`, `tc` de cambio, `wifi`, redireccion a archivo o
reinicio de servicio. En los radios de banco `.198`, `.253` y `.110` solo se escriben knobs en RAM,
con un watchdog de 60 s en el propio equipo que restaura el valor aunque se caiga la sesion. Cero
escrituras a Flash, cero arranque de RF, cero cambio de canal, cero GPIO, cero atpc. Las
estaciones se nombran solo por octeto de IP (cpe_41, cpe_223, cpe_80; cpe_9, cpe_235, cpe_238).

## 2. Panel1 .84: los 3 CPEs se mantienen (1770A)

| Estacion | TX phy | MCS / NSS | brport | multicast_to_unicast |
| :-- | :-- | :-- | :-- | :-- |
| cpe_41  | 144,4 Mbps | 7 / 2 | 3 (forwarding) | 1 |
| cpe_223 | 173,3 Mbps | 8 / 2 | 3 (forwarding) | 1 |
| cpe_80  | 144,4 Mbps | 7 / 2 | 3 (forwarding) | 1 |

Los tres siguen en VHT-MCS7/8 con dos flujos y con su puerto de bridge en forwarding y
multicast_to_unicast activo. cpe_80 sigue recuperado: en las tres iteraciones de 1771A se midio en
MCS7 con 0 por ciento de perdida ICMP.

## 3. Panel3 .83: delta de membresia y contadores (1770A)

Dos capturas de `wstalist` y `athstats` separadas 11 s, comparadas entre si y contra la base de
Stage 1722A. Asociados ahora: cpe_9, cpe_235 y cpe_238, los mismos tres de 1722A. Ninguno de los 3
CPEs que faltan se sumo y ninguno se fue; siguen 3 offline de los 6 esperados. Como la identidad
sale del ultimo octeto de la IP en `wstalist`, los 3 offline no se pueden nombrar hasta que
asocien.

Contadores que cambiaron en la ventana de 11 s:

| Contador athstats | Delta |
| :-- | :-- |
| paquetes enviados | 77 314 |
| tx fallidos por falta de buffer (datos) | 2 975 |
| tx fallidos por demasiados reintentos | 97 |
| interrupciones de beacon miss | 3 077 |

Observacion, no diagnostico: cerca del 3,8 por ciento de lo enviado en la ventana fallo por falta
de buffer de transmision, lo que sugiere picos de cola en el AP. Conviene repetir la medicion en
varias ventanas antes de sacar conclusiones o tocar la configuracion de Panel3.

## 4. Ciclo finito de 3 iteraciones (1771A, STOP_MAX_ITERATIONS)

Cada iteracion aplica un knob en RAM en orden A1-B1-A2-B2 bajo watchdog de 60 s y, en la misma
iteracion, mide 4 ventanas OTA solo-lectura en `.84` (A = cpe_41, B = cpe_223, mas cpe_80). Tras
la ultima fase se relee el knob para confirmar la restauracion completa.

| Iter | Radio | Knob | Clase | Base -> B -> final | Origen | goodput cpe_41 | p95 | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 | ath0 tx_queue_len | queue | 1000 -> 500 -> 1000 | Linux netdev | 8,54 Mbps | 24,2 ms | keep |
| 2 | .253 | net.core.dev_weight | sysctl | 96 -> 64 -> 96 | Linux NAPI | 6,09 Mbps | 17,8 ms | keep |
| 3 | .110 | ame_core sched_max_agg_cnt | queue | 8 -> 4 -> 8 | Stage 1758A | 0,89 Mbps | 14,7 ms | keep |

Sobre la reconciliacion con 1758A/1759A: ambos receipts son estaticos y solo de LTU. 1758A mapea la
superficie de planificacion de `ame_core.ko` (sched, agg, slot) y confirma que `eab_driver.ko` no
existe en LTU; 1759A cruza nombres del catalogo y aclara que eso no es un mapeo de control. Por eso
solo la iteracion 3 traza a 1758A; los knobs de XC vienen de la superficie generica de Linux. Con
la RF de `.110` apagada, `sched_max_agg_cnt` no tiene efecto en el aire: el ciclo prueba escritura
y restauracion seguras, no una mejora de LTU.

El goodput es trafico ambiente de los abonados medido con los contadores del AP, no una carga
inyectada; lo util es RTT, jitter, perdida y RSSI. Los radios de banco no tienen par aire.

## 5. results.tsv

Se agregaron 3 filas finitas: `s1771a_iter1_198`, `s1771a_iter2_253` y `s1771a_iter3_110`, en el
dominio D3, con motivo de parada STOP_MAX_ITERATIONS. Las filas de waves anteriores quedaron
intactas y el encabezado sigue siendo unico.

## 6. Verificacion

El gate `enforce_5pillar_research_gate.py --require-live-hardware` pasa en 1771A sin problemas ni
senales de juego, y la auditoria estricta de 5 pilares pasa en 1770A. Pilares: A catalogo de
knobs y superficie `ame_core` de 1758A; B reactor cerrado contra la base 1722A; C rondas
contrabalanceadas con watchdog de 60 s; D deltas de contadores y p95 por iteracion; E claims
FMX-1770A y FMX-1771A en MemoryMaster. La suite `tests/test_stage1770a_to_1775a_suite.py` y el gate
`tools/verify/verify_stage1775a_wave122_opus1_gate.py` los escribieron dos workers codex
gpt-6-astra en paralelo; el carril los reviso y los corrio antes de reportar.

## 7. Limites

- Todo el estado de los CPEs se lee desde el AP; no se entro a ningun CPE de abonado.
- Los 3 CPEs offline de Panel3 no tienen identidad hasta que asocien.
- El delta de athstats cubre una sola ventana de 11 s.
- El ciclo cerro por STOP_MAX_ITERATIONS, no por alcanzar un objetivo de goodput.
