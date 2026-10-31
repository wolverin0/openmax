<!-- doc-head: Wave 239 (2472A-2477A). 2472A: duodecima auditoria de solo lectura de la serie opus1, la primera despues de que Panel3-Guarida (.83) paso en vivo a OpenWrt 24.10.4 (kernel 6.6.110, ath10k_pci). Panel1 y Panel3 se auditan como OpenWrt (root, phy0/aqm, AQL, eth0, puertos de br-lan, uptime); Panel2 y el banco XC siguen con el vector uph_wifi0 de 12 entradas, status/gqparam/enable e info. El nuevo arranque de Panel3 cae dentro de la ventana del cambio; los otros 5 radios siguen en el mismo arranque en las 12 capturas; Panel3 ya marca fq_overmemory 608. 2473A: ciclo de 3 iteraciones con tcp_keepalive_intvl (base menos 15) y tcp_keepalive_time (base menos 300), todo restaurado. Leer antes de auditar Panel3 en OpenWrt o retomar ciclos TCP del banco. -->

# Stage 2474A: duodecima captura con Panel3 en OpenWrt y ciclo keepalive_intvl / keepalive_time

## 1. Resumen ejecutivo

- Panel3-Guarida (.83) corre OpenWrt 24.10.4 (ath79/generic, kernel 6.6.110, driver ath10k_pci). Se
  audito como Panel1: root, phy0/aqm, AQL, eth0, puertos de br-lan y uptime.
- Su arranque nuevo (11:21:40 UTC) cae dentro de la ventana del cambio: entre el reinicio pedido
  (11:19:06) y la primera sesion SSH en OpenWrt (11:23:52). Sus 11 capturas airOS fueron un solo arranque.
- Los otros 5 radios siguen en el mismo arranque en las 12 capturas.
- A unos 20 minutos de arrancar, Panel3 ya marca `fq_overmemory` 608. Panel1 sigue en 4055.
- Los vectores de Panel2, .198 y .253 siguen iguales desde 2286A.
- 2473A leyo primero los dos ajustes en los tres radios, aplico la resta pedida y devolvio cada uno a su
  base.

## 2. Alcance, seguridad y cambio de pedido

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sesion
SSH por radio. `assert_read_only` corrio sobre los comandos de .82, .83 y .84 antes de abrir el socket.
En .83 se entra como root de forma explicita: la funcion compartida `username_for()` todavia dice ubnt
para .83 porque cinco suites viejas lo comprueban, y no se toco.

El despacho de Orca todavia trataba a Panel3 como airOS y pedia tcp_keepalive_time a base menos 60. La
actualizacion en vivo del operador lo reemplaza: Panel3 como OpenWrt y base menos 300 con piso 300. Del
despacho se tomo el reparto de radios por ajuste.

En OpenWrt solo se leyeron contadores, limites AQL y nombres de interfaces; no se leyo la lista de
estaciones. En airOS se leyeron las 12 entradas seguras y status, gqparam y enable, con los filtros de
2322A en el radio. No aparecio ninguna MAC ni IP. En el banco solo se escribieron sysctls en RAM con
watchdog de 60 s y relectura final.

## 3. 2472A: los dos paneles OpenWrt

| Dato | Panel1 .84 | Panel3 .83 |
| --- | --- | --- |
| Version | OpenWrt 24.10.4 | OpenWrt 24.10.4 |
| Driver wifi | ath10k_pci | ath10k_pci |
| Uptime (s) | 62316.91 | 1204.56 |
| fq_overmemory | 4055 | 608 |
| fq_collisions | 724639 | 36139 |
| aql_threshold | 4000 | 4000 |
| AQL VO bajo/alto | 300/600 | 1200/2400 |
| AQL VI bajo/alto | 1000/2000 | 1200/2400 |
| AQL BE bajo/alto | 1500/3000 | 1200/2400 |
| AQL BK bajo/alto | 500/1000 | 1200/2400 |
| eth0 rx_fifo_errors | 778 | 1 |
| Tx Pause Frames Honored | 2356 | 3471 |
| Rx Pause | 0 | 0 |

Puertos de br-lan en Panel3: eth0, phy0-ap0 y phy0-ap0.sta1 a sta3 (las tres CPE en 4addr).

## 4. 2472A: mismo arranque

| Radio | Uptime ahora (s) | Capturas con uptime | Dispersion del arranque (s) |
| --- | --- | --- | --- |
| Panel2 .82 | 652139.82 | 11 | 1.2 |
| Panel1 .84 | 62316.91 | 12 | 29.7 |
| LTU .110 | 78525.48 | 10 | 1.4 |
| XC .198 | 149210.03 | 10 | 1.2 |
| XC .253 | 338389.17 | 10 | 1.4 |
| Panel3 .83 | 1204.56 | 11 | 2.7 antes del cambio; reinicio dentro de la ventana |

