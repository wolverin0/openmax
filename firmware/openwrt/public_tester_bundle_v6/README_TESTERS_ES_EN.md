# OpenMAX / FuturaMAX — Public Tester Bundle v6 (ES / EN)

## 1. Resumen Rapido (Espanol)
Este paquete (`v6`) cubre las **95 placas** de las 3 familias Ubiquiti `airMAX` (`31` `WA` + `34` `XC` + `30` `XW`) con imagenes `OpenWrt 24.10.4` (`Linux 6.6.110`) SquashFS (`hsqs`) pre-horneadas y verificadas:
- **Familia `WA` (`v7` SquashFS — `AR9342` `64 MB` RAM + `QCA9882` 5 GHz)**: `PowerBeam 5AC Gen2` (`0xe3d6`), `LiteBeam 5AC Gen2` (`0xe7f9`), `LiteAP AC LAP-120` (`0xe8e5`), `NanoStation 5AC Loco` (`0xe7fa`) y las 17 `board.sysid` de la familia `WA`. Incluye el `Champion v4` (`Stage 214A`, `100` ventanas `A1->B1->A2->B2`: `fq_limit=512`, `tcp_early_retrans=4`, `vm.min_free_kbytes=4096`, `distance=300`, `rps_cpus=1`, `flow_offloading=1`) y `mac80211_teb_4addr_v3_6.6.110.ko`.
- **Familia `XC` (`QCA9558` `720 MHz` `128 MB` RAM + `QCA9880` 5 GHz)**:
  * **Pasivas (`6` `sysid`s / `16` registros)**: `R5AC-Lite` (`0xe1f5`), `PBE-5AC-500` (`0xe3d5`), `PBE-5AC-620` (`0xe5f5`), `NBE-5AC-19` (`0xe4f5`), `NBE-5AC-Gen2-XC` (`0xe3d7`), `NS-5ACL-XC` (`0xe3d8`).
  * **Activas con `AirPrism` (`7` `sysid`s / `18` registros)**: `R5AC-PTP/PTMP` (`0xe3f5`), `R5AC-PRISM` (`0xe7e5`), `PrismStation 5AC` (`0xe7e6`, `0xe7e8`), `Rocket Prism 5AC Gen2` (`0xe7e7`, `0xe7e9`), `PrismAP-5AC` (`0xdc97`). Incluyen el demonio `/usr/sbin/fmx_xc_airprism_filterd.sh` (`GPIO 13..16` 2-bancos de filtros `AirPrism`) + opcion `Modo B` (`rc.poststart`).
- **Familia `XW` (`AR9342` `64 MB` RAM `8 MB` Flash `ath9k`) & Compuerta `XM` `32 MB`**:
  * `6` perfiles `XW` (`29` `sysid`s de produccion) con trailer `END.` CRC32 firmado.
  * Las placas `XM` de `32 MB` RAM (`0xe005`, `0xe0a5`, `0xe2d5`) estan bloqueadas contra `OpenWrt 24.10.4` (`BLOCK_OPENWRT_24_10_4_ON_32MB_XM`) y usan automaticamente `Modo B` (`99-fmx-xw-xm-ath9k-champion-v2`).

### Paso 1: Detectar el modelo exacto con `/etc/board.info`
```bash
ssh ubnt@<IP_RADIO> "cat /etc/board.info" > board.info
python3 detect_and_match_openmax_image.py --board-info board.info --role sta
```

### Paso 2: Respaldo obligatorio de particiones protegidas (`mtd0`, `mtd1`, `mtd4`, `mtd5`)
```bash
for m in mtd0 mtd1 mtd4 mtd5; do dd if=/dev/${m}ro of=/tmp/${m}.bin bs=64k; sha256sum /tmp/${m}.bin; done
```

---

## 2. Quick Start (English)
This `v6` Public Tester Bundle provides `100%` coverage across all **95 boards** (`31` `WA` + `34` `XC` + `30` `XW` records in `ubnthal.ko`):
1. Run `detect_and_match_openmax_image.py` (`v3`) against `/etc/board.info` to obtain the exact `factory.bin` / `sysupgrade.bin` path and SHA-256 digest.
2. Verify checksums against `SHA256SUMS.txt` before flashing.
3. Active-`AirPrism` `XC` radios (`0xe3f5`, `0xe7e5`, `0xe7e6`, `0xe7e8`, `0xe7e7`, `0xe7e9`, `0xdc97`) automatically run `/usr/sbin/fmx_xc_airprism_filterd.sh` on boot to program the 2-bank `GPIO 13..16` `AirPrism` RF preselector according to `iw dev` center frequency and channel width.

- **Generated UTC**: `2026-10-26T23:56:51.353946+00:00`
- **Selector Version**: `v3`
- **Total Verified Images Indexed**: `54`
