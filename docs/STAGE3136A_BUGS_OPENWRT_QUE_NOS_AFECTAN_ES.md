<!-- doc-head: Stage 3136A ES: bugs de OpenWrt, ath10k-ct (QCA988x CT), mac80211 4addr/WDS, AQL, hostapd y ath79 (LAP-120, LiteBeam AC gen2, NanoStation AC Loco) que nos pegan o pueden pegar; resultado: 12 candidatos; 0 fallas de firmware, SWBA, wedged, tx hang ni OOM en los 10 nodos legibles desde su arranque; 1 reinicio simultaneo de 10 equipos Guarida hoy 14:27 UTC (causa desconocida); 2 candidatos con impacto posible en nuestro driver (RSSI con noise floor CT, mac80211 6.12.y); nada publicado upstream; SOLO LECTURA -->
Que cubre: bugs abiertos o corregidos despues de nuestro tag v24.10.4, con evidencia de nodos (uci, dmesg y logread desde el arranque), telemetria (reinicios y flaps) y fuentes upstream (openwrt/openwrt, greearb/ath10k-ct, gregkh/linux).
Estado: SOLO LECTURA. 0 escrituras en equipos, radios de banco sin tocar (LAP .20, Loco .117, PBE .241/.242, LiteBeam .116, LTU), nada publicado upstream. Tarjetas de banco escritas, sin ejecutar.
Entrada: docs/STAGE3113A_VALIDACION_OPENWRT_2026_VS_OPENMAX_ES.md y docs/STAGE3116A_DIFF_ATH10K_CT_610_VS_618_ES.md (no repetidos). Dato: artifacts/autoresearch/stage3136a_openwrt_bug_hunt.json.
Leer cuando: antes de tocar ath10k-ct, el backport de mac80211, un enlace WDS con cifrado, o al investigar reinicios de Guarida.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

## Empieza con lo que necesitas de mí
- Revisar en sitio (Torre Guarida, celdas panel1-3) que paso a las 14:27:22 UTC del 2026-10-31: reiniciaron 10 equipos (3 APs y 7 CPEs) en 61 s. La lectura no da la causa. [CONFIRMED timing: telemetry.db; UNKNOWN causa]
- Nada mas requiere decision tuya.

## Lo que ya quedo resuelto (3113A, 3116A)
- 3116A: nuestro driver es ath10k-6.10 (ac71b14d, 2024-07-30). Los 3 fixes de recovery y NULL estan en 7.2 (uno solo parcial), no en 6.18 (25.12). Backport de ~97 lineas aplica limpio, sin compilar. No se repite.
- 3113A: ninguno sube capacidad de radio; 24.10 sin parches de seguridad desde sept 2026; flow offload no aplica a bridges. No se repite.
- Nuevo aqui: openwrt-24.10 no tiene cambios de ath10k-ct ni de su firmware despues de nuestro tag v24.10.4 (commit 78b23a26, 2025-10-20). El ultimo cambio del paquete es 2025-04-10. [CONFIRMED: gh api commits?path=package/kernel/ath10k-ct]

## Metodo y limites
- Nodos: 18 habilitados en el registro del daemon (`openwrt_before_after_nodes.json`). Leidos 10 con `wave449_memory.production()` + `rpc()`, solo shell de lectura: uname, uptime, boot_id, `uci show wireless` filtrado, dmesg y logread contados con awk. No leidos 8: timeout SSH (3 APs Guarida, 5 CPEs). De esos, 5 reiniciaron entre 14:27:28 y 14:28:23 (3 APs, cpe_200_41 y cpe_200_223); cpe_210_235 reinicio a 14:33:49, fuera del grupo.
- dmesg y logread son desde el ultimo arranque. Lo que paso antes de un reinicio no se ve.
- telemetry.db abierto `mode=ro`: 47 387 filas. Reinicio = cambio de boot_id con caida de uptime. Sin umbrales nuevos: no hay A/A propio.
- Upstream: gh sobre openwrt/openwrt, greearb/ath10k-ct y gregkh/linux (tags v6.12.52 y v6.12.96). MemoryMaster no se consulto (servidor MCP desconectado).

