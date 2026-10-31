<!-- doc-head: Stage 560A Consolidated 15-Round (180-Window) Universal LTU 5-Board Safe Linux Champion v13 (<220 lines) -->
`Stage 560A` consolida las `15` campañas (`45` rondas `A1->B1->A2->B2` = **`180` ventanas reales** en `198.18.0.63`) y el guard `fmx_ltu_super4096_dpd_evm_guard.sh` (`Stage 558A`) en `rc.poststart_ltu_safe_champion.sh` (`v13`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 560A — Consolidated 15-Round (`180`-Window Milestone!) Universal LTU 5-Board Safe Linux Champion `v13` (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `Linux`, `hardware`, `proprietary airMAX/LTU module`
- **Deliverable**: [`firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh`](../firmware/ltu_safe_kit/rc.poststart_ltu_safe_champion.sh) (`v13`)
- **Manifest**: [`firmware/ltu_safe_kit/ltu_5board_universal_manifest_v13.json`](../firmware/ltu_safe_kit/ltu_5board_universal_manifest_v13.json)
- **SHA-256**: `1e5c592c5b8e3be4d7f0d9139028062f5db53396d35a52c5434da8dde17a5319`
- **Live Evidence Base**: **`15` campaigns (`45` counterbalanced `A1->B1->A2->B2` rounds = `180` live measurement windows)** on `198.18.0.63` (`Boca 5`).

## 1. Consolidated `v13` 15-Round Knob Stack + `Stage 558A` Super-4096 DPD Guard (`CONFIRMED`)
| Subsystem | Parameter / Sysfs | Champion `v13` Value | Stage Proven |
| :--- | :--- | :--- | :--- |
| **Super-4096 DPD & EVM Guard** | `fmx_ltu_super4096_dpd_evm_guard.sh` | `--inspect-only` (`<= -38 dB` EVM, `4 dB` PA backoff) | `Stage 558A` |
| **Burst CWND & Route Cache** | `tcp_slow_start_after_idle` / `no_metrics_save` | `0` (holds cwnd across bursts) / `1` | `Stage 557A` |
| **AD9361 Fastlock & Temp LUT** | `fmx_ltu_ad9361_fastlock_temp_helper.sh` | `--inspect-only` (`8` fastlock slots `0x25A..0x29F`) | `Stage 486A` / `538A` |
| **PMTU & F-RTO Recovery** | `tcp_mtu_probing` / `tcp_frto` | `1` (Blackhole-only) / `2` (SACK F-RTO) | `Stage 537A` |
| **DCXO GPS vs TCXO Monitor** | `fmx_ltu_dcxo_gps_tcxo_monitor.sh` | `--inspect-only` (`<=0.25 ppm` `12x` CFO guard) | `Stage 486A` / `502A` |
| **RPS Reordering Resilience** | `net.ipv4.tcp_reordering` | `6` (prevents Dual-Core RPS false DupACKs) | `Stage 501A` |
| **Beetle DMA Ring & IRQ 52** | `irq/52/smp_affinity` + `net.core.busy_read` | `2` (`CPU1`) + `busy_read=0` (`busy_poll=0`) | `Stage 185A` / `460A` / `467A` |
| **QCA8337N / GMAC0 BQL** | `byte_queue_limits/limit_max` & `tx_queue_len` | `36288` (`24` MTUs) / `256` | `Stage 185A` / `188A` |

## 2. Hard Safety Verification (`CONFIRMED`)
- **Zero `/dev/ame*` character device touches**: `zero_dev_ame_touches = true`.
- **Strict Unix LF (`\n`) line endings**: `lf_line_endings_only = true`.
