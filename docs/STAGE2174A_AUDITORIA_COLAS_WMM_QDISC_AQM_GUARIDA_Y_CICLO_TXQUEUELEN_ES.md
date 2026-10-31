<!-- doc-head: Wave 189 (2172A-2177A). 2172A: auditoria de solo lectura por cola de ath0 (tc -s class / qdisc) en los airOS y el LTU, y AQM de mac80211 (debugfs) con FIFO de eth0 en OpenWrt .84. Todos los descartes y requeues de qdisc de ath0 de Panel2 y Panel3 estan en la clase mq :2, que lleva casi el 98 % de los paquetes; la AC de :2 no esta establecida. Las lineas de athstats que etapas previas leyeron como 'no tx buffer' siguen en vivo el contador de paquetes enviados de cada clase mq: son conteos de paquetes, no descartes. En OpenWrt los descartes AQM estan todos en BE y eth0 sumo 3 desbordes de FIFO en la ventana. 2173A: ciclo finito tx_queue_len/tcp_dsack en RAM en .198/.253/.110, todo restaurado. Leer antes de interpretar athstats o tocar tx_queue_len en un panel. -->

# Stage 2174A: colas WMM, qdisc y AQM en Guarida, y ciclo tx_queue_len

## 1. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex. Los tres AP de produccion de Guarida solo se
leyeron: el comando paso por `assert_read_only` antes de abrir el socket y no hubo escrituras. En el banco
solo se escribieron dos ajustes en RAM con watchdog de 60 s y relectura final del valor original. Cero
Flash, cero RF, cero canal, cero GPIO, cero atpc, cero knobs PROTECTED. No se inyecto trafico.

Correcciones al texto de la tarea, registradas en el recibo:

- ath0 en airOS tiene 5 clases mq (:1 a :5), no 4 subcolas WMM.
- La interfaz AP de OpenWrt es `netdev:phy0-ap0` (mas las WDS `phy0-ap0.staN`), no `netdev:wlan0`.
- .110 es LTU: su ath0 tiene una raiz htb con hojas fq_codel y su eth0 un mq de 8 colas.
- El nombre del archivo de 2173A dice tcp_sack; el cuerpo pide `tcp_dsack`, que es lo que se probo.

## 2. 2172A: que se midio

Una sesion SSH por radio, las seis en paralelo, dos instantaneas separadas por `sleep 30` en el equipo.

- airOS y LTU: `tc -s class show dev ath0`, luego `athstats`, luego otra vez `tc -s class show dev ath0`
  (la lectura de athstats queda entre dos lecturas de clases); ademas `tc -s qdisc show` de ath0, eth0
  y br0, `tc -s class show dev eth0` y tx_queue_len.
- OpenWrt: debugfs de mac80211 (`phy0/aqm`, `netdev:phy0-ap0/aqm` y el aqm de cada estacion sumado por
  AC sin imprimir MAC), limites AQL, contadores FIFO de eth0 en sysfs, `ethtool -S` y `-g`, e IRQ.

Captura cruda: `artifacts/verification/wave189/2172a_queues_20261028T075401Z.json` (sha256 en el recibo).

## 3. 2172A: descartes por cola en ath0

| Panel | Clase | Paquetes desde arranque | Parte % | Descartes | Requeues | Descartes ventana |
| --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 | :1 | 10628665 | 1.285 | 0 | 0 | 0 |
| Panel2 .82 | :2 | 807251050 | 97.623 | 184548 | 2354 | 0 |
| Panel2 .82 | :3 | 4643162 | 0.562 | 0 | 0 | 0 |
| Panel2 .82 | :4 | 4382560 | 0.53 | 0 | 0 | 0 |
| Panel2 .82 | :5 | 55 | 0.0 | 0 | 0 | 0 |
| Panel3 .83 | :1 | 1840203 | 0.808 | 0 | 0 | 0 |
| Panel3 .83 | :2 | 222560232 | 97.686 | 43598 | 2334 | 0 |
| Panel3 .83 | :3 | 679602 | 0.298 | 0 | 0 | 0 |
| Panel3 .83 | :4 | 2753069 | 1.208 | 0 | 0 | 0 |
| Panel3 .83 | :5 | 10 | 0.0 | 0 | 0 | 0 |

Todos los descartes y todos los requeues de la qdisc de ath0 estan en la clase :2, en los dos paneles.
En la ventana no hubo descartes; Panel3 sumo 2 requeues en :2.

Que AC es :2 no esta establecido. `tc` no muestra el mapa de cola a AC; el orden de mac80211 haria de
la cola 1 la VI y el orden WME_AC de Atheros la BK, mientras que :2 lleva casi todo el trafico, lo que
solo sugiere el camino best effort por defecto. Resolverlo requiere RE estatico de la seleccion de cola
del umac o una prueba en el banco con DSCP marcado.

## 4. 2172A: athstats no cuenta descartes

En cada instantanea, cada clase mq con mas de 1000 paquetes tiene una linea de athstats que coincide con
su contador de paquetes enviados, en Panel2 y en Panel3:

