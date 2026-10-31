<!-- doc-head: Wave 233 (2436A-2441A) sintesis ES: nota #653 con los diez ciclos de escritura y restauracion en RAM del banco (2107A a 2413A; XC .198, XC .253 y LTU .110); 29 escrituras, 29 restauradas, 28 combinaciones distintas, watchdog de 60 s por ciclo; 2413A leyo tcp_syn_retries 6 en el LTU y 5 en los XC, tcp_synack_retries 5 en todos, y escribio cada uno +1 y vuelta; una medicion ambiente con 1.665 por ciento de perdida ICMP; banda :8787 a 1536A..2441A; SIN campeon -->
# Reporte ejecutivo - Nota #653: diez ciclos, 29 escrituras del banco y los reintentos SYN

**Wave 233 - Etapas 2436A-2441A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los diez ciclos de escritura y restauracion del banco de la lista permitida en la nota evergreen
#653. Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2441A y
las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo**,
ningun valor de knob queda aplicado y no hay cambios permanentes.

Alcance de lectura: solo los diez recibos permitidos (2107A, 2143A, 2173A, 2203A, 2257A, 2287A, 2323A, 2353A, 2377A
y 2413A). No se abrio ningun archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- Las cuentas del pedido coinciden con los recibos: 10 ciclos, 29 escrituras, 29 restauradas y 28 combinaciones
  distintas; los valores de 2413A tambien coinciden.
- El pedido no menciona la perdida ICMP: en 2353A iteracion 1, cpe_41 marco 1.665 por ciento; las demas mediciones
  dan 0. Es el enlace ambiente de Panel1 y no se atribuye a ninguna escritura.
- El watchdog de 60 s figura una vez por ciclo; los recibos no lo detallan escritura por escritura.

## Lo nuevo de 2413A

- Lectura previa: tcp_syn_retries vale **6 en el LTU .110 y 5 en los dos XC**; tcp_synack_retries vale 5 en los tres.
- Escrituras, cada una en base mas 1: tcp_synack_retries de 5 a 6 y vuelta a 5 en .198 y en .110; tcp_syn_retries de
  5 a 6 y vuelta a 5 en .253. Las tres volvieron a su base.
- Las dos variables existen en el kernel 2.6.32 de los XC, a diferencia de tcp_early_retrans y
  tcp_thin_linear_timeouts. La version del kernel del LTU no esta en estos recibos.

## Matriz y repeticiones

- Escrituras por equipo: .198 nueve, .253 nueve, .110 once.
- **28 combinaciones distintas** entre las 29 escrituras. La unica repeticion exacta sigue siendo 2323A iteracion 1,
  que repite 2203A iteracion 3.

## Restauracion y perdida

- **29 de 29 escrituras restauradas**: lectura final igual a la base y restauracion completa verificada. Las 29
  tomaron efecto; 0 escrituras a flash; RF sin arrancar; ningun knob PROTECTED.
- Las mediciones OTA de los diez ciclos nombran cpe_41 y cpe_80.
- Los radios del banco no llevan carga: no se mide ningun efecto sobre el armado de conexiones ni sobre el aire.
  Las etiquetas "keep" del arnes, incluidas las tres de 2413A, son sobre trafico ambiente y no son mejoras.

## recall-first

4 de 6 consultas al vault tuvieron aciertos; tcp_syn_retries y tcp_synack_retries no tenian notas previas. No se
corrio chequeo scholar (no se pidio).

## Etapas 2436A y 2437A

La nota #653 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 709 a 711 notas). El tablero se
reconstruyo con 418 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**, sin valor de knob conservado y sin cambios permanentes.
- Escribir y restaurar prueba que estos knobs son seguros de tocar; no dice nada de su efecto. No es un A/B
  controlado.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el equipo del knob reenvie el trafico medido.
- Tener en cuenta que el LTU arranca con un reintento SYN mas que los XC al comparar equipos.

Recibos: `stage2436a_ten_cycle_29write_bench_matrix_syn_synack_retries_note653_receipt.json`,
`stage2437a_command_center_1536a_2441a_refresh_receipt.json`, `stage2439a_memorymaster_ingest_receipt.json`,
`stage2441a_wave233_opus2_gate.json`.
