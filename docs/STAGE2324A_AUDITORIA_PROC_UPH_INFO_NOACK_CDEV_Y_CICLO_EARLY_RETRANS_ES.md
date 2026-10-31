<!-- doc-head: Wave 214 (2322A-2327A). 2322A: auditoria de solo lectura de los archivos info y noack_info del driver uph en los 4 airOS, del dispositivo de caracteres ubnt_poll_host y de contadores de cola co-temporales. La ruta pedida /proc/uph_wifi0 no existe: los archivos estan en /proc/net/uph_wifi0, con permisos 0444. info es una tabla del driver con estaciones, tasas promedio y capacidad; noack_info esta vacio. El dispositivo es el mayor 190 ubnt_poll_host, visible como /dev/uph_wifi0. 2323A: tcp_early_retrans y tcp_thin_linear_timeouts no existen en el kernel 2.6.32 de los XC; el ciclo corrio los dos en el LTU .110, todo restaurado. Leer antes de usar /proc/net/uph_wifi0/info o retomar ciclos de TCP en el banco. -->

# Stage 2324A: info y noack_info del driver uph, dispositivo de caracteres y ciclo early_retrans

## 1. Resumen ejecutivo

- La ruta pedida `/proc/uph_wifi0/` no existe en ningun radio. Los archivos estan en
  `/proc/net/uph_wifi0/info` y `/proc/net/uph_wifi0/noack_info`, ambos con permisos 0444.
- `info` es una tabla que arma el driver: estaciones, tasas promedio, capacidad y uso del aire.
  `noack_info` no imprimio nada en ningun radio.
- El dispositivo de caracteres del driver es el mayor 190 `ubnt_poll_host` y se ve en userspace como
  `/dev/uph_wifi0` (190,0). El LTU no lo tiene: registra sus propios dispositivos `ame_*`.
- `tcp_early_retrans` y `tcp_thin_linear_timeouts` no existen en los XC (kernel 2.6.32). El ciclo corrio
  los dos ajustes en el LTU .110 y los restauro.

## 2. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex y sin leer archivos de RE binario. Una sesion
SSH por radio. Los AP de produccion solo se leyeron, con `assert_read_only` antes de abrir el socket.

Las muestras de `info` y `noack_info` (2048 bytes) se limpiaron en el propio radio antes de salir: MAC
a `[MAC]`, IP a `[IP]`, y todas las letras pasan a `x` salvo en las filas de rotulos de la tabla
(empiezan con `|` y no tienen digitos). Asi un nombre de estacion en una fila de datos no puede salir
del equipo. En esta captura no aparecio ninguna MAC ni IP.

En el banco solo se escribieron sysctls en RAM con watchdog de 60 s y relectura final. Cero Flash, RF,
canal, GPIO o atpc.

## 3. 2322A: los archivos del driver uph

| Radio | info bytes / lineas | noack_info bytes | Permisos |
| --- | --- | --- | --- |
| Panel2 .82 | 526 / 11 | 0 | 0444 |
| Panel3 .83 | 526 / 11 | 0 | 0444 |
| Banco .198 | 778 / 14 | 0 | 0444 |
| Banco .253 | 778 / 14 | 0 | 0444 |

Rotulos de columnas que imprime el driver en `info`:

- Tabla de estaciones (solo en los paneles): STAs, ACTv, AVGTXRT, AVGRXRT.
- Tabla de capacidad (en los cuatro): DCAPKBPS, UCAPKBPS, DCAP, UCAP, TXPER, RXPER, TXUSE, RXUSE, TLUSE.
- Los XC del banco suman una tabla por anchos de canal con todos los valores en cero.

Valores de los paneles en este instante (frecuencia y ancho salen de la primera linea):

| Panel | Frecuencia | Ancho | STAs | ACTv | AVGTXRT | AVGRXRT | DCAPKBPS | UCAPKBPS | TXUSE | RXUSE | TLUSE |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | 5805 | 20 | 7 | 0 | 116071 | 118857 | 96338 | 96274 | 452 | 16 | 468 |
| Panel3 .83 | 5755 | 20 | 3 | 1 | 138666 | 121333 | 108159 | 99493 | 35 | 8 | 43 |

El significado exacto de cada columna (unidades de TXUSE, TLUSE y TXPER) no esta decodificado; solo se
leen los rotulos del driver.

## 4. 2322A: dispositivo de caracteres

| Radio | /proc/devices | Nodo en /dev |
| --- | --- | --- |
| Panel2, Panel3, .198, .253 | 190 ubnt_poll_host | /dev/uph_wifi0, caracter 190,0, crw-r--r-- |
| LTU .110 | sin ubnt_poll_host | ame_dfs_dev, ame_fty_dev, ame_debug_dev, ame_bist_dev, ame_ctrl_dev |

Co-temporal: Panel2 sigue con 184548 descartes en la clase :2 de ath0 y Panel3 con 43817. Panel1: eth0
con 656 rx_fifo_errors y 0 tramas de pausa recibidas.

Veredicto del recibo: `BRIEF_PATH_ABSENT_FILES_UNDER_PROC_NET+FILES_0444+NOACK_INFO_EMPTY+CDEV_190_UBNT_POLL_HOST_DEV_UPH_WIFI0`.

## 5. 2323A: ciclo tcp_early_retrans / tcp_thin_linear_timeouts

La tarea pedia una iteracion en .198, otra en .253 y otra en .110. En los XC (kernel 2.6.32) no existe
ninguno de los dos sysctl: la prueba de solo lectura en .198 y .253 quedo guardada en la captura. El
ciclo corrio los dos ajustes en el LTU .110, unico kernel que los tiene (3.14), con A1, B1, A2, B2,
watchdog de 60 s, relectura final y ventanas OTA de solo lectura en Panel1 .84.

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .110 LTU | tcp_early_retrans | 3 | 0 | 3 | si | 3.46 | 29.49 | keep |
| 2 | .110 LTU | tcp_thin_linear_timeouts | 0 | 1 | 0 | si | 1.50 | 15.40 | keep |
| sin ejecutar | .198 XC | los dos | ausentes | - | - | - | - | - | - |
| sin ejecutar | .253 XC | los dos | ausentes | - | - | - | - | - | - |

Filas agregadas: `s2323a_iter1_110` y `s2323a_iter2_110` en `artifacts/autoresearch/results.tsv` y
`S2323A_ITER1_110` y `S2323A_ITER2_110` en `orchestration/autoresearch/results.tsv` (CRLF); las filas de
otros carriles se conservaron.

El banco no carga trafico: el ciclo prueba escritura y restauracion seguras, no un efecto.

## 6. Lo que queda abierto

- Decodificar las unidades de TXUSE, RXUSE, TLUSE y TXPER de la tabla `info`.
- Ver si `noack_info` imprime algo con el modo noack activo o con carga.
- Que publica el driver por `/dev/uph_wifi0` (no se leyo ni se abrio el dispositivo).

## 7. Recibos

- `artifacts/autoresearch/stage2322a_live_guarida_and_bench_uph_info_noack_and_cdev_audit_receipt.json`
- `artifacts/autoresearch/stage2323a_live_xc_ltu_tcp_early_retrans_and_thin_lto_cycle_receipt.json`
- `artifacts/verification/stage2327a_wave214_opus1_gate.json`
