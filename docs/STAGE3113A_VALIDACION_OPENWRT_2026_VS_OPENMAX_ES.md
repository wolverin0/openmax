<!-- doc-head: Stage 3113A ES: validacion de los 13 hallazgos OpenWrt 2025-2026 (research/inbox de ChatGPT, fuentes sin validar) contra las fuentes del vault hyperresearch (tag openwrt-2026) y contra openMAX real (24.10.4 ath79, ath10k-ct-smallbuffers 2024.07.30 / ath10k-6.10, kernel 6.6.110, core MikroTik); resultado: 11 CONFIRMED, 2 PARTIAL, 0 REFUTED; ninguno sube capacidad de radio; 3 acciones utiles (migracion 25.12 + A/B ath10k-ct, guarda de reset de contadores, precheck flowtable/oom) -->
Que cubre: tabla de 13 hallazgos (fuente, aplica, ya conocido, accion), ranking de lo accionable con tarjeta de banco, y lo que se ignora.
Estado: SOLO LECTURA / ESCRITORIO. 0 SSH, 0 escrituras en equipos. Radios con gate del operador: las tarjetas estan escritas, nada ejecutado.
Entrada: research/inbox/2026-10-31-openwrt-mejoras-ultimo-ano.md (copia importada en research/notes/imported/openwrt-2026/). Fuentes: research/notes/ tag openwrt-2026 (20 notas) + 1 WebFetch (Makefile main de ath10k-ct).
Leer cuando: antes de planear un salto 24.10.4 -> 25.12.x, tocar ath10k-ct, flow offload o cake-autorate.
<!-- /doc-head -->

## Linea base openMAX verificada en el repo
- Imagenes: OpenWrt 24.10.4 ath79/generic, kernel 6.6.110, mips_24kc, opkg, wifi en shell, wpad-basic-mbedtls.
- Driver: `kmod-ath10k-ct-smallbuffers` = `ath10k-ct-2024.07.30~ac71b14d`, fuente `ath10k-6.10`; firmware `ath10k-firmware-qca988x-ct` 2020.11.08-r1; mac80211 backports 6.12.x (STAGE1157A, STAGE1187A, manifest firmware/openwrt/futuramax-r28959-spectral/profiles.json).
- Kits: los champion solo hacen `firewall.@defaults[0].flow_offloading=1`; ninguna linea propia setea `flow_offloading_hw`. Nodos AP/CPE/PtP = bridges L2. Core/edge = MikroTik RB1100AHx4 (RouterOS).
- OpenWrt 24.10 sin parches de seguridad desde septiembre 2026 (nota release v25.12.0: "We will not provide security updates for OpenWrt 24.10 after September 2026"). Hoy 31/10/2026 nuestra base ya esta fuera de soporte.

