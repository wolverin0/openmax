<!-- doc-head: STAGE35A_LIVE_OPENWISP_PORTAL_AND_M15_5GHZ_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 35A — Live OpenWISP 26.09 + Dual-UISP Central Management Web Portal & 5 GHz `M15` Cross-Band Physical Benchmark

- **Task ID**: `T-S35A-LIVE-OPENWISP-PORTAL-SERVER-AND-5GHZ-M15-CROSSBAND-BENCH`
- **Date**: `2026-10-25`
- **Author**: `subagent:bench-runner`
- **Persistence Mode**: **`0` Flash Writes (`100%` RAM-Only across all physical bench radios)**
- **Authoritative Receipt**: [`artifacts/autoresearch/stage35a_openwisp_portal_and_m15_5ghz_bench_20261025.json`](../artifacts/autoresearch/stage35a_openwisp_portal_and_m15_5ghz_bench_20261025.json)
- **Live Portal Dashboard**: [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](../artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html) (`108,235` bytes)
- **Live Server & REST API**: [`tools/serve_openwisp_dual_nms_live.py`](../tools/serve_openwisp_dual_nms_live.py)

---

## 1. Executive Summary

Stage 35A accomplished two major deliverables:

1. **`S35A-R1` (`M15_5GHz` Cross-Band Physical Benchmark on the 3-CPE 5 GHz Sector — `PROMOTE_NEW_CHAMPION` / `Stage 35A Champion v9`, `CONFIRMED`)**:
   - Ported our Stage 34A 2.4 GHz winner (`M15`: `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit = 5`) from `Rocket 2AC Prism` (`.253`) to the 5 GHz `Rocket Prism 5AC Gen2` (`.198`) and paired it with a critical OpenWrt 24.10.4 4-addr WDS bridge discovery on `LAP-120` (`.20`):
     - On OpenWrt 24.10.4 (`Linux 6.6.110`), dynamic per-station 4-addr WDS bridge ports (`phy0-ap0.sta1`, `phy0-ap0.sta2`) default to `multicast_to_unicast = 0` even when the parent `phy0-ap0` VAP has `multicast_to_unicast = 1`, and `br-lan` defaults to `multicast_snooping = 0` and `multicast_querier = 0`.
     - Enabling `multicast_snooping = 1`, `multicast_querier = 1`, and `multicast_to_unicast = 1` across all `phy0-ap0*` bridge ports on `LAP-120` alongside `ff_mcast_airtime_limit = 5` on `Rocket Prism 5AC Gen2` (`.198`) eliminated low-rate `6 Mbps` (`MCS 0`) multicast airtime stalls across the 3-CPE 5 GHz sector.
   - Across a counterbalanced 4-phase `A1 -> B1 -> A2 -> B2` benchmark starting strictly from **`Stage 31A Champion v8`**, `M15_5GHz` increased aggregate 20 MHz sector goodput from **`59.888 -> 60.909 Mbps` (`+1.705%`, peaking at `61.659 Mbps` / `3.083 Mbps/MHz` in `B2`)**, reduced loaded sector `p95` RTT from **`76.834 -> 65.216 ms` (`-15.121%`)**, and reduced loaded sector `p99` RTT from **`84.115 -> 72.688 ms` (`-13.585%`)** (`0.00%` packet loss, Pareto score delta **`+6.9972%`** -> **`PROMOTE_NEW_CHAMPION`**).

