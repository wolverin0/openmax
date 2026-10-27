<!-- doc-head: STAGE409A_WMI_RETRY_AND_HOOK_LOADER.md preserved document content -->
<!-- /doc-head -->


# Stage 409A — `PB-010` / `WMI 0x9044` 4-Series Hardware Retry Fallback & `WMI 0x9064` Target Hook Loader (`fmx_wmi_retry_and_hook_loader.sh`)

- **Status**: `CONFIRMED`
- **Attribution**: `ath10k`, `QCA firmware`, `mac80211`, `Linux`
- **Deliverable**: [`firmware/openwrt/common/fmx_wmi_retry_and_hook_loader.sh`](../firmware/openwrt/common/fmx_wmi_retry_and_hook_loader.sh) (`sha256: 71854ad62dcf252c...`)

## 1. 4-Series Hardware Retry Schedule (`WMI 0x9044` / `PB-010`) (`CONFIRMED`)
| Retry Series | Spatial Streams & Guard Interval | Max Tries | First-Principles Purpose |
| :--- | :--- | :--- | :--- |
| **Series 0 (`S0`)** | `2x2 VHT` (`MCS 8/9`, `SGI 400 ns`) | `2` | Maximum spectral efficiency when both H/V chains are balanced. |
| **Series 1 (`S1`)** | `2x2 VHT` (`MCS - 1`, `LGI 800 ns`) | `2` | Absorbs multipath delay spread (`> 400 ns` foliage reflection). |
| **Series 2 (`S2`)** | `1x1 VHT CDD` (`MCS 0..7`, `LGI 800 ns`) | `2` | **Critical Break**: Drops spatial multiplexing (`2x2`) to `1x1` Cyclic Delay Diversity (`CDD`) if one polarity fades (`>= 6 dB`). |
| **Series 3 (`S3`)** | `1x1 MCS0 CDD Rescue` (`LGI`) | `2` | Prevents `BA` window stalls and TCP RTOs without waiting for slow host rate-control convergence. |

## 2. Integration with `fmx_chain_imbalance_rescue_daemon.sh` (`CONFIRMED`)
When chain imbalance reaches `>= 6 dB`, `fmx_wmi_retry_and_hook_loader.sh` atomically clamps `htt_max_amsdu_ampdu` to `"1 16"` and locks the VHT rate mask to `1:0-7` (`1x1 CDD`), restoring `"2 64"` and `1:0-9 2:0-9 sgi-5` once chain balance recovers (`<= 3 dB`).
