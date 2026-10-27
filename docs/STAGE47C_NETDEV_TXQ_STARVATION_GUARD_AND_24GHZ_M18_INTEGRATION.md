<!-- doc-head: STAGE47C_NETDEV_TXQ_STARVATION_GUARD_AND_24GHZ_M18_INTEGRATION.md preserved document content -->
<!-- /doc-head -->

# Stage 47C — Netdev `tx_queue_len=1000` Starvation Guard, Unpolled `airOS 6` `XW` Contention Guard & 2.4 GHz `R2AC` `M18` Integration (`T-S47C-GEM2-STAGE40A-42A-NETDEV-TXQ-GUARD-AND-24GHZ-M18-PACKAGER`)

- **Task ID**: `T-S47C-GEM2-STAGE40A-42A-NETDEV-TXQ-GUARD-AND-24GHZ-M18-PACKAGER`
- **Owner**: `orca:gemini-lane2`
- **Source Physical Benchmarks**:
  - [`artifacts/autoresearch/stage42a_m24_m25_airos6_mcast_and_txq_bench_20261025.json`](../artifacts/autoresearch/stage42a_m24_m25_airos6_mcast_and_txq_bench_20261025.json)
  - [`artifacts/autoresearch/stage40a_ltu_persistent_poststart_and_24ghz_bench_20261025.json`](../artifacts/autoresearch/stage40a_ltu_persistent_poststart_and_24ghz_bench_20261025.json)
- **Generated Stage 47C Artifacts**:
  - [`artifacts/autoresearch/stage47c_imagebuilder_txq1000_manifest_20261025.json`](../artifacts/autoresearch/stage47c_imagebuilder_txq1000_manifest_20261025.json)
  - [`artifacts/autoresearch/stage47c_closed_loop_reactor_s40a_s42a_ingestion_20261025.json`](../artifacts/autoresearch/stage47c_closed_loop_reactor_s40a_s42a_ingestion_20261025.json)
  - [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](../artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html)

---

## 1. Physical Hardware Discoveries (`Stage 42A` & `Stage 40A`)

### 1.1 Stage 42A: OpenWrt Netdev `tx_queue_len` Starvation & Unpolled `airOS 6` `XW` `ubnt_poll` Contention (`S42A-R1..R4`)
1. **BusyBox `ip link set txqueuelen` Silent Parser Bug**:
   - On OpenWrt 24.10.4 (`Linux 6.6.110`), BusyBox `ip link set dev br-lan txqueuelen 256` fails silently (`ip: either "dev" is duplicate, or "txqueuelen" is garbage`), leaving `/sys/class/net/br-lan/tx_queue_len` and `/sys/class/net/phy0-ap0*/tx_queue_len` at their kernel default of **`1000`**.
2. **Real Sysfs `tx_queue_len` Starvation Curve (`S42A-R2/R3/R4` — `REFUTED`)**:
   - When `tx_queue_len` was actually lowered via direct sysfs (`echo 128 > /sys/class/net/*/tx_queue_len` in `S42A-R2`, `256` in `S42A-R3`, `64` in `S42A-R4`) alongside `net.core.netdev_max_backlog=2000`, the Linux netdev Layer-2 queue tail-dropped high-priority `DSCP EF` VoIP (`100 pps`) packets *before* they could enter `mac80211`'s internal `wake_tx_queue` (`FQ_CoDel` + `AQL` `tid6_ac0`) scheduler:
     - **`tx_queue_len=64` (`S42A-R4`)**: `-3.903%` goodput, **`+29.472%` p95 RTT inflation** (`118.234 -> 153.081 ms`), `0.75%` VoIP loss.
     - **`tx_queue_len=128` (`S42A-R2`)**: **`+16.716%` p95 RTT inflation**, **`2.17%` (`2.7%` peak) VoIP loss**.
     - **`tx_queue_len=256` (`S42A-R3`)**: **`+2.378%` p95 RTT inflation**, **`0.58%` (`1.75%` peak) VoIP loss**.
     - **`tx_queue_len=1000` (`Champion v13` default)**: **`0.00%` VoIP loss (`0/1,200`)** and **`0.00%` Dual 1080p60 IPTV loss (`0/5,672`)**.
3. **Unpolled `airOS 6` `XW` `ubnt_poll` Contention (`S42A-R1` — `REFUTED`)**:
   - Enabling `txop_params='15 5'` and `no_ack_rate=1` in `/proc/sys/dev/ubnt_poll/` on `LiteBeam M5` (`.251`, `airOS 6 XW.v6.3.2`) while operating as an unpolled standard 802.11n WDS station caused **`-8.346%` (`-8.352%` vs baseline) sector goodput collapse** (`44.523 -> 40.807 Mbps`).

