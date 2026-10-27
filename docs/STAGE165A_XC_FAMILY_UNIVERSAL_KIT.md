<!-- doc-head: STAGE165A_XC_FAMILY_UNIVERSAL_KIT.md preserved document content -->
<!-- /doc-head -->



# Stage 165A — Universal `XC` (`QCA9558` + `QCA9880` `128 MB` RAM) OpenWrt `24.10.4` Champion Kit

- **Claim Status**: `CONFIRMED`
- **Attribution**: `Linux / mac80211 / ath10k / hardware`
- **Memory-Master Claim**: `mm-37fa` (`155044`, `scope="project:futuramax"`)
- **Kit Directory**: [`firmware/openwrt/xc_family_universal_kit/`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/xc_family_universal_kit/)

## 1. Hardware Architecture & Scaling Rationale (`XC` vs `WA`)
Unlike `WA` boards (`AR9342` `535 MHz` + `QCA9882` + `64 MB` DDR2 RAM), Ubiquiti `XC` boards pair a `720 MHz` `QCA9558` MIPS 74Kc SoC with `128 MB` DDR2 RAM and a `QCA9880-BR4A` 5 GHz 802.11ac radio (plus dedicated `airPrism` active RF filtering on `Rocket 5AC Prism Gen2` and `PrismStation 5AC`).
- **`vm.min_free_kbytes = 6144` (`6 MB`)**: Scales the atomic page reserve from `4 MB` (`WA`) to `6 MB` (`4.68%` of `128 MB` RAM) for zero page-allocation stalls during multi-CPE PtMP bursts.
- **`fq_memory_limit = 8388608` (`8 MB`) & `fq_limit = 2048` packets**: Doubles the `mac80211` `fq_codel` packet and byte ceiling relative to `WA` (`3 MB` / `1024` pkts) to support `30..60` PtMP CPEs per sector without premature tail drops.
- **Asymmetric `fq_quantum` (`AP=3028` / `STA=1514`) & `aql_threshold = 4000` us**: Preserves `2xMTU` AP burst aggregation and `1xMTU` STA uplink voice serialization with `AC_VO=300/600`, `AC_VI=1000/2000`, `AC_BE=2000/4000`, `AC_BK=500/1000`.
- **`eth0` BQL `6056 / 36288 / 600` ms**: Sets `limit_min = 6056` B (`4xMTU`) to match the faster `720 MHz` `QCA9558` Gigabit RGMII DMA drain rate.

## 2. Supported `XC` Board Matrix (`xc_board_manifest.json`)
| `sysid` | Ubiquiti Model | OpenWrt Board ID | RF / Antenna Profile |
| :--- | :--- | :--- | :--- |
| `0xe7f9` | `Rocket 5AC Prism Gen2` (`RP-5AC-Gen2`) | `ubnt,rocket-5ac-prism-gen2` | `QCA9880` 2x2 + `airPrism` + GPS |
| `0xe7f8` | `PrismStation 5AC` (`PrismAP-5AC`) | `ubnt,prismstation-5ac` | `QCA9880` 2x2 + `airPrism` horn + GPS |
| `0xe7f5` | `IsoStation 5AC` (`IS-5AC XC`) | `ubnt,isostation-5ac-xc` | `QCA9880` 2x2 die-cast horn |
| `0xe3f5` | `PowerBeam 5AC 500` (`PBE-5AC-500`) | `ubnt,powerbeam-5ac-500` | `QCA9880` 2x2 (27 dBi 500mm dish) |
| `0xe4f5` | `PowerBeam 5AC 620` (`PBE-5AC-620`) | `ubnt,powerbeam-5ac-620` | `QCA9880` 2x2 (29 dBi 620mm dish) |
| `0xe6e5` | `NanoBeam 5AC 19` (`NBE-5AC-19`) | `ubnt,nanobeam-ac-xc` | `QCA9880` 2x2 (19 dBi dual-Eth) |

## 3. Packaged Deliverables
1. [`firmware/openwrt/xc_family_universal_kit/99-fmx-xc-universal-champion`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/xc_family_universal_kit/99-fmx-xc-universal-champion) (dual-mode OpenWrt `24.10.4` + Stock `airOS 8` `XC` `rc.poststart`).
2. [`firmware/openwrt/xc_family_universal_kit/xc_board_manifest.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/xc_family_universal_kit/xc_board_manifest.json).
3. `firmware/openwrt/xc_family_universal_kit/sysupgrade-overlay-xc-universal-v1.tar.gz` (bundles `99-fmx-xc-universal-champion`, `mac80211_teb_4addr_v3_6.6.110.ko`, `fmx_pbe5ac_admitter.sh` v2, and `fmx_ptp_rollback_watchdog.sh`).
