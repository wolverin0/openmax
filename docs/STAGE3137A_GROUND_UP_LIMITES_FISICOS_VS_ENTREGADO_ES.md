<!-- doc-head: Stage 3137A (31/10/2026) ground-up contra fisica: estado de los 5 pilares, techos PtP-Colo / PtMP 20 MHz / CPU MIPS / memoria 64 MB frente a lo entregado, con telemetria solo lectura; brecha medida mayor = fallas de CPE por clase de cobertura del AP (antes/despues), 20 MHz PtMP bajo el modelo (causa UNKNOWN), goodput PtP-Colo no medido -->
Que cubre: estado de pilares (con recibo mas reciente), techos fisicos, brechas y causa, mediciones de banco pendientes.
Estado: ANALISIS. 0 escrituras a radios, 0 SSH, nada aplicado. Datos: artifacts/autoresearch/stage3137a_groundup_limits.json.
Leer cuando: antes de pedir ventana de banco, cambiar la clase de cobertura de un AP, o afirmar un techo de PtP-Colo o PtMP.
<!-- /doc-head -->

# Stage 3137A: limites fisicos vs entregado (ground-up)

Datos: telemetria 30/10 14:00Z a 31/10 14:18Z (solo lectura, `tools/observability/telemetry.db`). Etiquetas: CONFIRMED, INFERRED, UNKNOWN, REFUTED, con fuente.

## 0. Empieza con lo que necesitas de mi

Nada urgente para seguir el analisis. Tres decisiones tuyas, ninguna ejecutada aqui:

1. **Goodput del PtP-Colo (produccion):** autorizar un iperf3 TCP por el par. Hoy no hay ninguna medicion de goodput de ese enlace (UNKNOWN). Queda en cola; el banco esta ocupado (W457).
2. **Clase de cobertura del AP de Panel1 (produccion):** la regla de 3111A §3 queda cuestionada por datos (seccion 3.3). Un ABAB clase 0 vs 6 requiere tu autorizacion.
3. **Ventana de banco:** al terminar W457, W460 y W467, reservar una ventana para las pruebas de la seccion 7.

## 1. Respuesta corta

- **Ground-up hoy:** en banco hay avance real pero parcial. Confirmado: carga y rollback en vivo de la RAM Xtensa (PB-040), hook WMI 0x9044 activo en .241/.242, SQ de LTU y AirPrism en banco. Abierto: el modulo PPDU-end no cargo en banco (3016A), el canario PB-040 en PtP-Colo fallo el protocolo de firmware (1626A, 28/10) y el canario de PtP-Colo no esta autorizado (3013A).
- **Quien trabaja / auto-research:** segun AGENTS.md §3, el RE binario (Pilar A) es exclusivo de lane_4. Estado vivo de lanes y autoresearch: UNKNOWN (no consultado); los ultimos recibos son del 26 al 28/10. Bancos ocupados: .241/.242 (W457), .116 (W460), LTU (W467).
- **Brecha mayor medida:** fallas de CPE por clase de cobertura. Antes del cambio, hasta 78% de los reintentos de una CPE terminaban en falla; despues, 0,2-3,6% en las CPE que cambiaron (CONFIRMED en contadores; causa INFERRED).
- **Segunda brecha:** PtMP a 20 MHz medido 64-70 Mbps contra 128 Mbps modelados (ratio 0,50-0,55, n=2). La CPU no es el limite; la causa es UNKNOWN.
- **Tercera:** PtP-Colo sin goodput medido. Techo TCP modelado 118-144 Mbps.
- **Demanda vs plan:** no hay saturacion de radio en operacion normal: pico de un minuto por panel 14-26 Mbps. El cap de 15 Mbps por CPE es del plan, no de la radio.
- **Memoria:** nueve CPE tocaron entre 3,3 y 4,4 MB en 24 h; tres de ellas (cpe_200_169, cpe_210_166, cpe_210_21) bajaron a 3,3-3,6 MB, a 0,2-0,5 MB del piso de 3072 kB. Entre 13% y 54% de las muestras de cada CPE se omiten por la guarda: impacto en observabilidad, no en RF.

