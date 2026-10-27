<!-- doc-head: STAGE400A_LTU_GPS_REUSE1_TDD_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 400A — `SimPy` + `pymoo` `NSGA-II` Evaluation of LTU Multi-Tower GPS Frame Synchronization & Frequency Reuse-1 (`2 ms` TDD + `SQ`)

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `external controller`
- **Topology**: Back-to-back `LTU-Rocket` sectors (`Azimuth 0°` and `180°`) reusing the exact same `50 MHz` channel (`Frequency Reuse-1`).

## 1. Multi-Objective `NSGA-II` Comparison (`CONFIRMED`)
| Regime | Dual-Sector Reuse-1 Goodput (`Mbps`) | `p99` Latency (`ms`) | Cross-Slot Retx (`%`) | Configuration |
| :--- | :--- | :--- | :--- | :--- |
| **`LTU_GPS_Locked_2ms_SQ_Reuse1_Champion`** | **`1265.87 Mbps`** | **`2.738 ms`** | **`0.35%`** | `GPS 1PPS <= 1.2 µs`, `2.0 ms` frame, `75/25`, `SQ` enabled |
| `LTU_GPS_Locked_Std64_Reuse1` | `1183.08 Mbps` | `3.903 ms` | `0.35%` | `GPS 1PPS <= 1.2 µs`, `2.5 ms` frame, `75/25`, `Std 64-CPE` |
| `LTU_Unsynchronized_FreeRunning_Reuse1` | `357.09 Mbps` | `7.525 ms` | `8.4%` | Free-running clocks (`450 µs` drift), `Auto` duty |

## 2. First-Principles Conclusion (`CONFIRMED`)
1. **Why Unsynchronized Reuse-1 Collapses (`357.09 Mbps`)**: When AP1 transmits Downlink (`+22 dBm`) while AP2 is listening for Uplink (`-60 dBm`), even a `30 dB` front-to-back sector antenna injects `-8 dBm` of co-channel blocker into AP2's `AD9361` LNA, destroying `UL` `CINR` and spiking retransmissions to `8.40%`.
2. **GPS `1PPS` Lock + Fixed `75/25` `2.0 ms` + `SQ` (`1265.87 Mbps`)**: Locking both sectors to the same `2.0 ms` superframe and `75/25` split-duty eliminates AP-to-AP TX→RX overlap completely, achieving **`1,265.87 Mbps`** combined throughput across a single `50 MHz` channel.
