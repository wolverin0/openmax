<!-- doc-head: Stage 3117A ES: 5 imagenes OpenWrt 25.12.6 ath79 (LAP-120, LiteBeam AC Gen2, NanoStation AC Loco, PowerBeam 5AC Gen2 y 5AC-500) armadas con el ImageBuilder oficial (sha256 verificado) y el mismo set de paquetes que 24.10.4 mapeado a 25.12 (opkg->apk); tamano vs particion firmware 0xf60000, overlay libre, riesgo de RAM en 64 MB (UNKNOWN en runtime), y que lineas del kit v20 se rompen (parche ETH_P_TEB, .ko 6.6.110, spectral_scan_ctl); NADA flasheado -->
Que cubre: tabla por placa (tamano/particion/overlay), mapeo de paquetes, delta estatico 24.10.4 vs 25.12.6, lineas de kit afectadas, correccion a STAGE3113A (wifi ucode ya estaba en 24.10.4).
Estado: SOLO ESCRITORIO. 0 acceso a equipos, 0 flasheo. Imagenes en firmware/openwrt/2512/ (los .bin quedan fuera de git por la regla `*.bin` de .gitignore; manifests/sha256sums/profiles.json si son rastreables). No commiteado.
Build: WSL Ubuntu, ImageBuilder `openwrt-imagebuilder-25.12.6-ath79-generic.Linux-x86_64.tar.zst`, FILES = kit `common/99-fmx-wa-universal-champion-v20` + 14 `fmx_*.sh` que el v20 invoca (33 746 B).
Leer cuando: antes de planear el A/B 24.10.4 -> 25.12.6 en banco (tarjeta de STAGE3113A accion 1) o de flashear cualquier 25.12.
<!-- /doc-head -->

## 0. Respuesta a "la base tiene mas de dos anos de atraso?" (fechas del manifest, hoy 2026-10-31)
- Parcial. La base como conjunto NO tiene 2 anos: nuestra 24.10.4 trae `libubus 2025.10.17`, `jshn 2025.07.23`, `wireless-regdb 2025.07.10` (CONFIRMED manifest), o sea se construyo despues de oct-2025 (~12 meses). La rama 24.10 y su kernel 6.6 LTS si son de la generacion anterior (INFERRED) y 24.10 esta fuera de soporte desde sept-2026 (STAGE3113A).
- Lo viejo de verdad es el driver y el firmware: `kmod-ath10k-ct-smallbuffers` snapshot 2024.07.30 (~27 meses, CONFIRMED) y `ath10k-firmware-qca988x-ct` 2020.11.08 (~6 anos, CONFIRMED).
- Contrapeso: 25.12.6 solo los mueve a 2025.12.01 (~11 meses) y a firmware 2023.04.04 (~3.5 anos). Upstream tambien entrega firmware CT viejo; actualizar la base no lo renueva. No se cita fecha de release de 24.10.4/25.12.6 porque no esta en lo leido.

## 1. Fuente y verificacion
- CONFIRMED: sha256 del ImageBuilder (`6f40746139c833336e67b03d5bdb0501d3a80fb789bf7e5b7a9b9984b83a5e23`) y de las 5 imagenes stock coinciden con `sha256sums` de downloads.openwrt.org/releases/25.12.6/targets/ath79/generic. Salvedad: `sha256sums.asc` (GPG) NO verificado; el hash viene por HTTPS.
- Base 25.12.6 (profiles.json): kernel 6.12.112, mac80211 backports 6.18.55, `kmod-ath10k-ct-smallbuffers` 2025.12.01~bb84e159 (fuente ath10k-6.18), `ath10k-firmware-qca988x-ct` 2023.04.04, hostapd/wpad 2025.08.26, apk-mbedtls 3.0.5.
- Nuestra 24.10.4 (manifest spectral): kernel 6.6.110, backports 6.12.52, ath10k-ct 2024.07.30~ac71b14d (ath10k-6.10), firmware 2020.11.08, wpad 2024.09.15, opkg.
- INFERRED: la regla Macronix MX25L12805D (kernel >= 6.6.103) queda cubierta por kernel 6.12.112; no se corrio la validacion del packager sobre "25.12.6".

