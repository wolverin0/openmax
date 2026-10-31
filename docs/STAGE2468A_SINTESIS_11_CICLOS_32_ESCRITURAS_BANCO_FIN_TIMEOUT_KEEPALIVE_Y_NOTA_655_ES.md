<!-- doc-head: Wave 238 (2466A-2471A) sintesis ES: nota #655 con los once ciclos de escritura y restauracion en RAM del banco (2107A a 2449A; XC .198, XC .253 y LTU .110); 32 escrituras, 32 restauradas, 31 combinaciones distintas, watchdog de 60 s por ciclo; 2449A escribio tcp_fin_timeout 60, 45, 60 en .198 y .110 y tcp_keepalive_probes 9, 7, 9 en .253, y encontro tcp_fin_timeout 15 en .253; una medicion ambiente con 1.665 por ciento de perdida ICMP; filas CRLF en orchestration/autoresearch/results.tsv; banda :8787 a 1536A..2471A; SIN campeon -->
# Reporte ejecutivo - Nota #655: once ciclos, 32 escrituras del banco, FIN timeout y keepalive

**Wave 238 - Etapas 2466A-2471A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los once ciclos de escritura y restauracion del banco en la nota evergreen #655, recalculando todo
desde los recibos de ciclo (no desde la sintesis 2436A). Se regeneraron las paginas de indice del vault, el feed del
Command Center :8787 se amplio a 1536A..2471A, se agregaron filas CRLF a orchestration/autoresearch/results.tsv y las
tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico nuevo**, ningun
valor de knob queda aplicado y no hay cambios permanentes.

Alcance de lectura: solo los once recibos de ciclo (2107A, 2143A, 2173A, 2203A, 2257A, 2287A, 2323A, 2353A, 2377A,
2413A y 2449A). No se abrio ningun archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro
recibo.

## Aclaraciones sobre el pedido

- **Roles de los equipos:** el pedido dice ".198 XC AP, .253 LTU-LR, .110 XC STA". Todos los recibos de ciclo, el de
  2449A incluido, dicen XC .198, XC .253 y LTU .110; ningun recibo registra roles AP o STA ni un LTU-LR en .253. Se
  usan los nombres de los recibos.
- **Ruta del tablero:** artifacts/autoresearch/FUTURAMAX_COMMAND_CENTER.html no existe; el tablero que sirve :8787
  es artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html, y ese es el que se refresco.
- Las cuentas y las escrituras de 2449A coinciden con los recibos. La lectura previa ademas muestra
  tcp_fin_timeout 15 en .253, que el pedido no menciona.
- La perdida ICMP no fue 0 en todo: en 2353A iteracion 1, cpe_41 marco 1.665 por ciento; no se atribuye a ninguna
  escritura.

## Lo nuevo de 2449A

- Lectura previa: tcp_fin_timeout vale **60 en .198 y .110, y 15 en .253**; tcp_keepalive_probes vale 9 en los tres.
- Escrituras: tcp_fin_timeout de 60 a 45 y vuelta a 60 en .198 y en .110; tcp_keepalive_probes de 9 a 7 y vuelta a 9
  en .253. Las tres volvieron a su base, **sin desvio residual**.
- Las dos variables existen en el kernel 2.6.32 de los XC. La version del kernel del LTU no esta en estos recibos.

## Matriz y repeticiones

- Escrituras por equipo: .198 diez, .253 diez, .110 doce.
- **31 combinaciones distintas** entre las 32 escrituras. La unica repeticion exacta sigue siendo 2323A iteracion 1,
  que repite 2203A iteracion 3.
- Los equipos del banco no comparten todos los valores por defecto: .253 tiene un FIN timeout mas corto y el LTU un
  reintento SYN mas.

## Restauracion y perdida

- **32 de 32 escrituras restauradas**: lectura final igual a la base y restauracion completa verificada. Las 32
  tomaron efecto; 0 escrituras a flash; RF sin arrancar; ningun knob PROTECTED.
- El watchdog de 60 s figura una vez por ciclo; los recibos no lo detallan escritura por escritura.
- Las mediciones OTA de los once ciclos nombran cpe_41 y cpe_80, sobre el enlace ambiente de Panel1.
- Los radios del banco no llevan carga: no se mide ningun efecto de cierre de conexiones, de keepalive ni de aire.
  Las etiquetas "keep" del arnes son sobre trafico ambiente y no son mejoras.

## results.tsv

Se agregaron filas con el formato de cuatro columnas del archivo (identificador, etapa, detalle, resultado) y fin de
linea CRLF: 2466A, 2467A y 2469A antes del gate, y 2471A despues. Se verifico que el archivo sigue sin ningun salto
de linea LF suelto.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2466A y 2467A

La nota #655 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. El tablero se reconstruyo con 434 recibos en la
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
- Corregir los roles de los equipos en el generador de pedidos (XC .198, XC .253, LTU .110).

Recibos: `stage2466a_11cycle_32write_bench_matrix_fin_keepalive_note655_receipt.json`,
`stage2467a_command_center_1536a_2471a_refresh_receipt.json`, `stage2469a_memorymaster_ingest_receipt.json`,
`stage2471a_wave238_opus2_gate.json`.
