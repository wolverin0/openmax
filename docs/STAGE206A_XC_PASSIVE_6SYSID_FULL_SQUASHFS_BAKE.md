<!-- doc-head: Stage 206A Passive XC 6-Sysid (16-Record) Full SquashFS (hsqs) Bake on 198.18.0.62 -->
Full SquashFS (hsqs) rootfs bake and hardware safety gate verification on 198.18.0.62.
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.
# Stage 206A — Passive `XC` 6-Sysid (`16`-Record) Full SquashFS (`hsqs`) Bake

- **Status**: `CONFIRMED` (`live_radios_241_242_20_250_touched = false`, `memory-master`: `<memorymaster-id>`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `hardware` (`QCA9558` 720 MHz + `QCA9880-BR4A` 5 GHz PCIe + `128 MB` DDR2)
- **Receipt**: [`stage206a_xc_passive_6sysid_full_squashfs_bake.json`](../artifacts/autoresearch/stage206a_xc_passive_6sysid_full_squashfs_bake.json)

## 1. Embedded SquashFS (`hsqs`) Rootfs Payload (`mksquashfs 4.6.1 -comp xz -b 256k`)
- `/etc/hotplug.d/net/99-fmx-xc-universal-champion` (`SHA-256`: `a66c7d0664fe7ea87989b4adaee14df1367fbb6714f97c306d4e667fbb7ed08e` — `vm.min_free_kbytes=6144`, `FQ_MEM_LIMIT=8388608`, `FQ_LIMIT=2048`, `AP_FQ_QUANTUM=3028`, `STA_FQ_QUANTUM=1514`, `AQL_THRESHOLD=4000`, `BQL_MIN=6056`)
- `/lib/modules/6.6.110/mac80211.ko` (`SHA-256`: `fe4f730fccaa68848a70c952e40c0438b32d413993f22887a0e72fed5eebaae6` — `ETH_P_TEB 0x6558` decap + `WLAN_STA_AUTHORIZED` `BIT(3)`-gated 4-addr event)
- `/usr/sbin/fmx_pbe5ac_admitter.sh` v2 (`SHA-256`: `f8c7b054b241b0e6b901abcf96e8a777d62bf30a732e6eb05082ff47339285eb` — single-loop FIFO admitter)
- `/usr/sbin/fmx_ptp_rollback_watchdog.sh` + `/etc/rc.local`

## 2. Baked Passive `XC` 6-Sysid (`16`-Record) Images (`firmware/openwrt/xc_passive_kit_v1/`)
| `board.sysid` | Models (`ubnthal.ko` Records) | Base Profile | Factory Image (`OPEN` + `PART` + `ENDS` + `FWx0`) | Sysupgrade Image (`FWx0` Signed) |
| :--- | :--- | :--- | :--- | :--- |
| `0xe1f5` | `R5AC-Lite` (`4`) | `ubnt_rocket-5ac-lite` | `openwrt-24.10.4-xc-0xe1f5-r5ac-lite-squashfs-factory.bin` (`0ba121df6483161e...`) | `openwrt-24.10.4-xc-0xe1f5-r5ac-lite-squashfs-sysupgrade.bin` (`7c1fb2bfa1d0543a...`) |
| `0xe3d5` | `PBE-5AC-500, PBE-5AC-500-ISO` (`6`) | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-0xe3d5-pbe-5ac-500-squashfs-factory.bin` (`7ae9b39eb61f3d88...`) | `openwrt-24.10.4-xc-0xe3d5-pbe-5ac-500-squashfs-sysupgrade.bin` (`2cc752ef4ccde29b...`) |
| `0xe5f5` | `PBE-5AC-620` (`3`) | `ubnt_powerbeam-5ac-500` | `openwrt-24.10.4-xc-0xe5f5-pbe-5ac-620-squashfs-factory.bin` (`b4eb4416c9d9ee5c...`) | `openwrt-24.10.4-xc-0xe5f5-pbe-5ac-620-squashfs-sysupgrade.bin` (`92b2153f4fe9a6f0...`) |
| `0xe4f5` | `NBE-5AC-19` (`1`) | `ubnt_nanobeam-ac-xc` | `openwrt-24.10.4-xc-0xe4f5-nbe-5ac-19-xc-squashfs-factory.bin` (`78a31a92c44fec66...`) | `openwrt-24.10.4-xc-0xe4f5-nbe-5ac-19-xc-squashfs-sysupgrade.bin` (`f18a381f7d22dc69...`) |
| `0xe3d7` | `NBE-5AC-Gen2` (`1`) | `ubnt_nanobeam-ac-xc` | `openwrt-24.10.4-xc-0xe3d7-nbe-5ac-gen2-xc-squashfs-factory.bin` (`b47ce199446c8089...`) | `openwrt-24.10.4-xc-0xe3d7-nbe-5ac-gen2-xc-squashfs-sysupgrade.bin` (`9e3e830cd7df8fc7...`) |
| `0xe3d8` | `NS-5ACL` (`1`) | `ubnt_nanobeam-ac-xc` | `openwrt-24.10.4-xc-0xe3d8-ns-5acl-xc-squashfs-factory.bin` (`806714750d7fff87...`) | `openwrt-24.10.4-xc-0xe3d8-ns-5acl-xc-squashfs-sysupgrade.bin` (`43eb48ceb67e1774...`) |

## 3. Active `AirPrism` (`18` Records) Safety Gate
- Active `AirPrism` `XC` boards (`has_airprism_bit30 == true`, e.g. `0xe7e9` `RP-5AC-Gen2`, `0xe7e8` `PS-5AC`) require `GPIO 13..16` filter bank control (`ubnt_prism_filters` at `umac.ko+0x001510`) and automatically select `Mode B` (`rc.poststart` + `99-fmx-xc-universal-champion`) until the userspace `GPIO 13..16` filter daemon is enabled.
