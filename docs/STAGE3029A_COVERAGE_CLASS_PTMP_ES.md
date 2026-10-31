<!-- doc-head: Stage 3029A (W369) ES: coverage class y timeout de ACK en los sectores PtMP de Guarida, offline. Semantica confirmada en el codigo de iw 6.9 y ath10k-ct (3 us por clase al slot, al ACK y al CTS; sin dynack), distancia por CPE con etiqueta MEASURED, DOCUMENTED o UNKNOWN, clase actual por AP, patron propio de MCS de bajada 0 en las tres CPE a mas de 2 km, recomendacion por AP (Panel3, Panel2, Panel1) y spec A/B de costo en banco LAP-120 con clase 0 contra 6 -->
Que cubre: que hace la coverage class en nuestros radios, que ya se probo, a que distancia esta cada CPE de Guarida, que clase tiene hoy cada AP y que se hace con cada sector.
Estado: offline. 0 SSH, 0 escrituras. Datos maquina: artifacts/autoresearch/wave369_coverage_class_ptmp.json (telemetry.db hasta seq 14542).
Arbol: OpenWrt v24.10.4 (78b23a26); iw 6.9 y ath10k-ct 2024-07-30 ac71b14d con hashes iguales a los del Makefile. Rutas de ath10k relativas a ath10k-6.10/.
Leer cuando: antes de escribir distance o coverage en un AP o una CPE de Guarida, o de tocar el kit W340 de Panel3.
<!-- /doc-head -->
# Stage 3029A: coverage class en los sectores PtMP de Guarida (W369)

## Resumen

- **Hoy:** Panel3 esta en clase 0 en los dos extremos (CONFIRMED, 2532A). Panel1 y Panel2 en 0 por defecto de OpenWrt (INFERRED: nadie lo leyo).
- **Distancias:** las tres CPE mas lejanas estan a 2,1-2,85 km, clase 5 a 7 segun `iw`. Las otras diez estan a 1,2 km o menos.
- **Patron propio:** esas tres CPE tienen MCS de bajada mediana 0 con senal de -53 a -63 dBm. Las diez cercanas tienen 6 a 8. Es correlacion con n = 3, no causa.
- **Recomendacion:** no escribir nada en produccion hoy. Primero un A/B de **costo** en banco (clase 0 contra 6); despues, con aprobacion, el A/B de beneficio en Panel3.
- **Corregido:** R13 programo clase 4 y 7, no 3 y 6. "set-coverage-class" es un mensaje de log, no un comando de debugfs.

## 1. Que ya se probo (`artifacts/knob_index/knob_index.json`)

- **PtMP:** `coverage_class` tiene `probado` vacio. El indice no ingirio cuatro recibos de banco PtMP:
  - **1663A ronda 1**, LAP-120 + Loco, ABAB clase 0 contra 1 con AQL igual. Es el **unico A/B limpio** del repo. Goodput igual (A 69,6 y 66,7, B 69,3 y 68,0 Mbit/s) y p95 ruidoso (A 29,8 y 40,8, B 43,2 y 34,0 ms). Un bloque, sin potencia.
  - **1663A ronda 2 y 1753A:** clase 1 junto con VI 750/1500 y BE 1200/2400. REJECT_HOLDOUT_REGRESSION, que no se puede atribuir a la clase.
  - **R13 y R18:** corridas sueltas en secuencia con AQL cambiando. R13 stock en clase 7 contra stock en clase 0 dio 101,7 contra 105,15 Mbit/s (-3,3 %), una corrida cada una.
- **PtP:**
  - El champion v4 (214A) lista juntos `coverage_class 0` y `distance_m 1000`, que es un par contradictorio: distance 1000 programa la clase 3.
  - 161A (distance 1000 contra 300, KEPT +13,7 % en 4 ventanas) corrio sobre un enlace de banco corto. Mide el costo de sobreaprovisionar, no el beneficio.
  - El campeon v2 excluye las dos perillas por depender del enlace.

