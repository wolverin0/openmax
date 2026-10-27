<!-- doc-head: Stage 730A AF-LTU (Beetle) Thermal PA Bias & TX Gain Drift Read-Only Guard (<200 lines) -->
`Stage 730A` construye el auditor read-only `firmware/ltu_safe_kit/fmx_ltu_thermal_pa_bias_guard.sh` que operacionaliza la ingeniería inversa de `ame_core.ko` y `ame_dev.ko` (`Stage 728A`) auditando la temperatura del SoC (`soc_temp_mc`), la compensación térmica del PA y la estabilidad de EVM para `10x`/`12x` (`4096-QAM`) sin tocar `/dev/ame*`.
<!-- /doc-head -->

# Stage 730A — `AF-LTU` (`Beetle`) Thermal PA Bias & TX Gain Drift Guard (`mm-7760`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-7760`, `id=155472`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_thermal_pa_bias_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_thermal_pa_bias_guard.sh)
- **SHA-256**: `8330264ec36adeccfeefb576b376f1ac48da773668cd6b76edd74015d1ecc2be`
- **Artifact**: [`artifacts/autoresearch/stage730a_ltu_thermal_pa_bias_and_gain_guard.json`](../artifacts/autoresearch/stage730a_ltu_thermal_pa_bias_and_gain_guard.json)

## 1. Física Térmica del PA y Estabilidad `4096-QAM` (`12x`) en `AF-LTU` (`CONFIRMED`)
| Parámetro (`ame_core.ko` / `ame_dev.ko`) | Valor / Umbral | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `thermal_zone0/temp` (`soc_temp_mc`) | `47500 mC` (`47.5 °C` en `.110`) | Mide la temperatura die del SoC `Beetle` en tiempo real (`27.5 °C` de margen respecto al umbral de `75 °C`) (`hardware`). |
| `evm_12x_target_db` (`4096-QAM`) | `<= -38.0 dB` | Por encima de `75,000 mC` (`75 °C`), la compresión `AM-AM` y rotación `AM-PM` del FEM de `5 GHz` degradan el EVM de `-38 dB` si no actúa el bucle TSSI/DPD (`proprietary airMAX/LTU module`). |
| `PA_STATE` Read-Only Telemetry | `OPTIMAL_4096QAM_EVM` | Emite telemetría JSON determinística sin abrir ni escribir en `/dev/ame*` (`Linux`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