## 2. Imagenes generadas (sysupgrade, mismo comando `make image PROFILE=... FILES=...`)
Particion `firmware` = 0xf60000 = 16 121 856 B (DTS `ar9342_ubnt_wa.dtsi`; `IMAGE_SIZE := 15744k` en `common-ubnt.mk`, igual en 24.10.4). Kernel+rootfs van juntos; el overlay (jffs2) es el resto, alineado a 64 KiB. Overlay = INFERRED (sin overhead jffs2).
La columna 24.10.4 sale de `firmware/openwrt/wa_universal_kit_v34/`: es imagen del kmods OFICIAL 24.10.4 (mismo `ath10k_core.ko` 600 808 B y offset de rootfs 2 621 440 que el release oficial en `firmware/openwrt/`) + un uci-default fmx. Que v34 sea lo desplegado en prod: UNVERIFIED (no lo leimos en un registro de despliegue).
| Placa (profile) | factory 25.12.6 | sysupgrade 25.12.6 | % de particion | overlay libre 25.12.6 | sysupgrade 24.10.4 (kit v34) | overlay libre 24.10.4 | RAM |
| :-- | --: | --: | --: | --: | --: | --: | :-- |
| LAP-120 `ubnt_lap-120` | 7 275 160 | 7 274 761 | 45.1 | 8 781 824 B (8.38 MiB) | 6 947 115 | 9 109 504 (8.69 MiB) | 64 MiB |
| LiteBeam AC Gen2 `ubnt_litebeam-ac-gen2` | 7 144 088 | 7 143 707 | 44.3 | 8 912 896 B (8.50 MiB) | 7 013 167 | 9 043 968 (8.63 MiB) | 64 MiB |
| NanoStation AC Loco `ubnt_nanostation-ac-loco` | 7 275 160 | 7 274 785 | 45.1 | 8 781 824 B (8.38 MiB) | 7 013 173 | 9 043 968 (8.63 MiB) | 64 MiB (INFERRED por familia WA) |
| PowerBeam 5AC Gen2 `ubnt_powerbeam-5ac-gen2` | 7 209 624 | 7 209 247 | 44.7 | 8 847 360 B (8.44 MiB) | 6 947 137 | 9 109 504 (8.69 MiB) | 64 MiB |
| PowerBeam 5AC-500 `ubnt_powerbeam-5ac-500` (QCA9558, XC) | 7 144 088 | 7 143 709 | 44.3 | 8 912 896 B (8.50 MiB) | n/a (solo base_cache stock) | n/a | 128 MiB (spec del packager, INFERRED) |
- Margen: todas usan ~45 % de la particion; el overlay libre baja 0.13 a 0.31 MiB vs 24.10.4. Sin riesgo de tamano. El kernel crece: offset del rootfs 2 752 512 B vs 2 621 440 (v34) / 2 686 976 (spectral), +64 a +128 KiB (granularidad 64 KiB, CONFIRMED por busqueda de `hsqs`).
- SHA256 de cada .bin: `firmware/openwrt/2512/SHA256SUMS_images.txt`. Manifest y profiles.json por placa en `firmware/openwrt/2512/<profile>/`.
- 5AC-500 usa `kmod-ath10k-ct` (default del perfil, no smallbuffers); build_universal solo declara `powerbeam-5ac-gen2` y `litebeam-ac-gen2`. El 5AC-500 es extra, no estaba en la lista de 24.10.4 del packager.
- NO se aplico el parche de build_universal (squashfs repack con `99-fmx-pbe5ac-ptp`, watchdog, `rc.local`): ese kit PtP esta retirado (`99-fmx-pbe5ac-ptp` imprime "legacy actuator retired"). Solo se horneo el kit WA v20 (el v21 de STAGE797A no esta materializado en `common/`).

