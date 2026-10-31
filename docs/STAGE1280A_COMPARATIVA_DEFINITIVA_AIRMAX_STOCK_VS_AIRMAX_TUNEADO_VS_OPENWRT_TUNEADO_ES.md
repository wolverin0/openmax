<!-- doc-head: Stage 1280A comparativa lado a lado airOS 8 stock vs airOS 8 tuneado vs OpenWrt 24.10.4 tuneado (v17), PtP y PtMP, solo desde recibos guardados, con N/D explicitos y sin ranking global. -->
# Stage 1280A - Comparativa: airOS 8 stock vs airOS 8 tuneado vs OpenWrt 24.10.4 tuneado (v17)

Estado: OFFLINE, solo lectura de recibos locales; no mide nada nuevo, no es aceptacion fisica ni `PRODUCTION_READY`.
Datos celda por celda (valor, unidad, fuente + puntero JSON, setup, clase de evidencia, warnings): [`stage1280a_three_way_comparison_scorecard.json`](../artifacts/verification/stage1280a_three_way_comparison_scorecard.json). Los codigos `[S..]` y `RIG_..` de este doc son ids de ese JSON (`sources`, `setups`, con sha256 calculado en disco).
Etiquetas: CONFIRMED / INFERRED / UNKNOWN / REFUTED. Clase `CONFIRMED_LIVE_HARDWARE` aqui = hay ventanas crudas del equipo en el recibo; NO implica A/A controlado valido (regla Stage 1028A; las auditorias 887A/1003A del repo clasifican casi todos estos recibos UNKNOWN o PENDING_LIVE_RETEST).

## 1. Respuesta corta (lo que las celdas SI soportan)
1. **No hay ranking global defendible**: ninguna combinacion A/B/C se midio en la misma ventana, con el mismo generador de carga y el mismo canal. Cada columna sale de una rig distinta del mismo par PowerBeam (PtP) o de sectores distintos (PtMP).
2. **PtP, mismo par .241/.242, referencia historica**: stock airOS = 22.80 Mbps (DL 19.20 + UL 3.60), p50 idle 1.96 ms [S105_stock]. OpenWrt Champion v2 = 20.58 Mbps medio (-9.7 %, recomputado) y v3 en VHT40 = 24.18 (+6.1 %, pero con el doble de ancho de canal y 6.0 % de perdida 1472B en la media). El "+93 %" de la documentacion es contra el brazo OpenWrt por defecto (10.64), no contra airOS.
3. **airOS tuneado vs airOS stock** solo tiene evidencia pareada en Stage 53A: goodput DL igual (26.042 vs 26.145, -0.4 %), RTT bajo carga p50/p95/p99 -42/-37/-37 % (7.95/15.76/16.65 vs 13.78/25.00/26.26 ms). Los campeones v7..v9 se compararon contra el incumbente, nunca contra stock.
4. **OpenWrt v17 PtP no esta certificado ni es rankeable**: 1176A `BLOCKED_OTA_HEALTH`, A/A `INCONCLUSIVE` (deriva 141.7 %), 17 ventanas validas (12 A/A + 5 discovery = 2 pares completos), holdout 0; el "goodput" es un proxy `rx_bytes/dt`. 1175A solo prueba el ciclo de vida del kit.
5. **PtMP**: no existe ningun AP airOS (stock ni tuneado) medido con goodput/RTT. El unico PtMP medido es un AP OpenWrt LAP-120 con 3 CPE mixtos; su "v17" (Stage 51A) es OTRA cosa que el kit v17 PtP y el 97.8 % del goodput lo da un solo CPE.

## 2. Colision de nombres "v17" y stages mal atribuidos (leer antes de las tablas)
| Nombre | Que es realmente | Medicion viva |
| :-- | :-- | :-- |
| v17 #1 | Kit PBE5AC PtP Pareto AQM/AQL BusyBox (sha256 `8453c92d...`, [1050A](STAGE1050A_WA_V17_PARETO_AQM_AQL_BUSYBOX_KIT.md), [1175A](STAGE1175A_LIVE_PBE5AC_V17_VERIFIED_LIFECYCLE.md), [1176A](STAGE1176A_OTA_HEALTH_ABORT_CLOSURE.md)) | 17 ventanas diagnosticas, BLOCKED |
| v17 #2 | Stage 51A, sector LAP-120 + 3 CPE, BQL `eth0` 42392/3028/1000, relativo a v16 ([CURRENT_STATE](CURRENT_STATE_CONTINUATION_987d82886f_001.md)) | si, 6 rondas/24 ventanas, superado por v18..v23 |
| v17 #3 | `99-fmx-wa-universal-champion-v17` (correccion 1075A) | ninguna |
| Otros | 647A = RE ring HTT RX, 694A = RE ring DMA LTU, 722A = Pareto NSGA-III, 763A = DHCP rogue + guard ANI: docs RE/guard, no benchmarks. El "airOS v9" del brief = S94A/S95B; "kit v23" = 101A (AP OpenWrt + CPE airOS XC tuneado, NO un AP airOS). | - |

