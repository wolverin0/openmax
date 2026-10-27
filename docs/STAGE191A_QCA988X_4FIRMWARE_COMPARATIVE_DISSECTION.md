<!-- doc-head: STAGE191A_QCA988X_4FIRMWARE_COMPARATIVE_DISSECTION.md preserved document content -->
<!-- /doc-head -->


# Stage 191A — Comparative Dissection of All 4 `QCA988x` Target Firmwares (`CONFIRMED`)

## 1. Executive Summary & Attribution
- **Claim Status**: `CONFIRMED` (`live_devices_touched = False`; 100% offline binary dissection).
- **Attribution**: `QCA firmware` + `proprietary airMAX/LTU module` + `ath10k`.
- **Mask ROM `LITBASE` Hardware Invariant (`0x009bb001`, `CONFIRMED`)**:
  - All 4 `QCA988x` target firmwares begin at `BEGINADDR = 0x00983c00` with identical entrypoint bytes (`366100210014a101148812b10214a718`).
  - At `0x00983c03`, `21 00 14` (`l32r a2, imm16=0x1400`) loads `seg[0][0]` (`0x00980000`), proving `LITBASE = 0x009bb001` (`0x009bb000 + ((0x1400 - 0x10000) << 2) = 0x00980000`).

## 2. 4-Firmware `SGMT` Segment & Memory Map Comparison (`CONFIRMED`)
| Firmware Binary | Compressed (`B`) | Uncompressed (`B`) | `seg[0]` `.lit4` (`0x00980000`) | `seg[1]` `.rodata` (`0x0040b000`) | `seg[2]` `.data` (`VA` / `Size`) | `seg[3]` `.text` (`0x00983c00`) | WMI Literal Count |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `athwlan_AR9888v2_ptp_bin` | `214,299` | `261,516` | `5,720 B` | `7,384 B` | `0x0040cce0` (`10,888 B`) | `237,524 B` | `72` |
| `athwlan_AR9888v2_ptmp_ap_bin` | `250,900` | `304,572` | `6,328 B` | `8,600 B` | `0x0040d1a0` (`10,888 B`) | `278,756 B` | `72` |
| `athwlan_AR9888v2_ptmp_sta_bin` | `233,509` | `284,972` | `6,060 B` | `8,772 B` | `0x0040d250` (`10,888 B`) | `259,252 B` | `72` |
| OpenWrt `firmware-2.bin` (`10.1-ct`) | `197,537` (+`7,140` OTP) | `228,588` | `5,484 B` | `3,336 B` | `0x0040bd10` (`3,044 B`) | `216,724 B` | `83` |

## 3. Exact 32-Slot Platform Hook Tables (`seg[2]+0x2928` vs `seg[2]+0x29a8`, `CONFIRMED`)
- Every Ubiquiti `QCA988x` firmware allocates an identical `10,888`-byte `.data` segment (`seg[2]`) — **`7,844` bytes larger** than OpenWrt `10.1-ct`'s `3,044`-byte `.data` — to store the `ubnt_poll` TDMA state machine and two 32-pointer hook tables:
  1. **`Initial Hooks` (`seg[2] + 0x2928`, `15/32` active, `17/32` NULL)**:
     - `ptp_bin`: `0x0040f608` (referenced by literal `0x00981270` in `ubnt_poll_ptp_init`).
     - `ptmp_ap_bin`: `0x0040fac8` (referenced by literal `0x00981298` in `ubnt_poll_ptmp_init`).
     - `ptmp_sta_bin`: `0x0040fb78` (referenced by literal `0x00981298` in `ubnt_poll_ptmp_init`).
     - Active slots (`15`): `[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 19, 24]`; NULL slots (`17`): `[12, 14, 15, 16, 17, 18, 20, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31]`.
  2. **`Full Polling Hooks` (`seg[2] + 0x29a8`, `32/32` active, `0/32` NULL)**:
     - `ptp_bin`: `0x0040f688` (`0x009afc94..0x009b0f64`, installed by `platform_install_hooks` `0x009af2f8` on `HT_COMM` `msg_id=12` `polling_enabled=1`, uninstalled by `platform_uninstall_hooks` `0x009af2c4` on `polling_enabled=0`).
     - `ptmp_ap_bin`: `0x0040fb48` (`0x009b043c..0x009b2800`).
     - `ptmp_sta_bin`: `0x0040fbf8` (`0x009b0468..0x009b2858`).
  3. **OpenWrt `firmware-2.bin` (`10.1-ct-8x-__fW-022-ecad3248`) & `firmware-5.bin` (`10.2.4`)**:
     - `0/32` Ubiquiti polling hooks; adds Candela WMI extensions (`0x9066` `WMI_PDEV_SET_SPECIAL_CMDID`, `0x9067`, `0x9070`, `0x9071`) while freeing `75,984 B` (`74.2 KiB`) of target SRAM vs `ptmp_ap_bin` for additional MSDU/peer descriptors (`msdu-desc: %d sw-crypt: %d ct-sta: %d`).

