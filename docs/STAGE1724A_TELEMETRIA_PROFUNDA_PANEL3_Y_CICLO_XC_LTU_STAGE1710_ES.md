<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 114 (1722A-1727A) carril 3. Auditoria read-only del healer y el bridge de Panel1-Guarida .84, telemetria profunda read-only de Panel3-Guarida .83 (wstalist, athstats, radio.1.*), y ciclo finito de 3 iteraciones A1-B1-A2-B2 (STOP_MAX_ITERATIONS) sobre los knobs seguros reconciliados en Stage 1710A/1711A (noack / queue / sysctl, evitando atpc y GPIO) en RAM con watchdog 60s y ventanas OTA read-only en .84. Leer antes de tocar Panel1/Panel3 o el banco LTU/XC. -->

# Stage 1724A: telemetria profunda de Panel3 y ciclo XC/LTU con knobs de Stage 1710A

## 1. Alcance y seguridad

Carril 3, hardware real, cero red simulada. Los dos AP de produccion `198.18.0.7` (Panel1) y
`198.18.0.6` (Panel3) se tratan como solo-lectura: la guarda `assert_read_only` rechaza antes
de abrir socket cualquier `uci set`, `iw ... set`, `tc` de cambio, `wifi`, redireccion a archivo
o reinicio de servicio. Las escrituras en RAM a los radios de banco `.198`/`.253`/`.110` se hacen
bajo un watchdog de 60 s en el propio equipo y se verifican restauradas. Cero escrituras a Flash,
cero arranque de RF, cero escritura de GPIO del front-end, cero toque del knob de potencia atpc.
Los nombres de abonado y las coordenadas GPS se redactan en origen; las estaciones se rotulan solo
por octeto de IP.

## 2. Healer y bridge de Panel1 .84 (1722A, solo-lectura)

El healer de 4addr no escribe un archivo de log en `/tmp`: su presencia ya quedo probada por la
entrada de crontab que corre `fmx_ap_4addr_peer_healer.sh` cada minuto y por los hotplug (1674A).
Lo que confirma el efecto es el bridge: los 3 puertos `phy0-ap0.sta1/2/3` estan en estado 3
(forwarding) con `multicast_to_unicast` activado. Los 3 CPEs siguen sanos en esta captura:

| Estacion | TX phy | MCS / NSS | brport | m2u |
| :-- | :-- | :-- | :-- | :-- |
| cpe_41  | 144,4 Mbps | 7 / 2 | forwarding | si |
| cpe_223 | 173,3 Mbps | 8 / 2 | forwarding | si |
| cpe_80  | 144,4 Mbps | 7 / 2 | forwarding | si |

## 3. Telemetria profunda de Panel3 .83 (1722A, solo-lectura)

`.83` es un LiteAP AC (airOS WA.ar934x 8.7.25, ap-ptmp-mixed) alcanzable solo-lectura con usuario
ubnt. Canal 5755 MHz, ancho 20 MHz, uso de CPU 47 por ciento. Se capturaron `wstalist`,
`athstats`, `iwconfig`, un tramo de `dmesg` y los parametros `radio.1.*` de `/tmp/system.cfg`
(incluye atpc, ampdu, ack distance, antenna gain). Hoy hay 3 de los 6 CPEs asociados (octetos 9,
235 y 238). athstats muestra contadores altos de beacon_miss, consistente con enlaces largos en el
sector. No se ejecuto ningun escaneo fuera de canal para no perturbar el AP de produccion; el SSH
de `.83` reintenta una vez en modo solo-lectura por ser ocasionalmente inestable.

## 4. Ciclo finito de 3 iteraciones (1723A, STOP_MAX_ITERATIONS)

Tres iteraciones contrabalanceadas A1-B1-A2-B2, cada una con un control en RAM de un knob seguro
reconciliado en Stage 1710A/1711A, bajo watchdog de 60 s, mas 4 ventanas OTA solo-lectura sobre
`.84` (A = cpe_41, B = cpe_223). Criterio de parada: STOP_MAX_ITERATIONS (3 de 3).

| Iter | Radio | Knob en RAM | Clase | Restaurado | goodput cpe_41 | p95 | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 Rocket Prism 5AC | noack_mode | noack | si | 6,30 Mbps | 27,9 ms | keep |
| 2 | .253 Rocket 2AC Prism | netdev_max_backlog | queue | si | 5,73 Mbps | 24,0 ms | keep |
| 3 | .110 LTU-Lite | netdev_budget | sysctl | si | 3,11 Mbps | 35,2 ms | discard |

Decisiones sobre los knobs:

- Se usaron solo las clases reconciliadas seguras en 1710A/1711A: `noack` (ubnt_poll
  noack_mode), `queue` (receive-queue `net.core.netdev_max_backlog`) y `sysctl`
  (`net.core.netdev_budget`). Cada escritura toma efecto (la relectura lo confirma) y se restaura
  al valor que cada comando capturo.
- Se evitaron a proposito el knob de potencia atpc (poner ceros baja la TX a 0 dBm) y la GPIO del
  AirPrism (sin interfaz sysfs segura; seria escribir registros crudos del front-end de RF).
- La RF de `.110` no se encendio; el knob de LTU es un sysctl reversible togglado y restaurado.

El goodput es trafico ambiente del abonado sobre `.84`, no una carga inyectada; el valor real esta
en RTT, jitter, perdida y RSSI. Los radios de banco no tienen par aire, por eso su goodput propio
no se mide.

## 5. results.tsv

Se registraron 3 filas finitas `s1723a_iter1_198`, `s1723a_iter2_253`, `s1723a_iter3_110` en el
dominio D3 con el motivo de parada STOP_MAX_ITERATIONS. Las filas reales de Wave 85 (D4
`s1548a_g84_*`), Wave 96 (`s1615a_iter*`) y Wave 106 (`s1675a_iter*`) quedaron intactas, con
encabezado unico.

## 6. Verificacion

`tests/test_stage1722a_to_1727a_suite.py` reparsea los receipts contra sus capturas crudas, prueba
la guarda solo-lectura en ambos AP de produccion, la anonimizacion y las 3 filas finitas. El gate
`enforce_5pillar_research_gate.py ... --require-live-hardware` pasa en 1723A de forma honesta (0
gamed_signals). Pilares: A knobs s017/s020/s029/s032/s040 reconciliados en 1710A/1711A; B reactor
cerrado; C 3 iteraciones A1-B1-A2-B2 con watchdog 60 s; D p95 por iteracion; E claim FMX-1723A en
MemoryMaster. Skills K-Dense citadas desde su SKILL.md. La suite y el gate de esta wave los genero
un worker codex gpt-6-astra en paralelo (autorizado por el operador con el override del guard
T-1407); su salida fue revisada y ejecutada por el carril antes de reportar.

## 7. Limites

- El estado de los CPEs y del bridge se lee desde el AP; no se inicio sesion en ningun CPE.
- Panel3 tiene 3 de 6 CPEs en linea ahora; el inventario completo depende de que asocien los otros.
- El healer no deja log en disco; su efecto se infiere del estado del bridge y de 1674A.
- Los radios de banco no tienen par aire; su goodput propio no se mide, el OTA viene de `.84`.
- El ciclo cerro por STOP_MAX_ITERATIONS, no por alcanzar un objetivo de goodput.