## 3. PtP (par PowerBeam 5AC Gen2 .241/.242)
Columnas: A = stock airOS 8; B = airOS tuneado (Champion v9, S94A-R1 Arm B; entre parentesis otros campeones); C = OpenWrt v17 (1176A); R = referencia OpenWrt medida v2/v3 (no es v17).
| Metrica | A stock airOS | B airOS tuneado | C OpenWrt v17 | R OpenWrt v2 / v3 |
| :-- | :-- | :-- | :-- | :-- |
| Goodput Mbps | **22.80** idle-ref [S105_stock]; 26.15 DL bajo carga [S53A] | **12.61** [S94A] (v7 21.27 [S79A]; v9+CSA 13.79 [S95B]; v1 26.04 DL [S53A]) | **15.97** proxy rx_bytes/dt, n=2 ventanas [S1176]; A/A 8.12-19.63 | 20.58 [S429] / 24.18 [S583] |
| RTT p50 ms | 1.96 idle / 13.78 carga | 2.68 carga (v7 2.49; v1 7.95) | 19.6 carga ICMP 64B (base Arm A 44.2) | 1.73 idle (carga 15.6) |
| RTT p95 ms | 7.56 idle / 25.00 carga | 5.66 (v7 5.11; v9+CSA 17.18) | 28.5 (=max, n=12; Arm A 82.4) | 3.78 (=max) |
| RTT p99 ms | 10.68 idle (=max) / 26.26 | 9.41 (v7 5.30) | 28.5 (=max) | 3.78 (=max) |
| Triple-Play | 0.425 fmx_loss PARCIAL derivado (53A, sin Jain/retry) | fmx_loss **0.348** (v7 0.179; v9+CSA 0.495; v1 parcial 0.277) | N/D | N/D (488A: IPTV 0 % perdida, VoIP64 6 %, proxies ICMP) |
| CPU softirq % | N/D | N/D | N/D | N/D |
| RAM libre MB | N/D | N/D | N/D | N/D |
Triple-Play = `fmx_loss` de `compute_fmx_objective` ([harness](../orchestration/autoresearch/fmx_autoresearch_harness.py), menor es mejor: `0.45 deficit_goodput + 0.25 p95_exceso + 0.15 p99_exceso + 0.10 injusticia + 0.05 retries`) con la `ObjectiveConfig` de los runners airOS PtP (target 30 Mbps, RTT base 2.5 ms, presupuesto 25 ms). Solo es comparable dentro de la misma config; el 0.425 de A y el 0.277 del v1 son derivados por esta etapa (labelled `derived_partial`).
N/D de CPU/RAM PtP: ningun recibo PBE5AC (53A..95B, 105A, 429A, 583A, 1175A, 1176A) guarda `/proc/stat` ni MemFree (los "14,428 KiB" de 68A son tmpfs `/var`).

## 4. PtMP
| Metrica | A stock airOS (sector) | B airOS tuneado (AP) | C OpenWrt "v17" = Stage 51A R6 |
| :-- | :-- | :-- | :-- |
| Goodput Mbps | N/D (solo SIM: 43.85 [442A], 92.40 [724A]) | N/D (proxy: 57.39 con CPE XC airOS tuneado bajo AP OpenWrt [S93B]) | **42.35** agregado 3 CPE (A v16: 39.72); 97.8 % del Loco OpenWrt, XC ~0.9-1.0, XW ~0.03, Jain ~0.35 |
| RTT p50 / p95 / p99 ms | N/D | N/D | **33.85 / 92.73 / 98.23** (v16: 52.90 / 98.76 / 102.80) |
| Triple-Play | N/D | N/D | Pareto +8.75 % vs v16 (NO es fmx_loss); jitter IPTV 1.54 ms, VoIP 1.72 ms, perdida IPTV 0.070 %, VoIP 0 |
| CPU softirq % | **13.61** (Panel2 .82), 10.04 (.83) [S210], produccion pasiva | N/D | N/D (doc: 21.97 % en banco 1-CPE v2, otra rig [S163]) |
| RAM libre | **15.72 MiB** (.82), 15.45 (.83) [S210], MemFree | N/D | N/D (Panel1 produccion 10.01 MB MemAvailable, champion v4 [S214]) |
Panel2/3 corren stock (sin `rc.poststart`): no existe un "PtMP airOS tuneado". Evidencia SIMULATED_MODEL_ONLY (442A, 724A) no se mezcla con celdas medidas.

