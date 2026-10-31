<!-- doc-head: Wave 208 (2286A-2291A). 2286A: foto de solo lectura tomada en una sola sesion por radio en los 6 equipos: las 12 entradas uph_wifi0 de vector (las seis de 2202A y las seis de 2256A) leidas juntas, mas qdisc y clases de ath0, softnet_stat, conteo de FDB y, en Panel1 .84, ethtool de eth0. Resuelve la duda de .198: las 12 imprimen un solo vector y es el mismo que vio 2256A, asi que el vector cambio desde 2202A. Panel1 no tiene tc. 2287A: ciclo finito tcp_mtu_probing/tcp_reordering en RAM en .198/.253/.110, todo restaurado. Leer antes de interpretar el vector uph o retomar los ciclos de TCP del banco. -->

# Stage 2288A: 12 vectores uph a la vez, qdisc y ciclo tcp_mtu_probing

## 1. Resumen ejecutivo

- En cada airOS las 12 entradas uph_wifi0 de vector imprimen el mismo vector de 16 enteros en el mismo
  instante. En .198 ese vector es todo cero y coincide con el de 2256A, no con el `3 0 0 ...` de 2202A:
  el vector cambio entre 2202A y 2256A. Que lo mueve sigue sin establecerse.
- Los descartes de qdisc de los paneles siguen solo en la clase :2 de ath0.
- El ciclo de banco cambio y restauro tcp_mtu_probing y tcp_reordering sin incidentes.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sola
sesion SSH por radio, las seis en paralelo, una sola foto. Los AP de produccion solo se leyeron, con
`assert_read_only` antes de abrir el socket. De la FDB solo se contaron entradas, sin imprimir MAC. En
el banco solo se escribieron sysctls en RAM con watchdog de 60 s y relectura final. Cero Flash, RF,
canal, GPIO o atpc.

Panel1 no tiene el binario `tc` (ya visto en 2142A): el comando pedido se intento y termino con codigo
127. Como vista de salida se leyo `phy0/aqm` de mac80211, igual que en 2172A.

## 3. 2286A: las 12 entradas a la vez

Entradas leidas en un solo ciclo: atpc, cms_bias, ff_cap_rep, ff_mcast_airtime_limit, fixed_frame,
sta_rx_rssi_th (de 2202A) y timing, sqparam, ro, voip_bias, swr_limit, evm_meas_config (de 2256A).

| Radio | Vectores distintos | Vector ahora | Igual a 2202A | Igual a 2256A |
| --- | --- | --- | --- | --- |
| Panel2 .82 | 1 | 1 en la decima posicion | si | si |
| Panel3 .83 | 1 | todo cero | si | si |
| Banco .198 | 1 | todo cero | no | si |
| Banco .253 | 1 | todo cero | si | si |

Veredicto del recibo: `ALL_12_ONE_VECTOR_ON_EVERY_AIROS+BENCH_198_ONE_VECTOR_NOW_EQUALS_2256A_SO_IT_CHANGED_SINCE_2202A+OPENWRT_TC_ABSENT`.

Lectura: los dos grupos de archivos no difieren; es un unico vector por equipo que todos imprimen. En .198
paso de `3 0 0 ...` a todo cero entre 2202A y 2256A. Esta etapa no lo explica.

## 4. 2286A: qdisc, softnet y FDB en el mismo instante

| Radio | Descartes clase :2 | Requeues :2 | softnet procesados | dropped | time_squeeze | FDB local / aprendidas |
| --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 184548 | 2354 | 2230087094 | 0 | 14976 | 2 / 449 |
| Panel3 .83 | 43817 | 2352 | 663123918 | 0 | 8701 | 2 / 449 |
| Banco .198 | 0 | 0 | 4664698 | 0 | 559 | 2 / 40 |
| Banco .253 | 0 | 0 | 16902369 | 0 | 591 | 3 / 40 |
| Banco .110 LTU | sin clases mq | sin clases mq | 1644859 | 1 | 1 | 0 / 1 |
| Panel1 .84 | sin tc | sin tc | 20650838 | 0 | 3 | sin herramienta |

Panel3 sumo 219 descartes en :2 desde 2172A (43598 a 43817); Panel2 no sumo. Ningun panel descarto en el
backlog de softnet. Panel1: `fq_overmemory` 4055, eth0 con 636 rx_fifo_errors, 0 tramas de pausa
recibidas y "Tx Pause Frames Honored" en 807 (contador no monotono, ver 2202A y 2256A).

## 5. 2287A: ciclo finito tcp_mtu_probing / tcp_reordering

A1, B1, A2, B2 contrabalanceado, watchdog de 60 s, relectura final y ventanas OTA de solo lectura en
Panel1 .84 (cpe_41, cpe_223 y cpe_80). STOP_MAX_ITERATIONS con 3 iteraciones.

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_mtu_probing | 0 | 1 | 0 | si | 2.23 | 25.63 | keep |
| 2 | .253 XC | tcp_reordering | 3 | 6 | 3 | si | 2.82 | 25.37 | keep |
| 3 | .110 LTU | tcp_mtu_probing | 0 | 1 | 0 | si | 12.08 | 29.58 | discard |

Las tres escrituras tomaron efecto y se restauraron; perdida ICMP de cpe_41 en 0 %.

Filas agregadas: `s2287a_iter1_198`, `s2287a_iter2_253` y `s2287a_iter3_110` en
`artifacts/autoresearch/results.tsv` y `S2287A_ITER1_198` a `S2287A_ITER3_110` en
`orchestration/autoresearch/results.tsv`; las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto sobre MTU ni
reordenamiento. Los keep/discard reflejan el enlace ambiente de .84.

## 6. Lo que queda abierto

- Que hace cambiar el vector uph de 16 enteros (en .198 cambio sin ninguna escritura nuestra en uph).
- Los descartes de :2 de Panel3 siguen creciendo despacio; Panel2 estuvo quieto en esta hora.
- La anchura y el significado del contador de pausa de ag71xx en Panel1.

## 7. Recibos

- `artifacts/autoresearch/stage2286a_live_guarida_and_bench_cotimed_12vector_and_qdisc_audit_receipt.json`
- `artifacts/autoresearch/stage2287a_live_xc_ltu_tcp_mtu_probing_and_reordering_cycle_receipt.json`
- `artifacts/verification/stage2291a_wave208_opus1_gate.json`
