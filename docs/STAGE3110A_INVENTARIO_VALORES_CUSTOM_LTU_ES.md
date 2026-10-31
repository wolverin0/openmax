<!-- doc-head: STAGE3110A inventario de valores NO stock aplicados a las LTU de banco (Lite1 .110, Lite2, Rocket) y default a restaurar; solo lectura de docs/artifacts, sin acceso a equipos -->
Fuentes: STAGE15/16/17B/24D/24F/26/64A/80A/83B/247A, STAGE3092A_LTU_PTMP_ES, STAGE3101A, wave432_ltu_ptmp.json, wave441_ltu_autoresearch.json, controller/multiradio_golden_profile_applicator.py.
Etiquetas: CONFIRMED (evidencia citada), INFERRED, UNKNOWN. "Default" = valor stock inferido de rollback_commands del perfil dorado o de la comparacion A/B de los docs, NO de documentacion oficial de Ubiquiti (no hay en el repo): verificar contra backup stock antes de escribir.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# STAGE3110A: inventario de valores custom en LTU de banco

Equipos: **L1** = LTU-Lite #1 PUBLIC_DEVICE_0045 (198.18.0.63, br0 198.18.0.84); **L2** = LTU-Lite #2 PUBLIC_DEVICE_0043 (198.18.0.140 / .111/.115); **R** = LTU-Rocket PUBLIC_DEVICE_0050 (.114).
Estado "ahora" = despues de W432 (reboots de L1, L2 y R) y W441 (sin escrituras). Todo lo RAM-only de Stage 15-26/247A/83B se perdio en esos reboots (INFERRED, no hay readback posterior de sysfs).

## 1. Persistente en flash (cfgmtd mtd5 / rc.poststart): sigue activo

| Equipo | Parametro | Valor custom | Default / a restaurar | Efecto esperado | Evidencia |
|---|---|---|---|---|---|
| R | SSID / seguridad | FMX-LTU, aes_en=0, wpa_passphrase cambiada (no se imprime) | SSID original de produccion, WPA2 original (backup cifrado) | Ninguno en throughput; sin cifrado | wave432 rocket_radio.changes (CONFIRMED) |
| R | freq/rxfreq/txfreq, prefer_work_rx/tx | 5500 MHz (antes otro valor; "changed") | valor del backup stock | Fija portadora; no explica 6025 | rocket_radio, rocket_persistence (CONFIRMED) |
| R | autolink_en | 0 (changed) | stock (L2 stock/legado lo forzaba a 1) | Sin auto-reparacion de enlace | rocket_radio, profiles_compare_fresh (CONFIRMED) |
| R | netconf.2.ip / route.1.gateway | 198.18.0.138 / gw cambiado (antes 198.18.0.136) | IP/gw originales | Solo gestion | rocket_persistence (CONFIRMED) |
| R | ame.cfg: txpwr=30, czlen=10, ptmp_max_cpe=101, smart_scan=1, auto_freq_mode=1, auto_freq_list=0 | no se sabe cuales son de fabrica | UNKNOWN: comparar con backup stock | czlen/cz_len afecta contention zone de UL | profiles_compare_fresh (CONFIRMED valores; origen UNKNOWN) |
| L1 | system.cfg nativo CPE (role/mode=cpe, board_ssid 0xae08, SSID FMX-LTU, freq 5500, freq_scan_list "5500 5520", radio.countrycode 4097) | guardado por cfgmtd | countrycode 4097: UNKNOWN si es stock | Define el enlace | cpe_boot_trial, native_scan_comparisons (CONFIRMED) |
| L1 | rc.poststart: hook minimo nativo + excepcion NAT src110/dst114 (sha final 27c3932c...) | reemplaza al hook legado | hook stock: rc vacio/original | Gestion; NAT solo para 110->114 | wave441 final_readback (CONFIRMED) |
| L1 | Hook legado AP (sha 26e33e13...), con todos los sysfs de la seccion 3 | ya NO activo; copia cifrada lite110_poststart.dpapi | no restaurar salvo rollback | ver seccion 3 | phase2.cpe_boot_trial, RC comment "legacy AP hook retained privately" (CONFIRMED) |
| L2 | rc.poststart LEGADO (sha eb3bc4c0...; 7 archivos persistentes) restaurado por la guardia | ACTIVO: `af set powerout 28` x2, `txpwr = 15` en ame.cfg/ame.ini/etc/ame.ini, `autolink_en = 1`, `ame_drv.sh stop/start` en boot, br1 198.18.0.118 + 198.18.0.140 | hook stock; autolink_en stock UNKNOWN (R lo tiene en 0) | Fuerza potencia/autolink y reinicia el driver en cada boot | lite2_qualification.rollback_management_hook_excerpt; STAGE3092A_LTU_PTMP_ES (CONFIRMED) |
| L2 | system.cfg (sha 4bb9275f...): radio.1.mode=managed, txpower=15, SSID FMX-LTU, freq 5500, countrycode 4097 | guardado | stock UNKNOWN | idem | lite2_preflight (CONFIRMED) |