## 5. Setup y clase de evidencia (detalle en `setups` del JSON)
| Celda | Rig / ventanas | Clase | Limite principal |
| :-- | :-- | :-- | :-- |
| A PtP [S105_stock] | .241 v8.7.25 <-> .242 v8.7.11, 5205 MHz VHT20, 1 resumen historico, sin ventanas, n no registrado | LIVE_BENCH_SUMMARY_NO_RAW_WINDOWS (887A UNKNOWN) | ancla de todos los "supera airOS"; canal 5205 vs 5200 de OpenWrt |
| A/B PtP [S53A] | mismo par airOS 8.7.11, 5205 MHz, A1B1A2B2, R4 = 4 ventanas | CONFIRMED_LIVE_HARDWARE (sin A/A valido) | Arm A = sysctl stock (txq 1000, budget 300); iperf3 vs 1015A ("sin iperf3") |
| B PtP [S94A] [S79A] [S95B] | mismo par, 4 ventanas ~7 s c/u; 79A sin canal registrado | CONFIRMED_LIVE_HARDWARE (UNKNOWN en 887A) | Arm A = incumbente v8/v6, no stock |
| R PtP [S429] [S583] | par flasheado a OpenWrt 24.10.4, 5200 MHz, VHT20 (v3: VHT40), 4 ventanas | CONFIRMED_LIVE_HARDWARE (887A: CONFIRMED_LIVE_BENCH, triage heuristico), sin A/A controlado | percentiles = max; brazo A = OpenWrt por defecto |
| C PtP [S1176] | OpenWrt (24.10.4 INFERRED), 5200 MHz VHT20, 12 A/A + 5 discovery (3 A, 2 B), HTTP bursts >=10 s | CONFIRMED_LIVE_HARDWARE crudo, solo diagnostico | BLOCKED_OTA_HEALTH; A/A INCONCLUSIVE; excluido de rankings |
| C PtMP [S51A] | LAP-120 .20 OpenWrt 24.10.4, 5180 MHz VHT20, Loco OpenWrt + XC airOS 8 + XW airOS 6, 4 ventanas ~6.6 s | CONFIRMED_LIVE_HARDWARE (887A UNKNOWN) | brazo A = v16; delta +6.6 % menor que la dispersion A1/A2 (37.67 vs 41.77) |
| A PtMP [S210] | Panel2/3 Guarida, stock, lectura pasiva | LIVE_PRODUCTION_PASSIVE_READ | metodo de sirq (instantaneo o desde boot) no registrado |
Comparabilidad: A, B, C, R difieren en canal (5205/5200/5205-5200 CSA/sin registrar), generador (iperf3 -P2, HTTP bursts, uclient-fetch, host probe), duracion de ventana (7-10 s), tipo de RTT (idle 64B vs cargado) y firmware. Los % entre columnas son orientativos; no encadenar deltas entre stages (el brazo A de `fmx_loss` oscila 0.23-0.55 entre stages del mismo perfil).

