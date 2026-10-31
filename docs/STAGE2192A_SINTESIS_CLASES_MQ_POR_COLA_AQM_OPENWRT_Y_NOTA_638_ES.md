<!-- doc-head: Wave 192 (2190A-2195A) sintesis ES: nota #638 une la auditoria de solo lectura 2172A (clases mq por cola de ath0, lineas de athstats, AQM FQ-CoDel de mac80211 y FIFO de eth0 en OpenWrt) con 2142A y 2106A del mismo arranque: todos los descartes de los paneles airOS 8 estan en la clase :2, 0 en la ventana y 0 nuevos entre auditorias; la linea "no tx buffer" de athstats es un conteo de paquetes, no de descartes; OpenWrt descarta solo en BE; ciclo reversible 2173A (tx_queue_len, tcp_dsack) todo restaurado; banda :8787 a 1536A..2195A; SIN campeon -->
# Reporte ejecutivo - Nota #638: clases mq por cola, athstats y AQM de OpenWrt

**Wave 192 - Etapas 2190A-2195A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron los recibos en vivo stage2172A (Wave 189) con stage2142A y stage2106A, y el ciclo stage2173A,
en la nota evergreen #638. Se regeneraron las paginas de indice del vault (research/index/*.md), el feed del
Command Center :8787 se amplio a 1536A..2195A y las tres docs maestras siguen en 179 lineas con 0 apellidos
del alcance. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda aplicado.

Alcance de lectura: solo los recibos de telemetria de red, qdisc y AQM 2106A, 2142A, 2172A y 2173A. No se
abrio ningun archivo de RE binario ni de desensamblado; el constructor rechaza cualquier otro recibo.

Aclaraciones sobre el pedido:

- La qdisc mq de ath0 en airOS tiene **5 clases (:1 a :5)**, no 4 subcolas WMM.
- 2172A es telemetria de **solo lectura**; 2173A es un ciclo de escritura y restauracion en RAM, no
  telemetria.
- El "bracket" de athstats estricto fallo; la correspondencia usa una tolerancia de 10 ppm fijada despues de
  ese resultado.

## Mismo arranque en tres auditorias

El uptime de los seis radios avanzo lo mismo de 2106A a 2142A (dispersion 0.7 s) y de 2142A a 2172A
(dispersion 0.6 s). Ningun radio se reinicio: todos los totales desde el arranque son del **mismo arranque**.

## stage2172A - clases mq de ath0 (salida, airOS 8)

- Panel2 .82: la clase :2 envio 807251050 paquetes (97.623 por ciento) y tiene los 184548 descartes y los 2354
  requeues desde el arranque; las clases :1, :3, :4 y :5 tienen 0.
- Panel3 .83: la clase :2 envio 222560232 paquetes (97.686 por ciento) y tiene los 43598 descartes y los 2334
  requeues; las demas clases tienen 0.
- La clase :2 descarta 0.02286 por ciento de lo que envia en Panel2 y 0.01959 en Panel3.
- En la ventana de 30 s las clases descartaron **0 en todos los radios**.
- Lectura INFERIDA: los descartes se concentran en la clase :2 y no se reparten por volumen. En Panel2 las
  otras clases enviaron 19654442 paquetes sin descartes, cuando a la tasa de :2 darian unos 4493. Los
  descartes por desborde llegan en rafagas, asi que no es una prueba de probabilidad.
- El AC detras de la clase :2 **no esta establecido**: tc no muestra el mapa de cola a AC.
- Las participaciones por clase se recalculan desde los contadores y dan lo mismo que el recibo.

## 2142A contra 2172A en el mismo arranque

En los 1546.9 s entre ambas auditorias Panel2 siguio en 184548 descartes y Panel3 en 43598: **0 descartes
nuevos** de salida mientras Panel2 enviaba 1049.9 paquetes por segundo y Panel3 272.2. Los requeues de Panel3
pasaron de 2329 a 2334.

## stage2172A - las lineas de athstats son conteos por cola

En los dos paneles cada linea informativa de athstats coincide con el contador de paquetes enviados de una
clase de ath0, con error relativo de hasta 1.833e-06 (desfase de -408 a 0 paquetes). La linea "tx failed
'cuz no tx buffer (data)" sigue a la clase :2: es un **conteo de paquetes, no una tasa de descarte** ni de
falta de buffer. Limites: el bracket estricto fallo, la tolerancia se fijo despues, cubre una ventana en 2
paneles y no decodifica la estructura. Las etapas anteriores que la leyeron como descarte quedan marcadas por
2172A, sin editar.

