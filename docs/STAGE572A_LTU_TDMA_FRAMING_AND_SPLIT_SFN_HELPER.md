<!-- doc-head: Stage 572A Pillar 4 AF-LTU (Beetle) TDMA Framing (1ms..5ms), Split TX/RX Synthesizer & SFN Sync Helper (<220 lines) -->
`Stage 572A` construye el helper read-only `firmware/ltu_safe_kit/fmx_ltu_tdma_split_sfn_helper.sh` que operacionaliza el RE `Stage 564A` de `ame_core.ko` (`9,699` símbolos) y `ame_dev.ko` (`1,669` símbolos) sobre `frame_len`, `duty_cycle`, `bc_dl_symbols`, `frame_pulse_offset`, `rx/tx freq` split y `ame_bbp_is_remote_SFN_synchronized`.
<!-- /doc-head -->

# Stage 572A — Pillar 4 `AF-LTU` (`Beetle`) TDMA Framing, Split TX/RX & SFN Sync Helper (`mm-d4a8`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-d4a8`, `id=155447`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_tdma_split_sfn_helper.sh`](../firmware/ltu_safe_kit/fmx_ltu_tdma_split_sfn_helper.sh)
- **SHA-256**: `9ab4241a3835c885e390a762cc0713b763e74f64b08164128d6c16483c964cbc`
- **Artifact**: [`artifacts/autoresearch/stage572a_ltu_tdma_framing_and_split_sfn_helper.json`](../artifacts/autoresearch/stage572a_ltu_tdma_framing_and_split_sfn_helper.json)

## 1. Geometría de Trama `AF-LTU` (`ame_core.ko` & `ame_dev.ko` `Stage 564A` RE) (`CONFIRMED`)
| Símbolo / Atributo Sysfs | Módulo Propietario | Función First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `frame_len` (`show`/`store`) | `ame_dev.ko` + `ame_bbp_set_frame_len` | Gobierna la duración de trama TDD (`1 ms..5 ms`); `2 ms` minimiza RTT `p99` para Triple-Play sin degradar eficiencia de preámbulo (`proprietary airMAX/LTU module`). |
| `duty_cycle` (`show`/`store`) | `ame_dev.ko` + `ame_bbp_set_duty_cycle` | Define la partición `DL/UL` (`67/33` óptimo para WISP residencial con tráfico asimétrico `IPTV + Bulk TCP`) derivada de `dl_symbols` y `ul_symbols` (`proprietary airMAX/LTU module`). |
| `bc_dl_symbols` (`show`/`store`) | `ame_dev.ko` + `ame_core_set_bc_dl_symbols` | Símbolos OFDM de broadcast downlink (`UL-MAP` / control); mantener `bc_dl_symbols=2` evita desperdicio de símbolos en sectores `SQ <= 16` (`proprietary airMAX/LTU module`). |
| `frame_pulse_offset` (`show`/`store`) | `ame_dev.ko` + `ame_bbp_is_remote_SFN_synchronized` | Alinea el pulso `1PPS` / `SFN` entre paneles co-localizados (`ABAB` frequency reuse) y valida `bbp_get_ul_subframe_length_forDFS` (`hardware`). |
| `rx/tx freq` Split + `sched_ulmap_dump` | `ame_core.ko` + `AD9361` Fastlock | En modo Split Frequency, `AD9361` conmuta perfiles `Fastlock` entre los subframes `bbp_get_tx_sub_frame_length` y `bbp_get_rx_sub_frame_length` (`hardware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
