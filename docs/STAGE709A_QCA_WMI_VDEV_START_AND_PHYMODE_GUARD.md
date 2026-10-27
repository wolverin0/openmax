<!-- doc-head: Stage 709A QCA988x WMI_SERVICE_READY & WMI_VDEV_START Resource & Phymode Guard (<200 lines) -->
`Stage 709A` construye `firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh` operacionalizando la auditoría de `WMI_SERVICE_READY_EVENTID` y `WMI_VDEV_START_REQUEST_CMDID` (`Stage 693A`) junto con la resolución dinámica `phy*` (`phy0`/`phy1`/`phy2`).
<!-- /doc-head -->

# Stage 709A — `QCA988x` `WMI_SERVICE_READY` & `WMI_VDEV_START` Resource & Phymode Guard (`mm-7013`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-7013`, `id=155468`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `Linux`, `hardware`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh`](../firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh)
- **SHA-256**: `cb631efb22548b1799ee8a09964bfc97a359f6220c8ac5010846b2b4a2d0a484`
- **Artifact**: [`artifacts/autoresearch/stage709a_qca_wmi_vdev_start_and_phymode_guard.json`](../artifacts/autoresearch/stage709a_qca_wmi_vdev_start_and_phymode_guard.json)

## 1. Presupuesto IRAM `WMI_SERVICE_READY` y Resolución Dinámica `phy*` (`CONFIRMED`)
| Primitiva / Parámetro (`ath10k` / `QCA988x`) | Valor / Invariante | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `resolve_qca988x_phy` | `phy0` / `phy1` / `phy2` | Detecta dinámicamente el índice `ieee80211/phy*/ath10k` para que placas `XC` con radio de gestión `2.4 GHz` (`phy0`) apliquen el tuning sobre `QCA988x` (`phy1`) (`ath10k`). |
| `WMI_SERVICE_READY_EVENTID` | `max_peers=32`, `max_vdevs=4` | Preserva el pool de IRAM del procesador Xtensa evitando agotamiento al iniciar el VDEV (`QCA firmware`). |
| `WMI_VDEV_START_REQUEST_CMDID` | `pktlog_filter=0x0`, `htt="2 64"` | Garantiza que al arrancar el VDEV en `VHT20/40/80` no se active el drenaje DMA de `pktlog` (`ath10k`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Audita el `phy*` resuelto y el estado `WMI` sin alterar el enlace.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
