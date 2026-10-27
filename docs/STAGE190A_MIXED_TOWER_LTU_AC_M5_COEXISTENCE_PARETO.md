<!-- doc-head: STAGE190A_MIXED_TOWER_LTU_AC_M5_COEXISTENCE_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 190A: SimPy + Pymoo NSGA-III Mixed-Generation Tower Coexistence Benchmark

## 1. Co-Site Tower Architecture (`INFERRED` / `CONFIRMED` — `SimPy` + `pymoo` `NSGA-III`)
- **Co-Located Sectors**: Sector 1 `LTU Rocket 12x` (`40 MHz`, `4096-QAM`), Sector 2 `OpenMAX WA/XC 8x` (`40 MHz`, `256-QAM`, `AQL=4000 us`), Sector 3 `airMAX M5 XW/XM` (`20 MHz`, `64-QAM`).
- **Safety**: 100% discrete-event simulation; zero touches on `/dev/ame*` or `.241`/`.242`/`.20`/`.250`.

## 2. Baseline vs GPS-Synced Guard-Band Champion
| Profile | Guard Bands (`LTU-AC` / `AC-M5`) | GPS Sync | LTU 12x (Mbps) | OpenMAX 8x (Mbps) | M5 (Mbps) | Tower Aggregate (Mbps) | Tower `p99` (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Unsynced Tight Guard | `5 / 5 MHz` | `False` | `390.09` | `177.21` | `44.29` | `611.59` | `29.156` |
| **GPS-Synced Champion** | **`25 / 20 MHz`** | **`True`** | **`572.55`** | **`329.87`** | **`78.96`** | **`981.38` (`+60.46%`)** | **`5.163`** |

## 3. Co-Site Deployment Rules
- **Guard Band**: Enforce $\ge 25\text{ MHz}$ edge-to-edge guard band between `LTU 12x` (`4096-QAM`) and `airMAX AC` (`256-QAM`) so out-of-band phase noise stays below the `-42 dB` EVM floor required by `startThrd_4096=97%`.
- **GPS 1PPS Frame Lock**: Lock `LTU` (`80` symbols `2.0 ms`, `duty_cycle=670`) and co-located TDD sectors to a common DL/UL split to prevent near-field LNA saturation.
