<!-- doc-head: Catalogo de los valores tuneados por autoresearch en PtP OpenWrt (v7), PtP airOS (v9), PtMP (v23) y LTU (v20) segun los recibos, con conteos reales vs el brief, kits con sha256 y huecos. -->

# Stage 1257A - Catalogo completo de valores tuneados (PtP / PtMP / LTU)

Fuente unica de datos: `artifacts/verification/stage1256a_complete_tuned_knobs_production_ledger.json` (548 entradas de knob,
32 artefactos con sha256), generado por `tools/research/export_stage1256a_complete_tuned_knobs_production_ledger.py`
(solo lectura local, byte-estable salvo `generated_at`). Este doc muestra los conjuntos campeones completos y los descartes
mas relevantes; el detalle por ventana/ronda/knob esta solo en el JSON.

Alcance y limites: es un registro de lo que los recibos DICEN, no mediciones nuevas, ni aceptacion fisica, ni `PRODUCTION_READY`.
`evidence_class` se copia de las auditorias del repo (Stage 887A / 1003A), no se infiere: `CONFIRMED_LIVE_BENCH` es un triage heuristico,
no una ficha de procedencia por campeon; `CONFIRMED_LIVE_HARDWARE` exige `controlled_aa_valid` (CURRENT_STATE, Stage 1028A).
Deltas: copiados del recibo o derivados de valores de brazo registrados (`basis` lo indica). Cuando un delta aplica a un grupo de
knobs aplicados juntos se marca `scope=round_bundle` (no hay atribucion por knob).

## 1. Discrepancias vs lo recordado en el brief (conteos reales)

| Campania | Brief | Recibos (reales) | Nota |
| :-- | :-- | :-- | :-- |
| PtP OpenWrt "v7" | 100 ventanas, R1..R18 + E2E-R1, campeon v7 | 163A = 18 rondas / 76 ventanas (R1..R18 + E2E-R1, campeon v2); 214A = 24 rondas / 100 ventanas (campeon v4); 385A = 42 rondas / 172 ventanas (campeon v7) | El brief mezcla 3 hitos. Kit v7 (Stage 306A, 16 imagenes SquashFS) hornea el campeon **v4**; el campeon llamado v7 es 385A. INFERRED: campania = linaje WA/OpenWrt (cadena v2..v13 en el JSON) |
| PtP airOS "v9" | 9 stages S60A..S94A | 15 recibos con rondas en S60A..S94A (+ S95B) = 31 rondas, 124 ventanas | Campeon v9 = S94A-R1 (KEEP) y S95B-R1 (verificacion bajo carga): v9 queda en el borde/fuera del rango del brief |
| PtMP "v23" | 23 stages, kit v23 | 35 recibos con rondas de mecanismo, 102 rondas, 32 rondas promovidas (25 `PROMOTE_NEW_CHAMPION` + 7 `KEEP_NEW_CHAMPION`, estas ultimas en stages 21/24C/24E/25), 70 `RETAIN_CURRENT_CHAMPION` | Auto-descubiertos (control_arm_a + treatment_arm_b + decision); incluye 2.4 GHz (27) y bancos MikroTik VLAN107 (97A, 99A, 102D, 103D); 51A aparece 2 veces. Kit v23 = Stage 101A |
| LTU "v20" | 276 ventanas + Stage 50B | 22 campanias / 66 rondas A/B / **264** ventanas (recibo 764A lo confirma); 50B = 3 perfiles x 3 trials = 9 | 276 = Ronda 23 **planificada**: existe `tools/bench/run_stage793a_live_ltu110_round23_276window_autoresearch.py` y el kit `fmx_ltu_v21_276window_field_kit.sh`, pero NO hay recibo `stage793a*` (UNKNOWN: nunca se ejecuto en este arbol) |

## 2. PtP OpenWrt (`ptp_openwrt_v7`): 103 entradas (61 knobs campeon + 42 variantes de ronda: 23 promovidas, 19 descartadas)

Evidencia: receipts `stage163a/214a/385a_cumulative_*wa_champion_v*.json` (clase de evidencia del JSON, Stage 1003A: 163A `CONFIRMED_LIVE_HARDWARE`; 214A y 385A `PENDING_LIVE_RETEST`).
Delta del perfil completo (385A, E2E-R3 MK1-251, `scope=whole_champion_profile_E2E`): goodput 43.966 -> 54.623 Mbps (+24.239%),
p50 67.216 -> 15.006 ms (-77.675%), Pareto +202.15%, decision `PROMOTE_ARM_B` (n de ventanas del E2E: no registrado).

