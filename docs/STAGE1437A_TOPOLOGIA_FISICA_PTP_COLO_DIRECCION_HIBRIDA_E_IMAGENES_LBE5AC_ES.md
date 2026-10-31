<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: SUPERSEDED (W435, 31/10): the operator confirmed on 30/10 that the PtP-Colo link is 450 m (the airOS reading); the 1811 m GPS figure is superseded, see STAGE3098A. Stage 1437A (ES): topología física del PtP-Colo (ptp-colo-ap 198.18.0.91 / ptp-colo-sta 198.18.0.92, LiteBeam 5AC Gen2 0xe7f9) con el extremo de Edificio Principal INFERRED y no CONFIRMED, ether10-colo/192.168.27.x frente al br0 de los radios, dirección híbrida A (AP OpenWrt, STA airOS) contra B (AP airOS, STA OpenWrt) con sus filas de evidencia, las tres imágenes OpenMax LBE5AC (public_release, v3, v4) con hashes reales y qué las bloquea (988A), y lo que implican para una primera prueba híbrida; fuentes: recibos 1434A, 1435A y 1436A -->
# Stage 1437A: topología física, dirección híbrida e imágenes LBE5AC del PtP-Colo

Estado: `DOC_NOT_EXECUTED`. Es una síntesis offline de tres recibos y de archivos del repo: no tocó ningún radio, router ni switch, y no autoriza ningún cambio. Toda mutación de producción es del operador.
Etiquetas: CONFIRMED / INFERRED / UNKNOWN / REFUTED. Clases: CONFIRMED_LIVE_HARDWARE, CONFIRMED_STATIC_BINARY, SIMULATED_MODEL_ONLY, HYPOTHESIS, OFFLINE_ARTIFACT_INFERENCE.
Recibos fuente: `artifacts/verification/stage1434a_ptp_colo_physical_end_and_mac_topology.json`, `artifacts/verification/stage1435a_hybrid_direction_a_vs_b_evidence_audit.json`, `artifacts/verification/stage1436a_openmax_lbe5ac_image_variants_dissection.json`.
Contexto previo: `docs/STAGE1388A_CHECKLIST_UNIFICADO_PTP_COLO_105_62_54_INFRA_Y_BACKUP_MTD_ES.md` (checklist, veredicto NOT_READY), `docs/STAGE1335A_CANDIDATOS_LITEBEAM_EDIFICIO_PRINCIPAL_Y_PRUEBA_HIBRIDA_STOCK_OPENWRT_ES.md` (candidatos y prueba híbrida) y `artifacts/verification/stage1386a_hybrid_interop_509a_vs_105a_and_image_sha_reconciliation.json` (veredicto REFUTED_AS_STATED).

## 1. Topología física del PtP-Colo (1434A)

Identidad, CONFIRMED a la hora de captura (lectura de solo lectura de 1344A, recalculada desde los volcados crudos y el mtd4 decodificado):

| Extremo | IP | Rol | Placa | MAC de br0 | Puerta de enlace |
| --- | --- | --- | --- | --- | --- |
| `ptp-colo-ap` | 198.18.0.91/30 | `ap-ptp-ac`, `radio.1.mode=master` | 0xe7f9 LiteBeam 5AC Gen2, WA.v8.7.25 | PUBLIC_DEVICE_0069 | 198.18.0.120 |
| `ptp-colo-sta` | 198.18.0.92/30 | `sta-ptp-ac`, `radio.1.mode=managed` | 0xe7f9 LiteBeam 5AC Gen2, WA.v8.7.25 | PUBLIC_DEVICE_0070 | 198.18.0.121 |

Cada radio ve al otro como su único par asociado (la MAC de `ath0` del vecino aparece en `wstalist`). Los radios son puentes transparentes: `br0` = `eth0` + `ath0`, STP apagado, sin dispositivos VLAN, WDS habilitado.

### 1.1 Qué extremo está en Edificio Principal

