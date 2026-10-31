<!-- doc-head: Stage 3135A (ES): perillas de autoresearch sin probar que existen en OpenWrt 24.10.4 ath10k-ct (PtP/PtMP), deduplicadas, con top 15 y 5 protocolos A1-B1-A2-B2 con guardas de A/A de la misma corrida. Offline, 0 escrituras en radios ni en produccion. -->
Que cubre: inventario deduplicado del indice, discrepancias entre el indice y los recibos del 24/10, top 15 ordenado, protocolos predeclarados para el top 5 y anexo con los 52 nombres del pool de trabajo.
Estado: offline. No se escribio en radios ni en produccion. Datos en artifacts/autoresearch/stage3135a_knob_priorities.json.
Archivos: artifacts/knob_index/knob_index.json, orchestration/autoresearch/firmware_knob_candidates.json, orchestration/autoresearch/fmx_autoresearch_harness.py, orchestration/autoresearch/empirical_aa_policy.py, tools/bench/run_live_autoresearch_lap120_loco195.py.
Leer cuando: antes de elegir la siguiente perilla de banco, o al tocar el indice de perillas o el harness.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 3135A: priorizacion de perillas de autoresearch

## 0. Respuestas rapidas

- **Ground-up** (chipset, kernel, AQM, SGMT, EVM, WMI): existe como programa (PROGRAM seccion 3, D4). Los 571 knobs de firmware estan `enabled=false` y RAM-safety UNQUALIFIED en 571 de 571 (CONFIRMED: orchestration/autoresearch/firmware_knob_candidates.json). No hay actuacion viva autorizada.
- **Reverse engineering** (fullrea, D5): siguen abiertos TODO-D5.1 (ubntspecd, ame_dfs) y TODO-D5.2 (registros SGMT), segun PROGRAM seccion 3. No encontre recibos que los cierren (UNKNOWN: revision no exhaustiva).
- **Roturas en OpenWrt a arreglar** (CONFIRMED, docs/STAGE1257A seccion 6-7): 4 scripts de campeon con hash_mismatch y stubs retirados (commit e9acac6); SHA256SUMS de LTU con dos hashes distintos; fmx_wds_churn_healer.sh ausente (kit v23 PtMP); ubnt_spectral.ko no esta en firmware/ de openMAX (solo en artifacts/firmware_re_xw_m5/; 1257A no lo cita). Ademas, el runner PBE5AC es modelo y no banco (seccion 3).
- **Quien trabaja**: orchestration/master_orchestrator_state.json lista dueños: D4 lane_2 y lane_4; D5 lane_4; D8 lane_2 y lane_3. El archivo no tiene estado vivo. Segun la memoria del operador (31/10) no se asignan tareas nuevas a lanes Codex. Estado actual: UNKNOWN.
- **Autoresearch**: hay corridas reales (LAP-120 24/10, 8 iteraciones; ABBA16 r100-r107 24/10) con guardas legacy. Ninguna cumple el contrato A/A vigente. El harness (D8) esta listo y sin corrida nueva.

## 1. Prior work: lo que ya cerraron otros

| Fuente | Lo que ya establecio |
| :-- | :-- |
| artifacts/knob_index/knob_index.json | 998 entradas; 342 probadas; 656 sin probar. Por familia sin probar: airos 339, ltu 9, ptmp 164, ptp 144 |
| docs/STAGE3087A (30/10) | 8 filas: coverage_class NO_GO (W376 aborto por memoria; W384 -2.78 %), aql_txq_limit NO_GO, set_rate_override CRASH, htt NO_GO, campeon v2 NO_GO. Pendiente: si el builder corre sin merge, se pierden filas |
| docs/STAGE1257A | Catalogo de valores tuneados: PtP v4/v7, airOS v9, PtMP v23, LTU v20; descartes por ronda; huecos de sha256 |
| orchestration/autoresearch/PROGRAM.md | Campeones PtMP v19 (aql_threshold 4000, tcp_limit 64 KB) y PtP v18/LED v4. Regla de A/A por corrida (1.3). Sin tope global de rondas (1.3) |
| orchestration/thresholds.json L01-L04 | Todos DERIVE_SAME_RUN_SAME_DEVICE_AA: los valores legacy (perdida 2 %, p99 150 ms, RTT +20 %) no son guardas validas |
| harness + empirical_aa_policy.py | Guardas derivadas de la A/A de la misma corrida (seccion 5) |
| docs/STAGE12 (R57-R65, lower-MAC) | Bundles ABBA16 sin promover; Holm amplio no acepta ninguno |

## 2. Inventario sin probar en el stack actual

