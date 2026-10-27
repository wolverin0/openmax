<!-- doc-head: STAGE781A_CROSS_FLEET_CHAMPION_V58_BUNDLE.md preserved document content -->
<!-- /doc-head -->



# Stage 781A: Cross-Fleet Champion `v58.0` Bundle & Zero-Rogue-DHCP Guarantee

## 1. Objective & Classification
- **Claim Classification**: `CONFIRMED`
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Scope**: Packages **Cross-Fleet Champion `v58.0`** across all 8 radio families (`WA`, `XC`, `2XC`, `XW`, `XM`, `TI`, `AirGrid/Loco M5`, `AF-LTU`), backed by `872` cumulative counterbalanced `A1 -> B1 -> A2 -> B2` windows (`344 WA` + `264 Multi-Radio` + `264 LTU`) and a **100% Zero-Rogue-DHCP Guarantee**.

## 2. Sub-Champion Unification (`v58.0`)
| Sub-Champion | Version | Windows | Key Primitives & Verified Performance |
| :--- | :---: | :---: | :--- |
| **WA OpenWrt WDS** | `v13.0` | `344` | `78.51 Mbps` peak VHT20 (`66.01 Mbps` E2E `.251`), `AP/STA fq_quantum=4542/3028`, `bql_max=24192`, `nf_cal_period=120s` |
| **Multi-Radio (`XC/2XC/XW/XM`)** | `v58.0` | `264` | `98.0 Mbps` (`XC .198`), `97.6 Mbps` (`2XC .253`), `90.4 Mbps` (`WA .20`), `ani_ofdm_level=2` (`firstep=1`, `mrc_cck=1`) |
| **AF-LTU (`Beetle` `.110`)** | `v20.0` | `264` | `0.184 ms` RTT, `IRQ 52 -> CPU1` (`smp_affinity=2`), `netdev_budget=480` / `dev_weight=48`, `0` `/dev/ame*` touches |
| **PtP VHT40 (`PBE-5AC-Gen2`)** | `v4.0` | Isolated | `25.47 Mbps` goodput, `2.91 ms` `p50` RTT at `5745 MHz` `VHT40` (`.241 <-> .242` untouched) |
| **Guarida 3-Sector Tower** | `v9.0` | `34` EPs | `457.90 Mbps` pre-field OTA $\rightarrow$ `491.80 Mbps` post-hog-remediation (`+33.90 Mbps` from top-4 hog fixes) |

## 3. Universal Zero-Rogue-DHCP Guarantee
- **OpenWrt (`WA/XC/XW` `180` `v20` SquashFS Images)**: Enforces `uci set dhcp.lan.ignore='1'`, `dhcpv4='disabled'`, `dhcpv6='disabled'`, `ra='disabled'`, and stops/disables `dnsmasq` & `odhcpd` on first boot via `99-fmx-wa-universal-champion-v20` and `fmx_openwrt_lan_rogue_dhcp_and_ani_guard.sh`.
- **AF-LTU (`Beetle` Safe Kit `v20`)**: Verifies `0` rogue DHCP server daemons on `br0` via `fmx_ltu_irq_napi_and_dhcp_guard.sh --inspect-only`.

## 4. Artifacts & Verification
- Script: [`tools/autoresearch/build_stage781a_cross_fleet_champion_v58_bundle.py`](../tools/autoresearch/build_stage781a_cross_fleet_champion_v58_bundle.py)
- Receipt: [`artifacts/autoresearch/stage781a_cross_fleet_champion_v58_bundle.json`](../artifacts/autoresearch/stage781a_cross_fleet_champion_v58_bundle.json)
- Test: [`tests/test_stage781a.py`](../tests/test_stage781a.py)
