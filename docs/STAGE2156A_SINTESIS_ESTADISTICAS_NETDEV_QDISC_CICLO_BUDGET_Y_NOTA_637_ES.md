<!-- doc-head: Wave 186 (2154A-2159A) sintesis ES: nota #637 une la auditoria de solo lectura de /proc/net/dev, estadisticas sysfs y qdisc 2142A (0 descartes en la ventana de 30 s en toda interfaz fisica y en toda qdisc raiz medida; descartes de salida en la qdisc de ath0 de los paneles airOS 8 desde el arranque; qdisc de OpenWrt sin medir; mismo arranque que 2106A) y el ciclo reversible 2143A (netdev_budget, netdev_max_backlog; todo restaurado; la iteracion 3 repite 1951A); piso de ruido de 24 pliegues; banda :8787 a 1536A..2159A; SIN campeon -->
# Reporte ejecutivo - Nota #637: contadores netdev, sysfs y qdisc y ciclo netdev_budget / netdev_max_backlog

**Wave 186 - Etapas 2154A-2159A - 2026-10-28 - sintesis 100% offline (0 SSH, 0 escritura a radios en esta wave).**

## Que se hizo

Se sintetizaron 2 recibos primarios en vivo de la Wave 184 (stage2142A y stage2143A) en la nota evergreen
#637, se regeneraron las paginas de indice del vault (research/index/*.md), el feed del Command Center
:8787 se amplio a 1536A..2159A y las tres docs maestras siguen en 179 lineas o menos con 0 apellidos del
alcance. Titular honesto: **no hay campeon de trafico nuevo** y ningun valor de knob queda aplicado.

Aclaraciones sobre el pedido:

- 2142A es telemetria de **solo lectura** (0 escrituras, una ventana de 30 s entre 2 fotos mas los totales
  desde el arranque); 2143A es un ciclo de escritura y restauracion en RAM, no telemetria. No hay
  "telemetria de netdev_budget": en 2143A no se midio time_squeeze.
- /proc/net/dev y sysfs cubren los 6 radios; los contadores de qdisc cubren 5 de 6. Panel1 OpenWrt no
  tiene `tc`: su qdisc queda **sin medir** (vacio, no cero).
- La premisa de 2143A (netdev_budget 300 en los tres radios del banco) solo se cumplio en .110; 2106A ya
  habia leido 600 en .198 y .253 antes de que corriera el ciclo.

## stage2142A - qdisc raiz (salida, lado TX)

- Panel2 .82 (airOS 8, 176.9 h): ath0 mq descarto 184548 de 825281397 paquetes enviados (0.0224 por
  ciento), 2354 requeues, 1043.09 descartes por hora desde el arranque, 0 en la ventana.
- Panel3 .83 (airOS 8, 176.9 h): ath0 mq descarto 43598 de 227412270 (0.0192 por ciento), 2329
  requeues, 246.42 por hora, 0 en la ventana.
- En los dos paneles airOS la qdisc de eth0 (pfifo_fast) no descarto nada.
- Panel1 .84 (OpenWrt, 13.1 h): sin `tc`, qdisc sin medir.
- Banco XC .198, XC .253 y LTU .110: 0 descartes de qdisc desde el arranque y en la ventana.
- En la ventana de 30 s las qdisc raiz descartaron **0 en los 5 radios con tc**. Todo descarto distinto
  de cero es un total desde el arranque, y la comparacion de qdisc es solo entre radios airOS.
- Por hora Panel2 descarta 4.23 veces lo de Panel3, pero envio 3.63 veces mas paquetes por ath0; por
  paquete quedan cerca (0.0224 contra 0.0192 por ciento). Lectura INFERIDA: la diferencia por hora sigue
  al volumen mas que a la probabilidad de descarte; son solo dos paneles, no una correlacion.
- Los contadores de paquetes de 2.6.32 son de 32 bits: los porcentajes suponen que no dieron la vuelta.
  El contador de bytes de 64 bits da 1118 y 884 bytes por paquete, coherente con eso (INFERIDA, no
  probado).
- Todos los totales por radio y los porcentajes se recalculan desde los contadores crudos por interfaz y
  por qdisc y dan los mismos valores que el recibo.

## stage2142A - interfaces fisicas, puente y radio padre

- En la ventana de 30 s: 0 rx_dropped, tx_dropped, fifo, missed y colisiones en las interfaces fisicas
  de los **seis radios**.
- Desde el arranque: Panel2 tiene 1 tx_dropped y Panel3 4; Panel1 tiene 558 rx_fifo_errors en eth0, 0
  en la ventana.
- Puente aparte: el br-lan de Panel1 marca 14142 rx_dropped desde el arranque y 12 en la ventana. En
  Linux cuenta tramas para la pila local sin manejador de protocolo: **no es trafico de abonados
  perdido**.
- El radio padre wifi0 de airOS acumula 112593778 rx_dropped en Panel2 y 32216075 en Panel3, con un
  tx_dropped no monotono en Panel2. El driver no documenta ese contador: queda DESCONOCIDO y no se lee
  como perdida.
- Los paneles OpenWrt y airOS difieren en firmware, kernel, estaciones, carga y uptime: **no es un A/B
  controlado**.

## Mismo arranque que 2106A: backlog RX contra qdisc TX

El uptime de los seis radios avanzo entre 1275.9 y 1276.6 s entre 2106A y 2142A (dispersion 0.7 s; los
recibos se escribieron con 1332.2 s de diferencia, un desfase uniforme del momento de captura). Ningun
radio se reinicio: los dos recibos leen el **mismo arranque**. En ese arranque Panel2 descarto 0
paquetes en el backlog RX y 184548 en la qdisc TX; Panel3 0 y 43598. Los paneles airOS 8 pierden en la
salida, no en la entrada. Su squeeze desde el arranque (83.98 y 48.96 por hora) es falta de tiempo de
softirq, no perdida de paquetes.