## 6. Knobs cambiados (`nombre=stock->tuneado`, tal cual esta registrado; N/R = "antes" no registrado)
**airOS tuneado (linaje v9; stock = defaults airOS 8.7.11):** `tx_queue_len=1000->192`; `netdev_budget=300->600` (800 en v8); `dev_weight=N/R->64`; `netdev_max_backlog=N/R->600/2000`; `set_multiq=0->3`; `vow_extstats=1->0`; `enable_tx_tcp_cksum=0->1`; `set_CabqMaxdur=100->15`; `rmmod ath_pktlog` (cargado->descargado, un solo sentido por boot); `doth/vap_doth=N/R->1`; `uph_wifi0/ptp_xmit=0->1`; `daprot=1->2`; `ff_mcast_airtime_limit=0->5`; `timing=N/R->'200 200 5000'`; WMM AC_VI/VO aifs/cwmin/cwmax y AC_BE cwmin3/cwmax6, ampdu 24/32, acktimeout 25us (53A/60A, prosa); `tcp_limit_output_bytes=N/R->131072` (sysctl inexistente en Linux 3.3.8, ver D11). Minfree ACBE/BK/VI/VO 32/48/16/0 quedan stock (70B/80B descartados). Fuente: [1257A](STAGE1257A_CATALOGO_COMPLETO_VALORES_TUNEADOS_AUTORESEARCH_PTP_PTMP_LTU_ES.md) lineas 60-85, [S53A], [S94A].
**OpenWrt v17 PtP** (vs lectura del Arm A de 1176A, que NO es OpenWrt stock ni de fabrica, 1044A:13-14): `aql_threshold=24000->12000`; `aql_txq_limit` AC0 `5000/12000->500/1000`, AC1 `->1500/3000`, AC2 `->3000/6000`, AC3 `->1500/3000`; `fq_limit=8192->2048`; `fq_memory_limit=16777216->4194304`; `fq_quantum=3028->1514`; `nf_cal_period=30->120`; `pktlog_filter=64->0`; `tcp_notsent_lowat=4294967295->131072`; AP `rate_override mcs=4->3`, STA `nss=1->0`; `default_qdisc=fq_codel` (kit). Abierto: 1146A, `aql_threshold` 24000 vs 12000 SquashFS vs kit (MASTER_INDEX:95).
**OpenWrt v2 (429A) vs OpenWrt por defecto:** AP `nss=1 mcs=3 pream=3 sgi=0`, STA `nss=0 mcs=2`; `short_gi_*=0`; `disassoc_low_ack=0`; `htt_max_amsdu_ampdu="3 64"`; `fq_quantum=1514->300`; `bql_limit_max=32768`; `aql 24000->4000/12000`; `txpower=2300 mBm`.
**OpenWrt "v17" PtMP (51A vs v16):** `eth0 bql limit_max=1879048192->42392`, `limit_min=0->3028`, `hold_time=1000` (igual), `dev_weight_tx_bias=2` heredado. **airOS tuneado PtMP:** sin knobs (no existe).

## 7. Inconsistencias encontradas en documentos (archivo:linea; detalle en `discrepancies` del JSON)
| Id | Donde | Problema |
| :-- | :-- | :-- |
| D1 | STAGE491A:29 | Fila "OpenWrt Arm A medio" mezcla dos corridas: latencia 1.659/2.470 de 105A (su Arm A pierde 26.5 %); 9.67/0.97/10.64 y 30.0 % de 429A |
| D2 | STAGE491A:30, STAGE587A:13 | Fila "v2" une goodput de 429A con latencia 1.589/2.676 del Champion v1 (105A); v2 real: 1.725/3.782 |
| D3 | STAGE491A:30, STAGE105A:14 | "-64.6 % p95 / -74.9 % p99": p95==p99==max en todas las ventanas 105A/429A; vs el control OpenWrt el signo cambia (+8.3 % en 105A, -32.9 % en 429A) |
| D4 | STAGE429A, STAGE488A:20-21 | Omiten que v2 empeora RTT bajo carga (15.6 vs 6.0 ms, A perdio 20 %), 1472B p50 22 vs 2.5-3.7 ms, VoIP64 p50 3.57->21.39 y p95 46->147 ms |
| D5 | STAGE488A:20 | IPTV Arm A p50/jitter 15.490/14.170 y "15 probes" vs recibo 14.582/15.960 y 13 |
| D6 | STAGE699A:17 | v2 con "AQL 1500/2000"; el recibo 429A dice 4000 y 488A 4000/12000 (1500/2000 es de v3) |
| D7 | STAGE587A:13 | v3 "0.0 % 1472B" va junto al pico B1 (cierto en B1) pero omite que la media trae 6.0 % (B2 12 %, A tambien 6.0 %); la ganancia depende de A1=16.23 (A2 22.38 vs B2 22.90) |
| D8 | CURRENT_STATE:17 | Comprime la procedencia: 741A cita 583A-585A; 25.47 es B1 de v3 (583A), mientras v4 en 695A midio 12.79 (no lo reproduce) |
| D9 | STAGE80B:54 | Fila "v6 73A-R1" = brazo A de 79A-R1 (20.191); 73A-R1 B es 21.871 |
| D10 | STAGE95B:13,31 | Titular VERIFIED/ganancias QoE; recibo propio: agregado -7.16 %, bulk -27.4 %, p95 +190 %, fmx_loss 0.332->0.495 (peor) |
| D11 | STAGE70B:23 vs STAGE80B:31 | v5 incluye `tcp_limit_output_bytes=131072`; 80B dice que no existe en 3.3.8 (FMX-DISC-04) |
| D12 | STAGE93B:16 vs :37-39 | Resumen omite p50 sector +17.6 % (34.86->40.99 ms) |
| D13 | STAGE101A:41-50 vs STAGE1257A:98 | Tabla omite jitter IPTV +1008 % (1.81->20.02 ms) y bitrate IPTV 4.95->3.32 Mbps |
| D14 | CURRENT_STATE_CONT_001:155 | v17 "mejora estricta 3 CPE": 97.8 % de un CPE, Jain ~0.35, perdida IPTV 0.070 % (no 0) |
| D15 | STAGE1015A:28 vs STAGE53A:39 | "radios de 8 MB, sin iperf3" vs 53A usando iperf3 -P2 en el mismo par; sin resolver |
| D16 | STAGE93B:11 vs 51A:12 | AP OpenWrt 24.10.5 vs 24.10.4 |
| D17 | 887A / 1003A | Clases del repo: 105A, 53A, 60A, 79A, 94A, 95B, 51A/52A UNKNOWN; 491A PENDING_LIVE_RETEST ("sin evidencia de adquisicion") |

