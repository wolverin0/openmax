<!-- doc-head: Wave 184 (2142A-2147A). 2142A: auditoria de solo lectura de /proc/net/dev, /sys/class/net/*/statistics y qdisc (tc -s qdisc) con ventana de 30 s y totales desde el arranque en los 3 paneles de Guarida (.84 OpenWrt sin tc, .82 y .83 airOS 8) y en el banco (.198, .253, .110). En la ventana no hubo descartes de qdisc ni de interfaz fisica en ningun panel; desde el arranque los paneles airOS 8 acumulan descartes de qdisc de salida en ath0 (lado TX, distinto del backlog RX de 2106A). 2143A: ciclo finito de 3 iteraciones netdev_budget/netdev_max_backlog en RAM en .198/.253/.110, todo restaurado; la premisa de base 300 solo se cumplio en .110. Leer antes de proponer netdev_budget o txqueuelen para un panel. -->

# Stage 2144A: estadisticas netdev y qdisc en Guarida, y ciclo netdev_budget

## 1. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex. Los tres AP de produccion de Guarida solo se
leyeron: el comando paso por `assert_read_only` antes de abrir el socket y no hubo escrituras de
configuracion. En el banco solo se escribieron dos sysctls en RAM con watchdog de 60 s y relectura final
del valor original. Cero Flash, cero RF, cero canal, cero GPIO, cero atpc, cero knobs PROTECTED. No se
inyecto trafico: todo lo medido es carga ambiente.

## 2. 2142A: que se midio

Una sola sesion SSH por radio, las seis en paralelo, con dos instantaneas separadas por `sleep 30` en el
propio equipo:

- `/proc/net/dev` de todas las interfaces.
- `/sys/class/net/<if>/statistics/` para rx_dropped, rx_fifo_errors, rx_missed_errors, tx_dropped y
  collisions, mas `tx_queue_len`, en todas las interfaces salvo lo.
- `tc -s qdisc show`: bytes y paquetes enviados, dropped, overlimits y requeues por qdisc. Solo se
  suman las qdisc raiz (una raiz mq ya agrega a sus hijas). Panel1 OpenWrt no tiene `tc`.

Las interfaces se separan en fisicas (inalambrica y ethernet), puente y el radio padre `wifi0` de airOS.
Captura cruda: `artifacts/verification/wave184/2142a_netdev_20261028T072815Z.json` (sha256 en el recibo).

## 3. 2142A: resultados

| Radio | Uptime h | qdisc raiz inalambrica | txqueuelen inalambrica/eth0 | qdisc dropped desde arranque | por hora | requeues | qdisc dropped ventana |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 airOS 8 | 176.9 | ath0 mq | 1000 / 1000 | 184548 | 1043.09 | 2354 | 0 |
| Panel3 .83 airOS 8 | 176.9 | ath0 mq | 1000 / 1000 | 43598 | 246.42 | 2329 | 0 |
| Panel1 .84 OpenWrt | 13.1 | sin tc | 256 / 1000 | sin medir | sin medir | sin medir | sin medir |
| Banco .198 XC | 37.2 | ath0 mq | 1000 / 1000 | 0 | 0.0 | 0 | 0 |
| Banco .253 XC | 89.8 | ath0 mq | 1000 / 1000 | 0 | 0.0 | 0 | 0 |
| Banco .110 LTU | 17.6 | ath0 htb | 256 / 256 | 0 | 0.0 | 0 | 0 |

En Panel2 los descartes de qdisc son el 0.0224 % de lo enviado por ath0 desde el arranque; en Panel3 el
0.0192 %. La qdisc de eth0 (pfifo_fast) no descarto nada en ningun panel airOS.

Interfaces fisicas de los paneles (inalambrica mas eth0):

- En la ventana de 30 s: cero rx_dropped, tx_dropped, fifo, missed y colisiones en los tres paneles.
- Desde el arranque: Panel2 tiene 1 tx_dropped y Panel3 4; ninguno tiene fifo ni missed.
- Panel1 OpenWrt tiene 558 rx_fifo_errors en eth0 desde el arranque (desbordes de la FIFO de recepcion
  de la placa ethernet en 13.1 h), cero en la ventana. Es el unico contador de perdida fisica de los
  paneles distinto de cero.

Puente: el br-lan de Panel1 marca 14142 rx_dropped desde el arranque y 12 en la ventana; los br0 de
airOS marcan cero. En Linux ese contador del puente cuenta tramas para la pila local sin manejador de
protocolo, no trafico de abonados perdido, por eso se informa aparte.

Radio padre `wifi0` de airOS: Panel2 acumula 112593778 rx_dropped y Panel3 32216075, y en la ventana
crecieron 3321 y 712. Su tx_dropped bajo una unidad durante la ventana en Panel2 (contador no
monotono). El driver no documenta que cuenta ese contador: se registra y no se interpreta como perdida.

Veredicto del recibo: `NO_AIROS8_WINDOW_QDISC_DROPS+AIROS8_SINCE_BOOT_QDISC_DROPS+NO_PANEL_WINDOW_PHYS_DROPS+OPENWRT_QDISC_UNMEASURED`.

Lectura junto con 2106A:

- 2106A miro el lado de recepcion (backlog de softnet): cero descartes en los paneles. Esta etapa mira el
  lado de salida: los paneles airOS 8 si descartan en la qdisc de ath0, de forma acumulada y baja (dos
  centesimos de por ciento), y no en esta ventana.
- La comparacion de qdisc es solo entre radios airOS: OpenWrt no tiene `tc`, asi que su salida solo se
  ve por tx_dropped de sysfs, que esta en cero. No es una comparacion medida OpenWrt contra airOS.

## 4. 2143A: ciclo finito netdev_budget / netdev_max_backlog

La tarea pedia netdev_budget 300 a 600 en los tres radios del banco, por el hallazgo de 2106A (los
paneles airOS 8 corren 300 y OpenWrt 600). La premisa de base 300 solo se cumplio en .110: los XC ya
corren 600. Se resolvio asi, y cada iteracion del recibo registra si la premisa se cumplio:

- .198: netdev_budget 600 a 300. Mismo contraste 300 contra 600 en orden inverso; B reproduce el valor
  de los paneles.
- .253: netdev_max_backlog 768 a 1000, el valor de los paneles.
- .110: netdev_budget 300 a 600, el cambio literal de la tarea.

Mismo protocolo que 2107A: A1, B1, A2, B2 contrabalanceado, watchdog de 60 s por escritura en RAM,
relectura final y ventanas OTA de solo lectura en Panel1 .84. STOP_MAX_ITERATIONS con 3 iteraciones.

| Iteracion | Radio | Knob | Base | B | Final | Restaurado | Premisa 300 | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | netdev_budget | 600 | 300 | 600 | si | no | 0.26 | 3.95 | keep |
| 2 | .253 XC | netdev_max_backlog | 768 | 1000 | 768 | si | no aplica | 0.46 | 23.31 | discard |
| 3 | .110 LTU | netdev_budget | 300 | 600 | 300 | si | si | 1.20 | 17.93 | discard |

Las tres escrituras tomaron efecto y las tres se restauraron al valor original. Perdida ICMP de cpe_41 en
0 % en las tres; RSSI entre -49.5 y -49 dBm; MCS 7.

Filas agregadas: `s2143a_iter1_198`, `s2143a_iter2_253` y `s2143a_iter3_110` en
`artifacts/autoresearch/results.tsv` (12 columnas, LF) y `S2143A_ITER1_198` a `S2143A_ITER3_110` en
`orchestration/autoresearch/results.tsv` (4 columnas, CRLF). Las filas que otro carril agrego durante
esta wave se conservaron.

Los radios del banco no cargan trafico ni tienen par OTA: el ciclo prueba que los dos sysctls se escriben
y restauran con seguridad. No mide ningun efecto sobre time_squeeze. Los keep/discard reflejan el enlace
ambiente de .84, no el knob.

## 5. Lo que queda abierto

- Medir netdev_budget 300 contra 600 en un XC del banco con carga real y contar time_squeeze en cada
  fase, antes de proponerlo para un panel.
- Ver si los descartes de qdisc de ath0 en los paneles aparecen en hora pico: repetir 2142A entonces.
- Instalar o traer un `tc` estatico para medir la qdisc de Panel1 queda como decision del operador.
- Revisar la FIFO de eth0 de Panel1 (558 desbordes) contra el enlace cableado del panel.

## 6. Recibos

- `artifacts/autoresearch/stage2142a_live_guarida_and_bench_netdev_qdisc_stats_audit_receipt.json`
- `artifacts/autoresearch/stage2143a_live_xc_ltu_netdev_budget_and_backlog_cycle_receipt.json`
- `artifacts/verification/stage2147a_wave184_opus1_gate.json`
