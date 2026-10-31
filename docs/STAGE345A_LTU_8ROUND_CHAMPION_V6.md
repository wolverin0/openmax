<!-- doc-head: STAGE345A_LTU_8ROUND_CHAMPION_V6.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 345A — Consolidated 8-Round (`96`-Window) Live LTU-Lite (`.110`) Safe Linux Champion `v6`

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `hardware`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v6`)
- **SHA-256**: `493ec02748a766fe063451684e16094649238fd466fe6bfb81e9cad2d12e1cb2`
- **Live Evidence Base**: `8` campaigns (`Stages 185A, 188A, 218A, 247A, 287A, 299A, 329A, 341A`) = **`24` counterbalanced `A1->B1->A2->B2` rounds (`96` live windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v6` Knob Stack (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v6` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **SMP IRQ / RPS Steering** | `irq/52` (`ame_asic0`), `ath0`/`br0` `rps_cpus` | `2` (`CPU1` softirq steering, `IRQ 52` isolated) | `Stage 185A` / `329A` |
| **QCA8337N / GMAC0 BQL** | `byte_queue_limits/limit_max` & `tx_queue_len` | `36288` (`24` MTUs) / `256` | `Stage 185A` / `188A` |
| **NAPI & SoftIRQ Budget** | `netdev_budget` / `dev_weight` / `budget_usecs` | `480` / `48` / `4000` | `Stage 188A` / `329A` |
| **Socket Buffers & RFS** | `rmem/wmem_default` (`max`) & `rps_sock_flow_entries` | `262144` (`524288`) & `4096` (`2048`/queue) | `Stage 287A` |
| **TCP Pacing & Lowat** | `tcp_pacing_ca/ss_ratio` & `tcp_notsent_lowat` | `120` / `200` & `16384` (`limit_output=65536`) | `Stage 185A` / `247A` |
| **TFO, TLP & Passive ECN** | `tcp_fastopen` / `tcp_early_retrans` / `tcp_ecn` | `3` / `3` (TLP) / `2` | `Stage 341A` |
| **VoIP & FQ-CoDel** | `udp_rmem/wmem_min` & `fq_codel target/interval` | `16384` & `target 2000us interval 40000us ecn` | `Stage 299A` |
| **Conntrack Hardening** | `nf_conntrack_tcp_be_liberal` & `udp_timeout` | `1` & `30s` (`stream=120s`, `max=16384`) | `Stage 247A` / `329A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
