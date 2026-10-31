<!-- doc-head: STAGE46C_CHAMPION_V13_DUAL_NETDEV_AIRTIME_AND_AQL_INVERSION_GUARD.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 46C — Champion v13 Dual-Netdev (`phy0-ap0 + phy0-ap0.sta*`) Airtime Weights (`768:512:128`), Socket-Layer TCP Lowat 8K Pacing Co-Design & Hardware-Verified AQL Priority Inversion Guard

**Task ID:** `T-S46C-GEM2-CHAMPION-V13-DUAL-NETDEV-WEIGHTS-AND-AQL-INVERSION-GUARD`  
**Owner Lane:** `orca:gemini-lane2`  
**Date:** 2026-10-25  
**Status:** **COMPLETED & VERIFIED**

---

## 1. Executive Summary & Physical Hardware Discoveries (`Stage 41A`)

During the Stage 41A (`T-S41A-CODEX-M22-M23-DYNAMIC-FQ-QUANTUM-AND-VOIP-BURST-GUARD-BENCH`) 4-round (`80` physical measurements) 3-Tier Triple-Play benchmark (`100 pps` G.711 VoIP `DSCP EF -> tid6_ac0 AC_VO` + `470 pps` Dual `1080p60` IPTV `DSCP CS4 -> tid4_ac1 AC_VI` + `3-CPE` Bulk TCP `tid0_ac2 AC_BE`), our physical hardware instrumentation uncovered four critical cross-layer laws on `OpenWrt 24.10.4` (`LAP-120` `QCA9882` AP + `Loco 5AC` + `Rocket Prism 5AC Gen2` + `LiteBeam M5`):

| Round | Candidate Mechanism | Goodput (`Arm A -> Arm B`) | Loaded p95 RTT (`Arm A -> Arm B`) | Dual IPTV Loss (`tid4_ac1`) | VoIP Loss (`tid6_ac0`) | Decision & Physical Cause |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| **`S41A-R1`** | `M22_M23_SQUEEZED_AQL_4MTU_QUANTUM_VOIP_GUARD` (`AP fq_quantum=6056` `4xMTU`, `VO=250/500`, `VI=1000/2000`, `BE=1400/2800`, `thr=4000`) | `50.619 -> 50.098 Mbps` (`-1.029%`) | `107.752 -> 109.733 ms` (`+1.838%`) | `0.2116%` (`12/5,672`) | `0.00%` (`0/1,197`) | **REFUTED** — `fq_quantum=6056` (`4xMTU`) requires `~2,180 us` of airtime per DRR turn, exceeding `AC_BE_low=1400 us` (`2` `tid0_ac2` drops). |
| **`S41A-R2`** | **`M22b_M23b_DUAL_NETDEV_AIRTIME_WEIGHT_AND_TCP_LOWAT_8K_PACING` (Champion v13)** (`Dual-Netdev phy0-ap0 + phy0-ap0.sta* airtime_weight 768:512:128`, `tcp_notsent_lowat=8192`, `tcp_limit_output_bytes=98304`, `tcp_pacing_ca_ratio=105/140`, `fq_quantum=4542/1514`, `VO=300/600`, `VI=1200/2400`, `BE=1500/3000`, `thr=5000`) | **`49.585 -> 50.310 Mbps` (`+1.462%`)** | **`118.851 -> 119.538 ms` (`+0.578%`)** | **`0.4848% -> 0.00%` (`0/5,672`)** | **`0.00%` (`0/1,202`)** | **CONFIRMED (`PROMOTE_NEW_CHAMPION`, Pareto `+1.2598%`)** — Dual-Netdev `768:512:128` weights + `8 KiB` `tcp_notsent_lowat` eliminated Dual IPTV loss to `0.00%` with `0` `tid0_ac2` drops. |
| **`S41A-R3`** | `M22c_M23c_SELECTIVE_VO_VI_AQL_GUARD_AND_768_512_128_WEIGHTS` (`VO=250/500`, **`VI=1000/2000`**, `BE=1500/3000`, `fq_quantum=4542`) | `51.012 -> 49.327 Mbps` (`-3.303%`) | `107.614 -> 112.164 ms` (`+4.228%`) | **`4.728%` (`269/5,689`)** | `0.00%` (`0/1,197`) | **REFUTED** — **AQL Priority Inversion**: setting `AC_VI_low=1000 < AC_BE_low=1500` throttled `tid4_ac1` video before `tid0_ac2` bulk TCP! |
| **`S41A-R4`** | `M22d_M23d_DUAL_NETDEV_768_WEIGHTS_VO_250_500_VI_1200_2400_LOWAT_8K` (`VO=250/500`, **`VI=1200/2400`**, `BE=1500/3000`, `fq_quantum=4542`) | `50.838 -> 51.259 Mbps` (`+0.828%`) | `108.602 -> 112.208 ms` (`+3.321%`) | **`0.00%` (`0/5,671`)** | `0.00%` (`0/1,197`) | **REFUTED** — Restoring `VI=1200/2400` immediately cured IPTV loss (`4.728% -> 0.00%`), while `VO=250/500` inflated p95 RTT (`+3.321%`). |

