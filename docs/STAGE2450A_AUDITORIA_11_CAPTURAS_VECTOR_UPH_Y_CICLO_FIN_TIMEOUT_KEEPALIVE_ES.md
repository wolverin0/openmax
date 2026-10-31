<!-- doc-head: Wave 235 (2448A-2453A). 2448A: undecima auditoria de solo lectura de la serie opus1. Lee las 12 entradas seguras del vector de /proc/sys/dev/uph_wifi0, status, gqparam y enable, los escalares de /proc/net/uph_wifi0/info, phy0/aqm y eth0 de Panel1, la clase :2 de Panel2 y Panel3 y el uptime de los 6 radios. Los 4 vectores airOS siguen iguales desde 2286A (el de .198 todo en cero); los 6 radios siguen en el mismo arranque en las 11 capturas; fq_overmemory sigue en 4055. 2449A: ciclo de 3 iteraciones con tcp_fin_timeout (base menos 15) y tcp_keepalive_probes (base menos 2) en .198, .253 y .110, todo restaurado. Leer antes de retomar la serie de capturas o los ciclos TCP del banco. -->

# Stage 2450A: undecima captura, vector uph y ciclo tcp_fin_timeout / tcp_keepalive_probes

## 1. Resumen ejecutivo

- Undecima captura de la serie opus1, con la ruta y los nombres reales del driver; no hubo correcciones.
- Los vectores compartidos de los 4 airOS siguen iguales desde 2286A. El de .198 sigue todo en cero;
  Panel2 mantiene el 1 en la posicion 10.
- status, gqparam y enable no cambiaron: 1, 1, 1 en los paneles y 0, 0, 1 en los XC.
- Los 6 radios siguen en el mismo arranque en las 11 capturas.
- En Panel1, `fq_overmemory` sigue en 4055 y `rx_fifo_errors` llego a 736.
- 2449A leyo primero los dos ajustes en los tres radios, aplico la resta pedida y devolvio cada uno a su
  base.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sesion
SSH por radio. `assert_read_only` corrio sobre los comandos de .82, .83 y .84 antes de abrir el socket.

Del arbol `/proc/sys/dev/uph_wifi0/` solo se listaron los nombres y se leyeron las 12 entradas del
vector mas status, gqparam y enable. Nunca se leyeron set_*, get_*, debug_*, gps* ni addradio. El
vector paso por los filtros de MAC e IP en el radio; los escalares y la tabla `info`, por la limpieza
completa de 2322A. No aparecio ninguna MAC ni IP.

En el banco solo se escribieron sysctls en RAM con watchdog de 60 s y relectura final. Cero Flash, RF,
canal, GPIO o atpc.

## 3. 2448A: vector compartido

| Radio | 2202A | 2256A | 2286A | 2376A | 2412A | 2448A |
| --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | posicion 10 en 1 | igual | igual | igual | igual | igual |
| Panel3 .83 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 |
| XC .198 | posicion 1 en 3 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 |
| XC .253 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 | todo 0 |

| Radio | status | gqparam | enable |
| --- | --- | --- | --- |
| Panel2 .82 | 1 | 1 | 1 |
| Panel3 .83 | 1 | 1 | 1 |
| XC .198 | 0 | 0 | 1 |
| XC .253 | 0 | 0 | 1 |

## 4. 2448A: mismo arranque en las 11 capturas

| Radio | Uptime ahora (s) | Capturas con uptime | Dispersion del arranque (s) |
| --- | --- | --- | --- |
| Panel2 .82 | 648022.73 | 10 | 1.2 |
| Panel3 .83 | 648017.50 | 10 | 2.7 |
| Panel1 .84 | 58199.73 | 11 | 29.5 |
| LTU .110 | 74408.23 | 9 | 1.1 |
| XC .198 | 145092.90 | 9 | 1.0 |
| XC .253 | 334271.93 | 9 | 1.1 |

La tolerancia es 300 s, igual que en las capturas anteriores.