## stage2172A - OpenWrt Panel1: FQ-CoDel de mac80211 y AQL

- Descartes de TXQ por estacion desde el arranque: 3794, **solo en BE** (0.02256 por ciento de 16820301
  paquetes BE, 280.73 por hora en 13.5 h); BK, VI y VO en 0. 3789 son de una sola estacion (orden de
  debugfs, sin identidad). Marcas ECN 0; 0 descartes en la ventana.
- fq_overmemory de la phy (4055) es otro contador; se informa al lado, sin conciliar. AQL activo.
- Esto llena en parte el hueco de 2142A: la capa TXQ de mac80211 queda medida; la qdisc de phy0-ap0 sigue
  **sin medir** (no hay tc).
- FQ-CoDel de OpenWrt y las clases mq de airOS son mecanismos distintos: no se comparan en numeros, y **no es
  un A/B controlado**.

## Panel1 eth0: errores de FIFO de recepcion

- rx_fifo_errors paso de 558 (2142A) a 585 (2172A): 27 en 1546.8 s, y 3 en la ventana de 2172A sobre 6225
  paquetes recibidos (0 en la ventana de 2142A). Sin errores CRC, overrun ni missed. Causa DESCONOCIDA.
- El bloque de ethtool que el recibo llama "desde el arranque" no lo es: Rx Packet 40119 contra 18119244
  paquetes de netdev, y 1994 de sus 2454 tramas de pausa caen en la ventana. Lectura INFERIDA: la base de
  esos contadores es DESCONOCIDA.

## stage2173A - ciclo tx_queue_len / tcp_dsack

- A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de iteraciones.
- Iteracion 1: tx_queue_len de ath0 1000 -> 256 en XC .198; lectura final 1000.
- Iteracion 2: tcp_dsack 1 -> 0 en XC .253; lectura final 1.
- Iteracion 3: tx_queue_len de eth0 256 -> 1000 en LTU .110; lectura final 256.
- Las tres escrituras tuvieron efecto y **todas se restauraron**; 0 escrituras a flash, RF sin arrancar. Las
  dos lecturas base de tx_queue_len coinciden con 2172A; B copia los valores de OpenWrt (256) y de eth0 en los
  paneles (1000).
- Los radios del banco no tienen carga ni par por aire: no se mide efecto de cola y **no se atribuye**
  efecto en el aire. El "Improved fmx_loss" de la iteracion 2 es la etiqueta del harness sobre trafico
  ambiente.
- La iteracion 3 (fmx_loss 1.083548, p95 41.768 ms) queda por encima del piso de 24 pliegues de la nota
  #637 y del ancla sin escrituras de 34.08 ms: el piso ambiente se ensancha otra vez; no se atribuye.
- La comparacion de repeticiones contra ciclos anteriores no se corrio (fuera del alcance de lectura).

## Etapa 2190A - vault

La nota #638 quedo en research/notes/scholar_sources/ como evergreen. `hyperresearch sync` y
`hyperresearch index build` devolvieron 0; 18 paginas de indice listan la nota, _recent.md entre ellas. La
primera corrida vio 669 notas antes y 671 despues; el constructor se volvio a correr para corregir una frase.
recall-first: 5 de 6 consultas con aciertos (athstats, mq class, fq_codel, aql, tx_queue_len).

## Etapa 2191A - banda 1536A..2195A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (295 recibos en la banda) con 0
apellidos y 0 alias en toda la pagina; 2172A, 2173A y 2190A aparecen en el feed con su clase de evidencia y
entraron 16 recibos sobre el tope anterior de 2159. Los recibos de 2196A en adelante (de otras lineas) quedan
fuera a proposito. El servidor :8787 responde HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED
siguen en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- Los descartes de airOS 8 son acumulados desde el arranque y de una sola clase; en la ventana fueron 0.
- La qdisc de OpenWrt sigue sin medir; FQ-CoDel de OpenWrt no se compara con airOS.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- Una prueba de banco con trafico marcado por DSCP para establecer el AC de la clase :2.
- El A/B con carga de la nota #636, contando ahora los descartes de la clase :2 en cada fase.
- Revisar el enlace cableado de eth0 de Panel1 por los errores de FIFO que siguen apareciendo.

Recibos: `stage2190a_per_queue_mq_class_and_openwrt_aqm_telemetry_note638_receipt.json`,
`stage2191a_command_center_1536a_2195a_refresh_receipt.json`, `stage2193a_memorymaster_ingest_receipt.json`,
`stage2195a_wave192_opus2_gate.json`.