Conteos (CONFIRMED: artifacts/autoresearch/stage3135a_knob_priorities.json, seccion counts):

- Filas sin probar: 656 = airOS 339 (solo airOS) + LTU 9 (solo LTU) + OpenWrt 308 (PtMP 164, PtP 144).
- Las 308 filas OpenWrt por superficie: 174 WMI internos de ath10k (sin superficie de usuario); 39 ath10k-ct debugfs y ct_special; 36 sysctl, sysfs y qdisc; 23 mac80211, aqm e iw; 18 uci (config, no RF); 6 policy codel/cake (no runtime); 6 regulatorio (excluido por politica); 6 umac (airOS).
- Nombres canonicos tras dedupe de aliases entre roles: 158 en OpenWrt. Pool con superficie alcanzable: 55. Menos 2 aliases de knobs ya probados en ambos roles (coverage_class, aql_txq_limit_per_ac) y menos set_rate_override (CRASH) = **52**. De esos, 10 ya se ejecutaron el 24/10 con verdicto legacy y 42 no se ejecutaron.
- Clasificacion: airOS-only = familia airos (ioctl WEXT y sysctl airOS; 339 knobs en el catalogo). LTU-only = sysfs ame_ctrl_dev (9): adj_mcs, adj_mimo, adj_mix_mcs, autoMcs4096, ldpc_iteration, cpe_mcs, ofdma_en, ofdma_subband0_hdrIdx, ofdma_subbands.

## 3. Discrepancias (indice frente a recibos)

1. **El indice marca como sin probar knobs que ya se variaron en vivo.** Los 190 receipts LAP-120 del 24/10 variaron rc_max_per_thr, aql_threshold, fq_quantum, rts_threshold, tcp_notsent_lowat, tcp_limit_output_bytes y ani_enable. Recuento del revisor (clave de nivel superior con alias, contra la iteracion 0 de cada corrida): rc 47, aql 52, fq 34, tcp_notsent 13, tcp_limit 13, rts 7, ani 1 (CONFIRMED en artifacts/autoresearch/lap120*json). El JSON del autor cuenta 63, 68 y 49 filas en 14, 14 y 13 recibos, y 4 y 1 para rifs y pshack: no conciliado (UNKNOWN). El indice no las incorpora.
2. **Esos verdictos son legacy.** El objective_config del receipt usa min_repetitions 2, rtt_budget 20 ms y target 80 Mbps: son los valores legacy que thresholds.json L03 marca como no validos (CONFIRMED). La actualizacion del incumbente es secuencial, no A/A. No son KEEP validos.
3. **ABBA16 r100-r107 (24/10)** no tienen filas en el indice: cero coincidencias de abba16, rc24 o ftx en knob_index.json. Son bundles, y STAGE12 dice que el brazo B no aisla AF, FQ ni asimetria (CONFIRMED: docs/STAGE12_LOWER_MAC_HOOKS_AND_12BLOCK_CROSSOVER_AUDIT.md).
4. **El runner PBE5AC es modelo.** orchestration/autoresearch/fmx_pbe5ac_deep_autoresearch_runner.py: `_window_metrics` usa bonos fijos y jitter de +-0.04; no tiene llamadas a iperf, ssh, socket ni subprocess (CONFIRMED). No es evidencia de banco (PROGRAM 1.1).
5. **Module params de umac mal clasificados.** host_80211_enable, max_peers y vow_config estan bajo familias OpenWrt, pero el catalogo los liga a xc_8_7_25 y wa_8_7_25 (CONFIRMED). Se tratan como airOS-only. La prueba KEPT stage84a host_80211_enable en PtMP requiere revision.
6. **Produccion no uniforme** (lecturas 29-30/10, campo produccion del indice): aql_threshold PtMP 24000 en 9 de 15, 5000 en 4 y 4000 en 2; PtP 4000 en 2 de 2 (ptp_colo AP y STA) frente al 24000 del champion PtP v7 (214A); tcp_notsent_lowat 4294967295 en 12 de 16 y 8192 en 4; bql_limit_max stock 1879048192 en 10 de 16. PROGRAM D1 declara 4000 para PtMP. Discrepancia para el operador; no se cambio nada.
7. **Veredicto sin motivo.** PtMP netdev_budget_usecs 8000 (m33b) quedo DESCARTADO con +14.37 % de goodput y detalle null.
8. **Atribucion confundida en PtP.** tx_queue_len 135A-R6 (+9.82 %) va combinado con netdev_budget_usecs (4000 vs 6000).
9. **Direcciones de banco y produccion.** El Loco de banco es 198.18.0.67 (D4 en orchestration/master_orchestrator_state.json; runner LAP-120). Produccion Guarida usa 10.10.x.y (D3). Los nombres cpe_200_41, cpe_200_223 y cpe_200_80 del indice coinciden con 198.18.0.14, .223 y .80 de D3 (INFERRED por nombre). Quedan UNKNOWN la IP del AP (el runner usa 198.18.0.81; D4 lista el LAP en 198.18.0.43) y el .250 o .117 que citan PROGRAM y la nota W457.

