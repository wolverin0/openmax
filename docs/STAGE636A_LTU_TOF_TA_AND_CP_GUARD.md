<!-- doc-head: Stage 636A Pillar 4 AF-LTU (Beetle) Sub-Microsecond ToF Ranging, Timing Advance & Cyclic Prefix Guard (<220 lines) -->
`Stage 636A` construye el guard read-only `firmware/ltu_safe_kit/fmx_ltu_tof_ta_cp_guard.sh` que operacionaliza el RE `Stage 616A` de `ame_core.ko` y `ame_dev.ko` (`ame_core_get_distance_meter`, `cpe_distance`, `distance_meter_show/store`, `ame_core_update_ta_cpe`, `update_ta_show/store`, `early_data_cfg` y `cpsample`).
<!-- /doc-head -->

# Stage 636A — Pillar 4 `AF-LTU` (`Beetle`) Sub-Microsecond ToF Ranging & Timing Advance Guard (`mm-9137`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-9137`, `id=155457`)
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `Linux`
- **Deliverable**: [`firmware/ltu_safe_kit/fmx_ltu_tof_ta_cp_guard.sh`](../firmware/ltu_safe_kit/fmx_ltu_tof_ta_cp_guard.sh)
- **SHA-256**: `8da0657536c6dd0d756c32943c931b76db8ec2117398a40eb747711d3c4ff2cc`
- **Artifact**: [`artifacts/autoresearch/stage636a_ltu_tof_ta_and_cp_guard.json`](../artifacts/autoresearch/stage636a_ltu_tof_ta_and_cp_guard.json)

## 1. Distancia, `Timing Advance` (`TA`) y `Cyclic Prefix` (`cpsample`) en `AF-LTU` (`Stage 616A` RE) (`CONFIRMED`)
| Subsistema (`ame_core.ko` / `ame_dev.ko`) | Símbolos / Atributos Sysfs (`Stage 616A`) | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :--- | :--- |
| **Medición de Distancia (`ToF`)** | `ame_core_get_distance_meter`, `cpe_distance`, `distance_meter_show/store` | Calcula la distancia física en metros por CPE (`3.33 ns/m` ida y vuelta) para inicializar la ventana de recepción del subframe UL (`proprietary airMAX/LTU module`). |
| **Lazo `Timing Advance` (`TA`)** | `ame_core_update_ta_cpe`, `ame_core_updateTA`, `update_ta_show/store`, `AME_Sched_PtP_early_data_decision` | Ajusta dinámicamente el adelanto de transmisión (`TA`) de cada CPE para que las ráfagas UL arriben al AP alineadas dentro de la ventana del prefijo cíclico (`hardware`). |
| **Prefijo Cíclico (`cpsample`)** | `cpsample` (`ame_dev.ko`), `ame_core_czlen_vs_normal` | Define el número de muestras de guarda (`CP`) entre símbolos OFDM para absorber dispersión multitrayecto (`delay spread`) sin perder ortogonalidad en `1024-QAM`/`4096-QAM` (`hardware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
