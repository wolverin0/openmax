<!-- doc-head: Stage 308A Public Tester Bundle v6 (WA v7 + XC Passive & Active-AirPrism + XW 64MB + Selector v3) -->
Unified multifamily public tester release bundle v6 covering all 95 WA, XC, and XW boards with SHA256SUMS and bilingual guide.
<!-- /doc-head -->

# Stage 308A — Public Tester Bundle `v6` (`WA` `v7` + `XC` Active-`AirPrism` + `XW` `64 MB`)

- **Status**: `CONFIRMED` (`live_radios_241_242_20_250_touched = false`, `memory-master`: `mm-8c70`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `ath9k` / `hardware`
- **Receipt**: [`stage308a_public_tester_bundle_v6.json`](../artifacts/autoresearch/stage308a_public_tester_bundle_v6.json)

## 1. Bundle Contents (`firmware/openwrt/public_tester_bundle_v6/`)
- `openmax-public-tester-bundle-v6.zip` (`SHA-256`: `9480e26ae46fe4cccac6a028bb154a16f6860baa9f8891620c0ae6fe131b5465`)
- `openmax-public-tester-bundle-v6.tar.gz` (`SHA-256`: `9fbda6cfc52f0b4c88955327def2de9d47ff7ed45d4a1d7e06641fd051f9a3a6`)
- `SHA256SUMS.txt` (`61` verified digests, `SHA-256`: `396c0f5caaf80e7a3a0ee59cb7e04b47ea218113317dbe6856e2431edc67e61e`)
- `README_TESTERS_ES_EN.md` (`SHA-256`: `e955b5f8e0b6d30b06ffb31731bb6fc2eb8d13ba64091f94e2a6ee19d96096ce`)
- `detect_and_match_openmax_image.py` (`v3` `95`-board selector, `SHA-256`: `8f4f6827c721bebcac712f441493e6b88490f3af95d396245d94e1a8fc8e4def`)
- `fmx_xc_airprism_filterd.sh` (`GPIO 13..16` 2-bank daemon, `SHA-256`: `91698b102cdb1256fce7ca2ab35afad4348f0a0e6a0f0273cfab1825e4d511a4`)

## 2. Indexed Image Families (`54` Total SquashFS Images)
- **`WA` `v7` (`16` Universal Images in `firmware/openwrt/wa_universal_kit_v7/`)**: `PowerBeam 5AC Gen2` (`0xe3d6`), `LiteBeam 5AC Gen2` (`0xe7f9`), `LAP-120` (`0xe8e5`), `NanoStation 5AC Loco` (`0xe7fa`) AP & STA `factory.bin` + `sysupgrade.bin` embedding `99-fmx-wa-universal-champion-v4` (`fq_limit=512`, `tcp_early_retrans=4`, `vm.min_free_kbytes=4096`).
- **`XC` Passive (`12` Images in `firmware/openwrt/xc_passive_kit_v1/`)**: `0xe1f5`, `0xe3d5`, `0xe5f5`, `0xe4f5`, `0xe3d7`, `0xe3d8` (`16` records).
- **`XC` Active-`AirPrism` (`14` Images in `firmware/openwrt/xc_active_airprism_kit_v1/`)**: `0xe3f5`, `0xe7e5`, `0xe7e6`, `0xe7e8`, `0xe7e7`, `0xe7e9`, `0xdc97` (`18` records) embedding `/usr/sbin/fmx_xc_airprism_filterd.sh` + `99-fmx-xc-universal-champion-v2`.
- **`XW` `64 MB` (`12` Images in `firmware/openwrt/xw_64mb_kit_v1/`)**: `6` `ath9k` profiles covering `29` production `XW` `board.sysid`s with `END.` full-image CRC32 signing + `XM` `32 MB` OOM safety gate (`BLOCK_OPENWRT_24_10_4_ON_32MB_XM`).
