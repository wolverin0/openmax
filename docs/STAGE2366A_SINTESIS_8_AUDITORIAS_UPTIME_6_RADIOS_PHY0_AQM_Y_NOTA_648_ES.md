<!-- doc-head: Wave 221 (2364A-2369A) sintesis ES: nota #648 sobre la octava auditoria de solo lectura 2352A con las siete anteriores; uptime leido en los 6 radios, un solo arranque por radio en las 8 auditorias; Panel1 fq_overmemory 4055 en cada auditoria que lo leyo, errores FIFO de eth0 llegan a 676, pausas no monotonas; sin descartes clase :2 desde 2286A; escalares de uph_wifi0 info en los 4 airOS con unidades sin decodificar; banda :8787 a 1536A..2369A; SIN campeon -->
# Reporte ejecutivo - Nota #648: ocho auditorias, un arranque por radio y el AQM de phy0 en Panel1

**Wave 221 - Etapas 2364A-2369A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo de solo lectura stage2352A con las siete auditorias anteriores (2106A, 2142A, 2172A, 2202A,
2256A, 2286A y 2322A) en la nota evergreen #648. Se regeneraron las paginas de indice del vault, el feed del
Command Center :8787 se amplio a 1536A..2369A y las tres docs maestras siguen en 179 lineas con 0 apellidos.
Titular honesto: **no hay campeon de trafico nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo las ocho auditorias. No se abrio ningun archivo de RE binario ni de desensamblado; el
constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- El recibo 2352A no registra la ruta netdev:phy0-ap0/aqm. Trae el bloque phy_aqm y un bloque vif_aqm con una sola
  fila de la clase de acceso 2, todo en cero; se informa asi.
- El uptime no se leyo en todas las auditorias: los equipos del banco lo tienen en 6 de 8 (faltan 2256A y 2322A),
  los paneles airOS en 7 (falta 2256A) y Panel1 en las 8. El mismo arranque se afirma por equipo sobre las que lo
  leyeron.
- Los escalares de info son numeros al lado de las etiquetas del driver: **las unidades no estan decodificadas**.
- El listado de /proc/net/uph_wifi0 muestra tamano 0 para los dos archivos porque asi lista procfs; eso no
  prueba que esten vacios.

## Mismo arranque

En 2352A se leyo el uptime en **los seis radios** en la misma captura. La hora de arranque implicita (hora de
captura menos uptime) varia como mucho 29.8 s en Panel1 y menos de 3 s en los demas: **ningun radio se reinicio**
en las ocho auditorias. Panel1 tiene la mayor dispersion porque la hora de captura es el inicio de cada corrida.

## Panel1 .84 (OpenWrt)

- fq_overmemory del AQM de phy0: **4055 en 2172A, 2286A y 2352A**, sin cambio; las otras cinco no lo leyeron. En
  2352A el uso de memoria del AQM es 0, el backlog 0 y el overlimit 0.
- Errores rx_fifo de eth0: 558, 585, 596, 612, 636, 656 y 676; +20 desde 2322A. Sigue subiendo; causa
  desconocida.
- "Tx Pause Frames Honored": 2454, 881, entre 1007 y 1715, 807, 337 y 297. Sube y baja: **no es un total desde el
  arranque**. Pausas recibidas 0 en cada auditoria que las leyo.

## Panel2 .82 y Panel3 .83 (airOS 8)

- Descartes de la clase :2 de ath0: Panel2 184548 sin cambio; Panel3 43817 desde 2286A. **Ningun descarte nuevo
  en los dos paneles desde 2286A.**
- Requeues de la clase :2: Panel2 de 2354 a 2355; Panel3 de 2334 a 2359.
- time_squeeze de softnet: Panel2 14828, 14976, 14996 y 15012; Panel3 8644, 8701, 8706 y 8736.

## Escalares de uph_wifi0 info (2352A)

- /proc/net/uph_wifi0 lista info y noack_info, los dos con modo 0444, en los cuatro radios airOS.
- Panel2 muestra 7 estaciones y Panel3 3; los dos XC muestran todo en cero (sin estaciones).

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2364A y 2365A

La nota #648 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 696 a 698 notas). El tablero se
reconstruyo con 381 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2352A no escribio nada.
- Los paneles difieren en carga y estaciones: no es un A/B controlado y no se nombra ninguna causa.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.
- Decodificar las unidades de uph_wifi0 info antes de usar esos numeros para decidir algo.

Recibos: `stage2364a_eight_audit_same_boot_guarida_bench_uptime_and_phy0_aqm_note648_receipt.json`,
`stage2365a_command_center_1536a_2369a_refresh_receipt.json`, `stage2367a_memorymaster_ingest_receipt.json`,
`stage2369a_wave221_opus2_gate.json`.
