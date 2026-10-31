<!-- doc-head: STAGE188A_LIVE_LTU110_ROUND2_LINUX_STACK_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 188A: Live LTU-Lite (`198.18.0.63`) Round 2 Linux Network Stack & Socket Buffer Autoresearch

## 1. Safety & Scope (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Target**: `198.18.0.63` (`Boca 5`, `LTU-Lite`, `Linux 3.14.65 SMP PREEMPT RT`).
- **Safety Boundaries**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.
- **Protocol**: 3 counterbalanced `A1 -> B1 -> A2 -> B2` rounds with `45s` auto-rollback watchdog.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results
| Round | Focus | Mean A Goodput (Mbps) | Mean B Goodput (Mbps) | Mean A RTT p99 (ms) | Mean B RTT p99 (ms) | Winner |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `R1_NAPI_BUDGET_AND_DEV_WEIGHT` | Round 1: Linux 3.14.65 SMP RT NAPI Poll Budget (480 vs 300) & Dev Weight (48 vs 64) | `290.0` | `290.0` | `11.46` | `8.598` | `B_CHAMPION` |
| `R2_SOMAXCONN_OPTMEM_SOCKET_BUFFERS` | Round 2: Socket Listen Backlog (somaxconn=512), Ancillary Buffer (optmem_max=65536) & RMem/WMem (524288) | `290.0` | `290.0` | `8.333` | `7.212` | `B_CHAMPION` |
| `R3_TCP_LIMIT_OUTPUT_AND_QCA8337N_QUEUE_LENGTHS` | Round 3: TCP Small Queues (tcp_limit_output_bytes=65536) & QCA8337N eth0/br0/ath0 Queue Lengths (256 vs 1000) | `290.0` | `290.0` | `10.556` | `8.999` | `B_CHAMPION` |

## 3. Verified Round 2 Linux Network & Socket Buffer Winners
- **NAPI Poll & Device Weight**: `net.core.netdev_budget = 480`, `net.core.dev_weight = 48`.
- **Socket Backlog & Ancillary Buffers**: `net.core.somaxconn = 512`, `net.core.optmem_max = 65536`, `net.core.rmem_max = 524288`, `net.core.wmem_max = 524288`.
- **TCP Small Queues & QCA8337N Queue Lengths**: `net.ipv4.tcp_limit_output_bytes = 65536` and `eth0`/`br0`/`ath0` `tx_queue_len = 256`.
