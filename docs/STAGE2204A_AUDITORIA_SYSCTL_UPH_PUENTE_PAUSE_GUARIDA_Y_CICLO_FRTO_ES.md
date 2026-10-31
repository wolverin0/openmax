<!-- doc-head: Wave 194 (2202A-2207A). 2202A: auditoria de solo lectura de los sysctl uph_wifi0 pedidos en los 4 airOS, de la configuracion de puente y FDB en los 6 radios, y de pausa y FIFO de eth0 en Panel1 .84. El equipo del otro lado del cable de Panel1 no anuncia pausa y la placa conto 0 tramas de pausa recibidas: el contador 'Tx Pause Frames Honored' no viene de ese equipo y ademas no es monotono, asi que no es un total desde el arranque. Seis archivos uph imprimen un mismo vector de 16 valores por equipo. 2203A: ciclo finito eth0 tx_queue_len / tcp_frto / tcp_early_retrans en RAM en .198/.253/.110, todo restaurado. Leer antes de interpretar contadores de pausa de ag71xx o valores uph_wifi0. -->

# Stage 2204A: sysctl uph, puente y pausa en Guarida, y ciclo tcp_frto

## 1. Resumen ejecutivo

- La perdida de recepcion de Panel1 no se explica por tramas de pausa del equipo vecino: ese equipo no
  anuncia pausa y la placa de Panel1 conto 0 tramas de pausa recibidas desde el arranque.
- El contador "Tx Pause Frames Honored" de Panel1 bajo entre lecturas: no es un total desde el arranque.
  La lectura de 2454 que uso 2172A no vale como total.
- Panel2 y Panel3 tienen la misma configuracion uph salvo una posicion de un vector compartido.
- El ciclo de banco cambio y restauro tres ajustes sin incidentes.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Los AP de
produccion solo se leyeron, con `assert_read_only` antes de abrir el socket. En el banco solo se
escribieron ajustes en RAM con watchdog de 60 s y relectura final. Cero Flash, RF, canal, GPIO o atpc.

Decisiones de privacidad y seguridad, registradas en el recibo:

- `gps_info` guarda la posicion del radio: solo se registro que existe y su tamano, nunca su contenido.
- `gpsreset` y `addradio` son archivos de accion: solo se registro su existencia y permisos.
- Del puente se omitieron `bridge_id`, `root_id` y `group_addr`, y `flush` no se leyo.
- De la tabla FDB solo se contaron entradas locales y aprendidas, sin imprimir direcciones MAC.
- Del arbol uph_wifi0 solo se leyeron los nombres pedidos; set_*, debug_* y get_reg no se tocaron.

## 3. 2202A: sysctl uph_wifi0

Solo los cuatro airOS tienen `/proc/sys/dev/uph_wifi0` y `/proc/sys/dev/uph`; el LTU .110 y OpenWrt no.

| Valor | Panel2 .82 | Panel3 .83 | Banco .198 | Banco .253 |
| --- | --- | --- | --- | --- |
| noack_mode | 1 | 1 | 0 | 1 |
| daprot | 1 | 1 | 0 | 1 |
| ptp_xmit | 0 | 0 | 0 | 1 |
| sta_priority | 1 2 0 | 1 2 0 | 1 1 2 | 1 2 0 |

Seis archivos (`atpc`, `cms_bias`, `ff_cap_rep`, `ff_mcast_airtime_limit`, `fixed_frame` y
`sta_rx_rssi_th`) imprimen el mismo vector de 16 valores dentro de cada equipo. Por eso su nombre no dice
que contienen: Panel2 tiene un 1 en la decima posicion, Panel3 todo en cero, .198 un 3 en la primera.
La diferencia entre paneles es una sola posicion de esa tabla compartida, no seis ajustes distintos.

## 4. 2202A: puente y FDB

