<!-- doc-head: Wave 176 (2094A-2099A) sintesis ES: nota #634 une la auditoria de IRQ en vivo de solo lectura 1986A (paneles airOS 8 dominados por TASKLET, OpenWrt por NET_RX, IRQ espectral 33.21 y 48.47 por ciento del conteo de IRQ en Panel2 y Panel3) y el ciclo reversible 2059A (rmem_default, tcp_fin_timeout; todo restaurado; la iteracion 1 repite 1915A); banda :8787 a 1536A..2099A; SIN campeon -->
# Reporte ejecutivo - Nota #634: auditoria de IRQ por tipo de softirq y ciclo rmem_default / tcp_fin_timeout

**Wave 176 - Etapas 2094A-2099A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron 2 recibos primarios en vivo (stage1986A de la Wave 158 y stage2059A de la Wave 170) en la
nota evergreen #634, se regeneraron las paginas de indice del vault (research/index/*.md), el feed del
Command Center :8787 se amplio a 1536A..2099A y las tres docs maestras siguen en 179 lineas o menos con 0
apellidos del alcance. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda
aplicado.

Aclaraciones sobre el pedido:

- El archivo de 1986A nombrado en el pedido no existe; el recibo real es
  `stage1986a_guarida_spectral_irq_and_ubntspecd_overhead_audit_receipt.json` y se resolvio por etapa.
- Los dos recibos son de distinto tipo: 1986A es telemetria de **solo lectura** (0 escrituras de
  configuracion); 2059A es un ciclo de escritura y restauracion en RAM, no telemetria.
- La nota #632 ya habia resumido las tasas de IRQ espectral de 1986A; la #634 agrega el desglose de
  softirq por tipo y la parte espectral del conteo de IRQ.

## stage1986A - softirq por tipo (promedio de 3 ventanas de 10 s)

- Panel2 .82 airOS 8 (kernel 2.6.32.68): NET_RX 601.97/s, TASKLET 2821.07/s, TIMER 994.77/s.
- Panel3 .83 airOS 8: NET_RX 78.4/s, TASKLET 2815.27/s, TIMER 996.23/s.
- Panel1 .84 OpenWrt (kernel 6.6.110): NET_RX 225.5/s, TASKLET 0.2/s, TIMER 14.17/s.
- Banco: XC .198 TASKLET 465.63/s, XC .253 TASKLET 59.73/s, LTU .110 TASKLET 0.03/s; TIMER cerca de
  1000/s en los tres.
- En los dos paneles airOS 8 domina TASKLET; en OpenWrt domina NET_RX.
- TIMER ronda 1000/s en los kernels 2.6.32.68 y 3.14.65 y 14.17/s en 6.6.110. Lectura INFERIDA: coincide
  con un tick periodico de 1000 Hz frente a un kernel sin tick fijo; no se leyo HZ ni NO_HZ.

## stage1986A - parte espectral del conteo de IRQ

- ath-spectral-filter es el 33.21 por ciento de todas las IRQ en Panel2 y el 48.47 por ciento en Panel3;
  0.99 y 1.95 por ciento en los XC del banco; 0 en OpenWrt y en LTU.
- Es una parte del **conteo** de IRQ, no del tiempo de CPU: el costo por IRQ no se midio.
- Advertencias del propio recibo: los contadores de softirq son por tipo, asi que la parte causada por la
  IRQ espectral **no es separable**; los paneles tienen estaciones y carga distintas, asi que el
  contraste **no es un A/B controlado**; ubntspecd no se detuvo.
- CPU ocupada 19.79 por ciento en OpenWrt frente a 17.33 por ciento de promedio en airOS 8, con unas 5432
  frente a 135 IRQ espectrales mas wifi por segundo: menos IRQ no implico menos CPU en esta foto.

## stage2059A - ciclo rmem_default / tcp_fin_timeout

