<!-- doc-head: Stage 711A Universal WA/XC/XW v18 SquashFS (180 hsqs Images) Bake (<200 lines) -->
`Stage 711A` empaqueta las `180` imágenes universales `WA/XC/XW v18` SquashFS (`hsqs`) integrando `Stage 709A` (`fmx_qca_wmi_vdev_start_guard.sh` + resolución dinámica `phy*`), `Stage 671A` (`fmx_qca_htt_tx_compl_guard.sh`), `WA Champion v11` y `PtP Champion v3`.
<!-- /doc-head -->

# Stage 711A — Universal `WA/XC/XW v18` SquashFS (`180` `hsqs` Images) Bake (`mm-2c0a`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-2c0a`, `id=155470`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v18`)**: [`99-fmx-wa-universal-champion-v18`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v18) (`sha256: fa1a0a05d925b31fd980d2c1dcb04c10a7b56e59ba4ea74dddd122541b5f1ce9`).

## 1. Integrated Ground-Up `v18` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 709A` `WMI_VDEV_START` & Dynamic `phy*` Guard** | `firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh` | Resuelve dinámicamente `phy0`/`phy1`/`phy2` y audita `WMI_SERVICE_READY_EVENTID` + `WMI_VDEV_START_REQUEST_CMDID`. |
| **`Stage 671A` `HTT TX Completion` Guard** | `firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh` | Protege el pool de descriptores `HTT_T2H_MSG_TYPE_TX_COMPL_IND` (`max_num_pending_tx=1424`) mediante `aql_threshold=24000` y `aql_txq_limit=4000`. |
| **`WA Champion v11` + `PtP Champion v3`** | `tcp_limit_output_bytes=131072`, `netdev_budget_usecs=4000` | Sincroniza TSQ y presupuesto SoftIRQ con la agregación `htt_max_amsdu_ampdu = 2 64`. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
