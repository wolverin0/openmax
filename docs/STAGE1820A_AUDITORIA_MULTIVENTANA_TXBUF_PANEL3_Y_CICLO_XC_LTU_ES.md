<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 130 (1818A-1823A) carril 3. Caracterizacion multi-ventana read-only del descarte 'no tx buffer' en Panel3-Guarida .83 (3 ventanas de 10s: resulta CONTINUO, no una rafaga), chequeo de salud de los 3 CPEs de Panel1 .84, y ciclo finito de 3 iteraciones A1-B1-A2-B2 (STOP_MAX_ITERATIONS) con knobs queue/sysctl seguros reversibles en RAM y watchdog 60s en XC .198/.253 y LTU .110. Ningun knob PROTECTED de 1776A/1789A fue escrito. Leer antes de tocar la cola de Panel3 o el banco LTU/XC. -->

# Stage 1820A: auditoria multi-ventana del buffer de TX en Panel3 y ciclo XC/LTU

## 1. Alcance y seguridad

Carril 3, hardware real, sin simulacion. Los AP de produccion `198.18.0.7` (Panel1) y
`198.18.0.6` (Panel3) son solo-lectura: la guarda `assert_read_only` rechaza antes de abrir el
socket cualquier `uci set`, `iw ... set`, `tc` de cambio, `wifi`, redireccion a archivo o reinicio
de servicio. En los radios de banco `.198`, `.253` y `.110` solo se escriben knobs en RAM, con un
watchdog de 60 s en el propio equipo y una relectura final que confirma el valor original. Cero
Flash, cero RF, cero cambio de canal, cero GPIO, cero atpc. Estaciones por octeto de IP.

## 2. Panel3 .83: el descarte de buffer es continuo (1818A)

La Wave 122 vio en una sola ventana de 11 s que cerca del 3,8 por ciento de las tramas fallaba por
falta de buffer de TX. Aqui se tomaron 4 capturas en una misma sesion con pausas en el propio
equipo, dando 3 ventanas contiguas de 10 s, para distinguir si es continuo o una rafaga:

| Ventana | Enviadas | no tx buffer | Tasa | demasiados reintentos | beacon miss |
| :-- | :-- | :-- | :-- | :-- | :-- |
| W1 | 84 484 | 1 537 | 1,82 % | 92 | 1 641 |
| W2 | 37 296 | 1 242 | 3,33 % | 15 | 1 258 |
| W3 | 53 419 | 1 461 | 2,74 % | 74 | 1 536 |

Veredicto: CONTINUO. Las tres ventanas tienen descarte, con una dispersion max/min de 1,83 (por
debajo del umbral 3,0 que separa continuo de rafaga). No es un pico aislado: el agotamiento de
buffer de TX esta presente de forma sostenida. Los sysctls de cola se mantuvieron estables entre
capturas (netdev_max_backlog 1000, wmem_default/max 118784, txqlen ath0/eth0 1000). Esto es una
observacion, no un diagnostico de causa: conviene una serie mas larga antes de tocar la cola.

## 3. Panel1 .84: los 3 CPEs siguen sanos (1818A)

cpe_41 en VHT-MCS7, cpe_223 en MCS8, cpe_80 en MCS7, los tres NSS2 con el puerto de bridge en
forwarding y multicast_to_unicast activo. cpe_80 sigue recuperado.

## 4. Ciclo finito de 3 iteraciones (1819A, STOP_MAX_ITERATIONS)

Nota de procedencia importante: Stage 1789A rankeo 571 knobs del catalogo, pero su propio veredicto
es `automatic_execution_allowed=false` y marca todos los candidatos como PROTECTED /
QUALIFICATION_ONLY (swr_limit, sta_priority, adj_mcs, ampdu, retry...), con las colas de SAFE_RAM
vacias. Stage 1776A es RE estatico de A-MPDU/retry. Por lo tanto ninguno de los knobs de
1776A/1789A es un SAFE_RAM aprobado para escribir en vivo. Este ciclo usa, en cambio, 3 knobs
genericos de cola/sysctl de Linux, de la misma clase que el eje de ranking "queue residence" de
1789A, nunca un knob PROTECTED del catalogo.

| Iter | Radio | Knob | Clase | Base -> B -> final | goodput cpe_41 | p95 | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 | net.core.somaxconn | queue | 128 -> 256 -> 128 | 4,21 Mbps | 22,4 ms | keep |
| 2 | .253 | net.core.wmem_default | sysctl | 120832 -> 131072 -> 120832 | 2,25 Mbps | 5,8 ms | keep |
| 3 | .110 | net.core.netdev_max_backlog | queue | 2500 -> 2000 -> 2500 | 0,28 Mbps | 20,1 ms | discard |

Cada knob se escribio en RAM, se confirmo que la escritura tomo efecto y la relectura final lo dejo
en su valor original, todo bajo watchdog de 60 s. La RF de `.110` quedo apagada, asi que su knob no
tiene efecto en el aire: el ciclo prueba escritura y restauracion seguras. El goodput es trafico
ambiente medido con los contadores del AP, no una carga inyectada; lo util es RTT, jitter, perdida
y RSSI. Los radios de banco no tienen par aire.

## 5. results.tsv

Se agregaron 3 filas finitas `s1819a_iter1_198`, `s1819a_iter2_253` y `s1819a_iter3_110` en el
dominio D3, con motivo de parada STOP_MAX_ITERATIONS. Las filas de waves anteriores quedaron
intactas y el encabezado sigue siendo unico.

## 6. Verificacion

La auditoria estricta de 5 pilares pasa en 1818A, y el gate
`enforce_5pillar_research_gate.py --require-live-hardware` pasa en 1819A sin problemas ni senales de
juego. Pilares: A catalogo revisado (sin SAFE_RAM aprobado) mas superficie generica de Linux; B
reactor cerrado contra la ventana unica de 1770A; C rondas contrabalanceadas y multi-ventana con
watchdog de 60 s; D tasas por ventana y p95 por iteracion; E claims FMX-1818A y FMX-1819A en
MemoryMaster. La suite `tests/test_stage1818a_to_1823a_suite.py` y el gate
`tools/verify/verify_stage1823a_wave130_opus1_gate.py` los escribieron dos workers codex
gpt-6-astra en paralelo (sandbox workspace-write); el carril los reviso y los corrio antes de
reportar.

## 7. Limites

- Tres ventanas de 10 s describen este momento; falta una serie larga para el patron diario.
- Los contadores athstats son del driver del AP; no atribuyen el agotamiento de buffer por CPE.
- El umbral de clasificacion (max/min > 3,0) es una heuristica fija, no un modelo ajustado.
- 1776A/1789A no dieron ningun knob SAFE_RAM, asi que el catalogo queda sin probar por diseno.
- El ciclo cerro por STOP_MAX_ITERATIONS, no por alcanzar un objetivo de goodput.
