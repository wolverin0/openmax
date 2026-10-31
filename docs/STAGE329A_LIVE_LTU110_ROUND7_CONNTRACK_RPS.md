<!-- doc-head: STAGE329A_LIVE_LTU110_ROUND7_CONNTRACK_RPS.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 329A — Live LTU-Lite (`198.18.0.63` Boca 5) Round 7 Deep TCP/UDP Conntrack & SoftIRQ Budget Autoresearch

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `proprietary airMAX/LTU module`, `hardware`
- **Target**: `198.18.0.63` (`LTU-Lite`, `0xae08`, `Linux 3.14.65 SMP PREEMPT RT`, Dual-Core Cortex-A7)
- **Safety Boundary**: Zero `/dev/ame*` touches (`touched_dev_ame_nodes: false`), `45s` rollback watchdog (`FMX-DISC-24`), zero touches to `.241`/`.242`/`.20`/`.250`.

## 1. Round 7 Knobs Tested (`12` Counterbalanced Windows)
| Knob / Sysfs Path | Stock Default (`A1`/`A2`) | Champion `v5` (`B1`/`B2`) | Attribution & Engineering Mechanism |
| :--- | :--- | :--- | :--- |
| `net.netfilter.nf_conntrack_tcp_be_liberal` | `0` | `1` | Prevents spurious out-of-window RST drops during LTU split-duty HARQ retransmission bursts (`Linux`). |
| `net.netfilter.nf_conntrack_udp_timeout` | `30` | `30` (stream `120`) | Bounds stale UDP conntrack table bloat under VoIP/DNS micro-flows (`Linux`). |
| `net.core.netdev_budget` / `dev_weight` | `300` / `64` | `480` / `48` | Prevents `NET_RX` softirq starvation during multi-CPE burst drain while bounding per-NAPI poll slice (`Linux`). |
| `net.core.netdev_budget_usecs` | `8000` (or N/A on `3.14`) | `4000` (graceful fallback on `3.14.65`) | Caps NAPI softirq wall-clock dwell (`Linux`). |
| `eth0` / `br0` `rps_cpus` & `xps_cpus` | `0` | `2` (`CPU1`) | Steers Linux `NET_RX`/`NET_TX` softirqs to `CPU1`, keeping `CPU0` dedicated to `IRQ 52` (`ame_asic0` Beetle FPGA TDMA engine). |

## 2. Live Counterbalanced `A1 -> B1 -> A2 -> B2` Results
- **Total Rounds / Windows**: `3` rounds (`12` windows).
- **Stock Mean Loopback Burst RTT**: `0.22 ms`.
- **Champion `v5` Mean Loopback Burst RTT**: `0.22 ms`.
- **CPU0 `IRQ 52` (`ame_asic0`) Isolation**: `CONFIRMED` (`rps_cpus=2` verified in `B1`/`B2` across all 3 rounds).
