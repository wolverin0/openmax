<!-- doc-head: STAGE164A_WA_SQUASHFS_V5_R15_CHAMPION_BAKE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.



# Stage 164A — Universal `WA` SquashFS v5 Re-Bake (`R1..R15` `60`-Window Champion)

- **Claim Status**: `CONFIRMED`
- **Attribution**: `Linux / mac80211 / ath10k / hardware`
- **Memory-Master Claim**: `<memorymaster-id>` (`155043`, `scope="project:futuramax"`)
- **Safety Boundary**: Zero contact with live radios `.241`, `.242`, `.20`, or `.250`.

## 1. Executive Summary
Following the `Stage 145A` (`R13..R15`) counterbalanced `A1 -> B1 -> A2 -> B2` live discovery on `WA` (`AR9342` `535 MHz` + `QCA9882` + `64 MB` DDR2 RAM), **Stage 164A** bakes the `15`-round (`60`-window) Universal `WA` Champion (`99-fmx-wa-universal-champion` + `99-fmx-pbe5ac-ptp*`) directly into the `OpenWrt 24.10.4` (`Linux 6.6.110`) `SquashFS` (`hsqs`) rootfs on the build VM (`198.18.0.62` via `mksquashfs 4.6.1 -comp xz -b 256k -no-xattrs -all-root`).

## 2. Baked `R1..R15` Champion Parameters (`CONFIRMED`)
| Parameter | Value | Physical / Kernel Mechanism (`Linux / mac80211 / ath10k`) |
| :--- | :--- | :--- |
| `vm.min_free_kbytes` | `4096` (`4 MB`) | Reserves `4 MB` atomic page pool for `ath10k` HTT RX ring refill & `sk_buff` allocations; lifts free RAM under heavy load from `1.35 MB` to `10.23 MB` (CPE) / `16.08 MB` (AP). |
| `aql_threshold` | `4000` us | Tightens `mac80211` AQL station airtime threshold from `4500` us to `4000` us (`+43.87%` Pareto composite gain). |
| `AP` / `STA` `fq_quantum` | `3028` B / `1514` B | Asymmetric `2xMTU` on AP (`phy*-ap0`, `+8.48%` TCP goodput) and `1xMTU` on STA (`phy*-sta0`, sub-ms uplink voice serialization). |
| `fq_limit` / `fq_memory_limit` | `1024` pkts / `3,145,728` B (`3 MB`) | Bounds `mac80211` `fq` memory footprint on `64 MB` RAM boards. |
| `eth0` / `br-lan` `fq_codel` | `quantum 1514 target 5ms interval 100ms limit 1024 memory_limit 3145728 ecn` | End-to-end wired/bridge AQM alignment with wireless `fq`. |
| `eth0` BQL | `4542` / `36288` / `600` ms | `ag71xx` DMA ring byte queue limits (`3xMTU` min, `24xMTU` max). |
| `dev_weight` / `netdev_budget` | `48` / `480` (`6000` us) | Prevents NAPI softirq starvation on single-core `AR9342`. |
| `tcp_limit_output_bytes` | `65536` (`64 KB`) | Caps local TCP Small Queues (`TSQ`). |
| `mac80211.ko` | `mac80211_teb_4addr_v3_6.6.110.ko` (`fe4f730f...`) | `WLAN_STA_AUTHORIZED` `BIT(3)`-gated `WLAN_STA_4ADDR_EVENT` + `ETH_P_TEB 0x6558` decap. |

## 3. Re-Baked Image Matrix (`20` Images Verified)
- **`firmware/openwrt/pbe5ac_gen2_ptp_kit/` (`4` images)**:
  - `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-ap-241.bin`
  - `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-factory-sta-242.bin`
  - `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-ap-241.bin`
  - `openwrt-24.10.4-ubnt_powerbeam-5ac-gen2-squashfs-sysupgrade-sta-242.bin`
- **`firmware/openwrt/wa_universal_kit_v34/` (`16` images)**:
  - `powerbeam-5ac-gen2` (`0xe3d6`), `litebeam-5ac-gen2` (`0xe7f9`), `lap-120` (`0xe7f5`/`0xe8e5`), `nanostation-ac-loco` (`0xe7f7`/`0xe7fa`) (`factory-ap`, `factory-sta`, `sysupgrade-ap`, `sysupgrade-sta`).
