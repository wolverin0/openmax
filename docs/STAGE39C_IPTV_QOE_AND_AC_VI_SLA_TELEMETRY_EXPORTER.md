<!-- doc-head: STAGE39C_IPTV_QOE_AND_AC_VI_SLA_TELEMETRY_EXPORTER.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 39C — OpenWrt / airOS IPTV QoE, RFC 4445 MDI & WMM `AC_VI` SLA Telemetry Exporter

**Task ID**: `T-S39C-GEM2-IPTV-QOE-TELEMETRY-AGENT-AND-UISP-OPENWISP-SLA-EXPORTER`  
**Exporter Module**: [`telemetry/iptv_qoe_and_ac_vi_sla_exporter.py`](<repo>/telemetry/iptv_qoe_and_ac_vi_sla_exporter.py)  
**Machine-Readable Receipt**: [`artifacts/autoresearch/stage39c_iptv_qoe_sla_telemetry_20261025.json`](<repo>/artifacts/autoresearch/stage39c_iptv_qoe_sla_telemetry_20261025.json)

---

## 1. Executive Summary

Stage 39C closes the observability and feedback loop for WISP IPTV delivery over 802.11ac / airMAX / OpenWrt PtMP sectors (`LAP-120`, `Rocket Prism 5AC Gen2`) by building [`telemetry/iptv_qoe_and_ac_vi_sla_exporter.py`](<repo>/telemetry/iptv_qoe_and_ac_vi_sla_exporter.py):

1. **Per-CPE WMM `AC_VI` (`TID 4/5`) vs `AC_BE` (`TID 0`) AQL & Bridge MDB Parser**:
   - Reads `/sys/kernel/debug/ieee80211/phy0/ath10k/aqm` (or `mac80211/aqm`), `bridge mdb show` IGMP group memberships (`239.10.10.x`), and `/sys/class/net/phy0-ap0.sta*/brport/multicast_to_unicast`.
2. **RFC 4445 Media Delivery Index (`MDI = DF : MLR`) & Rebuffering Risk Engine**:
   - Computes per-CPE Delay Factor ($\text{DF} = \text{jitter\_p95\_ms} + \text{ac\_vi\_aql\_airtime\_us}/1000$) and Media Loss Rate ($\text{MLR} = \text{stream\_pps} \times \text{loss\_pct}/100 + \text{aqm\_drops}/\Delta t$).
3. **Closed-Loop Per-CPE ABR Profile Clamping**:
   - Automatically clamps individual degraded stations (`2.2 Mbps 1080p60` $\rightarrow$ `1.5 Mbps 720p60` $\rightarrow$ `0.9 Mbps 480p30`) via per-port `sch_fq maxrate` when SINR/MCS drops below `MCS4` (`< 18 dB` / `< 13 dB`) or `AC_VI` AQL backlog exceeds `2000 us` / `2800 us`, protecting sector airtime for all other subscribers.
4. **Dual-NMS Telemetry Export (OpenWISP `NetJSON` + UISP `udapi-bridge` AES-256-GCM)**:
   - Emits both an OpenWISP `DeviceMonitoring` `iptv_qoe_sla` block and an encrypted Ubiquiti UISP `getIptvQoeSlaStatus` WebSocket JSON-RPC payload.

---

## 2. Per-Station IPTV QoE & ABR Clamp Verification Table

| Station Name | MAC | MCS / SINR | `AC_VI` AQL (`TID 4/5`) | `AC_BE` AQL (`TID 0`) | DMS (`m2u`) | RFC 4445 `MDI (DF:MLR)` | Active ABR Profile | `sch_fq maxrate` | SLA Status |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- |
| **NanoStation-5AC-Loco** | `PUBLIC_DEVICE_0036` | `MCS 8` (`40.0 dB`) | `420 us` (`4 pkts`) | `940 us` (`8 pkts`) | `1` | `2.27:0.0000` | `ABR_TIER1_1080P60_AV1_2200K` (`2.2 Mbps`) | `3500kbit` | `SLA_PASS_BROADCAST_GRADE` |
| **Rocket-Prism-5AC-Gen2** | `PUBLIC_DEVICE_0048` | `MCS 8` (`45.0 dB`) | `310 us` (`3 pkts`) | `680 us` (`6 pkts`) | `1` | `1.73:0.0000` | `ABR_TIER1_1080P60_AV1_2200K` (`2.2 Mbps`) | `3500kbit` | `SLA_PASS_BROADCAST_GRADE` |
| **LiteBeam-M5-XW** | `PUBLIC_DEVICE_0066` | `MCS 4` (`16.5 dB`) | `2180 us` (`6 pkts`) | `1850 us` (`12 pkts`) | `1` | `6.98:0.0000` | `ABR_TIER2_720P60_AV1_1500K` (`1.5 Mbps`, **Clamped**) | `1750kbit` | `SLA_PASS_BROADCAST_GRADE` |
| **Weak-Edge-CPE-Sim** | `PUBLIC_DEVICE_0090` | `MCS 3` (`11.2 dB`) | `3100 us` (`10 pkts`, `1 drop`) | `1980 us` (`16 pkts`) | `1` | `15.60:0.1171` | `ABR_TIER3_480P30_AV1_900K` (`0.9 Mbps`, **Clamped**) | `1050kbit` | `SLA_WARNING_ABR_DOWNSHIFT_ADVISED` |

---

## 3. Closed-Loop ABR Clamping Rules

1. **Tier 1 — Full HD (`ABR_TIER1_1080P60_AV1_2200K`, `2.2 Mbps`, `maxrate 3500kbit`)**:
   - Condition: `mcs_index >= 5` AND `sinr_db >= 18.0 dB` AND `ac_vi_aql_airtime_us <= 2000 us`.
2. **Tier 2 — HD Soft Clamp (`ABR_TIER2_720P60_AV1_1500K`, `1.5 Mbps`, `maxrate 1750kbit`)**:
   - Condition: `mcs_index == 4` OR `13.0 <= sinr_db < 18.0 dB` OR `2000 < ac_vi_aql_airtime_us <= 2800 us`.
3. **Tier 3 — SD Rescue Hard Clamp (`ABR_TIER3_480P30_AV1_900K`, `0.9 Mbps`, `maxrate 1050kbit`)**:
   - Condition: `mcs_index < 4` OR `sinr_db < 13.0 dB` OR `ac_vi_aql_airtime_us > 2800 us`.

---

## 4. Verification

```bash
python telemetry/iptv_qoe_and_ac_vi_sla_exporter.py
python -m pytest tests/test_stage39c_iptv_qoe_exporter.py -v
```
