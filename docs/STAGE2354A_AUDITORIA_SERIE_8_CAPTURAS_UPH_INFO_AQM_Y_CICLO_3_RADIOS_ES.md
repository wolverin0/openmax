<!-- doc-head: Wave 219 (2352A-2357A). 2352A: octava auditoria de solo lectura de la serie opus1 (2106A, 2142A, 2172A, 2202A, 2256A, 2286A, 2322A y 2352A). Lee /proc/uptime en los 6 radios, phy0/aqm y netdev:phy0-ap0/aqm mas ethtool en Panel1 .84, y los escalares de /proc/net/uph_wifi0/info en los 4 airOS con limpieza en el radio. Los 6 radios siguen en el mismo arranque en las 8 capturas; fq_overmemory sigue en 4055; rx_fifo_errors de Panel1 sube a 676. 2353A: ciclo de 3 iteraciones con tcp_rfc1337 y tcp_stdurg en .198, .253 y .110, todo restaurado a 0. Leer antes de retomar la serie de capturas o los ciclos TCP del banco. -->

# Stage 2354A: serie de 8 capturas, info del driver uph, aqm de Panel1 y ciclo en 3 radios

## 1. Resumen ejecutivo

- Esta es la octava captura de la serie opus1. Por primera vez se leyo el uptime de los 6 radios en la
  misma captura.
- Los 6 radios siguen en el mismo arranque en las 8 capturas: la hora de arranque estimada varia como
  mucho 29.3 s (Panel1) y menos de 3 s en los demas.
- En Panel1 .84, `fq_overmemory` de phy0/aqm sigue en 4055 (igual en 2172A, 2286A y 2352A).
  `rx_fifo_errors` de eth0 sube a 676 y no bajo nunca en la serie.
- Los descartes de la clase :2 de ath0 no se movieron: Panel2 184548 y Panel3 43817.
- 2353A corrio las 3 iteraciones tal como se pidieron. Cada ajuste paso de 0 a 1 y volvio a 0.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sesion
SSH por radio. `assert_read_only` corrio sobre los comandos de .82, .83 y .84 antes de abrir el socket.

La tabla `info` se limpio en el propio radio con la misma regla de 2322A: MAC a `[MAC]`, IP a `[IP]` y
todas las letras pasan a `x` salvo en las filas de rotulos. No aparecio ninguna MAC ni IP.

En el banco solo se escribieron sysctls en RAM con watchdog de 60 s y relectura final. Cero Flash, RF,
canal, GPIO o atpc.

## 3. 2352A: mismo arranque en las 8 capturas

| Radio | Uptime ahora (s) | Capturas con uptime | Dispersion del arranque (s) |
| --- | --- | --- | --- |
| Panel2 .82 | 644485.67 | 7 | 1.2 |
| Panel3 .83 | 644480.66 | 7 | 2.6 |
| Panel1 .84 | 54662.10 | 8 | 29.3 |
| LTU .110 | 70870.59 | 6 | 0.9 |
| XC .198 | 141555.12 | 6 | 0.7 |
| XC .253 | 330734.28 | 6 | 0.8 |

La hora de arranque se estima como hora de la captura menos uptime. La tolerancia es 300 s porque la
hora de cada captura se escribe al terminar la sesion. 2256A no leyo uptime en los paneles airOS ni en
el banco, y 2322A tampoco en el banco.

## 4. 2352A: Panel1 .84

| Contador | 2142A | 2172A | 2202A | 2256A | 2286A | 2322A | 2352A |
| --- | --- | --- | --- | --- | --- | --- | --- |
| eth0 rx_fifo_errors | 558 | 585 | 596 | 612 | 636 | 656 | 676 |
| Tx Pause Frames Honored | - | 2454 | 881 | - | 807 | 337 | 297 |
| phy0 fq_overmemory | - | 4055 | - | - | 4055 | - | 4055 |

`Tx Pause Frames Honored` sigue sin ser monotono. phy0/aqm en este momento: fq_flows_cnt 4096,
fq_limit 512, fq_memory_limit 3145728, fq_memory_usage 0, fq_backlog 0, fq_overlimit 0, fq_collisions
720199, fq_quantum 3028.

## 5. 2352A: escalares de /proc/net/uph_wifi0/info

`/proc/net/uph_wifi0/` tiene solo `info` y `noack_info`, ambos 0444, en los 4 airOS.

| Panel | Frecuencia | STAs | ACTv | AVGTXRT | AVGRXRT | DCAPKBPS | UCAPKBPS | TXUSE | RXUSE | TLUSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 5805 | 7 | 0 | 120714 | 124428 | 97778 | 98298 | 115 | 21 | 136 |
| Panel3 .83 | 5755 | 3 | 3 | 138666 | 130000 | 109546 | 111800 | 12 | 10 | 22 |

Los XC del banco (.198 en 5165, .253 en 2432) muestran la tabla de capacidad con todo en cero. TXUSE
de Panel2 bajo de 452 en 2322A a 115 ahora: el valor es instantaneo, no un acumulado.

Veredicto del recibo: `UPTIME_6_OF_6+SAME_BOOT_ALL_6_ACROSS_8_AUDITS+FQ_OVERMEMORY_4055_FLAT+INFO_SCALARS_4_AIROS`.

## 6. 2353A: ciclo tcp_rfc1337 / tcp_stdurg en 3 radios

Antes del ciclo se confirmo que los dos sysctl existen en los dos kernels (2.6.32 y 3.14) y valen 0 en
los tres radios. Cada iteracion siguio A1, B1, A2, B2 con watchdog de 60 s, relectura final y ventanas
OTA de solo lectura en Panel1 .84 (cpe_41, cpe_223 y cpe_80).

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_rfc1337 | 0 | 1 | 0 | si | 0.35 | 24.92 | keep |
| 2 | .253 XC | tcp_stdurg | 0 | 1 | 0 | si | 0.34 | 3.06 | keep |
| 3 | .110 LTU | tcp_rfc1337 | 0 | 1 | 0 | si | 0.63 | 13.12 | discard |

Filas agregadas: `s2353a_iter1_198`, `s2353a_iter2_253` y `s2353a_iter3_110` en
`artifacts/autoresearch/results.tsv`, y `S2353A_ITER1_198`, `S2353A_ITER2_253` y `S2353A_ITER3_110` en
`orchestration/autoresearch/results.tsv` (CRLF). Las filas de otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto. keep y
discard salen del puntaje del trafico ambiente de Panel1, no del ajuste.

## 7. Lo que queda abierto

- La causa de los `rx_fifo_errors` de Panel1 (unos 20 por cada 20 minutos).
- Decodificar las unidades de TXUSE, RXUSE, TLUSE y TXPER.
- Si `fq_overmemory` 4055 viene de un solo evento anterior a 2172A.

## 8. Recibos

- `artifacts/autoresearch/stage2352a_live_guarida_and_bench_proc_net_uph_and_8audit_series_receipt.json`
- `artifacts/autoresearch/stage2353a_live_xc_ltu_3host_tcp_rfc1337_and_stdurg_cycle_receipt.json`
- `artifacts/autoresearch/stage2355a_memorymaster_ingest_receipt.json`
- `artifacts/verification/stage2357a_wave219_opus1_gate.json`
