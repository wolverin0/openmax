<!-- doc-head: Stage 3118A ES: pista A del operador (31/10): OpenWrt 24.10.4 oficial + backport de estabilidad ath10k-ct (rx_netbuf_pop NULL, recovery_check_work en workqueue_aux, beacon ar NULL) compilado con el SDK oficial 24.10.4 (sha256 verificado, feed base en tag v24.10.4) como kmod -r3, y 5 imagenes del ImageBuilder oficial (LAP-120, LiteBeam AC Gen2, NanoStation AC Loco, PowerBeam 5AC Gen2, 5AC-500) con el mismo set de paquetes y kit que 2512 + mac80211.ko TEB v3 (el de v34); vermagic y tamanos verificados; NADA flasheado -->
Que cubre: procedencia, parche, kmod, tabla por placa (tamano/particion/overlay), mac80211 TEB, que trae v34 que aca no, limites y siguiente tarjeta de banco.
Estado: SOLO ESCRITORIO. 0 acceso a equipos, 0 flasheo, sin commit. Salida en `firmware/openwrt/2410_bp/` (los `.bin` quedan fuera de git por la regla `*.bin`, igual que 2512).
Entrada: STAGE3116A (diff y backport), STAGE3117A (receta 2512). Build: WSL Ubuntu, `~/fmx_bp2410/` (SDK y IB nuevos, aislados del `~/fmx_sdk` de otra lane).
Leer cuando: antes del A/B en banco 24.10.4 oficial vs 24.10.4+backport, o antes de flashear cualquier `2410_bp`.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

## 1. Procedencia (CONFIRMED)
- SDK `openwrt-sdk-24.10.4-ath79-generic_gcc-13.3.0_musl...tar.zst` sha256 `0b693ad6...cdec5` e ImageBuilder `openwrt-imagebuilder-24.10.4-ath79-generic...tar.zst` sha256 `d5765c71...c17b4`: ambos coinciden con `sha256sums` de downloads.openwrt.org/releases/24.10.4/targets/ath79/generic (bajado por HTTPS hoy). `sha256sums.asc` (GPG) NO verificado.
- `feeds.conf.default` del SDK apunta a la rama `openwrt-24.10`, no al release: la rama trae backports 6.12.96, el release 6.12.52. Se fijo `feeds/base` en el tag `v24.10.4` (78b23a26; release r28959-29397011cc). Prueba de que el SDK quedo identico al release: el `mac80211.ko` que compilo el SDK tiene sha256 `8566fb1c...`, el mismo byte a byte que el oficial.
- El `~/fmx_sdk` previo tenia un parche ajeno sin versionar (`099-fmx-ppdu-end-ring.patch`) y el feed en la punta de la rama: no se uso ni se toco.

