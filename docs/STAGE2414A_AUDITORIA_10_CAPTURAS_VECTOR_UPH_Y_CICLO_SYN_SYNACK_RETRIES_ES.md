<!-- doc-head: Wave 229 (2412A-2417A). 2412A: decima auditoria de solo lectura de la serie opus1. Lee las 12 entradas seguras del vector de /proc/sys/dev/uph_wifi0, status, gqparam y enable, los escalares de /proc/net/uph_wifi0/info, phy0/aqm y eth0 de Panel1, la clase :2 de Panel2 y Panel3 y el uptime de los 6 radios. Los 4 vectores airOS siguen iguales desde 2286A (el de .198 todo en cero); los 6 radios siguen en el mismo arranque en las 10 capturas; fq_overmemory sigue en 4055. 2413A: ciclo de 3 iteraciones con tcp_synack_retries y tcp_syn_retries a base mas 1 en .198, .253 y .110, todo restaurado. Leer antes de retomar la serie de capturas o los ciclos TCP del banco. -->

# Stage 2414A: decima captura, vector uph y ciclo tcp_syn_retries / tcp_synack_retries

## 1. Resumen ejecutivo

- Esta es la decima captura de la serie opus1. El pedido ya usaba la ruta y los nombres reales del
  driver, asi que no hubo correcciones.
- Los vectores compartidos de los 4 airOS siguen iguales desde 2286A. El de .198 sigue todo en cero;
  Panel2 mantiene el 1 en la posicion 10.
- status, gqparam y enable no cambiaron: 1, 1, 1 en los paneles y 0, 0, 1 en los XC.
- Los 6 radios siguen en el mismo arranque en las 10 capturas.
- En Panel1, `fq_overmemory` sigue en 4055 y `rx_fifo_errors` llego a 720.
- 2413A leyo primero los dos ajustes en los tres radios, subio cada uno en 1 y lo devolvio a su base.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sesion
SSH por radio. `assert_read_only` corrio sobre los comandos de .82, .83 y .84 antes de abrir el socket.

Del arbol `/proc/sys/dev/uph_wifi0/` solo se listaron los nombres y se leyeron las 12 entradas del
vector mas status, gqparam y enable. Nunca se leyeron set_*, get_*, debug_*, gps* ni addradio. El
vector paso por los filtros de MAC e IP en el radio; los escalares y la tabla `info`, por la limpieza
completa de 2322A. No aparecio ninguna MAC ni IP.

En el banco solo se escribieron sysctls en RAM con watchdog de 60 s y relectura final. Cero Flash, RF,
canal, GPIO o atpc.

## 3. 2412A: vector compartido

| Radio | 2202A | 2256A | 2286A | 2376A | 2412A |
| --- | --- | --- | --- | --- | --- |
| Panel2 .82 | posicion 10 en 1 | igual | igual | igual | igual |
| Panel3 .83 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 |
| XC .198 | posicion 1 en 3 | todo 0 | todo 0 | todo 0 | todo 0 |
| XC .253 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 |

| Radio | status | gqparam | enable |
| --- | --- | --- | --- |
| Panel2 .82 | 1 | 1 | 1 |
| Panel3 .83 | 1 | 1 | 1 |
| XC .198 | 0 | 0 | 1 |
| XC .253 | 0 | 0 | 1 |

## 4. 2412A: mismo arranque en las 10 capturas

| Radio | Uptime ahora (s) | Capturas con uptime | Dispersion del arranque (s) |
| --- | --- | --- | --- |
| Panel2 .82 | 647049.99 | 9 | 1.2 |
| Panel3 .83 | 647044.83 | 9 | 2.7 |
| Panel1 .84 | 57227.03 | 10 | 29.5 |
| LTU .110 | 73435.59 | 8 | 1.1 |
| XC .198 | 144120.15 | 8 | 1.0 |
| XC .253 | 333299.27 | 8 | 1.1 |

La tolerancia es 300 s, igual que en 2352A y 2376A.