## 2. Estado de los pilares

Orden: gana el recibo mas reciente y mas especifico. P1..P5 = pilares 1 a 5 del blueprint.

| Item | Estado | Evidencia (fecha) | Etiqueta |
| :-- | :-- | :-- | :-- |
| P1 PB-040 carga RAM y rollback en vivo | HECHO en banco | 1620A PASS recarga + rollback real; 1536A PASS driver-metadata | CONFIRMED |
| P1 PB-050+PB-040 en PtP | FALLA PARCIAL | 1626A (28/10 02:14Z) PARTIAL_FAILED_FIRMWARE_PROTOCOL; supera a 471A (27/10, "100% READY") | CONFIRMED |
| P1 efecto RF de CCA (PB-031) y sub-20 MHz (PB-030) | ABIERTO | sin recibo de efecto RF | UNKNOWN |
| P2 extractor PPDU-end offline | HECHO offline | 3019A build con SDK oficial; 3031A CONFIRMED_OFFLINE; runtime UNKNOWN | CONFIRMED |
| P2 exportar PPDU-end por pktlog/userspace | REFUTADO | 3015A (gate lane4) y 3018A (W355 P3) | REFUTED |
| P2 modulo PPDU-end en banco | NO CARGO | 3016A: swap RAM en .20, modulo no cargo, rollback en 14 s | CONFIRMED |
| P2 beneficio RF y ranging 1,87 m | ABIERTO | 3027A gate PARTIAL: no atribuir mejora RF ni precision | UNKNOWN |
| P3 hook WMI 0x9044 activo | HECHO en banco | 428A (26/10): `wmi_peer_rate_retry_cmdid` 0x9044 activo en .241 y .242 | CONFIRMED |
| P3 fallback 2x2 a 1x2 medido | ABIERTO | 428A no separa su efecto | UNKNOWN |
| P4 SQ LTU y AirPrism en banco | HECHO en banco | 1548A (28/10 00:55Z) | CONFIRMED |
| P4 LTU-Lite OTA (17B) | UNKNOWN | receipt sin campo de veredicto en el nivel superior | UNKNOWN |
| P5 rescate de cadena (chain-mask) | PARCIAL | 428A: 1472 B post-rescate, 10,0% perdida; blueprint dice 0% (349A, 20/20) | CONFIRMED (conflicto) |
| P5 canario PtP-Colo | NO HECHO | 3013A: "No se autoriza despliegue automatico en PtP-Colo" | CONFIRMED |
| P5 clasificador cooperativo (350A) en produccion | ABIERTO | build existe; sin recibo de produccion | UNKNOWN |
| MCS 9 en VHT20 con 2 SS | REFUTADO | 3114A seccion 1, por la norma (no re-leida aqui) | REFUTED |
| Bajar potencia del PtP-Colo a -45 dBm sin costo | REFUTADO | 3114A W452b y W452c NO_GO; retries de subida x3,1 a x4,6 | CONFIRMED |
| Saturacion de potencia del PtP-Colo a 24 dBm | REFUTADO | 3114A seccion 6: hipotesis no sostenida | CONFIRMED |

Conflictos: 471A vs 1626A (gana 1626A, mas reciente y especifico). Blueprint "0% de perdida tras rescate" vs 428A 10% (sin resolver: 349A fue 20/20; 428A fue 1472 B en vivo; gana 428A por ser el dato vivo).

## 3. Techos fisicos vs entregado

### 3.1 PtP-Colo (VHT20 2x2, MCS 8, SGI)

