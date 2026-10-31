<!-- doc-head: Stage 470A Consolidated 12-Round (144-Window) Universal LTU 5-Board Safe Linux Champion v10 (<220 lines) -->
`Stage 470A` consolida las `12` campañas (`36` rondas `A1->B1->A2->B2` = **`144` ventanas reales** en `198.18.0.63`) y los hallazgos RE de `Stage 460A` (`Beetle DMA Ring & IRQ 52 Coalescing`) en `rc.poststart_ltu_safe_champion.sh` (`v10`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 470A — Consolidated 12-Round (`144`-Window Milestone!) Universal LTU 5-Board Safe Linux Champion `v10` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v10`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v10.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v10.json)
- **SHA-256**: `28ba77b4d3841296e6a50696c034390094586f663ba089bbc92f552829b31ecb`
- **Live Evidence Base**: **`12` campaigns (`36` counterbalanced `A1->B1->A2->B2` rounds = `144` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v10` 12-Round Knob Stack + `Stage 460A` DMA Ring Integration (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v10` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |
| **PREEMPT-RT & Timer Migration** | `sched_rt_runtime_us` / `timer_migration` | `980000` (`98%` RT) / `0` (local CPU timer pinning) | `Stage 375A` / `439A` |
| **QCA8337N / GMAC0 BQL** | `byte_queue_limits/limit_max` & `tx_queue_len` | `36288` (`24` MTUs) / `256` | `Stage 185A` / `188A` |
| **NAPI & SoftIRQ Budget** | `netdev_budget` / `dev_weight` / `budget_usecs` | `480` / `48` / `4000` | `Stage 188A` / `329A` |
| **Socket Buffers & RFS** | `rmem/wmem_default` (`max`) & `rps_sock_flow_entries` | `262144` (`524288`) & `4096` (`2048`/queue) | `Stage 287A` |
| **TCP Pacing, Lowat & Autocork** | `tcp_pacing_ca/ss_ratio` / `notsent_lowat` / `autocork` | `120` / `200` / `12288` (`8` MSS) / `0` | `Stage 247A` / `375A` / `439A` |
| **TFO, TLP=3, ECN & Thin-Stream** | `tcp_fastopen` / `early_retrans` / `thin_linear_timeouts` | `3` / `3` (TLP) / `1` (`thin_dupack=1`, `ecn=2`) | `Stage 341A` / `439A` / `467A` |
| **VoIP & FQ-CoDel** | `udp_rmem/wmem_min` & `fq_codel target/interval` | `16384` & `target 2000us interval 40000us ecn` | `Stage 299A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