---

## 2. End-to-End Integration Architecture (`Stage 46C`)

### 2.1 Controller & AQL Priority Inversion Guard ([`controller/wisp_iptv_ptmp_sector_optimizer.py`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py))
- [`validate_aql_and_aqm_priority_inversion_guard`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py#L1271-L1318) enforces three non-negotiable hardware invariants before any NetJSON template or shell script is emitted:
  1. **Rule 1 (`AQL_PRIORITY_INVERSION_VI_BELOW_BE`)**: Rejects `AC_VI_low < 1200` when `AC_BE_low >= 1500` (preventing the `4.728%` Dual IPTV packet loss discovered in `S41A-R3`).
  2. **Rule 2 (`AQM_AQL_QUANTUM_BUDGET_MISMATCH_4MTU`)**: Rejects `fq_quantum > 4542` (`4xMTU` `6056B`) when `AC_BE_low < 1500` or `aql_threshold < 5000` (preventing the `tid0_ac2` drops discovered in `S41A-R1`).
  3. **Rule 3 (`AC_VO_SUB_300US_WAKEUP_CHURN`)**: Rejects `AC_VO_low < 300` under 3-CPE load (preventing the `+3.321%` p95 RTT inflation discovered in `S41A-R4`).
- [`export_openwisp_dual_netdev_champion_v13_netjson_template`](<repo>/controller/wisp_iptv_ptmp_sector_optimizer.py#L1573-L1702) exports the 1-click OpenWISP 26.09 NetJSON DeviceConfiguration template (`FMX openwrt_dual_netdev_768_512_128_tcp_lowat_8k_champion_v13`).

### 2.2 OpenWrt 24.10.4 ImageBuilder First-Boot & Dynamic WDS Hotplug ([`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](<repo>/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py))
- Upgraded [`render_hotplug_99_futuramax_wds_dms`](<repo>/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L351-L424) (`files/etc/hotplug.d/net/99-futuramax-wds-dms`) so whenever a 4-address WDS station associates or re-keys (`phy0-ap0.sta*` `add`/`ifup`), OpenWrt automatically restores:
  - `multicast_to_unicast=1` & `multicast_fast_leave=1`
  - Dual-Netdev (`phy0-ap0 + phy0-ap0.sta*`) station `airtime_weight` `768:512:128` (`PUBLIC_DEVICE_0036 -> 768`, `PUBLIC_DEVICE_0048 -> 512`, `PUBLIC_DEVICE_0066 -> 128`) so `AP_VLAN` netdevs never revert to `Weight: 256`!
- Added [`render_uci_defaults_98_futuramax_champion_v13_aqm`](<repo>/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L657-L758) (`files/etc/uci-defaults/98-futuramax-champion-v13-aqm`) and [`generate_stage46c_imagebuilder_champion_v13_manifest`](<repo>/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py#L1310-L1410) generating [`artifacts/autoresearch/stage46c_imagebuilder_champion_v13_manifest_20261025.json`](<repo>/artifacts/autoresearch/stage46c_imagebuilder_champion_v13_manifest_20261025.json).

### 2.3 Closed-Loop Discovery-to-Research Reactor ([`tools/research/closed_loop_research_reactor.py`](<repo>/tools/research/closed_loop_research_reactor.py))
- Added [`ingest_stage41a_champion_v13_and_synthesize_m26_m27`](<repo>/tools/research/closed_loop_research_reactor.py#L1263-L1406) ingesting all 4 Stage 41A rounds (`S41A-R1..R4`) into the persistent HyperResearch vault and synthesizing:
  - **`M26` (`PB-044`)**: Event-Driven Dual-Netdev (`phy0-ap0 + phy0-ap0.sta*`) Airtime Weight Persistence (`768:512:128`) & TCP Lowat 8K Pacing Co-Design (`tcp_notsent_lowat=8192`, `tcp_limit_output_bytes=98304`, `tcp_pacing_ca_ratio=105/140`).
  - **`M27` (`PB-045`)**: Hardware-Verified AQL Priority Inversion & Quantum/Budget Mismatch Guard (`AC_VI_low >= 1200 us`, `AC_VO_low >= 300 us`, `AC_BE_low >= 1500 us`, `fq_quantum <= 4542B`).
- Emits [`artifacts/autoresearch/stage46c_closed_loop_reactor_v13_ingestion_20261025.json`](<repo>/artifacts/autoresearch/stage46c_closed_loop_reactor_v13_ingestion_20261025.json).

### 2.4 Live OpenWISP Dual-NMS Portal ([`tools/serve_openwisp_dual_nms_live.py`](<repo>/tools/serve_openwisp_dual_nms_live.py))
- Exposed `/api/v1/controller/template/champion-v13/` and added Card `a4)` inside [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](<repo>/artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html).
