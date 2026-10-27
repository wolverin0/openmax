<!-- doc-head: Stage 307A Unified Multifamily Selector v3 (100% 95-Board WA + XC Passive & Active-AirPrism + XW Coverage) -->
Upgrades detect_and_match_openmax_image.py to v3 achieving 100% OpenWrt 24.10.4 SquashFS coverage across all 95 WA, XC, and XW boards.
<!-- /doc-head -->

# Stage 307A — Unified Multifamily Selector `v3` (`95`-Board Complete Coverage)

- **Status**: `CONFIRMED` (`live_radios_241_242_20_250_touched = false`, `memory-master`: `mm-efb4`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `ath9k` / `hardware`
- **Receipt**: [`stage307a_selector_v3_95board_complete.json`](../artifacts/autoresearch/stage307a_selector_v3_95board_complete.json)

## 1. 95-Board Complete Coverage Summary (`detect_and_match_openmax_image.py` `v3`)
- **`WA` (`31` `ubnthal.ko` records / `17` unique `sysid`s)**: Matched to `wa_universal_kit_v34` + `wa_universal_kit_v7` (`Champion v4`: `fq_limit=512`, `tcp_early_retrans=4`, `vm.min_free_kbytes=4096`).
- **`XC` Passive (`16` `ubnthal.ko` records / `6` unique `sysid`s)**: Matched to `firmware/openwrt/xc_passive_kit_v1/` (`0xe1f5`, `0xe3d5`, `0xe5f5`, `0xe4f5`, `0xe3d7`, `0xe3d8`).
- **`XC` Active-`AirPrism` (`18` `ubnthal.ko` records / `7` unique `sysid`s)**: Matched to `firmware/openwrt/xc_active_airprism_kit_v1/` (`MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` embedding `/usr/sbin/fmx_xc_airprism_filterd.sh` + `Mode B` fallback option).
- **`XW` `64 MB` (`30` `ubnthal.ko` records / `29` production `sysid`s)**: Matched to `firmware/openwrt/xw_64mb_kit_v1/` (`6` profiles, `< 6.7 MB` `END.` CRC32 signed).
- **`XM` `32 MB` Safety Gate (`0xe005`, `0xe0a5`, `0xe2d5`, `0xe4a2`)**: Fail-closed `BLOCK_OPENWRT_24_10_4_ON_32MB_XM` (`MODE_B_AIROS6_RC_POSTSTART_FALLBACK_32MB_OOM_PROTECTION`).

## 2. Active-`AirPrism` `XC` 7-Sysid (`18`-Record) Selector `v3` Matches
| `board.sysid` | Models | Base Profile | Factory Image (`SHA-256` Prefix) | Deployment Mode |
| :--- | :--- | :--- | :--- | :--- |
| `0xe3f5` | `R5AC-PTP, R5AC-PTMP` | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe3f5-r5ac-ptp-ptmp-squashfs-factory.bin` (`4127cf163a900fb9...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
| `0xe7e5` | `R5AC-PRISM` | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe7e5-r5ac-prism-squashfs-factory.bin` (`3a9c6f658e58598f...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
| `0xe7e6` | `PS-5AC` | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-airprism-0xe7e6-ps-5ac-e7e6-squashfs-factory.bin` (`a71094d1afe2af63...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
| `0xe7e8` | `PS-5AC` | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-airprism-0xe7e8-ps-5ac-e7e8-squashfs-factory.bin` (`e62eb9a6a20f5c27...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
| `0xe7e7` | `RP-5AC-Gen2` | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe7e7-rp-5ac-gen2-e7e7-squashfs-factory.bin` (`a0d7bb78e655e8d8...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
| `0xe7e9` | `RP-5AC-Gen2` | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe7e9-rp-5ac-gen2-e7e9-squashfs-factory.bin` (`5f0ed5d95e7087f5...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
| `0xdc97` | `Prism-AP` | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-airprism-0xdc97-prismap-5ac-squashfs-factory.bin` (`0d1d6a8aa17ced96...`) | `MODE_A_FULL_OPENWRT_24_10_4_SQUASHFS_WITH_AIRPRISM_FILTERD` |
