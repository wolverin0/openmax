<!-- doc-head: Stage 763A OpenWrt Bridge Zero-Rogue-DHCP/RA & QCA988x ANI Immunity Guard (<200 lines) -->
`Stage 763A` construye `firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh` (y su alias `fmx_openwrt_lan_rogue_dhcp_guard.sh`) para deshabilitar permanentemente `dnsmasq` y `odhcpd` (`dhcp.lan.ignore='1'`, `dhcpv4/v6/ra='disabled'`) en toda radio OpenWrt en modo bridge WDS, integrando además la auditoría `ANI` (`Stage 753A`).
<!-- /doc-head -->

# Stage 763A — `OpenWrt` Bridge Zero-Rogue-DHCP/RA & `QCA988x` ANI Immunity Guard (`mm-797a`)

- **Status**: `CONFIRMED` (`memory-master`: `mm-797a`, `id=155478`)
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`
- **Deliverable**: [`firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh`](../firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh)
- **Alias**: [`firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_guard.sh`](../firmware/openwrt/common/fmx_openwrt_lan_rogue_dhcp_guard.sh)
- **SHA-256**: `748ad305d456699bdd052df190da42e677028738db1a816257e9ff542f9d6e43`
- **Artifact**: [`artifacts/autoresearch/stage763a_openwrt_lan_rogue_dhcp_and_ani_guard.json`](../artifacts/autoresearch/stage763a_openwrt_lan_rogue_dhcp_and_ani_guard.json)

## 1. Protección Crítica LAN `Zero-Rogue-DHCP/RA` y `QCA988x ANI` (`CONFIRMED`)
| Parámetro / Servicio (`OpenWrt` / `ath10k`) | Valor Forzado | Mecanismo First-Principles (`CONFIRMED`) |
| :--- | :---: | :--- |
| `dhcp.lan.ignore` + `dhcpv4/v6/ra` | `'1'` + `'disabled'` | Impide que una radio OpenWrt en puente `br-lan` responda `DHCPDISCOVER` o anuncios `ICMPv6 RA` en la LAN (`Linux`). |
| `/etc/init.d/dnsmasq` & `odhcpd` | `stop` + `disable` | Detiene los demonios DHCP/RA inmediatamente en primer arranque y elimina sus symlinks de `/etc/rc.d/` (`Linux`). |
| `WMI_PDEV_PARAM_ANI_ENABLE` (`ani_enable`) | `1` (Habilitado) | Mantiene activa la inmunidad adaptativa contra ruido (`ANI` OFDM/CCK Immunity Levels) en `QCA988x` (`QCA firmware`). |

## 2. Hard Safety Gate (`CONFIRMED`)
- **Zero touches en `.241`, `.242`, `.20`, `.250` y `/dev/ame*`**: `True`.
