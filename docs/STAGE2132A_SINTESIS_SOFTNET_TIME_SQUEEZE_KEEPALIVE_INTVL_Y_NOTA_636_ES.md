<!-- doc-head: Wave 182 (2130A-2135A) sintesis ES: nota #636 une la auditoria de solo lectura softnet_stat y /proc/net/snmp 2106A (0 time_squeeze y 0 descartes en la ventana de 30 s en los seis radios; el squeeze de airOS 8 es desde el arranque; valores NAPI que confirman restauraciones anteriores; TCP del plano de gestion) y el ciclo reversible 2107A (tcp_keepalive_intvl, tcp_keepalive_probes; todo restaurado); piso de ruido de 21 pliegues; banda :8787 a 1536A..2135A; SIN campeon -->
# Reporte ejecutivo - Nota #636: softnet time_squeeze, /proc/net/snmp y ciclo tcp_keepalive_intvl / probes

**Wave 182 - Etapas 2130A-2135A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron 2 recibos primarios en vivo de la Wave 178 (stage2106A y stage2107A) en la nota evergreen
#636, se regeneraron las paginas de indice del vault (research/index/*.md), el feed del Command Center
:8787 se amplio a 1536A..2135A y las tres docs maestras siguen en 179 lineas o menos con 0 apellidos del
alcance. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda aplicado.

Aclaraciones sobre el pedido:

- 2106A es telemetria de **solo lectura** (0 escrituras, una ventana de 30 s entre 2 fotos mas los totales
  desde el arranque); 2107A es un ciclo de escritura y restauracion en RAM, no telemetria.
- El "time squeeze" fue 0 en la ventana de 30 s en los seis radios. Todas las cifras distintas de cero son
  totales **desde el arranque** (entre 12.7 h y 176.6 h de uptime).
- Los contadores TCP de /proc/net/snmp son las sesiones propias de cada radio (**plano de gestion**), no
  trafico de abonados.

## stage2106A - softnet_stat

- Panel2 .82 (airOS 8, 176.6 h): 83.98 squeeze por hora, 6.7 por millon de paquetes, 0 descartes.
- Panel3 .83 (airOS 8, 176.6 h): 48.96 por hora, 13.14 por millon, 0 descartes.
- Panel1 .84 (OpenWrt, 12.7 h): 0.24 por hora, 0.16 por millon, 0 descartes.
- XC .198 (36.9 h): 15.16 por hora, 123.03 por millon. XC .253 (89.4 h): 6.61 por hora, 35.22 por millon.
- LTU .110 (17.2 h): 0.06 por hora, 0.65 por millon, 1 descarte desde el arranque.
- En la ventana de 30 s, time_squeeze y descartes fueron **0 en los seis radios**.
- time_squeeze cuenta rondas NAPI cortadas por presupuesto o por limite de tiempo: la CPU se quedo sin
  tiempo de softirq, no se perdieron paquetes (los perdidos son la columna de descartes).
- Por hora el que mas squeeze tiene es Panel2; por millon de paquetes es el XC .198 casi sin trafico.
  Lectura INFERIDA: los squeeze los dispara el limite de tiempo de softirq y no el volumen; no medido.
- Los paneles OpenWrt y airOS difieren en firmware, kernel, estaciones, carga y uptime: **no es un A/B
  controlado**.
- Todas las tasas por hora, por millon y de la ventana se recalculan desde los contadores crudos y dan los
  mismos valores que el recibo.

## Valores NAPI: las restauraciones anteriores se confirman

En 5 de 5 pares (host, knob) que un ciclo anterior escribio, 2106A lee horas despues el mismo valor que el
ciclo leyo antes de escribir: netdev_budget .253 600 y .110 300 (1951A); dev_weight .198 96 y .110 64 y
netdev_max_backlog .253 768 (1987A). Los demas valores son primeras lecturas sin ciclo con que comparar.
netdev_budget 300 contra 600 ya tuvo su escritura y restauracion en el banco en 1951A; lo que falta es una
prueba con un AP cargado, no otro ciclo de banco.

## stage2106A - /proc/net/snmp (plano de gestion)

- Retransmisiones TCP desde el arranque: Panel2 5.2717 por ciento, Panel3 5.0201, OpenWrt 6.5598; 0 en la
  ventana. Son sesiones TCP propias de cada radio, no trafico de abonados.
