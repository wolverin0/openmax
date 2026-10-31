<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 106 (1674A-1679A) carril 3. Verificacion read-only post-heal de Panel1-Guarida .84 (los 3 CPEs sanos, cpe_80 recuperado a VHT-MCS7 NSS2, healer 4addr/hotplug instalado), auditoria read-only de Panel3-Guarida .83, y ciclo finito de 3 iteraciones A1-B1-A2-B2 (STOP_MAX_ITERATIONS) sobre knobs no explorados de XC (ptp_xmit) y LTU (ame_core add_pm_dbg) en RAM con watchdog 60s, con ventanas OTA read-only en .84 sobre los 3 CPEs. Leer antes de tocar Panel1/Panel3 o el banco LTU/XC. -->

# Stage 1676A: verificacion post-heal de Panel1, auditoria Panel3 y ciclo finito XC/LTU

## 1. Alcance y seguridad

Carril 3, hardware real, cero red simulada. Los dos AP de produccion `198.18.0.7` (Panel1) y
`198.18.0.6` (Panel3) se tratan como solo-lectura: la guarda `assert_read_only` rechaza antes
de abrir socket cualquier `uci set`, `iw ... set`, `tc` de cambio, `wifi`, redireccion a archivo
o reinicio de servicio. Las escrituras en RAM a los radios de banco `.198`/`.253`/`.110` se hacen
bajo un watchdog de 60 s en el propio equipo y se verifican restauradas. Cero escrituras a Flash,
cero arranque de RF, cero escritura de GPIO del front-end, cero toque de knobs de potencia (atpc).
Nombres de abonado y coordenadas GPS se redactan en origen; las estaciones se rotulan solo por
octeto de IP.

## 2. Verificacion post-heal de Panel1 .84 (1674A, solo-lectura)

Los 3 CPEs OpenWrt estan sanos en esta captura: VHT-MCS7 NSS2 con 0 por ciento de perdida ICMP.

| Estacion | TX phy | MCS / NSS | RSSI | ICMP | estado |
| :-- | :-- | :-- | :-- | :-- | :-- |
| cpe_41  | 144,4 Mbps | 7 / 2 | -51 dBm | 0 % | sano |
| cpe_223 | 144,4 Mbps | 7 / 2 | -47 dBm | 0 % | sano |
| cpe_80  | 144,4 Mbps | 7 / 2 | -52 dBm | 0 % | recuperado |

cpe_80, que en Wave 96 estaba clavado en 6,5 Mbps MCS0 NSS1 con 25,2 por ciento de fallos, ahora
transmite a 144,4 Mbps MCS7 NSS2 con pocas tramas fallidas: el enlace de bajada se recupero. El
healer de 3 capas 4addr esta instalado y activo: hotplug `99-fmx-4addr-verify` y
`99-fmx-panel1-champion`, una entrada de crontab que corre `fmx_ap_4addr_peer_healer.sh` cada
minuto, y el script presente en el equipo. El estado se juzga desde el station dump del AP y el
ICMP de enlace local, sin iniciar sesion en ningun CPE del abonado. Nota: las tasas fluctuan; en
una lectura previa cpe_223 se vio momentaneamente en MCS3, lo que refuerza medir por ventanas y no
por una sola muestra.

## 3. Auditoria de Panel3 .83 (1674A, solo-lectura)

`.83` es un LiteAP AC (airOS WA.ar934x 8.7.25, SSID PUBLIC_TERM_0005, ap-ptmp-mixed), alcanzable
solo-lectura con usuario ubnt. Se capturo su canal, la scan-list configurada en `system.cfg` y el
station dump: hoy hay 3 de los 6 CPEs asociados. No se ejecuto ningun escaneo fuera de canal, para
no perturbar el AP de produccion. El SSH de `.83` es ocasionalmente inestable, por lo que la
captura reintenta una vez en modo solo-lectura.

## 4. Ciclo finito de 3 iteraciones (1675A, STOP_MAX_ITERATIONS)

Tres iteraciones contrabalanceadas A1-B1-A2-B2, cada una con un control en RAM de un knob no
explorado bajo watchdog de 60 s en un radio de banco, mas 4 ventanas OTA solo-lectura sobre `.84`
que miden los 3 CPEs activos (A = cpe_41, B = cpe_223, mas cpe_80). Criterio de parada:
STOP_MAX_ITERATIONS (3 de 3).

| Iter | Radio | Knob en RAM | Restaurado | goodput cpe_41 | p95 | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 Rocket Prism 5AC | ptp_xmit | si | 1,05 Mbps | 30,3 ms | keep |
| 2 | .253 Rocket 2AC Prism | ptp_xmit | si | 0,15 Mbps | 25,1 ms | keep |
| 3 | .110 LTU-Lite | add_pm_dbg | si | 1,28 Mbps | 29,3 ms | discard |

Decisiones sobre los knobs no explorados:

- XC ubnt_poll `ptp_xmit` (`/proc/sys/dev/uph_wifi0/ptp_xmit`): es un knob nuevo respecto de
  waves previas (antes solo se habia tocado noack_mode). La escritura toma efecto y se restaura al
  valor que cada comando capturo, bajo watchdog de 60 s. Se evito a proposito el knob de potencia
  atpc, porque escribir ceros en atpc baja la potencia de TX a 0 dBm.
- LTU ame_core `add_pm_dbg`: flag de depuracion reversible, togglado en RAM con la RF de `.110`
  apagada y restaurado. No se toco el front-end de RF ni el GPIO del AirPrism.

cpe_80 se mantuvo sano (MCS7, 0 por ciento de perdida) durante todo el ciclo, confirmando la
estabilidad del heal. El goodput es bajo porque es trafico ambiente del abonado sobre `.84`, no
una carga inyectada; el valor real esta en RTT, jitter, perdida y RSSI. Los radios de banco no
tienen par aire, por eso su goodput propio no se mide.

## 5. results.tsv

Se registraron 3 filas finitas `s1675a_iter1_198`, `s1675a_iter2_253`, `s1675a_iter3_110` en el
dominio D3 con el motivo de parada STOP_MAX_ITERATIONS. Las filas reales de Wave 85 (D4
`s1548a_g84_*`) y las de Wave 96 (`s1615a_iter*`) quedaron intactas, con encabezado unico.

## 6. Verificacion

`tests/test_stage1674a_to_1679a_suite.py` reparsea los receipts contra sus capturas crudas, prueba
la guarda solo-lectura en ambos AP de produccion, la anonimizacion y las 3 filas finitas. El gate
`enforce_5pillar_research_gate.py ... --require-live-hardware` pasa en 1675A de forma honesta (0
gamed_signals). Pilares: A knobs s017/s020/s029/s032/s040; B reactor cerrado; C 3 iteraciones
A1-B1-A2-B2 con watchdog 60 s; D p95 por iteracion; E claim FMX-1675A en MemoryMaster. Skills
K-Dense citadas desde su SKILL.md.

## 7. Limites

- El estado de los CPEs se juzga desde el AP; no se inicio sesion en ningun CPE del abonado.
- Panel3 tiene 3 de 6 CPEs en linea ahora; el inventario completo depende de que asocien los otros.
- Los radios de banco no tienen par aire; su goodput propio no se mide, el OTA viene de `.84`.
- Las tasas por estacion fluctuan entre lecturas; por eso se mide por ventanas contrabalanceadas.
- El ciclo cerro por STOP_MAX_ITERATIONS, no por alcanzar un objetivo de goodput.
