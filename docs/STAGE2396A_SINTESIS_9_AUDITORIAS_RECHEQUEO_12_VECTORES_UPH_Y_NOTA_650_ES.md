<!-- doc-head: Wave 226 (2394A-2399A) sintesis ES: nota #650 sobre la novena auditoria de solo lectura 2376A con las ocho anteriores; un solo arranque por radio en las 9 auditorias; un solo vector uph_wifi0 por radio airOS, sin cambio de 2286A a 2376A; XC .198 en ceros desde 2286A (el cambio de los nombres de 2202A queda en la ventana 2202A a 2286A, antes de 2256A es inferido); Panel1 fq_overmemory 4055 donde se leyo, errores FIFO 712; sin descartes clase :2 desde 2286A; banda :8787 a 1536A..2399A; SIN campeon -->
# Reporte ejecutivo - Nota #650: nueve auditorias, rechequeo de los 12 vectores uph y escalares

**Wave 226 - Etapas 2394A-2399A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo de solo lectura stage2376A con las ocho auditorias anteriores (2106A a 2352A) en la nota
evergreen #650. Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a
1536A..2399A y las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de
trafico nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo las nueve auditorias. No se abrio ningun archivo de RE binario ni de desensamblado; el
constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- El pedido ubica el cambio de .198 entre 2202A y 2256A. Los nombres de 2202A se volvieron a leer recien en 2286A,
  asi que el cambio queda en la ventana de 2202A a 2286A; que fuera antes de 2256A es **inferido**, porque 2256A
  leyo los otros seis nombres. La causa sigue desconocida.
- "Ceros en 2256A" vale para los seis nombres que leyo 2256A; los doce dan ceros en 2286A y en 2376A.
- El uptime no esta en todas las auditorias: el banco lo tiene en 7 de 9 (faltan 2256A y 2322A), los paneles airOS
  en 8 y Panel1 en las 9.
- Los escalares de info son numeros al lado de etiquetas del driver: **las unidades no estan decodificadas**.

## Mismo arranque

2352A y 2376A leyeron el uptime en **los seis radios**. La hora de arranque implicita varia como mucho 29.8 s en
Panel1 y menos de 3 s en los demas: **ningun radio se reinicio** en las nueve auditorias.

## Rechequeo de los 12 vectores (2376A)

- El arbol es /proc/sys/dev/uph_wifi0. 2376A volvio a leer las mismas doce entradas que 2286A; las entradas que
  nunca se leen (set_*, get_*, debug_*) siguieron sin leerse.
- **Un solo vector por radio airOS**, y cada radio muestra los mismos doce valores que en 2286A.
- XC .198 da **todo en ceros** en 2256A (sus seis nombres), en 2286A y en 2376A.
- status, gqparam y enable valen 1, 1 y 1 en los dos paneles; 0, 0 y 1 en los dos XC.

## Panel1 .84 (OpenWrt)

- fq_overmemory del AQM de phy0: **4055 en 2172A, 2286A, 2352A y 2376A**, sin cambio.
- Errores rx_fifo de eth0: 558, 585, 596, 612, 636, 656, 676 y 712; +36 desde 2352A. Sigue subiendo; causa
  desconocida.
- "Tx Pause Frames Honored": baja a 297 en 2352A y sube a 3055 en 2376A. **No es un total desde el arranque**.
  Pausas recibidas 0 en cada auditoria que las leyo.

## Panel2 .82 y Panel3 .83 (airOS 8)

- Descartes de la clase :2: Panel2 184548 y Panel3 43817, **ningun descarte nuevo desde 2286A**.
- Requeues de la clase :2: Panel2 2355 sin cambio desde 2352A; Panel3 de 2359 a 2366.
- time_squeeze: Panel2 15012 a 15036; Panel3 8736 a 8746 (2352A a 2376A).
- Estaciones en info: Panel2 7 y Panel3 3 en 2352A y en 2376A; los XC en cero.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2394A y 2395A

La nota #650 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 700 a 705 notas). El tablero se
reconstruyo con 395 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2376A no escribio nada.
- Los paneles difieren en carga y estaciones: no es un A/B controlado y no se nombra ninguna causa.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.
- Decodificar las unidades de uph_wifi0 info antes de usar esos numeros.

Recibos: `stage2394a_nine_audit_same_boot_12vector_recheck_and_uph_scalars_note650_receipt.json`,
`stage2395a_command_center_1536a_2399a_refresh_receipt.json`, `stage2397a_memorymaster_ingest_receipt.json`,
`stage2399a_wave226_opus2_gate.json`.