## Evidencia de nuestros nodos (desde su arranque)
| Nodo | Placa | Uptime leido (s) | Hallazgos since-boot |
| --- | --- | --- | --- |
| ptp_colo_ap | LiteBeam AC gen2 (AP) | 242 037 | 0 fallas; 1 deauth por inactividad 13:24:13 |
| ptp_colo_sta | LiteBeam AC gen2 (STA) | 242 047 | 1 "failed to enable peer stats" a 170 s |
| cpe_210_21 | LiteBeam (celda panel2) | 242 021 | 9 peer-stats; 23 "authentication/association timed out" |
| cpe_210_238 | LiteBeam, psk2 (panel3) | 251 471 | 5 peer-stats; 5 auth timeouts; deauth razon 7 a 14:30:15 |
| cpe_200_169 | LiteBeam (panel2) | 38 299 | 2 peer-stats; 2 auth timeouts; 7 reinicios en telemetria |
| 5 CPEs reiniciados 14:26-14:28 | LiteBeam | 340-709 | solo peer-stats de arranque |
| 8 no leidos | LAP-120 (3), NanoStation AC Loco (2), LiteBeam (3) | n/a | timeout SSH |

- Los 10 leidos, desde su arranque [CONFIRMED]: 0 "firmware crashed", 0 "wedged", 0 "SWBA overrun", 0 "tx hang", 0 OOM, 0 "check-sdata". La linea `ath10k_recover` (1 por nodo) es el arranque `reset_mode 0`, no un reset.
- Driver en los 10: `ath10k 6.10 driver, optimized for CT firmware` (dmesg). Kernel 6.6.110, OpenWrt 24.10.4 (uname, /etc/openwrt_release).
- uci en los 10 [CONFIRMED]: 9 con `encryption=none` y `wds=1`; 1 con `psk2` (cpe_210_238); `radio1 disabled=1` en todos; sin `ieee80211w` ni `wpa_group_rekey` en ninguno.
- pstore vacio en 10/10: no hay dump de caida guardado (si pstore funciona = UNKNOWN).

## Reinicios y flaps (telemetry.db, solo lectura)
- Migracion airOS 8 (WA.v8.7.25) a 24.10.4: 10 equipos el 2026-10-28 entre 19:41 y 19:42 UTC. No es un crash. [CONFIRMED: campo release]
- Reinicios sin cambio de release: 30 eventos, agrupados en 20 grupos (gap de 120 s):
  - 1 grupo de 10 (celdas panel1-3, 2026-10-31 PUBLIC_DEVICE_0084). PtP-Colo no afectado. [CONFIRMED timing; causa UNKNOWN]
  - 1 grupo de 2 (2026-10-30 22:06). 18 eventos sueltos; cpe_200_169 tiene 7 de ellos. [CONFIRMED]
- Memoria libre justo antes de los reinicios sueltos: 1,8 a 14,8 MB. Sin A/A no hay umbral. [UNKNOWN]. Valores del repo: guard del daemon 6144 KiB (`memory_guard.threshold_kib`), helper 3072 KiB (`wave449_memory.py`).
- PtP-Colo: sin reinicio desde la migracion. Un deauth por inactividad en el AP (13:24:13) con max_inactivity 60 s. El STA tuvo 1 estacion en cada muestra 13:10-13:39 (60 s), asi que el corte duro menos de 60 s. [INFERRED]
- fq_overmemory (contador por boot en telemetria): ptp_colo_sta 26 436 en 67 h (unos 394/h); panel2 182; panel3 108. Que sean drops por limite de memoria de cola es INFERRED; sin A/A.

