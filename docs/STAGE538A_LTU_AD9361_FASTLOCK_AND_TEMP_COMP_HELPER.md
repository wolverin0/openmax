<!-- doc-head: Stage 538A AD9361 Fastlock Profile (8-Slot) & Temp-Compensation Helper for AF-LTU (<220 lines) -->
`Stage 538A` operacionaliza los hallazgos RE de `Stage 486A` (`AD9361` `8`-slot fastlock `0x25A..0x29F` y tablas de calibración térmica en `ame_core.ko`) en `firmware/ltu_safe_kit/fmx_ltu_ad9361_fastlock_temp_helper.sh` para las 5 placas `LTU` + `LTU-Rocket`.
<!-- /doc-head -->

# Stage 538A — `AD9361` Fastlock Profile (`8`-Slot) & Temp-Compensation Helper for `AF-LTU` (`mm-9a47`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-9a47`, `id=155437`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_ad9361_fastlock_temp_helper.sh`](../firmware/ltu_safe_kit/fmx_ltu_ad9361_fastlock_temp_helper.sh)
- **SHA-256**: `6f09c00d9d9820cc8d1a444c5e05363f1231c7080452dddd981da55256ee4acd`
- **Artifact**: [`artifacts/autoresearch/stage538a_ltu_ad9361_fastlock_and_temp_comp_helper.json`](../artifacts/autoresearch/stage538a_ltu_ad9361_fastlock_and_temp_comp_helper.json)

## 1. Arquitectura `AD9361` `8`-Slot Fastlock & Compensación Térmica (`Stage 486A` $ightarrow$ `Stage 538A`) (`CONFIRMED`)
| Subsistema `AD9361` (`ame_core.ko`) | Registros / Símbolos | Beneficio First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| **`8`-Slot Fastlock Profiles** | `0x25A..0x29F` (`16 B`/perfil) | Almacena `8` perfiles completos de sintetizador `VCO/Alc/ChargePump` para cambio de frecuencia en `< 50 µs` sin recalibrar VCO (`hardware`). |
| **Split-Frequency `TX_LO != RX_LO`** | `RX Synth` / `TX Synth` independientes | Permite conmutar el canal de subida (`UL`) a un slot limpio sin alterar la portadora de bajada (`DL`) (`proprietary airMAX/LTU module`). |
| **Thermal Calibration LUT** | `COLD` (`<25°C`), `NOMINAL` (`25..60°C`), `HOT` (`>=60°C`) | Evita degradación de imagen IQ y fuga de LO bajo excursiones térmicas en torre para sostener `4096-QAM` (`12x`) (`hardware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
