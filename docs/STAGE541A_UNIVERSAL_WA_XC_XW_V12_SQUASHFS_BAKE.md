<!-- doc-head: Stage 541A Universal WA/XC/XW v12 SquashFS (180 hsqs Images) Bake (<220 lines) -->
`Stage 541A` empaqueta las `180` imágenes universales `WA/XC/XW v12` SquashFS (`hsqs`) integrando `Stage 487A` (`VHT40` `24.83 Mbps` `0.0%` loss & `VHT80` STA cap unlock), `Stage 403A` (`pktlog_filter=0x0` `+27.66%` goodput + `PB-040` `SGMT` RAM canary) y `Stage 539A` (`fmx_qca988x_dfs_chirp_immunity.sh`).
<!-- /doc-head -->

# Stage 541A — Universal `WA/XC/XW v12` SquashFS (`180` `hsqs` Images) Bake (`mm-d197`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-d197`, `id=155440`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`).
- **UCI Champion Script (`v12`)**: [`99-fmx-wa-universal-champion-v12`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v12) (`sha256: 616d550ad9d6f0bf1e235980d001d48feeaee429181307a867d18b3269c539b7`).

## 1. Integrated Ground-Up `v12` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 487A` `VHT40/VHT80` Cap Unlock** | `artifacts/autoresearch/stage487a_live_pbe5ac_sta_vht80_cap_and_vht40_unlock.json` | Desbloquea `VHT80` STA (`0.0%` loss en `VHT40` `24.83 Mbps`) sobre enlaces híbridos y nativos `OpenWrt`. |
| **`Stage 403A` `pktlog=0x0` & `PB-040` Canary** | `artifacts/autoresearch/stage403a_live_wa_pb040_ram_canary_and_nfcal_r43_45.json` | Elimina el overhead DMA de `pktlog` (`+27.66%` goodput en `74Kc`) y valida el canary `SGMT` en `/tmp`. |
| **`Stage 539A` `ath_dfs` Chirp Immunity** | `firmware/openwrt/common/fmx_qca988x_dfs_chirp_immunity.sh` | Protege canales `U-NII-2A/2C` frente a falsos positivos de radar causados por bordes de subportadora co-localizados. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
