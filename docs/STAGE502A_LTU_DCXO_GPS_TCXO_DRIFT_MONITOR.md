<!-- doc-head: Stage 502A Pillar 4 LTU DCXO GPS vs TCXO Clock Discipline & CFO Drift Detector (<220 lines) -->
`Stage 502A` construye el monitor read-only `firmware/ltu_safe_kit/fmx_ltu_dcxo_gps_tcxo_monitor.sh` basado en los `30` símbolos `bbp_rf_dcxo_*` descubiertos en `Stage 486A` para detectar deriva de frecuencia portadora (`CFO`) antes de que caiga `4096-QAM` (`12x`).
<!-- /doc-head -->

# Stage 502A — Pillar 4 LTU DCXO GPS vs TCXO Clock Discipline & CFO Drift Detector (`mm-5c28`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-5c28`, `id=155432`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_dcxo_gps_tcxo_monitor.sh`](../firmware/ltu_safe_kit/fmx_ltu_dcxo_gps_tcxo_monitor.sh)
- **SHA-256**: `a98ee8c924f685a8f796c09b4f1181ae38f361d240c636509fc7c43be33dd2ad`
- **Artifact**: [`artifacts/autoresearch/stage502a_ltu_dcxo_gps_tcxo_drift_monitor.json`](../artifacts/autoresearch/stage502a_ltu_dcxo_gps_tcxo_drift_monitor.json)

## 1. Símbolos `Stage 486A` & Umbrales CFO para `4096-QAM` (`12x`) (`CONFIRMED`)
| Símbolo / Parámetro (`eab_driver.ko` / `ame_core.ko`) | Rol en Disciplina de Reloj `AD9361` / `Beetle` | Umbral Crítico |
| :--- | :--- | :---: |
| **`bbp_rf_dcxo_is_sync_by_gps`** | Indica si el DCXO del `LTU-Rocket` AP está disciplinado por `1PPS` GPS (`Reuse-1`). | `1` (GPS Locked) |
| **`bbp_rf_dcxo_is_sync_by_tcxo`** | Indica transición a oscilador local TCXO (holdover o CPE sin GPS). | Holdover `< 0.25 ppm` |
| **`bbp_rf_dcxo_get_gps_state`** | Máquina de estados de enganche de fase GPS (`eab_driver.ko`). | `LOCKED` vs `HOLDOVER` |
| **`bbp_rf_tcxo_cal_variation`** | Variación térmica de la tabla de calibración TCXO frente a temperatura del SoC. | `< 75 °C` (`<= 0.25 ppm` para `12x`) |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
