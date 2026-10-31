<!-- doc-head: Stage 638A Consolidated 18-Round (216-Window Milestone!) Universal LTU 5-Board Champion v16 (<220 lines) -->
`Stage 638A` consolida las `18` campañas (`54` rondas `A1->B1->A2->B2` = **`216` ventanas reales** en `198.18.0.63`) y el guard `fmx_ltu_tof_ta_cp_guard.sh` (`Stage 636A`) en `rc.poststart_ltu_safe_champion.sh` (`v16`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 638A — Consolidated 18-Round (`216`-Window Milestone!) Universal LTU 5-Board Champion `v16` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v16`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v16.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v16.json)
- **SHA-256**: `c634fc78115fcfe6bfdf5529457015054387d2706375063c5ed91e076bc8cf44`
- **Live Evidence Base**: **`18` campaigns (`54` counterbalanced `A1->B1->A2->B2` rounds = `216` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v16` 18-Round Stack + `Stage 636A` ToF/TA/CP Guard (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v16` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **ToF Ranging, TA & CP Guard** | `fmx_ltu_tof_ta_cp_guard.sh` | `--inspect-only` (`distance_meter`, `update_ta`, `early_data_cfg`, `cpsample`) | `Stage 616A` / `636A` |
| **UDP Burst & Ancillary Reserves** | `udp_rmem_min` / `wmem_min` / `optmem_max` | `16384` / `16384` / `65536` | `Stage 635A` |
| **204-Window LBT & Spectral Guard** | `fmx_ltu_200w_golden_guard.sh` | `--inspect-only` (`lbt_enable`, `lbt_detects`, `auto_freq_mode`, `interf_avg`) | `Stage 590A` / `604A` |
| **TCP RACK-TLP Loss Recovery** | `net.ipv4.tcp_recovery` + `early_retrans` | `1` (`RACK`) + `3` (`TLP`) + `tcp_reordering=6` | `Stage 603A` |
| **TDMA Framing & Split/SFN Helper** | `fmx_ltu_tdma_split_sfn_helper.sh` | `--inspect-only` (`frame_len=2ms`, `duty_cycle=67%`, `bc_dl_symbols=2`, `SFN`) | `Stage 564A` / `572A` |
| **Super-4096 DPD & EVM Guard** | `fmx_ltu_super4096_dpd_evm_guard.sh` | `--inspect-only` (`<= -38 dB` EVM, `4 dB` PA backoff) | `Stage 558A` |
| **AD9361 Fastlock & Temp LUT** | `fmx_ltu_ad9361_fastlock_temp_helper.sh` | `--inspect-only` (`8` fastlock slots `0x25A..0x29F`) | `Stage 486A` / `538A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
