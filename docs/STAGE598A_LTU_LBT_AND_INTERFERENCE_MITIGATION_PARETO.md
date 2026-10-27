<!-- doc-head: STAGE598A_LTU_LBT_AND_INTERFERENCE_MITIGATION_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 598A — `AF-LTU` Listen-Before-Talk (`LBT`) & Interference Mitigation Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-598A` (reconciled with OpenCode `Stage 590A`)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko`, `eab_driver.ko`), `hardware` (`Beetle` + `ame_ASIC0`).
- **Key Finding**: Enabling hardware-assisted Listen-Before-Talk (`lbt_enable=1`) at an energy-detect threshold of **`-72 dBm`** combined with `bbp_rf_set_intf_mitigation=2` eliminates co-channel burst collision loss (`3.4%` $\rightarrow$ **`0.0%`**), cuts `RTT p99` from `9.80 ms` to **`2.95 ms`**, and lifts goodput from `442.0 Mbps` to **`568.4 Mbps`**.

## 2. Candidate Evaluation Matrix
| Candidate | `lbt_enable` | `ED` Threshold | `intf_mitig` | Goodput (`Mbps`) | RTT `p99` (`ms`) | Collision Loss | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `LBT_OFF_INTF_MITIG_0_DEFAULT_BLIND_TDMA` | `0` | Disabled | `0` | `442.0` | `9.80` | `3.4%` | `False` |
| `LBT_ON_M82DBM_OVER_DEFER` | `1` | `-82 dBm` | `1` | `468.5` | `6.40` | `0.4%` | `False` |
| `LBT_ON_M72DBM_INTF_MITIG_2_SWEETSPOT_PARETO` | `1` | **`-72 dBm`** | **`2`** | **`568.4`** | **`2.95`** | **`0.0%`** | **`True`** |
| `LBT_ON_M68DBM_INTF_MITIG_2_HIGH_THROUGHPUT_PARETO` | `1` | **`-68 dBm`** | **`2`** | **`576.2`** | `3.25` | `0.1%` | **`True`** |
| `LBT_ON_M62DBM_INTF_MITIG_1_UNDER_PROTECTED` | `1` | `-62 dBm` | `1` | `519.0` | `5.60` | `1.2%` | `False` |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage598a_ltu_lbt_and_interference_mitigation_pareto.py`](../tools/autoresearch/build_stage598a_ltu_lbt_and_interference_mitigation_pareto.py)
- **Receipt**: [`artifacts/autoresearch/stage598a_ltu_lbt_and_interference_mitigation_pareto.json`](../artifacts/autoresearch/stage598a_ltu_lbt_and_interference_mitigation_pareto.json)
