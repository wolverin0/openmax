<!-- doc-head: STAGE413A_TESTER_SELECTOR_V4.md preserved document content -->
<!-- /doc-head -->


# Stage 413A — One-Command Public Tester Installer & Interactive Board Selector `v4` (`detect_and_match_openmax_image.py`)

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `proprietary airMAX/LTU module`, `hardware`
- **Deliverable**: [`tools/firmware/detect_and_match_openmax_image.py`](../tools/firmware/detect_and_match_openmax_image.py) (`v4`)

## 1. Unified 4-Family Coverage (`WA v9`, `XC v2`, `XW v2`, `LTU Safe Kit v8`) (`CONFIRMED`)
| Hardware Family | Supported Boards / `sysid`s | Selected Champion Bundle (`v4`) | Mandatory Pre-Flight Safety Gate |
| :--- | :--- | :--- | :--- |
| **`WA` (`airMAX AC` Gen2)** | `31` `ubnthal.ko` records (`17` `sysid`s: `0xe3d6`, `0xe7f9`, `0xe8e5`, `0xe7fa`...) | `WA v9 SquashFS` (`99-fmx-wa-universal-champion-v9` + `WMI 0x9044` + `Sub-20MHz`) | SHA-256 backup of `mtd0`, `mtd1`, `mtd4`, `mtd5` (`ART`) + `45s` rollback watchdog. |
| **`XC` (`airMAX AC` Gen1/AirPrism)** | `34` `ubnthal.ko` records (`6` Passive + `7` Active-AirPrism `sysid`s) | `XC Passive v1` / `XC Active-AirPrism v2` (`fmx_xc_airprism_filterd.sh`) | SHA-256 backup of `mtd0/1/4/5` + `spi-gpio` bit-bang AirPrism filter guard. |
| **`XW` (`airMAX M5` `64 MB`)** | `30` `ubnthal.ko` records (`29` `64 MB` `sysid`s; `32 MB` `XM` blocked) | `XW 64MB v2 SquashFS` (`< 6.7 MB` `END.` CRC32 signed) | Fail-closed `32 MB XM` OOM block + `mtd0/1/4/5` backup. |
| **`LTU` (`AF-LTU` 5-Board + Rocket)** | `0xae02`, `0xae06`, `0xae07`, `0xae08`, `0xae09`, `0xae0b` | `LTU Safe Kit v8` (`10`-Round / `120`-Window `rc.poststart_ltu_safe_champion.sh`) | Zero `/dev/ame*` touches + `/etc/persistent` (`mtd10`) user-config persistence only. |
