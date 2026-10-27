<!-- doc-head: Public tester guidance through824A; board-specific profiles and qualified legacy setup/recovery retained -->
<!-- /doc-head -->

# Respuesta para testers / Tester reply: OpenMAX public WA v4

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

Revisado localmente para Stage 194A. Nada se publicó ni envió a Reddit/GitHub. Locally prepared for Stage 194A; nothing was posted or sent to Reddit/GitHub. Use los bloques siguientes como texto; no son autorización para flashear. The blocks below are copyable text, not flash authorization.

## English reply

```markdown
Experimental OpenMAX public WA tester v4 is available as a local package for:
- PowerBeam 5AC Gen2: ubnt,powerbeam-5ac-gen2 (catalog 0xe3d6).
- LiteBeam 5AC Gen2: ubnt,litebeam-ac-gen2 (catalog 0xe7f9).
- LAP-120: ubnt,lap-120 (catalog 0xe7f5/0xe8e5).
- NanoStation 5AC Loco: ubnt,nanostation-ac-loco (catalog 0xe7f7/0xe7fa).

There are eight images, factory and sysupgrade for each model, with separate official OpenWrt 24.10.4 / Linux 6.6.110 kernels and DTBs. Catalog aliases and the older 31-record WA table are not physical compatibility acceptance. Never interchange models, force a mismatch or copy a WA module to another family.

Package: firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v4/ Verify its current SHA256SUMS.txt and SHA256SUMS. From that directory, use `sha256sum -c SHA256SUMS.txt` and `sha256sum -c SHA256SUMS`. These checks establish file integrity, not vendor authentication or a signature. The package is not an official OpenWrt or Ubiquiti-signed release.

First setup is WIRED: management 192.168.1.20/24, Wi-Fi disabled, DHCP/RA off, no shared Wi-Fi key and no remote OTA migration watchdog. Configure one isolated unit at a time with your own password, distinct address, legal country/channel, SSID and unique key. The inactive template uses WDS. Factory/sysupgrade are installation formats, not preconfigured AP/STA remote roles. This public v4 kit CANNOT be used as an automatic remote OTA migration profile. Test recovery and exact board/revision on a spare before considering installation; never bypass signatures or write calibration/factory/MAC/bootloader partitions.

Remote-order caveat (FMX-DISC-42): Stage 138 is offline binary RE/simulation, not a bench-confirmed OTA migration. If a remote stock-airOS STA is in PtP mode (`is_ubnt_ptp=1`), retain the compatible airOS AP while converting the STA first with a separately validated migration profile. Alternatively set the STA's `radio.1.ptpmode=0`, APPLY, then verify reassociation and bidirectional ARP/IPv4 data BEFORE changing the AP. Public v4 does not supply that migration profile. Vendor-IE restoration, `polling_enabled=0`, or successful EAPOL do not replace verified data forwarding. Unknown mode/recovery means stop the remote sequence.

Some saved results are encouraging, but the limits matter:
- Stage 161 R16 reported +13.68% goodput (42.880 to 48.748 Mbps): a short setting
contrast, not universal or independently established distance/timer causality; p99 was slightly worse (118.926 to 119.515 ms).
- The reported 8-flow +68.3%..+90.6% compares different runs (22.611 versus
mean 38.055/best 43.108 Mbps). It is not an isolated VM-memory effect or a transferable gain. The within-R17 reported mean contrast was +4.34%.
- Stage 162 reported -25.78% E2E p95, but E2E benefit is UNPROVEN: auxiliary
ping records contain 999 sentinels with samples=1, and actual flowtable activation was not demonstrated (`offload_active=UNKNOWN`).

Stage 163 consolidated requested settings, not new independent proof. The package keeps 18 RF comparisons/72 windows plus one E2E/4 windows separate. Copied configured fields are not getters; conntrack sizing is not offload; RPS mask 1 is not multi-CPU scaling. There is no universal31-board acceptance. All champion switches start at 0. Qdisc experiments require matching target dependencies; base images have no tc executable or sch_fq module file, and built-in support is unverified. Local build/readback checks are not boot, flash, recovery, zero-touch stock-airOS or RF-performance acceptance.

For authorized bench testing, keep RF/load fixed, repeat counterbalanced baseline/treatment runs, and retain plain-text iperf3 plus raw loaded ping, sample counts/loss, p50/p95/p99, CPU/RAM, resets and actual getters. Redact credentials and customer addresses/configurations before sharing results. No new hardware test, deployment or public upload is claimed by this reply.
```

