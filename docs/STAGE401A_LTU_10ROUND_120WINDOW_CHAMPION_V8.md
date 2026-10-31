<!-- doc-head: STAGE401A_LTU_10ROUND_120WINDOW_CHAMPION_V8.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 401A — Consolidated 10-Round (`120`-Window Milestone!) Universal LTU 5-Board Safe Linux Champion `v8`

- **Status**: `CONFIRMED`
- **Attribution**: `Linux`, `hardware`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v8`)
- **SHA-256**: `2a7361c5a5014dba2d47fa0c39fed3f6eee1f92ec7f4e6ef87c5d870ba29e8e6`
- **Live Evidence Base**: **`10` campaigns (`30` counterbalanced `A1->B1->A2->B2` rounds = `120` live measurement windows)** on `198.18.0.63` (`Boca 5`).
- **Universal Board Coverage**: `0xae08` (`LTU-Lite`), `0xae07` (`LTU-LR`), `0xae02` (`LTU-Pro`), `0xae09` (`LTU-XR`), `0xae0b` (`LTU-Instant`), and `0xae06` (`LTU-Rocket`).

## 1. Consolidated `v8` 10-Round Knob Stack (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v8` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **SMP IRQ / RPS Steering** | `irq/52` (`ame_asic0`), `ath0`/`br0` `rps_cpus` | `2` (`CPU1` softirq steering, `IRQ 52` isolated) | `Stage 185A` / `329A` |
| **PREEMPT-RT Scheduler** | `sched_rt_runtime_us` / `min_granularity_ns` | `980000` (`98%` RT) / `1500000` (`1.5 ms`) | `Stage 375A` |
| **QCA8337N / GMAC0 BQL** | `byte_queue_limits/limit_max` & `tx_queue_len` | `36288` (`24` MTUs) / `256` | `Stage 185A` / `188A` |
| **NAPI & SoftIRQ Budget** | `netdev_budget` / `dev_weight` / `budget_usecs` | `480` / `48` / `4000` | `Stage 188A` / `329A` |
| **Socket Buffers & RFS** | `rmem/wmem_default` (`max`) & `rps_sock_flow_entries` | `262144` (`524288`) & `4096` (`2048`/queue) | `Stage 287A` |
| **VM Dirty & VFS Cache** | `dirty_ratio` / `dirty_background_ratio` / `vfs_pressure` | `10` / `5` / `50` (`min_free_kbytes=4096`) | `Stage 185A` / `397A` |
| **TCP Pacing & Autocork** | `tcp_pacing_ca/ss_ratio` & `tcp_autocorking` | `120` / `200` & `0` (`lowat=16384`, `limit=65536`) | `Stage 247A` / `375A` |
| **TFO, TLP & Passive ECN** | `tcp_fastopen` / `tcp_early_retrans` / `tcp_ecn` | `3` / `3` (TLP) / `2` | `Stage 341A` |
| **VoIP & FQ-CoDel** | `udp_rmem/wmem_min` & `fq_codel target/interval` | `16384` & `target 2000us interval 40000us ecn` | `Stage 299A` |
| **Conntrack Hardening** | `nf_conntrack_tcp_be_liberal` & `udp_timeout` | `1` & `30s` (`stream=120s`, `max=16384`) | `Stage 247A` / `329A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
