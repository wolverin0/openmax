<!-- doc-head: Wave 217 (2340A-2345A) sintesis ES: nota #646 sobre la auditoria de solo lectura 2322A y las seis anteriores del mismo arranque; uph_wifi0 vive en /proc/net/uph_wifi0 (info y noack_info, 0444, noack_info vacio), /dev/uph_wifi0 es el dispositivo 190:0 de ubnt_poll_host en los 4 radios airOS y el LTU usa dispositivos ame_*; serie de 7 auditorias: FIFO de Panel1 sigue subiendo, descartes clase :2 de Panel3 sin cambio desde 2286A, fq_overmemory leido solo en 2 auditorias; banda :8787 a 1536A..2345A; SIN campeon -->
# Reporte ejecutivo - Nota #646: uph_wifi0 en /proc/net, dispositivo 190 y serie de 7 auditorias

**Wave 217 - Etapas 2340A-2345A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo de solo lectura stage2322A con las seis auditorias anteriores (2106A, 2142A, 2172A, 2202A,
2256A y 2286A) en la nota evergreen #646. Se regeneraron las paginas de indice del vault, el feed del Command
Center :8787 se amplio a 1536A..2345A y las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular
honesto: **no hay campeon de trafico nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo las siete auditorias. No se abrio ningun archivo de RE binario ni de desensamblado; el
constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- El pedido dice que info muestra el estado del planificador TDMA. El recibo solo trae una tabla con etiquetas
  del driver y valores borrados en el equipo; el significado de las columnas **no esta decodificado**.
- fq_overmemory no tiene serie de siete puntos: solo lo leyeron 2172A y 2286A (4055 en ambas). 2322A leyo solo el
  AQM de la clase de acceso 2, todo en cero.
- Ninguna metrica se leyo en las siete auditorias; cada serie lista solo las auditorias que la leyeron.
- "Tx Pause Frames Honored" sube y baja entre auditorias: no es un total desde el arranque y no se saca tendencia.

## uph_wifi0 en /proc (2322A)

- La ruta /proc/uph_wifi0 **no existe** en ningun radio airOS. Los archivos estan en
  /proc/net/uph_wifi0/info y /proc/net/uph_wifi0/noack_info, los dos con modo **0444**, en Panel2, Panel3, XC .198
  y XC .253.
- **noack_info esta vacio** (0 bytes) en los cuatro. Si alguna vez se llena es desconocido con una sola lectura.
- info es una tabla chica: 526 bytes en los paneles y 778 en los XC. La tabla de estaciones (STAs, ACTv, AVGTXRT,
  AVGRXRT) aparece solo en Panel2 y Panel3.

## Dispositivo de caracteres 190 (2322A)

- /proc/devices muestra **ubnt_poll_host con major 190** en los cuatro radios airOS, y /dev/uph_wifi0 es **190:0**
  (crw-r--r--) en los mismos cuatro.
- El LTU .110 **no tiene ubnt_poll_host** ni /dev/uph_wifi0; registra en cambio ame_dfs_dev, ame_fty_dev,
  ame_debug_dev, ame_bist_dev y ame_ctrl_dev (majors 239 a 243).

## Mismo arranque

La hora de arranque implicita (hora de captura menos uptime) se mantiene dentro de 29.8 s en todos los equipos y
auditorias que leyeron uptime: ningun radio se reinicio. 2322A no leyo uptime en el banco y 2256A solo en Panel1.

## Serie de 7 auditorias

- Panel1 .84, errores rx_fifo de eth0: 558, 585, 596, 612, 636 y 656 (2142A a 2322A); +20 desde 2286A. Sigue
  subiendo; causa desconocida.
- Panel1, "Tx Pause Frames Honored": 2454, 881, entre 1007 y 1715, 807 y 337. Pausas recibidas 0 en cada
  auditoria que las leyo.
- Panel2 .82, descartes de la clase :2 de ath0: 184548 en 2142A, 2172A, 2286A y 2322A: **sin cambio**.
- Panel3 .83, descartes de la clase :2: 43598, 43598, 43817 y 43817. Los +219 llegaron entre 2172A y 2286A; **0
  nuevos desde 2286A**.
- time_squeeze de softnet: Panel2 14828, 14976 y 14996; Panel3 8644, 8701 y 8706 (2106A, 2286A y 2322A).
- 2142A leyo la raiz mq de ath0, no las clases; las otras lecturas son de la clase :2.

## recall-first

5 de 6 consultas al vault tuvieron aciertos; fq_overmemory no tenia notas previas. No se corrio chequeo scholar
(no se pidio).

## Etapas 2340A y 2341A

La nota #646 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista. El tablero se reconstruyo con 370 recibos en la
banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER, CURRENT y
CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2322A no escribio nada.
- Los paneles difieren en carga y estaciones: no es un A/B controlado y no se nombra ninguna causa.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Leer fq_overmemory y uptime del banco en la proxima auditoria para cerrar los huecos de la serie.
- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.

Recibos: `stage2340a_uph_proc_net_info_noack_cdev190_and_7audit_guarida_note646_receipt.json`,
`stage2341a_command_center_1536a_2345a_refresh_receipt.json`, `stage2343a_memorymaster_ingest_receipt.json`,
`stage2345a_wave217_opus2_gate.json`.
