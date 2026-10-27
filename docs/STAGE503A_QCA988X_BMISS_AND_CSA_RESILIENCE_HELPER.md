<!-- doc-head: Stage 503A QCA988x BMISS & CSA Channel-Switch Resilience Helper (<220 lines) -->
`Stage 503A` integra los hallazgos RE de `Stage 485A` (`WMI_VDEV_PARAM_BMISS_COUNT_MAX`, `ROAM_EVENTS` y máquina de estados `CSA` Channel Switch Announcement) en `firmware/openwrt/common/fmx_qca988x_bmiss_csa_helper.sh` para evitar desasociaciones espurias bajo ráfagas de interferencia o cambios `DFS`/`AirSelect`.
<!-- /doc-head -->

# Stage 503A — `QCA988x` `BMISS` & `CSA` Channel-Switch Resilience Helper (`mm-5f83`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-5f83`, `id=155433`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca988x_bmiss_csa_helper.sh`](../firmware/openwrt/common/fmx_qca988x_bmiss_csa_helper.sh)
- **SHA-256**: `fab4746a2af30bb64ecfd1f3fc1a2fda1858f2ebb0d9439b2449796f452ef517`
- **Artifact**: [`artifacts/autoresearch/stage503a_qca988x_bmiss_and_csa_resilience_helper.json`](../artifacts/autoresearch/stage503a_qca988x_bmiss_and_csa_resilience_helper.json)

## 1. Parámetros de Resiliencia `BMISS` y `CSA` (`Stage 485A` $ightarrow$ `Stage 503A`) (`CONFIRMED`)
| Parámetro / Estado | Valor Stock | Valor `Stage 503A` | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :---: | :--- |
| **`WMI_VDEV_PARAM_BMISS_COUNT_MAX`** | `10` beacons (`~1.0 s`) | `30` beacons (`~3.0 s`) | Impide que una ráfaga de ruido co-canal de `1..2 s` dispare `BMISS` y desasocie un CPE fijo WDS (`QCA firmware`). |
| **`ROAM_EVENTS` en WDS Fijo** | Activo | Suprimido en WDS fijo | Evita escaneos fuera de canal (`off-channel scan`) innecesarios en enlaces fijos direccionales (`ath10k`). |
| **`CSA` Beacon Switch Count** | `5` | `10` | Asegura que todos los CPEs del sector reciban el IE `Channel Switch Announcement` antes de saltar por `DFS` (`mac80211`). |
| **`max_inactivity`** | `300 s` | `600 s` | Mantiene entradas de estación activas con `skip_inactivity_poll=0` (`Null Data` keepalive) (`mac80211`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Inspecciona tiempos de actividad/inactividad sin reiniciar interfaces.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
