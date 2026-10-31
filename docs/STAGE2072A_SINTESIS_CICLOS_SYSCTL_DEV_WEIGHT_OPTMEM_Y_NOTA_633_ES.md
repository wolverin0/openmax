<!-- doc-head: Wave 172 (2070A-2075A) sintesis ES: nota #633 une los ciclos finitos en vivo 1987A (dev_weight, netdev_max_backlog) y 2017A (somaxconn, optmem_max) sobre XC .198/.253 y LTU .110; las 6 escrituras se restauraron; goodput de trafico ambiente del enlace .84, no se atribuye efecto en el aire; optmem_max en .253 repite 1915A; banda :8787 a 1536A..2075A; SIN campeon -->
# Reporte ejecutivo - Nota #633: ciclos sysctl net.core en XC y LTU

**Wave 172 - Etapas 2070A-2075A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron 2 recibos primarios en vivo (stage1987A de la Wave 158 y stage2017A de la Wave 163) en la
nota evergreen #633, se regeneraron las paginas de indice del vault (research/index/*.md), el feed del
Command Center :8787 se amplio a 1536A..2075A y las tres docs maestras siguen en 179 lineas o menos con 0
apellidos del alcance. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda
aplicado.

Aclaracion sobre el pedido: no es telemetria pasiva. Las dos etapas son ciclos finitos y reversibles de
escritura en RAM (A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de
iteraciones) sobre radios de banco, con el enlace de produccion Panel1 .84 medido en solo lectura.
"Verificado" significa que la escritura tuvo efecto y se restauro, no que mejore algo. Ademas el titulo
nombra dos knobs, pero se ciclaron cuatro.

## stage1987A - par del camino de recepcion

- Motivo del recibo: se eligieron tras ver carga de softirq NET_RX/TASKLET en airOS (1986A).
- Iteracion 1: dev_weight 96 -> 64 en XC .198; lectura final 96.
- Iteracion 2: netdev_max_backlog 768 -> 1024 en XC .253; lectura final 768.
- Iteracion 3: dev_weight 64 -> 96 en LTU .110; lectura final 64.
- dev_weight es la cuota de poll NAPI por dispositivo; netdev_max_backlog es la cola de entrada por CPU.
- fmx_loss bajo de 0.8737 a 0.6125 a lo largo de las iteraciones, pero eso es variacion del trafico
  ambiente, no una mejora causada por los knobs.

## stage2017A - par de control del plano de gestion

- Motivo del recibo: knobs de sockets de gestion, un par de control junto a los de recepcion de 1987A.
- Iteracion 1: somaxconn 128 -> 256 en XC .198; lectura final 128.
- Iteracion 2: optmem_max 10240 -> 20480 en XC .253; lectura final 10240.
- Iteracion 3: optmem_max 10240 -> 20480 en LTU .110; lectura final 10240.
- La iteracion 3 quedo marcada como descarte por el harness. Ese descarte es ruido ambiente, **no**
  prueba que optmem_max perjudique en LTU: la RF de .110 siguio estacionada y las radios de banco no
  tienen par por aire, asi que la escritura no podia llegar al aire medido.

## Valores leidos antes de cada escritura (XC vs LTU)

- dev_weight: XC .198 corria con **96** y LTU .110 con **64**: las dos plataformas usaban cuotas NAPI
  distintas en el momento de la lectura.
- netdev_max_backlog en XC .253: 768. somaxconn en XC .198: 128.
- optmem_max: 10240 tanto en XC .253 como en LTU .110.

## Dispersion ambiente en los 6 pliegues

No es un test A/A controlado, pero sirve como piso de ruido de este harness:

- fmx_loss de 0.612468 a 0.87373.
- p95 de RTT de cpe_41 de 12.004 a 29.96 ms.
- goodput de 0.014 a 0.083 Mbps, trafico ambiente sin carga inyectada.
- etiquetas del harness: 5 conservar y 1 descarte.

Cualquier reclamo futuro sobre este harness tiene que superar esa dispersion en un enlace donde el host
del knob este en el camino del trafico.

## Escritura repetida (fuera de este conjunto)

La iteracion 2 de 2017A (optmem_max 10240 -> 20480 en .253) repite la iteracion 2 de 1915A en el mismo
host con los mismos valores: es una segunda escritura y restauracion segura, no un knob nuevo.

## Cita de catalogo

Los dos recibos citan los ids de catalogo s017 y s020. En el catalogo de knobs esos ids son entradas del
modulo ubnt_poll_host.ko, no knobs sysctl: se leen solo como puntero de procedencia.

## recall-first

Antes de escribir la nota, 4 de 6 consultas al vault unificado tuvieron aciertos: dev_weight 1,
netdev_max_backlog 1, net.core sysctl 19 y NAPI 38; somaxconn y optmem_max 0 (especificos nuevos). No
se corrio chequeo scholar en esta wave (no se pidio).

## Etapa 2070A - vault

La nota #633 quedo en research/notes/scholar_sources/ como evergreen. Se corrio `hyperresearch sync` y
despues `hyperresearch index build`, que regenero research/index/*.md; _recent.md y las paginas de tag
futuramax, ltu, xc y recall-first listan la nota. Conteo observado: 652 antes y 653 despues en la
primera corrida; las re-corridas del constructor ven 653 antes y despues porque la nota ya estaba
sincronizada (el recibo guarda la ultima corrida).

## Etapa 2071A - banda 1536A..2075A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (237 recibos en la banda) con
0 apellidos del alcance y 0 alias en toda la pagina; 1987A, 2017A y 2070A aparecen en el feed con su
propia clase de evidencia, y entraron 12 recibos de las Waves 168 a 171 que estaban sobre el tope
anterior de 2045. Los recibos por encima de 2075A (2076A y siguientes, de otra linea) quedan fuera a
proposito. El servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED ya
estaban en 179 lineas, asi que ninguna se reescribio.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado: los cuatro knobs se restauraron; el ciclo prueba
  que escribir y restaurar es seguro, no que ayude.
- No se atribuye efecto en el aire ni perjuicio: el enlace medido nunca paso trafico por un host de knob.
- 0 escrituras a flash, RF sin arrancar, sin tocar atpc, AirPrism ni knobs PROTECTED del catalogo.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Un A/B con carga inyectada en un AP cargado donde el host del knob reenvie el trafico medido.
- Decidir si dev_weight 64 en LTU frente a 96 en XC merece una prueba dirigida.

Recibos: `stage2070a_sysctl_dev_weight_and_optmem_telemetry_note633_receipt.json`,
`stage2071a_command_center_1536a_2075a_refresh_receipt.json`, `stage2073a_memorymaster_ingest_receipt.json`,
`stage2075a_wave172_opus2_gate.json`.
