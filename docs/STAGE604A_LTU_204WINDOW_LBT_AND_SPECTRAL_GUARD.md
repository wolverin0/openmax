<!-- doc-head: Stage 604A Pillar 4 AF-LTU (Beetle) 204-Window Golden Telemetry & LBT/Spectral Guard (<220 lines) -->
`Stage 604A` construye el guard read-only `firmware/ltu_safe_kit/fmx_ltu_200w_golden_guard.sh` que operacionaliza el RE `Stage 590A` de `ame_core.ko` y `ame_dev.ko` (`24` símbolos `LBT`, `lbt_cfg_pause_txframe`, `ame_core_get_rf_interference_avg/curr` y `7` llaves `auto_freq`/`smart_scan`).
<!-- /doc-head -->

# Stage 604A — Pillar 4 `AF-LTU` (`Beetle`) `204`-Window Golden Telemetry & `LBT`/Spectral Guard (`mm-cd16`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-cd16`, `id=155452`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_200w_golden_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_200w_golden_guard.sh)
- **SHA-256**: `c35da9548399b555bffbec79edf52de6f07666893c528f49ae1819b799608c65`
- **Artifact**: [`artifacts/autoresearch/stage604a_ltu_204window_lbt_and_spectral_guard.json`](../artifacts/autoresearch/stage604a_ltu_204window_lbt_and_spectral_guard.json)

## 1. Arquitectura `LBT`, Detección de Interferencia y `Auto-Frequency` (`Stage 590A` RE) (`CONFIRMED`)
| Subsistema (`ame_core.ko` / `ame_dev.ko`) | Símbolos / Atributos Sysfs (`Stage 590A`) | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :--- | :--- |
| **Integración `LBT` en Scheduler TDMA** | `lbt_cfg_listen_window`, `lbt_cfg_pause_txframe`, `lbt_cfg_threshold`, `lbt_detects` | `LBT` en `AF-LTU` está integrado en el planificador de tramas mediante `lbt_cfg_pause_txframe` (`pauselen`, `window`, `threshold`) (`proprietary airMAX/LTU module`). |
| **Detectores de Interferencia RF** | `ame_core_get_rf_interference_avg`, `ame_core_get_rf_interference_curr`, `RX_POWER_TARGET_NOISE_VAL_THD` | Calcula interferencia RF promedio e instantánea (`pRfInterference`) para distinguir ruido térmico de interferencia co-canal (`hardware`). |
| **Llaves `Auto-Frequency` & `Smart Scan`** | `freq_list_enabled`, `auto_freq_list`, `auto_freq_mode`, `smart_scan`, `prefer_work_txfreq`, `prefer_work_rxfreq` | En enlaces WISP productivos, fijar `freq_list` acotada evita saltos erráticos de canal ante picos transitorios (`proprietary airMAX/LTU module`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