- Panel2 abrio 42561 conexiones TCP salientes desde el arranque y Panel3 42559: una cada 14.9 s, y cayeron 2
  en cada ventana de 30 s. Lectura INFERIDA: un cliente periodico del plano de gestion; identidad
  DESCONOCIDA.

## stage2107A - ciclo tcp_keepalive_intvl / tcp_keepalive_probes

- A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de iteraciones.
- Iteracion 1: tcp_keepalive_intvl 75 -> 30 en XC .198; lectura final 75.
- Iteracion 2: tcp_keepalive_probes 9 -> 5 en XC .253; lectura final 9.
- Iteracion 3: tcp_keepalive_intvl 75 -> 30 en LTU .110; lectura final 75; el harness la descarto.
- Las tres escrituras tuvieron efecto y **todas se restauraron**; 0 escrituras a flash, RF sin arrancar.
- Ninguna escritura repite un ciclo anterior. El patron de "objetivos nuevos" sigue en 2 de 7 ciclos
  (2059A y 2083A).
- Valores de keepalive leidos antes de escribir (2083A y 2107A): time .253 7200; intvl .198 y .110 75;
  probes .253 9. Coinciden con los valores por defecto documentados de Linux (referencia del kernel, no
  medidos aqui). Los demas pares host y knob no se leyeron.

## Piso de ruido ambiente (7 ciclos, 21 pliegues)

No es un test A/A controlado:

- fmx_loss de 0.464441 a 0.894905; p95 de RTT de cpe_41 de 4.207 a 31.542 ms.
- goodput de 0.009 a 3.94 Mbps, trafico ambiente del enlace .84 sin carga inyectada.
- La iteracion 2 de 2107A tiene p95 de 4.207 ms, por debajo de todos los pliegues anteriores (minimo
  11.858 ms), con una escritura en un radio de banco sin par por aire: es ruido ambiente y el piso se
  ensancha otra vez. No se atribuye mejora ni perjuicio.
- El ancla sin escrituras (2058A, fuera de este conjunto) sigue en 34.08 ms, por encima de todos.

## Cita de catalogo

2107A vuelve a citar s017 y s020, que son entradas del modulo ubnt_poll_host.ko, no knobs sysctl.

## recall-first

Antes de escribir la nota, 3 de 6 consultas al vault unificado tuvieron aciertos: netdev_budget 3,
tcp_keepalive 1 y snmp 4; softnet_stat, time_squeeze y Tcp_ActiveOpens 0. No se corrio chequeo scholar
en esta wave (no se pidio).

## Etapa 2130A - vault

La nota #636 quedo en research/notes/scholar_sources/ como evergreen. Se corrio `hyperresearch sync` y
despues `hyperresearch index build`; 14 paginas de indice listan la nota (_recent.md y 10 de tag entre
ellas). La primera corrida vio 661 notas antes, 662 despues de sincronizar y 663 despues del index build;
el constructor se volvio a correr para corregir dos frases y esa corrida ve 663 antes y despues.

## Etapa 2131A - banda 1536A..2135A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (265 recibos en la banda) con
0 apellidos del alcance y 0 alias en toda la pagina; 2106A, 2107A y 2130A aparecen en el feed con su
propia clase de evidencia, y entraron 4 recibos (2124A a 2130A) sobre el tope anterior de 2123. Los
recibos 2136A, 2137A, 2139A y 2142A (de otra linea) quedan fuera a proposito. El servidor :8787 responde
HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED ya estaban en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- El squeeze alto de airOS 8 es historico y significa falta de tiempo de CPU, no perdida de paquetes.
- No se atribuye efecto en el aire: ninguna sesion dependiente de keepalive se observo.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Un A/B con carga inyectada en un panel (por ejemplo netdev_budget 300 contra 600) donde el host del knob
  reenvie el trafico medido.
- Identificar el cliente TCP periodico de los paneles, solo si importa para el plano de gestion.

Recibos: `stage2130a_softnet_time_squeeze_and_keepalive_intvl_telemetry_note636_receipt.json`,
`stage2131a_command_center_1536a_2135a_refresh_receipt.json`, `stage2133a_memorymaster_ingest_receipt.json`,
`stage2135a_wave182_opus2_gate.json`.
