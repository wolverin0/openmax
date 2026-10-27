<!-- doc-head: Stage 468A QCA988x Hitless Background FFT Spectral Scan & Noise Floor Calibration Helper (<220 lines) -->
`Stage 468A` integra los hallazgos RE de `Stage 451A` (`WMI 0x905b/0x905c` Spectral Scan + calibración de piso de ruido `NF` en `QCA988x`) en `firmware/openwrt/common/fmx_qca988x_spectral_nf_helper.sh` para escaneo espectral FFT de `64` bines sin caída de enlace.
<!-- /doc-head -->

# Stage 468A — `QCA988x` Hitless Background FFT Spectral Scan & Noise Floor Calibration Helper (`mm-f9fe`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-f9fe`, `id=155427`)
- **Attribution**: `ath10k`, `QCA firmware`, `mac80211`
- **Helper Script**: [`firmware/openwrt/common/fmx_qca988x_spectral_nf_helper.sh`](../firmware/openwrt/common/fmx_qca988x_spectral_nf_helper.sh)
- **SHA-256**: `4a739ee4212d754e2effae8f10554dde57e47db89989e50dc4fb87a977120514`
- **Artifact**: [`artifacts/autoresearch/stage468a_xtensa_spectral_scan_and_nf_cal_helper.json`](../artifacts/autoresearch/stage468a_xtensa_spectral_scan_and_nf_cal_helper.json)

## 1. Arquitectura de Escaneo Espectral FFT Hitless (`WMI 0x905b / 0x905c`)
| Parámetro | Valor Configurado | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| **`WMI_PDEV_SPECTRAL_SCAN_CONFIGURE_CMDID`** | `0x905b` | Configura el motor FFT del baseband `QCA988x` sin cambiar de canal (`QCA firmware`). |
| **`WMI_PDEV_SPECTRAL_SCAN_ENABLE_CMDID`** | `0x905c` | Activa captura en modo `background` durante símbolos RX idle (`ath10k`). |
| **`spectral_bins` / `spectral_count`** | `64` / `64` | Captura una ráfaga acotada de `64` muestras FFT de `64` subportadoras y se auto-desactiva en `1s` (`ath10k`). |
| **Survey Noise Floor (`NF`)** | `iw dev wlan0 survey dump` | Correlaciona piso de ruido por cadena con el vector FFT para alimentar el clasificador de Pilar 5 (`mac80211`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: No altera registros ni inicia ráfagas salvo invocación explícita `--trigger-background-fft`.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