## Tabla de los 13 hallazgos
| # | Hallazgo | Fuente verificada | Aplica a openMAX | Ya conocido | Accion |
| --- | --- | --- | --- | --- | --- |
| 1 | Rust tier-1 (PR #22748) | CONFIRMED: merge a1788e6 en main 30/10/2026; triple mips soft-float soportado; sin pruebas en ath79 | NO (no cambia radio; solo herramienta futura en 16 MB flash / 64 MB RAM) | ninguno | none, watch |
| 2 | PPE qca_ppe/qca_edma (PR #24806) | CONFIRMED: merge en main 26/10 (robimarko "Lets see what explodes"); solo snapshot | NO: IPQ807x/IPQ60xx, no ath79 ni QCA988x | ninguno | none |
| 3 | PPE + CAKE + L4S | CONFIRMED: #26177 y sqm-scripts #196 en Draft; medidas solo AX3600, autor propio | NO: sin PPE, parches en pending-6.18, CPE MIPS single-core | CAKE si (FMX-0006, OPENMAX_RESEARCH_DECISION); L4S no | watch |
| 4 | cake_mq en 25.12 + issue #22344 | CONFIRMED: backport dd79feb; #22344 abierto ("Still a known issue" 19/10); Known issue en 25.12.6. UNVERIFIABLE: "sqm-scripts desactivo cake_mq por defecto" | NO: ath79 single-core, 1 cola TX; kernel 6.6 sin cake_mq | CAKE single-queue si; cake_mq no | none |
| 5 | Mejoras PPPoE (74bf368) | CONFIRMED: parches 621-626 + pending 650 GRO, contra backport-6.12 (solo 25.12/main) | NO: radios no terminan PPPoE; PPPoE vive en MikroTik | no (solo knob DSCP airMAX no relacionado) | none |
| 6 | ath10k-ct estable vs main | PARTIAL: 25.12.6 = 2025-12-01 (ath10k-6.18); main = 2026-07-31 fcbdb70 (ath10k-7.2) CONFIRMED; "fixes de RX/recuperacion" solo parcialmente visible en el diff | PARTIAL: nuestro driver es 6.10/2024.07.30, ~16-17 meses atras de ambos; fixes visibles relevantes para QCA988x: NULL en rx_netbuf_pop, recovery_check_work, beacon ar NULL tras FW crash | identidad del driver si (1103A/1157A/1189A/1431A); comparacion contra 25.12/main no | test card + watch |
| 7 | mt76 fixes 25.12.2 + multicast_to_unicast 25.12.6 | CONFIRMED (matiz: 160 MHz es wifi-scripts, no mt76; m2u "works again" es regresion de 25.12) | PARTIAL indirecto: mt76 no; m2u si lo usamos, pero via sysfs en 24.10.4 | m2u si (Stage 31A/35A M15_5GHz, champion v9) | checklist de migracion |
| 8 | Mesh MT7996 <-> ath11k (mt76 #1132) | CONFIRMED: PR abierto, Address3 = 00:..:00, 217 Open / 0 entregados | NO: sin 802.11s ni mt76 | WDS/4addr si (108A/111A); mesh no | none (leccion: ACK MAC != entrega a host) |
| 9 | Airtime MT7996 resetea (PR #26037) | CONFIRMED: abierto, sin review | NO como bug; SI como leccion de telemetria (delta negativo -> valor gigante) | parcial: Stage69B exige contadores same-boot; write a debugfs airtime resetea el STA (RESEARCH_LEDGER) | test card software |
| 10 | cake-autorate ago-2026 + fork JMarty | CONFIRMED (+ commit 29/10 #420 irtt no citado). UNVERIFIABLE: "integracion cake_mq pendiente" | PARCIAL bajo: solo en un Linux que alimente el PtP-Colo (.62/.54); no en MikroTik, no en PtMP | CAKE fijo si; autorate no (grep 0) | test card (baja) |
| 11 | Flow offload stale tras recrear Wi-Fi (#25646) | PARTIAL: reporte de 1 equipo (C7 v2, 25.12.5, ath10k no-CT), 310->135 Mbit/s con hw=1; DFS no probado; fix candidato no fusionado | PARTIAL / probable NO: requiere `flow_offloading_hw=1` y trafico ruteado; nuestros nodos son bridges sin hw=1 | parcial: CAMPEON V2 / guia V4 ya dicen offload UNPROVEN | precheck read-only + watch |
| 12 | Fork openwrt-ppe-nss benchmarks | CONFIRMED (matiz: wiki editada 20/10, no 29/10; "29/10 builds" UNVERIFIABLE); cifras propias, 1 placa | NO: IPQ807x/IPQ60xx + NSS ath11k | ninguno | none; citar como "self-reported, single-board" |
| 13 | Base 25.12: kernel 6.12, apk, ucode wifi, ASU | CONFIRMED: 6.12.71, mac80211 6.18.7 (25.12.6: 6.18.55 con fixes ath10k), opkg->apk, wifi en ucode; 24.10 EOL septiembre 2026 | PARTIAL: riesgo de mantenimiento/seguridad, no ganancia de radio; rompe kits que usen opkg o scripts wifi shell; invalida el ledger AQL/fq_codel | ninguno sobre 25.12/apk/ucode | test card + build change |

Conteo de fuentes: 11 CONFIRMED (4, 7, 8, 10, 12 con matices), 2 PARTIAL (6, 11), 0 REFUTED. Subclaims UNVERIFIABLE: #4 default de sqm-scripts, #10 integracion cake_mq, #12 builds del 29/10.
Aplica: 0 YES directo, 6 PARTIAL (6, 7, 9, 10, 11, 13), 7 NO (1, 2, 3, 4, 5, 8, 12).

## Accionable para openMAX (ranking)
1. **Salto de base 24.10.4 -> 25.12.6 con A/B de ath10k-ct (#13 + #6). Prioridad alta por seguridad, no por rendimiento.**
   - Paso 0 (escritorio, sin radios): diff estatico `ath10k-6.10` (nuestro) vs `ath10k-6.18` (25.12.6) para ver si ya existen los 3 fixes visibles de fcbdb70 (guarda NULL en `ath10k_htt_rx_netbuf_pop`, `recovery_check_work` en workqueue_aux, chequeo `ar` NULL en `ath10k_wmi_tx_beacon_nowait`). Si faltan en 6.10, evaluar backport minimo a smallbuffers sin cambiar de base.
   - Paso 1 (escritorio): grep de kits por `opkg`, `/usr/lib/opkg/status`, `/lib/netifd/wireless`, `wifi detect`; adaptar a apk/ucode. Los hooks hotplug/sysctl/tc en shell no se ven afectados.
   - Tarjeta de banco (gate del operador, NO ejecutado): LAP-120 `.20` + Loco `.250`, backup + hash de mtd0/1/4/5, watchdog de auto-revert, nunca mtd0/1/5. ImageBuilder: A = 24.10.4 actual, B = 25.12.6 con la misma lista (kmod-ath10k-ct-smallbuffers, ath10k-firmware-qca988x-ct, wpad-basic-mbedtls, kits champion). Medir tamano de imagen vs particion y RAM libre en reposo/carga (`free`, `/proc/meminfo`, OOM en dmesg); RAM exacta de la Loco: UNKNOWN, leer HARDWARE_MATRIX antes. Sysupgrade A->B conservando config y verificar UCI wireless/network + 99-fmx-cpe-champion. Luego A/B/A 3x30 min con 2 CPE, canal/ancho/potencia fijos: iperf3 TCP bulk + UDP IPTV + VoIP; goodput p50, RTT cargado p50/p95/p99, retries/PER por estacion, conteo de `firmware crashed`/recovery y warns de rx ring en dmesg, survey noise. Verificar `multicast_to_unicast=1` en `/sys/devices/virtual/net/br-lan/brif/phy0-ap0*/` (#7). Decision solo si la diferencia supera la varianza A/A medida (sin umbrales inventados). Todo el ledger de knobs AQL/fq_codel queda "sin validar en 25.12" hasta re-medirlo.
2. **Guarda de reset/wrap de contadores en el exportador zero-FP (#9). Solo software, sin radio, barato.**
   - Tarjeta: auditar tools/uisp/ y los engines v5-v9 para que un delta acumulativo < 0 o mayor que el techo fisico (tiempo de reloj x 1.0 para airtime) se marque `counter_reset`, se descarte la muestra y se rebasee el cache sin emitir alerta; distinguir wraparound legitimo (cerca de 2^32/2^64); no actualizar el cache si la lectura fallo. Test unitario: serie [100, 200, 5, 15] -> delta None + rebase; [2^32-10, 5] -> delta 15. Opcional con gate: escribir en debugfs `stations/<mac>/airtime` del LAP-120 `.20` con el exportador corriendo y verificar 0 alertas falsas.
3. **Precheck read-only de flowtable y oom_score_adj (#11). Prioridad baja/media.**
   - Tarjeta (gate del operador para cualquier `wifi reload`): en LAP-120 `.20`, Loco `.250`, PBE `.241/.242` leer `uci get firewall.@defaults[0].flow_offloading`, `...flow_offloading_hw`, `nft list flowtables`, `ip route`. Si la flowtable esta vacia o el nodo no rutea: cerrar #11 como NO APLICA. Ademas tras un `wifi reload` de banco leer `cat /proc/$(pidof hostapd)/oom_score_adj` (esperado -900). Riesgo INFERRED, no observado: en 24.10 hostapd es un proceso unico gestionado por ucode/ubus y puede no relanzarse; si vuelve a 0, re-aplicar en el hook con ACTION=add de phy*-ap*.
   - Sin radio: no activar `flow_offloading_hw` en kits publicos y rotular la afirmacion de offload de CAMPEON V2 como UNPROVEN hasta tener `nft list flowtables` como evidencia.
4. **cake-autorate en el PtP-Colo (#10). Baja.** Solo en un Linux del lado que alimenta el enlace (no en radios, no en MikroTik). Banco PtP `.241/.242`: CAKE fijo maximo vs conservador vs autorate (1 reflector = extremo remoto, 5 Hz), flent RRUL 5 min, p95/p99 bajo carga, goodput, CPU. Las caidas de capacidad controladas (cambio de ancho/potencia) solo con gate del operador y watchdog. Aceptar solo si p95 <= CAKE fijo conservador y goodput >= ese mismo baseline sin oscilar.

## Watch upstream
- openwrt-25.12 Makefile de ath10k-ct: aun no hay 25.12.x con fcbdb70 (ath10k-7.2); seguir el bump de PKG_SOURCE_DATE.
- Issue #25646 y el commit firewall4 "refresh flowtable on Wi-Fi netdev add".
- #26177 (CAKE ce_threshold) solo si llega a estable con kernel >= 6.12 y hay un Linux en el POP con ECT(1).

## Ignorar y por que
- #1 Rust: no cambia el datapath ni ath10k-ct; reabrir solo si se porta fmx_omn a Rust.
- #2, #3, #12 PPE/NSS: hardware IPQ807x/IPQ60xx que no tenemos; cifras de un solo AX3600 del autor; no extrapolar a MIPS 560-720 MHz.
- #4 cake_mq: nada que repartir en ath79 single-core; reabrir solo si un gateway Linux del POP satura un core de CAKE (comparar contra single CAKE con flent RRUL).
- #5 PPPoE: el PPPoE lo termina RouterOS, no Linux.
- #8 mesh mt76: no usamos 802.11s. Leccion para zero-FP: no declarar enlace UP solo por ACK/asociacion.
- #7 mt76: hardware ajeno; solo queda el item de checklist de m2u en la migracion (ver accion 1).

## Limites
- No se tocaron equipos ni red. El diff completo de fcbdb70 (ath10k-7.2 y 6.18/wmi.c) no esta visible en la nota: "fixes de RX" queda PARTIAL.
- Ningun hallazgo trae evidencia de mas capacidad de radio para QCA988x; el valor es seguridad/mantenimiento (#13), estabilidad del driver (#6) y higiene de telemetria (#9, #11).
