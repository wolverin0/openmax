<!-- doc-head: Wave 203 (2256A-2261A). 2256A: auditoria de solo lectura de las entradas seguras de /proc/sys/dev/uph_wifi0 (status, timing, gqparam, sqparam, hsr_diag, netconf, ro, enable, voip_bias, swr_limit, evm_meas_config) en los 4 airOS, y cadencia del contador 'Tx Pause Frames Honored' de Panel1 .84 con 4 muestras cada 10 s. Seis entradas seguras imprimen el mismo vector de 16 enteros; en los paneles y .253 coincide con el de 2202A, en .198 no. netconf es la tabla de programacion del AP y Panel2 y Panel3 usan esquemas distintos. El contador de pausa volvio a bajar entre muestras: solo un contador de 11 o 12 bits encaja. 2257A: ciclo finito .253 eth0 tx_queue_len / .198 tcp_frto / .110 tcp_dsack en RAM, todo restaurado, que completa la cobertura de 2203A. -->

# Stage 2258A: entradas uph seguras, cadencia de pausa y ciclo .253

## 1. Resumen ejecutivo

- Seis entradas seguras imprimen un mismo vector de 16 enteros por equipo. En Panel2, Panel3 y .253
  coincide con el vector que 2202A vio en otras seis entradas; en .198 no coincide. No se puede saber
  si el vector cambio o si los dos grupos de entradas difieren en .198.
- `netconf` es la tabla de programacion del AP. Panel2 tiene activos los campos de trama fija (`ff_*`);
  Panel3 los tiene en cero y usa los campos hibridos (`hyb_*`) con duraciones de 30000.
- El contador "Tx Pause Frames Honored" de Panel1 bajo otra vez entre muestras de 10 s. Solo un
  contador de 11 o 12 bits que da la vuelta encaja con todos los pasos.
- El ciclo de banco completo la cobertura de 2203A sin incidentes.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Los AP de
produccion solo se leyeron, con `assert_read_only` antes de abrir el socket. Del arbol uph_wifi0 se
listaron todas las entradas (nombre, permisos, tamano) y solo se leyeron las once seguras pedidas.
Nunca se leyeron set_*, get_diag, get_host_diag, get_reg, debug_*, gps_info, gpsreset ni addradio. Las
direcciones MAC y los decimales con forma de coordenada se enmascaran en el propio equipo antes de
salir; en esta captura no aparecio ninguno. En el banco solo se escribieron ajustes en RAM con watchdog
de 60 s y relectura final. Cero Flash, RF, canal, GPIO o atpc.

## 3. 2256A: clasificacion de las entradas seguras

Cada airOS tiene 31 entradas en uph_wifi0. El LTU .110 y OpenWrt .84 no tienen ese arbol.

| Entrada | Formato en los 4 airOS |
| --- | --- |
| status, gqparam, enable | escalar |
| timing, sqparam, ro, voip_bias, swr_limit, evm_meas_config | vector compartido de 16 enteros |
| netconf | tabla de texto |
| hsr_diag | vacia |

Valores escalares: `enable` 1 en los cuatro; `status` y `gqparam` 1 en los paneles y 0 en los dos XC del banco.

El vector compartido: Panel2 tiene un 1 en la decima posicion, Panel3 todo en cero, igual que en 2202A.
En .198 las entradas seguras imprimen todo cero, mientras que en 2202A sus otras seis entradas
imprimian `3 0 0 ...`. Como son archivos distintos, puede haber cambiado el vector o pueden ser dos
vectores distintos en .198; sin volver a leer los archivos de 2202A no se distingue.

## 4. 2256A: netconf, la tabla de programacion del AP

Diferencias entre Panel2 y Panel3 (Panel2 / Panel3):

| Campo | Panel2 | Panel3 |
| --- | --- | --- |
| flags | 137 | 14864 |
| down_dur | 4880 | 30000 |
| up_dur | 4370 | 30000 |
| cfp_dur_min | 180 | 10000 |
| cbp_dur | 180 | 900 |
| ff_frame_dur | 10000 | 0 |
| ff_dl_alloc | 50 | 0 |
| ff_mcast_airtime_limit | 10 | 0 |
| hyb_cfp_dur_unit | 0 | 1000 |
| hyb_bal_dl_avg_dur_thresh | 0 | 5000 |
| atpc_target_rssi | 0 | 36 |

Panel2 corre con los parametros de trama fija activos; Panel3 sin ellos y con los hibridos. Es una
diferencia de configuracion medida, no una recomendacion: que esquema conviene no se evaluo aqui.

## 5. 2256A: cadencia del contador de pausa en Panel1

Cuatro muestras de `ethtool -S eth0` cada 10 s en una sola sesion:

| Muestra | Tx Pause Frames Honored | Rx Pause Frame Packet | rx_fifo_errors |
| --- | --- | --- | --- |
| 1 | 1572 | 0 | 612 |
| 2 | 1715 | 0 | 612 |
| 3 | 1007 | 0 | 612 |
| 4 | 1465 | 0 | 612 |

El contador subio, bajo y volvio a subir. Sus subidas van a unos 29.8 por segundo. Las unicas anchuras
de contador que explican la bajada con una sola vuelta, dentro de 10 veces el mayor paso observado, son
11 y 12 bits (vuelta en 2048 o en 4096). Es una cota, no una anchura probada. Las tramas de pausa
recibidas siguen en cero y la FIFO de eth0 no sumo errores en estos 30 s.

Veredicto del recibo: `SHARED_VECTOR_IN_SAFE_ENTRIES+SHARED_VECTOR_MISMATCH_VS_2202A+PANELS_DIFFER_ON_SAFE_ENTRIES+PAUSE_COUNTER_STEPPED_DOWN_IN_SAMPLES+RX_PAUSE_ZERO`.

## 6. 2257A: ciclo que completa la cobertura de 2203A

Mismo protocolo que 2203A: A1, B1, A2, B2 contrabalanceado, watchdog de 60 s, relectura final y ventanas
OTA de solo lectura en Panel1 .84. STOP_MAX_ITERATIONS con 3 iteraciones.

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .253 XC | eth0 tx_queue_len | 1000 | 256 | 1000 | si | 3.22 | 11.47 | keep |
| 2 | .198 XC | tcp_frto | 2 | 0 | 2 | si | 6.06 | 18.22 | discard |
| 3 | .110 LTU | tcp_dsack | 1 | 0 | 1 | si | 1.41 | 7.95 | discard |

Con 2203A, eth0 tx_queue_len ya corrio en .198 y .253, y tcp_frto en .253 y .198. Las tres escrituras
tomaron efecto y se restauraron; perdida ICMP 0 %.

Filas agregadas: `s2257a_iter1_253`, `s2257a_iter2_198` y `s2257a_iter3_110` en
`artifacts/autoresearch/results.tsv` y `S2257A_ITER1_253` a `S2257A_ITER3_110` en
`orchestration/autoresearch/results.tsv`; las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto.

## 7. Lo que queda abierto

- Releer en .198 las entradas de 2202A junto con las seguras para saber si el vector cambio.
- Si conviene el esquema de trama fija de Panel2 o el hibrido de Panel3: requiere una prueba controlada.
- La anchura real del contador de pausa de ag71xx y que registra.

## 8. Recibos

- `artifacts/autoresearch/stage2256a_live_guarida_and_bench_uph_status_timing_gqparam_audit_receipt.json`
- `artifacts/autoresearch/stage2257a_live_xc_ltu_253_eth0_txqueuelen_and_frto_dsack_cycle_receipt.json`
- `artifacts/verification/stage2261a_wave203_opus1_gate.json`