## Respuesta en español

```markdown
OpenMAX public WA tester v4 es un paquete experimental local para PowerBeam 5AC Gen2, LiteBeam 5AC Gen2, LAP-120 y NanoStation 5AC Loco. Hay 8 imágenes: factory y sysupgrade por modelo, cada uno con SU kernel/DTB OpenWrt 24.10.4 / Linux 6.6.110. Los aliases catalogados no prueban compatibilidad física de todas las revisiones ni de los 31 registros históricos WA. No intercambiar modelos ni forzar cabeceras.

Carpeta: firmware/openwrt/pbe5ac_gen2_ptp_kit/public_release_v4/ Validar los archivos actuales SHA256SUMS.txt y SHA256SUMS; sus hashes prueban integridad, no autenticidad del fabricante ni firma. No es firmware oficial.

Primer inicio POR CABLE: gestión192.168.1.20/24, Wi-Fi y DHCP/RA desactivados, sin clave compartida ni watchdog OTA. Preparar una unidad aislada por vez, contraseña/dirección propias, país/canal legales, SSID y clave únicos. Este v4 público NO sirve como perfil automático de migración OTA remota. Verificar revisión, recuperación y backups en un repuesto antes de considerar instalación; nunca evadir firmas ni escribir calibración/fábrica/MAC/bootloader.

FMX-DISC-42 proviene de RE/simulación offline de Stage 138, no de una migración OTA confirmada en banco. Si la STA remota sigue en airOS PtP (`is_ubnt_ptp=1`), conservar el AP airOS compatible mientras se convierte primero la STA con otro perfil de migración previamente validado. Alternativa: `radio.1.ptpmode=0`, APPLY y comprobar reasociación y datos ARP/IPv4 bidireccionales ANTES de cambiar el AP. Guardar el valor sin aplicar no basta. v4 no aporta ese perfil remoto. Vendor IEs, polling_enabled=0 o EAPOL no sustituyen el camino de datos probado.

Resultados guardados, con sus límites al lado:
- R16 reportó +13.68% de goodput: ventana corta, sin causalidad independiente
de distancia/temporizador ni ganancia universal; p99 empeoró ligeramente.
- El contraste de 8 flujos +68.3%..+90.6% compara campañas distintas; no aísla el efecto VM.
Dentro de R17, el contraste de medias reportado fue +4.34%.
- E2E p95 -25.78% reportado: NO DEMOSTRADO/UNPROVEN por 999 / samples=1 y falta
de prueba de activación real de flowtable; offload_active=UNKNOWN.

Stage 163 consolida pedidos, no evidencia independiente. Se separan 18 ensayos RF/72 ventanas y 1 E2E/4 ventanas. Configuración copiada no es getter, conntrack no demuestra offload y RPS mask 1 no demuestra varios CPU. Todas las opciones champion empiezan en 0; no se promete boot, recuperación, zero-touch airOS ni rendimiento RF. El inventario base no incluye tc ni un archivo sch_fq; tampoco se verificó soporte integrado.

Para ensayos autorizados, repetir control/tratamiento con RF y carga fijas, guardar iperf3 en texto, ping bruto/cantidad/pérdida/colas, CPU/RAM y getters. No compartir credenciales, direcciones de clientes ni configuraciones privadas. Esta respuesta no ejecutó hardware, flasheo, despliegue ni publicación.
```

## Fuentes locales / Local sources

- [Guía universal](GUIA_UNIVERSAL_POWERBEAM_LITEBEAM_OPENMAX.md).
- [Stage 138 offline](../artifacts/autoresearch/stage138a_ptp_sta_data_gate_verdict.json).
- [Stage 161 R16..R18](../artifacts/autoresearch/stage161a_live_wa_round16_18_autoresearch.json).
- [Stage 162 E2E](../artifacts/autoresearch/stage162a_live_wa_e2e_forwarding_offload_benchmark.json).
- [Stage 163 consolidación](../artifacts/autoresearch/stage163a_cumulative_18round_wa_champion_v2.json).
- [Stage 170 build v4](../artifacts/autoresearch/stage170a_public_wa_4board_release_v4_receipt.json).

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
