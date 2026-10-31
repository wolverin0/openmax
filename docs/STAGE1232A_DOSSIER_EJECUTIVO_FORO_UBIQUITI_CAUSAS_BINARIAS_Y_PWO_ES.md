<!-- doc-head: Stage1232A dossier ejecutivo en espanol de los 117 hilos del foro Ubiquiti (airMAX AC/M y LTU), sus 25 causas raiz binarias .ko, lo confirmado vs hipotesis y el uso recommend-only en el PWO -->
<!-- /doc-head -->
# Stage 1232A - Dossier ejecutivo: foro Ubiquiti, causas binarias y PWO

Estado: documento de sintesis, 100% offline (sin red, sin radios tocadas). Evidencia del foro:
`FORUM_REPORTS_UNVERIFIED_BY_LIVE_HARDWARE`. Nada de este dossier es `CONFIRMED_LIVE_HARDWARE` salvo lo que
se marca asi de forma expresa en la seccion 5. No se citan usuarios, IPs ni MACs.

## 1. Que es el corpus (resumen para decidir)
- 117 hilos publicos de community.ui.com, 2018-10 a 2026-10, todos leidos el 2026-10-27 (`fetch_verified` en los 117).
  Base: `artifacts/research/ubiquiti_community_m_ac_ltu_field_issues_kb.json` (KB v1, Stage 1187A).
- Por familia: airMAX AC 58, airMAX M 9, LTU 50. Respuesta util: 8 con respuesta de personal de Ubiquiti
  como fuente del workaround y 10 con respuesta aceptada; el resto son opiniones de la comunidad o sin workaround.
- Es una muestra de un solo sitio, no un censo de fallas: la ausencia de un hilo no prueba ausencia de falla,
  y la cantidad de hilos mide cuanto se hablo del tema, no cuantos equipos fallan.

## 2. Las clases de sintoma y que significan para un WISP
Conteos leidos del KB (`stats.per_class`, verificados contra la lista de hilos). `other_field_issue` es la 10.a
etiqueta y agrupa 4 hilos LTU que no encajan; las 9 clases operativas son las de la tabla.

| Clase | AC | M | LTU | Total | Lectura operativa |
| :--- | ---: | ---: | ---: | ---: | :--- |
| `ptmp_single_cpe_tx_rate_collapse` | 6 | 0 | 0 | 6 | Un CPE cae de capacidad con buena senal mientras el resto va bien: reclamo individual, sin caida de enlace. |
| `silent_traffic_stall_while_associated` | 13 | 4 | 0 | 17 | Enlace "asociado" y con senal pero sin trafico: el monitoreo por ping/ccq lo ve tarde; suele resolverse reiniciando. |
| `dfs_false_trigger` | 19 | 3 | 0 | 22 | Radar falso, saltos de canal, CAC colgado: cortes de minutos en 5 GHz DFS. Es la clase mas numerosa. |
| `m5_on_ac_mixed_mode_airtime_starvation` | 10 | 0 | 0 | 10 | CPEs M5 viejos en un AP AC (modo mixto) consumen tiempo de aire y degradan a los AC. |
| `ethernet_100m_to_10m_negotiation_drop` | 10 | 2 | 0 | 12 | El puerto Ethernet baja a 10M o flapea: casi siempre cable, conectores o PoE, no radio. |
| `ltu_modulation_stuck_4x_6x` | 0 | 0 | 9 | 9 | Modulacion LTU pegada abajo (4x/6x) o que no sube: enlaces que rinden una fraccion de lo contratado. |
| `ltu_cpe_disconnect_storm` | 0 | 0 | 18 | 18 | CPEs que caen y reconectan en masa: impacto en muchos clientes a la vez. |
| `ltu_auto_frequency_atpc_glitch` | 0 | 0 | 9 | 9 | Auto-frecuencia/ATPC/DFS cambia canal o potencia de forma inesperada. |
| `ltu_udp_iptv_latency_spike` | 0 | 0 | 10 | 10 | Jitter y picos de latencia en UDP/IPTV/multicast. |
| `other_field_issue` | 0 | 0 | 4 | 4 | Problemas reales fuera del set cerrado; sin mecanismo binario atribuible. |
| Total | 58 | 9 | 50 | 117 | |

Notas: la clase de un solo CPE (6 hilos) es la de menor evidencia del corpus. Los totales AC+M (67) y LTU (50)
coinciden con la suma de las filas.

## 3. Causas raiz binarias (.ko): 25 RC
Catalogo `RC-01..RC-25` dentro del KB (`symptom_classes[*].ko_root_causes`). "Causalidad" es la clase de evidencia de
la RC como explicacion del sintoma del foro; "hecho" es la clase del hecho de mecanismo (lo que dice el binario).

