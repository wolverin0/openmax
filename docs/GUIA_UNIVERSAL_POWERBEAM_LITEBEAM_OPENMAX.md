<!-- doc-head: Public tester guidance through824A; board-specific profiles and qualified legacy setup/recovery retained -->
<!-- /doc-head -->

# Guía OpenMAX para testers WA / OpenMAX WA tester guide

## Current milestones through Stage824A / Hitos hasta Stage824A

This Stage825A update reconciles saved evidence; it adds no radio measurements or publication.
Esta actualizacion documental separa resultados reportados, empaquetado, simulacion y aceptacion fisica.

| Milestone | Source-qualified result and limit |
| --- | --- |
| WA v13 | Stage773A reported 78.51 Mbps peak TCP in VHT20 and -86.37% loaded p50 RTT; imported claims, not remeasured here. |
| PtP v4/v5 | Stage741A/v5 reported 25.47 Mbps peak TCP in VHT40; PBE-5AC-Gen2 and LBE-5AC-Gen2 have distinct board-specific profiles. |
| PB040 + PB050 + PB060 | Stage817A composed seven triple-patch SGMT payloads offline; byte/layout verification is CONFIRMED, target activation UNKNOWN. |
| LTU v20 | Stage774A reported 264 windows. Stage818A packages guarded br1 DHCP filtering tested with local command stubs; zero-rogue-DHCP runtime UNKNOWN. |
| Guarida v10 | Stage819A is an uncalibrated sensitivity/Pareto model, not measured tower capacity. The imported 514.80 Mbps claim belongs to Stage775A/v9. |
| Stage823A | Static strings in ubntspecd expose per-bandwidth BPS / SCORE / RATING labels; the numeric formula, coefficients and CPE-histogram combination remain UNKNOWN. |
| Stage824A | Static symbols locate the DFS classifier surface in ame_dfs.ko; numeric PW/PRI tables, detector criteria and LNA-saturation immunity remain UNKNOWN. |

Both PBE-5AC-Gen2 and LBE-5AC-Gen2 have CONFIRMED profile metadata; every revision's runtime compatibility remains UNKNOWN.
No universal compatibility, safe OTA conversion, zero-FP rate or production acceptance follows from these artifacts.
Attribution: Linux/mac80211/ath10k and QCA firmware for WA/PtP; Linux and proprietary airMAX/LTU module for LTU;
external controller for simulation, packaging and documentation. Static names alone do not establish algorithm behavior.
Source links are local evidence pointers; a privacy-filtered public selection may omit historical targets.
Sources: [WA v13](STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md), [PtP v5](STAGE741A_PBE5AC_LBE5AC_VHT40_PB050_PRODUCTION_BUNDLE_V5.md),
[triple patch](STAGE817A_UNIVERSAL_PB060_TRIPLE_PATCH_OPENWRT_AIROS_KIT.md), [LTU kit](STAGE818A_LTU_4096QAM_12X_LDPC_AND_SUPER4096_SAFE_KIT.md),
[model](STAGE819A_GUARIDA_TOWER_V10_TRIPLE_PATCH_AND_XW_MIXED_TDMA_PARETO.md), [825A source ledger](STAGE825A_PUBLIC_MILESTONES_THROUGH_824A.md).

Legacy public-v4 setup and benchmark qualifications remain below; the new milestones do not replace exact-board recovery requirements.

**ES:** Guía Stage 194A para candidatos públicos v4, basada en archivos guardados. La validación local de imágenes no demuestra boot, recuperación, enlace o rendimiento. **EN:** Stage 194A guide for public v4 candidates, based on saved files. Local image validation is not boot, recovery, link or performance acceptance.

## 1. Archivos y placa exacta / Files and exact board

Paquete / Package: [`firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v4/`](../firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v4/). Son ocho BIN: factory y sysupgrade por modelo. AP/STA son roles que configura el usuario; los formatos de instalación no son perfiles remotos AP/STA preconfigurados. There are eight BINs: factory and sysupgrade per model. Users choose AP/STA roles; installation formats are not preconfigured remote AP/STA profiles.

| Modelo / Model | Perfil exacto / Exact profile | Identificadores catalogados / Catalog aliases |
| :--- | :--- | :--- |
| PowerBeam 5AC Gen2 | `ubnt,powerbeam-5ac-gen2` | `0xe3d6` |
| LiteBeam 5AC Gen2 | `ubnt,litebeam-ac-gen2` | `0xe7f9` |
| LAP-120 | `ubnt,lap-120` | `0xe7f5`, `0xe8e5` |
| NanoStation 5AC Loco | `ubnt,nanostation-ac-loco` | `0xe7f7`, `0xe7fa` |