Veredicto del recibo: `ptp-colo-ap` (198.18.0.91) en Edificio Principal, lado MK2-RS, y `ptp-colo-sta` (198.18.0.92) en el sitio remoto COLO. Etiqueta: INFERRED, confianza MODERATE, `confirmed` false. NO es CONFIRMED: ninguna tabla de MAC aprendidas, ARP o bridge host de MK2-RS nombra una MAC de estos radios (recomprobado: ninguna MAC de los radios aparece en la captura de MK2-RS).
Evidencia que sí coincide (clase OFFLINE_ARTIFACT_INFERENCE):
1. Coordenadas configuradas: las del AP coinciden con los otros 21 dispositivos archivados en el sitio UISP EDIFICIO-PRINCIPAL (a menos de 0,5 km); las del STA quedan a unos 1,81 km y ningún otro dispositivo del sitio está cerca. Recuento independiente igual al del recibo. `gps.fix=0`: son valores cargados a mano, no un fijo satelital.
2. Asimetría de bytes: el contador de `ether10-colo` en MK2-RS es muy pesado hacia adentro (de 26 a 52 Mbps entrantes contra 1,3 a 1,8 salientes) y en los radios el flujo pesado va de la LAN del STA hacia el aire y a la LAN del AP (cociente cercano a 15,6 y 14,6). Es evidencia direccional, no una medida igualada.
3. Debilísima: el AP tiene 20 m de cable y altura 50 m con antena integrada de 23 dBi; el STA, 0 m y 6 dBi.
Contraevidencia: UISP archiva ambos extremos bajo EDIFICIO-PRINCIPAL (archivar no es cablear); las coordenadas propias de MK2-RS no están en ningún recibo, así que "local a MK2-RS" descansa en `AGENTS.md`; la etiqueta de operador `COLO-STA-PRINCIPAL` estaba sobre 198.18.0.122, que 1344A prueba que es un CPE de cliente.
Falta para CONFIRMED: en MK2-RS, `/ip arp print where interface=ether10-colo` y la tabla `switch host` (ether10-colo es un puerto del chip switch2, no miembro de `bridgeLAN`); en cada radio, `brctl showmacs br0` e `ip neigh`, para ver qué puerto (`eth0` o `ath0`) aprendió la MAC PUBLIC_DEVICE_0071 de `ether10-colo`. Ninguno de esos comandos está entre los 14 de 1344A.

### 1.2 ether10-colo, 192.168.27.x y br0

- MK2-RS tiene sobre `ether10-colo`: 198.18.0.121/30 (comentario "PTP colo"), 198.18.0.120/30 y 198.18.0.123/24. Las puertas de enlace de los dos radios (.61 y .53) son direcciones propias de MK2-RS en ese puerto: CONFIRMED a nivel de configuración IP (`artifacts/verification/infra_wan_colo_mangle_and_route_audit.json`, ids `*155E3`, `*155E4`, `*155E8`).
- Los radios no llevan ninguna dirección 192.168.27.x: su `br0` solo tiene la IP de gestión /30. El tráfico 192.168.27.x sería L2 puro que entra por un `eth0` y cruza el puente y el aire hacia el otro `eth0`. Veredicto: INFERRED que atraviesa los `br0` si 198.18.0.119 está detrás del radio lejano; UNKNOWN de qué lado están los hosts 192.168.27.x (ninguna tabla fdb o ARP de radio fue capturada).
- Neighbors de MK2-RS en `ether10-colo`: ninguno. El ARP del Infra (198.18.0.122 alcanzable, .51 falló, ambos en `bridgeLAN`) describe el CPE de cliente refutado, no este par.
- Cableado concreto (qué radio está enchufado a `ether10-colo`): UNKNOWN.

### 1.3 Distancia y coordenadas (redondeadas a 3 decimales)

Coordenadas redondeadas del AP -33.895 / -60.576 y del STA -33.887 / -60.592. Distancia haversine desde esos valores redondeados: 1,724 km; con las coordenadas completas del cfg: 1,811 km (diferencia de redondeo). El `distance` de airOS es 450 m en ambos y el `ackdistance` 600 m: no coinciden con el GPS (cuatro veces menos), y no se resuelve aquí.

## 2. Dirección híbrida A contra B (1435A)

Definición: dirección A = AP OpenWrt con STA airOS 8 stock. Dirección B = AP airOS 8 stock con STA OpenWrt. El PtP-Colo es una B si se convierte solo el extremo remoto, y una A si se convierte solo el AP.

### 2.1 Dirección A (AP OpenWrt, STA airOS 8)