## 4. Top 15 (orden: impacto esperado x consistencia del prior x alcanzabilidad)

Impacto y confianza son INFERRED. No hay umbrales numericos nuevos.

| # | Perilla | Rol | Mecanismo | Prior (fuente) | Estado | Impacto / confianza |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| 1 | rc_max_per_thr (ct_special id 7, 50 a 28) | PtMP | Umbral PER de tasa en firmware: menos reintentos | iter6 LAP-120: p95 -20.5 %, goodput -5.4 % (legacy). Bundle RC24 r100-r107 (artifacts/autoresearch/lap120_loco195_r100..r107_*_results.tsv, recalculado): p95 -57,0 a -90,5 %, goodput -1,7 a +2,4 % | Ejecutado 24/10 (legacy); 0 crash (no recontado; 63 en el JSON del autor, 47 en el recuento del revisor) | ALTO p95 / MEDIA |
| 2 | pktlog (modulo y pktlog_filter) | PtP/PtMP | CPU de captura en el host | airOS XC +23.35 % al descargar ath_pktlog (S93B; STAGE1257A seccion 4). Otra plataforma | Sin probar; presencia UNKNOWN | ALTO si esta cargado / BAJA |
| 3 | aql_threshold | PtMP | Tope de tiempo de aire agregado: bufferbloat | PtMP champion 4000. PtP KEPT -0.77 % y -2.98 %; DESCARTADO -3.88 %. Produccion 24000 en 9 de 15 | Ejecutado 24/10 (legacy, 68 filas) | MEDIO-ALTO p95 / MEDIA-BAJA (signo por rol) |
| 4 | tcp_notsent_lowat | PtMP | Limita la cola de escritura del socket | PtMP champion 8192 (m22b). PtP KEPT +4.09 % (16384 a 8192); PtP champion 8192 a 4294967295. Produccion 8192 en 4 de 16 | Ejecutado 24/10 (legacy) | MEDIO p95 / MEDIA-BAJA |
| 5 | tcp_limit_output_bytes | PtMP | TSQ: bytes por socket en qdisc | PtMP champion 64 KB. PtP KEPT 65536 +4.99 % (140A) y -0.77 % (145A) | Ejecutado 24/10 (legacy) | MEDIO p95 / MEDIA-BAJA |
| 6 | vht_mcs_mask | PtP/PtMP | Quita MCS altos: menos intentos caros | Sin medicion en OpenWrt. Estratos de distancia en r100-r107 (3 a 14 km) | Sin probar | ALTO en enlace marginal, negativo a alto SNR / BAJA |
| 7 | tx_queue_len | PtMP | Backlog antes de FQ | PtP 135A +9.82 % confundido. PtP champion 256 a 1000 | Sin probar | MEDIO p95 / BAJA |
| 8 | bql_limit_max, bql_hold_time | PtMP | BQL en eth0 (egreso cableado) | PtMP champion hold 800 +6.54 %, max 42392 +6.61 %; m28b -10.27 % | Sin probar | BAJO-MEDIO / BAJA (mecanismo sin verificar) |
| 9 | ani_enable | PtP/PtMP | Inmunidad al ruido: sensibilidad RX | Produccion 1 en 15 de 15 PtMP y 2 de 2 PtP | 1 fila 24/10 | INCIERTO / BAJA |
| 10 | udp_rmem_min, udp_wmem_min | PtP/PtMP | Memoria minima UDP: perdida de IPTV/VoIP | LTU 299A p99 -39.63 % (bundle; STAGE1257A seccion 5) | Sin probar | MEDIO estabilidad / BAJA |
| 11 | spectral_scan_ctl | PtP/PtMP | El escaneo espectral consume PHY | Analogo PB-021 1 Hz: -4.99 % (DESCARTADO) | Estado UNKNOWN | BAJO-MEDIO si activo / BAJA |
| 12 | fq_quantum (aqm) | PtMP | Quantum DRR por flujo | 24/10: 21 keep y 28 discard (legacy). PtP mezclado | Ejecutado 24/10 | BAJO-MEDIO / MEDIA-BAJA |
| 13 | netdev_budget_usecs | PtMP | Tiempo de poll NAPI | m33b +14.37 % DESCARTADO sin motivo; m32a -3.76 % | Sin probar | BAJO-MEDIO / BAJA |
| 14 | dev_weight | PtMP | Peso NAPI por poll | PtP champion +4.85 %; PtMP m29b +3.49 % | Sin probar | BAJO / MEDIA-BAJA |
| 15 | tcp_reordering | PtP/PtMP | Umbral de duplicados ACK | Sin prior | Sin probar | BAJO, exploratorio / BAJA |

