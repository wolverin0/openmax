<!-- doc-head: Stage 505A Universal WA/XC/XW v11 SquashFS (hsqs) Bake (<220 lines) -->
`Stage 505A` empaqueta las `180` imágenes universales `WA/XC/XW v11` SquashFS (`hsqs`) integrando `fmx_qca988x_bmiss_csa_helper.sh` (`Stage 503A`), el compensador Fraunhofer de campo cercano/lejano (`Stage 481A`) y el showcase `v5` (`Stage 483A`).
<!-- /doc-head -->

# Stage 505A — Universal `WA/XC/XW v11` SquashFS (`hsqs`) Bake (`mm-1f8e`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-1f8e`, `id=155435`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v11`)**: [`99-fmx-wa-universal-champion-v11`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v11) (`sha256: f043f1ffe57df527f3a62ad3ee62e3d173914bff1836ca2cb951f03f7285cac7`).

## 1. Integrated Ground-Up `v11` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 503A` `BMISS` & `CSA` Helper** | `firmware/openwrt/common/fmx_qca988x_bmiss_csa_helper.sh` | Eleva `WMI_VDEV_PARAM_BMISS_COUNT_MAX=30` y `CSA=10` para evitar desasociaciones bajo interferencia o `DFS`. |
| **`Stage 481A` Compensador Fraunhofer** | `artifacts/autoresearch/stage481a_nearfield_fraunhofer_dish_cavity_compensator.json` | Compensa reflexiones de cavidad parabólica (`400 mm` / `620 mm`, $d_F = 2D^2/\lambda$) y acoplamiento en banco. |
| **`Stage 483A` Showcase `v5`** | `artifacts/autoresearch/stage483a_public_tester_ground_up_showcase_v5.json` | Suite pública reproducible para testers de la comunidad (`WA/XC/XW/LTU`). |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