## 2. Binarios parcheados (offline; nunca confirmados en los 3 equipos de banco)

| Item | Valor custom | Donde | Ahora | Default | Efecto |
|---|---|---|---|---|---|
| ame_core_fmx / ame_dev_fmx 2.4.2 (STAGE64A): startThrd_4096 97->90, stayThrd_4096 90->82, table_ptpPwrRange 4096QAM (0,0)->(20,50..55) (hasta 25-27.5 dBm), autoMcsCeiling sin reset a 0x20, frame_len_store 0x54->0x5c | .ko en /tmp (RAM) | STAGE64A: 100% offline, 0 SSH (CONFIRMED). Banco: Rocket 2.1.0 / Lite 2.4.0, no 2.4.2: NO cargado (INFERRED) | .ko stock (sha en STAGE64A s1.1) | Subiria potencia maxima de PtP; irrelevante si no cargado |
| cds_mac_mod/ame_dev stage80A (4 .ko, 18 parches, NAPI 64, sin usleep) + script runtime (IRQ pinning, maxBD 84, skb_fpga 512) | /etc/persistent + insmod | STAGE83B dice "LIVE" sin identificar equipo (UNKNOWN); para 2.4.2 | .ko stock | si estuvo en L1 en /etc/persistent lo borro el reemplazo del hook (INFERRED) |
| air_fpga parse_role patch (byte 0x1acc33=0xea, bind-mount /tmp/air_fpga) | hook legado L1 | quitado al pasar a CPE nativo; W432 midio hash nativo 8543255c... (CONFIRMED) | /bin/air_fpga stock | Solo desbloqueaba rol AP en Lite |

## 3. RAM-only / hook legado de L1: perdido en reboot (verificar por readback)

| Parametro | Custom | Default (rollback del perfil, INFERRED) | Fuente | Efecto sobre UL |
|---|---|---|---|---|
| ame_core sched_max_agg_cnt | 8 | 5 | S15-R2, S24F | agregacion; ayuda DL |
| cz_cross_frame_backoff_enable | 0 | 1 | S15-R4 (-15.96% goodput), S24F | backoff de la contention zone UL |
| multi_ack_enable / send_ctrl_in_data / send_map_enable | 1 / 0 (S15: 1) / 1 | 1 / 1 / 0 | S15-R6, S24F | control/mapas UL/DL |
| sched_mcs_limit_symbol_begin / ap_symbol_end / symbol_end | 12 / 62 / 72 | 0 (S15 dice 15) / 60 / 70 | S24D/F | ventana de simbolos |
| DGAIN_DL_ENABLE, SNR_BOOST_THD_ADJ, pb_boost | hook final: DGAIN=1; pb_boost "1 12" | 0, 0, 2 (auto) | hook L1 lineas 40-41,163,169 | S24D: +9.85% CPU |
| ptmp_ul_strategy / cz_cross_frame_multiple_res_en | 1 / (1 en S26-B) | 0 / 0 | hook linea 168, S26 (+84.7% p95) | estrategia scheduler UL: sospechoso |
| ulpwr_enable | 0 | 1 (INFERRED) | hook linea 148 | desactiva control de potencia UL |
| autoMcsCeiling / cpe_mcs "0 19 0" y "0 19 2" / sched_*_mcs_limit_level / autoMcsUpDown | 19 / 19 / 6 / "7 10 15 5 93 93 1 20 0 60 2 25 1" | auto (0x20) / auto / UNKNOWN / UNKNOWN | hook lineas 143-146,164-166 | techo MCS UL/DL |
| maxBD, adj_stallBD, SWQ_INTERVAL_EXTEND, dbg_ptmp_ul_pm_cpe, SNR_BOOST_EN | 84, 0, 2, 0, 1 | 49 (0x31 por STAGE64A), UNKNOWN | hook lineas 141,167,170,171 | colas |
| af powerout / txpwr / antennagain | hook: powerout 28, txpwr 15; S15/S26: antennagain 26 + powerout 0 (-26 dBm) | stock UNKNOWN; Lite txpower 10 (S15) | hook 63,80,97; S26 | potencia conducida |
| dscp.4=32 (antes 34), dscp.5=46, qos_dscp | custom | dscp.4.value=34 | hook linea 44,158-162 | solo priorizacion |
| insmod sch_htb, cls_u32 | cargados | no cargados | hook 42-43 | QoS |
| sysctl rmem/wmem 524288, netdev_max_backlog 2500, tcp_dsack 1; txqueuelen 256 | custom | 262144/262144/1000; dsack 0; txqueuelen 1000 | golden profile | colas |
| fq_codel eth0/ath0 limit 1024 flows 1024 quantum 1514 target 2500us interval 50000us ecn | custom (S15-R3 lo rechazo: +134.95% p95) | quantum 300 target 5000us interval 100000us | golden profile, S247A | latencia |
| TCP pacing ca_ratio 120 / ss_ratio 200, ecn 1; br0/br1 multicast_snooping 0, ageing 30000; nf_conntrack_max 16384 | custom | kernel default | S247A | despreciable |
| RAM alineacion S15: SSID PUBLIC_TERM_0006, 5825 MHz, smart_scan 0, auto_freq_mode 0, freq_list 5825, set_ssd_pause_flag 1 (la clave WPA2 de S15 no se repite) | solo R/L1/L2 antes de W432 | SSID PUBLIC_TERM_0007 / PUBLIC_TERM_0008 originales | S15 s2 | Hoy smart_scan/auto_freq_mode=1 en R: el AP puede mover frecuencia |
| L1/L2 como AP PtMP desbloqueado: board_ssid 0xae05, role=ap, ptmp_max_cpe=4 (/tmp/ame.cfg + cds_mac_mod params) | RAM | 0xae08, role cpe | S17B, S26 | L1 ya es CPE nativo |
| L1/L2 S26: bandwidth 20, duty 750, frame 2000, czlen 6, tcp -26 dBm | RAM | idem excepto potencia | S26 | |