## 8. Veredicto: que opcion para que, SOLO donde las celdas lo permiten
| Pregunta | Respuesta soportada | Limite |
| :-- | :-- | :-- |
| Goodput PtP maximo | No decidible entre A, B y C. Con la referencia historica A=22.80, OpenWrt v3 en VHT40 (24.18; doble ancho de canal) queda +6 % y v2 en 20 MHz (20.58) -10 %; B y C miden otra cosa (12.6-26.0 segun stage; proxy 15.97) | un solo resumen para A; rigs distintas |
| Latencia de cola PtP | airOS tuneado bajo carga mejora a airOS stock (-37 % p95/p99, S53A). C (carga HTTP, 19.6/28.5 ms) y A/B idle no son comparables | RTT idle vs cargado; C bloqueado |
| Uplink PtP | OpenWrt v2 en 20 MHz (UL 5.54) y v3 en VHT40 (8.47) > airOS stock 20 MHz (3.60 Mbps), pero con peor RTT cargado/VoIP (488A) | brazo A = OpenWrt por defecto |
| Riesgo | v17: BLOCKED_OTA_HEALTH (2/3 respuestas en la ventana 18, causa UNKNOWN), watchdog v17 solo probado en harness; airOS stock sin cambios | cambios de flash/OTA (1258A) |
| Produccion | Ninguna opcion tiene A/A controlado + holdout; `production_ready_count=0` (1011A). No escribir "production-ready" | - |
| PtMP | Solo hay datos con AP OpenWrt (51A: 42.35 Mbps, p50 33.8 ms); para airOS solo CPU/RAM pasivos (sirq 13.6/10.0 %, libre 15.7/15.4 MiB) | no hay comparacion A/B/C posible |
`ranking_eligible_cells = 0` en el JSON: ninguna celda cumple a la vez misma rig, mismo generador y A/A valido.

## 9. Huecos y la medicion que cada uno cierra
| Hueco | Medicion que lo cierra |
| :-- | :-- |
| G1 sin A/B/C en misma ventana; ancla stock = un resumen | Bloques ABBA contrapesados en .241/.242 con el mismo generador/canal (5200): airOS stock / airOS v9 / OpenWrt v17 (requiere ventana RF del operador) |
| G2 v17 PtP bloqueado (17/36 ventanas, 2 pares, proxy) | Causa de la perdida OTA 2/3, luego 12 A/A + 12 A/B + 6 holdout con sumidero TCP/UDP real (adaptador 1013A) y perdida idle 0 |
| G3 no hay AP airOS PtMP medido | Banco 3 CPE con AP airOS (clase Panel2) stock vs tuneado: goodput por CPE, RTT cargado, triple-play |
| G4 PtMP v17 relativo a v16, un CPE domina, sin CPU/RAM | Re-corrida con compuerta de justicia por CPE, softirq + MemAvailable por ventana y brazo control OpenWrt stock |
| G5 softirq/RAM ausentes en todo PtP | Muestrear `/proc/stat` y `/proc/meminfo` antes/despues de cada ventana |
| G6 fmx_loss ausente en A, C y R | Una `ObjectiveConfig` comun + generadores IPTV/VoIP reales en todos los brazos |
| G7 confusores (DHCP rogue 763A, deriva del banco) sin cuantificar | A/A valido (criterios de 1015A) antes de cada comparacion |
Limite de esta etapa: no se leyeron radios; los valores se extrajeron de recibos con scripts locales y los % se recomputaron a mano (coinciden salvo lo listado en la seccion 7).