## Candidatos
| # | Bug (fuente) | Etiqueta | Nos pega | Upstream / portable | Banco (tarjeta, sin ejecutar) | Banco? |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | RSSI anclado al noise floor CT (greearb #236, 2026-10-24, abierto) | CONFIRMED codigo; INFERRED aplica; UNKNOWN impacto | Posible. a610/wmi.c:2783,2793 suman `ath10k_get_noisefloor` (chan_nf_0 del firmware) al RSSI. Magnitud no medida: no hay pdev_ext_stats en debugfs de los nodos | Sin fix upstream. No es backport simple: exige decidir la politica de RSSI | LiteBeam bench: leer chan_nf_0 y RSSI de una estacion 60 s, sin cambiar driver | Si |
| 2 | mac80211 6.12.y tras nuestro 6.12.52: 3b4d27acaf (skb leak en TX_DROP), 586c628c0b (tailroom doble en reconfig tras crash), 66a7153fd6 (stats al desconectar), 29a1a350af (carrera AQL en debugfs). gregkh/linux v6.12.52 a v6.12.96: 34 commits en net/mac80211 | CONFIRMED en 6.12.y; INFERRED nos pega (TX_DROP, reconfig) | Imagen: kmod-mac80211 6.6.110.6.12.52-r1 (manifest). Upstream si (6.12.y). Portable: probable, no compilado | Build de bench con 3b4d27acaf + 586c628c0b; A/B con la induccion de crash de 3116A; contar recuperaciones, drops y tiempo a trafico | Si |
| 3 | Timeouts de auth/assoc en STA y deauth por inactividad. OpenWrt #25416 (hostapd deja que la BSS Max Idle Period del cliente pise ap_max_inactivity; abierto 2026-09-26) | CONFIRMED conteos; UNKNOWN causa | Desconocido. cpe_210_21: 23 en 2,8 dias. El deauth de PtP no trae tiempo de baja completo | Sin fix a la fecha | Medir tiempo a deauth de un cliente que anuncia idle en PtP bench | Si |
| 4 | Reinicio simultaneo de 10 equipos Guarida (celdas panel1-3) | CONFIRMED timing; UNKNOWN causa | Si: corte de sitio. Nuestra lectura empezo despues del arranque, asi que no lo causo | n/a | n/a; accion en sitio del operador | No |
| 5 | "failed to enable peer stats info: -122" tras cada vdev up en STA (greearb #140, 2020) | CONFIRMED (9 STA, 0 AP); impacto UNKNOWN | Ruido en log. a610/mac.c:3732 = a72/mac.c:3768 | Sin fix; 7.2 lo conserva | No | No |
| 6 | GTK rekey falla en bridges 4addr con CT (greearb #196, 2022, abierto; tabla de terceros 3% a 99% segun intervalo, qca9980) | REFUTED para PtP-Colo (encryption=none); INFERRED ausente en psk2 | No con la config actual: 0 handshake_fail en cpe_210_238; sin wpa_group_rekey. El payload del repo exige 86400 (firmware/openwrt/wave103_ptp_colo_payload), no activo | Sin fix | Solo si se adopta psk2 en WDS | Condicional |
| 7 | 802.11w crash en QCA988x wave1 CT (greearb #233 2025-11, abierto; #212 2023) | INFERRED no aplica | No: sin ieee80211w en uci de 10/10 | Firmware blob, sin fix | No | No |
| 8 | SWBA overrun y AP que pierde clientes (OpenWrt #6937, UniFi AC Lite QCA988x; #22301 ahb 25.12) | CONFIRMED no visto desde arranque | No: 0 en 10/10 | n/a | No | No |
| 9 | ath9k sordo / sin RX (OpenWrt #7016); fix 6a11ba0f en 24.10 desde 2026-01-19 | CONFIRMED fix post-tag; INFERRED no aplica | No: radio1 disabled=1 en 10/10, sin ath9k activo | Portar solo si se activa 2.4 GHz | No | No |
| 10 | hostapd advisory 2026-1 (openwrt 452bc249, 2026-07-20; MLE link-ID, w1.fi/security/2026-1) | CONFIRMED falta en nuestra imagen; INFERRED sin exposicion (MLO, WiFi 7) | No | Fix en 24.10 | n/a; revision de seguridad | No |
| 11 | ETH_P_TEB para airOS 8 WDS (parche propio 990-fmx-mac80211-strip-eth-p-teb-airos8-wds.patch) | CONFIRMED sin upstream: ETH_P_TEB no aparece en net/mac80211 de mainline | Si: es parche propio | Nada que portar; re-portar si subimos a 6.12.96 | No | No |
| 12 | Ya cubiertos o no aplican: LAP-120 flash write-protect (#17234, fijo en kernel >=6.6.103; nuestro 6.6.110); usteer/DAWN (#206; no estan en dot.config); PowerBeam DFS (#10225; canales 48-161, sin DFS); CF-EW72 handshake CT en 25.12 (#23986, QCA9888) | CONFIRMED | No, salvo el riesgo de 25.12 CT (UNKNOWN para QCA988x) | n/a | Solo en un salto de base: handshake 25.12 CT en banco | Condicional |

- Sin resultados upstream (gh search): "wedged", "rekey", "ETH_P_TEB" y "sysupgrade keep" para ubnt/ath79. Sysupgrade: sysupgrade.conf sin cambios desde 2010 en 24.10; ninguno de los 346 commits posteriores al tag toca LAP-120, LiteBeam, NanoStation ni PowerBeam. [CONFIRMED]
- Kernel: 24.10 pasa de 6.6.110 a 6.6.158 (48 releases, 2025-10-06 a 2026-10-03; commit bumps en target/linux/ath79). [CONFIRMED; enumeracion UNKNOWN]

## Que no encontre o no pude medir
- Causa de los 10 reinicios de Guarida y de los 19 sueltos (incluidos 7 de cpe_200_169). [UNKNOWN]
- Impacto de #236 en el RSSI de nuestros nodos: no hay chan_nf expuesto. [UNKNOWN]
- Enumeracion completa de los parches mac80211 6.12.53 a 6.12.96 y de los de kernel 6.6.111 a 6.6.158: solo por path, sin compilar. [UNKNOWN]
- 8 nodos sin lectura en esta pasada (timeout SSH). cpe_200_80 y cpe_210_9 no reiniciaron el 31/10 segun telemetria (cpe_200_80 si reinicio el 30/10 a las 21:51 y 22:18; cpe_210_9 arranco por ultima vez el 29/10 a las 02:30). [UNKNOWN]

## Banco (tarjetas, gate del operador; nada ejecutado)
Radios de banco ocupados (LAP .20, Loco .117, PBE .241/.242 en W457; LiteBeam .116 en W460; LTU en W467): no se tocaron.
1. #236: LiteBeam bench. Leer chan_nf_0 (pdev stats CT) y RSSI de una estacion 60 s en reposo. Sin umbral nuevo: decidir solo con A/A.
2. mac80211: build de bench con 3b4d27acaf y 586c628c0b sobre backports 6.12.52. A/B con la induccion de crash de 3116A; contar recuperaciones, skb drops y tiempo a trafico.
3. Inactividad: medir el tiempo a deauth de un cliente que anuncia BSS Max Idle Period en PtP bench (#25416). Sin cambio de max_inactivity en produccion.

## Reglas y cierre
- Solo lectura: 0 escrituras; sin credenciales; sin IP ni MAC en este doc (los nodos se citan por ID de registro).
- Omitido: no compile nada, no revise el diff de mac80211 fuente por fuente, no consulte MemoryMaster. Riesgo: los candidatos 1 y 2 pueden afectar el RSSI y el recovery de nuestros nodos; sin medicion no se puede decir cuanto.
