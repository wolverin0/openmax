<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Wave 180 (2118A-2123A) sintesis ES: nota #635 une la auditoria de solo lectura del proceso ubntspecd 2058A (cambios de contexto por proceso: 100 a 130 por segundo con -a sin importar la IRQ espectral, 2 por segundo con -g; switch confundido con firmware; lanzador inittab segun la correccion <memorymaster-id>) y el ciclo reversible 2083A (wmem_default, tcp_keepalive_time; todo restaurado; la iteracion 1 repite 1951A); piso de ruido de 18 pliegues; banda :8787 a 1536A..2123A; SIN campeon -->
# Reporte ejecutivo - Nota #635: cambios de contexto de ubntspecd y ciclo wmem_default / tcp_keepalive_time

**Wave 180 - Etapas 2118A-2123A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron 2 recibos primarios en vivo (stage2058A de la Wave 170 y stage2083A de la Wave 174) en la
nota evergreen #635, se regeneraron las paginas de indice del vault (research/index/*.md), el feed del
Command Center :8787 se amplio a 1536A..2123A y las tres docs maestras siguen en 179 lineas o menos con 0
apellidos del alcance. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda
aplicado.

Aclaraciones sobre el pedido:

- 2058A es sobre todo una auditoria de cmdline, descriptores, mapas y configuracion de ubntspecd. Sus
  cambios de contexto son contadores **por proceso** de ubntspecd (una ventana de 10 s por radio), no una
  tasa de cambios de contexto de todo el sistema.
- 2058A es de **solo lectura** (0 escrituras de configuracion, 0 procesos senalizados); 2083A es un ciclo
  de escritura y restauracion en RAM, no telemetria.

## stage2058A - cambios de contexto de ubntspecd (por proceso)

- XC .198 (8.7.25, -a): 128.8 voluntarios por segundo, 3.0 involuntarios, IRQ espectral 16.5 por segundo.
- Panel2 .82 (8.7.25, -a): 111.9 voluntarios, 13.2 involuntarios, IRQ espectral 2363.6 por segundo.
- Panel3 .83 (8.7.25, -a): 99.7 voluntarios, 8.2 involuntarios, IRQ espectral 4233.8 por segundo.
- XC .253 (8.7.11, -g, quieto): 2.0 voluntarios, 4.2 involuntarios.
- Sin ubntspecd en OpenWrt .84 ni en LTU .110. Cada instancia: 1 hilo, 7 descriptores, durmiendo en
  poll_schedule_timeout.
- En los tres radios con -a la IRQ espectral varia unas 256.6 veces (16.5 a 4233.8 por segundo) y los
  cambios de contexto voluntarios solo 1.29 veces (99.7 a 128.8). Lectura INFERIDA: la tasa de
  despertares no sigue a la IRQ espectral; coincide con un bucle de poll con timeout y no con un despertar
  por IRQ. No se trazo nada.
- El unico campo que distingue a los activos del quieto es la cmdline (-a frente a -g), y el switch esta
  **confundido con el firmware** (8.7.25 frente a 8.7.11), como dice el propio recibo. La semantica de los
  demas switches es DESCONOCIDA.
- No hubo contadores de syscalls ni de E/S legibles en ningun host.

## Correccion posterior (<memorymaster-id>, Wave 174)

2058A dice que ningun script de texto lanza ubntspecd. Eso quedo **superado** para .198 por el claim
candidato <memorymaster-id> de MemoryMaster (lectura en vivo, sin recibo en disco): /etc/inittab tiene una linea
respawn para la instancia -a, asi que init la reinicia si se la mata; SIGSTOP la pausa sin respawn. Los
paneles no se volvieron a leer.

## Segunda foto de solo lectura de los paneles (1986A, fuera de este conjunto)

2058A corrio 39.3 minutos despues de 1986A. IRQ espectral de Panel2: 1999.8 por segundo (promedio de 3
ventanas) frente a 2363.6 (una ventana), mas 18.2 por ciento; Panel3: 3716.47 frente a 4233.8, mas 13.9
por ciento. Es variacion en el tiempo, una ventana frente a un promedio de tres.

## stage2083A - ciclo wmem_default / tcp_keepalive_time

