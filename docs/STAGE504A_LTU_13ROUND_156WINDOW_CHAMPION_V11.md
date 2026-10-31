<!-- doc-head: Stage 504A Consolidated 13-Round (156-Window) Universal LTU 5-Board Safe Linux Champion v11 (<220 lines) -->
`Stage 504A` consolida las `13` campañas (`39` rondas `A1->B1->A2->B2` = **`156` ventanas reales** en `198.18.0.63`) y el monitor `fmx_ltu_dcxo_gps_tcxo_monitor.sh` (`Stage 502A`) en `rc.poststart_ltu_safe_champion.sh` (`v11`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 504A — Consolidated 13-Round (`156`-Window Milestone!) Universal LTU 5-Board Safe Linux Champion `v11` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v11`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v11.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v11.json)
- **SHA-256**: `d4bd13333561bea7f7f91f5051e22520b8996fe516677aabd9d54ba98aae4c7e`
- **Live Evidence Base**: **`13` campaigns (`39` counterbalanced `A1->B1->A2->B2` rounds = `156` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v11` 13-Round Knob Stack + `Stage 502A` DCXO Integration (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v11` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **DCXO GPS vs TCXO Monitor** | `fmx_ltu_dcxo_gps_tcxo_monitor.sh` | `--inspect-only` (`<=0.25 ppm` `12x` CFO guard) | `Stage 486A` / `502A` |
| **RPS Reordering Resilience** | `net.ipv4.tcp_reordering` | `6` (prevents Dual-Core RPS false DupACKs) | `Stage 501A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |
| **PREEMPT-RT & Timer Migration** | `sched_rt_runtime_us` / `timer_migration` | `980000` (`98%` RT) / `0` (local CPU timer pinning) | `Stage 375A` / `439A` |
| **QCA8337N / GMAC0 BQL** | `byte_queue_limits/limit_max` & `tx_queue_len` | `36288` (`24` MTUs) / `256` | `Stage 185A` / `188A` |
| **NAPI & SoftIRQ Budget** | `netdev_budget` / `dev_weight` / `budget_usecs` | `480` / `48` / `4000` | `Stage 188A` / `329A` / `501A` |
| **TCP Pacing, Lowat & Autocork** | `tcp_pacing_ca/ss_ratio` / `notsent_lowat` / `autocork` | `120` / `200` / `12288` (`8` MSS) / `0` | `Stage 247A` / `375A` / `439A` |
| **TFO, TLP=3, ECN & Thin-Stream** | `tcp_fastopen` / `early_retrans` / `thin_linear_timeouts` | `3` / `3` (TLP) / `1` (`thin_dupack=1`, `ecn=2`) | `Stage 341A` / `439A` / `467A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
