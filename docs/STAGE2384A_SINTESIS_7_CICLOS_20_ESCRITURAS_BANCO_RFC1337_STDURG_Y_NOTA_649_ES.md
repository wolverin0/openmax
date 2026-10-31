<!-- doc-head: Wave 224 (2382A-2387A) sintesis ES: nota #649 con los siete ciclos de escritura y restauracion en RAM del banco (2143A a 2353A; XC .198, XC .253 y LTU .110); 20 escrituras, 20 restauradas, 19 combinaciones distintas, watchdog de 60 s por ciclo; tcp_rfc1337 y tcp_stdurg existen en los tres radios, a diferencia de dos ajustes ausentes en el kernel 2.6.32 de los XC; una medicion ambiente con 1.665 por ciento de perdida ICMP; banda :8787 a 1536A..2387A; SIN campeon -->
# Reporte ejecutivo - Nota #649: siete ciclos, 20 escrituras del banco, tcp_rfc1337 y tcp_stdurg

**Wave 224 - Etapas 2382A-2387A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los siete ciclos de escritura y restauracion del banco en la nota evergreen #649. Se regeneraron
las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2387A y las tres docs
maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo**, ningun valor
de knob queda aplicado y no hay cambios permanentes.

Alcance de lectura: solo los siete recibos de ciclo (2143A, 2173A, 2203A, 2257A, 2287A, 2323A y 2353A). No se
abrio ningun archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- **La perdida ICMP no fue 0 en todas las mediciones.** En 2353A iteracion 1, cpe_41 marco 1.665 por ciento; las
  demas mediciones dan 0. Es el enlace ambiente de Panel1, que ningun radio del banco transporta, asi que no se
  atribuye a ninguna escritura.
- 2353A no registra version de kernel. El 2.6.32.68 de los XC sale de 2323A, y que los dos ajustes existan en los
  tres radios sale de la nota del propio recibo (los dos leian 0 antes del ciclo).
- El watchdog de 60 s figura una vez por ciclo; los recibos no lo detallan escritura por escritura.

## Lo nuevo de 2353A

- tcp_rfc1337 de 0 a 1 y vuelta a 0 en XC .198 y en LTU .110; tcp_stdurg de 0 a 1 y vuelta a 0 en XC .253. Los
  tres volvieron a 0.
- Contraste: en 2323A, tcp_early_retrans y tcp_thin_linear_timeouts **no existen** en el kernel 2.6.32 de los XC;
  tcp_rfc1337 y tcp_stdurg **si existen** ahi. La version del kernel del LTU no esta en estos recibos.

## Matriz y repeticiones

- Escrituras por equipo: .198 seis, .253 seis, .110 ocho.
- **19 combinaciones distintas** de equipo, interfaz, knob, base y valor escrito entre las 20 escrituras. La unica
  repeticion exacta: 2323A iteracion 1 (tcp_early_retrans de 3 a 0 en .110) repite 2203A iteracion 3.

## Restauracion y perdida

- **20 de 20 escrituras restauradas**: lectura final igual a la base y restauracion completa verificada. Las 20
  tomaron efecto; 0 escrituras a flash; RF sin arrancar; ningun knob PROTECTED.
- Las mediciones OTA de los siete ciclos nombran cpe_41 y cpe_80.
- Los radios del banco no llevan carga, asi que no se mide ningun efecto de TIME_WAIT, de datos urgentes, de cola
  ni de aire. Las etiquetas "keep" del arnes son sobre trafico ambiente y no son mejoras.

## recall-first

4 de 6 consultas al vault tuvieron aciertos; tcp_rfc1337 y tcp_stdurg no tenian notas previas. No se corrio
chequeo scholar (no se pidio).

## Etapas 2382A y 2383A

La nota #649 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. La primera corrida vio 698 notas antes y 700
despues; el constructor se volvio a correr para corregir una frase. El tablero se reconstruyo con 389 recibos en la
banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED
siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo**, sin valor de knob conservado y sin cambios permanentes.
- Escribir y restaurar prueba que estos knobs son seguros de tocar; no dice nada de su efecto. No es un A/B
  controlado.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba con carga donde el equipo del knob reenvie el trafico medido.
- Vigilar si la perdida ambiente en cpe_41 se repite en la proxima auditoria.

Recibos: `stage2382a_seven_cycle_20write_bench_matrix_rfc1337_stdurg_note649_receipt.json`,
`stage2383a_command_center_1536a_2387a_refresh_receipt.json`, `stage2385a_memorymaster_ingest_receipt.json`,
`stage2387a_wave224_opus2_gate.json`.
