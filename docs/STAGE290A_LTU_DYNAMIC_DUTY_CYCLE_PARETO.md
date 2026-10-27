<!-- doc-head: STAGE290A_LTU_DYNAMIC_DUTY_CYCLE_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 290A: SimPy + Pymoo NSGA-II Dynamic vs Fixed Duty-Cycle 32-CPE Benchmark

## 1. Asymmetric Burst Traffic Comparison (`32` CPEs, `40 MHz`)
| Scheduler Mode | DL Goodput (Mbps) | UL Goodput (Mbps) | Sector Aggregate (Mbps) | UL Burst `p99` (ms) | DL `p99` (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **LTU Auto-Duty (`50/50` $\leftrightarrow$ `75/25`)** | `314.06` | `142.39` | **`456.45`** | **`3.693`** | `2.48` |
| **LTU Fixed `67/33` (GPS Co-Site Safe)** | `326.84` | `125.56` | `452.4` | `5.128` | `2.192` |
| **OpenMAX WA/XC (`AQL=4000 us`)** | `225.08` | `86.72` | `311.8` | `4.478` | `3.192` |

## 2. Deployment Policy
- **Single-AP Rural Tower**: Enable `Auto-Duty` to cut uplink burst `p99` latency from `5.128 ms` to `3.693 ms` while maximizing peak `75/25` downlink throughput.
- **Multi-AP GPS-Synchronized Tower**: Lock all co-located LTU sectors to fixed `67/33` (`duty_cycle=670`) to prevent DL-into-UL cross-sector collisions.