| Id | Rig y qué funcionó | Mecanismo | Clase | Fuente |
| --- | --- | --- | --- | --- |
| A01 | Banco LAP-120 OpenWrt con Loco 5AC stock WA.v8.7.25: asocia, WPA2, ping 0 % de pérdida y TCP medido (78,7 UL / 63,6 DL a 20 MHz) | parche de mac80211 del AP más parche del CPE (alcance histórico 2026-10-18) | CONFIRMED_LIVE_HARDWARE | `docs/STAGE10_STOCK_AIROS8_INTEROP_AND_REVERT.md:75` |
| A02 | Run17: STA stock asociado 71,7 s, ping bidireccional, sin throughput | admisión por IE de proveedor (pulso) | CONFIRMED_LIVE_HARDWARE | `artifacts/canary_panel1_guarida/root_goal_direct_association_20261022_run17/receipt.json:352` |
| A03 | Run25: WA y XC stock a la vez, 61 s, doble ping bien | igual a A02 | CONFIRMED_LIVE_HARDWARE | `artifacts/canary_panel1_guarida/root_multi_cpe_20261022_run25/receipt.json:21348` |
| A04 | Cuatro CPE a la vez, 64/64 pings cada uno | igual a A02 | CONFIRMED_LIVE_HARDWARE | `artifacts/canary_panel1_guarida/root_four_cpe_result_20261022.json:676` |
| A05 | AP de producción Panel1 con un CPE stock listado como admitido; sin prueba de unicast ni goodput medido | admisión sin toque | solo radiografía | `artifacts/canary_panel1_guarida/guarida_32cpe_radiography_20261024.json:9` |
| A06 | Canary de producción anterior rechazado, restaurado | n/a | CONFIRMED_LIVE_HARDWARE (negativo) | `artifacts/canary_panel1_guarida/panel1_cutover_result_20261019.json:2` |
| A07 | Estático: STA con `is_ubnt_ptp=1` y `allow_80211=1` entra a un AP WDS estándar pero manda `polling_enabled=0` | `ubnt_poll_host.ko` | CONFIRMED_STATIC_BINARY | `artifacts/autoresearch/stage111a_airos8_ptp_eapol_timeout_re.json:51` |

Veredicto A: hay recibos vivos de un STA stock WA.v8.7.25 que asocia y contesta ping bidireccional durante 60 a 72 s contra un AP OpenWrt con parche y truco de IE. NO está mostrado: este par LiteBeam, un AP sin parche ni estabilidad de varios días. Los rigs A son CPE PtMP (`sta-ptmp-ac`, Loco), no un STA `sta-ptp-ac` como el del PtP-Colo; para ese caso solo existe el análisis estático de 138A (INFERRED que un STA PtP stock no pasa datos con un AP OpenWrt).

### 2.2 Dirección B (AP airOS 8, STA OpenWrt)

| Id | Rig y qué falló o funcionó | Mecanismo | Clase | Fuente |
| --- | --- | --- | --- | --- |
| B01 | Banco PBE 5AC Gen2: AP stock, STA con OpenWrt 24.10.4. Asocia (AID 1), 4-way WPA2 completo y recibe el ARP de difusión, pero el AP descarta el unicast del STA, también con `uph_op_mode=0` y 4addr 0 y 1 | `ubnt_poll_host.ko` intercepta el camino de datos | CONFIRMED_LIVE_HARDWARE (negativo) | `docs/STAGE105A_PBE5AC_GEN2_REMOTE_OTA_PTP_CONVERSION_AND_AB_BENCHMARK.md:41` |
| B02 | Mismo par antes de flashear: airOS contra airOS con `allow_80211=1` y `wds 1`, 45 s sin pérdida (no es la pregunta) | perillas de `umac` | CONFIRMED_LIVE_HARDWARE | `docs/STAGE68A_PBE5AC_HYBRID_OTA_READINESS_AND_V5_AUTORESEARCH.md:23` |
| B03 | 0 apariciones de `allow_80211` y `op_mode` como perillas de `ubnt_poll_host.ko`; `hybrid_path_confirmed` en 0 | estático | CONFIRMED_STATIC_BINARY | `docs/STAGE1159A_UPH_ALLOW_80211_OP_MODE_0_HYBRID_OTA_RE.md:117` |
| B04 | Plan de comandos sin ejecutar | n/a | HYPOTHESIS | `docs/STAGE1110A_PTP_HYBRID_AIROS8_TO_OPENWRT_OTA_VALIDATOR.md:1` |
| B05 | Par PtP-Colo: AP en 6035 MHz; un STA OpenWrt no puede sintonizar sobre 5865 MHz | tabla de canales de ath10k | OFFLINE_ARTIFACT_INFERENCE | `artifacts/verification/stage1346a_ptp_colo_openwrt_lbe5ac_staged_profile.json:69` |
| B06 | Runbooks que suponen `allow_80211` y `op_mode` como claves de cfg | n/a | HYPOTHESIS | `docs/STAGE1131A_GUARIDA_AND_PTP_PRODUCTION_ROLLOUT_RUNBOOK_ES.md:35` |
| B07 | Estático inverso: AP OpenWrt con STA stock | n/a | CONFIRMED_STATIC_BINARY | `artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json:2` |