## 4. WMI/HTT Descriptor Rings, TX Rate-Control & RX Decap Matrix (`CONFIRMED`)
- **HTT H2T RX Ring Configuration (`umac.ko` `htt_h2t_rx_ring_cfg_msg_ll` @ `0x0d5298..0x0d5488`)**:
  - Emits `HTT_H2T_MSG_TYPE_RX_RING_CFG` (`0x0102` at `0x0d5380`) with 10 packed RX descriptor offsets (`0x14($s0)=0x003e002e` [`msdu_payload=62B`, `mac80211_hdr=46B`], `0x18($s0)=0x0019000f` [`ppdu_start=100B`, `ppdu_end=60B`], `0x1c($s0)=0x000e0003` [`mpdu_end=56B`, `mpdu_start=12B`], `0x20($s0)=0x00090006` [`msdu_end=36B`, `msdu_start=24B`], `0x24($s0)=0x00020001` [`frag_info=8B`, `rx_attention=4B`]).
- **TX Rate-Control Tables (`seg[1]` `.rodata+0x0000`)**:
  - All 4 firmwares place their 32-pointer base ROM/rate-control dispatch vtable at `0x0040b000` (`0x00984418..` in Ubiquiti `WA` vs `0x00984510..` in OpenWrt `10.1-ct` with `g_rc_rate_max_per_thr` tunable via `ct_special_7`).
- **RX Decapsulation Mode Matrix (`RAW` vs `NATIVE_WIFI` vs `ETHERNET`)**:
  - **`ptp_bin` (`is_ubnt_ptp=1`, `polling=1`)**: Target `Full Polling Hooks` (`0x0040f688`) decapsulate proprietary PtP TDMA containers into `ETHERNET`; host `ol_rx_deliver` (`0x0cd7c0`) has `pdev->host_80211_enable=0` and passes frames straight to `eth_type_trans`.
  - **`ptp_bin` (`is_ubnt_ptp=1`, `polling=0`) — `FMX-DISC-42` Catch-22**: Target uninstalls `0x0040f688` (`0x009af2c4`), passing raw 802.11 frames to host, while `__ol_ath_attach` (`0x0bc0f0`) forced `pdev->host_80211_enable=0`, so `ol_rx_deliver` (`0x0cd7c0`) skips 802.11-to-Ethernet conversion (`0x0cd7cc..0x0cdb4c`) and drops 100% of ARP/IPv4 frames!
  - **`ptmp_ap_bin` / `ptmp_sta_bin` (`is_ubnt_ptp=0`)**: `scn->host_80211_enable=1`; when `polling=0` (`allow_80211=1`), `ol_rx_deliver` (`0x0cd7cc..0x0cdb4c`) converts 802.11+LLC/SNAP to Ethernet on the host.
  - **OpenWrt `firmware-2.bin` (`10.1-ct`)**: Uses `ATH10K_HW_TXRX_NATIVE_WIFI` into `mac80211.ko` (`mac80211_teb_4addr_v3_6.6.110.ko`).
