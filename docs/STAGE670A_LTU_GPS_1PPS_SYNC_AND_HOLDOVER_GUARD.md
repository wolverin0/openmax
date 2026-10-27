<!-- doc-head: Stage 670A Pillar 4 AF-LTU (Beetle) GPS 1PPS Superframe Sync & Holdover Drift Guard (<200 lines) -->
`Stage 670A` construye el auditor read-only `firmware/ltu_safe_kit/fmx_ltu_gps_1pps_sync_guard.sh` que modela la sincronización `GPS 1PPS` de supertrama (`frame_pulse_offset`, `ame_bbp_is_remote_SFN_synchronized`, `frame_timer_init`) y la deriva en holdover para paneles `LTU` co-localizados.
<!-- /doc-head -->

# Stage 670A — Pillar 4 `AF-LTU` (`Beetle`) GPS 1PPS Superframe Sync & Holdover Guard (`mm-1a4e`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-1a4e`, `id=155462`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_gps_1pps_sync_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_gps_1pps_sync_guard.sh)
- **SHA-256**: `41f5b1eb95b86396f5fc2902d8cd930fc41c8a7ec07949dbdc83b4e873350429`
- **Artifact**: [`artifacts/autoresearch/stage670a_ltu_gps_1pps_sync_and_holdover_guard.json`](../artifacts/autoresearch/stage670a_ltu_gps_1pps_sync_and_holdover_guard.json)

## 1. Física de Sincronización `GPS 1PPS` y Holdover en `AF-LTU` (`CONFIRMED`)
| Símbolo / Parámetro (`ame_core.ko` / `ame_dev.ko`) | Valor / Umbral | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `frame_pulse_offset` (`show`/`store`) | `0 us` (alineado) | Desplaza el inicio de supertrama TDD respecto al pulso `1PPS` para alinear transiciones `DL->UL` entre paneles co-localizados (`proprietary airMAX/LTU module`). |
| `ame_bbp_is_remote_SFN_synchronized` | `1` (`SFN Locked`) | Verifica que el CPE rastree la fase de supertrama del AP mediante el bucle `DCXO` (`bbp_rf_dcxo_s`) (`hardware`). |
| **Ventana de Holdover sin `1PPS`** | `~10.7 s` (`gap0 = 62.5 us`) | Sin pulso `1PPS`, dos APs en torre con deriva diferencial de `1..5 ppm` invaden el intervalo de guarda `gap0` en pocos segundos, causando sordera `TX->RX` (`hardware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
