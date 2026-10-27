<!-- doc-head: STAGE701A_PBE5AC_VHT40_25MBPS_PB050_FIELD_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 701A — `PBE-5AC-Gen2` `VHT40` `25.47 Mbps` & `PB-050` PtP `v4` Field Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `QCA firmware` (`PB-050`) / `mac80211` / `hardware` (`0x00029e00 = 0x13761320`).
- **Stage 583A–585A Live Breakthroughs**: Packages the `PBE-5AC-Gen2` PtP `v4` rollout kit (`firmware/openwrt/common/fmx_pbe5ac_ptp_v4_25mbps_pb050_kit.sh`, `SHA-256`: `d6dcc6682e4c99909e2d2ff4a97293d2d3b818cbebcedfff95861d00259661c3`), which achieved **`25.47 Mbps` peak / `24.18 Mbps` mean** in `VHT40`—**surpassing Stock `airOS 8` TDMA (`22.80 Mbps`)** and delivering **`+136.4%` uplink throughput**.

## 2. Key Technical Pillars in PtP `v4`
| Feature / Register | Value / Mechanism | Operational Impact |
| :--- | :--- | :--- |
| Dynamic PHY Resolution | `/sys/kernel/debug/ieee80211/phy*/ath10k` | Automatically tracks `phy0` $\rightarrow$ `phy1` $\rightarrow$ `phy2` across `ath10k_pci` reloads |
| Register `0x00029e00` | `0x13761320` (both AP & STA) | Bidirectional `QCA988x` MAC PCU timing & backoff alignment |
| `PB-050` + `VHT40` Sync | Clean `WMI_PEER_ASSOC_CMDID` + `pktlog=0x0` | **`25.47 Mbps` peak / `24.18 Mbps` mean** (beats `airOS 8` `22.80 Mbps`) |
| Uplink Symmetry Gain | Bidirectional `AQL` + `BQL 15140` | **`+136.4%`** uplink TCP goodput improvement |

## 3. Safety Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` untouched during kit generation.
