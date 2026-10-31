<!-- doc-head: Wave 207 (2280A-2285A) sintesis ES: nota #642, sintesis longitudinal de las cinco auditorias de solo lectura 2106A, 2142A, 2172A, 2202A y 2256A de los seis radios en un mismo arranque (99 minutos): los errores de FIFO de eth0 de Panel1 siguen subiendo despacio; los descartes de salida de los paneles airOS estan en la clase :2 y no crecieron; los paneles corren dos perfiles de planificacion; el banco sin descartes de qdisc; la mayoria de las metricas son fotos unicas; banda :8787 a 1536A..2285A; SIN campeon -->
# Reporte ejecutivo - Nota #642: sintesis longitudinal de cinco auditorias

**Wave 207 - Etapas 2280A-2285A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron las cinco auditorias de solo lectura 2106A, 2142A, 2172A, 2202A y 2256A de Panel1 .84
(OpenWrt), Panel2 .82, Panel3 .83 (airOS 8) y el banco XC .198, XC .253 y LTU .110 en la nota evergreen #642.
Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2285A y
las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico
nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo las cinco auditorias. No se abrio ningun archivo de RE binario ni de desensamblado;
el constructor rechaza cualquier otro recibo.

Aclaraciones sobre el pedido:

- La mayoria de las metricas estan en **una sola auditoria** y son fotos, no tendencias: softnet (2106A),
  FQ-CoDel y athstats (2172A), FDB (2202A) y netconf (2256A). Solo el uptime, los errores de FIFO de Panel1,
  el contador de pausa, los descartes de ath0 y el vector uph aparecen en varias.
- El FQ-CoDel de OpenWrt viene por categoria de acceso (BE), no por TID.
- La correspondencia de athstats con la clase :2 se midio una sola vez (2172A).

## Mismo arranque

Las auditorias se tomaron en 0, 22, 48, 72 y 99 minutos. El uptime subio igual en todos los radios entre las
cuatro primeras (dispersiones 0.7, 0.6 y 0.6 s) y el de Panel1 otra vez en 2256A: **ningun radio se
reinicio**. 2256A no registro el uptime de los radios airOS.

## Panel1 .84 (OpenWrt)

- rx_fifo_errors de eth0: 558, 585, 596 y 612 (2142A a 2256A). Entre auditorias va de 26.1 a 62.8 por hora,
  alrededor del promedio desde el arranque (43.1 por hora): **una acumulacion lenta que continua**, causa
  DESCONOCIDA.
- "Tx Pause Frames Honored": 2172A tomo 2454 como total desde el arranque; 2202A y 2256A muestran que baja
  dos veces: **no es un total desde el arranque**. Las tramas de pausa recibidas siguen en 0: la pausa del
  par queda descartada.
- FQ-CoDel (solo 2172A): 3794 descartes BE sobre 16820301 paquetes (0.02256 por ciento), 0 marcas ECN.
- softnet (solo 2106A): 3 time_squeeze (0.24 por hora), 0 descartes de backlog.

## Panel2 .82 contra Panel3 .83 (airOS 8)

- Descartes de salida de ath0: 184548 y 43598 en 2142A, **sin cambio en 2172A** (0 nuevos). Requeues 2354 a
  2354 y 2329 a 2334. Todos en la clase :2 (97.623 y 97.686 por ciento de los paquetes).
- La linea de athstats "tx failed 'cuz no tx buffer (data)" es el contador de paquetes de la clase :2: un
  conteo de paquetes, no una tasa de descarte.
- softnet (solo 2106A): 83.98 y 48.96 squeeze por hora, 0 descartes de backlog.
- FDB (solo 2202A): 441 direcciones aprendidas en cada panel.
- netconf (solo 2256A): flags 137 contra 14864, down_dur 4880 contra 30000, up_dur 4370 contra 30000; Panel2
  usa campos ff_* y Panel3 campos hyb_*: **dos perfiles de planificacion**, unidades sin decodificar.
- Lectura INFERIDA: el panel con ff_* tambien tiene mas squeeze y mas descartes en la clase :2, pero lleva
  mucho mas trafico; **no es un A/B controlado** y no se establece ningun vinculo entre perfil y descartes.

## Banco XC .198, XC .253 y LTU .110

- Sin descartes de qdisc ni de clase en las dos auditorias que los midieron y sin descartes de interfaz en
  la ventana. Solo hay conteos desde el arranque: tx_dropped 78 y 11 en los XC; rx_dropped 7 y 1 descarte de
  backlog en el LTU.
- En XC .198 los dos subconjuntos de nombres de 2202A y 2256A imprimen vectores distintos; si cambio con el
  tiempo queda sin resolver (nota #643); causa
  DESCONOCIDA.

## recall-first

5 de 6 consultas al vault tuvieron aciertos (rx_fifo_errors, time_squeeze, mq class, netconf y fdb);
longitudinal, ninguno. No se corrio chequeo scholar (no se pidio).

## Etapas 2280A y 2281A

La nota #642 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. La primera corrida vio 678 notas antes y
683 despues; el constructor se volvio a correr para corregir tres frases sobre el banco y el ritmo de FIFO.
El tablero se reconstruyo con 341 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde
HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; ninguna auditoria escribio nada.
- Las metricas de una sola auditoria no muestran tendencias.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Repetir la auditoria con todas las metricas en cada foto para tener tendencias reales.
- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.

Recibos: `stage2280a_longitudinal_5audit_guarida_and_bench_telemetry_note642_receipt.json`,
`stage2281a_command_center_1536a_2285a_refresh_receipt.json`, `stage2283a_memorymaster_ingest_receipt.json`,
`stage2285a_wave207_opus2_gate.json`.
