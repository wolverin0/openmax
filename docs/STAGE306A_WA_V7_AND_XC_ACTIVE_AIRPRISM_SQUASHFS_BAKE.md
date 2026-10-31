<!-- doc-head: Stage 306A WA v7 (Stage 214A 100-Window Champion v4) & XC Active-AirPrism 7-Sysid Full SquashFS Bake -->
Full SquashFS (hsqs) bake on 198.18.0.62 of WA v7 (fq_limit=512, tcp_early_retrans=4) and Active-AirPrism XC 7-sysid images.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 306A — `WA` `v7` & Active-`AirPrism` `XC` `7`-Sysid (`18`-Record) Full SquashFS (`hsqs`) Bake

- **Status**: `CONFIRMED` (`live_radios_241_242_20_250_touched = false`, `memory-master`: `<memorymaster-id>`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `ath9k` / `hardware`
- **Receipt**: [`stage306a_wa_v7_and_xc_active_airprism_squashfs_bake.json`](../artifacts/autoresearch/stage306a_wa_v7_and_xc_active_airprism_squashfs_bake.json)

## 1. Propagated `Stage 214A` (`100`-Window) Champion Profiles
- `99-fmx-wa-universal-champion-v4` (`SHA-256`: `06d5d9ad1ab39bdd175090c24795024ff4a5c98bc0dcbd40791cb3d11b23e055` — `FMX_FQ_LIMIT=512`, `FMX_TCP_EARLY_RETRANS=4`, `FMX_MIN_FREE_KBYTES=4096`)
- `99-fmx-xc-universal-champion-v2` (`SHA-256`: `572145e5ec6defdba869d7c98fe1ac0f8396829ed20808017cf0e30effcf1aab` — `FMX_XC_FQ_LIMIT=512`, `FMX_XC_TCP_EARLY_RETRANS=4`, `FMX_XC_MIN_FREE_KBYTES=6144` + `fmx_xc_airprism_filterd.sh`)
- `99-fmx-xw-xm-ath9k-champion-v2` (`SHA-256`: `c2ea8c4f4c77bdf3be74dcd46d763de4840e1efe5c713c688c0abfd5ea28a387` — `FMX_FQ_LIMIT=512`, `FMX_TCP_EARLY_RETRANS=4`, `FMX_MIN_FREE_KBYTES=3072`)

## 2. Baked `WA` `v7` SquashFS Images (`firmware/openwrt/wa_universal_kit_v7/`)
| Board Slug | Factory AP (`OPEN` + `ENDS`) | Factory STA (`OPEN` + `ENDS`) | Sysupgrade AP (`FWx0`) | Sysupgrade STA (`FWx0`) |
| :--- | :--- | :--- | :--- | :--- |
| `powerbeam-5ac-gen2` | `openwrt-24.10.4-powerbeam-5ac-gen2-v7-factory-ap.bin` (`bcbe0c22a728f8...`) | `openwrt-24.10.4-powerbeam-5ac-gen2-v7-factory-sta.bin` (`c22c9965c16e3e...`) | `openwrt-24.10.4-powerbeam-5ac-gen2-v7-sysupgrade-ap.bin` (`30dd4d494b8d78...`) | `openwrt-24.10.4-powerbeam-5ac-gen2-v7-sysupgrade-sta.bin` (`a2da2926a23ff4...`) |
| `litebeam-5ac-gen2` | `openwrt-24.10.4-litebeam-5ac-gen2-v7-factory-ap.bin` (`648d891bfcd2aa...`) | `openwrt-24.10.4-litebeam-5ac-gen2-v7-factory-sta.bin` (`6bb8ccd277240e...`) | `openwrt-24.10.4-litebeam-5ac-gen2-v7-sysupgrade-ap.bin` (`4e2c67cfdda66c...`) | `openwrt-24.10.4-litebeam-5ac-gen2-v7-sysupgrade-sta.bin` (`0c4cbd2701d590...`) |
| `lap-120` | `openwrt-24.10.4-lap-120-v7-factory-ap.bin` (`6e58b147be9548...`) | `openwrt-24.10.4-lap-120-v7-factory-sta.bin` (`66a7437eb64305...`) | `openwrt-24.10.4-lap-120-v7-sysupgrade-ap.bin` (`733519edf07e9a...`) | `openwrt-24.10.4-lap-120-v7-sysupgrade-sta.bin` (`60744ec5f10a77...`) |
| `nanostation-ac-loco` | `openwrt-24.10.4-nanostation-ac-loco-v7-factory-ap.bin` (`ec22d83537df32...`) | `openwrt-24.10.4-nanostation-ac-loco-v7-factory-sta.bin` (`e1597129367f92...`) | `openwrt-24.10.4-nanostation-ac-loco-v7-sysupgrade-ap.bin` (`e4d30f35377ebb...`) | `openwrt-24.10.4-nanostation-ac-loco-v7-sysupgrade-sta.bin` (`5455ef37faacc3...`) |

## 3. Baked Active-`AirPrism` `XC` 7-Sysid (`18`-Record) Images (`firmware/openwrt/xc_active_airprism_kit_v1/`)
| `board.sysid` | Models (`Records`) | Base Profile | Factory Image (`OPEN` + `ENDS` + `FWx0`) | Sysupgrade Image (`FWx0`) |
| :--- | :--- | :--- | :--- | :--- |
| `0xe3f5` | `R5AC-PTP, R5AC-PTMP` (`3`) | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe3f5-r5ac-ptp-ptmp-squashfs-factory.bin` (`4127cf163a900f...`) | `openwrt-24.10.4-xc-airprism-0xe3f5-r5ac-ptp-ptmp-squashfs-sysupgrade.bin` (`7c952d126e579d...`) |
| `0xe7e5` | `R5AC-PRISM` (`2`) | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe7e5-r5ac-prism-squashfs-factory.bin` (`3a9c6f658e5859...`) | `openwrt-24.10.4-xc-airprism-0xe7e5-r5ac-prism-squashfs-sysupgrade.bin` (`d5013ba9bd3bde...`) |
| `0xe7e6` | `PS-5AC` (`3`) | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-airprism-0xe7e6-ps-5ac-e7e6-squashfs-factory.bin` (`a71094d1afe2af...`) | `openwrt-24.10.4-xc-airprism-0xe7e6-ps-5ac-e7e6-squashfs-sysupgrade.bin` (`df651205dd7208...`) |
| `0xe7e8` | `PS-5AC` (`1`) | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-airprism-0xe7e8-ps-5ac-e7e8-squashfs-factory.bin` (`e62eb9a6a20f5c...`) | `openwrt-24.10.4-xc-airprism-0xe7e8-ps-5ac-e7e8-squashfs-sysupgrade.bin` (`df651205dd7208...`) |
| `0xe7e7` | `RP-5AC-Gen2` (`4`) | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe7e7-rp-5ac-gen2-e7e7-squashfs-factory.bin` (`a0d7bb78e655e8...`) | `openwrt-24.10.4-xc-airprism-0xe7e7-rp-5ac-gen2-e7e7-squashfs-sysupgrade.bin` (`e58f3a3587e496...`) |
| `0xe7e9` | `RP-5AC-Gen2` (`3`) | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-airprism-0xe7e9-rp-5ac-gen2-e7e9-squashfs-factory.bin` (`5f0ed5d95e7087...`) | `openwrt-24.10.4-xc-airprism-0xe7e9-rp-5ac-gen2-e7e9-squashfs-sysupgrade.bin` (`e58f3a3587e496...`) |
| `0xdc97` | `Prism-AP, PrismAP-5AC` (`2`) | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-airprism-0xdc97-prismap-5ac-squashfs-factory.bin` (`0d1d6a8aa17ced...`) | `openwrt-24.10.4-xc-airprism-0xdc97-prismap-5ac-squashfs-sysupgrade.bin` (`7fc492e9270e38...`) |