## 3. Mapeo de paquetes 24.10.4 -> 25.12.6
`PACKAGES="kmod-ath10k-ct-smallbuffers ath10k-firmware-qca988x-ct iw-full ethtool iperf3 tcpdump-mini libpcap libatomic"` (+ defaults del perfil: wpad-basic-mbedtls, kmod-ath9k, kmod-usb2 en LAP/Loco, rssileds en PBE gen2).
| 24.10.4 | 25.12.6 | Nota |
| :-- | :-- | :-- |
| opkg | apk-mbedtls | CAMBIA. `/lib/apk/db/installed`, `/etc/apk/repositories.d/distfeeds.list`; no hay `/usr/lib/opkg`. |
| iw-full 6.9, ethtool 6.11, iperf3 3.17.1, tcpdump-mini 4.99.5, libpcap1 1.10.5 | iw-full 6.17, ethtool 6.15, iperf3 3.22, tcpdump-mini 4.99.6, libpcap1 1.10.6 | mismos nombres. |
| libatomic1 | libatomic1 (nombre del paquete `libatomic`) | igual. |
| ath10k-firmware-qca988x-ct 2020.11.08 | 2023.04.04 | NOMBRE IGUAL, FIRMWARE DISTINTO (variable nueva para el A/B). |
| kmod-ath10k-ct-smallbuffers 2024.07.30 | 2025.12.01 (ath10k-6.18) | confirma STAGE3113A #6. |
| openwisp-config-mbedtls, tc-tiny, kmod-sched-core (receta del packager) | NO resuelven en feeds 25.12.6 (`openwisp-config-mbedtls (no such package)`); tc-tiny/kmod-sched-core no estaban en el manifest real de 24.10.4 | excluidos; la linea `tc qdisc replace dev br-lan ... fq_codel` del v20 ya era no-op en 24.10.4 (INFERRED: sin paquete `tc`). |
| libiwinfo/iwinfo (en manifest 24.10.4) | solo entra via rssileds (PBE gen2) | ninguna linea del kit usa `iwinfo` (grep). |
| ATH_DEBUG=y, ATH_SPECTRAL=y (solo la build `futuramax-r28959-spectral`, compilada a mano) | NO disponible con ImageBuilder (kmods del feed oficial); tampoco lo tiene la v34 sobre 24.10.4 oficial | ver seccion 5. |
- Error evitado en el build: `-wpad-basic-mbedtls wpad-basic-mbedtls` en PACKAGES se cancela y la imagen salia SIN `/usr/sbin/wpad` (sin AP). Corregido; los 5 manifests finales tienen `wpad-basic-mbedtls 2025.08.26`.

## 4. RAM en 64 MB (riesgo)
- Medido en 24.10.x (STAGE2896A): Panel1 AP .84, MemTotal 56 120 kB, MemAvailable 15.3 MiB a 75 min del reinicio, 1.9 MiB bajo carga; los procesos son udapi-bridge/hostapd/uhttpd/rpcd de la imagen en prod. Nuestras 25.12 no llevan LuCI (uhttpd/rpcd), igual que el manifest 24.10.4.
- Delta estatico CONFIRMED (squashfs LAP-120 extraido con unsquashfs4). Contra 24.10.4 OFICIAL (base de v34): mac80211.ko 815 640 -> 857 880 (+42 KB), ath10k_core.ko 600 808 -> 601 348 (+0.5 KB). Contra la build `spectral` (ATH_DEBUG+SPECTRAL, solo para userland; el kmod no es comparable): wpad 864 296 -> 905 800 (+41 KB), netifd 198 661 -> 149 285 (-49 KB), procd 133 948 -> 80 852 (-53 KB), ucode 65 557 -> 12 309.
- Kernel comprimido +64 a +128 KiB (seccion 2). Efecto neto en RSS/Slab/DMA de ath10k en runtime: **UNKNOWN**. No se encontro dato publico y el delta estatico no lo determina (los 15 MiB "sin contar" de STAGE2896A son anillos DMA y skb, que no dependen del tamano de los .ko). Medirlo en banco: `MemAvailable` en reposo y bajo carga, 24.10.4 vs 25.12.6, mismo kit, sin LuCI.
- Riesgo INFERRED medio-bajo en las 4 placas de 64 MiB; el 5AC-500 (128 MiB) sin riesgo practico.

