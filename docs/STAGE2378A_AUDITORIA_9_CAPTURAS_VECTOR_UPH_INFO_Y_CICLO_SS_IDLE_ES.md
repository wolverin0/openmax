<!-- doc-head: Wave 223 (2376A-2381A). 2376A: novena auditoria de solo lectura de la serie opus1. Relee el vector compartido de 12 entradas de /proc/sys/dev/uph_wifi0 (la ruta pedida /proc/sys/uph_wifi0 no existe y cinco nombres pedidos no son entradas del driver), status, gqparam y enable, los escalares de /proc/net/uph_wifi0/info, phy0/aqm de Panel1 y el uptime de los 6 radios. El vector de .198 sigue todo en cero desde 2286A; los 6 radios siguen en el mismo arranque en las 9 capturas; fq_overmemory sigue en 4055. 2377A: ciclo de 3 iteraciones con tcp_slow_start_after_idle y tcp_no_metrics_save en .198, .253 y .110, todo restaurado. Leer antes de volver a leer el vector uph o retomar ciclos TCP del banco. -->

# Stage 2378A: novena captura, vector uph de 12 entradas, info del driver y ciclo slow start

## 1. Resumen ejecutivo

- La ruta pedida `/proc/sys/uph_wifi0/` no existe en ningun radio; el arbol del driver esta en
  `/proc/sys/dev/uph_wifi0/`. Cinco nombres pedidos (cca, dfs, dynamic-ack, frame_len, rate) no son
  entradas del driver. Se leyeron las 12 entradas que 2286A ya leyo de forma segura.
- El vector compartido de .198 sigue todo en cero, igual que en 2256A y 2286A. Solo 2202A lo vio con un
  3 en la primera posicion.
- Las 12 entradas siguen mostrando un unico vector por radio en los 4 airOS.
- Los 6 radios siguen en el mismo arranque en las 9 capturas.
- 2377A corrio las 3 iteraciones tal como se pidieron y cada ajuste volvio a su valor base.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sesion
SSH por radio. `assert_read_only` corrio sobre los comandos de .82, .83 y .84 antes de abrir el socket.

Del arbol del driver solo se listaron los nombres. Se leyeron las 12 entradas del vector y status,
gqparam y enable; nunca set_*, get_diag, get_host_diag, get_reg, debug_*, gps_info, gpsreset ni
addradio. Ninguno de los nombres pedidos que no existen se intento leer.

El vector paso por los filtros de MAC e IP en el radio. status, gqparam, enable y la tabla `info`
pasaron por la limpieza completa de 2322A. No aparecio ninguna MAC ni IP.

En el banco solo se escribieron sysctls en RAM con watchdog de 60 s y relectura final. Cero Flash, RF,
canal, GPIO o atpc.

## 3. 2376A: vector compartido de 12 entradas

| Radio | 2202A | 2256A | 2286A | 2376A |
| --- | --- | --- | --- | --- |
| Panel2 .82 | posicion 10 en 1 | posicion 10 en 1 | posicion 10 en 1 | posicion 10 en 1 |
| Panel3 .83 | todo 0 | todo 0 | todo 0 | todo 0 |
| XC .198 | posicion 1 en 3 | todo 0 | todo 0 | todo 0 |
| XC .253 | todo 0 | todo 0 | todo 0 | todo 0 |

Cada vector tiene 16 enteros. 2202A leyo solo `fixed_frame`; 2256A y 2286A, el vector comun.

| Radio | status | gqparam | enable |
| --- | --- | --- | --- |
| Panel2 .82 | 1 | 1 | 1 |
| Panel3 .83 | 1 | 1 | 1 |
| XC .198 | 0 | 0 | 1 |
| XC .253 | 0 | 0 | 1 |

Son los mismos valores que en 2256A.

## 4. 2376A: mismo arranque en las 9 capturas

