<!-- doc-head: STAGE37C_REALISTIC_PTMP_PTP_CAPACITY_AND_IPTV_OPERATOR_PLAYBOOK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 37C — Realistic PtMP/PtP Capacity Ceiling Across All 6 Radio Families & WISP IPTV Operator Playbook

**Task ID:** `T-S37C-GEM2-PTMP-PTP-REALISTIC-CAPACITY-CEILING-AND-IPTV-NETJSON-TEMPLATE`  
**Date:** `2026-10-25`  
**Calculator & Exporter:** [`analysis/realistic_ptmp_ptp_capacity_and_iptv_roi_calculator.py`](<repo>/analysis/realistic_ptmp_ptp_capacity_and_iptv_roi_calculator.py), [`controller/wisp_iptv_ptmp_sector_optimizer.py`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py)  
**Artifact Receipt:** [`artifacts/autoresearch/stage37c_realistic_capacity_and_iptv_roi_20261025.json`](<repo>/artifacts/autoresearch/stage37c_realistic_capacity_and_iptv_roi_20261025.json)

---

## 1. Current Achieved vs. Realistic Fine-Tuned vs. Physical Silicon Ceiling Matrix (All 6 Radio Families)

Every number below separates **Stock Baseline**, **Current Achieved Champion (Verified on Physical Bench)**, **Realistic Fine-Tuned Target**, and **Hard Physical Silicon / Shannon-MAC Ceiling** at `20 MHz`:

| Family ID | Radio Family & Representative Hardware | Mode (`20 MHz`) | Stock Goodput | **Current Achieved Champion** | **Realistic Fine-Tuned** | **Physical Silicon Ceiling** | Loaded `p95` RTT (`Stock -> Achieved -> Ceiling`) | `1080p60` IPTV (`Stock -> FMX`) | Primary Silicon / MAC Boundary |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`FAM1_OPENWRT_QCA988X_PTP_20MHZ`** | OpenWrt `QCA988x` (`LAP-120` $\leftrightarrow$ `Loco 5AC`) | PtP 1-CPE (`VHT20 MCS8`) | `60.43 Mbps` | **`76.44 Mbps` (`+26.49%`)** | **`79.50 Mbps`** | **`81.50 Mbps`** | `43.64 -> 17.46 -> 14.00 ms` | `5 -> 25` (`32` ABR) | `AR9342` `535 MHz` MIPS `74Kc` softirq/NAPI & PCIe HTT copy latency |
| **`FAM1_OPENWRT_QCA988X_PTMP_20MHZ`** | OpenWrt `QCA988x` (`LAP-120` 3..32 CPE Sector) | PtMP Mixed (`VHT20`/`HT20`) | `45.73 Mbps` | **`69.80 Mbps` (`+52.63%`)** | **`72.50 Mbps`** | **`76.00 Mbps`** | `110.40 -> 38.97 -> 29.00 ms` | **`3 -> 22` (`32` ABR)** | Heterogeneous `1x1` `802.11n` vs `2x2` `802.11ac` airtime serialization |
| **`FAM2_AIROS8_5GHZ_XC_WA_20MHZ`** | Stock `airOS 8` 5 GHz (`Rocket Prism 5AC Gen2` XC / `Loco 5AC` WA) | PtMP/PtP `airMAX AC` | `51.02 Mbps` | **`70.68 Mbps` (`+38.53%`)** | **`75.20 Mbps`** | **`78.50 Mbps`** | `187.04 -> 23.86 -> 17.50 ms` | `4 -> 22` (`32` ABR) | Linux `2.6.32.68` legacy TCP stack & `IRQ 64` AirPrism interrupt rate |
| **`FAM3_AIROS8_24GHZ_2XC_XM_20MHZ`** | Stock `airOS 8` 2.4 GHz (`Rocket 2AC Prism` $\leftrightarrow$ `NanoLoco M2`) | 2.4 GHz PtMP Mixed | `23.85 Mbps` | **`28.99 Mbps` (`+21.55%`)** | **`30.40 Mbps`** | **`31.50 Mbps`** | `38.40 -> 15.17 -> 13.20 ms` | `2 -> 9` (`13` ABR) | `AR7240` `400 MHz` + `AR9285` `802.11n` PHY & 2.4 GHz ISM noise |
| **`FAM4_LTU_AMESOC_CYCLONEV_20MHZ`** | Ubiquiti `LTU` (`LTU-Lite` `v2.4.0` `AME SoC` + `AD9361` + `Cyclone V`) | AP-PtMP SQ (`0xae05`) & PtP | `29.85 Mbps` | **`67.48 Mbps` (`+126.06%`)** | **`86.50 Mbps`** | **`92.00 Mbps`** | `213.93 -> 47.01 -> 12.00 ms` | `2 -> 21` (`31` ABR) | `2 ms` TDD turnaround tax, `czlen` contention symbols & `IRQ 63` budget |
| **`FAM5_AIROS6_M5_XW_WEAK_OTA_20MHZ`** | Legacy `airOS 6` `802.11n` (`PowerBeam M5` `XW.v6.3.22` at `-80 dBm`) | PtP Weak Link Rescue (`-80 dBm`) | `11.40 Mbps` | **`15.22 Mbps` (`+33.51%`)** | **`16.00 Mbps`** | **`16.50 Mbps`** | `16.94 -> 6.41 -> 5.40 ms` | `1 -> 4` (`7` ABR) | Shannon-Hartley thermal SNR ceiling at `-80 dBm` (`txchainmask=2, rx=3`) |
| **`FAM6_AIRFIBER_4X_INVICTUS2_TDD`** | Ubiquiti `airFiber 4X` (`AM1808` + `Invictus v2` Custom TDD FPGA) | Dedicated PtP Backhaul | `4.58 Mbps` (Sub-ch) | **`5.31 Mbps` (`+15.94%`)** | **`165.00 Mbps` (LoS)** | **`176.00 Mbps` (`20 MHz`)** | `33.25 -> 25.42 -> 1.50 ms` | `1 -> 52` (`77` ABR) | `TI AM1808` (`124 BogoMIPS`) CPU interrupt budget & outdoor MIMO dish LoS |

