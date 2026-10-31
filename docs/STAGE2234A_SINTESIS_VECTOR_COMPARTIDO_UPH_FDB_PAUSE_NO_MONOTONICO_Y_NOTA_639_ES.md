<!-- doc-head: Wave 199 (2232A-2237A) sintesis ES: nota #639 sobre la auditoria de solo lectura 2202A (valores uph_wifi0, puente/FDB y contador de pausa de eth0 en Panel1) junto con 2172A, 2142A y 2106A del mismo arranque: los seis nombres uph imprimen un mismo vector de 16 valores por radio y los paneles difieren en una sola posicion; semantica desconocida; el contador de pausa no es monotono y la pausa del par queda descartada; errores de FIFO de eth0 siguen subiendo; banda :8787 a 1536A..2237A; SIN campeon -->
# Reporte ejecutivo - Nota #639: vector compartido uph, FDB y pausa no monotona

**Wave 199 - Etapas 2232A-2237A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizo el recibo en vivo stage2202A (Wave 194) junto con 2172A, 2142A y 2106A en la nota evergreen
#639. Se regeneraron las paginas de indice del vault, el feed del Command Center :8787 se amplio a
1536A..2237A y las tres docs maestras siguen en 179 lineas con 0 apellidos. Titular honesto: **no hay
campeon de trafico nuevo**, no hubo escrituras y ningun valor de knob queda aplicado.

Alcance de lectura: solo los recibos de telemetria 2202A, 2172A, 2173A, 2142A y 2106A. No se abrio ningun
archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo. 2173A se usa solo
como contexto (ya sintetizado en la nota #638).

## Mismo arranque en cuatro auditorias

El uptime avanzo igual en todos los radios de 2106A a 2142A, a 2172A y a 2202A (dispersiones 0.7, 0.6 y
0.6 s). Ningun radio se reinicio: todo es el **mismo arranque**.

## stage2202A - uph_wifi0: un vector compartido, no seis ajustes

- En los cuatro radios airOS los seis nombres atpc, cms_bias, ff_cap_rep, ff_mcast_airtime_limit,
  fixed_frame y sta_rx_rssi_th imprimen el **mismo vector de 16 valores**.
- Panel2: un 1 en la posicion 9 y el resto en 0. Panel3: todo en 0. Los valores escalares (daprot,
  noack_mode, ptp_xmit, sta_priority) son iguales en los dos paneles.
- Por eso las "seis diferencias entre paneles" son **una sola posicion** de una tabla compartida.
- Banco: XC .198 tiene un 3 en la posicion 0; XC .253 todo en 0 y daprot, noack_mode y ptp_xmit en 1. El
  LTU no tiene uph_wifi0.
- Lectura INFERIDA: que indexa esa tabla y que significan sus valores es DESCONOCIDO. Ningun nombre se lee
  como el ajuste que nombra; atpc no se lee como potencia. No se recomienda tocar nada a partir de esto.
- No se leyo el contenido de gps_info; gpsreset y addradio son archivos de accion, solo se registro que
  existen.

## stage2202A - puente, FDB y multicast snooping

- Entradas FDB (locales / aprendidas): Panel2 2 / 441, Panel3 2 / 441, XC .198 2 / 39, XC .253 3 / 39,
  LTU 0 / 1. Panel1 no tiene la herramienta: queda **sin medir**. Estables entre las dos fotos; no se
  imprime ninguna MAC.
- Lectura INFERIDA: el mismo numero de direcciones en los dos paneles encaja con un mismo segmento L2; no
  se verifico MAC por MAC.
- El multicast snooping esta apagado solo en los XC del banco.

## stage2202A - contador de pausa de eth0 en Panel1

- El par del enlace no anuncia pausa y la MAC conto 0 tramas de pausa recibidas desde el arranque: la
  **pausa del par queda descartada**.
- "Tx Pause Frames Honored" en las capturas: 1168, 2526, 3848 y 881. **Baja** entre capturas separadas por
  un minuto: **no es un total desde el arranque**. 2172A habia leido 2454 como si lo fuera; esto confirma
  la advertencia de la nota #638.
- Que cuenta ese contador del driver ag71xx es DESCONOCIDO (encajaria un contador angosto que da la
  vuelta; su ancho no esta establecido). Panel1 no tiene chip de switch y ethtool -a no esta soportado.

## Panel1 eth0: errores de FIFO en el mismo arranque

rx_fifo_errors: 558 (2142A), 585 (2172A) y 596 (2202A); +27 y luego +11. En las ventanas: 0, 3 y 0. Son
cerca de 0.003 por ciento de los paquetes recibidos desde el arranque; 3 cambios de carrier desde el
arranque y 0 en la ventana. La pausa del par queda descartada como causa; la causa sigue DESCONOCIDA.

## recall-first

Antes de escribir la nota, 4 de 6 consultas al vault tuvieron aciertos (atpc, pause frames, fdb y
rx_fifo_errors); uph_wifi0 y multicast_snooping, ninguno. No se corrio chequeo scholar (no se pidio).

## Etapa 2232A - vault

La nota #639 quedo en research/notes/scholar_sources/ como evergreen. `hyperresearch sync` e
`hyperresearch index build` devolvieron 0 y _recent.md lista la nota. La primera corrida vio 671 notas
antes y 675 despues; el constructor se volvio a correr para corregir una frase.

## Etapa 2233A - banda 1536A..2237A y docs maestras

El tablero se reconstruyo con 314 recibos en la banda, 0 apellidos y 0 alias en toda la pagina; 2202A y
2232A aparecen en el feed con su clase de evidencia. El servidor :8787 responde HTTP 200 y sirve la banda
nueva. MASTER, CURRENT y CURATED siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado; 2202A no escribio nada.
- La semantica del vector uph no esta decodificada; no se atribuye ningun efecto a esos nombres.
- El contador de pausa no es un total desde el arranque y no es el par pausando el puerto.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Establecer que indexa el vector compartido uph antes de tratar cualquier nombre uph como knob.
- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO.

Recibos: `stage2232a_uph_sysctl_shared_vector_bridge_and_pause_telemetry_note639_receipt.json`,
`stage2233a_command_center_1536a_2237a_refresh_receipt.json`, `stage2235a_memorymaster_ingest_receipt.json`,
`stage2237a_wave199_opus2_gate.json`.
