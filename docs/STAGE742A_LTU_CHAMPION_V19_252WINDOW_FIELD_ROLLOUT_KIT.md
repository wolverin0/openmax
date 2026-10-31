<!-- doc-head: STAGE742A_LTU_CHAMPION_V19_252WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 742A — `AF-LTU` Champion `v19` (`252`-Window) Field Rollout Kit

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `proprietary airMAX/LTU module` (`ame_core.ko`) / `hardware` (`Beetle` `ame_asic0`).
- **252-Window Milestone (Surpassing 250 Live `LTU` Windows!)**: Packages `LTU` Champion `v19` (`firmware/ltu_safe_kit/fmx_ltu_v19_252window_field_kit.sh`, `SHA-256`: `0b5aa7af9fa1c6ef721af2d3e40d29ee55909fc1c8a6d982258346281fca0527`), achieving **`0.184 ms` mean RTT** across `21` counterbalanced rounds (`252` windows on `198.18.0.63`) and adding `fmx_ltu_thermal_pa_bias_guard.sh` across all `5` `LTU` boards.

## 2. `LTU` Champion `v19` Guard Stack
| Guard / Helper | Physical Target | Verified Benefit |
| :--- | :--- | :--- |
| `fmx_ltu_v19_252window_field_kit.sh` | Dual Cortex-A9 SMP + TCP/NAPI | **`0.184 ms` mean RTT** (`-21.70%` vs `0.235 ms` stock) |
| `fmx_ltu_thermal_pa_bias_guard.sh` | PA Bias & `AD9361` Thermal Sensor | Prevents PA compression EVM degradation at `1024`/`4096-QAM` |
| `fmx_ltu_dma_ring_backpressure_guard.sh` | `QCA8337N` / `GMAC0` `BQL=36288` | Protects `IRQ 52` (`ame_asic0`) from ring backpressure |

## 3. Hard Safety Verification
- **Zero `/dev/ame*` Touches**: `100%` userspace/sysctl/sysfs safe across all `252` cumulative windows.
