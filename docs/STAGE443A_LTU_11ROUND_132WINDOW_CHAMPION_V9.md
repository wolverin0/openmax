<!-- doc-head: Stage 443A Consolidated 11-Round (132-Window) Universal LTU 5-Board Safe Linux Champion v9 (<220 lines) -->
`Stage 443A` consolida las `11` campañas (`33` rondas `A1->B1->A2->B2` = `132` ventanas reales en `198.18.0.63`) en el kit `v9` (`rc.poststart_ltu_safe_champion.sh` + `ltu_5board_universal_manifest_v9.json`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 443A — Consolidated 11-Round (`132`-Window Milestone!) Universal LTU 5-Board Safe Linux Champion `v9` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v9`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v9.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v9.json)
- **SHA-256**: `ff277409cc1c8edc04addc8df5b8b1b61389ca4194a4567eb9916ddd2a3c7193`
- **Live Evidence Base**: **`11` campaigns (`33` counterbalanced `A1->B1->A2->B2` rounds = `132` live measurement windows)** on `198.18.0.63` (`Boca 5`).
- **Universal Board Coverage**: `0xae08` (`LTU-Lite`), `0xae07` (`LTU-LR`), `0xae02` (`LTU-Pro`), `0xae09` (`LTU-XR`), `0xae0b` (`LTU-Instant`), and `0xae06` (`LTU-Rocket`).

## 1. Consolidated `v9` 11-Round Knob Stack (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v9` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **SMP IRQ / RPS Steering** | `irq/52` (`ame_asic0`), `ath0`/`br0` `rps_cpus` | `2` (`CPU1` softirq steering, `IRQ 52` isolated) | `Stage 185A` / `329A` |
| **PREEMPT-RT & Timer Migration** | `sched_rt_runtime_us` / `timer_migration` | `980000` (`98%` RT) / `0` (local CPU timer pinning) | `Stage 375A` / `439A` |
| **QCA8337N / GMAC0 BQL** | `byte_queue_limits/limit_max` & `tx_queue_len` | `36288` (`24` MTUs) / `256` | `Stage 185A` / `188A` |
| **NAPI & SoftIRQ Budget** | `netdev_budget` / `dev_weight` / `budget_usecs` | `480` / `48` / `4000` | `Stage 188A` / `329A` |
| **Socket Buffers & RFS** | `rmem/wmem_default` (`max`) & `rps_sock_flow_entries` | `262144` (`524288`) & `4096` (`2048`/queue) | `Stage 287A` |
| **VM Dirty & VFS Cache** | `dirty_ratio` / `dirty_background_ratio` / `vfs_pressure` | `10` / `5` / `50` (`min_free_kbytes=4096`) | `Stage 185A` / `397A` |
| **TCP Pacing, Lowat & Autocork** | `tcp_pacing_ca/ss_ratio` / `notsent_lowat` / `autocork` | `120` / `200` / `12288` (`8` MSS) / `0` | `Stage 247A` / `375A` / `439A` |
| **TFO, TLP, ECN & Thin-Stream** | `tcp_fastopen` / `early_retrans` / `thin_linear_timeouts` | `3` / `3` (TLP) / `1` (`thin_dupack=1`, `ecn=2`) | `Stage 341A` / `439A` |
| **VoIP & FQ-CoDel** | `udp_rmem/wmem_min` & `fq_codel target/interval` | `16384` & `target 2000us interval 40000us ecn` | `Stage 299A` |
| **Conntrack Hardening** | `nf_conntrack_tcp_be_liberal` & `udp_timeout` | `1` & `30s` (`stream=120s`, `max=16384`) | `Stage 247A` / `329A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
