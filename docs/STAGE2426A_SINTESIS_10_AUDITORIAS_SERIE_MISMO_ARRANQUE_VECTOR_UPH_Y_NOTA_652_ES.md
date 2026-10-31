<!-- doc-head: Wave 231 (2424A-2429A) sintesis ES: nota #652 sobre la decima auditoria de solo lectura 2412A con las nueve anteriores; un solo arranque por radio en las 10 auditorias; un solo vector uph_wifi0 por radio airOS, sin cambio de 2286A a 2376A a 2412A; XC .198 en ceros desde 2286A (antes de 2256A sigue inferido); Panel1 fq_overmemory 4055 donde se leyo, errores FIFO 720; sin descartes clase :2 desde 2286A; escalares de info con unidades sin decodificar; banda :8787 a 1536A..2429A; SIN campeon -->
# Reporte ejecutivo - Nota #652: diez auditorias en el mismo arranque, vector uph y escalares

**Wave 231 - Etapas 2424A-2429A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo de solo lectura stage2412A con las nueve auditorias anteriores (2106A a 2376A) en la nota
evergreen #652. Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a
1536A..2429A y las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de
trafico nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo las diez auditorias. No se abrio ningun archivo de RE binario ni de desensamblado; el
constructor rechaza cualquier otro recibo.

## Aclaraciones sobre el pedido

- El pedido coincide con los recibos. Se agregan dos precisiones: el mismo arranque vale sobre las auditorias que
  leyeron uptime (el banco en 8 de 10, faltan 2256A y 2322A; los paneles airOS en 9; Panel1 en las 10), y los
  escalares de info **no tienen unidades decodificadas**.
- Para .198 el cambio de los nombres de 2202A sigue en la ventana de 2202A a 2286A; que fuera antes de 2256A es
  **inferido** y la causa sigue desconocida.

## Mismo arranque

2352A, 2376A y 2412A leyeron el uptime en **los seis radios**. La hora de arranque implicita varia como mucho 29.8 s
en Panel1 y menos de 3 s en los demas: **ningun radio se reinicio** en las diez auditorias.

## Vector de /proc/sys/dev/uph_wifi0

- **Un solo vector por radio airOS** en 2412A, con los mismos doce valores que en 2286A y en 2376A.
- XC .198 da **todo en ceros** en 2256A (sus seis nombres), 2286A, 2376A y 2412A.
- status, gqparam y enable: 1, 1 y 1 en los paneles; 0, 0 y 1 en los XC, igual que en 2376A.

## Panel1 .84 (OpenWrt)

- fq_overmemory del AQM de phy0: **4055 en 2172A, 2286A, 2352A, 2376A y 2412A**, sin cambio.
- Errores rx_fifo de eth0: 558, 585, 596, 612, 636, 656, 676, 712 y 720; +8 desde 2376A. Sigue subiendo; causa
  desconocida.
- "Tx Pause Frames Honored": 3055 en 2376A y 876 en 2412A. Sube y baja: **no es un total desde el arranque**.
  Pausas recibidas 0 en cada auditoria que las leyo.

## Panel2 .82 y Panel3 .83 (airOS 8)

- Descartes de la clase :2: Panel2 184548 y Panel3 43817, **ningun descarte nuevo desde 2286A**.
- Requeues de la clase :2: Panel2 2355 sin cambio; Panel3 de 2366 a 2370.
- time_squeeze: Panel2 15036 a 15056; Panel3 8746 a 8754 (2376A a 2412A).
- Estaciones en info: Panel2 7 y Panel3 3 en 2352A, 2376A y 2412A; los XC en cero.

## recall-first

6 de 6 consultas al vault tuvieron aciertos. No se corrio chequeo scholar (no se pidio).

## Etapas 2424A y 2425A

La nota #652 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md la lista (el vault paso de 707 a 709 notas). El tablero se
reconstruyo con 408 recibos en la banda, 0 apellidos y 0 alias; el servidor :8787 responde HTTP 200 y sirve la
banda nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2412A no escribio nada.
- Los paneles difieren en carga y estaciones: no es un A/B controlado y no se nombra ninguna causa.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico
  por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.
- Decodificar las unidades de uph_wifi0 info antes de usar esos numeros.

Recibos: `stage2424a_ten_audit_same_boot_series_and_uph_scalars_note652_receipt.json`,
`stage2425a_command_center_1536a_2429a_refresh_receipt.json`, `stage2427a_memorymaster_ingest_receipt.json`,
`stage2429a_wave231_opus2_gate.json`.
