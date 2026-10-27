<!-- doc-head: STAGE41C_CLOSED_LOOP_REACTOR_CHAMPION_V10_SYNTHESIS.md preserved document content -->
<!-- /doc-head -->

# Stage 41C — Closed-Loop Research Reactor Ingestion (`Stage 34A -> Stage 35A Champion v9 -> Stage 36A Champion v10`) & Next-Wave Mechanisms `M18..M21`

**Task ID**: `T-S41C-GEM2-CLOSED-LOOP-REACTOR-STAGE35A-36A-CHAMPION-V10-AND-IPTV-INGESTION`  
**Reactor Module**: [`tools/research/closed_loop_research_reactor.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py)  
**Machine-Readable Receipt**: [`artifacts/autoresearch/stage41c_closed_loop_reactor_v10_ingestion_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage41c_closed_loop_reactor_v10_ingestion_20261025.json)  
**Persistent Discovery Queue**: [`artifacts/autoresearch/discovery_to_research_queue.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/discovery_to_research_queue.json)

---

## 1. Executive Summary

Stage 41C extends [`ClosedLoopResearchReactor`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py#L395-L495) and [`formulate_followup_queries`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py#L151-L392) via [`ingest_stage34a_35a_36a_champion_v10_and_synthesize_m18_m21`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/closed_loop_research_reactor.py#L758-L878) to ingest four empirical physical bench milestones into `artifacts/hyperresearch_vault/notes/empirical_feedback/` and [`artifacts/autoresearch/discovery_to_research_queue.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/discovery_to_research_queue.json):

| Bench Round | Profile ID | Tested Knob / Mechanism | Goodput (`A -> B`) | `p95` RTT (`A -> B`) | Empirical Verdict |
| :--- | :--- | :--- | :---: | :---: | :--- |
| **`S34A-R1`** | `r2ac_prism_ap` | `M15`: `/proc/sys/dev/uph_wifi0/ff_mcast_airtime_limit=5` (2.4 GHz) | `27.031 -> 28.989 Mbps` (**`+7.244%`**) | `21.184 -> 20.567 ms` (**`-2.913%`**) | **`PROMOTE_NEW_CHAMPION` (`HW_CONFIRMED`)** |
| **`S35A-R1`** | `openwrt_lap120_ptmp_multicpe_champion` | `M15_5GHz` (`Champion v9`): `br-lan` `multicast_snooping=1` + dynamic WDS `phy0-ap0*` `multicast_to_unicast=1` + `ff_mcast_airtime_limit=5` | `59.888 -> 60.909 Mbps` (**`+1.705%`**) | `76.834 -> 65.216 ms` (**`-15.121%`**) | **`PROMOTE_NEW_CHAMPION` (`HW_CONFIRMED`)** |
| **`S36A-R1`** | `openwrt_lap120_ptmp_multicpe_champion` | `M16_IPTV_AC_VI`: `AC_VI=1200/2400` + squeezing `AC_BE` to `1000/2000` (`thresh=4000`) | `69.077 -> 64.777 Mbps` (**`-6.225%`**) | `83.731 -> 72.552 ms` (**`-13.351%`**) | **`RETAIN_CURRENT_CHAMPION` (`HW_REFUTED_OR_BOUNDED` — starves 2-MTU TCP)** |
| **`S36A-R2`** | `openwrt_lap120_ptmp_multicpe_champion` | `M16b_IPTV_AC_VI_MAC80211_AQM` (`Champion v10`): direct `/sys/kernel/debug/ieee80211/phy0/aqm` (`fq_quantum=3028`, `fq_memory_limit=4194304`) + `AC_VI=1200/2400` + `AC_BE=1500/3000` (`thresh=5000`) | `55.352 -> 56.743 Mbps` (**`+2.513%`**) | `79.268 -> 76.593 ms` (**`-3.375%`**, `p99 -8.990%`, **`0/3,980` IPTV loss**) | **`PROMOTE_NEW_CHAMPION` (`HW_CONFIRMED`)** |

---

## 2. Synthesized Next-Wave Candidate Mechanisms (`M18..M21`)

1. **`M18` (`PB-036` — Direct `mac80211` `aqm` Packet Count Bounding `fq_limit=2048` + Per-TID `overlimit` Zero-Drop Guard)**:
   - Builds on `S36A-R2` (`fq_quantum 3028` and `fq_memory_limit 4194304`) by bounding total packet descriptors across `mac80211` TXQs (`echo fq_limit 2048 > /sys/kernel/debug/ieee80211/phy0/aqm`) to prevent descriptor exhaustion on 64 MB RAM `AR9342` APs during 32-CPE micro-bursts.
2. **`M19` (`PB-037` — Stock `airOS 8` `netconf` `WMM AC_VI` EDCA Contention Window & `TXOP` Tuning (`CWmin=7`, `CWmax=15`, `AIFSN=2`, `TXOP=3008 us`) + `ff_mcast_airtime_limit=5`)**:
   - Co-designs CPE-side `airOS 8` `WMM AC_VI` EDCA contention window parameters with AP-side `tid4_ac1` (`1200/2400 us`) and `voip_bias=6`.
3. **`M20` (`PB-038` — IGMPv3 Fast-Leave (`multicast_fast_leave=1`) + Dynamic 4-Addr WDS Port Querier Tightening on `br-lan`)**:
   - Eliminates stale `multicast_to_unicast=1` DMS stream replication during rapid IPTV channel zapping across dynamic `phy0-ap0.sta*` bridge ports.
4. **`M21` (`PB-039` — Closed-Loop Per-CPE ABR Feedback Clamping (`2.2 Mbps 1080p60 -> 1.5 Mbps 720p60 -> 0.9 Mbps 480p30`) Driven by `AC_VI` AQL & SINR)**:
   - Couples [`telemetry/iptv_qoe_and_ac_vi_sla_exporter.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/telemetry/iptv_qoe_and_ac_vi_sla_exporter.py) RFC 4445 MDI & `tid4_ac1` AQL telemetry directly to per-port `sch_fq maxrate` clamping (`3500kbit -> 1750kbit -> 1050kbit`).

---

## 3. Verification

```bash
python tools/research/closed_loop_research_reactor.py
python -m pytest tests/test_stage28_closed_loop_reactor.py tests/test_stage41c_reactor_v10_ingestion.py -v
```
