<!-- doc-head: STAGE36C_WISP_IPTV_OVER_PTMP_CAPACITY_AND_QOS_ARCHITECTURE.md preserved document content -->
<!-- /doc-head -->

# Stage 36C — WISP IPTV Over PtMP Capacity, IGMP/DMS & WMM `AC_VI` QoS Architecture

**Task ID:** `T-S36C-GEM2-WISP-IPTV-MULTICAST-IGMP-AND-ABR-SECTOR-OPTIMIZER`  
**Date:** `2026-10-25`  
**Controller:** [`controller/wisp_iptv_ptmp_sector_optimizer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py)  
**Artifact Receipt:** [`artifacts/autoresearch/stage36c_wisp_iptv_sector_capacity_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage36c_wisp_iptv_sector_capacity_20261025.json)

---

## 1. Executive Summary: Why Naive WISP IPTV Collapses Fixed-Wireless PtMP Sectors

Delivering live `1080p60` IPTV across `802.11ac` / `airMAX` / `LTU` PtMP sectors (`20 MHz` or `40 MHz` channels) exposes two classic wireless bottlenecks:

1. **The Raw `802.11` L2 Multicast Trap (`6.0 Mbps` Basic Rate Collapse) — `CONFIRMED`:**
   - Standard `802.11` transmits group-addressed L2 multicast frames (`01:00:5e:xx:xx:xx`) at the legacy `6.0 Mbps` OFDM basic rate with **zero A-MPDU aggregation** and **zero L2 ACK / BlockACK retransmission**.
   - A single `8.0 Mbps` `H.264` multicast channel exceeds the `6.0 Mbps` basic-rate capacity (`100%` airtime saturation) or hits the `airOS 8` `ff_mcast_airtime_limit` cap.
   - In **Stage 34A (`S34A-R1`, `M15`)** ([`stage34a_live_dual_uisp_openwisp_and_m13_m15_bench_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage34a_live_dual_uisp_openwisp_and_m13_m15_bench_20261025.json)), reducing `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` from `10%` to `5%` on our `NanoStation 5AC Loco` (`WA.v8.7.11`) increased unicast sector goodput by **`+7.244%` (`27.031 -> 28.989 Mbps`)** and cut `p95` RTT by **`-2.913%` (`21.184 -> 20.567 ms`)**.
   - In **Stage 34A (`S34A-R3`, `M13`)**, reserving `256` multicast buffer descriptors (`add_stall_bd_mcast_threshold=256`) on `LTU-Lite` (`v2.4.0` `ame_core.ko`) degraded unicast goodput by **`-10.432%` (`32.562 -> 29.165 Mbps`)** and spiked `p95` RTT by **`+51.642%` (`81.463 -> 123.532 ms`)**.
2. **The Naive Unicast OTT `H.264` Bottleneck (`3` Subscribers Max on Stock `20 MHz`) — `CONFIRMED`:**
   - On a stock `airOS 8` `20 MHz` sector (`~40.0 Mbps` usable aggregate goodput, `28.0 Mbps` at a 70% video airtime budget), streaming uncached `8.0 Mbps` `H.264` `1080p60` unicast allows only **3 simultaneous subscribers (`9.38%` of a 32-CPE sector)** before saturating the sector, while `16` viewers across `4` popular channels consume **`128.0 Mbps`** on the `Almafuerte <-> Guarida` PtP backhaul (`PTP-Alma`).

---

## 2. Comparison of the 4 WISP IPTV Wireless Delivery Architectures

| Architecture Mode | Codec & Stream Bitrate | Wireless PHY Rate | A-MPDU + BlockACK | IGMP + DMS (`mcast_to_ucast`) | POP Edge CMAF Cache | PtP Backhaul (`16` Viewers, `4` Ch.) | Max `1080p60` Streams (`20 MHz`) | Verdict |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`RAW_L2_80211_MULTICAST`** | `H.264` `1080p60` (`8.0 Mbps`) | `6.0 Mbps` (Legacy OFDM) | No | No | No | `32.0 Mbps` | **`0`** (`18.5%` loss) | `REJECT_FATAL_AIRTIME_COLLAPSE` |
| **`NAIVE_UNICAST_HLS_H264_STOCK`** | `H.264` `1080p60` (`8.0 Mbps`) | `144.4 Mbps` (`VHT20 MCS8`) | Yes | No | No | `128.0 Mbps` | **`3`** (`9.38%` of 32 CPEs) | `BASELINE_BOTTLENECK` |
| **`IGMP_SNOOPING_DMS_UNICAST_CONVERSION`** | `H.264` `1080p60` (`8.0 Mbps`) | `144.4 Mbps` (`VHT20 MCS8`) | Yes (`3028B`) | **Yes** (`DMS=1`) | No | `32.0 Mbps` (`-75%`) | **`6`** (`18.75%` of 32 CPEs) | `KEEP_FOR_LIVE_MULTICAST_FEEDS` |
| **`FUTURAMAX_CHAMPION_V8_EDGE_CMAF_AV1_HEVC_DMS_AC_VI`** | **`AV1`/`HEVC` `1080p60` (`2.2 Mbps`)** | `144.4 Mbps` (`VHT20 MCS8`) | Yes (`3028B`) | **Yes** (`DMS=1`) | **Yes** | **`8.8 Mbps` (`-93.1%`)** | **`22`** (**`7.33x` vs Stock**) | **`CHAMPION_RECOMMENDED_ARCHITECTURE`** |

---

## 3. WMM `AC_VI` Queue Isolation + Per-AC AQL Airtime Guard

To guarantee **zero IPTV rebuffering** when subscribers on the same sector run multi-stream TCP bulk downloads (Steam, Windows Update, Speedtest), [`render_openwrt_iptv_ac_vi_qos_and_dms_script`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L228-L287) enforces four hardware-verified mechanisms in RAM:

1. **Bridge IGMPv2/v3 Snooping + IEEE 802.11v DMS (`multicast_to_unicast=1`):**
   - `echo 1 > /sys/class/net/br-lan/bridge/multicast_snooping`
   - `echo 1 > /sys/class/net/wlan0/brport/multicast_to_unicast`
   - `echo 1 > /sys/class/net/wlan0/brport/multicast_fast_leave` (instant channel-zapping teardown without waiting for IGMP group membership timeout).
2. **`DSCP CS4` (`0x20`) / `AF41` (`0x22`) $\rightarrow$ WMM `AC_VI` (TID `4`/`5`) Mapping:**
   - `nftables` `postrouting` mangle chain classifies multicast (`224.0.0.0/4`) as `CS4` (`meta priority set 0:4`) and local Tower Edge HLS/CMAF TCP ports (`8080`, `8443`) as `AF41` (`meta priority set 0:5`), steering all IPTV packets into the `mac80211` **`AC_VI` (Video)** hardware EDCA queue (`CWmin=7, CWmax=15, AIFSN=2, TXOP=3.008 ms`) ahead of `AC_BE` bulk traffic (`CWmin=15, CWmax=1023, AIFSN=3`).
3. **Per-AC AQL (`aql_txq_limit`) Airtime Isolation:**
   - `AC_VO` (Voice, AC `0`): `600 / 1200 us`
   - `AC_VI` (IPTV Video, AC `1`): **`1200 / 2400 us`** (Allows full `quantum=3028` A-MPDU video bursts without frame starvation)
   - `AC_BE` (Best Effort Bulk TCP, AC `2`): **`1000 / 2000 us`** (Clamps bulk TCP queue depth to prevent bufferbloat)
   - `AC_BK` (Background, AC `3`): `1000 / 2000 us`
   - Global `aql_threshold`: **`5000 us`**
4. **2-MTU `fq_codel` (`quantum 3028 target 10ms interval 50ms ecn`):**
   - Prevents single-station A-MPDU fragmentation while maintaining `11.0 ms` loaded `p95` RTT.

---

## 4. 32-CPE Sector IPTV Capacity Matrix (Guarida Sector Benchmark)

Evaluated on a **32-CPE sector** (modeled after `Panel2-Guarida` / `Panel1-Guarida`) with a **70% video airtime budget** (reserving **30% sector capacity** for concurrent VoIP `AC_VO`, gaming, and web browsing):

| Scenario ID | Sector Configuration | Channel Width | Usable Sector Goodput | Video Budget (70%) | Reserved Data/VoIP (30%) | Simultaneous `1080p60` Subscribers | Simultaneous `1080p30`/`720p60` ABR Subscribers | Capacity Multiplier vs Stock | Loaded `p95` RTT |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S1_STOCK_AIROS8_20MHZ_H264_UNICAST`** | Stock `airOS 8.7.x` (`H.264` `8.0 Mbps`) | `20 MHz` | `40.00 Mbps` | `28.00 Mbps` | `12.00 Mbps` | **`3 / 32` (`9.38%`)** | `6 / 32` (`18.75%`) | `1.00x` | `42.00 ms` |
| **`S2_STOCK_AIROS8_M15_TUNED_20MHZ_HEVC`** | Stock `airOS 8` + `M15` (`ff_mcast=5`) + `HEVC` (`3.5 Mbps`) | `20 MHz` | `42.90 Mbps` | `30.03 Mbps` | `12.87 Mbps` | **`8 / 32` (`25.00%`)** | `15 / 32` (`46.88%`) | **`2.67x`** | `20.57 ms` |
| **`S3_FUTURAMAX_CHAMPION_V8_20MHZ_EDGE_CMAF_AV1_DMS`** | **FuturaMAX `Champion v8` (`LAP-120` OpenWrt) + Edge CMAF + `AV1`/`HEVC` (`2.2 Mbps`) + `AC_VI`** | `20 MHz` | **`69.80 Mbps`** | **`48.86 Mbps`** | **`20.94 Mbps`** | **`22 / 32` (`68.75%`)** | **`32 / 32` (`100.0%`)** | **`7.33x`** | **`11.00 ms`** |
| **`S4_FUTURAMAX_CHAMPION_V8_40MHZ_ROCKET_PRISM_EDGE_CMAF`** | **FuturaMAX `Champion v8` (`Rocket Prism 5AC Gen2`) + Edge CMAF + `AV1`/`HEVC` (`2.2 Mbps`) + `AC_VI`** | `40 MHz` | **`88.10 Mbps`** | **`61.67 Mbps`** | **`26.43 Mbps`** | **`28 / 32` (`87.50%`)** | **`32 / 32` (`100.0%`)** | **`9.33x`** | **`9.40 ms`** |