## stage2143A - ciclo netdev_budget / netdev_max_backlog

- A1 -> B1 -> A2 -> B2, 3 iteraciones, watchdog de 60 s, parada por maximo de iteraciones.
- Iteracion 1: netdev_budget 600 -> 300 en XC .198; lectura final 600; el harness la marco keep como
  linea base inicial.
- Iteracion 2: netdev_max_backlog 768 -> 1000 en XC .253; lectura final 768; descartada.
- Iteracion 3: netdev_budget 300 -> 600 en LTU .110; lectura final 300; descartada.
- Las tres escrituras tuvieron efecto y **todas se restauraron**; 0 escrituras a flash, RF sin arrancar.
- La iteracion 3 repite exactamente la iteracion 3 de 1951A. La iteracion 2 difiere de la iteracion 2
  de 1987A solo en B (1000 contra 1024). La iteracion 1 corre el contraste 600 -> 300 de la iteracion 2
  de 1951A en .198 en vez de .253. El patron de "objetivos nuevos" sigue en 2 de 8 ciclos (2059A y
  2083A).
- Los radios del banco no tienen carga: no se mide efecto sobre time_squeeze y **no se atribuye** efecto
  en el aire.

## Valores NAPI: se mantienen

En 3 de 3 iteraciones la lectura previa a la escritura de 2143A coincide con el valor que 2106A leyo 32
minutos antes: netdev_budget .198 600, netdev_max_backlog .253 768 y netdev_budget .110 300. Cada
lectura final coincide con su lectura base.

## Piso de ruido ambiente (8 ciclos, 24 pliegues)

No es un test A/A controlado:

- fmx_loss de 0.464441 a 0.894905; p95 de RTT de cpe_41 de 3.952 a 31.542 ms.
- goodput de 0.009 a 3.94 Mbps, trafico ambiente del enlace .84 sin carga inyectada.
- La iteracion 1 de 2143A tiene p95 de 3.952 ms, por debajo de todos los pliegues anteriores (minimo
  4.207 ms). Es la linea base inicial del harness, medida con una escritura en un radio de banco sin par
  por aire: es ruido ambiente, no una mejora, y el piso se ensancha otra vez.
- El ancla sin escrituras (2058A, fuera de este conjunto) sigue en 34.08 ms, por encima de todos.

## Catalogo

2143A no cita ids del catalogo de knobs; netdev_budget y netdev_max_backlog no estan en el catalogo, asi
que ninguno es un knob PROTECTED.

## recall-first

Antes de escribir la nota, 4 de 6 consultas al vault unificado tuvieron aciertos: qdisc 57,
netdev_budget 4, netdev_max_backlog 2 y requeues 1; tx_queue_len y rx_fifo_errors 0. No se corrio
chequeo scholar en esta wave (no se pidio).

## Etapa 2154A - vault

La nota #637 quedo en research/notes/scholar_sources/ como evergreen. Se corrio `hyperresearch sync` y
despues `hyperresearch index build`; 19 paginas de indice listan la nota, _recent.md entre ellas. La
primera corrida vio 663 notas antes, 664 despues de sincronizar y 669 despues del index build; el
constructor se volvio a correr para corregir el formato de una linea y calcular dos lecturas desde los
datos, y esa corrida ve 669 antes y despues.

## Etapa 2155A - banda 1536A..2159A y docs maestras

`python tools/generate_command_center_dashboard.py` reconstruyo el tablero (277 recibos en la banda) con
0 apellidos del alcance y 0 alias en toda la pagina; 2142A, 2143A y 2154A aparecen en el feed con su
propia clase de evidencia, y entraron 10 recibos (2136A a 2154A) sobre el tope anterior de 2135. Los
recibos de 2160A en adelante (de otras lineas) quedan fuera a proposito. El servidor :8787 responde
HTTP 200 y sirve la banda nueva. MASTER, CURRENT y CURATED ya estaban en 179 lineas.

## Limites y advertencias (honestas)

- **Sin campeon nuevo** y sin valor de knob conservado.
- Los descartes de qdisc de airOS 8 son acumulados desde el arranque y bajos; en la ventana fueron 0.
- La qdisc de OpenWrt queda sin medir; no se compara OpenWrt contra airOS en la salida.
- No se atribuye efecto en el aire ni sobre time_squeeze a netdev_budget ni a netdev_max_backlog.
- **Verificacion en navegador real: NO realizada** (no hay herramienta de navegador en esta sesion); se
  verifico por CLI con HTTP 200, banda servida y conteo de PII de toda la pagina.

## Que sigue (decision del operador)

- El pendiente de la nota #636 sigue abierto: un A/B con carga inyectada en un panel (por ejemplo
  netdev_budget 300 contra 600) donde el host del knob reenvie el trafico medido, contando ahora tambien
  los descartes de qdisc de ath0 en cada fase.
- No repetir ciclos de banco de netdev_budget: ya hay dos (1951A y 2143A).
- Traer un `tc` estatico para medir la qdisc de Panel1 queda como decision del operador.

Recibos: `stage2154a_netdev_qdisc_and_netdev_budget_telemetry_note637_receipt.json`,
`stage2155a_command_center_1536a_2159a_refresh_receipt.json`, `stage2157a_memorymaster_ingest_receipt.json`,
`stage2159a_wave186_opus2_gate.json`.