---

## 2. 1-Click OpenWISP NetJSON IPTV Template (`export_openwisp_iptv_netjson_template`)

Implemented in [`export_openwisp_iptv_netjson_template`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py#L366-L450), OpenWISP exports a deterministic `netjsonconfig.OpenWrt` `DeviceConfiguration` template (`FMX openwrt_iptv_ac_vi_dms_champion_v8`) that deploys in 1 click:
- Bridge `br-lan`: `igmp_snooping=true`, `multicast_querier=true`, `multicast_to_unicast=true` (`IEEE 802.11v` DMS), and `multicast_fast_leave=1`.
- Per-AC AQL (`aql_txq_limit`): `AC_VO=600/1200 us`, **`AC_VI=1200/2400 us`**, **`AC_BE=1000/2000 us`**, `AC_BK=1000/2000 us`, `aql_threshold=5000 us`.
- Egress QoS & Video Pacing: `tc qdisc replace dev wlan0 root fq_codel limit 1024 flows 1024 quantum 3028 target 10ms interval 50ms ecn` + `tc qdisc replace dev eth0 root fq quantum 3028 initial_quantum 15140 maxrate 3500kbit`.
- Stock `airOS 8` Coexistence: `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit = 5` (`S34A-R1` `M15` `+7.244%` goodput winner).
- `nftables` `fmx_iptv_qos`: `224.0.0.0/4 -> DSCP CS4 (0x20, priority 0:4)` and `tcp sport {8080, 8443} -> DSCP AF41 (0x22, priority 0:5)`.

---

## 3. MikroTik RouterOS v7 (`MK2-RS` `198.18.0.2`) Core Mangle, CAKE `diffserv4` & IGMP Proxy

> [!IMPORTANT]
> **Guarida Topology Safety Rule:** `ether2-sw-poe200` on `198.18.0.2` (`MK2-RS`) carries the backbone `Edificio Principal -> Almafuerte (198.18.0.3) -> Guarida (198.18.0.4)`. Never disable or cycle `ether2-sw-poe200`.

```routeros
/ip firewall mangle
add action=change-dscp chain=postrouting comment="FuturaMAX IPTV Multicast -> DSCP CS4 (32) WMM AC_VI" \
    dst-address=224.0.0.0/4 new-dscp=32 passthrough=yes
add action=set-priority chain=postrouting comment="FuturaMAX IPTV Multicast -> WMM Priority 4 (AC_VI)" \
    dscp=32 new-priority=4 passthrough=yes
add action=change-dscp chain=postrouting comment="FuturaMAX POP Edge HLS/CMAF -> DSCP AF41 (34) WMM AC_VI" \
    protocol=tcp src-port=8080,8443 new-dscp=34 passthrough=yes
add action=set-priority chain=postrouting comment="FuturaMAX POP Edge HLS/CMAF -> WMM Priority 5 (AC_VI)" \
    dscp=34 new-priority=5 passthrough=yes

/queue type
add kind=cake name=fmx-cake-diffserv4-dl cake-diffserv=diffserv4 cake-flowmode=dual-dsthost \
    cake-nat=yes cake-rtt=20ms cake-overhead=38 cake-mpu=84
add kind=cake name=fmx-cake-diffserv4-ul cake-diffserv=diffserv4 cake-flowmode=dual-srchost \
    cake-nat=yes cake-rtt=20ms cake-overhead=38 cake-mpu=84

/routing igmp-proxy
set quick-leave=yes query-interval=30s query-response-interval=5s
/routing igmp-proxy interface
add interface=vlan-iptv-ingest upstream=yes alternative-subnets=0.0.0.0/0
add interface=ether2-sw-poe200 upstream=no
```

---

## 4. POP/Tower `NGINX` HLS/CMAF Edge Micro-Cache & `SVT-AV1` ABR Transcoding

```nginx
# FuturaMAX Stage 37C — Tower/POP NGINX HLS/CMAF Low-Latency Edge Micro-Cache
proxy_cache_path /dev/shm/fmx_cmaf_cache levels=1:2 keys_zone=fmx_iptv_edge:32m
                 max_size=1536m inactive=60s use_temp_path=off;

server {
    listen 8080 reuseport;
    server_name PUBLIC_TERM_0009;
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;

    location ~* \.(m3u8|mpd)$ {
        proxy_pass http://198.18.0.143:9000;
        proxy_cache fmx_iptv_edge;
        proxy_cache_key "$uri";
        proxy_cache_valid 200 1s;
        proxy_cache_lock on;
        proxy_cache_lock_timeout 2s;
        proxy_cache_use_stale updating error timeout;
        add_header X-FuturaMAX-Cache $upstream_cache_status always;
    }

    location ~* \.(m4s|cmfv|cmfa|ts|mp4)$ {
        proxy_pass http://198.18.0.143:9000;
        proxy_cache fmx_iptv_edge;
        proxy_cache_key "$uri";
        proxy_cache_valid 200 206 30s;
        proxy_cache_lock on;
        proxy_cache_lock_age 3s;
        proxy_cache_use_stale updating;
        add_header X-FuturaMAX-Cache $upstream_cache_status always;
    }
}
```

---

## 5. WISP IPTV Backhaul & Sector Economic ROI Summary

- **Backhaul Bandwidth Saved on `PTP-Alma` (`16` Viewers across `4` Live Channels):** Collapses **`128.0 Mbps`** (naive `8.0 Mbps` `H.264` unicast) down to **`8.8 Mbps`** (`4` unique CMAF channels $\times$ `2.2 Mbps` `AV1`/`HEVC`), saving **`119.2 Mbps` (`-93.12%` backhaul load)**.
- **Additional `1080p60` Subscribers Unlocked per `20 MHz` 32-CPE Sector:** **`+19` simultaneous subscribers** (`3 -> 22` at `1080p60`, or **`32 / 32` (`100%`)** at `1.5 Mbps` ABR) with zero additional tower spectrum or RF hardware.
- **Economic Impact (`$8.50/mo` IPTV add-on ARPU + `$1,850` avoided sector-split CapEx):**
  - **Per 32-CPE Sector:** **`+$161.50/month`** (`+$1,938.00/year` recurring revenue) + `$1,850` avoided CapEx.
  - **10-Sector WISP Fleet:** **`+190` `1080p60` IPTV subscribers**, **`+$19,380/year`** recurring revenue + **`$18,500`** avoided tower CapEx = **`$37,880` Year-1 impact**.