Veredicto B: REFUTED_AS_STATED / NOT_FOUND como camino que funcione, igual que 1386A. El único test vivo (B01) es negativo y ningún recibo lo muestra arreglado. Los 14,62 Mbps de 105A son OpenWrt en ambos extremos, no una dirección híbrida.

### 2.3 Qué dice el system.cfg de los dos radios (mtd4 decodificado)

| Clave | AP .62 | STA .54 |
| --- | --- | --- |
| `radio.1.mode` | master | managed |
| `radio.1.ptpmode` | 1 | enabled |
| `radio.1.polling` | enabled | enabled |
| `wireless.1.wds.status` | enabled | enabled |
| `netmode` | bridge | bridge |
| `radio.1.ieee_mode` | 11acvht20 | auto |
| `radio.1.freq` | 6035 | 0 (lista de exploración) |
| `radio.1.countrycode` | 511 | 511 |

- Puede decir: ambos radios están en modo PtP airMAX con polling y WDS; el AP fija 6035 MHz y 20 MHz y el STA busca en una lista; los valores no secretos coinciden con el decodificado propio.
- No puede decir: ninguno de los dos cfg tiene las claves `allow_80211` ni `op_mode`, así que esas perillas son de tiempo de ejecución y no se persisten; tampoco dice nada del cableado físico ni de la frecuencia viva del STA. El mtd4 del STA difiere del cfg vivo en `radio.1.scan_list.channels` (cambio sin guardar). Los valores secretos (clave WPA, contraseñas, comunidad SNMP) no se copian: solo los nombres de las claves.

## 3. Las tres imágenes OpenMax para LiteBeam 5AC Gen2 (1436A)

Hashes recalculados desde disco (12 hex), directorio `firmware/openwrt/pbe5ac_gen2_ptp_kit/`:

| Variante | factory (6947480 bytes) | sysupgrade | Agrega sobre la oficial | mac80211.ko |
| --- | --- | --- | --- | --- |
| `public_release` (v1, 132A) | `97ae94bf5a11` | `3c923b94a3a8` | 5 archivos (admitter, init, qos, release, uci-default) más `/etc/openmax` | parche TEB, 71 bytes cambiados, `3e3d812ff0d4` |
| `public_release_v3` (144A) | `c96b493b60bd` | `c66e2baf428d` | v1 más perfil "champion" (hotplug, init, champion.conf con enabled=0): 8 archivos | TEB más 4addr con compuerta, 113 bytes, `fe4f730fccaa` |
| `public_release_v4` (170A) | `4a5d61eafb24` | `09a6ead882ed` | v3 más `champion-v2.json` y hotplug reescrito: 9 archivos | el mismo de v3 |

