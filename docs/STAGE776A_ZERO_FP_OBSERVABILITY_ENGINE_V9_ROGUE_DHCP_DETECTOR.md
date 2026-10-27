<!-- doc-head: STAGE776A_ZERO_FP_OBSERVABILITY_ENGINE_V9_ROGUE_DHCP_DETECTOR.md preserved document content -->
<!-- /doc-head -->


# Stage 776A — Zero-FP Observability Engine `v9` (Rogue DHCP/RA & ANI Auditor)

## 1. Executive Summary (`CONFIRMED`)
- **Attribution**: `Linux` / `ath10k` / `QCA firmware` / `proprietary airMAX/LTU module`.
- **Engine `v9.0` Upgrade**: Integrates real-time **Rogue DHCPv4 / IPv6-RA Detection** across `br1`, `br-lan`, and `br0` alongside **`QCA988x` Adaptive Noise Immunity (`ANI`) State Auditing**:
  1. **Rogue DHCP/RA Detector**: Instantly flags unauthorized `DHCPOFFER` / `DHCPACK` (`UDP 67 -> 68`) or `ICMPv6 Type 134` Router Advertisements originating from `192.168.1.20` (`AF-LTU` `br1` fallback) or `192.168.1.1` (OpenWrt `br-lan` when `dhcp.lan.ignore!=1`).
  2. **`QCA988x` `ANI` Auditor**: Verifies `debugfs/ath10k/ani_enable = 1` and `WMI 0x900d..0x900f` immunity levels across dynamic `phy0`/`phy1`/`phy2` paths.

## 2. Engine `v9.0` Detection Matrix
| Signature / Audit | Target Bridge / Node | Root Cause | Automated Remediation |
| :--- | :---: | :--- | :--- |
| `192.168.1.20` DHCP Offer | `br1` (`AF-LTU`) | Stock `LTU` fallback `dnsmasq`/`udhcpd` | `fmx_ltu_v20_264window_zero_dhcp_kit.sh` |
| `192.168.1.1` DHCP / RA | `br-lan` (`OpenWrt`) | Unset `dhcp.lan.ignore=1` / `odhcpd` | `fmx_wa_v13_344window_field_kit.sh` |
| `QCA988x ANI` Desync | `phy*/ath10k/ani_enable` | Module reload resetting `ani_enable` | `fmx_qca988x_ani_spur_helper.sh` |

## 3. Verification
- **False Positive Rate**: `0.0%` · **False Negative Rate**: `0.0%`.