| RC | .ko | Mecanismo (resumen) | Causalidad | Hecho |
| :--- | :--- | :--- | :--- | :--- |
| RC-01 | ubnt_poll_host | Umbrales de supresion de reintentos por `cms_bias` (hidden node) | HYPOTHESIS | STATIC_BINARY |
| RC-02 | ubnt_poll_host | Sondeo TDMA, prioridad y airtime por STA | HYPOTHESIS | STATIC_BINARY |
| RC-03 | ubnt_poll_host | ATPC por CPE hacia un RSSI objetivo | HYPOTHESIS | STATIC_BINARY |
| RC-04 | ubnt_poll_host | Timer de missing-poll que termina en panic; bmiss | HYPOTHESIS | STATIC_BINARY |
| RC-05 | umac (otro) | `ubnt_radar_mode` solo en 8.7.25; corte de 521 s en canal DFS | HYPOTHESIS | LIVE_HARDWARE (corte, no radar) |
| RC-06 | ath10k_core | Debugfs DFS/CCA de OpenWrt ath10k-ct (no es driver airOS) | HYPOTHESIS | STATIC_BINARY |
| RC-07 | mac80211 | `ieee80211_radar_detected` en el cutover OpenWrt | HYPOTHESIS | STATIC_BINARY |
| RC-08 | mac80211 | Admision de txq por AQL/airtime (OpenWrt) | HYPOTHESIS | STATIC_BINARY |
| RC-09 | mac80211 | `airtime_flags`/AQL: banco OpenWrt con M5 lento | CONFIRMED_LIVE_HARDWARE (banco OpenWrt) | LIVE_HARDWARE |
| RC-10 | mac80211 | 4-address/AP_VLAN hacia el camino iTXQ | HYPOTHESIS | STATIC_BINARY |
| RC-11 | ath10k_core | Reporte de airtime de ath10k-ct a mac80211 | HYPOTHESIS | STATIC_BINARY |
| RC-12 | otro | Autonegociacion PHY/cable/PoE: fuera del alcance .ko | HYPOTHESIS | ninguno |
| RC-13 | ame_core | Compuertas de subida de MCS LTU (95/96/97 %) | CONFIRMED_STATIC_BINARY | STATIC_BINARY |
| RC-14 | ame_core | Tabla SISO tope MCS 23; 4096-QAM solo MIMO | CONFIRMED_STATIC_BINARY | STATIC_BINARY |
| RC-15 | ame_core | `set_Param_mcs` devuelve el MCS a auto (0x20) | HYPOTHESIS | STATIC_BINARY |
| RC-16 | ame_core | Potencia conducida cae con el MCS | HYPOTHESIS | STATIC_BINARY |
| RC-17 | ame_core | `cpeFsmStop` -> reset-with-setup(1) | HYPOTHESIS | STATIC_BINARY |
| RC-18 | ame_core | Scheduler N/S de CPEs y su activity check | HYPOTHESIS | STATIC_BINARY |
| RC-19 | ame_core | Timing Advance, GPS 1PPS, zona ciclica | HYPOTHESIS | STATIC_BINARY |
| RC-20 | ame_core | auto_freq/smart_scan y deteccion DFS en el modulo | HYPOTHESIS | STATIC_BINARY |
| RC-21 | ame_core | `autopwr_*`, `dlpwr_tune`, `ulpwr_*`, potencia forzada | HYPOTHESIS | STATIC_BINARY |
| RC-22 | ame_core | Escalera de frames 2000/2500/4000/5000 us; bcast | HYPOTHESIS | STATIC_BINARY |
| RC-23 | eab_driver | Modulo ausente del corpus: inanalizable | HYPOTHESIS | ninguno |
| RC-24 | otro | Modelo SimPy+pymoo de torre (sin binario) | SIMULATED_MODEL_ONLY | SIMULATED_MODEL_ONLY |
| RC-25 | otro | Sin atribucion posible | HYPOTHESIS | ninguno |

Lectura: solo RC-13 y RC-14 tienen causalidad respaldada por el binario (techo de modulacion de LTU).
El resto son mecanismos reales del binario ofrecidos como posible explicacion, no probados para el sintoma.

## 4. Leyenda de clases de evidencia
- `CONFIRMED_STATIC_BINARY`: lo dice la decompilacion de un `.ko` concreto (build, offset y constante citados).
- `CONFIRMED_LIVE_HARDWARE`: observado en un equipo propio o banco propio (recibo con fecha).
- `SIMULATED_MODEL_ONLY`: resultado de un modelo, sin binario ni radio.
- `HYPOTHESIS`: plausible, sin respaldo directo; no se usa para decidir.
- `FORUM_REPORTS_UNVERIFIED_BY_LIVE_HARDWARE`: un usuario lo dijo; jamas se promueve a confirmado.

