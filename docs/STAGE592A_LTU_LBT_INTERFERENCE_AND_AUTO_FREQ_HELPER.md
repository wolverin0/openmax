<!-- doc-head: STAGE592A_LTU_LBT_INTERFERENCE_AND_AUTO_FREQ_HELPER.md preserved document content -->
<!-- /doc-head -->


# Stage 592A — `AF-LTU` LBT Interference Mitigation & Auto-Frequency Helper

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko`) / `hardware` (`Beetle` `ame_asic0`) / `Linux`.
- **Stage 590A RE Grounding**: Operationalizes the Listen-Before-Talk (`ame_core_lbt_*`), interference mitigation, and spectral auto-frequency (`bbp_rf_set_freq`) symbol paths from `ame_core.ko` into a 100% userspace read-only helper (`firmware/ltu_safe_kit/fmx_ltu_lbt_auto_freq_helper.sh`, `SHA-256`: `354484dfe768cc1d497c6836065430d544087ef03814415ce9c4ba0b71fe7db8`).
- **Universal 5-Board Coverage**: `LTU-Lite` (`0xae08`), `LTU-LR` (`0xae07`), `LTU-Pro` (`0xae02`), `LTU-XR` (`0xae09`), and `LTU-Instant` (`0xae0b`).

## 2. LBT & Auto-Frequency Policy Parameters
| Parameter | Symbol / Hook | Threshold / Value | Operational Purpose |
| :--- | :--- | :---: | :--- |
| LBT Energy Detect | `ame_core_lbt_threshold_set` | `-75 dBm` | Prevents LBT deferral on weak `-85 dBm` adjacent-tower leakage |
| Auto-Freq EVM Trigger | `bbp_rf_set_freq` | `<= -31.0 dB` | Prevents false channel hops when `1024-QAM` (`10X`) remains stable |
| Hop Hysteresis | Userspace guard | `90 s` | Eliminates ping-pong channel oscillation under short interference bursts |

## 3. Hard Safety Verification
- **Zero `/dev/ame*` Touches**: Verified `--inspect-only` audit via `/proc/kallsyms` without opening `/dev/ame0`.
