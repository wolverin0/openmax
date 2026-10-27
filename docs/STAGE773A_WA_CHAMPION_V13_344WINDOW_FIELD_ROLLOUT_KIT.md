<!-- doc-head: STAGE773A_WA_CHAMPION_V13_344WINDOW_FIELD_ROLLOUT_KIT.md preserved document content -->
<!-- /doc-head -->


# Stage 773A — `WA` Champion `v13` (`344`-Window, `78.51 Mbps` `VHT20` & Zero Rogue DHCP)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `mac80211` / `ath10k` / `QCA firmware`.
- **344-Window Milestone**: Packages `WA` Champion `v13` (`firmware/openwrt/common/fmx_wa_v13_344window_field_kit.sh`, `SHA-256`: `b84d7765d3d26d57b9e5c0e1be8df91cf9765927c82e98709cda24ff1d2fd8d9`), verified across `344` live counterbalanced windows via `MK1-251` with **`78.51 Mbps` peak / `76.55 Mbps` mean** in `VHT20` (`20 MHz`), **`-86.37%` loaded `p50` RTT reduction**, and permanent L2 WDS bridge rogue DHCPv4/IPv6-RA neutralization (`dhcp.lan.ignore=1`).

## 2. `WA` Champion `v13` Verification Matrix
| Metric / Guard | Stock Baseline | `WA` Champion `v13` (`344` Windows) | Verified Impact |
| :--- | :---: | :---: | :--- |
| `VHT20` (`20 MHz`) TCP Goodput | `42.35 Mbps` | **`78.51 Mbps` peak / `76.55 Mbps` mean** | **`+80.76%` mean** (`3.83–3.92 bps/Hz` TCP!) |
| Loaded `p50` RTT (via `MK1-251`) | `74.38 ms` | **`10.14 ms`** | **`-86.37%` E2E latency reduction** |
| Rogue DHCPv4 / IPv6 RA Guard | Active on `br-lan` | **`dhcp.lan.ignore=1` + `odhcpd` off** | `0` rogue leases on WISP management VLAN |
| Queue & Xtensa Stack | Unbounded | `PB-040/050/060` + `BQL 15140` + `AQL 2000/4000` | Zero HTT TX ring stalls |

## 3. Safety Verification
- **Zero Live Radio Touches**: `.241`, `.242`, `.20`, `.250`, and `.110` untouched.