**ES:** Cada modelo conserva SU kernel/DTB oficial OpenWrt 24.10.4 / Linux 6.6.110. Los 31 registros históricos WA no equivalen a 31 placas físicamente aceptadas. No intercambiar imágenes, retaggear cabeceras ni extender estos aliases a otros modelos/revisiones. **EN:** Each model retains ITS official OpenWrt 24.10.4 / Linux 6.6.110 kernel/DTB. The 31 historical WA records do not establish physical acceptance of 31 boards. Do not interchange images, retag headers or extend these aliases to other models/revisions.

El módulo mac80211 v3 está fijado a 815640 bytes, ABI 352 y SHA256 `fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6`. Compartir vermagic no hace intercambiables otros módulos; WA no establece compatibilidad XC/XW. The module pin does not prove stock-airOS zero-touch interoperability or an RF gain.

Desde la carpeta del paquete / From the package directory:

```sh
sha256sum -c SHA256SUMS.txt
sha256sum -c SHA256SUMS
```

Estos archivos actuales reemplazan tablas de hashes de kits antiguos. Checksums verify content, not publisher identity or a vendor signature. Nunca forzar firmas, revisiones o particiones; verificar recuperación y backups antes de considerar una instalación. Never bypass signatures or write calibration/ART, factory/MAC storage, bootloader or environment.

## 2. Primer inicio cableado / Wired first setup

**ES:** v4 arranca con gestión `192.168.1.20/24`, DHCP/IPv6 RA y **Wi-Fi desactivados**. No incluye credenciales compartidas, gateway de un sitio ni watchdog de migración OTA. **Este kit público NO sirve como perfil automático de migración OTA remota.** Una instalación limpia puede cortar el único enlace remoto; conservar configuración tampoco valida una migración. **EN:** v4 starts at `192.168.1.20/24`, with DHCP/IPv6 RA and **Wi-Fi disabled**. It has no shared credentials, site gateway or remote OTA migration watchdog. **This public kit CANNOT be used as an automatic remote OTA migration profile.** A clean installation can disconnect the only remote link; retaining configuration does not qualify a migration.

Usar una unidad por vez en PoE cableado aislado. Crear contraseña propia, direcciones distintas, país/canal/ancho legales, SSID y clave WPA2 únicos antes de habilitar la radio. Use one unit at a time on isolated wired PoE. Set a unique password, distinct addresses, legal country/channel/width, SSID and WPA2 key before enabling the radio. La plantilla inactiva tiene WDS habilitado y no tiene clave; no incluye IEs de fabricante capturados. The inactive template enables WDS without a supplied key or captured vendor-IE identity.

## 3. FMX-DISC-42: orden remoto condicional / Conditional remote order

[Stage 138](../artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json) es **100% offline: RE binaria y simulación**, con `live_devices_touched=false`. It is **offline binary RE plus simulation**, not a bench-confirmed OTA recovery or migration. Su conclusión se limita a la ruta analizada de airOS 8 PtP; no es aceptación universal. Its conclusion concerns the analyzed airOS 8 PtP path, not universal hardware acceptance.

1. **ES:** Si la STA remota está en stock PtP (`is_ubnt_ptp=1`), conservar el AP compatible
en airOS mientras se prepara y convierte **primero la STA**. Esto exige otro perfil STA específico, previamente validado, con acceso, seguridad, red y recuperación conocidos; v4 público no lo aporta. **EN:** If the remote STA is stock PtP (`is_ubnt_ptp=1`), retain the compatible airOS AP while preparing and converting the **STA first**. This needs a separately validated STA profile with known access/security/network/recovery; public v4 does not provide it.
2. **ES:** Alternativamente, antes de migrar el AP, cambiar `radio.1.ptpmode=0` en la STA
mediante el procedimiento soportado, **APPLY**, y verificar nueva asociación y tráfico ARP/IPv4 bidireccional. Guardar el valor sin aplicarlo no cambia el modo de firmware activo. **EN:** Alternatively, before migrating the AP, set `radio.1.ptpmode=0` on the STA using the supported procedure, **APPLY**, then verify reassociation and bidirectional ARP/IPv4 data. Saving a value without applying it does not change the active firmware mode.
3. **ES:** Sólo después de probar acceso y datos de la STA, considerar la migración del AP
con recuperación y autorización propias. Si el modo o la conectividad son desconocidos, detener esa secuencia. **EN:** Only after verifying STA reachability and data should AP migration be considered, with its own recovery and authorization. Stop that sequence if mode or reachability is unknown.
4. **ES/EN:** Restaurar `vendor_elements`, usar `polling_enabled=0`, o completar EAPOL
no sustituye la apertura del camino de datos PtP ni prueba ARP/IPv4. Vendor IEs, `polling_enabled=0`, or successful EAPOL are not substitutes for verified data forwarding.