| Radio | Uptime ahora (s) | Capturas con uptime | Dispersion del arranque (s) |
| --- | --- | --- | --- |
| Panel2 .82 | 646105.86 | 8 | 1.2 |
| Panel3 .83 | 646101.09 | 8 | 2.6 |
| Panel1 .84 | 56282.83 | 9 | 29.3 |
| LTU .110 | 72491.42 | 7 | 0.9 |
| XC .198 | 143175.99 | 7 | 0.7 |
| XC .253 | 332355.11 | 7 | 0.8 |

La tolerancia es 300 s, igual que en 2352A.

## 5. 2376A: Panel1 .84 y paneles airOS

| Contador | 2286A | 2322A | 2352A | 2376A |
| --- | --- | --- | --- | --- |
| eth0 rx_fifo_errors | 636 | 656 | 676 | 712 |
| Tx Pause Frames Honored | 807 | 337 | 297 | 3055 |
| phy0 fq_overmemory | 4055 | - | 4055 | 4055 |

`rx_fifo_errors` sumo 36 en unos 27 minutos, mas rapido que antes, y nunca bajo en la serie. `Tx Pause
Frames Honored` salto de 297 a 3055: sigue sin ser monotono. Rx Pause sigue en 0. Los descartes de la
clase :2 no se movieron: Panel2 184548 y Panel3 43817.

| Panel | Frecuencia | STAs | ACTv | AVGTXRT | AVGRXRT | DCAPKBPS | UCAPKBPS | TXUSE | RXUSE | TLUSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 5805 | 7 | 0 | 124428 | 122571 | 108252 | 104185 | 209 | 24 | 233 |
| Panel3 .83 | 5755 | 3 | 1 | 138666 | 134333 | 120639 | 123586 | 22 | 6 | 28 |

Veredicto del recibo: `BRIEF_SYSCTL_PATH_ABSENT_TREE_UNDER_PROC_SYS_DEV+VEC198_ALL_ZERO_UNCHANGED_SINCE_2286A+ONE_VECTOR_ON_ALL_4_AIROS+SAME_BOOT_ALL_6_ACROSS_9_AUDITS`.

## 6. 2377A: ciclo tcp_slow_start_after_idle / tcp_no_metrics_save en 3 radios

Antes del ciclo se confirmo que los dos sysctl existen en los dos kernels y que
`tcp_slow_start_after_idle` vale 1 y `tcp_no_metrics_save` vale 0 en los tres radios. Cada iteracion
siguio A1, B1, A2, B2 con watchdog de 60 s, relectura final y ventanas OTA de solo lectura en Panel1
.84 (cpe_41, cpe_223 y cpe_80).

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_slow_start_after_idle | 1 | 0 | 1 | si | 0.24 | 24.82 | keep |
| 2 | .253 XC | tcp_no_metrics_save | 0 | 1 | 0 | si | 1.56 | 40.15 | discard |
| 3 | .110 LTU | tcp_slow_start_after_idle | 1 | 0 | 1 | si | 2.17 | 9.30 | keep |

Filas agregadas: `s2377a_iter1_198`, `s2377a_iter2_253` y `s2377a_iter3_110` en
`artifacts/autoresearch/results.tsv`, y `S2377A_ITER1_198`, `S2377A_ITER2_253` y `S2377A_ITER3_110` en
`orchestration/autoresearch/results.tsv` (CRLF). Las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto. keep y
discard salen del puntaje del trafico ambiente de Panel1, no del ajuste.

## 7. Lo que queda abierto

- La causa de los `rx_fifo_errors` de Panel1, que se aceleraron en esta captura.
- Que significa la posicion 10 del vector de Panel2 y por que .198 tuvo un 3 en 2202A.
- Decodificar las unidades de TXUSE, RXUSE, TLUSE y TXPER.

## 8. Recibos

- `artifacts/autoresearch/stage2376a_live_guarida_and_bench_9audit_and_uph_sysctl_recheck_receipt.json`
- `artifacts/autoresearch/stage2377a_live_xc_ltu_3host_tcp_ss_idle_and_no_metrics_cycle_receipt.json`
- `artifacts/autoresearch/stage2379a_memorymaster_ingest_receipt.json`
- `artifacts/verification/stage2381a_wave223_opus1_gate.json`