**Campeon v7 (Stage 385A, 16 knobs; antes = valor en 315A/v6):**

| Knob | Antes (v6) | Despues (v7) | Interfaz (registrada) |
| :-- | :-- | :-- | :-- |
| tcp_slow_start_after_idle | 1 | 0 | sysctl `net.ipv4` via script `99-fmx-wa-universal-champion` |
| tcp_mtu_probing | 0 | 1 | idem |
| tcp_thin_linear_timeouts | 0 | 1 | idem |
| tcp_autocorking | no registrado | 0 | idem |
| htt_max_amsdu / htt_max_ampdu | no registrado | 2 / 64 | ath10k htt |
| rts_threshold | no registrado | off | mac80211 |
| gro_normal_batch / gro_flush_timeout_ns | 16 / 20000 | 16 / 20000 | sin cambio |
| fq_limit / tcp_early_retrans / tcp_streams | 512 / 4 / 2 | 512 / 4 / 2 | sin cambio |
| enable_nft_wmm_qos / gaming_udp_probe / traffic_mode | 1 / 0 / bidir | 1 / 0 / bidir | sin cambio |
| profile_mode | universal_wa_champion_v6_36round_148window | r42_universal_wa_champion_v7_42round_172window | etiqueta |

**Campeon v4 (214A, 45 knobs; el que hornea el kit v7). Cambios vs v3 (169A) -> v4:** ap_fq_quantum 3028->300, cpe_fq_quantum 1514->300,
fq_initial_quantum 3028->15140, fq_limit 1024->512, fq_memory_limit 3145728->4194304, aql_threshold 4000->24000, aql_bk 500/1000->5000/12000,
aql_vi 1000/2000->5000/12000, aql_vo 300/600->5000/12000, bql_min 4542->0, bql_max 36288->65536, bql_hold 600->1000, dev_weight 48->64,
netdev_budget 480->300, netdev_budget_usecs 6000->2000, netdev_max_backlog 1500->1000, tcp_limit_output_bytes 65536->262144,
tcp_notsent_lowat 8192->4294967295, tcp_pacing_ca/ss 110/150->120/200, tx_bias 2->1, tx_queue_len 256->1000, packet_steering 1->0,
flow_offloading 1->0, distance_m 300->1000, tcp_early_retrans (sin valor v3)->4, tcp_recovery (sin valor v3)->1. Los 45 valores completos, con sus
punteros JSON (`/promoted_wa_champion_v4_knobs/*`), estan en el JSON.

**Descartes registrados (`RETAIN_ARM_A`, 19 de 42; delta de objetivo A->B segun el recibo):** S139A-R9 -5.80%, S140A-R11 +5.49%, S140A-R12 +9.83%,
S145A-R13 +3.75%, S145A-R15 -18.49%, S161A-R18 -6.83%, S167A-R20 -3.88%, S167A-R21 -4.47%, S123A-R3 -1.70%, S212A-R22 +1.11%, S212A-R24 -9.66%,
S275A-R27 -1.58%, S276A-R29 -7.98%, S311A-R32 +1.89%, S311A-R33 -3.53%, S312A-R34 +2.89%, S312A-R35 -16.24%, S381A-R39 -6.08%, S382A-R40 -4.99%
(los % son el goodput A->B derivado de los promedios de brazo registrados; el criterio de decision del recibo es el score Pareto y varias rondas
`PROMOTE_ARM_B` tienen menor goodput, p.ej. S135A-R4: 55.574 -> 54.107 Mbps). Antes/despues de cada variante solo existen en el titulo (prosa): hueco.

## 3. PtP airOS (`ptp_airos_v9`): 198 entradas (31 rondas; 8 CHAMPION, 7 KEPT, 14 DISCARDED, 2 UNCLASSIFIED)

Evidencia: 16 recibos `stage60a..stage95b_pbe5ac_*`; valores desde `candidate_commands`; "antes" = stock registrado (hardware_audit de 70B y ledger
curado 80C/86B/100B) con match por nombre de clave (no por comando; la nota de cada entrada cita el puntero). Ventanas: 4 por ronda (A1/B1/A2/B2), 124 en total.