- Los prefijos del enunciado (`97ae94bf5a11`, `c96b493b60bd`, `4a5d61eafb24`) coinciden con el disco; la oficial stock es `dafd701bc80f` (6881944 bytes). Los tres factory tienen el mismo tamaño.
- Qué son: la imagen oficial OpenWrt 24.10.4 ath79 para LiteBeam AC Gen2 con el kernel idéntico byte a byte y el rootfs SquashFS reconstruido: rootfs oficial más los archivos agregados y un `mac80211.ko` parcheado. Contenedor OPEN/ENDS sin firma de proveedor; el sysupgrade lleva un trailer "fake certificate".
- Las tres re-extraídas aquí con `sqfs2tar` local: las listas de archivos agregados y cambiados coinciden con el recibo.
- Reproducibilidad: los 20 pares factory/sysupgrade de `public_release*` y sus `_repro` son idénticos byte a byte (recalculado). Eso prueba que el empaquetado es repetible, no que las imágenes arranquen.
- Cuál encaja con 0xe7f9: solo las seis imágenes `lbe5ac-gen2` (tres factory y tres sysupgrade), cuyo kernel descomprimido contiene el DTB `ubnt,litebeam-ac-gen2` (recomprobado con un decodificador LZMA propio). Las de pbe5ac, lap-120 y nanostation en los mismos directorios son de otras placas. El mapeo 0xe7f9 a ese DTB viene del catálogo del operador, no de un volcado mtd.
- Evidencia de flasheo en vivo: ninguna. No existe recibo de flasheo ni de arranque de ninguna imagen LiteBeam. El único flasheo vivo del repo (105A) usó imágenes del kit para PowerBeam (0xe3d6) y esos archivos ya no están en disco con los hashes que cita el doc.

### 3.1 Por qué 988A dice BLOCKED y qué sí existe

`docs/STAGE988A_SQUASHFS_WATCHDOG_AND_REPO_HYGIENE_GATE.md:17` y `docs/STAGE983A_SQUASHFS_FACTORY_FAIL_CLOSED_CONTRACT.md:21` dejan `native_image_emission` NOT_EXECUTED y `packaging_readiness` BLOCKED por tres motivos del JSON de 983A: bootstrap activo revisado, toolchain nativo local con hash y base fijada con árbol de payload completo.
- Bloqueado, con precisión: la emisión de una imagen NUEVA por la tubería B (`firmware/openwrt/build_universal_pbe5ac_lbe5ac_openwrt_factory.py`) que lleve el payload FMX PtP (uci-default `99-fmx-pbe5ac-ptp`, watchdog de rollback, transacción de runtime). Exige POSIX con root y `mksquashfs`/`unsquashfs` con hash; este checkout es Windows y no tiene ninguno; el bootstrap del kit es un stub "Legacy actuator retired".
- Existe: las 20 imágenes públicas, emitidas el 2026-10-26 por la tubería A (`firmware/openwrt/pbe5ac_gen2_ptp_kit/build_public_openmax_release.py` con squashfs-tools-ng fijado por sha256), con otro payload público y solo por cable. No se re-ejecutó la tubería A (si correría hoy: UNKNOWN).
- No contradice: son dos tuberías. La redacción de 988A y de 983A no nombra la tubería B, y 1386A repite "BLOCKED" sin calificar; un lector puede concluir mal que no existe ninguna imagen utilizable. Lo cierto: no existe una imagen con watchdog y perfil PtP-Colo.

### 3.2 Riesgos de las imágenes públicas para una primera prueba (todos CONFIRMED_STATIC_BINARY)

- Wireless apagado: radio `disabled=1` y una sola interfaz `openmax` deshabilitada, sin canal, país ni htmode. Una unidad remota flasheada sin cable queda con LAN 198.18.0.50/24, sin DHCP y sin radio: solo se recupera con acceso cableado. Esto choca con la regla de `AGENTS.md` de no pedir acceso físico al extremo remoto, y 988A no lo menciona.
- Ninguna imagen impone el tope de 5865 MHz: el canal, el ancho y el país los fija el operador tras habilitar el radio.
- El admitter público (1318 bytes) solo une al `br-lan` las interfaces WDS de hostapd; no contiene la lógica de admisión sin IE que los docs del kit atribuyen a "admitter v2" (relevante para la dirección A).
- Ningún `mac80211.ko` parcheado tiene recibo de ejecución en hardware. El preflight `tools/deploy/verify_litebeam_edificio_principal_hybrid_preflight.py:935` con `--auto-image` elige la variante v1, la más vieja; hay que elegir por sha completo y directorio, no por nombre de archivo (los tres comparten nombre).

## 4. Consecuencias para la prueba del PtP-Colo

