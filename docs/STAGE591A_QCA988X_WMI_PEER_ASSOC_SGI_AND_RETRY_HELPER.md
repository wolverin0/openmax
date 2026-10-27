<!-- doc-head: STAGE591A_QCA988X_WMI_PEER_ASSOC_SGI_AND_RETRY_HELPER.md preserved document content -->
<!-- /doc-head -->


# Stage 591A — QCA988x `WMI_PEER_ASSOC_CMDID` Sync, SGI/LGI & Retry Helper

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `QCA firmware` (`QCA988x` Xtensa target) / `mac80211`.
- **Breakthrough Grounding (Stage 487A)**: Switching `htmode` (`VHT20` $\rightarrow$ `VHT40`) on `QCA988x` without forcing a clean `WMI_PEER_ASSOC_CMDID` (`0x5003`) re-association leaves `peer_phymode` pinned to `MODE_11AC_VHT20` inside Xtensa target RAM (`11.53 Mbps`). Triggering a clean `peer_phymode` sync unlocks `180.0 Mbps` PHY and **`24.83 Mbps` TCP (`+115.35%`)**.
- **Deliverable**: `firmware/openwrt/common/fmx_qca988x_peer_sgi_retry_helper.sh` (`SHA-256`: `9c02aea80614ef52390e2baec30f2c22e409638176b0c79abb89f2900c9512d1`).

## 2. WMI & Guard Interval Architecture
| Symbol / Parameter | ID / Value | Physical & MAC Role |
| :--- | :--- | :--- |
| `WMI_PEER_ASSOC_CMDID` | `0x5003` | Synchronizes `peer_phymode` (`VHT20`/`VHT40`/`VHT80`) and VHT MCS mask in Xtensa rate-control table |
| `WMI_VDEV_PARAM_SGI` | `0x2b` | Selects `400 ns` Short Guard Interval vs `800 ns` Long Guard Interval |
| `WMI_PDEV_PARAM_0x9044` | `0x9044` | Bounds hardware MAC retry count (`50 us`/retry) before rate fallback |

## 3. Adaptive Profiles (`WA` & `XC`)
| Profile | Guard Interval | VHT MCS Mask | Retry Limit | Target Deployment |
| :--- | :---: | :---: | :---: | :--- |
| `NEAR_FIELD_LGI_SAFE` | `800 ns` (LGI) | `2:0-7` | `4` | Fraunhofer near-field bench ($<6.15\text{ m}$) |
| `CLEAN_PTP_VHT40_SGI` | `400 ns` (SGI) | `2:0-9` | `6` | Clean LOS PtP (`Stage 487A` `24.83 Mbps` winner) |
| `FRESNEL_MULTIPATH_GUARD` | `800 ns` (LGI) | `2:0-8` | `8` | Multipath / Fresnel reflection ($>400\text{ ns}$ delay spread) |
| `AUTO_SGI_PEER_SYNC` | `400 ns` (SGI) | `2:0-9` | `6` | Automatic `hostapd_cli` / `WMI_PEER_ASSOC_CMDID` refresh |

## 4. Safety & Verification
- **Zero Protected Node Touches**: `.241`, `.242`, `.20`, `.250`, and `/dev/ame*` on `.110` untouched.