| Stage-Ronda | Verdicto (raw) | Goodput A -> B (Mbps, %) | Knobs principales (antes -> despues) |
| :-- | :-- | :-- | :-- |
| 60A-R1/R2/R3 | R3 CHAMPION (`promoted_champion_round`); R1/R2 UNCLASSIFIED | no registrado (solo ventanas) | rps_cpus, cwmin/cwmax, ampdu, acktimeout (solo en prosa) |
| 62A-R2 | KEPT (keep) | 20.328 -> 25.615 (+26.01%) | set_multiq 0->1, aggr_swretry=6, nonaggr_swretry=8, enable_tx_tcp_cksum 0->1, netdev_budget=800 (regex de prosa) |
| 62A-R1/R3 | DISCARDED | 25.352 -> 21.837 (-13.86%); 21.26 -> 15.507 (-27.06%) | IRQ33/spectral (prosa) |
| 68A-R1 / R2 (v5) / R3 | KEPT / CHAMPION / DISCARDED | +41.81% / +14.32% / -2.43% | R2: DMA/NAPI dev_weight=64 (campeon v5); R3 combinado descartado |
| 70B-R1 | DISCARDED | 20.411 -> 18.181 (-10.93%); p95 +33.47% | protmode 1->0, ACBEMinfree 32->8, ACBKMinfree 48->16, ACVIMinfree 16->8, CABMinfree 48->16, uapsd 0, burst 1, burst_dur 2000 |
| 70B-R2 | DISCARDED | 19.693 -> 18.794 (-4.57%) | timing 2, voip_bias 0->6, cms_bias 0->6, daprot 1->2, tx_queue_len 256 |
| 72B-R1 / R2 | KEEP / KEEP | -13.54% / +6.27% | ptp_xmit, daprot=2 (R1 KEEP con goodput negativo: criterio fmx_loss) |
| 73A-R1 (v6) / R2 | KEEP / DISCARD | -5.79% / +12.26% (p95 +139%) | ptp_xmit 0->1, daprot 1->2, ff_mcast_airtime_limit |
| 74A-R1/R2, 77B-R1/R2 | todas DISCARD | -27.57, -21.80, -2.78, +1.63% | ATPC/UPH bug-05, fast turnaround |
| 79A-R1 (v7) | CHAMPION (KEEP) | 20.191 -> 21.268 (+5.33%; p95 -29.76%) | set_multiq 0->3, timing '200 200 5000', ptp_xmit 0->1, daprot 1->2, ff_mcast_airtime_limit 0->5 |
| 79A-R2, 80B-R1, 80B-R2 | DISCARD | +1.14%, -10.93%, -3.37% | 80B: CABlevel 15, tcp_notsent_lowat 16384, timing '200 200 4500' (fine-grid descartado) |
| 84A-R1 | KEPT | -4.64% (p95 -46.37%) | rejoin 5200 MHz |
| 86A-R1 / R2 (v8) | DISCARD / CHAMPION | -1.26% / +4.54% | R2: netdev_budget=800, tcp_low_latency=1, ACVO/VI/BE/BK Minfree 0/16/32/48 |
| 87A-R1/R2, 92A-R1 | KEEP | +3.07%, +5.41%, -16.21% | CabqMaxdur 15, tx_cksum; doth/CSA 3-int (92A: outage -100%) |
| **94A-R1 (v9)** | CHAMPION (KEEP) | 8.945 -> 12.613 (+41.01%; p95 -64.8%) | rmmod ath_pktlog, vow_extstats 1->0, doth 1, vap_doth 1, doth_chanswitch '5200 5200 10', enable_tx_tcp_cksum 0->1, set_CabqMaxdur 100->15, set_multiq 0->3 |
| **95B-R1 (v9)** | CHAMPION (raw `VERIFIED_CSA_AND_VLAN_UNDER_LOAD`) | 14.849 -> 13.786 (-7.16%; p95 +190.27%) | mismo set v9 + VLAN 112/113 + CSA 5200/5205 bajo carga |

