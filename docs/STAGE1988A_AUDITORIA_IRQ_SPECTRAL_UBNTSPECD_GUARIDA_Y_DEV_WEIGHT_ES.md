<!-- doc-head: Wave 158 (1986A-1991A) carril 3. Auditoria read-only de IRQ y softirq en los 3 paneles de Guarida (Panel1 .84 OpenWrt 24.10.4 contra Panel2 .82 y Panel3 .83 airOS 8 WA v8.7.25) y en el banco (.198/.253 XC, .110 LTU): la IRQ ath-spectral-filter dispara 2000 a 3700 por segundo en los paneles airOS, TASKLET cerca de 2800/s, softirq cerca del 10 por ciento de CPU contra 2 en OpenWrt, ubntspecd cerca del 2,7. Mas un ciclo finito de 3 iteraciones dev_weight/netdev_max_backlog en RAM en el banco real. Leer antes de atacar la CPU de los paneles airOS. -->

# Stage 1988A: IRQ spectral y ubntspecd en Guarida, y ciclo dev_weight

## 1. Alcance y seguridad

Carril 3, hardware real. Los AP de produccion `.84`, `.82` y `.83` son solo-lectura: la guarda
`assert_read_only` rechaza cualquier escritura antes de abrir el socket. 1986A tambien fue solo
lectura en el banco. En 1987A solo se escribieron sysctls en RAM con watchdog de 60 s y relectura
final del valor original. Cero Flash, cero RF, cero cambio de canal, cero GPIO, cero atpc.

## 2. Metodo (1986A)

En los seis radios, al mismo tiempo, cuatro capturas en una sola sesion con pausas de 10 s en el
equipo: `/proc/interrupts`, `/proc/softirqs`, `/proc/stat` y ticks por proceso (solo el nombre del
binario, sin argumentos). Asi salen tres ventanas exactas de 10 s por radio.

Deteccion de plataforma: los kernels de airOS tambien se compilan con toolchain OpenWrt, y Panel1
conserva un `/etc/version` viejo (WA.v8.3.2). Solo `/etc/openwrt_release` identifica OpenWrt real.

## 3. Resultados por radio (media de 3 ventanas)

| Radio | Sistema | spectral IRQ/s | wifi IRQ/s | TASKLET/s | NET_RX/s | softirq CPU | ubntspecd |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Panel2 .82 | airOS WA 8.7.25 | 2000 | 2347 | 2821 | 602 | 12,7 % | 2,9 % |
| Panel3 .83 | airOS WA 8.7.25 | 3716 | 2801 | 2815 | 78 | 7,5 % | 2,6 % |
| Panel1 .84 | OpenWrt 24.10.4 | 0 (no existe) | 135 | 0,2 | 226 | 2,2 % | no corre |
| .198 XC | airOS XC 8.7.25 | 17 | 457 | 466 | 7 | 2,4 % | 1,3 % |
| .253 XC | airOS 2XC 8.7.11 | 25 | 50 | 60 | 7 | 0,4 % | 0,0 % |
| .110 LTU | afltu 2.4.0 | 0 (no existe) | 0 (RF apagada) | 0 | 24 | 0,0 % | no corre |

La CPU ocupada total es parecida en Panel2 (20,3 %) y Panel1 (19,8 %), pero se reparte distinto: en
airOS la mayor parte es softirq; en OpenWrt el softirq es poco y el resto es otro tipo de trabajo.
La interrupcion por hardware en si cuesta poco (cerca del 1,6 % en airOS).

## 4. Lectura

- En los paneles airOS la IRQ `ath-spectral-filter` dispara mas que las IRQ de la radio
  (`wifi0`/`wifi1`). En los radios XC de banco, sin trafico, apenas pasa de 20 por segundo: la tasa
  crece con el entorno RF y el trafico real.
- TASKLET corre a unos 2800 por segundo en los dos paneles airOS y practicamente en cero en OpenWrt.
  Es el mayor componente del softirq de airOS.
- `ubntspecd`, el demonio de espectro, cuesta cerca del 2,7 por ciento de CPU en cada panel airOS y
  no existe en OpenWrt ni en el LTU.

Limite importante: los contadores de softirq son por tipo, no por origen. No se puede decir que
porcion del TASKLET viene de la IRQ spectral y cual de la radio. Ademas Panel1 y los paneles airOS
tienen distintas estaciones y carga, asi que la comparacion es un contraste, no un A/B controlado.
Para atribuir el costo haria falta apagar el analisis espectral en un panel, algo que esta wave no
hizo porque los paneles son solo-lectura.

## 5. Ciclo finito de 3 iteraciones (1987A, STOP_MAX_ITERATIONS)

| Iter | Radio | Knob | Base -> B -> final | goodput cpe_41 | p95 | fmx_loss | estado |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | .198 XC | net.core.dev_weight | 96 -> 64 -> 96 | 0,03 Mbps | 30,0 ms | 0,874 | keep |
| 2 | .253 XC | net.core.netdev_max_backlog | 768 -> 1024 -> 768 | 0,08 Mbps | 21,6 ms | 0,818 | keep |
| 3 | .110 LTU | net.core.dev_weight | 64 -> 96 -> 64 | 0,03 Mbps | 12,0 ms | 0,612 | keep |

Las tres escrituras tomaron efecto y la relectura final devolvio el valor original. dev_weight es la
cuota de paquetes por pasada NAPI y netdev_max_backlog la cola de entrada por CPU, los dos del camino
NET_RX. Aqui solo se probo que se pueden escribir y restaurar sin riesgo en el banco: los radios de
banco no tienen par aire y el goodput es trafico ambiente del enlace `.84`, asi que keep refleja ese
trafico y no el knob. cpe_80 se mantuvo en MCS7 sin perdida.

## 6. results.tsv

Se agregaron 3 filas finitas `s1987a_iter1_198`, `s1987a_iter2_253` y `s1987a_iter3_110`. Las
filas de waves anteriores quedaron intactas y el encabezado sigue siendo unico.

## 7. Verificacion

1986A pasa la auditoria estricta de 5 pilares y 1987A pasa
`enforce_5pillar_research_gate.py --require-live-hardware`, sin senales de juego. Pilar E: claims
FMX-1986A y FMX-1987A en MemoryMaster. Sin workers codex: la suite
`tests/test_stage1986a_to_1991a_suite.py` y el gate `tools/verify/verify_stage1991a_wave158_opus1_gate.py`
los escribio y corrio el carril.

## 8. Limites

- Tres ventanas de 10 s describen este momento; falta una serie en hora pico.
- El costo del softirq no se puede repartir entre la IRQ spectral y la radio con estos contadores.
- dev_weight y netdev_max_backlog solo se probaron como escritura y restauracion segura en el banco.