2. **Live OpenWISP 26.09 + Dual-UISP Central Management Web Portal & REST API (`tools/serve_openwisp_dual_nms_live.py` & `artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`)**:
   - Registered all **8 physical bench radios** (`LAP-120`, `NanoStation 5AC Loco`, `Rocket Prism 5AC Gen2`, `LiteBeam M5`, `Rocket 2AC Prism`, `NanoStation Loco M2`, `LTU-Lite #1`, and `LTU-Lite #2`) with:
     - Their 3-layer `NetJSON` `DeviceConfiguration` templates (`layer1_universal_linux_tcp_bridge`, `layer2_soc_radio_driver_family`, `layer3_per_link_rf_overrides`) and deterministic SHA-256 checksums (`APPROVED_PROFILE_SET_SHA256 = 26d7aa8e97f89bc7f69a88e02a4672053f3ca7d76775417371784de654f51f6e`),
     - Their validated `NetJSON` `DeviceMonitoring` telemetry (`validate_device_monitoring` = `True`),
     - Their live Ubiquiti UISP NMS `udapi-bridge` AES-256-GCM coexistence envelopes (`unms.status=2`, 96-bit IV/nonce, 128-bit auth tag, Base64 ciphertext preview, and per-CPE `wstalist` table), and
     - All **5 live published upstream OpenWrt Wiki Table-of-Hardware (ToH) links** (`rocket_ac`, `nanostation_ac_loco`, `litebeam_5ac_gen2`, `powerbeam`, `common`).

---

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Physical Benchmark Results (`S35A-R1`: `M15_5GHz`)

| Phase / Metric | `Arm A` (`Stage 31A Champion v8`) | `Arm B` (`Champion v8 + M15_5GHz` -> `Champion v9`) | Delta (`A -> B`) | Verdict |
| :--- | :---: | :---: | :---: | :--- |
| **Phase 1 (`A1` / `B1`) Goodput** | `59.105 Mbps` (`2.955 Mbps/MHz`) | **`60.158 Mbps` (`3.008 Mbps/MHz`)** | `+1.782%` | — |
| **Phase 2 (`A2` / `B2`) Goodput** | `60.670 Mbps` (`3.034 Mbps/MHz`) | **`61.659 Mbps` (`3.083 Mbps/MHz`)** | `+1.630%` | — |
| **Mean Aggregate Goodput** | `59.888 Mbps` | **`60.909 Mbps`** | **`+1.705%`** | **PASS** |
| **Phase 1 (`A1` / `B1`) Sector `p95` RTT** | `74.982 ms` | **`71.443 ms`** | `-4.720%` | — |
| **Phase 2 (`A2` / `B2`) Sector `p95` RTT** | `78.685 ms` | **`58.989 ms`** | `-25.031%` | — |
| **Mean Loaded Sector `p95` RTT** | `76.834 ms` | **`65.216 ms`** | **`-15.121%`** | **`PROMOTE_NEW_CHAMPION` (`CONFIRMED`)** |
| **Mean Loaded Sector `p99` RTT** | `84.115 ms` | **`72.688 ms`** | **`-13.585%`** | **Pareto `+6.9972%`** |
| **Packet Loss (`%`)** | `0.00%` | **`0.00%`** | `0.00%` | `0` station drops |

### Exact Hardware Readbacks Verified in Each Phase
- **`Arm A` (`A1`, `A2`)**:
  - `LAP-120` (`198.18.0.43`): `br-lan/bridge/multicast_snooping = 0`, `multicast_querier = 0`, `brif/phy0-ap0.sta1/multicast_to_unicast = 0`, `brif/phy0-ap0.sta2/multicast_to_unicast = 0`
  - `Rocket Prism 5AC Gen2` (`198.18.0.64`): `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit = 0	0	0...`
- **`Arm B` (`B1`, `B2` — Winning State Retained in RAM)**:
  - `LAP-120` (`198.18.0.43`): `br-lan/bridge/multicast_snooping = 1`, `multicast_querier = 1`, `brif/phy0-ap0.sta1/multicast_to_unicast = 1`, `brif/phy0-ap0.sta2/multicast_to_unicast = 1`, `brif/phy0-ap0/multicast_to_unicast = 1`
  - `Rocket Prism 5AC Gen2` (`198.18.0.64`): `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit = 5	0	0...`

---