Ledger curado (80C/86B/100B, 20 entradas en esta campania): p.ej. `set_multiq` 0->3 KEEP, `enable_tx_tcp_cksum` 0->1 KEEP, `ac_minfree_and_protmode`
DISCARD, `uph_wifi0_timing_and_daprot` DISCARD (timing=2 PtP), `ath_pktlog_module_unload` KEEP (S93B/94A), `vow_extstats` 1->0 KEEP. Texto de evidencia completo en el JSON.

## 4. PtMP (`ptmp_v23`): 122 entradas (102 rondas + 20 del ledger curado)

Antes/despues = descripcion de brazo control/tratamiento del recibo (prosa; los valores numericos viven dentro del texto). 4 ventanas por ronda (408 contadas).
Rondas promovidas a campeon (goodput brazo A -> B Mbps, delta registrado; ademas, `KEEP_NEW_CHAMPION` en 21-R2 -0.35%, 21-R3 -0.94%, 24C-R1 -2.56%, 24C-R2 +11.19%, 24E-R1 +21.87%, 24E-R2 +5.24%, 25-R2 +3.66%): 27-R1 27.062->28.470 (+5.20%); 27-R2 +1.50%; 28-R1 +0.59%; 31A-R1 -0.01%; 34A M15 +7.24%;
35A M15_5GHz +1.71%; 36A M16b IPTV AC_VI +2.51%; 37A M17b fq_limit/quantum VO AQL +2.65%; 39A M19c/M20c fast-leave +5.86%; 41A M22b/M23b +1.46%; 42A M24e/M25e txq 256 +3.21%;
44A M26b br0 txq 256 +7.14%; 46A M29b dev_weight tx_bias 2 @ budget 600 +3.49%; 51A M30c BQL limit_max 42392 hold 1000 +6.61% (dos recibos); 52A M33a budget_usecs 6000 + BQL min 4542 +7.02%;
55A M34b BQL hold 800 +6.54% (v19); 72A M41d XC multiq 1 + cksum 1 (v20) +7.89%; 81C M44c XC multiq 1 + Minfree + XW txq 64 (v21) +2.44%; 93B M46a `rmmod ath_pktlog` en XC
46.526 -> 57.391 (+23.35%; v22); 95C M47 chanbw 20/40 +1.63%; 97A M48 VLAN107 PCP/DSCP -0.98%; **101A M50 (kit v23) 47.636 -> 46.996 (-1.344%)**;
102D M51 CSA 5180/5200 +8.85%; 103D M52 DiffServ4 +6.16%.

Kit v23 (S101A-R1, `fmx_wds_churn_healer.sh`): goodput -1.344%, p95 sector 42.988 -> 33.486 ms (-22.104%), survivor p95 20.218 -> 6.892 ms (-65.91%), auto-heal 2500 -> 1111 ms (-55.56%),
VoIP jitter -55.08%, pero IPTV jitter 1.807 -> 20.024 ms (+1008%) y bitrate IPTV 4.945 -> 3.315 Mbps; decision `PROMOTE_NEW_CHAMPION` (Pareto +6.39%).

Descartes (`RETAIN_CURRENT_CHAMPION`, 70 rondas), los peores por goodput: 44A-R4 -34.14%, 25-R1 -27.31%, 51A-R5 -21.17%, 34A-R3 -10.43%, 46A-R5 -10.27%, 72A-COUPLED -10.27%,
42A-R1 -8.35%, 28-R2 -7.79%, 34A-R2 -6.69%, 36A-R1 -6.23%. Lista completa en el JSON.

## 5. LTU (`ltu_v20`): 125 entradas (116 knobs de 22 campanias A/B, 2 perfiles OTA 50B, 4 del ledger curado, 3 bundles sin valores)

Metrica: por ventana se registra una latencia (p99 en 185A..299A; media `rtt_avg_ms` en 329A..761A; 329A la llama `loopback_Burst_rtt_avg_ms`). NO hay throughput RF.
Los knobs de cada campania se aplican juntos: el delta es del bundle. Verdicto = arm `champion_b` del recibo (todos KEPT); rondas 7..10 no muestran ganancia (0.22->0.22 etc.).