Fuera del top 15 (motivos en el JSON, seccion excluded_groups): set_rate_override (CRASH en W394); set_rates (misma familia de firmware, sin cota de riesgo); 174 WMI internos; ct_special marcados excluded en el catalogo (THRESH62, NOISE_FLR, MAX_TXPOWER, PDEV_XRETRY, WMI_WD, CSI); tx_power (regulatorio); codel y cake (no runtime); uci dhcp y firewall; oom_score_adj (ya es guarda del runner, linea 265); 339 airOS; 9 LTU; coverage_class y aql_txq_limit (ya probados en ambos roles).

## 5. Protocolo para el top 5 (A1 a B1 a A2 a B2)

**Restriccion del harness (CONFIRMED).** `validate_observation` (orchestration/autoresearch/empirical_aa_policy.py:124-130) rechaza un candidato que empiece antes de que termine la ultima ventana A/A. Por eso el orden A1-B1-A2-B2 no entra directo en `compute_fmx_objective`. Solucion: un bloque A/A previo (AA1 y AA2, mismo config A) define la banda; despues se corren A1, B1, A2 y B2. Cada ventana B se evalua con una llamada directa a compute_fmx_objective(obs, config, best_fmx_loss = mediana de fmx_loss de A1 y A2), no con run_iteration, porque run_iteration mueve el incumbente y B2 no podria superar a B1 (harness:540). El registro nativo record_native_counterbalanced_block (harness:461) no sirve: el puente declara solo bloques CPU, sin goodput ni RTT (tools/observability/stage2713a_harness_sqlite_bridge.py:1).

**Comun a los 5 protocolos:**

- **Prerrequisitos.** W457 libera LAP .20, Loco 198.18.0.67 y PBE .241/.242. AAContext fijado con SHA256 de dispositivo, UUID de arranque, workload_sha256 y fixed_config_sha256 (empirical_aa_policy.py:35-60).
- **Carrier (dato existente).** P1 y P3 estan en el runner LAP-120: ct_rc_per_thresh (linea 53; escritura en lineas 72-73) y aql_threshold_us (escritura en apply_knob_state). P4 y P5 solo aparecen en los runners de bundle r100-r105 (tcp_notsent_lowat) y r100-r103 (tcp_limit_output_bytes): hace falta un perfil de una sola variable en el runner, sin cambio de harness. P2 no tiene carrier. P1 puede correr en el par PBE .241/.242 solo si su firmware expone ct_special (UNKNOWN en PBE).
- **Ventanas.** Ruta de ejecucion del runner: `run_loaded_probe(repetitions=2, duration_sec=4)` (tools/bench/run_live_autoresearch_lap120_loco195.py:429), con iperf3 -P 2 y ping. Es corta. Si la banda A/A es mas ancha que el efecto, el resultado es no concluyente. No se fija duracion nueva.
- **Metricas por ventana.** goodput_rx_mbps; p50, p95 y p99 RTT; packet_loss_pct; jain_fairness; retry_rate; station_drops; oom_events; link_alive; restoration_verified; repetitions; started_s y ended_s.
- **Guardas (todas de la A/A de la misma corrida).** Goodput >= minimo AA (harness:281-292). p95 <= maximo AA (harness:281-292). p99 <= maximo AA (harness:308). Perdida <= maximo AA (harness:296). Repeticiones >= las de AA (harness:269). Mejora de fmx_loss > ruido del score AA (harness:330). restoration True, station_drops 0, oom_events 0 y link_alive True (empirical_aa_policy.py:115-117).
- **Abort.** restoration falso o station_drops > 0 da CRASH (harness:245-253). Enlace caido en cualquier ventana da CRASH y rollback inmediato. Fuera de banda da DISCARD.
- **Rollback.** Antes de la primera escritura, armar un watchdog HUP-immune (patron del runner, lineas 262-283, 300 s) que restaure el valor LEIDO al inicio, no una constante. Al final restaurar y verificar readback; si no coincide, CRASH.
- **Regla de decision.** KEEP solo si compute_fmx_objective, llamado directo por cada ventana B con best_fmx_loss = fmx_loss mediano de A, da KEEP en B1 y en B2, y la mediana de B mejora sobre A por mas que el ruido AA (harness:330). Una sola variable por corrida.
- **Parada.** Sin tope de rondas (PROGRAM 1.3). Parar al decidir o ante un evento de seguridad.
- **Riesgo.** El watchdog de 300 s no evita una caida de firmware al activar (W394: caida 0.33 s despues). La recuperacion es reiniciar el radio de banco.