## 4. Observado hoy (W432/W441, CONFIRMED)

- L1 como CPE: `Txpower 2,2, Antenna Gain 13`, rx 5500 / **tx 6025 MHz**; R ve `rx(6025) tx(5500)`, Txpower 23-25, Gain 26. Firma R: aflturocket.v2.1.0 (cz_len 3); Lite v2.4.0 (cz_len 6).
- Senal: AP recibe de L1 -56..-69 dBm; L1 recibe del AP -35 dBm (asimetria ~20-30 dB). TCP: UL 4.47-6.27 Mbps (206-228 retrans), DL 69.4-70.5 Mbps (0 retrans). Distancia 140-147 m (cable de banco).
- L2: `Txpower 15 (legado) -> 2`, Gain 13, rx 5490 tx 6025 en Scan, 0 preambulos, "Stations count 0"; campos de radio comparados iguales a L1 (native_scan_comparisons); guardia restauro el hook legado.

## 5. Sospechosos

**(a) UL 5 Mbps vs DL 70**
1. UL de L1 a 2 dBm conducidos con rx del AP en 6025 MHz (fuera de 5500): potencia/portadora UL, asimetria 20-30 dB. El 6025 no esta entre los valores aplicados; origen UNKNOWN (smart_scan/auto_freq_mode=1 en R, splitfreqmode=disabled). Accion: fijar rxfreq=txfreq=5500, smart_scan=0, auto_freq_mode=0 y leer `/bin/af get powerout`, `amecli get_remote_info`.
2. Mismatch de firmware R 2.1.0 (cz_len 3, tx_isr_sample SYM#7) vs Lite 2.4.0 (cz_len 6, SYM#4): contention zone de UL desalineada (S15 s3, S16 s2). No es custom pero domina UL; solo se arregla con parity 2.4.x (upgrade oficial permitido solo como fallback).
3. Knobs de scheduler UL del hook legado L1: ptmp_ul_strategy=1 (S26: +84.7% p95), cz_cross_frame_backoff=0 (S15-R4: -15.96%), ulpwr_enable=0, mcs_limit_level 6, cpe_mcs "0 19": probablemente NO activos hoy (hook reemplazado). Confirmar con `cat /sys/module/ame_core/parameters/*` y `ulpwr_enable` en L1 antes de descartarlos.

**(b) L2 con 0 preambulos**
1. Hook legado de L2 reactivado: `autolink_en=1`, `powerout 28`, `txpwr=15`, `ame_drv.sh stop/start` en boot, mas freq_scan_list "5500 5520" y countrycode 4097: el driver reinicia y puede escanear 5490/6025 en vez de 5500. INFERRED.
2. Frecuencia de RX/TX de L2 (rx 5490, tx 6025) distinta de R (tx 5500): mismo patron 6025 que L1; si el AP no emite en la frecuencia que L2 escucha, 0 preambulos. Fijar 5500 y autolink_en=0 como en R/L1.
3. Cadena RF fisica de L2 (conector/antena): W432 dijo "causa fisica no confirmada". Stage 26 la dejo con antennagain 26/powerout 0 (-26 dBm, RAM) y rx -43 dBm (OK entonces con L1 como AP); descartar con rxpower0/1 y `amecli beacon_list` con R en 5500 fijo.

## 6. Restauracion en un paso (orden sugerido, sin ejecutar)

1. Backup stock de cada equipo (cifrado en STAGE3092A_private_backups/): reponer system.cfg y rc.poststart stock con cfgmtd -w -p /etc/ (solo mtd5 cfg; nunca mtd0/1/5-EEPROM).
2. R: SSID/seguridad/IP/gw/freq originales; L1/L2: role cpe, quitar hook legado/NAT.
3. Reboot y readback sysfs para confirmar que la seccion 3 volvio a default (esperado por reboot).
Limites: sin acceso a equipos; defaults de 3 y 1 son inferidos de rollback de perfil, no de fabrica.