## 5. 2448A: Panel1 .84 y paneles airOS

| Contador | 2352A | 2376A | 2412A | 2448A |
| --- | --- | --- | --- | --- |
| eth0 rx_fifo_errors | 676 | 712 | 720 | 736 |
| Tx Pause Frames Honored | 297 | 3055 | 876 | 3209 |
| phy0 fq_overmemory | 4055 | 4055 | 4055 | 4055 |

`rx_fifo_errors` sumo 16 en unos 16 minutos y nunca bajo en la serie. `Tx Pause Frames Honored` volvio a
subir, de 876 a 3209, y sigue sin ser monotono. Rx Pause sigue en 0. Los descartes de la clase :2 no se
movieron: Panel2 184548 y Panel3 43817.

| Panel | Frecuencia | STAs | ACTv | AVGTXRT | AVGRXRT | DCAPKBPS | UCAPKBPS | TXUSE | RXUSE | TLUSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 5805 | 7 | 0 | 113285 | 118857 | 91760 | 102217 | 242 | 21 | 263 |
| Panel3 .83 | 5755 | 3 | 2 | 138666 | 134333 | 120639 | 123586 | 71 | 9 | 80 |

Veredicto del recibo: `VEC198_ALL_ZERO_UNCHANGED_SINCE_2286A+ALL_4_AIROS_VECTORS_UNCHANGED_SINCE_2286A+SAME_BOOT_ALL_6_ACROSS_11_AUDITS+FQ_OVERMEMORY_4055_FLAT`.

## 6. 2449A: ciclo tcp_fin_timeout / tcp_keepalive_probes en 3 radios

Lectura previa en los tres radios, antes de escribir nada:

| Radio | tcp_fin_timeout | tcp_keepalive_probes |
| --- | --- | --- |
| XC .198 | 60 | 9 |
| XC .253 | 15 | 9 |
| LTU .110 | 60 | 9 |

El pedido fijaba cada iteracion: tcp_fin_timeout a base menos 15 en .198 y .110, tcp_keepalive_probes a
base menos 2 en .253. La herramienta aborta antes de escribir si una base no coincide con el plan o si el
valor quedaria por debajo de 1. Cada iteracion siguio A1, B1, A2, B2 con watchdog de 60 s, relectura
final y ventanas OTA de solo lectura en Panel1 .84 (cpe_41, cpe_223 y cpe_80).

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_fin_timeout | 60 | 45 | 60 | si | 1.40 | 34.06 | keep |
| 2 | .253 XC | tcp_keepalive_probes | 9 | 7 | 9 | si | 0.67 | 27.68 | keep |
| 3 | .110 LTU | tcp_fin_timeout | 60 | 45 | 60 | si | 0.42 | 12.55 | keep |

Filas agregadas: `s2449a_iter1_198`, `s2449a_iter2_253` y `s2449a_iter3_110` en
`artifacts/autoresearch/results.tsv`, y `S2449A_ITER1_198`, `S2449A_ITER2_253` y `S2449A_ITER3_110` en
`orchestration/autoresearch/results.tsv` (CRLF). Las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto. keep sale
del puntaje del trafico ambiente de Panel1, no del ajuste.

## 7. Lo que queda abierto

- La causa de los `rx_fifo_errors` de Panel1, que suben a ritmo variable.
- Que significa la posicion 10 del vector de Panel2.
- Decodificar las unidades de TXUSE, RXUSE, TLUSE y TXPER.

## 8. Recibos

- `artifacts/autoresearch/stage2448a_live_guarida_and_bench_11audit_and_uph_sysctl_recheck_receipt.json`
- `artifacts/autoresearch/stage2449a_live_xc_ltu_3host_tcp_fin_timeout_and_keepalive_probes_cycle_receipt.json`
- `artifacts/autoresearch/stage2451a_memorymaster_ingest_receipt.json`
- `artifacts/verification/stage2453a_wave235_opus1_gate.json`