No se ejecutó aquí ningún cambio de modo, flash, reinicio o prueba OTA. No mode change, flash, reboot or OTA test was executed for this guide.

## 4. Resultados reportados y límites / Reported results and limits

Los titulares siguientes describen fuentes guardadas, **no ganancias nuevas del paquete v4**. These source-reported headlines are **not new gains demonstrated by public v4**.

| Fuente / Source headline | Calificación inmediata / Adjacent qualification |
| :--- | :--- |
| [Stage 161 R16](../artifacts/autoresearch/stage161a_live_wa_round16_18_autoresearch.json): `42.880 -> 48.748 Mbps`, **+13.68%** reportado / reported | Contraste corto de ajustes; no prueba causal del temporizador/distancia ni ganancia universal. Both coverage classes were 0; p99 worsened `118.926 -> 119.515 ms`. |
| [Stage 161/163](STAGE161A_LIVE_WA_ROUND16_18_AUTORESEARCH.md): 8 flujos / 8 flows, **+68.3%..+90.6%** reportado / reported | Comparación entre campañas: `22.611` frente a media `38.055` y mejor ventana `43.108 Mbps`. Cross-run/short-window comparison, **not independent VM causality**; the within-R17 reported mean contrast was +4.34%. |
| [Stage 162](../artifacts/autoresearch/stage162a_live_wa_e2e_forwarding_offload_benchmark.json): p95 E2E **-25.78%** reportado / reported | **UNPROVEN / NO DEMOSTRADO**: auxiliary ping fields contain `999` sentinels with `samples=1`; no actual flowtable activation is demonstrated, `offload_active=UNKNOWN`. |

Stage 163 consolida propuestas; no vuelve independientes los ensayos anteriores. Stage 163 consolidates requested settings; it does not make the earlier observations independent. `nf_conntrack_max` no prueba offload y RPS mask 1 no prueba paralelismo entre CPU. `nf_conntrack_max` does not prove offload; RPS mask 1 does not prove multi-CPU execution. La evidencia v4 conserva 18 comparaciones RF/72 ventanas y 1 E2E/4: poblaciones distintas, 76 guardadas. v4 retains 18 RF comparisons/72 windows plus 1 E2E comparison/4 windows: distinct populations, 76 saved windows. La regresión de colas de R12 y discrepancias de getters siguen abiertas. R12 tail regressions and getter discrepancies remain qualified.

## 5. Ajustes experimentales y prueba propia / Experimental settings and own test

`enabled`, `distance_enabled`, `forwarding_enabled` y `fq_pacing_enabled` empiezan en 0. All four switches start at 0. Desired configuration is not a successful actuator/getter. Requests include VM 4096 KiB, AQL 4000, distance 300 m, pacing 110/150, initial_quantum 3028, packet_steering 1, flow_offloading 1 and conntrack 16384. No elegir distancia/potencia por una tabla: adecuarlas al enlace real y a regulación. Do not select distance/power from a table; actual link geometry and legal limits govern. El inventario base no trae ejecutable `tc` ni archivo de módulo `sch_fq`; soporte integrado también sin verificar. Base inventories have no `tc` executable or `sch_fq` module file; built-in support is also unverified. No confundir `sch_fq` con `fq_codel`; cambios de firewall/red requieren validación separada. Do not conflate `sch_fq` and `fq_codel`; firewall/network changes need separate validation. Desactivar una bandera no revierte ajustes anteriores ni UCI persistente; registrar restauración. Disabling a flag does not undo previous transient settings or persistent UCI changes; record restoration.

Sólo en un laboratorio autorizado y recuperable, fijar RF/carga, comparar A1/B1/A2/B2 y repetir con suficientes muestras. Guardar salida de texto `iperf3`, ping bruto, cantidad de muestras, pérdida, p50/p95/p99, CPU/RAM, reinicios y getters reales. On an authorized recoverable bench, hold RF/load fixed, repeat A1/B1/A2/B2, and retain plain-text iperf3, raw ping, sample counts/loss, tails, CPU/RAM, resets and actual getters. No publicar credenciales, IP/MAC de clientes ni configuraciones privadas al compartir resultados. Do not publish credentials, client IP/MAC addresses or private configurations with results.

