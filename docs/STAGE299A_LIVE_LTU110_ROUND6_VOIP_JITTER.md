<!-- doc-head: STAGE299A_LIVE_LTU110_ROUND6_VOIP_JITTER.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 299A: Live LTU-Lite (`198.18.0.63`) Round 6 ICMP/UDP Micro-Burst Jitter & VoIP Pacing

## 1. Scope & Safety (`CONFIRMED` — Attribution: `Linux` / `hardware`)
- **Target**: `198.18.0.63` (`Boca 5`, `LTU-Lite`, `Linux 3.14.65 SMP PREEMPT RT`).
- **Safety Boundaries**: `0` touches on `/dev/ame*`; `0` touches on `.241`, `.242`, `.20`, or `.250`.
- **Protocol**: 3 counterbalanced `A1 -> B1 -> A2 -> B2` rounds with `45s` auto-rollback watchdog.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Results
| Round | Focus | Mean A Goodput (Mbps) | Mean B Goodput (Mbps) | Mean A RTT `p99` (ms) | Mean B RTT `p99` (ms) | Winner |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `R1_UDP_MIN_BUFFERS_16KB` | Round 1: VoIP/RTP UDP Minimum Socket Buffers (udp_rmem_min=16384, udp_wmem_min=16384 vs 4096) | `297.0` | `297.0` | `18.585` | `11.22` | `B_CHAMPION` |
| `R2_PING_GROUP_AND_EPHEMERAL_PORT_RANGE` | Round 2: Fast ICMP Socket Group Range (0..2147483647) & Ephemeral Port Range (10240..65535) | `297.0` | `297.0` | `10.656` | `9.068` | `B_CHAMPION` |
| `R3_FQ_CODEL_TARGET_2000US_VS_2500US` | Round 3: FQ-CoDel VoIP Micro-Burst Target (target 2000us interval 40000us vs 2500us/50000us on eth0/ath0) | `297.0` | `297.0` | `38.934` | `24.966` | `B_CHAMPION` |

## 3. Verified Round 6 Winners
- **UDP VoIP/RTP Reserve**: `net.ipv4.udp_rmem_min = 16384`, `net.ipv4.udp_wmem_min = 16384`.
- **ICMP & Ephemeral Ports**: `net.ipv4.ping_group_range = "0 2147483647"`, `net.ipv4.ip_local_port_range = "10240 65535"`.
- **FQ-CoDel 2.0ms Superframe-Matched Target**: `target 2000us interval 40000us quantum 1514 limit 1024 flows 1024 ecn` on `eth0` and `ath0`.
