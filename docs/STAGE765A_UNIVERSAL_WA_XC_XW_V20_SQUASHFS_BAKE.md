<!-- doc-head: Stage 765A Universal WA/XC/XW v20 SquashFS (180 hsqs Images with Zero-Rogue-DHCP Guarantee) Bake (<200 lines) -->
`Stage 765A` empaqueta las `180` imágenes universales `WA/XC/XW v20` SquashFS (`hsqs`) integrando la garantía `Zero-Rogue-DHCP/RA` (`dhcp.lan.ignore='1'`, `dnsmasq`/`odhcpd` detenidos y deshabilitados) y `Stage 763A` (`fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh`).
<!-- /doc-head -->

# Stage 765A — Universal `WA/XC/XW v20` SquashFS (`180` `hsqs` Images with Zero-Rogue-DHCP Guarantee) Bake (`mm-0898`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-0898`, `id=155480`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `hardware`
- **Total Verified SquashFS (`hsqs`) Images**: **`180`** (`all_images_have_hsqs_superblock = true`, `zero_rogue_dhcp_guarantee = true`).
- **UCI Champion Script (`v20`)**: [`99-fmx-wa-universal-champion-v20`](../firmware/openwrt/common/99-fmx-wa-universal-champion-v20) (`sha256: 66bb96b18f8f5f0435b6142437d1045a64decd1feb901e5ec649d7d94b66d6d4`).

## 1. Integrated Ground-Up `v20` Stack Across `WA`, `XC`, & `XW` (`CONFIRMED`)
| Component | Path / Artifact | First-Principles Role |
| :--- | :--- | :--- |
| **`Stage 763A` `Zero-Rogue-DHCP/RA` & `ANI` Guard** | `firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh` | Fuerza `dhcp.lan.ignore='1'`, `dhcpv4/v6/ra='disabled'`, detiene/deshabilita `dnsmasq` y `odhcpd` en `br-lan` y audita `ANI` (`ani_enable=1`). |
| **`Stage 731A` Spectral & Radar `PHYERR` Guard** | `firmware/openwrt/common/fmx_qca_spectral_radar_phyerr_guard.sh` | Silencia `ATH10K_PHYERR_SPECTRAL` (`spectral_scan_ctl=disable`) durante tráfico activo mientras preserva `ATH10K_PHYERR_RADAR`. |
| **`Stage 709A` `WMI_VDEV_START` & Dynamic `phy*` Guard** | `firmware/openwrt/common/fmx_qca_wmi_vdev_start_guard.sh` | Resuelve dinámicamente `phy0`/`phy1`/`phy2` y audita `WMI_SERVICE_READY_EVENTID` + `WMI_VDEV_START_REQUEST_CMDID`. |

## 2. Hard Safety Audit (`CONFIRMED`)
- **Zero touches on `.241`, `.242`, `.20`, `.250` and `/dev/ame*`**: `True`.
