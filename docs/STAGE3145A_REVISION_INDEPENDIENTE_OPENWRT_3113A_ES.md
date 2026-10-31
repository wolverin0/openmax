<!-- doc-head: Stage 3145A (W474) ES: revision independiente de los 13 hallazgos de STAGE3113A contra sus fuentes primarias (gh api y raw GitHub, release notes, lista openwrt-announce), sin anclarse al autor; resultado: 13 CONFIRMED de fuente (autor 11 CONFIRMED y 2 PARTIAL), los 3 subclaims UNVERIFIABLE (sqm-scripts use_mq, cake-autorate cake_mq, builds ppe-nss 29/10) pasan a CONFIRMED; aplica: 0 SI de rendimiento, 4 PARTIAL (6, 7, 10, 13), 9 NO; correccion a STAGE3116A: fcbdb70 tambien lleva los 3 fixes a la carpeta ath10k-6.18, pero 25.12.6 fija bb84e159 sin ellos; omision de aplicabilidad: 24.10.5 a 24.10.8 existen con el mismo driver ath10k-ct y no se consideraron; watch firewall4 a3296754 revertido el 29/10 -->
Que cubre: metodo, tabla de 13 filas (etiqueta del autor y del revisor con la linea exacta de la fuente), subclaims de #4/#10/#12, parciales #6/#11, reconciliacion con 3116A, la omision 24.10.5-24.10.8, erratas y conteo.
Estado: SOLO LECTURA / ESCRITORIO. 0 SSH, 0 banco, 0 harness, 0 escrituras en equipos o en GitHub. Fuentes leidas el 31/10/2026 entre 19:00 y 19:50 UTC.
Entrada: research/inbox/2026-10-31-openwrt-mejoras-ultimo-ano.md (sha256 1f8cf72a...e594, recalculado, coincide), STAGE3113A (sha256 4d4d1720...ae7f) y STAGE3116A (sha256 a7f5e342...50ff), ambos sin cambios desde el cierre de Mission Control.
Leer cuando: antes de citar una fila de 3113A, de decidir entre 24.10.8, 24.10.4 con backport o 25.12.x, o de tocar flow offload.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

