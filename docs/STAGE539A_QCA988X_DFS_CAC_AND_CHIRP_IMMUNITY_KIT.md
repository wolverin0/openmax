<!-- doc-head: Stage 539A QCA988x ath_dfs False-Radar Immunity & CAC Override Integration (<220 lines) -->
`Stage 539A` operacionaliza los hallazgos RE de `Stage 499A` (`DFS_SET_CAC_TIME_OVERRIDE_MS`, `DFS_SET_FALSE_RSSI_THRESHOLD`, `DFS_SET_FILTER_RSSI_OFFSET`, `DFS_SET_PRI_MULTIPLIER`, `DFS_chirp_protect` en `ath_dfs.ko`) y controles `debugfs` `OpenWrt` en `firmware/openwrt/common/fmx_qca988x_dfs_chirp_immunity.sh`.
<!-- /doc-head -->

# Stage 539A — `QCA988x` `ath_dfs` False-Radar Immunity & `CAC` Override Integration (`mm-db72`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-db72`, `id=155438`)
- **Attribution**: `proprietary airMAX/LTU module`, `ath10k`, `QCA firmware`, `mac80211`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca988x_dfs_chirp_immunity.sh`](../firmware/openwrt/common/fmx_qca988x_dfs_chirp_immunity.sh)
- **SHA-256**: `5ab0914b02a4f2b1073fd8c561e79125b39e00d013f6a167c24aef4f0ffaef54`
- **Artifact**: [`artifacts/autoresearch/stage539a_qca988x_dfs_cac_and_chirp_immunity_kit.json`](../artifacts/autoresearch/stage539a_qca988x_dfs_cac_and_chirp_immunity_kit.json)

## 1. Parámetros `ath_dfs.ko` (`Stage 499A` $ightarrow$ `Stage 539A`) (`CONFIRMED`)
| Parámetro / Control (`ath_dfs.ko` / `ath10k`) | Valor Configurado | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| **`DFS_chirp_protect`** | `1` (Activo) | Descarta espurios de borde de subportadora VHT80 co-localizada que imitan chirps de radar (`proprietary airMAX/LTU module`). |
| **`DFS_SET_FALSE_RSSI_THRESHOLD`** | `24 dB` | Eleva el umbral mínimo de potencia de pulso sobre `NF` para evitar disparos por ruido de piso térmico (`QCA firmware`). |
| **`DFS_SET_FILTER_RSSI_OFFSET`** | `+6 dB` | Compensa el acoplamiento de campo cercano entre paneles de la misma torre (`hardware`). |
| **`DFS_SET_PRI_MULTIPLIER`** | `2` | Verifica múltiplos armónicos de `PRI` (Pulse Repetition Interval) antes de declarar radar válido (`proprietary airMAX/LTU module`). |
| **`DFS_SET_CAC_TIME_OVERRIDE_MS`** | Soportado en banco | Documenta el control de tiempo `CAC` junto al gate de `120s` (`FMX-DISC-24`) en canales `U-NII-2A/2C` (`mac80211`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Inspecciona `dfs_stats` y piso de ruido sin alterar estado regulatorio.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
