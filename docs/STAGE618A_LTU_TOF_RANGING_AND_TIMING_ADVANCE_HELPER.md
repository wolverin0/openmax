<!-- doc-head: STAGE618A_LTU_TOF_RANGING_AND_TIMING_ADVANCE_HELPER.md preserved document content -->
<!-- /doc-head -->


# Stage 618A — `AF-LTU` ToF Ranging & Timing Advance Drift Helper

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `proprietary airMAX/LTU module` (`ame_core.ko`) / `hardware` (`Beetle` `ame_asic0`) / `Linux`.
- **Stage 616A RE Grounding**: Operationalizes the `AF-LTU` Time-of-Flight ranging (`cpe_distance`), uplink Timing Advance (`TA`), and Cyclic Prefix (`3.2 us`) alignment thresholds into a 100% userspace read-only monitor (`firmware/ltu_safe_kit/fmx_ltu_tof_timing_advance_helper.sh`, `SHA-256`: `4757b7247a32b9f94e74e10e8128bd436d66a7ca162afc74f89eae07b15efe7e`).

## 2. Ranging & Timing Advance Thresholds
| Metric / Threshold | Value | Physical Interpretation |
| :--- | :---: | :--- |
| Baseband Ranging Step | `0.937 m` | `160 MHz` (`6.25 ns`) round-trip two-way ranging quantization |
| Cyclic Prefix Guard | `3.2 us` (`480 m`) | Maximum tolerated uplink arrival offset before inter-symbol / inter-CPE ISI |
| Thermal / Tower Sway Drift | `< 2.8 m` | Benign diurnal temperature or wind tower deflection |
| Multipath Lobe Jump Alert | `>= 7.5 m` | Direct LOS blocked; correlator locked onto secondary Fresnel reflection |

## 3. Safety Verification
- **Zero `/dev/ame*` Touches**: Operates in `--inspect-only` mode with zero character device opens.
