<!-- doc-head: Wave 163 (2016A-2021A) carril 3. Experimento controlado A1-B1-A2-B2 en el banco: pausa reversible de ubntspecd (SIGSTOP con restaurador en el equipo) en los XC .198 y .253, con el LTU .110 como control solo-lectura. En .198 pausar ubntspecd baja TASKLET de 381 a 44 por segundo y las IRQ de radio de 371 a 34, mientras ath-spectral-filter no cambia: el demonio genera trabajo de radio y TASKLET, no la IRQ spectral. Mas un ciclo finito somaxconn/optmem_max en RAM. Leer antes de proponer cambios a ubntspecd en los paneles airOS. -->

# Stage 2018A: atribucion A/B de ubntspecd en el banco y ciclo optmem

## 1. Alcance y seguridad

Carril 3, hardware real, solo banco para la intervencion. La pausa usa `kill`, que la guarda
`assert_read_only` rechaza en los AP de produccion `.84`, `.82` y `.83`: ningun panel se pauso.
En el banco, cada ventana B arma primero un restaurador desacoplado en el propio equipo
(`start-stop-daemon -b`: espera 60 s y manda `kill -CONT`), recien despues hace `kill -STOP`, mide,
manda CONT en la misma sesion y Python vuelve a mandar CONT desde un bloque `finally`. SIGSTOP deja
el proceso vivo, asi que nada lo reinicia. Cero Flash, cero RF, cero canal, cero GPIO, cero atpc.

## 2. Diseno (2016A)

Orden A1, B1, A2, B2 en cada XC. En A el demonio corre normal; en B esta en SIGSTOP. Cada ventana es
de 10 s con pausa en el equipo, sobre `/proc/interrupts`, `/proc/softirqs`, `/proc/stat` y ticks por
proceso. El LTU `.110` toma las mismas ventanas sin intervencion. El efecto es la media de B menos la
media de A; el ruido es la diferencia entre A1 y A2, y el orden cancela una deriva lineal. Se marca
"detectado" si el efecto supera dos veces el ruido y el 10 por ciento de A. Con dos ventanas por
brazo es un filtro, no una prueba de significancia.

Verificacion de la pausa: en las cuatro ventanas B el estado de ubntspecd fue T (detenido) al inicio
y al final, con cero ticks. Al terminar, los dos XC tienen ubntspecd corriendo con el mismo pid.

## 3. Resultados

| Radio | Metrica | A (corre) | B (pausado) | Cambio | Ruido A1-A2 | Detectado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| .198 XC 8.7.25 | TASKLET/s | 381 | 44 | -88 % | 6 | si |
| .198 XC 8.7.25 | IRQ radio wifi0/wifi1/s | 371 | 34 | -91 % | 6 | si |
| .198 XC 8.7.25 | ath-spectral-filter/s | 17,6 | 16,3 | -7 % | 0,5 | no |
| .198 XC 8.7.25 | softirq CPU | 1,9 % | 0,3 % | -84 % | 0,2 | si |
| .198 XC 8.7.25 | CPU ocupada | 5,0 % | 2,0 % | -59 % | 0,7 | si |
| .253 2XC 8.7.11 | TASKLET/s | 58 | 60 | +4 % | 9 | no |
| .253 2XC 8.7.11 | ath-spectral-filter/s | 24,0 | 24,1 | 0 % | 1,8 | no |
| .110 LTU control | NET_RX/s | 29 | 27 | -6 % | 3 | no |

Lectura: en el Rocket Prism (`.198`) ubntspecd es quien genera casi todo el trabajo de IRQ de radio
y de TASKLET. Lo mas probable es que consulte la radio todo el tiempo. Pero no es quien dispara
`ath-spectral-filter`, que sigue igual con el demonio pausado. En el Rocket 2AC (`.253`, firmware
8.7.11) el demonio casi no genera trabajo de radio y la pausa no cambia nada medible. El "detectado"
de softirq CPU en `.253` (0,30 a 0,35 %) es un artefacto de resolucion: un tick con ruido cero en
A. El LTU de control no cambio.

Que no se puede afirmar: en los paneles airOS el TASKLET corre a unos 2800/s y la spectral a 2000 a
3700/s (1986A), con trafico real. Esta prueba no pauso ningun panel, asi que no mide cuanto de esa
carga se iria. Si sugiere dos causas separadas: ubntspecd sobre TASKLET e IRQ de radio, y otra fuente
para la IRQ spectral.

Durante la prueba el enlace de produccion `.84` siguio sano (cpe_41 p95 19,1 ms, cpe_223 18,9 ms,
cpe_80 en MCS7 sin perdida). Es solo control de salud, no un resultado de la pausa.

Nota de proceso: la primera corrida se descarto. Un restaurador de 60 s que quedo de la prueba de
humo desperto ubntspecd en medio de una ventana B de `.253`. Se repitio todo pasado ese plazo.

## 4. Ciclo finito de 3 iteraciones (2017A, STOP_MAX_ITERATIONS)

| Iter | Radio | Knob | Base -> B -> final | goodput cpe_41 | p95 | fmx_loss | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 XC | net.core.somaxconn | 128 -> 256 -> 128 | 0,06 Mbps | 23,9 ms | 0,762 | keep |
| 2 | .253 XC | net.core.optmem_max | 10240 -> 20480 -> 10240 | 0,01 Mbps | 14,5 ms | 0,686 | keep |
| 3 | .110 LTU | net.core.optmem_max | 10240 -> 20480 -> 10240 | 0,01 Mbps | 22,1 ms | 0,782 | discard |

Las tres escrituras tomaron efecto y la relectura final devolvio el valor original. Son knobs de
sockets de gestion, fuera del camino de datos: el ciclo prueba escritura y restauracion seguras, y
keep o discard refleja el trafico ambiente del enlace `.84`, no el knob. cpe_80 se mantuvo en MCS7.

## 5. results.tsv

Se agregaron 3 filas finitas `s2017a_iter1_198`, `s2017a_iter2_253` y `s2017a_iter3_110`. Las
filas de waves anteriores quedaron intactas y el encabezado sigue siendo unico.

## 6. Verificacion

2016A y 2017A pasan `enforce_5pillar_research_gate.py --opus55-strict --require-live-hardware` sin
senales de juego. Pilar E: claims FMX-2016A y FMX-2017A en MemoryMaster. Sin workers codex: la
suite `tests/test_stage2016a_to_2021a_suite.py` y el gate `tools/verify/verify_stage2021a_wave163_opus1_gate.py`
los escribio y corrio el carril.

## 7. Siguiente paso posible

Para medir el efecto en carga real haria falta una pausa igual de corta y protegida en un panel
airOS. Eso es escribir en produccion: queda como decision del operador, no de este carril.