| Radio | Puente | multicast_snooping | multicast_querier | wlan_isolation | FDB local / aprendidas |
| --- | --- | --- | --- | --- | --- |
| Panel2 .82 | br0 | 1 | 1 | 1 | 2 / 441 |
| Panel3 .83 | br0 | 1 | 1 | 1 | 2 / 441 |
| Panel1 .84 | br-lan | 1 | 1 | sin dato | sin herramienta |
| Banco .198 | br0 | 0 | 1 | 1 | 2 / 39 |
| Banco .253 | br0 | 0 | 1 | 1 | 3 / 39 |
| Banco .110 | br0 | 1 | 0 | sin dato | 0 / 1 |

Los dos paneles airOS aprenden las mismas 441 direcciones: comparten el mismo segmento de capa 2. En
todos, hash_max 512 y STP apagado. Panel1 no tiene la herramienta `bridge` instalada, asi que su FDB
queda sin medir (no en cero).

## 5. 2202A: pausa y FIFO de eth0 en Panel1

- Enlace 1000 full con autonegociacion. Panel1 anuncia pausa simetrica y de solo recepcion; el equipo
  del otro lado anuncia "No".
- `ethtool -a` no esta soportado en eth0 y `swconfig` no lista ningun switch: no hay chip de switch.
- La placa conto 0 tramas de pausa recibidas desde el arranque.
- "Tx Pause Frames Honored" en las dos capturas de esta etapa, un minuto aparte: 1168 y 2526 en la
  primera, 3848 y 881 en la segunda. Bajo, incluso dentro de una ventana de 30 s. Un contador de
  hardware angosto que da la vuelta encajaria, pero su ancho no esta establecido.
- rx_fifo_errors no subio en la ventana (sobre 3783 paquetes recibidos).

Veredicto del recibo: `PANEL_UPH_DIFFER+PEER_PAUSE_RULED_OUT+PAUSE_HONORED_NON_MONOTONIC+NO_ETH0_FIFO_ERRORS_IN_WINDOW`.

Lectura: el equipo vecino no esta pausando a Panel1. Que registra ese contador de ag71xx no se puede
saber solo con contadores. Los desbordes de FIFO de eth0 vistos en 2142A y 2172A siguen sin explicar;
esta ventana no tuvo ninguno.

## 6. 2203A: ciclo finito eth0 tx_queue_len / tcp_frto / tcp_early_retrans

Mismo protocolo que 2173A: A1, B1, A2, B2 contrabalanceado, watchdog de 60 s, relectura final y ventanas
OTA de solo lectura en Panel1 .84. STOP_MAX_ITERATIONS con 3 iteraciones.

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | eth0 tx_queue_len | 1000 | 256 | 1000 | si | 0.58 | 13.03 | keep |
| 2 | .253 XC | tcp_frto | 2 | 0 | 2 | si | 2.07 | 27.09 | discard |
| 3 | .110 LTU | tcp_early_retrans | 3 | 0 | 3 | si | 1.68 | 23.30 | discard |

Cobertura: la tarea nombra eth0 tx_queue_len en .198/.253 y tcp_frto o tcp_early_retrans en los tres.
Con un ajuste por iteracion, tx_queue_len corrio en .198, tcp_frto en .253 y tcp_early_retrans en .110,
el unico kernel que lo tiene. Las tres escrituras tomaron efecto y se restauraron; perdida ICMP 0 %.

Filas agregadas: `s2203a_iter1_198`, `s2203a_iter2_253` y `s2203a_iter3_110` en
`artifacts/autoresearch/results.tsv` y `S2203A_ITER1_198` a `S2203A_ITER3_110` en
`orchestration/autoresearch/results.tsv`; las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto. Los
keep/discard reflejan el enlace ambiente de .84.

## 7. Lo que queda abierto

- Averiguar que cuenta "Tx Pause Frames Honored" en ag71xx y su ancho real.
- Medir la FIFO de eth0 de Panel1 en una ventana larga en hora pico.
- Decodificar el vector compartido de 16 valores de los archivos uph_wifi0.

## 8. Recibos

- `artifacts/autoresearch/stage2202a_live_guarida_and_bench_uph_sysctl_and_bridge_audit_receipt.json`
- `artifacts/autoresearch/stage2203a_live_xc_ltu_txqueuelen_eth0_and_tcp_frto_cycle_receipt.json`
- `artifacts/verification/stage2207a_wave194_opus1_gate.json`