## 5. Confirmado vs hipotesis (estricto)
Confirmado en binario estatico (mecanismo, no sintoma):
- F1, F2 y F3 de la seccion 6; y el resto de los hechos de RC-01..RC-04 y RC-13..RC-22 como existencia de
  codigo, tablas y umbrales en builds concretos.
- `sta_remove_oldest` (unico camino de desalojo por capacidad) no existe en los builds 8.7.4-cs ni 8.7.11 de
  `ubnt_poll_host.ko` (1190A, seccion 7); 8.7.11 tiene 12 hilos en el corpus.
- 1190A deja `UNKNOWN` la hipotesis de un bloqueo a 1x: el modulo no selecciona tasas.
Confirmado en hardware vivo:
- RC-05: una auditoria viva de solo lectura registro un corte de 521 s tras beacon-miss en canal DFS, sin evento de radar;
  el umac 8.7.25 de stock agrego `ubnt_radar_mode`. Prueba que
  hay cortes en DFS en la flota; no prueba que el radar fuera falso.
- RC-09: banco OpenWrt (no AP AC de stock): ATF/AQL bien ajustados bajan la latencia de un AC mezclado con un M5.
Solo hipotesis o reporte de foro:
- Que cualquier firmware concreto "cause" un sintoma; que `free_node` produzca el stall observado por usuarios
  (1190A lo marca `INFERRED`: falta la mitad visible por el par); que el hysteresis 1 vs 90 explique un 4x/6x
  o una tormenta de desconexiones (1191A `INFERRED`); todo lo que dice un hilo sobre "arreglado en X".
- Los hilos son relatos de usuarios con firmware y condiciones no controladas.

## 6. Tres hechos binarios reconciliados
- F1 (`ubnt_poll_host.ko`, MIPS32 BE, 1190A): `check_sta` (offset 0x1860) vence un par a los 120000 ms exactos y
  llama `ieee80211_free_node`; NO llama `ieee80211_kick_node` ni `ath_kickout_node_notify`. El estado local se
  libera sin aviso y el par puede seguir creyendose asociado (forma de un stall silencioso). Tabla de ancho de
  banda del perfil PtMP: 10 MHz -> ht10, 11-28 -> ht20, 29-30 -> ht30, 31-39 -> ht20, 40 -> ht40, y 80 MHz (fuera
  de 10..40) cae al default ht20. La tabla no es monotona; AC de 80 MHz no tiene perfil PtMP propio.
- F2 (`ame_core.ko` LTU 2.4.2, ARM, 1191A): `mcsDnThreshold_timer` = 1 (`.data+0x12d8`) frente a
  `mcsUpThreshold_timer` = 90 (`.data+0x12dc`): bajar de modulacion cuesta 1 unidad de evidencia, subir 90
  (asimetria 90x, con umbrales 10 y 7). Es la forma observable de un 4x/6x pegado; evidencia de la bajada `INFERRED`.
- F3 (1214A): el timer de missing-poll de `ubnt_poll_host.ko` es UNA constante en el sitio de callback/parche
  0x07c08: calcula `(jiffies - uph_dev+0x288) * 1000` y entra en panic con `>= 0x01c9c768` = 30,001,000, unos 30 s
  si jiffies son ms (la escala HZ esta inferida, no verificada). Se retira el "30 min / 1,800,000 ms" de Stage 70A
  (error de unidad: ese inmediato no existe en ninguno de los seis builds). En `ame_core.ko` 2.4.2
  `penaltyThreshold` = 60 (0x3c; `.data` 0x12d2 CPE / 0x12ee AP); se retira el "25" de Stage 12 (error de
  transcripcion). Conflictos retirados: STAGE10 (~30 s, ahora consistente), STAGE70A (30 min), STAGE12 (25) vs STAGE249A (60).

## 7. Como usa el PWO estos hallazgos (siempre asesor)
- Reglas del PWO (`wireless-optimizer/rules/`): `signalRules.js`, `capacityRules.js`, `channelRules.js`,
  `advancedKnobRules.js`, `gpsRules.js`, `tddRules.js`, `ltuRules.js` (motor: `RuleEngine.js`). El catalogo de RC
  cita por id: `LOW_CCQ`, `LOW_CINR`, `HIGH_AIRTIME`, `STATION_PRIORITY_IMBALANCE`, `GPS_SYNC_MISALIGNED`,
  `TDD_FRAME_MISMATCH`, `ATPC_NOT_ENABLED`, `EXCESSIVE_TX_POWER`, `LTU_FRAME_OPTIMIZATION`, `isDFSChannel`.
- RC-10, RC-12, RC-23 y RC-25 no tienen regla del PWO: son brechas declaradas (1213A cubre parte de ellas).
- Politica fija: toda tarjeta es `recommend_only=True`, `auto_approve=False`; una persona aprueba; el PWO no
  aplica cambios y no ejecuta acciones sobre radios en vivo; el veto SG-01 de backbone sigue vigente (1215A).
