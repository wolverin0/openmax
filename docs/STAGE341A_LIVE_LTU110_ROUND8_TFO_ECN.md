<!-- doc-head: STAGE341A_LIVE_LTU110_ROUND8_TFO_ECN.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 341A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 8 Deep TCP FastOpen, Early Retrans & ECN/DSCP Autoresearch

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `hardware`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`)
- **Safety Boundary**: Zero `/dev/ame*` touches (`touched_dev_ame_nodes: false`), `45s` rollback watchdog (`FMX-DISC-24`), zero touches to `.241`/`.242`/`.20`/`.250`.

## 1. Round 8 Knobs Tested (`12` Counterbalanced Windows)
| Knob / Qdisc | Stock Baseline (`A1`/`A2`) | Champion `v6` (`B1`/`B2`) | Engineering Rationale (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| `net.ipv4.tcp_fastopen` | `0` | `3` (Client + Server) | Eliminates 1-RTT SYN handshake penalty for management/telemetry HTTP/SSH sockets (`Linux`). |
| `net.ipv4.tcp_early_retrans` | `2` | `3` (ER + Tail Loss Probe) | Enables Tail Loss Probe (`TLP`) to recover single tail losses across TDD frames without RTO stalls (`Linux`). |
| `net.ipv4.tcp_ecn` | `0` | `2` (Passive/On-Request ECN) | Negotiates ECN without breaking legacy middleboxes (`Linux`). |
| `eth0`/`ath0` `fq_codel` | `target 5000us noecn` | `target 2000us interval 40000us ecn` | Marks CE (`ECN`) at `2.0 ms` queue sojourn while preserving `DSCP EF` (`0xb8`) VoIP priority (`Linux`). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Total Rounds / Windows**: `3` rounds (`12` windows).
- **Stock Mean DSCP EF Burst RTT**: `0.22 ms`.
- **Champion `v6` Mean DSCP EF Burst RTT**: `0.22 ms`.
