<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 96 (1614A-1619A) carril 3, cierre finito D3/D4. Diagnostico read-only de cpe_80 en Panel1 .84, inventario vivo read-only de Panel3-Guarida .83, y ciclo finito de 3 iteraciones A1-B1-A2-B2 (STOP_MAX_ITERATIONS) sobre XC .198/.253 (ubnt_poll noack_mode en RAM, AirPrism solo-lectura) y LTU .110 (param ame_core en RAM, sin RF) con 4 ventanas OTA read-only en .84. Leer antes de tocar Panel3 o el banco LTU/XC. -->

# Stage 1616A: diagnostico cpe_80, inventario Panel3 .83 y cierre finito D3/D4

## 1. Alcance y seguridad

Carril 3, hardware real, cero red simulada. Dos AP de produccion se tratan como solo-lectura
(`198.18.0.7` Panel1 y `198.18.0.6` Panel3): la guarda `assert_read_only` rechaza antes de
abrir socket cualquier `uci set`, `iw ... set`, `tc` de cambio, `wifi`, redireccion a archivo o
reinicio de servicio. Las escrituras en RAM a los radios de banco `.198`/`.253`/`.110` se hacen
bajo un watchdog de 60 s en el propio equipo y se verifican restauradas. Cero escrituras a Flash,
cero arranque de RF, cero escritura de GPIO del front-end. Nombres de abonado y coordenadas GPS
se redactan en origen; las estaciones se rotulan solo por octeto de IP.

## 2. Diagnostico de cpe_80 (1614A, solo-lectura sobre .84)

cpe_80 sigue asociado pero el enlace esta roto en una sola direccion. Evidencia viva:

| Metrica | Valor |
| :-- | :-- |
| TX AP hacia CPE | 6,5 Mbps MCS0 NSS1 |
| RX CPE hacia AP | 104 Mbps |
| RSSI en el AP | -51 dBm (cadenas -57 / -60) |
| tramas TX fallidas (vida) | 25,2 % |
| piso de ruido / canal | -109 dBm / 5240 MHz |
| ICMP a 198.18.0.125 desde el AP | 100 % perdida |
| TCP 22 / 80 / 443 desde el AP | cerrado / cerrado / cerrado |

Clasificacion: DOWNLINK_BROKEN_UPLINK_OK_CPE_UNREACHABLE. La causa raiz es asimetrica: el AP
recibe del CPE a 104 Mbps, pero su transmision al CPE cayo a 6,5 Mbps MCS0 con 25,2 % de fallos y
la IP de gestion del CPE no responde ni ICMP ni TCP. El RSSI en el AP es bueno (-51 dBm), asi que
no es falta de senal del lado del AP, sino un colapso del control de tasa o interferencia en el
receptor del CPE, con caida a un solo flujo espacial (NSS1). Esto apunta a un problema fisico del
lado del cliente (receptor del CPE, interferencia local o antena), no del AP. Etapa solo-lectura,
sin accion.

## 3. Inventario vivo de Panel3-Guarida .83 (1614A, solo-lectura)

`.83` es un LiteAP AC (airOS WA.ar934x 8.7.25, SSID PUBLIC_TERM_0005, ap-ptmp-mixed), alcanzable
solo-lectura con usuario ubnt. Su `wstalist` lista hoy 3 de los 6 CPEs esperados (octetos 9, 235
y 238); los otros 3 no estan asociados en este momento. Esto cierra parcialmente la compuerta G5
del plan de rollout de 1549A: inventario medido en vivo 3 de 6, estado FAIL hasta que los 6 esten
en linea. Es el estado real de la red, no un supuesto.

## 4. Ciclo finito de 3 iteraciones (1615A, STOP_MAX_ITERATIONS)

Tres iteraciones contrabalanceadas A1-B1-A2-B2, cada una con un control en RAM bajo watchdog de
60 s en un radio de banco mas 4 ventanas OTA solo-lectura sobre `.84` (A = cpe_41, B = cpe_223)
que aportan goodput/RTT/RSSI reales. Criterio de parada: STOP_MAX_ITERATIONS (3 de 3).

| Iter | Radio | Knob en RAM | Restaurado | goodput | p95 | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 Rocket Prism 5AC | noack_mode | si | 1,23 Mbps | 12,4 ms | keep |
| 2 | .253 Rocket 2AC Prism | noack_mode | si | 0,08 Mbps | 24,8 ms | discard |
| 3 | .110 LTU-Lite | eab_txcmd_dump | si | 0,87 Mbps | 11,8 ms | keep |

Decisiones sobre los knobs reales de XC y LTU:

- noack_mode (ubnt_poll, `/proc/sys/dev/uph_wifi0/noack_mode`): la escritura toma efecto (la
  relectura lo confirma) y se restaura al valor que cada comando capturo. Es un knob gestionado
  por el firmware que varia solo entre lecturas, por lo que no hay linea base fija.
- AirPrism GPIO 13..16: se capturo solo-lectura el banco de filtro activo derivado de la
  frecuencia viva via la tabla de verdad de 305A (`.198` en 5165 MHz, banco UNII-1). No se
  escribio ningun registro del front-end de RF: no existe interfaz sysfs de GPIO en estos equipos
  y una escritura seria a registros crudos, algo que no se hace por seguridad.
- LTU ame_core: se togglo en RAM el flag de depuracion `eab_txcmd_dump` (reversible, sin efecto
  de RF) con la RF de `.110` apagada, y se restauro.

El goodput es bajo porque es trafico ambiente del abonado sobre `.84`, no una carga inyectada; el
valor real esta en RTT/jitter/perdida/RSSI. Ningun radio de banco tiene par aire, por eso su
goodput propio no se mide.

## 5. results.tsv y cierre D3/D4

Se registraron 3 filas finitas `s1615a_iter1_198`, `s1615a_iter2_253`, `s1615a_iter3_110` en el
dominio D3, con el motivo de parada STOP_MAX_ITERATIONS. Las filas reales de Wave 85 (D4
`s1548a_g84_*`) y las de otros carriles quedaron intactas, con encabezado unico.

## 6. Verificacion

`tests/test_stage1614a_to_1619a_suite.py` reparsea los receipts contra sus capturas crudas,
prueba la guarda solo-lectura en ambos AP de produccion, la anonimizacion y las 3 filas finitas.
El gate `enforce_5pillar_research_gate.py ... --require-live-hardware` pasa en 1615A de forma
honesta (0 gamed_signals). Pilares: A knobs s017/s020/s029/s032/s040 (ubnt_poll_host.ko, AirPrism
305A, ame_core); B reactor cerrado; C 3 iteraciones A1-B1-A2-B2 con watchdog 60 s; D p95 por
iteracion; E claim FMX-1615A en MemoryMaster. Skills K-Dense citadas desde su SKILL.md.

## 7. Limites

- El diagnostico de cpe_80 es del lado del AP; no se inicio sesion en el CPE del abonado.
- Panel3 tiene 3 de 6 CPEs en linea ahora; el inventario completo depende de que asocien los otros.
- La prueba a la IP de gestion es alcanzabilidad (ICMP mas conexion TCP), no una descarga HTTP.
- Los radios de banco no tienen par aire; su goodput propio no se mide, el OTA viene de `.84`.
- noack_mode lo gestiona el firmware y varia entre lecturas; cada escritura se restauro.
