<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 152 (1950A-1955A) carril 3. (1) Redaccion de los campos JSON hostname/devicename de wstalist en 7 capturas crudas wave85..wave146 con el helper redact() compartido, re-pin de hashes hasta punto fijo (39 archivos, CRLF preservado, registros historicos congelados). (2) Auditoria read-only de CPU en Panel2 .82 y Panel3 .83: el 95 por ciento de 1914A era una muestra unica de mca-status al iniciar SSH; en ventanas de 10 s Panel2 esta cerca del 19 por ciento ocupado, con irq+softirq como mayor parte. (3) Ciclo finito de 3 iteraciones wmem_default/netdev_budget en RAM en el banco real .198/.253/.110 (las IPs del brief no son del banco). Leer antes de tocar capturas crudas o la CPU de Panel2. -->

# Stage 1952A: CPU de Panel2, redaccion JSON y ciclo wmem/netdev_budget

## 1. Alcance y seguridad

Carril 3, hardware real. Los AP de produccion `.84`, `.83` y `.82` son solo-lectura: la guarda
`assert_read_only` rechaza cualquier token de escritura antes de abrir el socket. En el banco solo
se escribieron sysctls en RAM con watchdog de 60 s y relectura final del valor original. Cero
Flash, cero RF, cero cambio de canal, cero GPIO, cero atpc, cero knobs PROTECTED. CPEs por octeto.

## 2. Redaccion de hostname en capturas crudas (1950A)

La Wave 146 encontro que `wstalist` de airOS devuelve JSON con `"hostname"` por estacion, que es el
nombre del equipo del abonado, y que `redact()` solo cubria la forma `clave=valor`. Se corrigio el
helper compartido `tools/bench/stage1548_1549_live_common.py`: ahora tambien redacta `"hostname"` y
`"devicename"` en JSON. El campo `"name"` se conserva porque en `wstalist` es el SSID del AP (un
solo valor para todas las estaciones), y 1614A lo usa como `ap_ssid`.

- Se revisaron las 14 capturas crudas de wave85 a wave146; 7 tenian nombres sin redactar (33
  valores). El brief pedia wave114 a wave146; wave85, wave96 y wave106 tenian el mismo campo, asi
  que tambien se redactaron. La captura de wave146 ya estaba limpia.
- Prueba de que solo cambiaron nombres: con los valores de hostname enmascarados, cada string es
  identico byte a byte antes y despues, y el esqueleto JSON no textual tambien. Cero apariciones
  residuales de los valores redactados. Los valores originales no se guardaron en ningun lado.

## 3. Re-pin de hashes hasta punto fijo

Cambiar una captura cambia su sha256, y varios recibos la fijan: los propios de cada wave, pero
tambien recibos y gates de otros carriles (1830A, 1835A, 1885A). Al re-fijar un recibo cambia su
propio hash, asi que la herramienta sigue la cadena hasta que ningun archivo vivo apunte a un hash
viejo. Resultado: 39 archivos en 5 rondas, todos con su formato exacto.

Dos errores del primer intento, corregidos antes de cerrar:

- `read_text()` normaliza CRLF, y 18 recibos de otros carriles son CRLF. El primer pase calculo
  hashes viejos falsos y guardo esos archivos como LF, lo que rompio la cadena 1843A a 1842A. Se
  restauraron desde copia y la herramienta ahora trabaja sobre bytes y conserva CRLF.
- El segundo pase reescribia registros historicos. Ahora quedan congelados las copias
  `_snapshot_`, `_attempt`, `before_fix`, las corridas de pytest con fecha y los propios ledgers de
  esta wave. Son 14 registros que siguen mostrando el hash que vieron en su momento.

Regresion: 78 suites de stage 1500 en adelante, 2804 pasan y 1 falla (`test_1591a_literal_is_named`,
un recibo del 27 de octubre que esta wave no toco). Los 7 gates del carril siguen en verde.

## 4. CPU de Panel2 .82 y Panel3 .83 (1950A)