## 2. Que hace la coverage class (codigo, CONFIRMED_STATIC_SOURCE)

- **`iw set distance D`** programa la clase `(D + 449) / 450`, redondeando hacia arriba (`iw-6.9/phy.c:676`, cita IEEE 802.11-2007 tabla 7-27). Una clase son 450 m, o 3 us de ida y vuelta. El readback es `Coverage class: N (up to 450N m)` (`info.c:527`).
- **OpenWrt** fija `distance 0` por defecto (`mac80211.sh:1186`) y lo aplica en cada wifi up o reload (`:1195`).
- **QCA988x** (`hw.c:592`, ops en `:1159-1160`): el driver lee los registros que dejo el firmware y suma 3 us por clase al slot (`:683`), al timeout de ACK (`:690`) y al de CTS (`:696`).
  - Se niega si el slot base no es 9 o 20 us (`:663`, `:670`). Panel3 usa short slot (telemetria seq 1843), o sea base 9; en Panel1 y Panel2 es INFERRED.
  - Con firmware CT los valores se fijan por WMI (`:709-723`). Sin eso, se reaplican tras un reset del firmware cuando la clase no es 0 (`wmi.c:6459`).
- **Sin dynack:** ath10k-ct no tiene ACKTO_ESTIMATION ni DYN_ACK, asi que `distance auto` no sirve y la clase tiene que ser explicita.
- **Alcance:** la clase del AP vale para todo el phy, o sea para todas las CPE del sector. La de cada CPE vale solo para lo que esa CPE transmite.
- **UNKNOWN: el timeout base de ACK/CTS del firmware.** Ningun recibo lo leyo. "25 us = SIFS 16 + slot 9" es un supuesto de la norma, no un dato del hardware.

## 3. Correcciones a trabajo anterior

- **Wave 81 y `topic_ack_slottime_coverage_class.md`:** "R13 vio clase 3 a 1500 m y 6 a 3000 m" queda **REFUTED**. El JSON de R13 tiene `Coverage class: 4 (up to 1800m)` dos veces y `Coverage class: 7 (up to 3150m)` seis veces; el 3 y el 6 eran etiquetas escritas a mano. El hardware sigue `ceil(d/450)`, asi que la marca NEEDS_LIVE_CONFIRMATION se cierra.
- **W353 y el indice:** "write set-coverage-class en debugfs" queda **REFUTED**. Es un `ath10k_warn` que sale una sola vez (`hw.c:643`). La unica via es nl80211 (`iw phy set coverage` o `set distance`).

## 4. Timeout corto contra timeout largo (Pilar B)

**Corto** (el AP no cubre a la CPE mas lejana):
- Cada trama a esa CPE cuenta como perdida aunque llegue.
- Hay reintentos hasta el limite (short 7 y long 4 en Panel3), tx_failed se infla, el control de tasa baja el MCS y se gasta aire de todo el sector.
- Analogo propio en airOS (209A): acktimeout de 35 us contra los 54 us que pide un enlace de 3750 m dio 3,45 M descartes por reintentos.

**Largo:**
- Cada clase alarga 3 us el slot del equipo que la tiene, y lo paga cada acceso, tambien el que va a una CPE cercana.
- Cuenta (INFERRED, BE con AIFSN 3 y CWmin 15): la espera media por acceso pasa de 110,5 us en clase 0 a 299,5 us en clase 6. Eso es 5 a 9 % de aire frente a una rafaga A-MPDU de 2 a 4 ms, y cerca de 9 % con tramas sueltas de 1500 B en MCS0.
- Si solo el AP sube la clase, compite peor que sus CPE por el canal (INFERRED).

