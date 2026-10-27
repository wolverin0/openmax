<!-- doc-head: Stage 671A QCA988x HTT TX Descriptor & Completion Ring (HTT_T2H_MSG_TYPE_TX_COMPL_IND) Backpressure Guard (<200 lines) -->
`Stage 671A` construye `firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh` para gobernar la contrapresión entre `mac80211` `AQL` (`aql_txq_limit = 4000 us`) y el anillo de completitud `HTT_T2H_MSG_TYPE_TX_COMPL_IND` (`max_num_pending_tx = 1424`) en `QCA988x`.
<!-- /doc-head -->

# Stage 671A — `QCA988x` HTT TX Descriptor & Completion Ring Backpressure Guard (`mm-97d8`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-97d8`, `id=155463`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh`](../firmware/openwrt/common/fmx_qca_htt_tx_compl_guard.sh)
- **SHA-256**: `be9115aa873c6de9338d64611973ef1634ff4d2561d1bf13f4800245feffb96a`
- **Artifact**: [`artifacts/autoresearch/stage671a_qca_htt_tx_compl_and_aql_guard.json`](../artifacts/autoresearch/stage671a_qca_htt_tx_compl_and_aql_guard.json)

## 1. Contrapresión `AQL -> HTT TX Descriptor Ring` en `QCA988x` (`CONFIRMED`)
| Parámetro (`ath10k` / `mac80211`) | Valor Configurado | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `HTT_T2H_MSG_TYPE_TX_COMPL_IND` | `max_num_pending_tx = 1424` | Cada MSDU en vuelo retiene un descriptor `HTT` hasta que el firmware Xtensa emite la indicación de completitud por `Copy Engine` (`QCA firmware`). |
| `htt_max_amsdu_ampdu` | `"2 64"` | Limita `A-MSDU = 2` (evitando corrupción de subframes largos ante ruido) mientras sostiene `A-MPDU = 64` subframes (`ath10k`). |
| `aql_txq_limit` / `aql_threshold` | `4000 us` / `24000` | Retiene el exceso de paquetes en `fq_codel` del host (`Linux`) en lugar de inundar la RAM de `QCA988x`, reduciendo la latencia `p99` bajo carga (`mac80211`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Audita `aql_txq_limit`, `aql_threshold` y `htt_max_amsdu_ampdu` sin alterar tráfico.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