## 2. Parche y kmod
- `990-fmx-ath10k-ct-stability-backport.patch` = `<tmp> (sin CR) con las rutas reescritas a `a/ath10k-6.10/<archivo>` (OpenWrt aplica `-p1` desde la raiz del paquete). Se aplica despues de los 11 parches de OpenWrt 24.10.4 (001, 002, 010, 201, 202, 205, 206, 300, 960-0010, 960-0011, 988), sin cambios en esos: el stack completo que trae la imagen oficial se conserva.
- CONFIRMED (`prepare V=s`): aplica en las 2 variantes (regular y smallbuffers) sin FAILED. Solo hay corrimientos: core.c +17/+32, core.h +1, mac.c +2 lineas.
- `PKG_RELEASE` 2 -> 3 para que opkg del IB elija el kmod local y el manifest lo muestre (`6.6.110.2024.07.30~ac71b14d-r3`). Depends: `kernel (=6.6.110~35ef4dd36891d37023436baa842fa311-r1)`, que es el kernel del release oficial.
- CONFIRMED: 0 warnings/errores de compilacion en `ath10k-6.10/*.c|h`. Hay 395 warnings en el log, todos de otros paquetes que se compilaron como dependencia (openssl, hostapd).
- CONFIRMED (strings en `ath10k_core.ko`): estan `rx ring slot` (#1), `consecutive fail` y `previous recovery succeeded` (#2), `wmi-tx-beacon-nowait` (#3), y `already restarting` desaparece (0). `hardware is wedged` no aparece. CONFIRMED: es un `ath10k_dbg`, y `-DCONFIG_ATH10K_DEBUG` solo se activa con `CONFIG_PACKAGE_ATH_DEBUG`, que en el SDK esta "not set" (`total recovery count` tampoco aparece, por lo mismo).
- Tamanos de `ath10k_core.ko`: smallbuffers 601 672 B (sha `dc17d325...`), regular 601 448 B (`63ae70bd...`). El oficial pesa 600 808 B, o sea +864 B.

## 3. Imagenes (`make image PROFILE=... PACKAGES=... FILES=...`)
PACKAGES igual a `2512/packages.txt`: `kmod-ath10k-ct-smallbuffers ath10k-firmware-qca988x-ct iw-full ethtool iperf3 tcpdump-mini libpcap libatomic`. El 5AC-500 no lleva smallbuffers: usa el default del perfil, `kmod-ath10k-ct` regular, tambien con backport -r3. FILES = el mismo overlay de 2512 (`99-fmx-wa-universal-champion-v20` + 14 `fmx_*.sh`, 33 746 B) + `lib/modules/6.6.110/mac80211.ko` (ver 4).
Particion `firmware` = 0xf60000 = 16 121 856 B. Overlay libre = particion - sysupgrade redondeado a 64 KiB (INFERRED, mismo criterio que STAGE3117A).
| Placa (profile) | factory | sysupgrade | % particion | overlay libre | 25.12.6 sysupgrade (3117A) | kmod |
| :-- | --: | --: | --: | --: | --: | :-- |
| LAP-120 `ubnt_lap-120` | 6 947 480 | 6 947 613 | 43.1 | 9 109 504 B (8.69 MiB) | 7 274 761 | smallbuffers -r3 |
| LiteBeam AC Gen2 `ubnt_litebeam-ac-gen2` | 6 816 408 | 6 816 559 | 42.3 | 9 240 576 B (8.81 MiB) | 7 143 707 | smallbuffers -r3 |
| NanoStation AC Loco `ubnt_nanostation-ac-loco` | 6 947 480 | 6 947 637 | 43.1 | 9 109 504 B (8.69 MiB) | 7 274 785 | smallbuffers -r3 |
| PowerBeam 5AC Gen2 `ubnt_powerbeam-5ac-gen2` | 6 816 408 | 6 816 563 | 42.3 | 9 240 576 B (8.81 MiB) | 7 209 247 | smallbuffers -r3 |
| PowerBeam 5AC-500 `ubnt_powerbeam-5ac-500` | 6 816 408 | 6 816 561 | 42.3 | 9 240 576 B (8.81 MiB) | 7 143 709 | regular -r3 |
- CONFIRMED (squashfs de cada sysupgrade extraido; rootfs en el offset 2 621 440, igual que el oficial):
  - `ath10k_core.ko`, `ath10k_pci.ko`, `mac80211.ko` y `cfg80211.ko` tienen todos `vermagic=6.6.110 mod_unload MIPS32_R2 32BIT`, igual que el oficial.
  - `opkg status` muestra `kernel 6.6.110~35ef4dd...-r1`, `kmod-mac80211 6.6.110.6.12.52-r1`, kmod ath10k-ct `-r3`, firmware CT 2020.11.08-r1, `wpad-basic-mbedtls 2024.09.15~5ace39b0-r3` (con `/usr/sbin/wpad` presente), iw-full 6.9, ethtool 6.11, iperf3 3.22, tcpdump-mini 4.99.5, libpcap1 1.10.5 y libatomic1.
  - Estan los 14 `fmx_*` y el uci-default v20. Sin LuCI, igual que 2512.
- Los nombres de paquete son los mismos que en 2512, pero las versiones no estan congeladas. CONFIRMED: el IB baja los paquetes de los feeds vivos `releases/24.10.4/...` (`repositories.conf`), no del snapshot del release.
  - Ejemplo: `wpad-basic-mbedtls` es -r3 aca y -r2 en el stock/v34 y en el manifest oficial.
  - El iperf3 3.22 de aca vs el 3.17.1 que STAGE3117A le atribuye a 24.10.4 no se verifico.
  - Las versiones exactas quedan fijadas en `2410_bp/feed_ipks.sha256` (124 ipk). 2512 se armo igual, desde su propio feed vivo.
- Todas entran holgadas, alrededor del 43 % de la particion. Respecto de 25.12.6 son ~320 a 390 KB mas chicas. Reparto entre kernel y rootfs: INFERRED (3117A midio solo +64 a 128 KiB de kernel).

## 4. Parche TEB / WDS con airOS 8 (mac80211)
- CONFIRMED (squashfs extraido): las imagenes v34 (`wa_universal_kit_v34`, LAP y PBE) llevan `mac80211.ko` sha `fe4f730f...` = `pbe5ac_gen2_ptp_kit/mac80211_teb_4addr_v3_6.6.110.ko`. Es un parche BINARIO sobre el `mac80211.ko` oficial `8566fb1c` (`mac80211_rom_241.ko`) que cubre:
  - TEB 0x6558 (FMX-DISC-36);
  - bypass de EAPOL 4-addr (DISC-38);
  - trigger AP_VLAN con gate de AUTHORIZED (DISC-41).
- Se horneo ese mismo .ko via FILES (sha verificado en las 5 imagenes). Es valido porque el backport no toca mac80211: el kmod-mac80211 del IB es el oficial (`8566fb1c`, el mismo que reprodujo el SDK) y el vermagic coincide.
- NO se uso el quilt `999-futuramax-ubnt-wds-strip-eth-p-teb-0x6558.patch` del packager, por 3 motivos:
  - solo cubre DISC-36, asi que perderia DISC-38/41;
  - el build.log de la spectral no lo muestra aplicado;
  - apunta a `net/mac80211/util.c`, pero `ieee80211_data_to_8023_exthdr` esta definida en cfg80211 (`net/wireless/util.c` de backports 6.12.52) y se llama desde `net/mac80211/rx.c`. CONFIRMED con grep: el quilt no aplicaria.
- INFERRED: el WDS con CPE airOS 8 se comporta igual que en v34, porque son los mismos bytes de mac80211 y el mismo kernel. UNKNOWN en hardware: falta probarlo en banco.

## 5. Que trae v34 y NO estas imagenes (decision del operador si hace falta)
- CONFIRMED por diff de rootfs:
  - `etc/uci-defaults/99-fmx-pbe5ac-ptp` con hostname `FMX-PBE5AC-AP-241` e IP `198.18.0.45` fijos;
  - `etc/hotplug.d/net/99-fmx-wa-universal-champion` (sha `8c41a7f9...`);
  - `fmx_pbe5ac_admitter.sh` y `fmx_ptp_rollback_watchdog.sh`;
  - `rssileds` y LuCI completo.
- Ademas, el `lap-120` de v34 no trae modulos USB y si trae rssileds: INFERRED, es la imagen de PBE reempaquetada.
- Cual imagen corre hoy en los paneles de produccion: UNVERIFIED, no hay registro leido. Se eligio la receta 2512 para que `2410_bp` vs `2512` difieran en la base, mas las versiones de feed de cada rama (ver 3).

## 6. Archivos (`firmware/openwrt/2410_bp/`)
- `<profile>/`: factory y sysupgrade `.bin`, `.manifest`, `.bom.cdx.json`, `profiles.json` y `sha256sums` del IB.
- `kmod/`: los 2 `.ipk` -r3 y el `.patch`.
- `packages.txt`, `BUILD_PROVENANCE.txt` (incluye las URLs de los feeds), `feed_ipks.sha256` y `SHA256SUMS` (bin, ipk, patch y manifest).
- Nota: el `.manifest` lista `kmod-mac80211 ...-r1` oficial, aunque el `.ko` quedo reemplazado por el TEB v3 desde FILES.
- Atajo de banco (NO ejecutado): el `.ipk` -r3 se puede instalar con `opkg install` en un 24.10.4 oficial ya flasheado, sin reflashear. Ojo: el `.ipk` no lleva el TEB.

## 7. Limites y siguiente tarjeta
- 0 arranques: ni en hardware ni en QEMU. Boot, carga de modulos y comportamiento del recovery: UNKNOWN.
- El rework de recovery agrega el estado WEDGED terminal tras 4 fallos seguidos (STAGE3116A 1.3). Requiere el watchdog de auto-revert en nodos remotos.
- Banco (gate del operador, STAGE3116A §5 tarjeta 2):
  - equipos LAP-120 `.20` y Loco `.250`, con backup y hash de mtd0/1/4/5, watchdog de auto-revert y nunca mtd0/1/5;
  - A = 24.10.4 con kit, B = `2410_bp`;
  - forzar `simulate_fw_crash` N veces y contar recuperaciones, `firmware crashed`, `previous recovery`/`consecutive fail`/WEDGED y tiempo hasta volver el trafico;
  - WDS con CPE airOS 8 stock (TEB);
  - decidir solo si B no es peor que la varianza A/A. Sin umbrales inventados.
