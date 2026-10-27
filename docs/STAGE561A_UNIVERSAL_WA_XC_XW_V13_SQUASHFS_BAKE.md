<!-- doc-head: Stage 561A Universal WA/XC/XW v13 SquashFS (180 hsqs Images) Bake (<220 lines) -->
`Stage 561A` empaqueta las `180` imágenes universales `WA/XC/XW v13` SquashFS (`hsqs`) integrando `Stage 559A` (`fmx_xw_xm_ani_and_swr_limit_helper.sh`), `Stage 539A` (`fmx_qca988x_dfs_chirp_immunity.sh`), `Stage 503A` (`fmx_qca988x_bmiss_csa_helper.sh`) y `tcp_slow_start_after_idle=0` (`Stage 557A`).
<!-- /doc-head -->

# Stage 561A — Universal `WA/XC/XW v13` SquashFS (`180` `hsqs` Images) Bake (`mm-ccd0`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-ccd0`, `id=155445`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v13`)**: [`99-fmx-wa-universal-champion-v13`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v13) (`sha256: 3a62ea303d98bc0bbb40e08ce303d98839b1ed7037a2c1ee4435a9c434580241`).

## 1. Integrated Ground-Up `v13` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 559A` `XW/XM` `ANI` & `SWR` Helper** | `firmware/openwrt/common/fmx_xw_xm_ani_and_swr_limit_helper.sh` | Acota reintentos largos (`long=4`, `short=7`) y activa `ANI` en `AR934x`/`AR724x` para proteger sectores mixtos `AC+M5`. |
| **`Stage 557A` Burst CWND Preservation** | `tcp_slow_start_after_idle=0`, `tcp_no_metrics_save=1` | Evita colapso de ventana TCP entre ráfagas de video/TDMA y descarta métricas obsoletas tras desvanecimientos. |
| **`Stage 539A` `ath_dfs` Chirp Immunity** | `firmware/openwrt/common/fmx_qca988x_dfs_chirp_immunity.sh` | Protege canales `U-NII-2A/2C` frente a falsos positivos de radar. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