- **Techo PHY:** 173,3 Mbps en ambos sentidos como capacidad (MCS 8, 2 SS, SGI; 3114A seccion 1). Observado (CONFIRMED: `artifacts/autoresearch/wave438_colo_bql.json`; telemetria `ptp_colo_sta` 24 h): RX 173,3 MCS8, TX 144,4 MCS7.
- **Techo TCP modelado:** 144,3 Mbps con 64 subtramas, 134,4 con 32, 118,1 con 16 (MCS 8, payload 1448 B, un cliente, sin contencion). INFERRED: constantes 802.11ac de memoria (DIFS 34 us, backoff medio 67,5 us, A-MPDU de 1538 B, un ACK de bloque por ciclo); sin archivo fuente en el repo (no reproducible desde artifacts); no re-leido de la norma.
- **Entregado:** UNKNOWN. `wave438` tiene `measured_bottleneck_goodput_mbps: null`; no hay iperf del par. El 20,6 Mbps de `stage1656a` es un diagnostico de banco no identificado; no es el Colo.
- **Senales:** 93.445 reintentos/h y 29 fallas/h en la STA (24 h). W452 a 24 dBm: reintentos por paquete subida 0,0055, bajada 0,0001 (CONFIRMED: 3114A seccion 4).
- **Potencia:** INFERRED (fisica). A -46 dBm RSSI el SNR queda muy por encima del ruido termico de 20 MHz (kTB ~ -101 dBm; NF no medido). Un SNR simple no explica el salto de reintentos de W452b/c. Candidatos: adaptacion de tasa del firmware o interferencia en canal 153. UNKNOWN: no se midio espectro.

### 3.2 PtMP por panel (20 MHz)

Tasas DL reportadas por CPE, snapshot 31/10 13:28-14:22Z (CONFIRMED, telemetria). P1 = Panel1, P2 = Panel2, P3 = Panel3.

| Panel | CPE | DL reportadas (Mbps) | Media aritmetica | Media armonica | Modelo x0,83 | Aire si todas a 15 Mbps |
| :-- | --: | :-- | --: | --: | --: | --: |
| P1 | 3 | 144,4 / 173,3 / 144,4 | 154,0 | 152,9 | 127,8 | 35% |
| P2 | 7 | 144,4 / 104 / 173,3 / 173,3 / 117 / 78 / 78 | 124,0 | 112,4 | 102,9 | 112% |
| P3 | 3 | 173,3 / 144,4 / 144,4 | 154,0 | 152,9 | 127,8 | 35% |

- **Dos modelos de reparto (INFERRED):** la media aritmetica es el aire repartido en partes iguales (ATF). La media armonica es el mismo caudal por CPE (DCF sin ATF). Difieren poco en P1 y P3; 10% en P2.
- **0,83:** eficiencia de TXOP del modelo de 3.1 (INFERRED). No se calibro con P1; no es un factor transferible.
- **104, 117 y 78 Mbps:** tasas de intervalo corto (LGI). Los valores SGI de VHT20 2SS son 115,6, 130 y 86,7 (aritmetica CONFIRMED; que el firmware elija LGI es INFERRED).
- **Medido P1 a 20 MHz, 3 CPE:** 63,95 y 70,45 Mbps, CPU AP 68,7% y 45,4% (CONFIRMED: `artifacts/observability/guarida_panel1_ground_up_fastpath_bridge_20261028.json`). Una tercera corrida de 147,92 la W336 atribuye a un error de parser de ancho; la receta W334 dice que la dispersion es real. UNKNOWN: uso solo las dos corridas.
- **Ratio medido/modelo P1:** 0,50 (63,95) y 0,55 (70,45). Causa UNKNOWN. Candidatos INFERRED: reparto desigual (una CPE llego a 3,25 Mbps en una corrida), reintentos del cliente mas debil, agregacion corta con 3 estaciones.
- **Demanda real** (CONFIRMED, `fmx_sidecar_queue_minute`, delta por minuto, 1413 min): suma DL por panel. Pico de minuto 25,2 (P1), 25,7 (P2), 14,4 (P3) Mbps; p95 9,2 / 13,6 / 5,4; mediana 2,8 / 4,2 / 0,16. El pico de P2 es 36% de la mediana medida a 20 MHz.
- **Aire promedio** (INFERRED, bytes/PHY sin sobrecarga): P1 2,2%, P2 4,0%, P3 0,8%.
- **Por CPE:** en 0 a 5 de 1413 minutos llega al 90% del cap; el descarte del shaper aparece en 0 a 694 minutos (rafagas). WAVE335 §5 ya trae el margen de 4 a 7 planes por sector; no lo rederivo.

