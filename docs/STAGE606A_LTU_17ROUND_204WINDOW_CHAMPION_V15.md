<!-- doc-head: Stage 606A Consolidated 17-Round (204-Window Milestone!) Universal LTU 5-Board Golden Champion v15 (<220 lines) -->
`Stage 606A` consolida las `17` campañas (`51` rondas `A1->B1->A2->B2` = **`204` ventanas reales** en `198.18.0.63`) y el guard `fmx_ltu_200w_golden_guard.sh` (`Stage 604A`) en `rc.poststart_ltu_safe_champion.sh` (`v15`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 606A — Consolidated 17-Round (`204`-Window Milestone!) Universal LTU 5-Board Golden Champion `v15` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v15`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v15.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v15.json)
- **SHA-256**: `c30f453698462ef63ed80eddcf60daa6452600d8b8bfbc93d24eaa6e96233d46`
- **Live Evidence Base**: **`17` campaigns (`51` counterbalanced `A1->B1->A2->B2` rounds = `204` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v15` 17-Round Golden Stack + `Stage 604A` LBT/Spectral Guard (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v15` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **204-Window LBT & Spectral Guard** | `fmx_ltu_200w_golden_guard.sh` | `--inspect-only` (`lbt_enable`, `lbt_detects`, `auto_freq_mode`, `interf_avg`) | `Stage 590A` / `604A` |
| **TCP RACK-TLP Loss Recovery** | `net.ipv4.tcp_recovery` + `early_retrans` | `1` (`RACK`) + `3` (`TLP`) + `tcp_reordering=6` | `Stage 603A` |
| **TDMA Framing & Split/SFN Helper** | `fmx_ltu_tdma_split_sfn_helper.sh` | `--inspect-only` (`frame_len=2ms`, `duty_cycle=67%`, `bc_dl_symbols=2`, `SFN`) | `Stage 564A` / `572A` |
| **TDMA-Aligned TCP Pacing** | `tcp_pacing_ca_ratio` / `ss_ratio` | `110` / `160` + `netdev_budget_usecs=4000` | `Stage 571A` |
| **Super-4096 DPD & EVM Guard** | `fmx_ltu_super4096_dpd_evm_guard.sh` | `--inspect-only` (`<= -38 dB` EVM, `4 dB` PA backoff) | `Stage 558A` |
| **Burst CWND & Route Cache** | `tcp_slow_start_after_idle` / `no_metrics_save` | `0` (holds cwnd across bursts) / `1` | `Stage 557A` |
| **AD9361 Fastlock & Temp LUT** | `fmx_ltu_ad9361_fastlock_temp_helper.sh` | `--inspect-only` (`8` fastlock slots `0x25A..0x29F`) | `Stage 486A` / `538A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
