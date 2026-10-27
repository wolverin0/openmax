<!-- doc-head: Stage 573A QCA988x & AR9344 PAPRD, TPC/CTL Loop & Thermal Compensation Helper (<220 lines) -->
`Stage 573A` construye `firmware/openwrt/common/fmx_qca_paprd_olpc_tpc_helper.sh` operacionalizando el RE `Stage 563A` sobre los `7` módulos `WA/XC/XW` (`ath_hal.ko`, `ath_dev.ko`, `umac.ko`: `29` símbolos `PAPRD`, `15` símbolos `TPC` y `22` símbolos `CTL`).
<!-- /doc-head -->

# Stage 573A — `QCA988x` & `AR9344` `PAPRD`, `TPC/CTL` Loop & Thermal Helper (`mm-25f8`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-25f8`, `id=155448`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `proprietary airMAX/LTU module`, `hardware`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca_paprd_olpc_tpc_helper.sh`](../firmware/openwrt/common/fmx_qca_paprd_olpc_tpc_helper.sh)
- **SHA-256**: `c6e3681b052fee269749f63854240c5bc70dbb11f8c454e46a23e20a9c08dcb7`
- **Artifact**: [`artifacts/autoresearch/stage573a_qca_paprd_olpc_and_thermal_tpc_helper.json`](../artifacts/autoresearch/stage573a_qca_paprd_olpc_and_thermal_tpc_helper.json)

## 1. Pipeline `PAPRD` de 7 Etapas y Control `TPC/CTL` (`Stage 563A` RE) (`CONFIRMED`)
| Subsistema (`ath_hal.ko` / `ath_dev.ko` / `umac.ko`) | Símbolos Clave Descubiertos (`Stage 563A`) | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :--- | :--- |
| **Pipeline `PAPRD` (`7` etapas)** | `create_curve -> init_table -> populate_paprd -> swizzle -> setup_gain_table -> set_paprd_tx_desc -> is_done` + `ath_apply_paprd_table` | Construye la curva polinomial de pre-distorsión digital del `PA` en tiempo de ejecución para linealizar `64-QAM`/`256-QAM` (`hardware`). |
| **Guardia `GreenTX` vs `PAPRD`** | `ar9300_is_skip_paprd_by_greentx` | `GreenTX` salta `PAPRD` para ahorrar energía en corto alcance, degradando el EVM en enlaces WISP de alta modulación; mantener `GreenTX=0` preserva `PAPRD` activo (`proprietary airMAX/LTU module`). |
| **Lazo `TPC/CTL` & Térmico** | `ar9300_enable_tpc`, `tpc_config_get_rate_tpc`, `ar9300_get_ctl_chan_nf`, `ar9300_paprd_thermal_send` | El control de potencia en `WA/XC/XW` se gobierna mediante `enable_tpc` + tablas por tasa/país (`CTL` + `EEPROM` `mtd5`) y recalibración térmica (`QCA firmware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Audita el estado de `PAPRD`, `TPC` y `nf_cal_period` (`30000 ms`) sin alterar caldata `mtd5`.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
