<!-- doc-head: STAGE579A_LTU_TDMA_FRAMELEN_AND_SPLIT_FREQ_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 579A — `AF-LTU` TDMA Frame Duration (`1ms`–`5ms`), Split TX/RX Frequency & `bc_dl_symbols` Pareto

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-579A` (reconciled with OpenCode `Stage 564A`)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko`, `eab_driver.ko`), `hardware` (`Beetle` + `ame_ASIC0`).
- **Key Findings**:
  1. **TDMA Frame Duration (`1ms`–`5ms`)**: `2.0 ms` (`rtt_p95 = 2.15 ms`, `562.4 Mbps`) and `2.5 ms` (`rtt_p95 = 2.55 ms`, `579.8 Mbps`) lie on the sweet-spot knee of the Pareto frontier between ultra-low-latency `1.0 ms` (`rtt_p95 = 1.45 ms`, `14.2%` framing overhead) and high-capacity `4.0 ms` (`591.2 Mbps`, `4.1%` overhead).
  2. **Split TX/RX Frequency (`40 MHz` Delta)**: Isolating TX and RX center frequencies by `>= 40 MHz` decouples near-field co-site interference and enables asymmetric clean RX channels.
  3. **`ame_core_set_bc_dl_symbols`**: Setting `bc_dl_symbols=1` for PtP and clean PtMP sectors saves `1.8%`–`2.7%` of downlink airtime per frame compared to `bc_dl_symbols=4`.

## 2. Pareto Matrix (`AF-LTU`)
| Candidate | Frame (`ms`) | Split Delta (`MHz`) | `bc_dl_symbols` | Goodput (`Mbps`) | RTT `p95` (`ms`) | Overhead (`%`) | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `LTU_1MS_SPLIT40_BC1_ULTRA_LOW_LATENCY` | `1.0` | `40` | `1` | `498.0` | **`1.45`** | `14.2%` | **`True`** |
| `LTU_2MS_SPLIT40_BC1_BALANCED_PARETO` | `2.0` | `40` | `1` | **`562.4`** | **`2.15`** | `7.4%` | **`True`** |
| `LTU_2_5MS_SPLIT40_BC1_SWEETSPOT_PARETO` | `2.5` | `40` | `1` | **`579.8`** | **`2.55`** | `5.9%` | **`True`** |
| `LTU_4MS_SPLIT40_BC2_HIGH_CAPACITY` | `4.0` | `40` | `2` | **`591.2`** | `3.85` | **`4.1%`** | **`True`** |
| `LTU_5MS_SPLIT0_BC4_DEFAULT_UNISOLATED` | `5.0` | `0` | `4` | `534.0` | `5.10` | `6.8%` | `False` |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage579a_ltu_tdma_framelen_and_split_freq_pareto.py`](../tools/autoresearch/build_stage579a_ltu_tdma_framelen_and_split_freq_pareto.py)
- **Receipt**: [`artifacts/autoresearch/stage579a_ltu_tdma_framelen_and_split_freq_pareto.json`](../artifacts/autoresearch/stage579a_ltu_tdma_framelen_and_split_freq_pareto.json)
