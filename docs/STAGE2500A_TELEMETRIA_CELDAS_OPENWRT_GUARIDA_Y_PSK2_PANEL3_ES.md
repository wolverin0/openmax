<!-- doc-head: Wave 243 (2496A-2501A). Panel3-Guarida (.83) y sus 3 CPE pasaron de encryption=none a psk2 con watchdog de vuelta atras en los 4 radios (script tools/panel3/upgrade_panel3_to_psk2.py corregido: sleep 2 y setsid antes de wifi reload, conteo de estaciones sobre las AP/VLAN phy0-ap0.staN, confirmacion solo con 3/3). 2496A audita la celda Panel3 en OpenWrt 24.10.4 contra los recibos del cambio; 2497A ordena el arranque 4addr (el puerto phy0-ap0.staX queda en forwarding antes del 4-way); 2498A y 2499A comparan las dos celdas OpenWrt de Guarida (Panel1 y Panel3). La CPE .210.9 ya no duplica respuestas de ping pero sigue en MCS0 NSS1; fq_overmemory de Panel3 crece unas 10 veces mas rapido que el de Panel1. Leer antes de tocar la celda Panel3 o comparar celdas OpenWrt. -->

# Stage 2500A: psk2 en Panel3, auditoria post-cambio y telemetria de las dos celdas OpenWrt de Guarida

## 1. Resumen ejecutivo

- Panel3-Guarida y sus 3 CPE (.210.9, .210.235, .210.238) quedaron en psk2. Los 4 watchdogs registraron
  que se mantenia psk2 y el controlador confirmo 3 de 3 estaciones respondiendo.
- La CPE .210.9 ya no devuelve respuestas de ping duplicadas, pero no subio a MCS 7/8: sigue en MCS 0-1
  con un solo flujo espacial, unos 2000 envios fallidos cada 45 s y entre 30 y 60 por ciento de perdida
  vista desde el AP. Sus cadenas muestran unos 10 dB de diferencia. El cifrado no era la causa del bajo
  rendimiento; queda como sospecha el camino de RF (antena, alineacion o cableado), sin verificar.
- Las dos celdas OpenWrt de Guarida usan ahora psk2 y los mismos limites AQL.
- Panel1 tiene sus 3 estaciones en MCS 7 con dos flujos; Panel3 tiene 2 de 3.
- `fq_overmemory` de Panel3 paso de 608 (2472A) a 3306 y sumo 184 en 45 s; Panel1 sigue en 4055.

## 2. Cambio psk2 en Panel3 (orden directa del operador)

El script original tenia tres problemas, corregidos antes de correrlo:

- `wifi reload` arrancaba de inmediato y podia cortar el SSH antes de cerrar el canal: ahora cada radio
  espera 2 s y el script corre separado de la sesion con `setsid`.
- El AP contaba estaciones solo en `phy0-ap0`, que con 4addr siempre da 0: ahora suma las AP/VLAN
  `phy0-ap0.staN`. Con el conteo viejo el AP volvia siempre a `none` salvo que se marcara la confirmacion.
- La confirmacion en el AP se marcaba sin condicion a los 22 s, lo que anulaba su vuelta atras aunque una
  CPE no se hubiera unido. Ahora se marca solo si hay 3 estaciones y las 3 CPE responden ping desde el
  controlador (el AP no recibe respuesta de ping de .235 ni .238 ni siquiera en `none`).

Ventanas de decision: AP 80 s, CPE 150 s, para que una CPE siga al AP si este vuelve atras. La clave se
lee de Panel1 y no se imprime ni se guarda.

| Tiempo desde el lanzamiento | Estaciones en el AP | Respuestas de ping (.9 / .235 / .238) |
| --- | --- | --- |
| 46.7 s | 1 | 1 / 4 / 4 |
| 72.6 s | 3 | 4 / 4 / 2 |

Resultado de los watchdogs: AP `kept_psk2 stations=3`; las 3 CPE `kept_psk2`.

## 3. 2496A: celda Panel3 despues del cambio

| Radio | Version | Kernel | Cifrado | Arranque dentro de la ventana del cambio |
| --- | --- | --- | --- | --- |
| Panel3 .83 | 24.10.4 | 6.6.110 | psk2 | si |
| CPE .210.9 | 24.10.4 | 6.6.110 | psk2 | si |
| CPE .210.235 | 24.10.4 | 6.6.110 | psk2 | si |
| CPE .210.238 | 24.10.4 | 6.6.110 | psk2 | si |

Veredicto: `PANEL3_CELL_OPENWRT_24.10.4_PSK2+BOOTS_INSIDE_CUTOVER_WINDOWS+CPE_210_9_NSS1_MCS0_IMBALANCE_10DB`.

