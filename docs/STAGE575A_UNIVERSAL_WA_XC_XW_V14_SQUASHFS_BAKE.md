<!-- doc-head: Stage 575A Universal WA/XC/XW v14 SquashFS (180 hsqs Images) Bake (<220 lines) -->
`Stage 575A` empaqueta las `180` imágenes universales `WA/XC/XW v14` SquashFS (`hsqs`) integrando `Stage 573A` (`fmx_qca_paprd_olpc_tpc_helper.sh`), las promociones `WA Champion v9` (`228` ventanas `PB-050`: `tcp_notsent_lowat=131072`, `tx_queue_len=1000`), `Stage 559A` (`fmx_xw_xm_ani_and_swr_limit_helper.sh`) y `Stage 539A` (`fmx_qca988x_dfs_chirp_immunity.sh`).
<!-- /doc-head -->

# Stage 575A — Universal `WA/XC/XW v14` SquashFS (`180` `hsqs` Images) Bake (`mm-cb4f`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-cb4f`, `id=155450`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v14`)**: [`99-fmx-wa-universal-champion-v14`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v14) (`sha256: 31dca3093f4f8d83b2b5d6fd72de0d7762a2ee2c0e9ee5a7cdcfb7a067313298`).

## 1. Integrated Ground-Up `v14` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 573A` `PAPRD` & `TPC/CTL` Helper** | `firmware/openwrt/common/fmx_qca_paprd_olpc_tpc_helper.sh` | Protege el pipeline `PAPRD` (`7` etapas, `GreenTX=0`) y el lazo térmico `TPC/CTL` (`ar9300_paprd_thermal_send`, `nf_cal_period=30000`). |
| **`WA Champion v9` (`PB-050`, `228` Windows)** | `tcp_notsent_lowat=131072`, `tx_queue_len=1000` | Promociona los ganadores validados en `228` ventanas reales sobre `.83` para sostener agregación `A-MPDU` sin inanición de socket. |
| **`Stage 559A` `XW/XM` `ANI` & `SWR` Helper** | `firmware/openwrt/common/fmx_xw_xm_ani_and_swr_limit_helper.sh` | Acota reintentos largos (`long=4`, `short=7`) y activa `ANI` en `AR934x`/`AR724x`. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