- El foro solo prioriza que mirar y fija el texto de la advertencia; no es entrada para ninguna accion.
  Los workarounds de la comunidad (reiniciar, cambiar firmware, bajar ancho) se reportan, no se ejecutan.
- Integracion completa y bilateral: ver `docs/STAGE1239A_GUIA_MAESTRA_INTEGRACION_PWO_Y_CONCIENCIA_BILATERAL_ES.md`.

## 8. Asesor de firmware 1233A (nuevo)
`tools/uisp/forum_firmware_regression_and_workaround_advisor.py` (solo lectura, stdlib, sin IO al importar):
`advise(firmware, familia, sintoma=None, kb=None)`. Cuenta menciones de la version en el KB (campo
`fw_versions_mentioned` mas titulo, resumen y workaround), lista causas raiz binarias, hechos binarios si hay
KB v2, y revisiones de solo lectura. Siempre `recommend_only=True`, `auto_approve=False`, `applied_changes=[]`.
Receipt: `artifacts/verification/stage1233a_firmware_regression_advisor.json`. Resultados de humo (KB v1):
8.7.11 AC = 12 hilos; 6.3.10 M = 1; LTU 2.3.1 = 3; 8.7.25 AC y LTU 2.4.2 = 0 hilos (solo notas binarias).
Una mencion no es una regresion: el asesor lo declara en cada respuesta.

## 9. Brechas y limites
- `eab_driver.ko` no esta en el corpus (0 de 209,121 miembros del tar): RC-23 es inanalizable.
- ath10k/mac80211 analizados son de OpenWrt (`ath10k-ct`, backports), no de airOS de stock: RC-06..RC-11 son analogia.
- Negociacion Ethernet 100M->10M (12 hilos) esta fuera del alcance de un `.ko`: PHY, cable, PoE (RC-12).
- Solo 6 hilos de un unico CPE; clase con la menor base para generalizar.
- Defecto del KB: `fw_versions_mentioned` omite versiones que si aparecen en titulo o resumen (6 hilos; p. ej.
  8.7.14 figura con 0 en el campo pero 2 hilos la mencionan en texto). Los conteos por campo subestiman.
- `RC-04` del KB v1 aun cita el conflicto 30 s vs 30 min; 1214A lo resuelve (seccion 6) y la reconciliacion
  del KB v2 es trabajo de la Wave #32.
- Sin cobertura de versiones recientes: 8.7.25 y LTU 2.4.2 no tienen hilos; sus notas son solo binarias.
- Nada de lo anterior fue repetido en hardware vivo en este stage.

## 10. Checklist del operador
1. Antes de culpar al firmware: descartar RF, cable/PoE y alineacion del equipo afectado.
2. Registrar firmware de ambos extremos, uptime y hora del sintoma; comparar con el ultimo estado conocido bueno.
3. Stall: confirmar con ping/throughput desde ambos lados y guardar syslog y estadisticas antes de reiniciar.
4. DFS: revisar eventos de radar y la lista de canales DFS del equipo antes de cambiar de canal.
5. LTU: anotar modulacion, uptime y SNR; contar caidas por CPE; verificar sincronismo GPS en el AP.
6. Ethernet: cable, conectores y puerto del switch primero; es capa fisica.
7. Ejecutar el asesor (`python -m tools.uisp.forum_firmware_regression_and_workaround_advisor --firmware X --family Y --json`)
   y leer `unknowns` y `caveats` antes que los conteos.
8. Cualquier cambio (canal, ancho, potencia, reinicio, firmware) lo decide y aplica una persona, en ventana.

## 11. Referencias
- `docs/STAGE1187A_UBIQUITI_COMMUNITY_FORUM_M_AC_LTU_FIELD_ISSUES_AND_KO_ROOT_CAUSES.md` (corpus y 25 RC)
- `docs/STAGE1190A_UPH_PTMP_RATE_COLLAPSE_AND_SILENT_STALL_RE.md` (F1)
- `docs/STAGE1191A_LTU_MODULATION_ATPC_AND_DISCONNECT_STORM_RE.md` (F2)
- `docs/STAGE1214A_BINARY_CONSTANTS_RECONCILIATION_POLL_TIMER_AND_PENALTY.md` (F3)
- `docs/STAGE1239A_GUIA_MAESTRA_INTEGRACION_PWO_Y_CONCIENCIA_BILATERAL_ES.md` (integracion PWO)
- `docs/STAGE1192A_BINARY_RE_TO_FIELD_SYMPTOM_SIGNATURES_MATRIX.md`, `docs/STAGE1213A_PWO_COVERAGE_GAP_RULES_STALL_ETH_DISCONNECT.md`,
  `docs/STAGE1215A_UNIFIED_BILATERAL_AND_FORUM_GROUNDED_PWO_ADVISOR.md`
