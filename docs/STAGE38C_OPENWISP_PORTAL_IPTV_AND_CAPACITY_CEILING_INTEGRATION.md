<!-- doc-head: STAGE38C_OPENWISP_PORTAL_IPTV_AND_CAPACITY_CEILING_INTEGRATION.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 38C — OpenWISP Dual-NMS Portal IPTV & 6-Family Capacity Ceiling Integration

**Task ID:** `T-S38C-GEM2-OPENWISP-PORTAL-IPTV-TAB-AND-FULL-WISP-ROLLOUT-BLUEPRINT`  
**Date:** `2026-10-25`  
**Servers & Portal Generators:** [`tools/serve_openwisp_dual_nms_live.py`](<repo>/tools/serve_openwisp_dual_nms_live.py), [`tools/serve_command_center_live.py`](<repo>/tools/serve_command_center_live.py), [`tools/build_command_center_html.py`](<repo>/tools/build_command_center_html.py)  
**HTML Portals:** [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](<repo>/artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html), [`artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html`](<repo>/artifacts/dashboard/FUTURAMAX_COMMAND_CENTER.html)

---

## 1. REST API Endpoints Mounted on OpenWISP Dual-NMS Portal (`:8788`) & Live Command Center (`:8765`)

Both [`OpenWispDualNmsHandler`](<repo>/tools/serve_openwisp_dual_nms_live.py#L975-L1065) and [`CommandCenterHandler`](<repo>/tools/serve_command_center_live.py#L142-L245) now expose two dedicated REST endpoints for WISP IPTV & Capacity Ceiling orchestration:

| Endpoint | HTTP Method | Payload Returned |
| :--- | :---: | :--- |
| **`/api/v1/iptv/capacity/`** | `GET` | Full Stage 36C/37C/38C JSON bundle via [`build_iptv_and_capacity_ceiling_api_payload`](<repo>/tools/serve_openwisp_dual_nms_live.py#L563-L579): 6-Family Capacity Ceiling matrix, 32-CPE Sector IPTV Concurrency scenarios (`20 MHz` & `40 MHz`), Backhaul ROI calculator (`-93.12%` savings on `PTP-Alma`), MikroTik RouterOS v7 config, and POP `NGINX` `/dev/shm` CMAF Edge Cache config. |
| **`/api/v1/controller/template/iptv/`** | `GET` | 1-Click OpenWISP `netjsonconfig.OpenWrt` `DeviceConfiguration` template (`FMX openwrt_iptv_ac_vi_dms_champion_v8`, SHA-256 `da0bd9dfe0f96432be458732a20e889778b33915a40ebee97976e472d9737846`) via [`export_openwisp_iptv_netjson_template`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py#L366-L450). |

---

## 2. Dedicated `WISP IPTV & 6-Family Capacity Ceiling` Section in `OPENWISP_DUAL_NMS_PORTAL.html`

Section 5 (`#wisp-iptv-capacity-ceiling-tab`) in [`OPENWISP_DUAL_NMS_PORTAL.html`](<repo>/artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html) surfaces four self-contained operator panels:

1. **a) 1-Click OpenWISP NetJSON IPTV Template (`FMX openwrt_iptv_ac_vi_dms_champion_v8`):**
   - Displays the deterministic SHA-256 checksum (`da0bd9dfe0f96432...`) and the complete RAM-only (`/tmp/futuramax/apply_iptv_ac_vi_dms_ram.sh`) script configuring `br-lan` IGMPv2/v3 snooping + `multicast_to_unicast=1` (DMS), `DSCP CS4/AF41 -> WMM AC_VI (1200/2400 us AQL)`, `sch_fq` video pacing (`maxrate 3500kbit`), and `ff_mcast_airtime_limit=5`.
2. **b) 6-Family Realistic PtMP/PtP Capacity Ceiling Matrix:**
   - Contrasts **Stock Baseline**, **Current Achieved Champion**, **Realistic Fine-Tuned Target**, and **Physical Silicon Ceiling** across all 6 hardware families (`OpenWrt QCA988x PtP & PtMP`, `Stock airOS 8 5 GHz XC/WA`, `Stock airOS 8 2.4 GHz 2XC/XM`, `LTU Custom Silicon AME/AD9361/Cyclone V`, `Legacy airOS 6 M5 XW`, and `airFiber 4X Invictus v2`).
3. **c) 32-CPE Sector IPTV Concurrency Calculator (`20 MHz` vs. `40 MHz`):**
   - Shows Stock `3/32` (`9.4%`) vs. FuturaMAX `Champion v8/v9` **`22/32` (`68.8%`) `1080p60` & `32/32` (`100%`) ABR** on `20 MHz` (**`7.33x` multiplier**, `11.0 ms` loaded `p95` RTT) and **`28/32` (`87.5%`) `1080p60` & `32/32` (`100%`) ABR** on `40 MHz` (**`9.33x` multiplier**, `9.4 ms` loaded `p95` RTT).
4. **d) Copy-Pasteable Core BNG & Tower Edge Configurations:**
   - **MikroTik RouterOS v7 (`MK2-RS` `198.18.0.2`):** `DSCP CS4 (32) / AF41 (34)` mangle rules, `CAKE diffserv4` queues, and IGMP proxy (preserving `ether2-sw-poe200` backbone safety).
   - **Tower/POP `NGINX` `/dev/shm` HLS/CMAF Edge Micro-Cache & `SVT-AV1` ABR Transcoder:** Reduces `PTP-Alma` backhaul load for 16 viewers across 4 channels from `128.0 Mbps` down to `8.8 Mbps` (**`-93.12%` savings**).