| Stage (ronda) | Knobs antes -> despues | Latencia A -> B (%) |
| :-- | :-- | :-- |
| 185A (1) | ath0/eth0 rps+xps_cpus 0->2/1; dev_weight 64->48; netdev_budget 300->480; netdev_max_backlog 1000->2500; eth0 bql_limit_max 1879048192->36288; tcp_limit_output_bytes 131072->65536; tcp_notsent_lowat -1->16384; vm_min_free 1414->4096 | p99 R1 -18.46%, R2 +7.49%, R3 -1.39% |
| 188A (2) | somaxconn 128->512; rmem/wmem_max 262144->524288; optmem_max 10240->65536; tx_queue_len 1000->256 | p99 -24.97%, -13.45%, -14.75% |
| 218A (3) | head-to-head stock vs safe champion (mismos 8 knobs) | p99 -24.49%, -5.37%, +19.81% (R3 peor, igual KEPT) |
| 247A (4) | tcp_dsack 0->1; br0 ageing 15000->30000; multicast_snooping 1->0; nf_conntrack_max 4096->16384 | p99 -5.77%, -5.52%; R3 (fq_codel eth0/ath0, sin valores estructurados) +46.53% |
| 287A (5) | rmem/wmem_default 163840->262144; netdev_max_backlog 1000->3000; tcp_tw_reuse 0->1 | p99 -16.58%, +10.63% |
| 299A (6) | udp_rmem/wmem_min 4096->16384; ip_local_port_range 32768-61000 -> 10240-65535; ping_group_range | p99 -39.63%, -14.90% |
| 329A..397A (7-10) | conntrack liberal 0->1, rps_cpus 2, netdev_budget 300->480, tcp_fastopen 0->3, tcp_ecn 0->2, early_retrans 2->3, sched_rt_runtime 950000->980000, autocorking 1->0, dirty_ratio 10 | 0.22->0.22, 0.22->0.22, 0.21->0.21, 0.21->0.21 (0%) |
| 439A (9) .. 761A (22) | tcp_notsent_lowat ->12288, thin_dupack/linear_timeouts 0->1, busy_poll/read 50->0 (variante candidata 50 descartada), tcp_reordering 3->6, tcp_mtu_probing 0->1, slow_start_after_idle 1->0, pacing_ca/ss 120/200->110/160, netdev_budget_usecs 2000->4000, tcp_recovery 0->1, optmem_max 10240->65536, tcp_limit_output 262144->131072, max_backlog 1000->2048, no_metrics_save 0->1, dev_weight 64->48, budget 300->480 | 0.238->0.205 (-13.87%) ... 0.231->0.184 (-20.35%) en 761A (campeon v20) |

**Campeon v20 (Stage 764A, 22 campanias, 66 rondas, 264 ventanas):** netdev_budget 480, dev_weight 48, 0 daemons DHCP rogue, IRQ 52 fija en CPU1 (smp_affinity=2), watchdog 45 s, 0 toques a `/dev/ame*`.
Valores de ronda 22 (761A): `netdev_budget` 300->480, `dev_weight` 64->48; RTT medio 0.231 -> 0.184 ms.

**Stage 50B (OTA, 9 trials, interfaz sysfs NO registrada; solo `ap_apply_out`):** baseline 49B `1024qam (10x)`: bulk TCP 14.545 Mbps, ping p95 10.437 ms. R1 `256qam (8x)` (ceiling 19):
bulk 9.775 (-32.795%), IPTV 9.814 Mbps, ping p95 7.663 ms -> `winning_profile`. R2 `64qam (6x) SWQ2` (ceiling 15): bulk 10.028 (-31.055%), p95 8.892 ms -> no ganador (DISCARDED).
El recibo elige R1 aunque el bulk TCP baja: criterio latencia/IPTV, no throughput.

## 6. Kits y artefactos con sha256 (calculado en disco; 12 hex)

