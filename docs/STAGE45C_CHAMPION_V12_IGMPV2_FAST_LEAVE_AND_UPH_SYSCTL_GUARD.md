<!-- doc-head: STAGE45C_CHAMPION_V12_IGMPV2_FAST_LEAVE_AND_UPH_SYSCTL_GUARD.md preserved document content -->
<!-- /doc-head -->

# Stage 45C — Champion v12 WDS Fast-Leave, Single-Querier IGMPv2 & `ubnt_poll_host.ko` Sysctl Clobber Guard

**Task ID**: `T-S45C-GEM2-CHAMPION-V12-WDS-FAST-LEAVE-AND-UPH-BUFFER-CLOBBER-GUARD`  
**Stage**: `45C`  
**Date**: `2026-10-25`  
**Status**: `CONFIRMED` (`S39A-R3` Stage 39A Champion v12 promoted across OpenWISP NetJSON, ImageBuilder 24.10.4 First-Boot/Hotplug, and Closed-Loop Reactor)

---

## 1. Executive Summary & Two Physical Hardware Discoveries (`Stage 39A`)

In [`artifacts/autoresearch/stage39a_m19_m20_igmp_fast_leave_bench_20261025.json`](../artifacts/autoresearch/stage39a_m19_m20_igmp_fast_leave_bench_20261025.json) and [`docs/STAGE39A_M19_M20_IGMP_FAST_LEAVE_AND_MCAST_STALL_BENCHMARK.md`](STAGE39A_M19_M20_IGMP_FAST_LEAVE_AND_MCAST_STALL_BENCHMARK.md), three physical 3-CPE Triple-Play bench rounds (`S39A-R1`, `S39A-R2`, `S39A-R3`) uncovered two critical low-level kernel/driver interactions:

1. **Shared `sysctl_table->data` Buffer Clobber in `ubnt_poll_host.ko` (`airOS 8` `Rocket Prism 5AC Gen2` `.198`) — `CONFIRMED`**:
   - In `S39A-R1`, writing `echo 1 > /proc/sys/dev/uph_wifi0/voip_bias` *after* `echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` silently overwrote `ff_mcast_airtime_limit` from `5` down to `1` (`"uph_wifi0/ff_mcast_airtime_limit": 1` in all 3 Arm B readback snapshots).
   - **Root Cause**: All `/proc/sys/dev/uph_wifi0/*` entries in `ubnt_poll_host.ko` share a single 16-integer `sysctl_table->data` vector.
   - **Mandatory Guard (`M24`)**: Always write `echo 5 > /proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit` **LAST** and omit `voip_bias` writes on 5 GHz WDS stations.

2. **IGMPv2 Single-Querier & Zero-Flush WDS Fast-Leave Discipline (`S39A-R3` Stage 39A Champion v12) — `CONFIRMED`**:
   - **`S39A-R1` (`REFUTED`)**: Upgrading `multicast_igmp_version` to `3` and enabling `multicast_snooping=1` on CPE bridges caused Linux bridges to inject `72`-byte `DSCP CS6` (`tid7_ac0` `WMM AC_VO`) IGMPv3 query bursts during active Triple-Play windows (`-4.560%` goodput, `+12.729%` p95 RTT).
   - **`S39A-R2` (`REFUTED`)**: Mid-round writes to `bridge/multicast_snooping` and `tc qdisc replace dev ath0 root fq_codel` flushed bridge MDB and qdisc state (`-0.700%` goodput, `+11.736%` p95 RTT, `-28.254%` VoIP jitter).
   - **`S39A-R3` (`M19c_M20c_CLEAN_WDS_FAST_LEAVE_AND_UPH_MCAST_LIMIT` — Stage 39A Champion v12, `CONFIRMED`)**:
     - Enforcing `multicast_igmp_version=2`, AP `multicast_querier=1`, CPE `multicast_querier=0`, AP WDS `phy0-ap0*` `multicast_fast_leave=1` + `multicast_to_unicast=1`, CPE `brif/*/multicast_fast_leave=1`, and writing `ff_mcast_airtime_limit=5` **LAST** on `.198` achieved:
       - **Aggregate Goodput**: `48.949 Mbps -> 51.819 Mbps` (**`+5.863%`**)
       - **Loaded p95 RTT**: `113.749 ms -> 107.651 ms` (**`-5.361%`**)
       - **Loaded p50 RTT**: `49.605 ms -> 45.266 ms` (**`-8.747%`**)
       - **Pareto Score Delta**: **`+7.740%`** (`PROMOTE_NEW_CHAMPION`)
       - **Dual 1080p60 IPTV Loss (`tid4_ac1` `AC_VI`)**: **`0 / 5,669` (`0.00%`)**
       - **VoIP Loss (`tid6_ac0` `AC_VO`)**: **`0 / 1,199` (`0.00%`)**

---

## 2. Updated Modules & Artifacts

| Component | File / Symbol | Description |
| :--- | :--- | :--- |
| **WISP IPTV Optimizer & NetJSON v12** | [`controller/wisp_iptv_ptmp_sector_optimizer.py`](../controller/wisp_iptv_ptmp_sector_optimizer.py) | Added `load_empirical_stage39a_champion_v12_evidence()`, `render_openwrt_wds_fast_leave_champion_v12_script()`, and `export_openwisp_wds_fast_leave_champion_v12_netjson_template()` |
| **OpenWrt 24.10.4 ImageBuilder v12** | [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](../firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py) | Updated `render_hotplug_99_futuramax_wds_dms()` with Single-Querier IGMPv2 (`querier=1` on AP, `querier=0` on CPE), added `render_uci_defaults_98_futuramax_champion_v12_aqm()` and `generate_stage45c_imagebuilder_champion_v12_manifest()` |
| **Closed-Loop Research Reactor v12** | [`tools/research/closed_loop_research_reactor.py`](../tools/research/closed_loop_research_reactor.py) | Enforced `ff_mcast_airtime_limit=5` written last in `M19` and added `ingest_stage39a_champion_v12_and_synthesize_m24_m25()` synthesizing `M24` and `M25` |
| **OpenWISP Dual-NMS Portal** | [`tools/serve_openwisp_dual_nms_live.py`](../tools/serve_openwisp_dual_nms_live.py) | Exposed `openwisp_wds_fast_leave_champion_v12_template` at `/api/v1/controller/template/champion-v12/` and rendered Card `a3)` in [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](../artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html) |
| **Verification Suite** | [`tests/test_stage45c_champion_v12_integration.py`](../tests/test_stage45c_champion_v12_integration.py) | End-to-end tests verifying Champion v12 NetJSON, ImageBuilder manifest, Reactor `M24/M25` synthesis, and `ubnt_poll_host.ko` ordering guard |