**Literatura** (nivel resumen; via `scholar_search` sobre OpenAlex):
- **Simo-Reigadas et al.,** IEEE TMC 9(6), 2010, doi 10.1109/TMC.2010.27: los modelos de DCF que ignoran la propagacion fallan a distancia. Validan con emulacion de canal y proponen ajustar ACKTimeout, CTSTimeout, SlotTime y CWmin. El texto completo (URJC) no estaba disponible el 30/10.
- **Patra et al.,** WiLDNet, NSDI 2007: con un MAC modificado midieron 2 a 5 veces mas throughput en un despliegue real.
- **Chebrolu et al.,** MobiCom 2006, doi 10.1145/1161089.1161099: ocho enlaces de 1 a 37 km. El rendimiento es predecible con buena planificacion y la interferencia es lo que mas dana.
- **Hussain et al.,** 2014, doi 10.5120/16496-5702 (survey de MAC TDMA para enlaces largos) y **Rademacher,** 2015/2016 (solo ns-3).
- **La norma:** la tabla de coverage class no se leyo directamente; se cita por el comentario de iw y por los documentos de comentarios 11-13/0063 y 11-23/0138 del grupo 802.11.

## 5. Distancia por CPE y clase por AP

- **MEASURED:** estimacion de airOS por tiempo de ACK (wstalist 419A y 531A, vista del AP y de la CPE), en pasos de 150 m y antes del corte a OpenWrt.
- **DOCUMENTED:** radiografia del 24/10, sin metodo registrado y con valores fuera de la grilla de 150 m.
- **UNKNOWN:** ni el mapa UISP (W351) ni telemetry.db traen distancia. La telemetria tampoco sondea la clase (0 de 14542 muestras): es un hueco de sondeo.

| AP (clase hoy) | CPE | wstalist m | radiografia m | etiqueta | clase iw | MCS bajada / senal (n) |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Panel3 (0, CONFIRMED) | cpe_210_9 | 2700-2850 | 2275 | MEASURED, conflicto | 6-7 | 0 / -53 (636) |
| | cpe_210_235 | 150-1200 | 1050 | MEASURED | 1-3 | 7 / -38 (917) |
| | cpe_210_238 | 600-900 | 450 | MEASURED | 2 | 7 / -45 (892) |
| Panel2 (0, INFERRED) | cpe_210_21 | 2100-2700 | 2674 | MEASURED | 5-6 | 0 / -63 (43) |
| | cpe_200_169 | 2100-2250 | 2043 | MEASURED | 5 | 0 / -55 (36) |
| | cpe_210_166 | 600 | 578 | MEASURED | 2 | 8 / -43 (651) |
| | cpe_210_83, cpe_210_239, cpe_200_183, cpe_200_213 | 300-450 | 259-578 | MEASURED, conflicto en 200_183 | 1 | 6-8 / -32 a -51 |
| Panel1 (0, INFERRED) | cpe_200_41, cpe_200_223, cpe_200_80 | sin dato | 272-300 | DOCUMENTED | 1 | 7 / -40 a -50 |

**Patron (CORRELATION, INFERRED, n = 3).** La bajada en MCS 0 aparece solo en las CPE a mas de 2 km. La subida en MCS 0 no depende de la distancia: cpe_200_183, cpe_200_213 y cpe_210_83, a 300-450 m, tienen 47 a 78 % de muestras en MCS 0, lo que apunta a una causa del lado del AP, la que RTS ataco.

**2534A no veta la hipotesis.** Los timeouts de ACK y CTS son medias palabras separadas (`hw.h:1170-1173`), las dos con base UNKNOWN. Que RTS 512 bajara 75 % los fallos prueba que el CTS cubre unos 2,3 km; del ACK/BA no dice nada.

**Otras explicaciones:** desbalance de cadenas de 9 dB en .9; Fresnel u obstruccion en los trayectos largos; .9 sin sesiones BA (2532A).

## 6. Recomendacion por AP

