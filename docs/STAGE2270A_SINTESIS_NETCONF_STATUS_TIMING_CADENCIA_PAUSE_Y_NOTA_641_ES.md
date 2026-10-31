<!-- doc-head: Wave 205 (2268A-2273A) sintesis ES: nota #641 sobre la auditoria de solo lectura 2256A (entradas seguras de uph_wifi0, netconf y cadencia del contador de pausa de Panel1) con 2202A y 2172A: los paneles corren dos perfiles de planificacion distintos (ff_* en Panel2, hyb_* en Panel3; unidades sin decodificar); doce nombres uph imprimen un mismo vector de 16 valores y en XC .198 los dos subconjuntos no coinciden; el contador de pausa encaja con 12 bits (no probado); FIFO de eth0 sigue subiendo; banda :8787 a 1536A..2273A; SIN campeon -->
# Reporte ejecutivo - Nota #641: netconf, entradas seguras uph y cadencia de pausa

**Wave 205 - Etapas 2268A-2273A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo en vivo stage2256A (Wave 203) con 2202A y 2172A en la nota evergreen #641. Se
regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a 1536A..2273A y
las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay campeon de trafico
nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo los recibos 2256A, 2202A y 2172A. No se abrio ningun archivo de RE binario ni de
desensamblado; el constructor rechaza cualquier otro recibo. 2256A tampoco leyo las entradas set_*, get_*,
debug_*, gps_info, gpsreset ni addradio, y enmascaro MAC y coordenadas en el equipo.

Aclaraciones sobre el pedido:

- netconf no tiene campos op_mode ni fixed_frame; los parametros de trama fija son los campos ff_*.
- timing, sqparam, ro, voip_bias, swr_limit y evm_meas_config no imprimen valores propios: imprimen el vector
  compartido.

## netconf: dos perfiles de planificacion

- 57 campos por equipo; los paneles difieren en 30.
- Panel2 contra Panel3: flags 137 contra 14864; down_dur 4880 contra 30000; up_dur 4370 contra 30000;
  cfp_dur_min 180 contra 10000; cbp_dur 180 contra 900; atpc_target_rssi 0 contra 36.
- 11 campos ff_* son distintos de cero solo en Panel2 (ff_frame_dur 10000, ff_dl_alloc 50) y 4 campos hyb_*
  solo en Panel3.
- Los XC del banco imprimen todo en cero (sin estaciones).
- Lectura INFERIDA: dos perfiles de planificacion distintos. Las unidades y los bits de flags **no estan
  decodificados**: ningun valor se lee como microsegundos ni como un modo.

## Entradas seguras y vector compartido

- status, gqparam y enable: 1, 1 y 1 en los paneles; 0, 0 y 1 en los XC. hsr_diag esta vacio en todos.
- Seis nombres nuevos imprimen el **mismo vector de 16 valores** que los seis de 2202A: **doce nombres uph
  son etiquetas de una sola tabla** en cada radio airOS.
- Las entradas no imprimen el valor de su nombre: en Panel2 la entrada voip_bias imprime el vector y el
  campo voip_bias de netconf vale 0; la entrada ff_mcast_airtime_limit imprimio el vector y el campo de
  netconf vale 10.
- Diferencia con 2202A: solo en XC .198 los nombres de 2202A dieron "3 0 0 ..." y los de 2256A dan ceros. 2256A no
  releyo los nombres de 2202A: no se sabe si el vector cambio con el tiempo o si los dos subconjuntos difieren
  (redaccion corregida, ver nota #643). Los paneles y XC .253 coinciden en ambos subconjuntos
  (Panel2 conserva el 1 en la posicion 9). La causa es DESCONOCIDA; entre ambas auditorias un ciclo de
  banco toco eth0 de .198 (2203A, nota #640, no releido) y no se establece ningun vinculo.

## Panel1 eth0: cadencia del contador de pausa

- "Tx Pause Frames Honored" cada 10 s: 1572, 1715, 1007 y 1465 (pasos +143, -708 y +458). Bajo una vez:
  **no es un total desde el arranque**.
- 2256A encuentra 11 o 12 bits compatibles con la bajada. 2202A leyo hasta 3848, lo que **descarta 11
  bits**: 12 bits es el ancho minimo compatible con todas las lecturas, no un ancho probado. Con 12 bits
  la bajada equivaldria a +3388 en 10.16 s.
- Los pasos de subida van a 14.1 y 45.6 por segundo: la cadencia no es pareja. Las tramas de pausa
  recibidas siguen en 0, asi que la **pausa del par sigue descartada**; que cuenta el contador es
  DESCONOCIDO.

## Panel1 eth0: errores de FIFO

rx_fifo_errors: 585 (2172A), 596 (2202A) y 612 (2256A); +11 en 1515 s y +16 en 989 s; 0 durante los 30
s de muestras. Causa DESCONOCIDA.

## recall-first

5 de 6 consultas al vault tuvieron aciertos (netconf, fixed frame, uph_wifi0, pause frames y
rx_fifo_errors); down_dur, ninguno. No se corrio chequeo scholar (no se pidio).

## Etapa 2268A - vault

La nota #641 quedo en research/notes/scholar_sources/ como evergreen. `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md lista la nota. La primera corrida vio 677 notas
antes y 678 despues; el constructor se volvio a correr para corregir dos frases.

## Etapa 2269A - banda 1536A..2273A y docs maestras

El tablero se reconstruyo con 331 recibos en la banda, 0 apellidos y 0 alias en toda la pagina; 2256A y
2268A aparecen en el feed con su clase de evidencia. El servidor :8787 responde HTTP 200 y sirve la banda
nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2256A no escribio nada.
- La diferencia de perfiles entre paneles es una diferencia de configuracion: no se actua sobre ella antes
  de decodificar los campos.
- Los nombres uph no son knobs individuales.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una comparacion planificada de los dos perfiles de planificacion de los paneles.
- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.

Recibos: `stage2268a_uph_netconf_status_timing_and_pause_cadence_note641_receipt.json`,
`stage2269a_command_center_1536a_2273a_refresh_receipt.json`, `stage2271a_memorymaster_ingest_receipt.json`,
`stage2273a_wave205_opus2_gate.json`.