### 3.3 Clase de cobertura y fallas (brecha medida mayor)

- **Mecanismo** (CONFIRMED en codigo upstream): `ath10k_hw_qca988x_set_coverage_class` (registrada en `qca988x_ops`): slot += 3·C us; ack/cts timeout += 3·C us. Fuente: `https://raw.githubusercontent.com/torvalds/linux/master/drivers/net/wireless/ath/ath10k/hw.c`. Es master upstream, no el ath10k-ct de produccion (INFERRED que es igual).
- **Costo de aire por TXOP** (INFERRED): 28,5·C us (DIFS y backoff). Clase 6: 171 us = 3,3% de un ciclo de 64 subtramas (5136 us), 10,9% de uno de 16 (1569 us). Clase 7: 200 us = 3,9% y 12,7%.
- **Un fallo solo cuesta +3·C us de timeout** (clase 6: +18 us). Eso no explica por si solo 70% de intentos fallidos. Candidatos (INFERRED, sin medir): timeout de ACK corto para estaciones lejanas en clase 0; aire consumido por reintentos de una CPE lejana.
- **Antes/despues** (CONFIRMED en contadores; causa INFERRED; confundido por hora del dia, sin A/A). P3 AP clase 7 desde 31/10 02:17Z (3111A §1, W448). P2 AP clase 6 desde 31/10 03:50Z (W447). Metrica: fallas / reintentos de la misma estacion.

| CPE | Distancia (3111A; cpe_210_9 de wave431) | Antes | Despues |
| :-- | :-- | --: | --: |
| cpe_210_9 (P3) | 2275 m | 77,7% | 0,46% |
| cpe_200_169 (P2) | 2250 m | 71,6% | 2,5% |
| cpe_210_21 (P2) | sin dato en 3111A | 69,4% | 2,2% |
| cpe_210_83 (P2) | 450-578 m | 15,0% | 3,6% |
| cpe_200_183 (P2) | 300-578 m | 19,8% | 3,5% |
| cpe_200_213 (P2) | 259-300 m | 4,5% | 1,4% |
| cpe_210_166 (P2) | 578-600 m | 2,3% | 1,3% |
| cpe_210_239 (P2) | 300-450 m | 0,9% | 0,17% |
| cpe_210_235 (P3) | 150-1200 m | 1,36% | 0,17% |
| cpe_210_238 (P3) | 600-900 m | 0,54% | 0,28% |

Control sin cambio de clase (P1): cpe_200_41 (1139 m) 0,04%; cpe_200_223 (9 m) 0,11%; cpe_200_80 (272 m UISP) 2,5%.

- **Consecuencia:** el efecto aparece tambien en CPE de 150 a 600 m. Eso contradice la lectura de 3111A §3 ("solo las lejanas"). La regla de 3111A §3 ("subir el AP solo con CPE > 1,5 km y falla/paquete > 0,5") queda cuestionada; no la cambio aqui. Probarla con ABAB en P1 (cpe_200_80, 2,5%) requiere tu autorizacion.
- **Competidor** (CONFIRMED, 1818A del 28/10): P3 tuvo drops "no tx buffer" en las 3 ventanas (CONTINUOUS en el recibo). Puede ser parte del mismo efecto; la atribucion por CPE no esta expuesta.

### 3.4 CPU por paquete (AR9342 535 MHz, un nucleo)

- **Plataforma:** CONFIRMED en docs (`docs/archive/2026-10-25_full_history/CURRENT_STATE.md` stage 5; WAVE335 §3). No re-leida en el equipo.
- **40 MHz, 153,39 Mbps, CPU 80,32%** (W334): 13,2k pps (1448 B) -> 32,5k ciclos/paquete -> techo CPU 191 Mbps.
- **TCP DL 154,58 Mbps, CPU 95,8%** (stage 5): 13,3k pps -> 38,4k ciclos -> techo 161 Mbps.
- **Techo en pps:** 13,9k a 16,5k pps (1448 B). Para paquetes chicos el costo por paquete domina: UNKNOWN aqui.
- **20 MHz, 64-70 Mbps** (5,5-6,0k pps): CPU modelada 40-44%; medida 45-69%. La CPU no es el limite a 20 MHz; el limite es aire/MAC (3.2).
- **XC 720 MHz:** x1,35 solo por reloj (INFERRED, no medido).