1. **Panel3: mantener 0 hoy.** Luego el A/B de costo en banco (seccion 7). Si pasa y se resuelve la distancia de .9 (2275 contra 2850 m), un ABAB en produccion con aprobacion: clase 6 (7 si son 2850 m) en el AP y en cpe_210_9. Metricas: MCS de bajada y tx_failed por trama de .9. Es el primero porque la clase actual esta confirmada, .9 tiene buena observabilidad y solo 2 CPE pagarian el slot. El kit W340 cambia solo la CPE; hay que sumarle el AP.
2. **Panel2: mantener 0.** Antes de probar, leer la clase actual y arreglar la observabilidad de las 2 CPE lejanas (36 y 43 muestras OpenWrt). Despues, el mismo camino con clase 6. Aca son 5 CPE cercanas las que pagarian el slot largo.
3. **Panel1: mantener 0, sin prueba.** Las CPE estan a 272-300 m (2 us de ida y vuelta) y trabajan en MCS 7.

## 7. Spec X-CC1: A/B de costo en banco

- **Equipos:** LAP-120 .20 (AP) y Loco 5AC .250 (CPE), OpenWrt 24.10.4 con el mismo ath10k-ct.
- **Alcance:** el enlace es corto, asi que esto mide solo el **costo** del slot largo (no inferioridad), no el beneficio a distancia.
- **Variable:** la clase en los dos extremos, A = 0 y B = 6 (B' = 7 solo si .9 queda en 2850 m). Se aplica con `iw phy PHY set coverage N`, sin uci commit. PHY es el phy que posee la interfaz del enlace (lo dice `iw dev`); no suponer phy0: en 1663A el AP de .20 era phy4.
- **Fijo:** AQL, RTS apagado, fq, canal, ancho, potencia y firmware. Mezclar perillas es lo que invalido 1663A ronda 2 y 1753A.
- **Readback:** `iw phy PHY info` muestra `Coverage class: N` en los dos extremos; dmesg tiene `set-coverage-class` y no tiene `failed to set coverage class`.
- **Diseno:**
  - A/A primero: si el goodput difiere 2 % o mas, o el p95 5 % o mas, el banco no esta estable y se para.
  - 3 bloques ABBA. Cada fase: aplicar y leer, 2 min de asentamiento y 10 min de medicion.
  - Carga: iperf3 TCP con 4 flujos en subida y bajada desde hosts cableados, mas ping con carga cada 200 ms.
- **Metricas:** goodput; RTT con carga p50/p95/p99; tx_retries y tx_failed por trama; MCS; delta de fq_overmemory; MemAvailable.
- **Decision:** permutacion pareada por bloque con Sidak (889A). B pasa si el goodput no cae mas de 2 % y el p95 no sube mas de 5 %. Si no pasa, se queda 0.
- **Abortar si:** el readback no coincide o dmesg rechaza la clase; el A/A es inestable; hay desasociacion o mas de 5 % de perdida de ping en una ventana; el firmware hace crash; MemAvailable baja de 5120 KiB; o fq_overmemory crece.
- **Rollback:** `iw phy PHY set distance 0` en los dos extremos y readback `Coverage class: 0 (up to 0m)`. `wifi reload` y reboot tambien vuelven a 0, porque no hay uci commit. El watchdog compartido aceptado (`tools/watchdog_acceptance/fmx_watchdog.sh`) se arma antes de la primera escritura.
- **Paso 0 opcional (solo lectura):** leer el registro ACK/CTS (`hw.h:1168`) y PHYCLK (`hw.h:1181`) en .20 para conocer el timeout base en us.

## 8. Que aprueba el operador y limites

- **Aprobaciones:** el uso del banco .20 + .250, y cualquier escritura de clase en Panel3 o Panel2 (en ventana de valle, nunca persistente sin veredicto).
- **Pilar B:** no se corrio el pipeline completo HYPERRESEARCH V8 porque escribe fuera del alcance exclusivo. Se uso `scholar_search` por import directo y la boveda solo en lectura. `scholar_inspect` fallo (timeout y 429) y `scholar_verify_claim` no corrio porque solo acepta arXiv.
- **Contrato Karpathy:** TARGET_NOT_MET; la ola es offline y no midio nada en Panel3.