Cuatro capturas en una sola sesion con pausas de 10 s en el equipo, sobre `/proc/stat`,
`/proc/softirqs`, `/proc/interrupts` y ticks por proceso (solo nombre del binario, sin argumentos):

| Panel | Ventanas ocupado | irq+softirq | system | user | mca-status inicio / fin |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Panel2 .82 | 19,5 / 16,8 / 19,5 % | 12,8 % | 2,6 % | 3,2 % | 59,0 / 19,8 % |
| Panel3 .83 | 15,8 / 16,2 / 11,8 % | 9,3 % | 2,6 % | 2,7 % | 35,6 / 7,9 % |

Veredicto: ninguno esta saturado. El 95 por ciento de 1914A fue una sola muestra de `mca-status`
tomada justo al iniciar la sesion SSH; aqui la primera muestra tambien sale alta (59 %) y la ultima
baja (19,8 %), mientras las ventanas medidas dan cerca del 19 %. Es consistente con que esa lectura
incluye el costo de abrir la sesion, no con carga sostenida.

En Panel2 el softirq TASKLET corre a unos 2600 por segundo y NET_RX a unos 580. Las IRQ mas activas
son `ath-spectral-filter` (unas 1900 por segundo) y `wifi0` (unas 1700). El proceso de usuario mas
pesado es `ubntspecd`, el demonio de espectro, con cerca del 2,6 por ciento.
Panel3 muestra el mismo patron con menos carga.

## 5. Ciclo finito de 3 iteraciones (1951A, STOP_MAX_ITERATIONS)

Procedencia de hosts: el brief nombro `198.18.0.126`, `.155` y `.50`. La `.155` es la PC del
operador (`infra/PLACEMENT.md` 1.4) y `.100`/`.50` no figuran en ningun inventario de banco; las tres
estan fuera de la lista permitida que aplica `L.run()`. El ciclo corrio en el banco XC/LTU real y
ninguna de esas IPs fue contactada.

| Iter | Radio | Knob | Base -> B -> final | goodput cpe_41 | p95 | fmx_loss | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 XC | net.core.wmem_default | 131072 -> 163840 -> 131072 | 0,10 Mbps | 31,5 ms | 0,883 | keep |
| 2 | .253 XC | net.core.netdev_budget | 600 -> 300 -> 600 | 0,03 Mbps | 18,6 ms | 0,770 | keep |
| 3 | .110 LTU | net.core.netdev_budget | 300 -> 600 -> 300 | 0,09 Mbps | 28,3 ms | 0,895 | discard |

Las tres escrituras tomaron efecto y la relectura final devolvio el valor original. netdev_budget
limita cuantos paquetes procesa cada pasada del softirq NET_RX, el componente que 1950A vio como mayor
parte de la CPU en Guarida. Aqui solo se probo que se puede escribir y restaurar sin riesgo en el banco: los
radios de banco no tienen par aire y el goodput es trafico ambiente del enlace `.84`, asi que keep o
discard refleja ese trafico y no el knob. cpe_80 se mantuvo en MCS7 sin perdida.

## 6. results.tsv

Se agregaron 3 filas finitas `s1951a_iter1_198`, `s1951a_iter2_253` y `s1951a_iter3_110`. Las
filas de waves anteriores quedaron intactas y el encabezado sigue siendo unico.

## 7. Verificacion

1950A pasa la auditoria estricta de 5 pilares y 1951A pasa
`enforce_5pillar_research_gate.py --require-live-hardware`, sin senales de juego. Pilar E: claims
FMX-1950A y FMX-1951A en MemoryMaster. Esta wave no uso workers codex: la suite
`tests/test_stage1950a_to_1955a_suite.py` y el gate `tools/verify/verify_stage1955a_wave152_opus1_gate.py`
los escribio y corrio el carril.

## 8. Limites

- Tres ventanas de 10 s describen este momento; falta una serie en hora pico para Panel2.
- Los ticks por proceso no atribuyen el softirq al proceso que lo causa.
- Que `mca-status` incluya el costo de la sesion SSH es una inferencia, no una prueba.
- netdev_budget solo se probo como escritura y restauracion segura; su efecto en un AP cargado no
  se midio.