### 3.5 Memoria (placas 64 MB; MemTotal 56.120 kB)

| Nodo | MemAvailable ultimo (kB) | Minimo 24 h | Muestras omitidas por guarda |
| :-- | --: | --: | :-- |
| cpe_210_21 | 3.700 | 3.616 | 630 de 1266 (50%) |
| cpe_200_169 | 5.444 | 3.256 | 684 (54%) + 27 SKIPPED_LOW_MEMORY |
| cpe_210_166 | 7.872 | 3.556 | 197 (16%) |
| cpe_210_9 | 5.312 | 3.884 | 304 (24%) |
| cpe_210_83 | 4.436 | 4.436 | 170 (13%) |
| cpe_210_238 | 4.160 | 4.160 | 188 (15%) |
| cpe_210_239 | 4.312 | 4.312 | 168 (13%) |
| cpe_210_235 | 4.916 | 4.916 | 259 (20%) |
| cpe_200_183 | 4.696 | 4.696 | 200 (16%) |
| cpe_200_213 | 5.232 | 4.204 | 211 (17%) |
| cpe_200_223 | 10.880 | 4.444 | 197 (16%) |
| cpe_200_41 | 8.796 | 8.548 | 216 (17%) |
| cpe_200_80 | 11.256 | 5.480 | 283 (22%) |
| AP P1 / P2 / P3 | 14.632 / 17.072 / 14.188 | 12.224 / 11.632 / 10.236 | 224 / 231 / 238 (~18%) |
| ptp_colo AP / STA | 10.856 / 11.460 | 10.300 / 10.916 | 159 / 176 |

Fuente: telemetria 24 h, campo `mem_available_kb`. Piso 3072 kB: regla del tool `wave449_memory` (rpc rechaza por debajo).

- **Desglose cpe_210_83** (CONFIRMED, 31/10): MemFree 11.264; MemAvailable 4.436; Cached 9.728; Slab 9.436 (SUnreclaim 7.892); Committed_AS 11.968; Shmem 356 kB. MemFree menos MemAvailable = 6.828 kB no disponibles: reserva o watermark (INFERRED); el desglose exacto es UNKNOWN.
- **cpe_200_80** (`wave449_bridge_memory.json`, 31/10 04:28Z, lectura de solo lectura en produccion): MemFree 13.332; MemAvailable 16.268; Active 5.132; Shmem 348 kB. MemAvailable mayor que MemFree = cache reclamable (INFERRED).
- **FQ:** en CPE, `fq_memory_limit` 4.194.304 B (4 MiB) con MemAvailable de 3,3 a 4,4 MB en las ajustadas; si llegara a su limite consumiria casi toda la memoria disponible (INFERRED). En 24 h `fq_memory_usage` fue 0 en todas las CPE. En AP, pico 0,46 MB (P1), 1,16 MB (P2), 1,11 MB (P3) (CONFIRMED).
- **fq_overmemory de P2 AP:** incremento 24 h de 119,4 M, pero 5 saltos (4,5 a 53 M cada uno) suman el 99,2%; la mediana del paso es 0. No es una tasa sostenida de descarte: UNKNOWN (posible artefacto de contador). 2720A (simulado) afirma que P2 no tiene descartes por memoria; 2812A es diagnostico offline. No se resuelve aqui.
- **Banco (solo referencia, no produccion)** (`wave449_bridge_memory.json`, 31/10 04:25-04:32Z): lap20 6.560 kB; loco117 2.628; loco250 2.576 (bajo 3072, rpc rechaza) y 3.656 tras parar el servicio (CONFIRMED). No tocar.

