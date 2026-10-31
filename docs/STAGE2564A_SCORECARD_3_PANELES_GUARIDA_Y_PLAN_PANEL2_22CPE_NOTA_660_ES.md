<!-- doc-head: Wave 254 (2562A-2567A) sintesis ES: nota #660, scorecard de las 3 celdas de Guarida y orden candidato de lotes para Panel2: Panel1 con 2 CPEs confirmados en OpenWrt 24.10.4 psk2 + 1 estacion vista solo desde el AP (no hay registro de una baja); Panel3 migro 3 de sus 6 CPEs y el CPE .9 paso de sano en airOS a MCS 0 en OpenWrt (compatible con regresion, no probado); Panel2 con 22 CPEs, 7 medidos y 15 modelados en una radiografia del 24-10; orden de lotes es candidato, no decision; aviso de PII heredada en la seccion Stage 12 del tablero; banda :8787 a 1536A..2567A; SIN campeon -->
# Reporte ejecutivo - Nota #660: scorecard de los 3 paneles de Guarida y plan candidato para Panel2

**Wave 254 - Etapas 2562A-2567A - 2026-10-28 - sintesis 100% offline (esta wave no toco ningun equipo).**

## Que se hizo

Se armo en la nota evergreen #660 un scorecard de las tres celdas de Guarida y un orden candidato de lotes para
migrar Panel2, a partir de la radiografia de 32 CPEs del 24-10 y de los recibos OpenWrt del 28-10 (2496A, 2498A y
2499A). Se regeneraron los indices del vault, el feed del Command Center :8787 se amplio a 1536A..2567A, se agregaron
filas CRLF a orchestration/autoresearch/results.tsv y las tres docs maestras siguen en 179 lineas.

Titular honesto: no hay ninguna medicion nueva. La radiografia tiene **32 CPEs, 16 medidos y 16 modelados**, y el
orden de Panel2 es un **candidato, no una decision**. **No hay campeon** y no se afirma ninguna mejora.

Alcance de lectura: la radiografia y tres recibos JSON. La radiografia trae nombres de abonados, MAC y direcciones
completas: se leyeron pero no se copiaron; los equipos se nombran solo por el ultimo octeto. No se abrio ningun
binario ni desensamblado.

## Aclaraciones sobre el pedido

- **Panel1** "3 CPEs en OpenWrt + 1 baja": hay 2 CPEs confirmados en OpenWrt 24.10.4 con psk2 (.41 y .223, leidos
  directo); la tercera estacion solo se ve desde el AP y su firmware no esta confirmado. La radiografia lista 4 CPEs,
  dos de ellos con airOS 8 de fabrica. **Ninguna fuente registra una baja.**
- **Panel3** "3 CPEs migrados y 0% DUP": se migraron 3 de los 6 CPEs de la radiografia (psk2 3 de 3); .106
  (modelado, activo), .68 y .30 (fuera de linea) no se migraron. **Ninguna fuente cuenta respuestas DUP.**
- **Panel2** "22 CPEs": 7 medidos y **15 modelados** en una radiografia de hace cuatro dias.
- La radiografia existe en dos copias identicas; se leyo la de artifacts/.
- closed_loop_research_reactor.py no tiene la opcion --sync-hyperresearch (su arranque regenera recibos viejos) y
  build_hyperresearch_vault_index.py no existe; se uso `hyperresearch sync` y `hyperresearch index build`.

## Scorecard

| celda | CPEs en la radiografia | medidos / modelados | estado al 28-10 |
| --- | --- | --- | --- |
| Panel1 | 4 | 4 / 0 | AP OpenWrt; 2 CPEs confirmados en OpenWrt psk2, 1 estacion sin confirmar |
| Panel2 | 22 | 7 / 15 | sin migrar; sin lectura del 28-10 en el alcance |
| Panel3 | 6 | 5 / 1 | AP + 3 CPEs en OpenWrt psk2; 3 CPEs sin migrar |

## Panel3: el CPE .9

En airOS (radiografia del 24-10, dato medido) tenia 107.9 Mbit/s de capacidad estimada, 0 dB de diferencia entre
cadenas y 5.6% de reintentos. En OpenWrt (28-10) esta en **MCS 0 en las dos direcciones**, una sola cadena espacial y
10 dB de desbalance visto desde el AP. Las metricas no son las mismas, asi que es **compatible con una regresion
causada por la migracion, pero no esta probado**.

fq_overmemory por hora de uptime: 2358.64 en Panel3 contra 220.65 en Panel1.

## Panel2 en la radiografia

- Los 15 modelados siguen un patron regular (la senal baja cerca de 1 dB cada 137 m y la diferencia entre cadenas es
  1.5 dB en 13 filas y 5.0 dB en 2): no son mediciones.
- Acaparan tiempo de aire: .113 (modelado), .169 y .21 (medidos; .169 con 22% de reintentos).
- Falla grave de cable (10 Mbit/s o half duplex): .121, que es una fila modelada.
- Solo .213 negocia 1000 Mbit/s; el resto 100 Mbit/s.
- Panel2 tiene un CPE terminado en .83, el mismo octeto que el AP de Panel3; son equipos distintos.

## Orden candidato de lotes para Panel2 (no es una decision)

- Lote 0 (requisito): explicar el resultado del CPE .9 y volver a medir en solo lectura las 15 filas modeladas.
- Lote 1 (medidos, sin acaparar aire, sin falla grave): .213, .239, .183, .83 y .166, del enlace mas corto al mas
  largo, de a un CPE por ventana con lectura antes y despues.
- Lote 2 (medidos que acaparan aire): .169 y .21; enlaces largos, probablemente con visita a campo.
- Lote 3 (modelados, despues de medirlos): .108 a .120, .122 y .113, ordenados por la medicion nueva.
- Lote 4: .121, primero arreglar el cable.

## Aviso de PII en el tablero

La seccion heredada "Stage 12 — Guarida" del tablero muestra 6 nombres de CPE de la radiografia que parecen nombres de
personas, y el sanitizador actual no los detecta (cuenta 0 apellidos). Ademas, dos MAC de la radiografia aparecen en
secciones heredadas (el tablero de tareas de agentes y la de las etapas 57A a 61A). Viene del codigo compartido del
tablero, no de esta wave; no se corrigio porque esta fuera del alcance. Ningun artefacto de esta wave lleva nombres ni
MAC, y la tarjeta 2562A del tablero tampoco.

## Etapas 2562A y 2563A

La nota #660 quedo en research/notes/scholar_sources/ como evergreen; `hyperresearch sync` e `hyperresearch index build`
devolvieron 0 y el vault llego a 723 notas. El tablero se reconstruyo con 479 recibos en la banda y el servidor :8787
responde HTTP 200. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon**, sin A/B y sin ninguna medicion nueva.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se verifico por CLI
  con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Decidir si se corrige la seccion Stage 12 del tablero para que no muestre nombres de abonados.
- Explicar el CPE .9 antes de migrar mas equipos (revisar los recibos 2532A y 2534A, que no se leyeron).
- Aprobar o cambiar el orden candidato de Panel2 y la nueva medicion de las 15 filas modeladas.
- Decidir que hacer con los tres CPEs de Panel3 sin migrar.

Recibos: `stage2562a_guarida_32cpe_3panel_migration_scorecard_note660_receipt.json`,
`stage2563a_command_center_1536a_2567a_refresh_receipt.json`, `stage2565a_memorymaster_ingest_receipt.json`,
`stage2567a_wave254_opus2_gate.json`.