- :1 con "tx encapsulation failed"
- :2 con "tx failed 'cuz no tx buffer (data)" y con "tx failed 'cuz xmit filtered"
- :3 con "Number of times netif_wake called" y "tx frames with no ack marked"
- :4 con "tx failed 'cuz too many retries" y "tx frames with short preamble"

La prueba estricta (clase antes, athstats, clase despues, en orden) fallo: athstats va hasta 408 paquetes
por detras del contador de tc. Con una tolerancia de 10 ppm, fijada despues de ver ese resultado, todas
las clases coinciden; el error maximo observado es 1.833e-06. Con contadores de millones a cientos de
millones, una coincidencia asi no es casual. athstats imprime solo campos distintos de cero, por eso se
comparan valores y no numeros de linea.

Consecuencia: la linea "no tx buffer" de Panel2 y Panel3 es el contador de paquetes enviados de la clase
:2, no un contador de descartes ni de falta de buffers. Las etapas 1818A, 1830A y 1914A la leyeron como
agotamiento de buffers; 1938A y 1939A la habian rechazado como contador de descartes sin poder decir que
era. Esas etapas son de otros carriles: se senalan aqui y no se editan.

## 5. 2172A: OpenWrt .84

- Los descartes AQM de mac80211 por estacion suman 3794 desde el arranque (13.5 h), todos en BE (tid 0);
  una estacion tiene 3789 y otra 5, en orden de debugfs, sin MAC. Ninguno en la ventana.
- El contador `fq_overmemory` del phy marca 4055. Es otro contador; se informan los dos sin conciliarlos.
- Limites AQL activos (umbral 4000 us): BE 1500/3000 us, VI 1000/2000, VO 300/600, BK 500/1000.
- eth0: 585 rx_fifo_errors desde el arranque y 3 en esta ventana de 30 s, sobre 6225 paquetes recibidos.
  El anillo RX esta en 256, su maximo; TX en 128. El enlace es 1000 full y ethtool cuenta 2454 tramas de
  pausa respetadas. La placa ethernet se queda sin descriptores de recepcion de vez en cuando.

Los descartes de OpenWrt (FQ-CoDel por estacion y AC) y los de airOS (clase mq de ath0) son mecanismos
distintos: completan en parte el hueco `OPENWRT_QDISC_UNMEASURED` de 2142A, no los hacen comparables.

Veredicto del recibo: `AIROS8_ATH0_DROPS_ONLY_IN_CLASS_2+NO_WINDOW_CLASS_DROPS+ATHSTATS_TRACKS_MQ_CLASS_PKTS_WITH_LAG+OPENWRT_AQM_DROPS_ONLY_BE+OPENWRT_ETH0_FIFO_ERRORS_IN_WINDOW`.

## 6. 2173A: ciclo finito tx_queue_len / tcp_dsack

Mismo protocolo que 2143A: A1, B1, A2, B2 contrabalanceado, watchdog de 60 s por escritura en RAM,
relectura final y ventanas OTA de solo lectura en Panel1 .84. STOP_MAX_ITERATIONS con 3 iteraciones.

| Iteracion | Radio | Ajuste | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | ath0 tx_queue_len | 1000 | 256 | 1000 | si | 0.26 | 25.73 | keep |
| 2 | .253 XC | tcp_dsack | 1 | 0 | 1 | si | 0.15 | 17.66 | keep |
| 3 | .110 LTU | eth0 tx_queue_len | 256 | 1000 | 256 | si | 1.11 | 41.77 | discard |

En .198, B=256 reproduce el valor de phy0-ap0 de OpenWrt; en .110, B=1000 el de los paneles airOS.
tx_queue_len es un atributo del netdev de Linux: escribirlo en ath0 no toca RF, canal ni registros del
radio. Las tres escrituras tomaron efecto y las tres se restauraron. Perdida ICMP de cpe_41 en 0 %.

Filas agregadas: `s2173a_iter1_198`, `s2173a_iter2_253` y `s2173a_iter3_110` en
`artifacts/autoresearch/results.tsv` y `S2173A_ITER1_198` a `S2173A_ITER3_110` en
`orchestration/autoresearch/results.tsv`. Las filas de otros carriles agregadas durante la wave se
conservaron.

Los radios del banco no cargan trafico: el ciclo prueba escritura y restauracion seguras, no un efecto
sobre colas, descartes ni retransmisiones. Los keep/discard reflejan el enlace ambiente de .84.

## 7. Lo que queda abierto

- Establecer la AC de la clase :2 (RE de la seleccion de cola del umac o prueba con DSCP en el banco).
- Probar tx_queue_len 1000 contra 256 en un XC con carga y contar descartes de :2 en cada fase.
- Revisar la FIFO de eth0 de Panel1 contra el equipo del otro lado del cable (tramas de pausa).

## 8. Recibos

- `artifacts/autoresearch/stage2172a_live_guarida_and_bench_per_queue_qdisc_and_aqm_audit_receipt.json`
- `artifacts/autoresearch/stage2173a_live_xc_ltu_txqueuelen_and_tcp_sack_cycle_receipt.json`
- `artifacts/verification/stage2177a_wave189_opus1_gate.json`