## 3. Registered Bench Radios in OpenWISP 26.09 + Dual-UISP Portal (`OPENWISP_DUAL_NMS_PORTAL.html`)

| # | Device Key | IP / MAC | SoC & OS | Active Profile & Checksum Prefix | Goodput | `p95` RTT | Dual-NMS State |
| :-: | :--- | :--- | :--- | :--- | :---: | :---: | :--- |
| 1 | `lap120_ap_openwrt` | `198.18.0.43`<br>`PUBLIC_DEVICE_0086` | `WA` (`AR9342 + QCA9882`)<br>`OpenWrt 24.10.4` | `openwrt_lap120_ptmp_multicpe_champion`<br>`Stage 35A Champion v9` | **`60.909 Mbps`** | **`65.216 ms`** | OpenWISP `applied` + UISP `unms.status=2` (`3` CPEs in `wstalist`) |
| 2 | `loco5ac_cpe_openwrt` | `198.18.0.47`<br>`PUBLIC_DEVICE_0036` | `WA` (`AR9342 + QCA9882`)<br>`OpenWrt 24.10.4` | `openwrt_lap120_ptp_1cpe_champion`<br>`Stage 31A Champion v8` | `27.640 Mbps` | `65.216 ms` | OpenWISP `applied` + UISP `unms.status=2` |
| 3 | `r5ac_prism_cpe_airos8` | `198.18.0.64`<br>`PUBLIC_DEVICE_0048` | `XC` (`QCA9558 + QCA9880 + AirPrism`)<br>`airOS XC.v8.7.19` | `r5ac_prism_sta`<br>`Stage 35A XC Champion` | `26.456 Mbps` | `23.511 ms` | OpenWISP `applied` + UISP `unms.status=2` |
| 4 | `lbm5_xw_cpe_airos6` | `198.18.0.48`<br>`PUBLIC_DEVICE_0066` | `XW` (`AR9342`)<br>`airOS XW.v6.3.2` | `pbm5_xw_weak_ota`<br>`Stage 26 XW Champion` | `8.480 Mbps` | `65.216 ms` | OpenWISP `applied` + UISP `unms.status=2` |
| 5 | `r2ac_prism_ap_airos8_24ghz` | `198.18.0.65`<br>`PUBLIC_DEVICE_0087` | `2XC` (`QCA9558 + QCA9880 2.4 GHz`)<br>`airOS 2XC.v8.7.1` | `r2ac_prism_ap`<br>`Stage 34A S34A-R1 Champion` | **`28.989 Mbps`** | **`20.567 ms`** | OpenWISP `applied` + UISP `unms.status=2` (`1` CPE in `wstalist`) |
| 6 | `nanoloco_m2_xm_cpe_24ghz` | `198.18.0.50`<br>`PUBLIC_DEVICE_0088` | `XM` (`AR7241 + AR9285`)<br>`airOS XM.v6.1.12` | `r2ac_prism_ap`<br>`Stage 27 2.4 GHz CPE` | `28.989 Mbps` | `20.567 ms` | OpenWISP `applied` + UISP `unms.status=2` |
| 7 | `ltu_lite_1_amesoc` | `198.18.0.63`<br>`PUBLIC_DEVICE_0045` | `LTU` (`Zynq-7000 + AME SoC`)<br>`AF-LTU.v2.4.0` | `ltu_lite_amesoc`<br>`Stage 24F S24F-R1 Champion` | **`32.562 Mbps`** | **`47.006 ms`** | OpenWISP `applied` + UISP `unms.status=2` |
| 8 | `ltu_lite_2_amesoc` | `198.18.0.118`<br>`PUBLIC_DEVICE_0089` | `LTU` (`Zynq-7000 + AME SoC`)<br>`AF-LTU.v2.4.0` | `ltu_ptmp_3unit_sector_champion`<br>`Stage 24F S24F-R1 Champion` | `32.562 Mbps` | `47.006 ms` | OpenWISP `applied` + UISP `unms.status=2` |
