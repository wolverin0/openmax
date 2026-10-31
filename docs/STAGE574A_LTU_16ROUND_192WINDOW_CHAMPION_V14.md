<!-- doc-head: Stage 574A Consolidated 16-Round (192-Window Milestone!) Universal LTU 5-Board Safe Linux Champion v14 (<220 lines) -->
`Stage 574A` consolida las `16` campañas (`48` rondas `A1->B1->A2->B2` = **`192` ventanas reales** en `198.18.0.63`) y el helper `fmx_ltu_tdma_split_sfn_helper.sh` (`Stage 572A`) en `rc.poststart_ltu_safe_champion.sh` (`v14`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 574A — Consolidated 16-Round (`192`-Window Milestone!) Universal LTU 5-Board Safe Linux Champion `v14` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v14`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v14.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v14.json)
- **SHA-256**: `726c1b61afd0420bab3df280247e54e0a6335b1c1ebb56d2ac4d2a7cd0a1c3d8`
- **Live Evidence Base**: **`16` campaigns (`48` counterbalanced `A1->B1->A2->B2` rounds = `192` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v14` 16-Round Knob Stack + `Stage 572A` TDMA Split/SFN Helper (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v14` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **TDMA Framing & Split/SFN Helper** | `fmx_ltu_tdma_split_sfn_helper.sh` | `--inspect-only` (`frame_len=2ms`, `duty_cycle=67%`, `bc_dl_symbols=2`, `SFN`) | `Stage 564A` / `572A` |
| **TDMA-Aligned TCP Pacing** | `tcp_pacing_ca_ratio` / `ss_ratio` | `110` / `160` + `netdev_budget_usecs=4000` | `Stage 571A` |
| **Super-4096 DPD & EVM Guard** | `fmx_ltu_super4096_dpd_evm_guard.sh` | `--inspect-only` (`<= -38 dB` EVM, `4 dB` PA backoff) | `Stage 558A` |
| **Burst CWND & Route Cache** | `tcp_slow_start_after_idle` / `no_metrics_save` | `0` (holds cwnd across bursts) / `1` | `Stage 557A` |
| **AD9361 Fastlock & Temp LUT** | `fmx_ltu_ad9361_fastlock_temp_helper.sh` | `--inspect-only` (`8` fastlock slots `0x25A..0x29F`) | `Stage 486A` / `538A` |
| **PMTU & F-RTO Recovery** | `tcp_mtu_probing` / `tcp_frto` | `1` (Blackhole-only) / `2` (SACK F-RTO) | `Stage 537A` |
| **DCXO GPS vs TCXO Monitor** | `fmx_ltu_dcxo_gps_tcxo_monitor.sh` | `--inspect-only` (`<=0.25 ppm` `12x` CFO guard) | `Stage 486A` / `502A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