| Campania | Artefacto | sha256 (disco) | Estado |
| :-- | :-- | :-- | :-- |
| OpenWrt v7 | 16 imagenes `firmware/openwrt/wa_universal_kit_v7/*-v7-{factory,sysupgrade}-{ap,sta}.bin` (p.ej. powerbeam factory-ap) | `bcbe0c22a728` (powerbeam factory-ap); resto en JSON | los 16 coinciden con el manifiesto 306A |
| OpenWrt v7 | `pbe5ac_gen2_ptp_kit/99-fmx-wa-universal-champion-v4` | `edf58be7c133` | **hash_mismatch**: 306A cita `06d5d9ad1ab3`; el archivo es el stub retirado (974 B) |
| OpenWrt v7 | `99-fmx-wa-universal-champion`, `99-fmx-wmm-dscp-qos`, `99-fmx-pbe5ac-ptp` | `edf58be7c133` (los 3) | stub retirado, sin hash citado |
| OpenWrt v7 | PBE factory AP-241 / STA-242 `.bin` | `6cbc647d3dca` / `84d57f95becb` | presentes |
| airOS v9 | `controller/guarida_stage29b_deploy_packager.py` | `e8d7e364cdf5` | presente (renderiza v5..v8) |
| airOS v8 | script renderizado en memoria | null | 87A cita `0e83b1cb01a6`; no hay archivo. v9 no tiene hash de script registrado |
| PtMP v23 | `tools/panel1/panel1_admitter.sh` / `fmx_panel1_champion_persistence.sh` | `a52de88bdb13` / `40487229279c` | presentes |
| PtMP v23 | `fmx_wds_churn_healer.sh` (daemon del kit v23) | null | ausente: el recibo solo nombra `/usr/sbin/...` en la radio |
| LTU v20 | `firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh` | `edf58be7c133` | **hash_mismatch**: 764A cita `c6e6499d8cc7`; stub retirado |
| LTU v20 | `fmx_ltu_irq_napi_and_dhcp_guard.sh` | `edf58be7c133` | **hash_mismatch**: 762A/764A citan `adc2fa88aa76`; el original (1334 B) existe en git commit `1afaeb771216` y SU hash coincide con el citado |
| LTU v20 | `fmx_ltu_v20_264window_zero_dhcp_kit.sh` | `edf58be7c133` | **hash_mismatch**: 774A cita `395c397fae42`; stub, sin original recuperable en git |
| LTU v20 | `ltu_5board_universal_manifest_v20.json` | `911f7eefb734` | presente |
| LTU | `firmware/ltu_safe_kit/SHA256SUMS` | `16e179acee4e` | 21 lineas, 2 hashes distintos: 20 listan `edf58be7...` (el del stub) y `fmx_ltu_runtime_transaction.sh` lista `743a47fb86f6`; no coincide con los hashes citados por los recibos |

Hallazgo: los scripts campeon de `firmware/` fueron reemplazados por un stub fail-closed (cabecera "Legacy actuator retired", commit `e9acac6`); los bytes que se
midieron en los recibos NO estan en el arbol actual (salvo el guard IRQ/NAPI recuperable en git). Reproducir un campeon requiere los valores de este catalogo, no los scripts.

## 7. Huecos (gaps) y limites

- Valores no registrados en campos estructurados (computado sobre las entradas): OpenWrt before 7 sin valor, delta pct 45 sin registrar; airOS before 92, tuned 7, delta 38, verdicto no clasificado 13;
  PtMP delta 20; LTU before 16, tuned 3, delta 4. Los "antes" de airOS son match por nombre de clave (no por comando) y algunos conflictos de stock entre recibos quedan en null.
- Variantes de ronda OpenWrt: valores antes/despues solo en prosa del titulo. PtMP: solo prosa de brazos. airOS 60A/62A/68A: sin `candidate_commands` (62A/68A con regex de hipotesis, marcado `value_source`).
- LTU 7..22: atribucion por knob imposible (bundle); la ruta de la metrica RTT no esta nombrada en los recibos tardios. 185A-R2, 218A-R3, 247A-R3, 287A-R2 y 287A-R3 empeoran p99 y el recibo igual elige campeon (lista computada en el JSON, gap `verdict_semantics`).
- Ronda 23 LTU (276 ventanas): runner + kit v21 presentes, recibo ausente. Knobs planificados (docstring): `neigh.default.gc_thresh2` 512 vs 2048, `gc_thresh3` 1024 vs 4096, budget 480, dev_weight 48.
- Verdicto: `PROMOTE_ARM_B` / `KEEP` siguen la regla del recibo (Pareto / fmx_loss), no el goodput solo; se copia tal cual.
- Fuera de rango, solo contexto (no contado): 53A, 54A, 56A, 105A (airOS); campeones WA v8..v13 (407A..759A).
- Atribucion: Linux/mac80211/ath10k y firmware QCA para WA/PtP; Linux y modulo propietario airMAX/LTU para LTU. Ninguna fila implica aceptacion fisica.
