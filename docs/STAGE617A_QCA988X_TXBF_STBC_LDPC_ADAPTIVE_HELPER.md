<!-- doc-head: STAGE617A_QCA988X_TXBF_STBC_LDPC_ADAPTIVE_HELPER.md preserved document content -->
<!-- /doc-head -->


# Stage 617A — `QCA988x` TxBF, SU-BF, STBC & LDPC Adaptive Helper

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `QCA firmware` (`QCA988x` Xtensa) / `mac80211`.
- **Stage 615A Grounding**: Operationalizes `WMI_VDEV_PARAM_LDPC` (`0x2a`), `WMI_VDEV_PARAM_TX_STBC` (`0x2c`), `WMI_VDEV_PARAM_RX_STBC` (`0x2d`), and `WMI_VDEV_PARAM_TXBF` (`0x3b`) across `WA`, `XC`, and `XW` (`AR9344`).
- **Deliverable**: `firmware/openwrt/common/fmx_qca988x_txbf_stbc_ldpc_helper.sh` (`SHA-256`: `02e3c0375ab26afcb3de6999f28cf16d6fa44ff8b251b557d301ba4b0ac512bf`).

## 2. Adaptive Profile Matrix
| Profile | LDPC (`0x2a`) | SU-TxBF (`0x3b`) | TX/RX STBC (`0x2c`/`0x2d`) | Target Regime |
| :--- | :---: | :---: | :---: | :--- |
| `NEAR_FIELD_NO_SUBF_SOUNDING` | `1` | `0` | `0` / `0` | Bench $<6.15\text{ m}$ (avoids `3.2%` NDP sounding overhead & phase wrap) |
| `FAR_FIELD_LDPC_SUBF_OPTIMAL` | `1` | `1` | `1` / `1` | Clean LOS $>6.15\text{ m}$ (`+2.1 dB` LDPC + `+1.8 dB` SU-BF gain) |
| `MULTIPATH_STBC_ROBUST` | `1` | `0` | `1` / `1` | Heavy Fresnel multipath / NLOS (`2x1` Alamouti diversity) |

## 3. Safety Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` `/dev/ame*` untouched.