- Step-0 sigue bloqueando (1387A, compuerta G5 BLOCKER): el enlace opera a 6035 MHz y OpenWrt con ath10k no sintoniza sobre 5865 MHz. Mover ambos extremos airOS a un canal de la tabla es una mutación de un enlace de producción (la subida WAN de COLO) y es decisión del operador, con ventana y relevamiento de espectro. 5865 es necesario, no suficiente.
- Una primera prueba híbrida (dirección B: AP .62 airOS, STA .54 con una imagen LBE5AC) mostraría, como mucho, si un AP airOS 8 stock pasa unicast de un STA OpenWrt en este par; B01 sugiere que no. NO mostraría estabilidad, throughput, la dirección A, el extremo físico ni rollback (ninguna imagen trae watchdog).
- Pasos exclusivos del operador, ninguno ejecutado aquí: ventana de mantenimiento; drenaje de los mangles de MK2-RS según 1388A; Step-0; elegir una imagen por sha completo; acceso cableado para el primer flasheo; rollback revisado.
- Si el extremo de Edificio Principal es el AP (INFERRED), el STA remoto es el que habría que flashear sin cable, que es justo el caso que las imágenes públicas no resuelven.

## 5. Contradicciones halladas por los sub-agentes (archivo:línea)

- 1388A afirma que ningún recibo ata `ether10-colo` al par: `docs/STAGE1388A_CHECKLIST_UNIFICADO_PTP_COLO_105_62_54_INFRA_Y_BACKUP_MTD_ES.md:137`; la tabla de direcciones de MK2-RS sí los ata a nivel IP: `artifacts/verification/infra_wan_colo_mangle_and_route_audit.json:5769`.
- Ambos extremos figuran bajo EDIFICIO-PRINCIPAL: `artifacts/verification/stage1332a_edificio_principal_ptp_candidates.json:641` y `:663`, pero el GPS los separa 1,8 km.
- `distance` de airOS 450 m contra 1811 m de GPS: `artifacts/backups/ptp_colo_10_10_105_62/radiography/mca_status.txt:26`.
- STA con cambio sin guardar: `artifacts/backups/ptp_colo_10_10_105_54/radiography/cat_tmp_system_cfg.txt:98` (carpeta ignorada por git).
- El nombre de archivo de 1347A conserva "51_50": `docs/STAGE1347A_RADIOGRAFIA_Y_BACKUP_MTD_PTP_COLO_51_50_LISTO_PARA_PRUEBA_ES.md:13`.
- 988A y 983A, redacción sin calificar: `firmware/openwrt/build_universal_pbe5ac_lbe5ac_openwrt_factory.py:435`.
- El manifiesto del kit describe un comportamiento ausente del archivo: `firmware/openwrt/pbe5ac_gen2_ptp_kit/conversion_kit_manifest.json:16`.
- 105A cita hashes de imágenes (`709c0dbf9ef2`, `810cf6a1b9ed`) que ya no coinciden con los archivos del kit: `docs/STAGE105A_PBE5AC_GEN2_REMOTE_OTA_PTP_CONVERSION_AND_AB_BENCHMARK.md:31`.
- Datos personales: 1344A y 1347A incluyen el nombre de un cliente (CPE refutado); esta etapa no lo copia, y conviene limpiarlo en esos archivos.

## 6. Qué NO está probado

- Qué radio está cableado a `ether10-colo` y por tanto cuál extremo está en Edificio Principal: solo INFERRED (GPS y asimetría de bytes); ninguna tabla de MAC aprendidas fue leída.
- Que el tráfico 192.168.27.x cruce los `br0` de los radios.
- Que un AP airOS 8 stock pase unicast de un STA OpenWrt (dirección B) en este par o en cualquiera; que la dirección A sirva con un STA PtP stock.
- Que alguna imagen LBE5AC (v1, v3, v4) arranque, asocie o pase tráfico en un LiteBeam real; ninguna fue flasheada según el repo.
- Que los `mac80211.ko` parcheados funcionen en hardware; el valor de los parámetros de tiempo de ejecución de `allow_80211` y `op_mode`.
- Que la tubería A pueda reconstruir hoy las imágenes; que exista una imagen OTA-segura con watchdog (no existe).
- El estado actual de radios y router: todo es de la hora de captura de cada recibo.
