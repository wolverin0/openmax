<!-- doc-head: Stage 207A XW 64MB Full SquashFS (hsqs) Bake on 198.18.0.62 & XM 32MB Safety Gate -->
Full SquashFS (hsqs) rootfs bake and hardware safety gate verification on 198.18.0.62.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 207A — `XW` `64 MB` Full SquashFS (`hsqs`) Bake & `XM` `32 MB` Safety Gate

- **Status**: `CONFIRMED` (`live_radios_241_242_20_250_touched = false`, `memory-master`: `<memorymaster-id>`)
- **Attribution**: `Linux` / `mac80211` / `ath9k` / `hardware` (`AR9342` 535 MHz + `64 MB` DDR2 + `8 MB` SPI NOR)
- **Receipt**: [`stage207a_xw_64mb_full_squashfs_bake.json`](../artifacts/autoresearch/stage207a_xw_64mb_full_squashfs_bake.json)

## 1. Embedded SquashFS (`hsqs`) Rootfs Payload & `END.` Full-Image CRC32
- `/etc/hotplug.d/net/99-fmx-xw-xm-ath9k-champion` (`SHA-256`: `f1331274eab7e79b09a51d0407badc3343b09f3ef0b8294d0a1d82a315086e0c` — `vm.min_free_kbytes=3072`, `FQ_MEM_LIMIT=2621440` `2.5 MB`, `FQ_LIMIT=768`, `ath9k` `ani=1`, `airtime_flags=7`)
- `/lib/modules/6.6.110/mac80211.ko` (`SHA-256`: `fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6` — `ETH_P_TEB 0x6558` 4-addr WDS decap)
- Rebuilt `XW.ar934x` `factory.bin` with `OPEN` CRC32, `PARTkernel` CRC32, `PARTrootfs` CRC32, and `12`-byte `END.` full-image CRC32 (`zlib.crc32(image[:pr_end+8])`), keeping all images `< 6.7 MB` inside the `8 MB` SPI NOR ceiling.

## 2. Baked `XW` `64 MB` Profiles (`firmware/openwrt/xw_64mb_kit_v1/`)
| OpenWrt Profile | Mapped `XW` `board.sysid`s | Models | Factory Image (`OPEN` + `PART` + `END.`) | Sysupgrade Image (`FWx0` Signed) |
| :--- | :--- | :--- | :--- | :--- |
| `ubnt_nanostation-loco-m-xw` | `0xe845, 0xe867, 0xe835` | `NanoStation loco M5 XW, NanoStation loco M2 XW, AirGrid M5 HP XW` | `openwrt-24.10.4-xw-ubnt_nanostation-loco-m-xw-squashfs-factory.bin` (`f7d26be1f99cad87...`) | `openwrt-24.10.4-xw-ubnt_nanostation-loco-m-xw-squashfs-sysupgrade.bin` (`7d738ec998015670...`) |
| `ubnt_nanostation-m-xw` | `0xe855, 0xe866` | `NanoStation M5 XW (Dual-Port + GPIO 2 PoE), NanoStation M2 XW (Dual-Port + GPIO 2 PoE)` | `openwrt-24.10.4-xw-ubnt_nanostation-m-xw-squashfs-factory.bin` (`e4972a1c2b000bfa...`) | `openwrt-24.10.4-xw-ubnt_nanostation-m-xw-squashfs-sysupgrade.bin` (`79e6647dff4de683...`) |
| `ubnt_powerbeam-m5-xw` | `0xe3e5, 0xe5e5, 0xe4e5, 0xe6e5, 0xe885, 0xe7f8, 0xe815, 0xe825, 0xe875, 0xe3b5, 0xe6b5, 0xe868, 0xe1d5, 0xe4d5, 0xe1d2` | `PowerBeam M5 300/400/400-ISO/620 XW, IsoStation M5 XW, NanoBeam M5 16/19 XW, Rocket M5/M2 XW & Titanium` | `openwrt-24.10.4-xw-ubnt_powerbeam-m5-xw-squashfs-factory.bin` (`1341a60e5d5ba322...`) | `openwrt-24.10.4-xw-ubnt_powerbeam-m5-xw-squashfs-sysupgrade.bin` (`2fc680d6a3275832...`) |
| `ubnt_powerbeam-m2-xw` | `0xe2c2, 0xe812` | `PowerBeam M2 400 XW, NanoBeam M2 13 XW` | `openwrt-24.10.4-xw-ubnt_powerbeam-m2-xw-squashfs-factory.bin` (`11ead8c887f0dfaf...`) | `openwrt-24.10.4-xw-ubnt_powerbeam-m2-xw-squashfs-sysupgrade.bin` (`80de35383ddfa688...`) |
| `ubnt_litebeam-m5-xw` | `0xe865, 0xe895` | `LiteBeam M5 23 XW (rev1 & rev2)` | `openwrt-24.10.4-xw-ubnt_litebeam-m5-xw-squashfs-factory.bin` (`a576bf3c012e64e3...`) | `openwrt-24.10.4-xw-ubnt_litebeam-m5-xw-squashfs-sysupgrade.bin` (`52c0dbf4e19e1fe2...`) |
| `ubnt_bullet-m-xw` | `0xe2c3, 0xe2c4, 0xe2d4, 0xe869, 0xe879` | `Bullet M2/Ti XW, Bullet M5/Ti XW` | `openwrt-24.10.4-xw-ubnt_bullet-m-xw-squashfs-factory.bin` (`f59f25395e497591...`) | `openwrt-24.10.4-xw-ubnt_bullet-m-xw-squashfs-sysupgrade.bin` (`586a225ee66acbb7...`) |

## 3. `XM` `32 MB` OOM Safety Gate (`BLOCK_OPENWRT_24_10_4_ON_32MB_XM`)
- `32 MB` `XM` boards (`0xe005` `NSM5`, `0xe0a5` `locoM5`, `0xe2d5` `AG-HP-5G23`) are strictly blocked from flashing `OpenWrt 24.10.4` (`Linux 6.6` `ath79` OOM risk) and automatically select `Mode B` (`Stock airOS 6` + `rc.poststart` `polling=disabled`, `wds=enabled`), interoperating 100% zero-touch with OpenWrt 24.10.4 APs.