## 5. Lineas del kit v20 que se rompen o cambian en 25.12
Auditado: `99-fmx-wa-universal-champion-v20` + 14 helpers (15 archivos). Cero usos de `opkg`, `swconfig`, `fw_setenv`, `/dev/mtd`, `hostapd_cli`.
1. **SIN CAMBIO vs v34, PERO NO-OP: `ath10k/spectral_scan_ctl`** (v20, `fmx_qca988x_spectral_nf_helper.sh`, `fmx_qca_spectral_radar_phyerr_guard.sh`). CONFIRMED: el `ath10k_core.ko` de 25.12.6 y el de 24.10.4 oficial (base de v34) tienen 0 coincidencias; solo la build `spectral` (ATH_SPECTRAL) la trae (1). Los `echo` van con `2>/dev/null || true`: no falla, no actua. Perdida real solo respecto de la build spectral; todo lo espectral exige build propia (no ImageBuilder).
2. **OK, verificado en el .ko oficial: `ani_enable`, `pktlog_filter`, `htt_max_amsdu_ampdu`, `fw_stats`** (debugfs ath10k presente). `mac80211` expone `aql_threshold` y `aql_txq_limit` (cadena en mac80211.ko). Estructura `/sys/kernel/debug/ieee80211/phyN/ath10k/` sin cambio de nombres (INFERRED: no se arranco hardware).
3. **POSIBLE ROTURA FUNCIONAL: parche ETH_P_TEB (0x6558) de mac80211** para 4-addr WDS con CPE airOS 8 stock. `999-futuramax-ubnt-wds-strip-eth-p-teb-0x6558.patch` solo aplica en build de fuente; el ImageBuilder usa el kmod oficial sin parche. Los `.ko` precompilados (`mac80211_teb*_6.6.110.ko` en `pbe5ac_gen2_ptp_kit/`) tienen `vermagic=6.6.110` (CONFIRMED con grep) y no cargan en 6.12.112 (INFERRED). Re-basar el parche contra mac80211 6.18.55 y compilar es trabajo aparte. Sin eso, WDS vs airOS 8 queda UNKNOWN. (El build.log de la spectral 24.10.4 no muestra el parche aplicado: tampoco esta probado que lo llevara.)
4. **Sin cambio (verificado en el rootfs 25.12): opciones UCI `wireless.radio0.{ldpc,rx_stbc,tx_stbc,su_beamformer,su_beamformee,max_inactivity,skip_inactivity_poll,distance}`**: todas siguen en `wifi-scripts` (`/lib/wifi/mac80211.uc`, `wifi/validate.uc`). `wifi down; wifi up` (en `fmx_qca988x_wmi_peer_rate_sgi_guard.sh` y `fmx_pbe5ac_ptp_champion_v3_vht40.sh`) sigue existiendo.
5. **Sin cambio: `dhcp.lan.{ignore,dhcpv4,dhcpv6,ra}`, `/etc/init.d/{dnsmasq,odhcpd}`, `sysctl -w net.*` (los de 6.12 existen; van con `|| true`), `tx_queue_len`, `iw phy phy0 set rts off`, `iw ... set distance`.**
6. **Orden de uci-defaults**: v20 es `99-`, corre despues de `11_network-migrate-bridges`, `12_network-generate-ula`, `15_odhcpd`, `50-dropbear`. Los `uci set dhcp.*` de v20 son seguros, pero `uci-defaults` se borra al ejecutarse (= una sola vez por flasheo), igual que en 24.10.4.
7. **Fuera del overlay (no auditado a fondo):** scripts de inspeccion en `artifacts/autoresearch/stage1542a/` y `stage1584a/` usan `opkg`; 11 archivos .sh/.py del repo mencionan `opkg install/list` o `/usr/lib/opkg`.
- Correccion a STAGE3113A (lineas 9 y 42): la 24.10.4 propia YA usa wifi en ucode (`wifi-scripts 1.0`, `ucode-mod-nl80211`, `/lib/wifi/mac80211.uc` + stub `mac80211.sh` en la imagen extraida). El cambio real 24.10.4 -> 25.12 en este frente es **opkg -> apk**, no shell -> ucode.

## 6. Lo que NO se hizo / limites
- 0 flasheos, 0 acceso a equipos; las imagenes no se arrancaron (ni QEMU: no hay target mips ath79 ubnt). Compatibilidad fisica y boot: UNKNOWN hasta banco.
- Gate del operador para cualquier flasheo: ver tarjeta de banco en STAGE3113A (LAP-120 .20 + Loco .250, backup + hash de mtd0/1/4/5, watchdog de auto-revert, nunca mtd0/1/5). El factory `.bin` Ubiquiti es para instalar desde airOS; el sysupgrade es para desde OpenWrt.
- Variables confundidas en un A/B 24.10.4 vs 25.12.6: kernel 6.6->6.12, mac80211 6.12.52->6.18.55, driver ath10k-ct 2024.07.30->2025.12.01, FIRMWARE 2020.11.08->2023.04.04, sin parche TEB (v34 tampoco tenia spectral). Para atribuir, repetir con 25.12 + firmware 2020.11.08 solo si el A/B da diferencia mayor que la varianza A/A.
