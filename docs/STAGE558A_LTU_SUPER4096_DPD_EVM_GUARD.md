<!-- doc-head: Stage 558A Pillar 4 LTU Super-4096-QAM (12x) DPD & PA EVM Backoff Guard (<220 lines) -->
`Stage 558A` construye el guard read-only `firmware/ltu_safe_kit/fmx_ltu_super4096_dpd_evm_guard.sh` que modela el umbral de `EVM <= -38 dB` (`CINR >= 36 dB`) y backoff lineal de `PA` (`4 dB`) para sostener `Super-4096-QAM` (`12x`) en la familia `AF-LTU`.
<!-- /doc-head -->

# Stage 558A — Pillar 4 LTU `Super-4096-QAM` (`12x`) DPD & PA EVM Backoff Guard (`mm-1204`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-1204`, `id=155442`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_super4096_dpd_evm_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_super4096_dpd_evm_guard.sh)
- **SHA-256**: `cf5001d6dd63f1875f1b892808310f2818c9e2de2ff03a028188eabe7f0fa0a6`
- **Artifact**: [`artifacts/autoresearch/stage558a_ltu_super4096_dpd_evm_guard.json`](../artifacts/autoresearch/stage558a_ltu_super4096_dpd_evm_guard.json)

## 1. Física de `Super-4096-QAM` (`12x`) y Compresión de `PA` (`CONFIRMED`)
| Parámetro `AF-LTU` (`12x`) | Umbral Requerido | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| **Constelación & Eficiencia** | `4096-QAM` (`12 bits/símbolo`) | Requiere distancia euclidiana mínima entre puntos `4x` más estrecha que `256-QAM` (`hardware`). |
| **TX EVM Requerido** | `<= -38.0 dB` (`1.25%` RMS) | Si el amplificador de potencia (`PA`) opera cerca del punto `P1dB`, la distorsión `AM-AM` / `AM-PM` degrada el EVM a `-31 dB` e impide `12x` (`hardware`). |
| **Backoff Óptimo de PA** | `4.0 dB` (`6.0 dB` `>= 65°C`) | Mantener `4 dB` de backoff debajo del máximo TX permite operar en zona lineal y alcanzar `CINR >= 36 dB` reales (`proprietary airMAX/LTU module`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
