<!-- doc-head: Wave 178 (2106A-2111A). 2106A: auditoria de solo lectura de /proc/net/softnet_stat (time_squeeze, dropped) y /proc/net/snmp en los 3 paneles de Guarida (.84 OpenWrt, .82 y .83 airOS 8) y en el banco (.198, .253, .110). En la ventana de 30 s no hubo time_squeeze ni descartes en ningun radio; desde el arranque los paneles airOS 8 acumulan time_squeeze muy por encima de OpenWrt, sin un solo descarte de backlog. 2107A: ciclo finito de 3 iteraciones tcp_keepalive_intvl/tcp_keepalive_probes en RAM en .198/.253/.110, todo restaurado. Leer antes de tocar dev_weight/netdev_budget en los paneles. -->

# Stage 2108A: softnet time_squeeze y SNMP en Guarida, y ciclo keepalive_intvl/probes

## 1. Alcance y seguridad

Carril opus1, hardware real, sin subtrabajadores Codex. Los tres AP de produccion de Guarida solo se
leyeron: el comando paso por `assert_read_only` antes de abrir el socket y no hubo escrituras de
configuracion. En el banco solo se escribieron dos sysctls en RAM con watchdog de 60 s y relectura final
del valor original. Cero Flash, cero RF, cero canal, cero GPIO, cero atpc, cero knobs PROTECTED. No se
inyecto trafico: todo lo medido es carga ambiente.

## 2. 2106A: que se midio

Una sola sesion SSH por radio, las seis en paralelo, con dos instantaneas separadas por `sleep 30` en el
propio equipo (una ventana exacta de unos 30 s):

- `/proc/net/softnet_stat`: por CPU, columnas 0 a 2 en hexadecimal (procesados, descartados,
  time_squeeze). El numero de columnas cambia con el kernel: 9 en 2.6.32, 11 en 3.14 y 15 en 6.6.
  Solo se comparan las tres primeras, que son estables.
- `/proc/net/snmp`: contadores Ip, Icmp, Tcp y Udp (RetransSegs, OutSegs, InErrs, InErrors,
  RcvbufErrors, InDiscards y otros).
- `/proc/sys/net/core/dev_weight`, `netdev_budget` y `netdev_max_backlog`.

Captura cruda: `artifacts/verification/wave178/2106a_softnet_20261028T070658Z.json` (sha256 fijado en el
recibo).

## 3. 2106A: resultados

| Radio | Kernel | CPU | dev_weight / budget / backlog | squeeze ventana | squeeze/h desde arranque | squeeze por millon de paquetes | descartes desde arranque |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Panel2 .82 airOS 8 WA | 2.6.32 | 1 | 64 / 300 / 1000 | 0 | 83.98 | 6.70 | 0 |
| Panel3 .83 airOS 8 WA | 2.6.32 | 1 | 64 / 300 / 1000 | 0 | 48.96 | 13.14 | 0 |
| Panel1 .84 OpenWrt 24.10 | 6.6 | 1 | 64 / 600 / 1000 | 0 | 0.24 | 0.16 | 0 |
| Banco .198 XC 8.7.25 | 2.6.32 | 1 | 96 / 600 / 1024 | 0 | 15.16 | 123.03 | 0 |
| Banco .253 XC 8.7.11 | 2.6.32 | 1 | 96 / 600 / 768 | 0 | 6.61 | 35.22 | 0 |
| Banco .110 LTU 2.4.0 | 3.14 | 2 | 64 / 300 / 2500 | 0 | 0.06 | 0.65 | 1 |

Uptime al medir: Panel2 y Panel3 176.6 h, Panel1 12.7 h, .198 36.9 h, .253 89.4 h, .110 17.2 h. Las
tasas desde el arranque estan normalizadas por uptime y por paquetes procesados, para que el reinicio
reciente de Panel1 no sesgue la comparacion.

Veredicto del recibo: `NO_WINDOW_SQUEEZE_OR_DROP+SINCE_BOOT_SQUEEZE_AIROS8_ABOVE_OPENWRT+GUARIDA_ZERO_SOFTNET_DROPS`.

Lectura:

- En la ventana de 30 s ningun radio tuvo time_squeeze ni descartes de backlog. Panel2 proceso unos
  2128 paquetes/s y Panel3 unos 703 paquetes/s en esa ventana, sin presion visible.
- Desde el arranque, Panel2 y Panel3 acumulan time_squeeze entre 42 y 82 veces mas por paquete que
  Panel1 OpenWrt. airOS 8 corre con `netdev_budget` 300 y OpenWrt con 600.
