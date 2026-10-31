<!-- doc-head: Wave 236 (2454A-2459A) sintesis ES: nota #654 sobre la undecima auditoria de solo lectura 2448A con las diez anteriores; un solo arranque por radio en las 11 auditorias; un solo vector uph_wifi0 por radio airOS, sin cambio de 2286A a 2448A; XC .198 en ceros desde 2286A (antes de 2256A sigue inferido); Panel1 fq_overmemory 4055 donde se leyo, errores FIFO 736, pausas no monotonas; sin descartes clase :2 desde 2286A; escalares de info sin unidades decodificadas; banda :8787 a 1536A..2459A; SIN campeon -->
# Reporte ejecutivo - Nota #654: once auditorias en el mismo arranque, vector uph y escalares

**Wave 236 - Etapas 2454A-2459A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo de solo lectura stage2448A con las diez auditorias anteriores (2106A a 2412A) en la nota
evergreen #654. Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a
1536A..2459A y las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de
trafico nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo las once auditorias. No se abrio ningun archivo de RE binario ni de desensamblado; el
constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- El pedido coincide con los recibos. Se agregan precisiones: el mismo arranque vale sobre las auditorias que
  leyeron uptime (el banco en 9 de 11, faltan 2256A y 2322A; los paneles airOS en 10; Panel1 en las 11).
- "Tx Pause Frames Honored" no tiene una trayectoria: vale 876 en 2412A y 3209 en 2448A, sube y baja, y **no es un
  total desde el arranque**; no se saca tendencia.
- Para .198 el cambio de los nombres de 2202A sigue en la ventana de 2202A a 2286A; que fuera antes de 2256A es
  **inferido**. Los escalares de info **no tienen unidades decodificadas**.

## Mismo arranque

2352A, 2376A, 2412A y 2448A leyeron el uptime en **los seis radios**. La hora de arranque implicita varia como mucho
29.8 s en Panel1 y menos de 3 s en los demas: **ningun radio se reinicio** en las once auditorias.

## Vector de /proc/sys/dev/uph_wifi0

- **Un solo vector por radio airOS** en 2448A, con los mismos doce valores que en 2286A, 2376A y 2412A.
- XC .198 da **todo en ceros** en 2256A (sus seis nombres) y en todas las auditorias siguientes.
- status, gqparam y enable: 1, 1 y 1 en los paneles; 0, 0 y 1 en los XC, sin cambio.

## Panel1 .84 (OpenWrt)

- fq_overmemory del AQM de phy0: **4055 en 2172A, 2286A, 2352A, 2376A, 2412A y 2448A**, sin cambio.
- Errores rx_fifo de eth0: de 558 en 2142A a 720 en 2412A y 736 en 2448A; +16 desde 2412A. Sigue subiendo; causa
  desconocida.
- Pausas recibidas 0 en cada auditoria que las leyo.

## Panel2 .82 y Panel3 .83 (airOS 8)

- Descartes de la clase :2: Panel2 184548 y Panel3 43817, **ningun descarte nuevo desde 2286A**.
- Requeues de la clase :2: Panel2 2355 sin cambio; Panel3 de 2370 a 2373.
- time_squeeze: Panel2 15056 a 15064; Panel3 8754 a 8760 (2412A a 2448A).
- Estaciones en info: Panel2 7 y Panel3 3 desde 2352A; los XC en cero.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2454A y 2455A

La nota #654 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 711 a 713 notas). El tablero se
reconstruyo con 425 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2448A no escribio nada.
- Los paneles difieren en carga y estaciones: no es un A/B controlado y no se nombra ninguna causa.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.
- Decodificar las unidades de uph_wifi0 info antes de usar esos numeros.

Recibos: `stage2454a_eleven_audit_same_boot_series_and_uph_scalars_note654_receipt.json`,
`stage2455a_command_center_1536a_2459a_refresh_receipt.json`, `stage2457a_memorymaster_ingest_receipt.json`,
`stage2459a_wave236_opus2_gate.json`.