### 1.2 Stage 40A: 2.4 GHz `Rocket 2AC Prism` `M18` & `LTU` Persistent `rc.poststart` (`S40A-R1` & `S40A-R2`)
1. **`S40A-R1` (`Rocket 2AC Prism` `.253` + `NanoLoco M2` `.252` — `CONFIRMED`)**:
   - Writing `ff_mcast_airtime_limit=5` **LAST** (after `fixed_frame=1`, `cms_bias=6`, `voip_bias=6` to prevent the shared 16-integer `sysctl_table->data` vector overwrite in `ubnt_poll_host.ko`) + `multicast_igmp_version=2` (`IGMPv2=2`) + `multicast_fast_leave=1` + `tcp_wmem='4096 16384 524288'` (`512 KB`, avoiding the `-14.79%` starvation of `64 KB`) achieved:
     - **`-20.75%` loaded p95 RTT reduction** (`11.542 -> 9.147 ms`, `-2.298 ms`)
     - **`-15.32%` IPTV jitter reduction** (`0.4875 -> 0.4128 ms`)
     - **`0.00%` (`0/816`) IPTV packet loss** & **`0.00%` (`0/391`) VoIP packet loss**
2. **`S40A-R2` (`LTU-Lite` `LTU.afltu.v2.4.0` Persistent `/etc/persistent/rc.poststart` — `CONFIRMED`)**:
   - Persisting `air_fpga` RAM surgical patch + `ath0`-only `fq_codel limit 1024 flows 1024 quantum 1514 target 2.5ms interval 50ms noecn` across cold reboots (`cfgmtd -w -p /etc/`) achieved **`-45.66%` IPTV jitter**, **`-57.26%` VoIP jitter**, and **`-50.40%` loaded ping p95** with `0.00%` loss.

---

## 2. Implemented Stage 47C Architecture

1. **`validate_openwrt_netdev_txq_and_airos6_unpolled_guard()`** in [`controller/openwrt_ptmp_2cpe_aqm_profile.py`](../controller/openwrt_ptmp_2cpe_aqm_profile.py), [`controller/airos_stock_champ_profile.py`](../controller/airos_stock_champ_profile.py), and [`controller/wisp_iptv_ptmp_sector_optimizer.py`](../controller/wisp_iptv_ptmp_sector_optimizer.py):
   - Rejects `tx_queue_len < 512` on `br-lan`/`phy0-ap0*` (`NETDEV_TXQ_STARVATION_VIOLATION`).
   - Rejects `netdev_max_backlog > 1500` under Champion v13 (`NETDEV_MAX_BACKLOG_BLOAT_VIOLATION`).
   - Rejects unpolled `airOS 6` `XW` `ubnt_poll` `no_ack_rate != 0` or `txop_params != '0 0'` (`AIROS6_UNPOLLED_UBNT_POLL_CONTENTION_VIOLATION`).
2. **`export_r2ac_24ghz_m18_iptv_netjson_template()`** in [`controller/airos_stock_champ_profile.py`](../controller/airos_stock_champ_profile.py) and [`controller/wisp_iptv_ptmp_sector_optimizer.py`](../controller/wisp_iptv_ptmp_sector_optimizer.py):
   - Exports the 1-Click OpenWISP NetJSON template `FMX airos8_r2ac_24ghz_m18_iptv_voip_champion_v14` encoding `ff_mcast_airtime_limit=5` written last, `IGMPv2=2`, `multicast_fast_leave=1`, and `512 KB` `tcp_wmem`.
3. **OpenWrt ImageBuilder TXQ=1000 Preservation** in [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](../firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py) and [`controller/futuramax_openwrt_imagebuilder_packager.py`](../controller/futuramax_openwrt_imagebuilder_packager.py):
   - Updates `98-futuramax-champion-v13-aqm` and `99-futuramax-wds-dms` to explicitly write `1000` into `/sys/class/net/br-lan/tx_queue_len` and `/sys/class/net/phy0-ap0*/tx_queue_len` via sysfs (`0` broken BusyBox `ip link set txqueuelen` calls) and exports [`artifacts/autoresearch/stage47c_imagebuilder_txq1000_manifest_20261025.json`](../artifacts/autoresearch/stage47c_imagebuilder_txq1000_manifest_20261025.json).
4. **Closed-Loop Research Reactor (`M28` & `M29`)** in [`tools/research/closed_loop_research_reactor.py`](../tools/research/closed_loop_research_reactor.py) and [`controller/closed_loop_research_reactor.py`](../controller/closed_loop_research_reactor.py):
   - `ingest_stage40a_and_stage42a_and_synthesize_m28_m29()` ingests `S40A-R1`, `S40A-R2`, and `S42A-R1..R4`, synthesizing `M28` (`PB-046`) and `M29` (`PB-047`) into [`artifacts/autoresearch/stage47c_closed_loop_reactor_s40a_s42a_ingestion_20261025.json`](../artifacts/autoresearch/stage47c_closed_loop_reactor_s40a_s42a_ingestion_20261025.json).
5. **OpenWISP Dual-NMS Portal Endpoint (`/api/v1/controller/template/stage47c-guards/`)**:
   - Exposed in [`tools/serve_openwisp_dual_nms_live.py`](../tools/serve_openwisp_dual_nms_live.py), [`tools/nms/serve_openwisp_dual_nms_live.py`](../tools/nms/serve_openwisp_dual_nms_live.py), and [`tools/serve_command_center_live.py`](../tools/serve_command_center_live.py), and rendered as Card `a5)` in [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](../artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html).
