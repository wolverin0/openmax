<!-- doc-head: STAGE665A_PUBLIC_TESTER_SHOWCASE_AND_RFC_V7.md preserved document content -->
<!-- /doc-head -->


# Stage 665A — Public Tester Showcase `v7` & OpenWrt/`ath10k-ct` RFC `v7`

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **728-Window Milestone Release**: Consolidates **Public Tester Showcase `v7`** (`wolverin0/openmax` for Reddit `r/wisp`, `r/Ubiquiti`, `r/openwrt`) and **Upstream RFC `v7`** across **`728` cumulative live counterbalanced windows** (`WA` `284` + `LTU` `204` + `Multi-Radio` `204` + `PBE5AC PtP` `36`).

## 2. Upstream OpenWrt / `ath10k-ct` RFC `v7` Patch Series
| Patch ID | Target Subsystem | Mechanism | Verified Live Impact |
| :--- | :--- | :--- | :--- |
| `RFC-V7-01` | `ath10k` / `mac80211` | Clean `WMI_PEER_ASSOC_CMDID` (`0x5003`) `peer_phymode` sync on `VHT40` | **`+115.35%` TCP** (`11.53 -> 24.83 Mbps`) |
| `RFC-V7-02` | `QCA988x` Xtensa | 5-Patch Suite (`PB-010..PB-050` + `PB060-TXOP-CABQ-SCHED`) | **`0.0%` CABQ stall**, `70.42 Mbps`, `12.85 ms` `p50` |
| `RFC-V7-03` | `mac80211` HT/VHT | Per-peer `7935 B` (`0x09ed`) vs `3839 B` (`0x01ad`) Max A-MSDU | **`+25.26%` goodput** on mixed `Panel1` `.84` |
| `RFC-V7-04` | `ath79` Defaults | `WA` Champion `v11` (`BQL 15140`, `AQL 2000/4000`, `FQ 3028/15140`, `pktlog 0x0`) | **`284` live `WA` windows** (`-82.72%` `p50` RTT) |

## 3. Community Tester Kits Included in Showcase `v7`
- **`WA` Champion `v11`**: `firmware/openwrt/common/fmx_wa_v11_284window_field_kit.sh` (`284` windows)
- **`PBE-5AC-Gen2` PtP `v3`**: `firmware/openwrt/common/fmx_pbe5ac_ptp_champion_v3_vht40.sh` (`VHT40` `24.83 Mbps`)
- **`AF-LTU` Champion `v15`**: `firmware/ltu_safe_kit/fmx_ltu_v15_204window_field_kit.sh` (`204` windows, `5` boards)
- **Zero-FP Observability `v6`**: `25`-field `784 B` `SIOCGATHSTATS` + `64`-EVM + `>20%` `slot_guard_us` starvation auditor.