## 4. 2497A: orden del arranque 4addr

En el unico episodio que quedo en el registro del AP (psk2, CPE .210.235), el puerto `phy0-ap0.sta3` del
puente quedo en forwarding 1 s despues de la asociacion y el 4-way termino a los 2 s. O sea, la AP/VLAN
4addr ya existe cuando corre el 4-way. La comparacion con `none` no se pudo hacer: el registro del AP
empieza a las 12:35:07, despues de toda asociacion en `none`. Las llamadas WMI_PEER_ASSOC y
nl80211_set_wds_sta no se registran en el nivel normal y no se trazaron; nada se dedujo de binarios.

## 5. 2498A: telemetria de los 8 radios

Se leyeron 7 radios directamente; la tercera estacion de Panel1 (cpe_80) no tiene direccion de gestion
alcanzable y se leyo solo desde el AP.

| Celda | Estacion | TX MCS / NSS (AP) | RX MCS | Senal dBm | Dif. cadenas dB | Fallidos en 45 s |
| --- | --- | --- | --- | --- | --- | --- |
| Panel1 | cpe_41 | 7 / 2 | 5 | -51 | 1 | 0 |
| Panel1 | cpe_223 | 7 / 2 | 6 | -44 | 8 | 0 |
| Panel1 | cpe_80 | 7 / 2 | 7 | -59 | 1 | 0 |
| Panel3 | .210.9 | 0 / 1 | 0 | -50 | 12 | 2184 |
| Panel3 | .210.238 | 8 / 2 | 6 | -44 | 1 | 0 |
| Panel3 | .210.235 | 8 / 2 | 8 | -36 | 7 | 0 |

| AP | Uptime (s) | fq_overmemory | En 45 s | eth0 rx_fifo_errors | En 45 s | Carga 1 min |
| --- | --- | --- | --- | --- | --- | --- |
| Panel1 .84 | 66093 | 4055 | 0 | 801 | 4 | 0.41 |
| Panel3 .83 | 4974 | 3122 | 184 | 13 | 3 | 0.73 |

Del lado de las CPE la memoria disponible va de 1840 a 4640 KiB. La CPE .210.238 ve 23 dB de diferencia
entre sus cadenas aunque el AP la ve con 1 dB.

## 6. 2499A: comparacion de las celdas

- Cifrado: psk2 en las dos.
- AQL: iguales ahora (VO 300/600, VI 1000/2000, BE 1500/3000, BK 500/1000, umbral 4000). En 2472A Panel3
  tenia 1200/2400 en todas las clases; el valor cambio despues del `wifi reload` del cambio psk2. La causa
  exacta no se verifico.
- `fq_overmemory` por hora de uptime: Panel1 220.65, Panel3 2358.64. Panel3 coincide con la estacion lenta
  .210.9, que reintenta miles de veces; la relacion no esta probada.

Veredicto: `BOTH_CELLS_PSK2+AQL_EQUAL+P1_3_OF_3_NSS2_MCS7PLUS+P3_2_OF_3_NSS2_MCS7PLUS`.

## 7. Seguridad

Las auditorias 2496A a 2499A fueron de solo lectura: cada comando paso el filtro de escritura antes de
abrir el socket. Ninguna MAC salio de los radios: se reemplazan en el equipo por un hash corto y se cruzan
por hash. No se leyeron nombres de host, porque algunos llevan nombres de abonados. La unica escritura de
la ola fue el cambio psk2 pedido por el operador.

## 8. Lo que queda abierto

- Revisar en sitio la antena y el cableado de la CPE .210.9 (una cadena unos 10 dB mas baja).
- Confirmar si la estacion lenta explica el `fq_overmemory` de Panel3.
- Decidir si se fija el AQL de Panel3 para que no cambie con un `wifi reload`.
- Encontrar la direccion de gestion de la tercera CPE de Panel1.

## 9. Recibos

- `artifacts/canary_panel3_guarida/panel3_psk2_upgrade_20261028_receipt.json`
- `artifacts/autoresearch/stage2496a_live_panel3_postcutover_openwrt_and_psk2_audit_receipt.json`
- `artifacts/autoresearch/stage2497a_panel3_4addr_wds_bringup_none_vs_psk2_analysis_receipt.json`
- `artifacts/autoresearch/stage2498a_live_guarida_two_openwrt_cells_8radio_telemetry_receipt.json`
- `artifacts/autoresearch/stage2499a_guarida_openwrt_cells_comparative_analysis_receipt.json`
- `artifacts/verification/stage2501a_wave243_opus1_gate.json`
