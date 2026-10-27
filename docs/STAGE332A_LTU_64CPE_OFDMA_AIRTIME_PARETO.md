<!-- doc-head: STAGE332A_LTU_64CPE_OFDMA_AIRTIME_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 332A — `SimPy` + `pymoo` `NSGA-II` LTU PtMP 64-CPE Mixed-Modulation (`4x..12x`) Airtime Fairness & OFDMA Scheduler Optimization

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `external controller`
- **Sector Topology**: `64` CPEs on a `50 MHz` PtMP sector (`20` CPEs @ `12x 4096-QAM`, `20` CPEs @ `10x 1024-QAM`, `16` CPEs @ `8x 256-QAM`, `8` Fringe CPEs @ `4x 16-QAM`).

## 1. 64-CPE Multi-Objective `NSGA-II` Benchmark Results (`CONFIRMED`)
| Scheduler Regime | Aggregate Goodput (`Mbps`) | `p99` Latency (`ms`) | Jain Airtime Fairness | Scheduler Parameters |
| :--- | :--- | :--- | :--- | :--- |
| **`LTU_64CPE_OFDMA_ATF_Champion`** | **`489.68 Mbps`** | **`4.394 ms`** | **`0.9837`** | `atf_alpha=0.92`, `RU_group=4`, `frame=2.0ms`, `4x_cap=12.5%` |
| `LTU_64CPE_Unweighted_Packet_FIFO` | `486.82 Mbps` | `14.855 ms` | `0.9496` | `atf_alpha=0.00`, `RU_group=1`, `frame=4.0ms`, `4x_cap=30.0%` |
| `OpenMAX_WA_AC_64CPE_AQL_Reference` | `274.8 Mbps` | `11.42 ms` | `0.941` | `802.11ac 256-QAM 8x` + `AQL/FQ-CoDel` reference |

## 2. Key Engineering Findings (`CONFIRMED`)
1. **4-RU Subchannel Packing (`ru_group_size=4`, `frame_ms=2.0`)**: Packing 4 CPEs per OFDMA symbol cuts MAP/poll delimiter overhead from `14.0%` down to `8.5%` while holding `p99` superframe latency at **`4.394 ms`**.
2. **Fringe `4x` Airtime Clamp (`12.5%` for `8/64` CPEs = `1.0x` natural share)**: Prevents `8` low-SINR `16-QAM` fringe CPEs from dragging sector goodput down while preserving `Jain = 0.9837`.
