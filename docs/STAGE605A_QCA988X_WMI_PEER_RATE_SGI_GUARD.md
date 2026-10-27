<!-- doc-head: Stage 605A QCA988x WMI_PEER_ASSOC_CMDID peer_vht_rates, SGI Mask & Retry-Schedule Helper (<220 lines) -->
`Stage 605A` construye `firmware/openwrt/common/fmx_qca988x_wmi_peer_rate_sgi_guard.sh` operacionalizando el RE `Stage 589A` sobre `WA/XC:umac.ko` (`WMI_PEER_ASSOC_CMDID`, `WMI_PEER_RATE_RETRY_SCHED_CMDID`, `_RATE_SetSGIMasks`, `g_default_sgi_per_thresh`, `ieee80211_setup_vht_rates`) y el hallazgo empírico `Stage 487A` (`wifi down; sleep 2; wifi up`).
<!-- /doc-head -->

# Stage 605A — `QCA988x` `WMI_PEER_ASSOC_CMDID` `peer_vht_rates`, `SGI` Mask & Retry Helper (`mm-636f`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-636f`, `id=155453`)
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `proprietary airMAX/LTU module`, `Linux`
- **Deliverable**: [`firmware/openwrt/common/fmx_qca988x_wmi_peer_rate_sgi_guard.sh`](../firmware/openwrt/common/fmx_qca988x_wmi_peer_rate_sgi_guard.sh)
- **SHA-256**: `f304e9831aea534fb054e9accb260638c3f84b482e47401ccdba3ecaaddea060`
- **Artifact**: [`artifacts/autoresearch/stage605a_qca988x_wmi_peer_rate_sgi_guard.json`](../artifacts/autoresearch/stage605a_qca988x_wmi_peer_rate_sgi_guard.json)

## 1. Descriptores `WMI_PEER_ASSOC_CMDID` y Máscara `SGI` en `umac.ko` (`Stage 589A` RE) (`CONFIRMED`)
| Subsistema (`WA/XC:umac.ko`) | Símbolos Clave Descubiertos (`Stage 589A`) | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :--- | :--- |
| **Construcción UMAC de `PEER_ASSOC`** | `WMI_PEER_ASSOC_CMDID`, `rate_init_peer_ratectxt`, `ieee80211_setup_vht_rates`, `ol_ath_vht_rate_setup` | El vocabulario de tasas por peer reside `100%` en `umac.ko` (`95` tokens vs `0` en `ath_dev.ko`/`ubnt_poll_host.ko`) y popula `phymode`, `vht_mcs_set` y `ht_mcs_set` (`QCA firmware`). |
| **Máscara `SGI` por Tasa (`0..9`)** | `_RATE_SetSGIMasks`, `_RATE_GetSGIFlag`, `g_default_sgi_per_thresh` | `Short GI` (`400 ns`) no es un bit global sino una máscara por índice `MCS 0..9` gobernada por umbral de `PER` (`g_default_sgi_per_thresh`) (`QCA firmware`). |
| **Re-asociación Limpia (`Stage 487A`)** | `ieee80211_update_ht_vht_phymode` + `wifi down; sleep 2; wifi up` | Explica desde primeros principios por qué un cambio de ancho de canal en caliente deja `peer_phymode` obsoleto en RAM del `QCA988x` hasta re-emitir `WMI_PEER_ASSOC_CMDID` (`ath10k`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Modo por defecto `--status` (`read-only`)**: Inspecciona `phymode`, ancho de canal y `vht_mcs` sin cortar el enlace.
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
