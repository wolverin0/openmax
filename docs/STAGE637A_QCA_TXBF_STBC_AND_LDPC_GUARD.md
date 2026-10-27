<!-- doc-head: Stage 637A QCA988x & AR9344 Transmit Beamforming (TxBF), STBC & LDPC Guard (<220 lines) -->
`Stage 637A` construye `firmware/openwrt/common/fmx_qca_txbf_stbc_ldpc_guard.sh` operacionalizando el RE `Stage 615A` sobre los `7` módulos `WA/XC/XW` (`umac.ko`, `ath_dev.ko`, `ath_hal.ko`: `14` tokens `TXBF`, `38` tokens `STBC`, `18` tokens `LDPC` y desambiguación de `bf_` como buffer TX).
<!-- /doc-head -->

# Stage 637A — `QCA988x` & `AR9344` `TxBF`, `STBC` & `LDPC` Guard (`mm-e480`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-e480`, `id=155458`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `proprietary airMAX/LTU module`, `Linux`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca_txbf_stbc_ldpc_guard.sh`](../firmware/openwrt/common/fmx_qca_txbf_stbc_ldpc_guard.sh)
- **SHA-256**: `0a34b6f3a02c85cfc429c119b3ac55e12539632d096d10a544decf4611253b76`
- **Artifact**: [`artifacts/autoresearch/stage637a_qca_txbf_stbc_and_ldpc_guard.json`](../artifacts/autoresearch/stage637a_qca_txbf_stbc_and_ldpc_guard.json)

## 1. Hallazgos `Stage 615A` RE: `LDPC`, `STBC` y `TxBF` en `WA/XC/XW` (`CONFIRMED`)
| Subsistema (`umac.ko` / `ath_dev.ko`) | Evidencia Binaria (`Stage 615A`) | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :--- | :--- |
| **`LDPC` (`Low-Density Parity-Check`)** | `Getting LDPC`, `getLDPC` (`18` tokens en `WA/XC`) | Aporta `+1.5..2.0 dB` de ganancia de codificación FEC respecto a `BCC` convolucional en `VHT40`/`VHT80` `256-QAM` (`MCS8/9`) (`hardware`). |
| **`STBC` (`Space-Time Block Coding`)** | `Getting TX STBC`, `Getting RX STBC` (`38` tokens) | Provee diversidad de Alamouti `2x1` cuando un CPE cae a `1` flujo espacial (`NSS=1`) durante desvanecimientos profundos (`QCA firmware`). |
| **`TxBF` (`txbf_not_supported` / `maxregpwr_txbf`)** | `14` tokens en `WA/XC:umac.ko`; `bf_` en `ath_dev.ko` es `struct ath_buf` (`bf_node`, `bf_lastfrm`) | En parábolas fijas `2x2` (`N_tx=2, N_rx=2`), el sounding explícito `NDPA/NDP` consume aire sin ganancia de arreglo; mantener `su_beamformer=0` preserva airtime y evita recorte `maxregpwr_txbf` (`QCA firmware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Inspecciona capacidades `LDPC`/`STBC`/`TxBF` en `phy0` sin tocar enlaces activos.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