- A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de iteraciones.
- Iteracion 1: wmem_default 131072 -> 163840 en XC .198; lectura final 131072.
- Iteracion 2: tcp_keepalive_time 7200 -> 3600 en XC .253; lectura final 7200.
- Iteracion 3: wmem_default 163840 -> 131072 en LTU .110; lectura final 163840; el harness la descarto.
- Las tres escrituras tuvieron efecto y **todas se restauraron**; 0 escrituras a flash, RF sin arrancar.
- Valores leidos antes de escribir: wmem_default XC .198 con 131072 y LTU .110 con 163840 (la misma
  division que rmem_default en la nota #634); tcp_keepalive_time XC .253 con 7200; en LTU no se leyo.

## Escritura repetida y el patron de objetivos nuevos

La iteracion 1 de 2083A (wmem_default 131072 -> 163840 en .198) repite la iteracion 1 de 1951A en el
mismo host con los mismos valores. En 2 de los 6 ciclos de banco (2059A y 2083A) el recibo dice que
prueba objetivos nuevos mientras la iteracion 1 repite exactamente un ciclo anterior (2059A repite
1915A, 2083A repite 1951A). No se cambio nada en tools/bench.

## Piso de ruido ambiente (6 ciclos, 18 pliegues)

No es un test A/A controlado:

- fmx_loss de 0.603602 a 0.894905; p95 de RTT de cpe_41 de 11.858 a 31.542 ms.
- goodput de 0.009 a 1.976 Mbps, trafico ambiente del enlace .84 sin carga inyectada.
- Ancla sin escrituras: durante 2058A, sin ninguna escritura, el p95 de cpe_41 fue **34.08 ms**, por
  encima de todos los pliegues de los ciclos (misma herramienta de medicion, no la misma estructura de
  rondas).
- Por eso la mejora de fmx_loss de la iteracion 2 de 2083A es ruido ambiente: no se atribuye mejora ni
  perjuicio.

## Cita de catalogo

2083A vuelve a citar s017 y s020, que son entradas del modulo ubnt_poll_host.ko, no knobs sysctl.

## recall-first

Antes de escribir la nota, 3 de 6 consultas al vault unificado tuvieron aciertos: ubntspecd 9, context
switch 11 e inittab 4; voluntary_ctxt, wmem_default y tcp_keepalive_time 0. No se corrio chequeo
scholar en esta wave (no se pidio).

## Etapa 2118A - vault

La nota #635 quedo en research/notes/scholar_sources/ como evergreen. Se corrio `hyperresearch sync` y
despues `hyperresearch index build`; _recent.md y 11 paginas de tag listan la nota. Conteo observado:
655 antes, 656 despues de sincronizar y 661 despues del index build, que suma 5 paginas de indice al
conteo del vault.

## Etapa 2119A - banda 1536A..2123A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (257 recibos en la banda) con
0 apellidos del alcance y 0 alias en toda la pagina; 2058A, 2083A y 2118A aparecen en el feed con su
propia clase de evidencia, y entraron 8 recibos (2100A a 2118A) que estaban sobre el tope anterior de
2099. Ningun recibo supera 2123A todavia. El servidor :8787 responde HTTP 200 y sirve la banda nueva.
MASTER, CURRENT y CURATED ya estaban en 179 lineas, asi que ninguna se reescribio.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- Los cambios de contexto son de un solo proceso y de una ventana por radio.
- No se atribuye efecto en el aire: el enlace medido nunca paso trafico por un host de knob.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Un A/B controlado con SIGSTOP de ubntspecd en un solo panel (matarlo solo dispara el respawn de
  inittab).
- Un A/B con carga inyectada en un AP cargado donde el host del knob reenvie el trafico medido.
- Revisar por que el generador de ciclos repite la iteracion 1 mientras dice probar objetivos nuevos.

Recibos: `stage2118a_ctxt_switch_and_wmem_keepalive_telemetry_note635_receipt.json`,
`stage2119a_command_center_1536a_2123a_refresh_receipt.json`, `stage2121a_memorymaster_ingest_receipt.json`,
`stage2123a_wave180_opus2_gate.json`.
