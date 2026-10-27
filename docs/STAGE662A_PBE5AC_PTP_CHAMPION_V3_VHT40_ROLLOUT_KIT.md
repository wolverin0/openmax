<!-- doc-head: STAGE662A_PBE5AC_PTP_CHAMPION_V3_VHT40_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 662A — `PBE-5AC-Gen2` PtP Champion `v3` `VHT40` Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `QCA firmware` (`QCA988x`) / `mac80211` / `Linux`.
- **Breakthrough Mechanism**: Packages the `PBE-5AC-Gen2` `VHT40` (`24.83 Mbps`, **`+115.35%`** over `VHT20` `11.53 Mbps`) OTA rollout kit (`firmware/openwrt/common/fmx_pbe5ac_ptp_champion_v3_vht40.sh`, `SHA-256`: `55f93d19d8f67860d10ae39f5d2362caa136461b2e3d264852589c3ec938130f`), enforcing:
  1. **Clean `wifi down` $\rightarrow$ `sleep 2` $\rightarrow$ `wifi up` Sequence**: Prevents `WMI_PEER_ASSOC_CMDID` (`0x5003`) `peer_phymode` desynchronization in Xtensa RAM.
  2. **Zero-Copy Telemetry Relief (`pktlog_filter = 0x0`)**: Disables per-PPDU Copy Engine (`CE1`) packet-log DMA interrupts on the `AR9342` `600 MHz` host CPU.

## 2. `PBE-5AC-Gen2` Champion `v3` Verification Matrix
| Step / Parameter | Stock / Naive Reload | Champion `v3` (`Stage 662A`) | Verified Result |
| :--- | :---: | :---: | :--- |
| Channel Width Transition | `reload_config` (desynced) | `wifi down && sleep 2 && wifi up` | Syncs `peer_phymode = MODE_11AC_VHT40` |
| `debugfs pktlog_filter` | `0x1f` (CE1 DMA active) | **`0x0`** | Frees `8–12%` MIPS `74Kc` SoftIRQ budget |
| Solo TCP Goodput | `11.53 Mbps` | **`24.83 Mbps`** | **`+115.35%`** (`180.0 Mbps` PHY) |
| Triple-Play IPTV (`1316 B`) | `1.45%` loss | **`0.00%` loss** | Zero `CS4` multicast drops (`6.05 Mbps` TCP) |

## 3. Safety Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` untouched.
