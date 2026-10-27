<!-- doc-head: Stage 673A Universal WA/XC/XW v17 SquashFS (180 hsqs Images) Bake (<200 lines) -->
`Stage 673A` empaqueta las `180` imágenes universales `WA/XC/XW v17` SquashFS (`hsqs`) integrando `Stage 671A` (`fmx_qca_htt_tx_compl_guard.sh`), `WA Champion v11`, `PtP Champion v3` y `Stage 637A` (`fmx_qca_txbf_stbc_ldpc_guard.sh`).
<!-- /doc-head -->

# Stage 673A — Universal `WA/XC/XW v17` SquashFS (`180` `hsqs` Images) Bake (`mm-e9d1`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-e9d1`, `id=155465`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v17`)**: [`99-fmx-wa-universal-champion-v17`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v17) (`sha256: 651a64a94b4656b1303116586647024c8da3ef63fedb14e7560dee5bf582c09d`).

## 1. Integrated Ground-Up `v17` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 671A` `HTT TX Completion` Guard** | `firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh` | Protege el pool de descriptores `HTT_T2H_MSG_TYPE_TX_COMPL_IND` (`max_num_pending_tx=1424`) mediante `aql_threshold=24000` y `aql_txq_limit=4000`. |
| **`WA Champion v11` + `PtP Champion v3`** | `tcp_limit_output_bytes=131072`, `netdev_budget_usecs=4000` | Sincroniza TSQ y presupuesto SoftIRQ con la agregación `htt_max_amsdu_ampdu = 2 64`. |
| **`Stage 637A` `TxBF`/`STBC`/`LDPC` Guard** | `firmware/openwrt/common/fmx_qca_txbf_stbc_ldpc_guard.sh` | Activa `LDPC=1` y `STBC=1` mientras desactiva sounding `SU-TxBF` en enlaces fijos `2x2`. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
