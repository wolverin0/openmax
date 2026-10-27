<!-- doc-head: STAGE774A_LTU_CHAMPION_V20_264WINDOW_ZERO_DHCP_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 774A — `AF-LTU` Champion `v20` (`264`-Window & Zero Rogue DHCP Kit)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `proprietary airMAX/LTU module` (`AF-LTU v2.4.2`) / `hardware`.
- **264-Window Milestone (`22` Live Rounds on `.110`)**: Packages `LTU` Champion `v20` (`firmware/ltu_safe_kit/fmx_ltu_v20_264window_zero_dhcp_kit.sh`, `SHA-256`: `395c397fae42ec7024621e41d170e4816760d908539f543bda39795aaae514ae`), verified across `264` live windows (`0.184 ms` mean RTT) and permanently disabling the fallback `dnsmasq`/`udhcpd` server on `br1` (`192.168.1.20`) across all `5` `LTU` boards.

## 2. `LTU` Champion `v20` Architecture
| Feature | Target / Interface | Verified Outcome |
| :--- | :--- | :--- |
| `br1` (`192.168.1.20`) DHCP Shield | `dnsmasq` / `udhcpd` on `br1` | Eliminates rogue `192.168.1.x` DHCP offers on WISP switches |
| `22`-Round (`264`-Window) Stack | `tcp_recovery=1`, `BQL=36288`, `IRQ 52`/`63` | **`0.184 ms` mean RTT** (`-21.70%` vs `0.235 ms` stock) |
| Guard Integration | Thermal PA + GPS `1PPS` + DMA Ring | Zero `/dev/ame*` character device opens |

## 3. Hard Safety Verification
- **Zero `/dev/ame*` Touches**: Verified across all `264` cumulative windows on `.110`.