- Ningun panel de Guarida descarto un solo paquete en el backlog de softnet desde el arranque. El unico
  descarte de los seis radios es 1 en .110, en el banco.
- time_squeeze cuenta rondas NAPI cortadas por presupuesto o por tiempo: dice que la CPU se quedo sin
  tiempo de softirq en esa ronda, no que se perdio un paquete. Los paquetes perdidos son la columna de
  descartes, que esta en cero en los paneles.
- Los XC del banco, casi sin trafico, tienen la tasa por paquete mas alta (.198: 123 por millon). Eso
  sugiere que en airOS 2.6.32 el time_squeeze lo dispara sobre todo el limite de tiempo con la CPU
  ocupada en otra cosa, no el volumen de paquetes. Es una hipotesis, no una medicion.

SNMP desde el arranque, sin errores de entrada en ningun radio: Ip InHdrErrors, Ip InDiscards, Tcp InErrs,
Udp InErrors y Udp RcvbufErrors en cero en los seis. Retransmision TCP desde el arranque: Panel2 5.27 %,
Panel3 5.02 %, Panel1 6.56 %, banco por debajo de 0.4 %; en la ventana fue 0 en todos. Esos contadores
Tcp son las sesiones propias de cada radio (gestion), no el trafico de abonados que pasa por el puente.

Conclusion para el operador: no hay evidencia de que Panel2 o Panel3 pierdan paquetes en softnet. Hay
evidencia de que agotan el presupuesto de softirq con mucha mas frecuencia que OpenWrt. Subir
`netdev_budget` en los paneles es un candidato a probar en el banco primero, no una correccion probada.

## 4. 2107A: ciclo finito tcp_keepalive_intvl / tcp_keepalive_probes

Mismo protocolo que 2083A (que cicla tcp_keepalive_time): A1, B1, A2, B2 contrabalanceado, watchdog de
60 s por escritura en RAM, relectura final, y ventanas OTA de solo lectura en Panel1 .84 (cpe_41 en A,
cpe_223 en B, cpe_80 como sonda degradada). STOP_MAX_ITERATIONS con 3 iteraciones.

| Iteracion | Radio | Knob | Base | B | Final | Restaurado | cpe_41 Mbps | cpe_41 p95 ms | Estado |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | .198 XC | tcp_keepalive_intvl | 75 | 30 | 75 | si | 3.94 | 20.49 | keep |
| 2 | .253 XC | tcp_keepalive_probes | 9 | 5 | 9 | si | 1.39 | 4.21 | keep |
| 3 | .110 LTU | tcp_keepalive_intvl | 75 | 30 | 75 | si | 2.98 | 21.09 | discard |

Las tres escrituras tomaron efecto y las tres se restauraron al valor original (relectura final igual a
la base). Perdida ICMP de cpe_41 en 0 % en las tres; RSSI entre -51 y -50 dBm; MCS 7.

Filas agregadas: `s2107a_iter1_198`, `s2107a_iter2_253` y `s2107a_iter3_110` en
`artifacts/autoresearch/results.tsv` (tabla de 12 columnas, LF) y `S2107A_ITER1_198` a `S2107A_ITER3_110`
en `orchestration/autoresearch/results.tsv` (4 columnas, CRLF). Las filas que otro carril agrego al
mismo libro durante esta wave se conservaron.

Los radios del banco no tienen par OTA y ninguna sesion dependia del keepalive: el ciclo prueba que los
dos sysctls se escriben y restauran con seguridad. No mide un efecto en el aire. Los keep/discard de la
tabla reflejan el enlace ambiente de .84, no el knob.

## 5. Lo que queda abierto

- Una ventana de 30 s describe solo este momento. Repetir la captura en hora pico de Guarida.
- La comparacion OpenWrt contra airOS 8 mezcla firmware, kernel, estaciones y carga: es un contraste,
  no un A/B controlado.
- Probar `netdev_budget` 300 contra 600 en un XC del banco con carga, antes de proponerlo para un panel.
- Separar en airOS cuanto time_squeeze sale del limite de tiempo y cuanto del presupuesto requiere un
  kernel que exponga ese desglose; 2.6.32 no lo hace.

## 6. Recibos

- `artifacts/autoresearch/stage2106a_live_guarida_and_bench_softnet_snmp_audit_receipt.json`
- `artifacts/autoresearch/stage2107a_live_xc_ltu_keepalive_intvl_probes_cycle_receipt.json`
- `artifacts/verification/stage2111a_wave178_opus1_gate.json`
