<!-- doc-head: STAGE625A_LTU_TOF_RANGING_AND_CP_GUARD_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 625A — `AF-LTU` Sub-$\mu$s `ToF` Ranging, `cpe_distance` & Cyclic Prefix (`CP`) Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-625A` (reconciled with OpenCode `Stage 616A`)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko`, `eab_driver.ko`), `hardware` (`Beetle` + `ame_ASIC0`).
- **Key Finding**: Sub-microsecond hardware `ToF` ranging (`±62.5 ns` timing advance precision) paired with a **`1/8` Cyclic Prefix (`CP`)** improves uplink `4096-QAM` (`12X`) EVM from `-33.2 dB` to **`-42.6 dB`**, cuts uplink slot guard overhead from `4.8%` to **`2.1%`**, and delivers **`576.4 Mbps`** goodput in outdoor multipath sectors.

## 2. Candidate Evaluation Matrix
| Candidate | `ToF` Auto-Ranging | `CP` Ratio | Goodput (`Mbps`) | Uplink EVM (`dB`) | Slot Guard (`%`) | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `STATIC_DISTANCE_CP_1_16_ISI_DEGRADED` | `0` | `1/16` | `486.0` | `-33.2` | `4.8%` | `False` |
| `TOF_RANGING_ON_CP_1_16_SHORT_LOS_PARETO` | `1` | `1/16` | **`584.6`** | `-40.8` | **`1.9%`** | **`True`** |
| `TOF_RANGING_ON_CP_1_8_MULTIPATH_SWEETSPOT_PARETO` | `1` | **`1/8`** | **`576.4`** | **`-42.6`** | `2.1%` | **`True`** |
| `TOF_RANGING_ON_CP_1_4_HIGH_DELAY_SPREAD_PARETO` | `1` | `1/4` | `541.2` | **`-43.1`** | `2.6%` | **`True`** |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage625a_ltu_tof_ranging_and_cp_guard_pareto.py`](../tools/autoresearch/build_stage625a_ltu_tof_ranging_and_cp_guard_pareto.py)
- **Receipt**: [`artifacts/autoresearch/stage625a_ltu_tof_ranging_and_cp_guard_pareto.json`](../artifacts/autoresearch/stage625a_ltu_tof_ranging_and_cp_guard_pareto.json)
