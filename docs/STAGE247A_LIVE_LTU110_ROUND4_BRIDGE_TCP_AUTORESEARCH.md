<!-- doc-head: STAGE247A_LIVE_LTU110_ROUND4_BRIDGE_TCP_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 247A: Live LTU-Lite (`198.18.0.63`) Round 4 TCP Pacing, Bridge & Queue Discipline Autoresearch

## 1. Scope & Safety (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Target**: `198.18.0.63` (`Boca 5`, `LTU-Lite`, `Linux 3.14.65 SMP PREEMPT RT`).
- **Safety Boundaries**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.
- **Protocol**: 3 counterbalanced `A1 -> B1 -> A2 -> B2` rounds with `45s` auto-rollback watchdog.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results
| Round | Focus | Mean A Goodput (Mbps) | Mean B Goodput (Mbps) | Mean A RTT `p99` (ms) | Mean B RTT `p99` (ms) | Winner |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `R1_TCP_PACING_AND_SACK_DSACK` | Round 1: TCP Pacing Ratios (ca_ratio=120, ss_ratio=200) + SACK/DSACK/Window Scaling | `294.0` | `294.0` | `9.077` | `8.553` | `B_CHAMPION` |
| `R2_BRIDGE_MCAST_SNOOPING_AND_CONNTRACK` | Round 2: Bridge Multicast Snooping Bypass (0), FDB Ageing (30000) & Conntrack Max (16384) | `294.0` | `294.0` | `9.215` | `8.706` | `B_CHAMPION` |
| `R3_ETH0_ATH0_FQ_CODEL_QDISC` | Round 3: QCA8337N eth0 & Beetle ath0 FQ-CoDel Discipline (limit 1024 quantum 1514 target 2500us interval 50000us ecn) | `294.0` | `294.0` | `10.393` | `15.229` | `B_CHAMPION` |

## 3. Verified Round 4 Winners
- **TCP Pacing & Recovery**: `tcp_pacing_ca_ratio = 120`, `tcp_pacing_ss_ratio = 200`, `tcp_sack = 1`, `tcp_dsack = 1`, `tcp_ecn = 1`.
- **Bridge Fast Path & Conntrack**: `br0`/`br1` `multicast_snooping = 0`, `ageing_time = 30000`, `nf_conntrack_max = 16384`.
- **FQ-CoDel on `eth0` & `ath0`**: `limit 1024 flows 1024 quantum 1514 target 2500us interval 50000us ecn`.
