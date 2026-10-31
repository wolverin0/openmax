<!-- doc-head: Wave 228 (2406A-2411A) sintesis ES: nota #651 con los ciclos de escritura y restauracion en RAM del banco de la lista permitida (2107A a 2377A; XC .198, XC .253 y LTU .110); los nueve recibos son ciclos: 26 escrituras, 23 en los ocho del pedido (sin 2107A), todas restauradas, 25 combinaciones distintas, watchdog de 60 s por ciclo; tcp_slow_start_after_idle y tcp_no_metrics_save existen en los tres radios; una medicion ambiente con 1.665 por ciento de perdida ICMP; kernel del LTU fuera de alcance; banda :8787 a 1536A..2411A; SIN campeon -->
# Reporte ejecutivo - Nota #651: matriz del banco con tcp_slow_start_after_idle y tcp_no_metrics_save

**Wave 228 - Etapas 2406A-2411A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los ciclos de escritura y restauracion del banco de la lista permitida en la nota evergreen #651. Se
regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2411A y las tres
docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo**, ningun valor
de knob queda aplicado y no hay cambios permanentes.

Alcance de lectura: solo los nueve recibos permitidos (2107A, 2143A, 2173A, 2203A, 2257A, 2287A, 2323A, 2353A y
2377A). No se abrio ningun archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- **Son 26 escrituras en nueve ciclos.** Los nueve recibos permitidos son ciclos de banco. Las "23 escrituras en
  ocho ciclos" del pedido son el mismo conjunto sin 2107A (tcp_keepalive_intvl y tcp_keepalive_probes); las dos
  cuentas estan en el recibo y las 23 tambien se restauraron.
- 2377A no escribio las dos variables en los tres equipos: tcp_slow_start_after_idle en .198 y .110,
  tcp_no_metrics_save solo en .253. El recibo anota que las dos existian en los tres antes del ciclo.
- **El kernel 3.14.77 del LTU no figura en ningun recibo permitido.** Auditorias anteriores, fuera de este alcance y
  no releidas, registraron 3.14.65; no se repite ninguno.
- La perdida ICMP no fue 0 en todo: en 2353A iteracion 1, cpe_41 marco 1.665 por ciento.

## Lo nuevo de 2377A

- tcp_slow_start_after_idle de 1 a 0 y vuelta a 1 en XC .198 y en LTU .110; tcp_no_metrics_save de 0 a 1 y vuelta a
  0 en XC .253. Las tres volvieron a su base.
- Contraste de kernel: en 2323A, tcp_early_retrans y tcp_thin_linear_timeouts **no existen** en el kernel 2.6.32 de
  los XC; tcp_rfc1337, tcp_stdurg, tcp_slow_start_after_idle y tcp_no_metrics_save **si existen** ahi.

## Matriz y repeticiones

- Escrituras por equipo: .198 ocho, .253 ocho, .110 diez.
- **25 combinaciones distintas** entre las 26 escrituras. La unica repeticion exacta sigue siendo 2323A iteracion 1,
  que repite 2203A iteracion 3.

## Restauracion y perdida

- **26 de 26 escrituras restauradas**: lectura final igual a la base y restauracion completa verificada. Las 26
  tomaron efecto; 0 escrituras a flash; RF sin arrancar; ningun knob PROTECTED.
- El watchdog de 60 s figura una vez por ciclo; los recibos no lo detallan escritura por escritura.
- Las mediciones OTA de los nueve ciclos nombran cpe_41 y cpe_80. La unica perdida (1.665 por ciento) es del enlace
  ambiente de Panel1, que ningun radio del banco transporta: no se atribuye a ninguna escritura.
- Los radios del banco no llevan carga: no se mide ningun efecto de reinicio tras inactividad, de cache de metricas,
  de keepalive ni de aire. Las etiquetas "keep" del arnes no son mejoras.

## recall-first

4 de 6 consultas al vault tuvieron aciertos; tcp_slow_start_after_idle y tcp_no_metrics_save no tenian notas
previas. No se corrio chequeo scholar (no se pidio).

## Etapas 2406A y 2407A

La nota #651 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 705 a 707 notas). El tablero se
reconstruyo con 402 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**, sin valor de knob conservado y sin cambios permanentes.
- Escribir y restaurar prueba que estos knobs son seguros de tocar; no dice nada de su efecto. No es un A/B
  controlado.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el equipo del knob reenvie el trafico medido.
- Confirmar la version de kernel del LTU con una auditoria dentro del alcance antes de citarla.

Recibos: `stage2406a_eight_cycle_23write_bench_matrix_ss_idle_no_metrics_note651_receipt.json`,
`stage2407a_command_center_1536a_2411a_refresh_receipt.json`, `stage2409a_memorymaster_ingest_receipt.json`,
`stage2411a_wave228_opus2_gate.json`.
