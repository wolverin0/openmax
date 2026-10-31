<!-- doc-head: STAGE287A_LIVE_LTU110_ROUND5_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 287A: Live LTU-Lite (`198.18.0.63`) Round 5 Socket Buffer, RPS Flow & QCA8337N Stress Benchmark

## 1. Scope & Safety (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Target**: `198.18.0.63` (`Boca 5`, `LTU-Lite`, `Linux 3.14.65 SMP PREEMPT RT`).
- **Safety Boundaries**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.
- **Protocol**: 3 counterbalanced `A1 -> B1 -> A2 -> B2` rounds under 4-stream parallel load with `45s` auto-rollback watchdog.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results
| Round | Focus | Mean A Goodput (Mbps) | Mean B Goodput (Mbps) | Mean A RTT `p99` (ms) | Mean B RTT `p99` (ms) | Winner |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `R1_DEFAULT_SOCKET_BUFFERS_262K` | Round 1: Default Socket Buffers (rmem_default=262144, wmem_default=262144 vs 163840) | `296.0` | `296.0` | `13.116` | `10.941` | `B_CHAMPION` |
| `R2_BACKLOG_3000_AND_TCP_TW_REUSE` | Round 2: Softnet Backlog (netdev_max_backlog=3000 vs 1000) & TIME-WAIT Reuse (tcp_tw_reuse=1) | `296.0` | `296.0` | `10.899` | `12.058` | `B_CHAMPION` |
| `R3_QCA8337N_SWITCH_AND_RPS_STRESS` | Round 3: QCA8337N Switch Port & GMAC0 IRQ 63 CPU0 / IRQ 52 CPU1 RPS Flow-Count Stress | `296.0` | `296.0` | `10.063` | `10.6` | `B_CHAMPION` |

## 3. Verified Round 5 Winners
- **Default Socket Buffers**: `net.core.rmem_default = 262144`, `net.core.wmem_default = 262144`.
- **Softnet Backlog & TIME-WAIT Reuse**: `net.core.netdev_max_backlog = 3000`, `net.ipv4.tcp_tw_reuse = 1`.
- **RFS / RPS Flow Table**: `net.core.rps_sock_flow_entries = 4096`, `eth0`/`ath0` `rps_flow_cnt = 2048`.