La tolerancia es 300 s. La serie de clase :2, vector e info de Panel3 termina en 2448A; sus contadores
OpenWrt empiezan una serie nueva aqui.

## 5. 2472A: Panel1 y airOS

| Contador Panel1 | 2412A | 2448A | 2472A |
| --- | --- | --- | --- |
| eth0 rx_fifo_errors | 720 | 736 | 778 |
| Tx Pause Frames Honored | 876 | 3209 | 2356 |
| phy0 fq_overmemory | 4055 | 4055 | 4055 |

`rx_fifo_errors` sumo 42 en unos 69 minutos y nunca bajo en la serie. Panel2 sigue con 184548
descartes en la clase :2.

| Radio | 2202A | 2286A | 2448A | 2472A |
| --- | --- | --- | --- | --- |
| Panel2 .82 | posicion 10 en 1 | igual | igual | igual |
| XC .198 | posicion 1 en 3 | todo 0 | todo 0 | todo 0 |
| XC .253 | todo 0 | todo 0 | todo 0 | todo 0 |

| Radio | status | gqparam | enable |
| --- | --- | --- | --- |
| Panel2 .82 | 1 | 1 | 1 |
| XC .198 | 0 | 0 | 1 |
| XC .253 | 0 | 0 | 1 |

| Panel | Frecuencia | STAs | ACTv | AVGTXRT | AVGRXRT | DCAPKBPS | UCAPKBPS | TXUSE | RXUSE | TLUSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 5805 | 7 | 0 | 118857 | 124428 | 102217 | 108252 | 27 | 21 | 48 |

Veredicto del recibo: `PANEL3_OPENWRT_24.10.4_ATH10K_PCI+PANEL3_REBOOT_INSIDE_CUTOVER_WINDOW+SAME_BOOT_OTHER_5_ACROSS_12_AUDITS+AIROS_3_VECTORS_UNCHANGED_SINCE_2286A+P1_FQ_OVERMEMORY_4055_FLAT`.

## 6. 2473A: ciclo tcp_keepalive_intvl / tcp_keepalive_time en 3 radios

| Radio | tcp_keepalive_intvl | tcp_keepalive_time |
| --- | --- | --- |
| XC .198 | 75 | 7200 |
| XC .253 | 75 | 7200 |
| LTU .110 | 75 | 7200 |

Esa fue la lectura previa, antes de escribir nada. La herramienta aborta antes de escribir si una base
no coincide con el plan o si el valor queda por debajo del piso (15 para intvl, 300 para time). Cada
iteracion siguio A1, B1, A2, B2 con watchdog de 60 s, relectura final y ventanas OTA de solo lectura en
Panel1 .84 (cpe_41, cpe_223 y cpe_80).

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_keepalive_intvl | 75 | 60 | 75 | si | 0.01 | 22.30 | keep |
| 2 | .253 XC | tcp_keepalive_time | 7200 | 6900 | 7200 | si | 0.01 | 8.49 | keep |
| 3 | .110 LTU | tcp_keepalive_intvl | 75 | 60 | 75 | si | 0.01 | 13.74 | discard |

El trafico ambiente de cpe_41 fue casi nulo en estas ventanas. Filas agregadas: `s2473a_iter1_198`,
`s2473a_iter2_253` y `s2473a_iter3_110` en `artifacts/autoresearch/results.tsv`, y `S2473A_ITER1_198`,
`S2473A_ITER2_253` y `S2473A_ITER3_110` en `orchestration/autoresearch/results.tsv` (CRLF). Las filas de
otros carriles se conservaron. keep y discard salen del puntaje del trafico ambiente, no del ajuste.

## 7. Lo que queda abierto

- Por que Panel3 acumulo 608 `fq_overmemory` en 20 minutos con un limite de memoria de 3 MB sin uso.
- Si los limites AQL de Panel3 (1200/2400 en todas las AC) deben igualarse a los de Panel1.
- La causa de los `rx_fifo_errors` de Panel1.
- Actualizar `username_for()` para .83 cuando se retiren las suites viejas que esperan ubnt.

## 8. Recibos

- `artifacts/autoresearch/stage2472a_live_guarida_and_bench_12audit_and_uph_sysctl_recheck_receipt.json`
- `artifacts/autoresearch/stage2473a_live_xc_ltu_3host_tcp_keepalive_intvl_and_time_cycle_receipt.json`
- `artifacts/autoresearch/stage2475a_memorymaster_ingest_receipt.json`
- `artifacts/verification/stage2477a_wave239_opus1_gate.json`
- `artifacts/canary_panel3_guarida/panel3_and_3cpe_cutover_20261028_receipt.json`
