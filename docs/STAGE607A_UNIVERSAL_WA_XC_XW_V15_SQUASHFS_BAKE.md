<!-- doc-head: Stage 607A Universal WA/XC/XW v15 SquashFS (180 hsqs Images) Bake (<220 lines) -->
`Stage 607A` empaqueta las `180` imágenes universales `WA/XC/XW v15` SquashFS (`hsqs`) integrando `Stage 605A` (`fmx_qca988x_wmi_peer_rate_sgi_guard.sh`), `Stage 573A` (`fmx_qca_paprd_olpc_tpc_helper.sh`), `WA Champion v9` (`PB-050`) y `RACK-TLP` (`tcp_recovery=1`).
<!-- /doc-head -->

# Stage 607A — Universal `WA/XC/XW v15` SquashFS (`180` `hsqs` Images) Bake (`mm-038d`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-038d`, `id=155455`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v15`)**: [`99-fmx-wa-universal-champion-v15`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v15) (`sha256: 81290b604af86f7f7c62bbb82ba11530123f41267b84fa0ca2ca6b49552eac80`).

## 1. Integrated Ground-Up `v15` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 605A` `WMI_PEER_ASSOC` & `SGI` Guard** | `firmware/openwrt/common/fmx_qca988x_wmi_peer_rate_sgi_guard.sh` | Audita `peer_phymode`, `vht_mcs_set` y `_RATE_SetSGIMasks` (`Stage 589A`) + re-asociación limpia en cambios de ancho de canal (`Stage 487A`). |
| **`Stage 573A` `PAPRD` & `TPC/CTL` Helper** | `firmware/openwrt/common/fmx_qca_paprd_olpc_tpc_helper.sh` | Protege el pipeline `PAPRD` (`7` etapas, `GreenTX=0`) y el lazo térmico `TPC/CTL`. |
| **`Stage 603A` + `PB-050` Promotions** | `tcp_recovery=1`, `tcp_notsent_lowat=131072`, `tx_queue_len=1000` | Combina recuperación `RACK-TLP` con las promociones `PB-050` de `228` ventanas en `.83`. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
