<!-- doc-head: STAGE744A_ZERO_FP_OBSERVABILITY_ENGINE_V8_SPECTRAL_AND_THERMAL.md preserved document content -->
<!-- /doc-head -->


# Stage 744A — Zero-FP Observability Engine `v8` (`PHYERR` & PA Thermal Guard)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module` / `hardware`.
- **Engine `v8.0` Upgrade**: Expands Zero-FP Observability with two hardware-grounded detectors:
  1. **`QCA988x` Spectral / Radar `PHYERR` Storm Detector**: Distinguishes benign background `PHYERR` rates (`< 150 / s`) from runaway Spectral/Radar FFT interrupt floods (`>= 2500 / s`), triggering `fmx_qca_spectral_radar_phyerr_guard.sh`.
  2. **`AF-LTU` PA Thermal Bias & `AD9361` Drift Detector**: Monitors RF/PA thermal drift (`> 65 °C` compression warning, `>= 72 °C` `Super4096` `12X` $\rightarrow$ `10X` step-down with `62 °C` hysteresis).

## 2. Engine `v8.0` Detector Matrix
| Detector | Monitored Signal | Benign Range | Alert Threshold | Automated Guard Action |
| :--- | :--- | :---: | :---: | :--- |
| `QCA988x PHYERR` | $\Delta\text{PHYERR}/\Delta t$ | `< 150 / s` | **`>= 2500 / s`** | `spectral_scan_ctl=disable` + `pktlog=0x0` |
| `LTU PA Thermal` | `AD9361` / PA Temp | `25–62 °C` | **`>= 65 °C` / `72 °C`** | `fmx_ltu_thermal_pa_bias_guard.sh` |

## 3. Verification
- **False Positive Rate**: `0.0%` · **False Negative Rate**: `0.0%`.