## 5. 2412A: Panel1 .84 y paneles airOS

| Contador | 2322A | 2352A | 2376A | 2412A |
| --- | --- | --- | --- | --- |
| eth0 rx_fifo_errors | 656 | 676 | 712 | 720 |
| Tx Pause Frames Honored | 337 | 297 | 3055 | 876 |
| phy0 fq_overmemory | - | 4055 | 4055 | 4055 |

`rx_fifo_errors` sumo 8 en unos 16 minutos: el salto de 2376A no siguio. Nunca bajo en la serie. `Tx
Pause Frames Honored` volvio a bajar, de 3055 a 876, y sigue sin ser monotono. Rx Pause sigue en 0.
Los descartes de la clase :2 no se movieron: Panel2 184548 y Panel3 43817.

| Panel | Frecuencia | STAs | ACTv | AVGTXRT | AVGRXRT | DCAPKBPS | UCAPKBPS | TXUSE | RXUSE | TLUSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 5805 | 7 | 0 | 124428 | 124428 | 103275 | 102030 | 116 | 24 | 140 |
| Panel3 .83 | 5755 | 3 | 1 | 138666 | 138666 | 113706 | 126186 | 18 | 5 | 23 |

Veredicto del recibo: `VEC198_ALL_ZERO_UNCHANGED_SINCE_2286A+ALL_4_AIROS_VECTORS_UNCHANGED_SINCE_2286A+SAME_BOOT_ALL_6_ACROSS_10_AUDITS+FQ_OVERMEMORY_4055_FLAT`.

## 6. 2413A: ciclo tcp_synack_retries / tcp_syn_retries en 3 radios

Lectura previa en los tres radios, antes de escribir nada:

| Radio | tcp_synack_retries | tcp_syn_retries |
| --- | --- | --- |
| XC .198 | 5 | 5 |
| XC .253 | 5 | 5 |
| LTU .110 | 5 | 6 |

El pedido nombraba los dos ajustes y el orden de radios, pero no que ajuste va en cada iteracion. Se
siguio el patron de las olas anteriores: tcp_synack_retries en .198 y .110, tcp_syn_retries en .253,
cada uno a su base mas 1. La herramienta aborta antes de escribir si una base no coincide con el plan.
Cada iteracion siguio A1, B1, A2, B2 con watchdog de 60 s, relectura final y ventanas OTA de solo
lectura en Panel1 .84 (cpe_41, cpe_223 y cpe_80).

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_synack_retries | 5 | 6 | 5 | si | 1.34 | 34.39 | keep |
| 2 | .253 XC | tcp_syn_retries | 5 | 6 | 5 | si | 0.71 | 29.25 | keep |
| 3 | .110 LTU | tcp_synack_retries | 5 | 6 | 5 | si | 0.32 | 11.54 | keep |

Filas agregadas: `s2413a_iter1_198`, `s2413a_iter2_253` y `s2413a_iter3_110` en
`artifacts/autoresearch/results.tsv`, y `S2413A_ITER1_198`, `S2413A_ITER2_253` y `S2413A_ITER3_110` en
`orchestration/autoresearch/results.tsv` (CRLF). Las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto. keep sale
del puntaje del trafico ambiente de Panel1, no del ajuste.

## 7. Lo que queda abierto

- La causa de los `rx_fifo_errors` de Panel1, que suben a ritmo variable.
- Que significa la posicion 10 del vector de Panel2.
- Decodificar las unidades de TXUSE, RXUSE, TLUSE y TXPER.

## 8. Recibos

- `artifacts/autoresearch/stage2412a_live_guarida_and_bench_10audit_and_uph_sysctl_recheck_receipt.json`
- `artifacts/autoresearch/stage2413a_live_xc_ltu_3host_tcp_syn_and_synack_retries_cycle_receipt.json`
- `artifacts/autoresearch/stage2415a_memorymaster_ingest_receipt.json`
- `artifacts/verification/stage2417a_wave229_opus1_gate.json`
