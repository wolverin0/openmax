<!-- doc-head: Stage 710A Consolidated 20-Round (240-Window Milestone!) Universal LTU 5-Board Champion v18 (<200 lines) -->
`Stage 710A` consolida las `20` campañas (`60` rondas `A1->B1->A2->B2` = **`240` ventanas reales** en `198.18.0.63`) y el guard `fmx_ltu_dma_ring_backpressure_guard.sh` (`Stage 708A`) en `rc.poststart_ltu_safe_champion.sh` (`v18`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 710A — Consolidated 20-Round (`240`-Window Milestone!) Universal LTU 5-Board Champion `v18` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v18`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v18.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v18.json)
- **SHA-256**: `e6433977ddca3a34cf7156a12a723b5f5a4a9394ce216fd038399445f9117435`
- **Live Evidence Base**: **`20` campaigns (`60` counterbalanced `A1->B1->A2->B2` rounds = `240` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v18` 20-Round Stack + `Stage 708A` DMA Ring Guard (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v18` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **Zero-Copy DMA Ring Guard** | `fmx_ltu_dma_ring_backpressure_guard.sh` | `--inspect-only` (`eab_driver.ko` + `ame_core.ko`, `BQL=36288`, `busy_read=0`) | `Stage 694A` / `708A` |
| **Thin Streams & RPS Backlog** | `tcp_thin_linear_timeouts` / `netdev_max_backlog` | `1` (`early_retrans=3`) / `2048..3000` | `Stage 707A` |
| **GPS 1PPS & Holdover Guard** | `fmx_ltu_gps_1pps_sync_guard.sh` | `--inspect-only` (`frame_pulse_offset`, `SFN_synchronized`, `holdover=10.7s`) | `Stage 670A` |
| **SoftIRQ Time Budget & TSQ** | `netdev_budget_usecs` / `tcp_limit_output_bytes` | `4000 us` / `131072` (`65536` CPE) | `Stage 669A` |
| **ToF Ranging, TA & CP Guard** | `fmx_ltu_tof_ta_cp_guard.sh` | `--inspect-only` (`distance_meter`, `update_ta`, `early_data_cfg`, `cpsample`) | `Stage 616A` / `636A` |
| **204-Window LBT & Spectral Guard** | `fmx_ltu_200w_golden_guard.sh` | `--inspect-only` (`lbt_enable`, `lbt_detects`, `auto_freq_mode`, `interf_avg`) | `Stage 590A` / `604A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