## 4. Brechas mayores: techo menos entregado, causa fisica, medicion que la confirma

| # | Brecha | Medido | Causa fisica | Medicion de confirmacion |
| :-- | :-- | :-- | :-- | :-- |
| 1 | Fallas de CPE por clase de cobertura | 70-78% de reintentos fallidos antes en CPE lejanas; 0,2-3,6% despues | Timeout de ACK/CTS y aire perdido en reintentos (INFERRED) | ABAB clase 0 vs 6 con CPE lejana atenuada, station dump por ventana. Produccion: tu autorizacion |
| 2 | PtMP 20 MHz bajo el modelo | 64-70 vs 128 Mbps (ratio 0,50-0,55, n=2) | Reparto desigual, reintentos del cliente debil, agregacion corta (INFERRED) | 1/2/3 CPE iperf3 -R a 20 MHz, MCS fijo, station dump con tx_packets y longitud de A-MPDU. Banco en cola |
| 3 | PtP-Colo sin goodput | Techo TCP 118-144 modelado; medido UNKNOWN | No medido | iperf3 TCP por el par. Produccion: tu autorizacion |
| 4 | Retries del PtP-Colo al bajar potencia | W452b/c x3,1 a x4,6 | Adaptacion de tasa o interferencia, no SNR (INFERRED) | Barrido de potencia a tasa fija en .241/.242 con atenuador |
| 5 | Memoria en CPE ajustadas | 9 CPE con minimo 24 h entre 3.256 y 4.444 kB; 13-54% muestras omitidas | Reserva del kernel y FQ de 4 MiB (INFERRED) | Lectura de solo lectura de meminfo y zoneinfo en una CPE |
| - | Demanda vs plan 15 Mbps | Pico de minuto 14-26 Mbps | Es el plan, no la radio | Ninguna |

## 5. Cambios respecto a docs previos

- **3111A §3:** regla de clase del AP cuestionada por las CPE cercanas de P2 (seccion 3.3). No se cambia el doc de 3111A aqui.
- **WAVE335 §3 vs W334:** 147,92 Mbps; WAVE335 y W336 lo llaman artefacto de parser, la receta W334 lo llama dispersion real. Sin conclusion.
- **471A "100% READY" (27/10):** superado por 1626A (28/10) para PB-040 en PtP.
- **Blueprint "0% perdida tras rescate":** frente a 428A 10%. Sin resolver.
- **2720A (simulado) "ningun descarte por memoria en P2":** no confirmado ni refutado; los saltos de contador no son sostenidos (UNKNOWN).

## 6. Limites

- Sin escrituras a radios, sin SSH y sin lecturas nuevas de produccion. La unica lectura de produccion es el receipt `wave449` (31/10 04:28Z, cpe_200_80).
- Modelos TXOP y CPU: constantes de memoria (INFERRED). No se re-leyo la norma IEEE 802.11ac.
- Snapshot de tasas 31/10 13:28-14:22Z. La ventana de W334 (28/10 22:00-23:59Z) da el mismo conjunto de tasas DL en P1 (CONFIRMED).
- MemoryMaster MCP no conectado: no consulte memoria previa; solo docs y artefactos. Sin nombres ni IDs de suscriptor; los nodos van por ID de registro.
- Sin datos de espectro: la interferencia en canal 153 queda sin medir.

## 7. Pruebas pendientes (orden)

1. [needs_bench, produccion, en cola] iperf3 TCP por el par PtP-Colo. Requiere tu autorizacion.
2. [needs_bench, banco, en cola tras W457] ABAB de clase de cobertura con CPE lejana atenuada.
3. [needs_bench, banco, en cola] 1/2/3 CPE a 20 MHz con MCS fijo y station dump.
4. [lectura de solo lectura, produccion] meminfo y zoneinfo de cpe_210_21 (la mas ajustada y la mas omitida), via `wave449_memory`.
5. [needs_bench, banco, en cola] Barrido de potencia a tasa fija en .241/.242 para separar adaptacion de tasa de SNR.
