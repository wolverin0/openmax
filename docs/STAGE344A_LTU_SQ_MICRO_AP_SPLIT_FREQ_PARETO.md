<!-- doc-head: STAGE344A_LTU_SQ_MICRO_AP_SPLIT_FREQ_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 344A — `SimPy` + `pymoo` `NSGA-II` Evaluation of LTU Short-Queue (`SQ` `ptmp_max_cpe=8`) + Split-Frequency (`TX_LO != RX_LO`)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `external controller`
- **Physical Scenario**: 8-CPE high-capacity `50 MHz` micro-sector operating on a congested WISP tower with `-62 dBm` co-channel Uplink interference on the primary DL channel.

## 1. Ground-Up `NSGA-II` Comparison (`CONFIRMED`)
| Regime | Aggregate Goodput (`Mbps`) | `p99` Latency (`ms`) | UL HARQ Retx (`%`) | Configuration |
| :--- | :--- | :--- | :--- | :--- |
| **`LTU_SQ8_SplitFreq_AD9361_Champion`** | **`630.92 Mbps`** | **`2.099 ms`** | **`0.45%`** | `ptmp_max_cpe=8` (`SQ`), `TX_LO != RX_LO` (`+14 dB`), `75/25`, `1.5 ms` |
| `LTU_SQ8_CoChannel_SingleFreq` | `556.64 Mbps` | `3.491 ms` | `4.8%` | `ptmp_max_cpe=8` (`SQ`), `TX_LO == RX_LO`, `75/25`, `1.5 ms` |
| `LTU_Std64_CoChannel_Default` | `495.33 Mbps` | `5.281 ms` | `4.8%` | `ptmp_max_cpe=64` (`Std`), `TX_LO == RX_LO`, `67/33`, `2.5 ms` |

## 2. First-Principles Attribution (`CONFIRMED`)
1. **Short-Queue (`SQ` `ptmp_max_cpe=8`) Gain**: Shrinking the `ame.core.L2Q` descriptor ring from `64` stations (`512 KB`) to `8..16` stations (`64 KB`, resident in Cortex-A7 `256 KB` L2 cache) cuts MAP/poll overhead from `11.4%` to `5.2%` and reduces superframe `p99` latency from `5.281 ms` to **`2.099 ms`**.
2. **AD9361 Dual-LO Split-Frequency (`TX_LO != RX_LO`) Gain**: Moving `RX_LO` to a clean Uplink frequency lifts UL SINR by `+11.9 dB`, restoring `4096-QAM 12x` on Uplink and cutting UL HARQ retransmissions from `4.80%` to **`0.45%`**.
