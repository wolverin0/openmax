<!-- doc-head: Stage 731A QCA988x Spectral Scan FFT & DFS Radar PHYERR Storms Guard (<200 lines) -->
`Stage 731A` construye `firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh` operacionalizando la ingeniería inversa de `Stage 727A` (`ATH10K_PHYERR_SPECTRAL`, `ATH10K_PHYERR_RADAR`, `WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID`) para evitar tormentas de interrupciones `PHYERR` durante tráfico de datos activo.
<!-- /doc-head -->

# Stage 731A — `QCA988x` Spectral Scan FFT & DFS Radar `PHYERR` Storms Guard (`mm-6eff`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-6eff`, `id=155473`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh`](../firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh)
- **SHA-256**: `d7e48f2a962865847be712b888ed66c18349caf29b10dab0b1df2319c5b3c096`
- **Artifact**: [`artifacts/autoresearch/stage731a_qca_spectral_radar_phyerr_guard.json`](../artifacts/autoresearch/stage731a_qca_spectral_radar_phyerr_guard.json)

## 1. Mitigación de Tormentas `ATH10K_PHYERR_SPECTRAL` vs `ATH10K_PHYERR_RADAR` (`CONFIRMED`)
| Primitiva / Parámetro (`ath10k` / `QCA988x`) | Valor Configurado | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` | `spectral_scan_ctl = disable` | Desactiva el muestreo FFT continuo durante tráfico activo para que `ATH10K_PHYERR_SPECTRAL` no sature el Copy Engine PCIe (`QCA firmware`). |
| `ATH10K_PHYERR_RADAR` | Activo (DFS Pulse Detector) | Preserva la detección hardware de pulsos de radar ETSI/FCC sin sobrecarga de bins FFT (`ath10k`). |
| `pktlog_filter` | `0x0` | Elimina la copia DMA por paquete de diagnóstico en `phy0`/`phy1`/`phy2` (`ath10k`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Audita `spectral_scan_ctl` y `pktlog_filter` sin alterar el enlace.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
