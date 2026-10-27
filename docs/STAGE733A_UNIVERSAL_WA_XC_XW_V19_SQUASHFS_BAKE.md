<!-- doc-head: Stage 733A Universal WA/XC/XW v19 SquashFS (180 hsqs Images) Bake (<200 lines) -->
`Stage 733A` empaqueta las `180` imágenes universales `WA/XC/XW v19` SquashFS (`hsqs`) integrando `Stage 731A` (`fmx_qca_spectral_radar_phyerr_guard.sh`), `Stage 709A` (`fmx_qca_wmi_vdev_start_guard.sh`), `Stage 671A` (`fmx_qca_htt_tx_compl_guard.sh`), `WA Champion v11` y `PtP Champion v3`.
<!-- /doc-head -->

# Stage 733A — Universal `WA/XC/XW v19` SquashFS (`180` `hsqs` Images) Bake (`mm-6e1e`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-6e1e`, `id=155475`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v19`)**: [`99-fmx-wa-universal-champion-v19`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v19) (`sha256: 2d4aedda796555e340a40c133d859301a3f723c08838c97308ee5b167be46743`).

## 1. Integrated Ground-Up `v19` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 731A` Spectral & Radar `PHYERR` Guard** | `firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh` | Silencia `ATH10K_PHYERR_SPECTRAL` (`spectral_scan_ctl=disable`) durante tráfico activo mientras preserva `ATH10K_PHYERR_RADAR`. |
| **`Stage 709A` `WMI_VDEV_START` & Dynamic `phy*` Guard** | `firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh` | Resuelve dinámicamente `phy0`/`phy1`/`phy2` y audita `WMI_SERVICE_READY_EVENTID` + `WMI_VDEV_START_REQUEST_CMDID`. |
| **`Stage 671A` `HTT TX Completion` Guard** | `firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh` | Protege el pool de descriptores `HTT_T2H_MSG_TYPE_TX_COMPL_IND` (`max_num_pending_tx=1424`) mediante `aql_threshold=24000` y `aql_txq_limit=4000`. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