## 1. Metodo
- Cada fila se abrio en su fuente primaria, no en las notas del vault: `gh api` (PR, issue, commit, compare, releases, reviews, timeline, actions) y `raw.githubusercontent.com` por tag. La lista de correo se leyo por HTTPS.
- Pertenencia de un commit a una version: `compare <commit>...<tag>`; `ahead` = incluido, `diverged` = no incluido.
- La etiqueta certifica que la fuente dice lo que afirma la nota, no que la afirmacion sea cierta en el mundo (leccion de la nota 669). Las cifras autoinformadas (#3, #11, #12) quedan como autoinformadas.
- Dos etiquetas por fila: fuente (CONFIRMED, PARTIAL, REFUTED, UNVERIFIABLE) y aplicabilidad a openMAX (SI, PARTIAL, NO). Base verificada en el repo: imagenes 24.10.4 r28959, kernel 6.6.110 (profiles.json), `kmod-ath10k-ct-smallbuffers`, kits sin `flow_offloading_hw`, CPE y AP con `psk2`.
- MemoryMaster estaba desconectado: <memorymaster-id>, <memorymaster-id> y <memorymaster-id> no se pudieron leer.

## 2. Tabla de los 13 hallazgos
| # | Hallazgo | Autor | Revisor (fuente) | Linea exacta de la fuente primaria | Aplica (autor / revisor) |
| --- | --- | --- | --- | --- | --- |
| 1 | Rust tier-1 (PR #22748) | CONFIRMED | CONFIRMED | PR: merged_at 2026-10-30T10:08:05Z, merge a1788e6, base main. Body: "The mips and mipsel triples of rustc are soft-float"; probado solo "on mipsel (ramips/mt7621)", no ath79 | NO / NO |
| 2 | PPE qca_ppe/qca_edma (PR #24806) | CONFIRMED | CONFIRMED | merged_at 2026-10-26T08:45:08Z; comentario robimarko 08:45:34Z "Lets see what explodes"; body "No NSS firmware, no ECM and no new uAPI are involved."; compare c7924dc...v25.12.6 = diverged | NO / NO |
| 3 | PPE + CAKE + L4S (#26177, sqm-scripts #196) | CONFIRMED | CONFIRMED | #26177 draft=true, abierto desde 25/10; sqm #196 draft=true, desde 24/10. #26177: "Shaping 310 Mbit/s of download on the AX3600"; sqm #196: "Measured on a Xiaomi AX3600 (IPQ8074)". Archivos: 6 en pending-6.18, 1 en hack-6.18 | NO / NO |
| 4 | cake_mq en 25.12 (dd79feb) y #22344 | CONFIRMED + 1 UNVERIFIABLE | CONFIRMED (subclaim pasa a CONFIRMED) | dd79feb "kernel: add cake-mq support", backport-6.12/700-01..07; ahead en v25.12.0 y v25.12.6, diverged en openwrt-24.10. #22344 abierto, rpodric 19/10 00:30Z "Still a known issue". Known issues 25.12.6: "SQM CAKE MQ (`cake_mq`): throughput may be unexpectedly low on some configurations." | NO / NO |
| 5 | PPPoE (74bf368) | CONFIRMED | CONFIRMED | "kernel: backport pppoe improvements": 621 percpu netstats, 622/623 remove rwlock, 624 drop sock refcount, 625 TX scatter-gather, 650 GRO; ahead en v25.12.0 y .6, diverged en 24.10 | NO / NO |
| 6 | ath10k-ct estable vs main | PARTIAL | CONFIRMED | Makefile v25.12.6: l.11 `PKG_SOURCE_DATE:=2025-12-01`, l.12 bb84e159, l.18 `CT_KVER="-6.18"`. Main: l.11 2026-07-31, l.12 fcbdb70, l.18 `-7.2`. fcbdb70: "Pull in upstream stable changes and bug fixes. In particular, this pulls in some guard logic" | PARTIAL / PARTIAL |
| 7 | mt76 25.12.2 y m2u 25.12.6 | CONFIRMED | CONFIRMED | 25.12.2: "mt76: fix severe WiFi latency regression (up to multiple seconds) on 2.4 GHz introduced in 25.12.1", "fix MT7996/MT7992 link handling during MLO station add/remove", "fix scan work requeue race with spinlock", "wifi-scripts: fix 160 MHz channel width configuration". 25.12.6: "wifi-scripts: the `multicast_to_unicast` option works again" | PARTIAL / PARTIAL |
| 8 | Mesh MT7996 con ath11k (mt76 #1132) | CONFIRMED | CONFIRMED | Abierto, creado 11/09. Body: "the BPI-R4 reaches plink `ESTAB` with all three ath11k nodes"; tabla "Mesh Peering Open, 217, 0". Review 28/10 08:42Z APPROVED: "The AX3600 (ath11k) peers on 2.4 and 5 GHz in all three cases." | NO / NO |
| 9 | Airtime MT7996 (PR #26037) | CONFIRMED | CONFIRMED | Abierto, creado 19/10 22:37Z, 0 reviews. Body: "If a WTBL airtime counter resets, subtracting the old cached value produces a huge airtime delta." | NO en tabla, PARTIAL en conteo / NO (solo leccion) |
| 10 | cake-autorate agosto y fork JMarty | CONFIRMED + 1 UNVERIFIABLE | CONFIRMED (subclaim pasa a CONFIRMED) | 4cf5c693 17/08 "Batch simultaneous shaper updates"; 2582dfff 24/08 "restart pingers on global ping timeout (#413)". JMarty README l.37 "The rate-control algorithm itself is upstream's and unchanged"; l.49-50 "tested it on one setup only — OpenWrt 25.12 (`apk`), a 5G WAN, a single instance" | PARTIAL / PARTIAL baja |
| 11 | Flowtable stale tras recrear Wi-Fi (#25646) | PARTIAL | CONFIRMED | Body l.3 "I used Claude (an AI assistant) to help dig into this"; "TP-Link Archer C7 v2", "25.12.5", "non-CT kmod-ath10k"; tabla "~310 Mbit/s" fresca contra "~135 Mbit/s" stale. Body l.9: "Software-only mode (`flow_offloading_hw=0`) lists the logical bridge devices and is not affected" | PARTIAL / NO hoy, con watch |
| 12 | Fork openwrt-ppe-nss | CONFIRMED + 1 UNVERIFIABLE | CONFIRMED (subclaim pasa a CONFIRMED) | README l.29-30 "The Xiaomi AX3600 is the test board. Other boards are built but not tested by the maintainer, and IPQ60xx is not tested at all."; wiki Benchmarks "Bridged, PC → Pi, v4, 941, 0.8" y "The Pi's 1 Gbit/s port is the ceiling."; SQM-and-QoS l.14 "Upload is a hardware `tbf` on the WAN port." | NO / NO |
| 13 | Base 25.12 | CONFIRMED | CONFIRMED | 25.12.0: "6.12.71 for all targets", "cfg80211/mac80211 from kernel 6.18.7", "Switch package manager from opkg to apk", "The Wi-Fi scripts were rewritten in ucode.", "We will not provide security updates for OpenWrt 24.10 after September 2026.", "Sysupgrade from 23.05 to 25.12 is not officially supported." Announce 000090: "Sun Oct 18 16:41:12 PDT 2026". 25.12.6: "Linux kernel: update to 6.12.112" | PARTIAL / PARTIAL (SI seguridad, NO rendimiento) |

## 3. Subclaims de #4, #10 y #12 (eran UNVERIFIABLE)
- **#4 "sqm-scripts desactivo cake_mq por defecto": CONFIRMED.** tohojo/sqm-scripts 20ba9263 (2026-02-25) "Default use_mq to off": "To be cautious, default use_mq to off for now." En `src/defaults.sh` queda `USE_MQ=0`. Es el tag v1.7.2 y es exactamente el `PKG_SOURCE_VERSION` de net/sqm-scripts en openwrt/packages openwrt-25.12 (24.10 trae 1.6.0, sin cake_mq).
- #4 "fairness no global entre instancias": CONFIRMED por #26177: "a host whose 4 flows landed on 4 queues took 76 of 100 Mbit/s against a host with 1 flow (84 with upstream cake_mq)". La parte de DiffServ es INFERRED: la arquitectura es por instancia y no hay una linea explicita.
- **#10 "integracion con cake_mq pendiente": CONFIRMED.** lynxthecat/cake-autorate #353 "FR: implement support for cake_mq" sigue abierto (ultima actividad 12/09). El PR #391 "detect a cake_mq root qdisc" se cerro sin merge el 17/08.
- **#12 "builds del 29/10": CONFIRMED (hora UTC).** El build vive en JuliusBairaktaris/Qualcommax_NSS_Builder:
  - La corrida 40801317948 del 2026-10-29T01:35:19Z compilo `xiaomi_ax3600`, ipq807x e ipq60xx, y termino con "Publish release" y "Prune old releases" en success. Las otras 3 corridas de ese dia no tenian cambios.
  - Hoy solo se listan releases del 31/10 porque la poda borra los viejos: que no aparezca no lo refuta.
  - Matiz: las 01:35 UTC del 29/10 son el 28/10 en hora ART. La pagina Benchmarks se creo el 20/10 (commit de wiki 3d88283), como ya decia el autor.

## 4. Parciales del autor (#6 y #11): por que cambian
- **#6, de PARTIAL a CONFIRMED.** El autor no veia el diff completo de fcbdb70. Ahora se leyo el commit: 75 archivos, 93585 lineas agregadas, casi todas por la carpeta nueva ath10k-7.2.
  - "Correcciones de RX": guarda NULL en `ath10k_htt_rx_netbuf_pop`, hunk `@@ -342` de htt_rx.c.
  - "Recuperacion": `ath10k_core_recovery_check_work` en `workqueue_aux`.
  - "Otros bugs": guarda de `ar` en `ath10k_wmi_tx_beacon_nowait` ("Crash was seen here after FW crash (1/4/2026)"); `else` en `ath10k_wmi_cmd_send` cuando la placa esta WEDGED; `peer_ps_state` bajo `data_lock`; free alineado en ce.c; `dump_mutex` en sdio; peer stats de wmi-tlv.
  - "Kernel no basta": 25.12.6 trae kernel 6.12.112 con mac80211 6.18.55, y 24.10.4 trae kernel 6.6.110 con mac80211 6.12.52.
  - Aplica PARTIAL: el hueco existe en nuestro 6.10, pero no hay evidencia propia de esos crashes en ath79 y QCA988x. El backport ya esta compilado en 3118A, sin probar en banco.
- **#11, de PARTIAL a CONFIRMED de fuente.** La nota dice exactamente lo que dice el issue: un solo equipo, autoinformado, redactado con IA y con el fix sin integrar. "DFS" figura en el issue como disparador posible, no probado.
  - Estado al 31/10: el PR del fix, #25650 "firewall4: refresh flowtable on Wi-Fi netdev add", esta cerrado sin merge.
  - Aplica NO hoy: la linea 9 del issue excluye `flow_offloading_hw=0`, nuestros kits no setean hw (grep 0) y los nodos son bridges L2.
  - Watch nuevo: firewall4 a3296754 (18/10, "fw4: list lower devices for software flow offloading") habria hecho que el modo software liste los puertos y quede expuesto al mismo problema. Se revirtio el 29/10 en e6f600c4 ("Fixes: #114" de firewall4).
  - Su mensaje cita el commit 871df5007eda de Linux: por un bridge solo se descarga el flujo cuyo dispositivo de entrada de abajo esta en la flowtable. Eso respalda que el offload en nuestros bridges es UNPROVEN. UNKNOWN si nuestro kernel 6.6.110 tiene ese commit.

## 5. Otras precisiones por fila
- **#7:** el m2u roto en 25.12.0-25.12.5 vino de 1682d876, "wifi-scripts: pass multicast_to_unicast as an integer" (cherry-pick de dc33d7bc): "so the option was a no-op".
  - Es exclusivo de 25.12: 24.10.4 no tiene `wireless-device.uc` (raw responde 404).
  - Nuestros kits escriben sysfs `brport/multicast_to_unicast` directo (por ejemplo tools/panel1/fmx_panel1_champion_persistence.sh:76), asi que el bug de UCI no los tocaba.
  - El item del checklist sigue: si se migra, usar 25.12.6 o posterior y releer el sysfs despues de un `wifi reload`.
- **#8:** el comentario del 27/10 de un tercero, que culpaba al parche de un atasco multicast por AQL, fue retractado por el mismo autor en la review del 28/10: "the multicast stall was not caused by this change". No citarlo como regresion. La causa era el camino rx de la NPU Airoha (mt76 #1169).
- **#9:** el unico comentario (20/10) dice "This needs to go to the Linux Wireless mailing list, not here": probablemente no se integre por OpenWrt. Para nosotros es solo una leccion para el exportador, con guarda de reset.
- **#5:** el mismo commit trae 626, "net: bridge: locally receive all multicast packets if IFF_ALLMULTI is set". Solo afecta bridges con snooping y ALLMULTI de odhcpd en relay. El kit v20 deshabilita odhcpd (99-fmx-wa-universal-champion-v20:13-14): N/A INFERRED, sin leer el estado vivo.
- **#3:** #26177 aclara "the CAKE patches apply to any target that runs CAKE", pero estan en pending-6.18, solo en main. No hay un Linux con CAKE en nuestro camino.

## 6. Reconciliacion con STAGE3116A
- CONFIRMED, igual que 3116A: 25.12.6 y la rama openwrt-25.12 al 31/10 fijan bb84e159 (2025-12-01). fcbdb70 es el unico commit posterior (compare: ahead_by 1). 25.12.6 sola no trae los 3 fixes.
- **CORRECCION:** "los 3 solo en 7.2" es incompleto. fcbdb70 tambien parchea la carpeta ath10k-6.18:
  - htt_rx.c +9: guarda NULL.
  - core.c y core.h: `recovery_check_work` y `INIT_WORK`.
  - mac.c: `cancel_work_sync` en `ath10k_stop`.
  - wmi.c: umbral 0x8000, guarda de `ar` y el `else` de WEDGED.
  - Ademas lleva la guarda de beacon a ath10k-6.11 y ath10k-6.15.
- Consecuencia: un 25.12.x que solo suba `PKG_SOURCE_VERSION` a fcbdb70, sin cambiar `CT_KVER="-6.18"`, recibe los 3 fixes sin parche propio. A la fecha ningun 25.12.x lo hace: sigue en watch.
- La carpeta ath10k-6.10 (la nuestra) no recibe nada de fcbdb70. En 24.10 el backport propio de 3116A y 3118A sigue siendo el unico camino (CONFIRMED).
- Las filas de la tabla 2 de 3116A que dicen "7.2" para el free alineado de ce.c, `peer_ps_state` bajo lock y el `else` de `cmd_send` estan tambien en 6.18, pero solo en fcbdb70.
- En los Limites de 3116A, "24.10 (6.12.96)" es el valor de la rama y de 24.10.8. v24.10.4 trae mac80211 6.12.52, como ya dice 3118A.

## 7. Omision de aplicabilidad: 24.10.5 a 24.10.8
- CONFIRMED (releases de GitHub): v24.10.5 2025-12-19, v24.10.6 2026-03-18, v24.10.7 2026-05-31 y v24.10.8 2026-07-26. Nuestras imagenes son 24.10.4 (2025-10-21): 4 service releases atras. Ningun doc de 3113A, 3116A, 3118A, 3119A ni del cierre las considera; 3118A fijo el feed en v24.10.4 a proposito.
- 24.10.8 dice "The OpenWrt 24.10 series is in security maintenance (only security problems are fixed), with end of life (EoL) projected for September 2026."
- 24.10.8 mantiene el driver: ath10k-ct `PKG_SOURCE_DATE:=2024-07-30` y firmware CT 2020.11.08. Siguen opkg y los scripts wifi en shell; cambian el kernel (6.6.144) y mac80211 (6.12.96).
- Lo que nos toca segun `default_packages` de profiles.json (dropbear, firewall4, libustream-mbedtls, odhcpd-ipv6only, wpad-basic-mbedtls):
  - dropbear: CVE-2025-14282 (24.10.5) y backports de 2026.90 (24.10.8). Aplica.
  - hostapd/wpa_supplicant, advisory 2026-1 (24.10.8). 25.12.6 aclara: "In client mode, wpa_supplicant is affected in general". Nuestros CPE son STA con `psk2`: aplica, INFERRED, sin explotar ni medir.
  - mbedtls 3.6.6 (24.10.7) y kernel 6.6.110 a 6.6.144: aplica en general. El detalle CVE por CVE no se hizo.
  - odhcpd, con CVE critico en 24.10.8: mitigado si el kit v20 lo deshabilito. INFERRED, estado vivo no leido.
  - LuCI, uhttpd y rpcd: no estan en `default_packages`, asi que N/A. UNKNOWN si alguien los instalo en campo.
- No es un riesgo nuevo: el known issue #14541 ("5GHz WiFi is non-functional on certain devices with ath10k chipsets", placas QCA9888 como la Archer C60) ya figura en las notas de 24.10.4.
- El fix de 24.10.8 "ath10k: skip WMI and beacon transmission when the device is wedged" es del ath10k upstream dentro de mac80211, no de ath10k-ct: N/A INFERRED.
- La rama openwrt-24.10 sigue recibiendo commits (29/10, kernel 6.6.159). UNKNOWN si habra 24.10.9.
- Efecto sobre la accion 1 de 3113A, no ejecutado y a decidir por el operador: existe un paso de seguridad de la misma serie, rearmar 2410_bp sobre el SDK y el ImageBuilder 24.10.8.
  - A favor: el driver no cambia, asi que el ledger de knobs no se invalida por driver, y el parche ath10k-ct deberia aplicar igual.
  - En contra: hay que recompilar el mac80211.ko TEB para 6.12.96 y kernel 6.6.144 (UNKNOWN si el parche aplica), y no extiende el soporte mas alla de septiembre de 2026.

## 8. Erratas de 3113A y 3116A (no editados aca, fuera de alcance)
- 3113A #6: "~16-17 meses atras de ambos" esta mal. Son 16 meses hasta bb84e159 (25.12.6) y 24 meses hasta fcbdb70 (main).
- 3113A #13: "6.12.71" es el kernel de 25.12.0; 25.12.6 corre 6.12.112.
- 3113A conteo: #9 figura NO en la tabla y PARTIAL en el conteo de aplicabilidad.
- 3113A Watch: el "commit firewall4 refresh flowtable" era el PR #25650, hoy cerrado sin merge. Reemplazar por firewall4 a3296754, e6f600c4 y #114.
- 3113A linea base: "fuera de soporte" es cierto para la serie, pero ademas faltan 24.10.5 a 24.10.8 (seccion 7).
- 3116A: la correccion "solo en 7.2" y el valor 6.12.96 de la seccion 6.

## 9. Conteo
- Fuente: 13 CONFIRMED, 0 PARTIAL, 0 REFUTED, 0 UNVERIFIABLE a nivel fila (autor: 11 CONFIRMED y 2 PARTIAL). Subclaims: los 3 UNVERIFIABLE del autor pasan a CONFIRMED; solo la parte DiffServ de #4 queda INFERRED.
- Aplica: 0 SI de rendimiento; 4 PARTIAL (6, 7, 10, 13); 9 NO (1, 2, 3, 4, 5, 8, 9, 11, 12). El autor contaba 6 PARTIAL: el #9 vuelve a NO, como su propia tabla, y el #11 pasa a NO por la linea 9 del issue.
- La conclusion de 3113A se sostiene: ninguna fila trae mas capacidad de radio para QCA988x. El valor esta en seguridad (13 y la seccion 7), estabilidad del driver (6) e higiene de telemetria (9 y 11).

## 10. Limites
- Solo lectura de fuentes publicas al 31/10/2026; PRs e issues abiertos pueden cambiar. Las marcas `updated_at` estan en el recibo.
- No se cruzaron CVE por CVE contra binarios instalados, no se leyo el estado vivo de ningun nodo y no se compilo nada.
- Recibo: artifacts/autoresearch/wave474_openwrt_independent_review.json. Gate: artifacts/verification/wave474_lane3_openwrt_review_gate.json.
