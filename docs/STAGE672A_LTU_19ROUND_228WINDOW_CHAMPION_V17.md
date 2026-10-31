<!-- doc-head: Stage 672A Consolidated 19-Round (228-Window Milestone!) Universal LTU 5-Board Champion v17 (<200 lines) -->
`Stage 672A` consolida las `19` campañas (`57` rondas `A1->B1->A2->B2` = **`228` ventanas reales** en `198.18.0.63`) y el guard `fmx_ltu_gps_1pps_sync_guard.sh` (`Stage 670A`) en `rc.poststart_ltu_safe_champion.sh` (`v17`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 672A — Consolidated 19-Round (`228`-Window Milestone!) Universal LTU 5-Board Champion `v17` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v17`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v17.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v17.json)
- **SHA-256**: `4da705ce5fbc8443c2b680d98697b4c16dd849bcfb33705682e6dd5a3425e65d`
- **Live Evidence Base**: **`19` campaigns (`57` counterbalanced `A1->B1->A2->B2` rounds = `228` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v17` 19-Round Stack + `Stage 670A` GPS 1PPS Guard (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v17` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **GPS 1PPS & Holdover Guard** | `fmx_ltu_gps_1pps_sync_guard.sh` | `--inspect-only` (`frame_pulse_offset`, `SFN_synchronized`, `holdover=10.7s`) | `Stage 670A` |
| **SoftIRQ Time Budget & TSQ** | `netdev_budget_usecs` / `tcp_limit_output_bytes` | `4000 us` / `131072` (`65536` CPE) | `Stage 669A` |
| **ToF Ranging, TA & CP Guard** | `fmx_ltu_tof_ta_cp_guard.sh` | `--inspect-only` (`distance_meter`, `update_ta`, `early_data_cfg`, `cpsample`) | `Stage 616A` / `636A` |
| **UDP Burst & Ancillary Reserves** | `udp_rmem_min` / `wmem_min` / `optmem_max` | `16384` / `16384` / `65536` | `Stage 635A` |
| **204-Window LBT & Spectral Guard** | `fmx_ltu_200w_golden_guard.sh` | `--inspect-only` (`lbt_enable`, `lbt_detects`, `auto_freq_mode`, `interf_avg`) | `Stage 590A` / `604A` |
| **TCP RACK-TLP Loss Recovery** | `net.ipv4.tcp_recovery` + `early_retrans` | `1` (`RACK`) + `3` (`TLP`) + `tcp_reordering=6` | `Stage 603A` |
| **Super-4096 DPD & EVM Guard** | `fmx_ltu_super4096_dpd_evm_guard.sh` | `--inspect-only` (`<= -38 dB` EVM, `4 dB` PA backoff) | `Stage 558A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