| # | Perilla | Brazo A | Brazo B | Ruta o comando | Banco |
| :-- | :-- | :-- | :-- | :-- | :-- |
| P1 | rc_max_per_thr | 50 (leido) | 28 | ct_special con escritura decimal de (7 << 32) + valor (runner linea 72). Restaurar 50 = 30064771122 | LAP-120 + Loco |
| P2 | pktlog_filter | Valor leido (si es 0, P2 queda anulado) | 0 | GATE: leer /sys/kernel/debug/ieee80211/phy0/ath10k/pktlog_filter (superficie OpenWrt del indice). Sin carrier: habria que escribirlo | PtMP o PtP |
| P3 | aql_threshold | 24000 (leido) | 4000 | /sys/kernel/debug/ieee80211/phy0/aql_threshold (runner linea 279). Fijar AQL por AC en su valor leido | LAP-120 + Loco |
| P4 | tcp_notsent_lowat | 4294967295 (leido) | 8192 | sysctl en el AP emisor | LAP-120 + Loco |
| P5 | tcp_limit_output_bytes | Valor leido | 65536 | sysctl en el AP emisor | LAP-120 + Loco |

Orden de ejecucion: P1, P3, P4 y P5, una por corrida; al final P2, solo si el gate lee un valor distinto de 0. El orden difiere del ranking porque P2 depende de un gate y no tiene carrier.

## 6. Lo que no hice y riesgos

- No consulte MemoryMaster (MCP no conectado en esta sesion). No lei el estado vivo de los nodos: el helper wave449 exige espera de telemetria y mutex SSH, y no se justifico para una priorizacion offline. La existencia de cada perilla en OpenWrt queda INFERRED, salvo las lecturas de produccion ya guardadas en el indice.
- Riesgo principal: los priors de rc_max_per_thr y tcp_notsent_lowat vienen de guardas legacy o de bundles. Hasta correr P1 a P5 con A/A, no son decision.
- No verifique ct_special ni pktlog en PBE: el par PBE sigue UNKNOWN para P1 y P2.

## 7. Anexo: los 52 nombres del pool de trabajo

Excluidos del pool: coverage_class y aql_txq_limit_per_ac (ya probados en ambos roles) y set_rate_override (CRASH).

Ejecutados el 24/10 con verdicto legacy (10):
- Ambos roles (8): ani_enable, aql_threshold, fq_quantum, distance_m, rts_threshold, pshack, rc_max_per_thr, rifs_enable.
- Solo PtMP (2): tcp_limit_output_bytes, tcp_notsent_lowat.

Sin ejecutar (42):
- Ambos roles (26): a_msdu_subframes_nl80211, ack_timeout_derived_from_coverage_class, bql_limit_max, bw_disable_mask, csi, ibss_amsdu_ok, fq_flow_limit, netdev_tstamp_prequeue, noise_flr_thresh, oom_score_adj, pdev_xretry_th, pktlog_filter, qdisc_fq_codel, rx_all_mgt, set_rates, spectral_scan_ctl, tcp_moderate_rcvbuf, tcp_no_metrics_save, tcp_reordering, thresh62_ext, txbf_cv_msg, txbw_mask, udp_rmem_min, udp_wmem_min, vht_mcs_mask, wmi_wd.
- Solo PtMP (16): bql_hold_time, bql_limit_min, dev_weight, fq_memory_limit, gro_normal_batch, netdev_budget, netdev_budget_usecs, tcp_autocorking, tcp_early_retrans, tcp_mtu_probing, tcp_pacing_ca_ratio, tcp_pacing_ss_ratio, tcp_recovery, tcp_slow_start_after_idle, tcp_thin_linear_timeouts, tx_queue_len.

Notas:
- Ningun nombre del pool esta sin probar solo en PtP: todos estan sin probar en PtMP.
- Varios nombres estan marcados excluded o characterization_only en el catalogo (thresh62_ext, csi, bw_disable_mask, txbw_mask, rx_all_mgt, txbf_cv_msg, pdev_xretry_th, noise_flr_thresh, ibss_amsdu_ok, wmi_wd, set_rates); por eso no entran al top 15.
- ack_timeout y distance_m se variaron por corrida (cobertura), no por iteracion: su estado 24/10 es de corrida.
