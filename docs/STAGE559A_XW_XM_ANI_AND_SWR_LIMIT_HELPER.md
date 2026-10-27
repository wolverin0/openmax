<!-- doc-head: Stage 559A XW/XM (AR934x/AR724x) Adaptive Noise Immunity (ANI) & Software Retry (SWR) Limit Helper (<220 lines) -->
`Stage 559A` construye `firmware/openwrt/common/fmx_xw_xm_ani_and_swr_limit_helper.sh` para gobernar `Adaptive Noise Immunity` (`ANI`) y el límite de reintentos `SWR` (`short=7`, `long=4`) en equipos `M5` (`XW`/`XM` `AR934x`/`AR724x`).
<!-- /doc-head -->

# Stage 559A — `XW/XM` (`AR934x`/`AR724x`) `ANI` & `SWR` Limit Helper (`mm-b024`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-b024`, `id=155443`)
- **Attribution**: `mac80211`, `Linux`, `proprietary airMAX/LTU module`, `hardware`
- **Deliverable**: [`firmware/openwrt/common/fmx_xw_xm_ani_and_swr_limit_helper.sh`](../firmware/openwrt/common/fmx_xw_xm_ani_and_swr_limit_helper.sh)
- **SHA-256**: `a424e4b2888b9f5c5a3219a31b56f8907c0f9d4c94bbf0e06961e1a37cc88ac7`
- **Artifact**: [`artifacts/autoresearch/stage559a_xw_xm_ani_and_swr_limit_helper.json`](../artifacts/autoresearch/stage559a_xw_xm_ani_and_swr_limit_helper.json)

## 1. Control de `ANI` y `SWR` en Sectores Mixtos `AC + M5` (`CONFIRMED`)
| Parámetro (`ath9k` / `XW` / `XM`) | Valor Configurado | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| **`ANI` (`Adaptive Noise Immunity`)** | `1` (`ofdm_level=3`, `firstep=2`) | Ajusta dinámicamente el detector de preámbulo OFDM en `AR9344`/`AR9342` para evitar falsos bloqueos de receptor (`hardware`). |
| **`swr_long_retry_limit`** | `4` (vs `15` stock) | Impide que un CPE `M5` en `MCS0/1` reintente `15` veces una agregación fallida y robe decenas de milisegundos al sector `AC` (`mac80211`). |
| **`swr_short_retry_limit`** | `7` | Mantiene recuperación rápida para tramas cortas (`VoIP` / `TCP ACK`) mientras delega la recuperación de cola a `TLP` en capa 4 (`Linux`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Inspecciona estado `ANI`/`SWR` sin alterar la interfaz.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