Recibo local / Local build receipt: [Stage 170](../artifacts/autoresearch/stage170a_public_wa_4board_release_v4_receipt.json). Esta guía no autoriza publicación, producción ni flasheo; no requiere acción física para su validación documental. This guide does not authorize publication, production changes or flashing; its documentation checks need no physical action.

<!-- stage265a-recovery:start -->
## Recuperación y diagnóstico / Troubleshooting and recovery

Esta matriz es un plan condicionado, no una orden de flash ni prueba de recuperación. This is a gated plan, not an executed flash or evidence of successful recovery.

| Síntoma / Symptom | Diagnóstico sin escritura / Read-only diagnosis | Ruta y condición de parada / Route and stop condition |
| :--- | :--- | :--- |
| Sin Wi-Fi tras imagen pública / No wireless after public image | Wi-Fi y DHCP empiezan deshabilitados; Ethernet directo aislado, PC en 192.168.1.0/24 con IP distinta de .20. Verificar enlace, alimentación PoE correcta y ARP. | Administración inicial 192.168.1.20/24; evitar otro equipo con esa IP. No usar este kit para conversión remota desatendida. |
| No responde la administración / Management unreachable | Revisar subred, ARP, VLAN, cable y MAC/placa; no resetear repetidamente ni adivinar una IP de producción. | Si la unidad sigue accesible, guardar configuración y hashes. No escribir sin identificar modelo/revisión e imagen exactos. |
| Boot fallido / Failed boot | Recuperación U-Boot TFTP en red Ethernet local aislada; confirmar el modo recovery según el modelo exacto. | TFTP objetivo 192.168.1.20, PC por ejemplo 192.168.1.10/24. Solo firmware factory/vendor validado para esa placa, tamaño y hash comprobados; no sysupgrade ni imagen raw. Detener si el bootloader/modelo no están confirmados. |
| Volver de OpenWrt a airOS / Return from OpenWrt to airOS | Leer /proc/mtd y mapa exacto; verificar nombre firmware y geometría, backups y hashes de bootloader/env/cfg/ART, salud y recovery. | La imagen raw stock_airos8_wa_8711_for_mtd_firmware.bin corresponde al área firmware (mtd2 SOLO en el mapa validado). No es un archivo TFTP, factory o sysupgrade; no adivinar /dev/mtd2 por número. Escritura bloqueada hasta autorización específica y recuperación demostrada. |
| Asociación sin ARP/IPv4 / Associated but no data | Separar EAPOL/L2 de datos bidireccionales; revisar WDS 4-address, bridge y Stage138A is_ubnt_ptp=1. | Si la STA sigue stock PtP, conservar AP airOS compatible y convertir STA remota primero con perfil OTA recuperable validado; alternativa radio.1.ptpmode=0, APPLY, reasociar y verificar ARP/IPv4 ANTES del AP. Stage138A es evidencia estática, no prueba de flash OTA. |
| Datos unidireccionales / One-way forwarding | Revisar ETH_P_TEB 0x6558, módulo/ABI, AP_VLAN y admitter dinámico phy*-ap0, rutas y puentes. | No atribuirlo solo a señal RF ni forzar puertos desconocidos al bridge. Los kits públicos no aportan watchdog OTA. |
| Menor velocidad, latencia o reinicios / Slow link, tails or resets | Comparar carga/RF/canal legales, CPU/RAM, pérdidas, resets y getters; iperf3 en texto (sin -J en MIPS BE). | Champion es opt-in; apagar una bandera no restaura UCI/sysctl anteriores. Restaurar snapshot conocido con autorización, medir de nuevo y conservar la regresión. |
| Archivo o hash distinto / Wrong file or digest | Comparar SHA256SUMS, perfil exacto, longitud, CRC y origen; coincidencia de familia WA no basta. | STOP: no flashear, renombrar otra placa ni tocar bootloader/env/calibración/ART/factory/MAC. |

Raw local: 10,092,544 bytes; SHA256 `2d4838ff638d6726dbbd0587bc538856c777d592b4b7593f88a96d0300801c49`. El nombre histórico dice 8711, pero Stage157A declara como fuente WA.v8.7.25.bin: no inferir versión ni compatibilidad del nombre; procedencia/placa requieren validación separada. The historical filename is not a version or compatibility guarantee. TFTP y raw son rutas distintas; ninguna requiere tocar radios para revisar esta guía.
<!-- stage265a-recovery:end -->