- A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de iteraciones.
- Iteracion 1: rmem_default 131072 -> 163840 en XC .198; lectura final 131072.
- Iteracion 2: tcp_fin_timeout 15 -> 30 en XC .253; lectura final 15; el harness la marco como descarte.
- Iteracion 3: rmem_default 163840 -> 131072 en LTU .110; lectura final 163840.
- Las tres escrituras tuvieron efecto y **todas se restauraron**; 0 escrituras a flash, RF sin arrancar.
- Por semantica del kernel (no medido aqui), los dos knobs actuan sobre sockets que abre la propia radio;
  las tramas puenteadas de los abonados no pasan por un buffer de socket, asi que ninguno de los dos esta
  en el camino de IRQ y softirq medido en 1986A.

## Valores leidos antes de cada escritura (XC vs LTU)

- rmem_default: XC .198 corria con 131072 y LTU .110 con 163840.
- tcp_fin_timeout: XC .253 con 15 (2059A) y LTU .110 con 60 (1915A, fuera de este conjunto).
- Son valores en ejecucion al momento de la lectura, no valores de fabrica.

## Escritura repetida (fuera de este conjunto)

La iteracion 1 de 2059A (rmem_default 131072 -> 163840 en .198) repite la iteracion 1 de 1915A en el
mismo host con los mismos valores, aunque el recibo de 2059A dice que prueba objetivos nuevos.

## Piso de ruido ambiente (1987A + 2017A + 2059A, 9 pliegues)

No es un test A/A controlado:

- fmx_loss de 0.612468 a 0.893667; p95 de RTT de cpe_41 de 12.004 a 29.96 ms.
- goodput de 0.009 a 1.976 Mbps, trafico ambiente del enlace .84 sin carga inyectada.
- La mejora de fmx_loss de la iteracion 3 de 2059A coincide con una rafaga de goodput ambiente (1.976
  Mbps contra 0.083 como maximo en los otros pliegues), y el descarte de la iteracion 2 (0.893667) queda
  apenas por encima del maximo de la nota #633 (0.87373). Las dos cosas son ruido ambiente: no se atribuye
  mejora ni perjuicio.

## Cita de catalogo

2059A vuelve a citar s017 y s020, que son entradas del modulo ubnt_poll_host.ko, no knobs sysctl.

## recall-first

Antes de escribir la nota, 3 de 6 consultas al vault unificado tuvieron aciertos: TASKLET 1,
ath-spectral-filter 3 y softirq 47; rmem_default, tcp_fin_timeout y NET_RX 0. No se corrio chequeo
scholar en esta wave (no se pidio).

## Etapa 2094A - vault

La nota #634 quedo en research/notes/scholar_sources/ como evergreen. Se corrio `hyperresearch sync` y
despues `hyperresearch index build`; _recent.md y las paginas de tag (guarida, ath-spectral-filter,
futuramax, ltu, xc, recall-first) listan la nota. La primera corrida se corto en el chequeo de IP
completas despues de sincronizar la nota (la version de kernel 2.6.32.68 parecia una IP; se excluyo del
chequeo), asi que el recibo final ve 655 notas antes y despues.

## Etapa 2095A - banda 1536A..2099A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (247 recibos en la banda) con
0 apellidos del alcance y 0 alias en toda la pagina; 1986A, 2059A y 2094A aparecen en el feed con su
propia clase de evidencia, y entraron 8 recibos de las Waves 173 a 176 que estaban sobre el tope
anterior de 2075. 2100A (de otra linea) queda fuera a proposito. El servidor :8787 responde HTTP 200 y
sirve la banda nueva. MASTER, CURRENT y CURATED ya estaban en 179 lineas, asi que ninguna se reescribio.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- La parte espectral es del conteo de IRQ, no del tiempo de CPU, y la parte de softirq no es separable.
- No se atribuye efecto en el aire: el enlace medido nunca paso trafico por un host de knob.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Un A/B controlado de detener ubntspecd en un solo panel, para medir el costo de CPU de la IRQ espectral.
- Un A/B con carga inyectada en un AP cargado donde el host del knob reenvie el trafico medido.

Recibos: `stage2094a_irq_audit_and_rmem_fin_timeout_telemetry_note634_receipt.json`,
`stage2095a_command_center_1536a_2099a_refresh_receipt.json`, `stage2097a_memorymaster_ingest_receipt.json`,
`stage2099a_wave176_opus2_gate.json`.
