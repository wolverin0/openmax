<!-- doc-head: STAGE48C_CHAMPION_V14_SYSFS_TXQ256_IMAGEBUILDER_AND_REACTOR.md preserved document content -->
<!-- /doc-head -->

# Stage 48C — Stage 42A Champion v14 (`S42A-R5`) Pure Sysfs WDS `tx_queue_len=256`, ImageBuilder Packager & Closed-Loop Reactor `M30..M31`

- **Task ID**: `T-S48C-GEM2-STAGE42A-CHAMPION-V14-SYSFS-TXQ256-PACKAGER-AND-REACTOR`
- **Stage**: `48C`
- **Date**: `2026-10-25`
- **Hardware Access**: Strictly `0` SSH connections (100% offline controller, ImageBuilder packager, Closed-Loop Reactor, and OpenWISP Dual-NMS Portal integration; all live bench radios left untouched).

---

## 1. Executive Summary & Causal Physics (`S42A-R3` / `S42A-R4` vs. `S42A-R5` Champion v14)

In Stage 42A ([`artifacts/autoresearch/stage42a_m24_m25_airos6_mcast_and_txq_bench_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage42a_m24_m25_airos6_mcast_and_txq_bench_20261025.json)), rounds `S42A-R2` (`tx_queue_len=128`), `S42A-R3` (`tx_queue_len=256`), and `S42A-R4` (`tx_queue_len=64`) were initially tested alongside `net.core.netdev_max_backlog=2000`:
- **`S42A-R2` (`tx_queue_len=128` + `backlog=2000`)**: `REFUTED` (`+16.716%` p95 RTT, `2.17%` VoIP loss) — starving `mac80211` internal per-TID TXQs.
- **`S42A-R4` (`tx_queue_len=64` + `backlog=2000`)**: `REFUTED` (`-3.903%` goodput, `+29.472%` p95 RTT, `0.75%` VoIP loss) — extreme netdev TXQ starvation.
- **`S42A-R3` (`tx_queue_len=256` + `backlog=2000`)**: `REFUTED` (`-1.643%` goodput, `+2.378%` p95 RTT, `0.58%` VoIP loss) — coupling `tx_queue_len=256` with `net.core.netdev_max_backlog=2000` shifted packets out of the netdev ring into single-core MIPS 74Kc softirq backlog bloat.

**`S42A-R5` (`Stage 42A Champion v14` — `M24e_M25e_PURE_SYSFS_WDS_TXQ_256_AND_LBM5_BR0_TXQ_256`, `CONFIRMED` / `PROMOTE_NEW_CHAMPION`)** isolated **pure direct sysfs `tx_queue_len=256`** across `br-lan` and `phy0-ap0*` on `LAP-120` (`.20`) and `br-lan`/`phy0-sta0` on `Loco 5AC` (`.250`) (`M25e`) plus clean unpolled `LiteBeam M5` (`.251`, `airOS 6` `XW`) `br0/ath0/eth0 tx_queue_len=256` + `ubnt_ewma_delegate_on=1` (`M24e`) while keeping **`net.core.netdev_max_backlog=1000`** and **`net.ipv4.tcp_early_retrans=3`**:

| Metric (3-CPE 5 GHz Hybrid Sector + 590 pps Triple-Play) | Arm A (Champion v13 `tx_queue_len=1000`) | Arm B (`S42A-R5` Champion v14 `tx_queue_len=256` + `backlog=1000`) | Delta | Verdict |
| :--- | :---: | :---: | :---: | :---: |
| **Aggregate TCP Goodput** | `45.331 Mbps` | **`46.785 Mbps`** | **`+3.208%` (`+1.454 Mbps`)** | **CONFIRMED** |
| **Loaded ICMP p95 RTT** | `104.429 ms` | **`96.161 ms`** | **`-7.917%` (`-8.268 ms`)** | **CONFIRMED** |
| **Loaded ICMP p50 RTT** | `51.148 ms` | **`48.940 ms`** | **`-4.317%`** | **CONFIRMED** |
| **Dual 1080p60 IPTV Loss (`470 pps` `tid4_ac1`)** | `0 / 5,642 (0.00%)` | **`0 / 5,640 (0.00%)`** | **`0.00%` Loss** | **CONFIRMED** |
| **Dual 1080p60 IPTV Jitter** | `1.902 ms` | **`1.667 ms`** | **`-12.355%`** | **CONFIRMED** |
| **G.711 VoIP Loss (`120 pps` `tid6_ac0`)** | `0 / 1,200 (0.00%)` | **`0 / 1,200 (0.00%)`** | **`0.00%` Loss** | **CONFIRMED** |
| **G.711 VoIP Jitter** | `2.429 ms` | **`2.232 ms`** | **`-8.110%`** | **CONFIRMED** |
| **mac80211 `tid0_ac2` Overlimit Drops** | `0` | **`0`** | **`0` Drops** | **CONFIRMED** |
| **Pareto Composite Score Delta** | — | — | **`+5.9786%`** | **`PROMOTE_NEW_CHAMPION` (v14)** |

---

## 2. Delivered Components & Artifacts

1. **Controller Profile & Guard Upgrades**:
   - [`controller/wisp_iptv_ptmp_sector_optimizer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py), [`controller/openwrt_ptmp_2cpe_aqm_profile.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/openwrt_ptmp_2cpe_aqm_profile.py), and [`controller/airos_stock_champ_profile.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/airos_stock_champ_profile.py):
     - Updated [`validate_openwrt_netdev_txq_and_airos6_unpolled_guard`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L1721-L1786) so `tx_queue_len=256` is accepted when paired with `netdev_max_backlog <= 1500` (`1000`) and `tcp_early_retrans == 3`, while rejecting `tx_queue_len < 256` (`64`, `128`), `netdev_max_backlog > 1500` (`2000`), or unpolled `airOS 6` `XW` `ubnt_poll` `no_ack_rate != 0` / `txop_params != '0 0'`.
     - Added [`load_empirical_stage42a_champion_v14_evidence`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L1904-L1946), [`render_openwrt_sysfs_txq256_champion_v14_script`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L1949-L2031), and [`export_openwisp_sysfs_txq256_champion_v14_netjson_template`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L2034-L2147).
2. **OpenWrt 24.10.4 ImageBuilder Packager (`v14` UCI-Defaults & Hotplug)**:
   - [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py) and [`controller/futuramax_openwrt_imagebuilder_packager.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/futuramax_openwrt_imagebuilder_packager.py):
     - Added `render_uci_defaults_98_futuramax_champion_v14_aqm()` and updated `render_hotplug_99_futuramax_wds_dms()` to write `256` directly into `/sys/class/net/br-lan/tx_queue_len` and `/sys/class/net/phy0-ap0*/tx_queue_len` upon boot and dynamic 4-addr WDS station re-association.
     - Generated [`artifacts/autoresearch/stage48c_imagebuilder_champion_v14_manifest_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage48c_imagebuilder_champion_v14_manifest_20261025.json).
3. **Closed-Loop Research Reactor (`M30..M31` Synthesis)**:
   - [`tools/research/closed_loop_research_reactor.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py) and [`controller/closed_loop_research_reactor.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/closed_loop_research_reactor.py):
     - Added `ingest_stage42a_r5_champion_v14_and_synthesize_m30_m31()` ingesting `S42A-R1..R5` and synthesizing `M30` (`PB-048` Pure Direct Sysfs WDS `tx_queue_len=256` & `netdev_max_backlog=1000` Co-Design) and `M31` (`PB-049` Unpolled `airOS 6` `XW` `br0/ath0/eth0 txqueuelen=256` & `ubnt_ewma_delegate_on=1`).
     - Generated [`artifacts/autoresearch/stage48c_closed_loop_reactor_champion_v14_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage48c_closed_loop_reactor_champion_v14_20261025.json).
4. **OpenWISP Dual-NMS Portal & Command Center Integration**:
   - [`tools/serve_openwisp_dual_nms_live.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/serve_openwisp_dual_nms_live.py), [`tools/nms/serve_openwisp_dual_nms_live.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/nms/serve_openwisp_dual_nms_live.py), and [`tools/serve_command_center_live.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/serve_command_center_live.py):
     - Exposed `/api/v1/controller/template/champion-v14-aqm/` and rendered Card `a6)` in [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html).
