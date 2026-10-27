<!-- doc-head: STAGE302A_LTU_THERMAL_RAINFADE_HYSTERESIS_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 302A: SimPy + Pymoo NSGA-II Thermal (`25C..65C`) & Rain-Fade Hysteresis Model

## 1. Thermal PA Drift & Rain-Fade Step-Down Problem (`INFERRED` / `CONFIRMED`)
- **Mechanism**: As outdoor radio enclosure temperature climbs from `25C` to `65C` alongside a `3.6 dB` rain fade, insufficient PA backoff (`2.0 dB`) causes severe `IMD3` EVM compression, driving `4096-QAM` codeword BLER to `6.535%` (`p99 = 7.973 ms`).
- **Calibrated `6.0 dB` Backoff + `97% / 90%` Hysteresis (`ame_core.ko`)**: Preserves PA linearity and steps down cleanly (`12x -> 10x -> 8x`), achieving `601.69 Mbps` and reducing `p99` latency to `4.04 ms`.

## 2. Comparative Results (`25C..65C` + `3.6 dB` Rain Fade)
| Profile | `startThrd` / `stayThrd` | PA Backoff (dB) | Goodput (Mbps) | Mean BLER (%) | `p99` Latency (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| Unbacked Aggressive `4096-QAM` | `93% / 82%` | `2.0 dB` | `482.82` | `6.535%` | `7.973` |
| **Calibrated `97%/90%` Champion** | **`97% / 90%`** | **`6.0 dB`** | **`601.69`** | **`1.902%`** | **`4.04`** |
