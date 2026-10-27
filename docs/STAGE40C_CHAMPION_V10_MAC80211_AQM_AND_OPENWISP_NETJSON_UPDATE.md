<!-- doc-head: STAGE40C_CHAMPION_V10_MAC80211_AQM_AND_OPENWISP_NETJSON_UPDATE.md preserved document content -->
<!-- /doc-head -->

# Stage 40C — Stage 36A Champion v10 Direct `mac80211` `aqm` & `AC_BE=1500/3000` OpenWISP NetJSON Integration

**Task ID**: `T-S40C-GEM2-POP-CMAF-MICROCACHE-AND-CHAMPION-V10-AQM-NETJSON-INTEGRATION`  
**Updated Optimizer & Template Generator**: [`controller/wisp_iptv_ptmp_sector_optimizer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py)  
**Hardware Benchmark Source**: [`artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json) & [`docs/STAGE36A_LIVE_IPTV_AC_VI_AND_DMS_PTMP_BENCHMARK.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE36A_LIVE_IPTV_AC_VI_AND_DMS_PTMP_BENCHMARK.md)

---

## 1. Critical Physical Hardware Finding (`Stage 36A: S36A-R1 vs S36A-R2`)

In [`artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json), live counterbalanced `A1 -> B1 -> A2 -> B2` bench testing on the 3-CPE 5 GHz sector (`LAP-120` `.20` + `NanoStation 5AC Loco` `.250` + `Rocket Prism 5AC Gen2` `.198` + `LiteBeam M5` `.251`) under simultaneous bulk TCP + `3.5 Mbps` HEVC 1080p60 IPTV load established two critical physical facts:

1. **Why `S36A-R1` (`AC_BE=1000/2000`, `aql_threshold=4000`) Was Refuted (`-6.225%` Goodput)**:
   - Lowering `AC_BE` (`TID 0`, `AC 2`) from `1500/3000 us` down to `1000/2000 us` (`aql_threshold=4000 us`) starved 2-MTU (`2 × 1514B = 3028B`) TCP A-MPDU aggregation (`69.077 -> 64.777 Mbps`, `-6.225%`), because 2-MTU TCP frames plus RTS/CTS at `78 Mbps` require `~1,450 us` of airtime.
2. **Why `S36A-R2` (`Stage 36A Champion v10`: `AC_VI=1200/2400`, `AC_BE=1500/3000`, `thresh=5000` + Direct `mac80211` `aqm` Programming) Won `PROMOTE_NEW_CHAMPION`**:
   - On OpenWrt 24.10.4 (`Linux 6.6.110`), `/sys/kernel/debug/ieee80211/phy0/aqm` is a **single debugfs control file** (and `tc` is not installed by default on 64 MB RAM images). Writing directly to `/sys/kernel/debug/ieee80211/phy0/aqm`:
     ```sh
     echo fq_quantum 3028 > /sys/kernel/debug/ieee80211/phy0/aqm
     echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
     ```
     while preserving `AC_BE=1500/3000 us` (`aql_threshold=5000 us`) and isolating IPTV in `WMM AC_VI` (`TID 4 AC 1`, `1200/2400 us`) achieved:
     - **Aggregate 3-CPE Sector Goodput**: **`+2.513%` (`55.352 -> 56.743 Mbps`, peak `57.756 Mbps`)**
     - **Loaded Sector `p95` RTT**: **`-3.375%` (`79.268 -> 76.593 ms`)**
     - **Loaded Sector `p99` RTT**: **`-8.990%` (`94.423 -> 85.934 ms`)**
     - **IPTV Delivery (`tid4_ac1`)**: **`0 / 3,980` lost datagrams (`0.00%` loss, `1.591–2.510 ms` jitter)**

---

## 2. OpenWISP IPTV NetJSON Template Update (`Stage 36A Champion v10`)

[`render_openwrt_iptv_ac_vi_qos_and_dms_script`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L369-L443) and [`export_openwisp_iptv_netjson_template`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py#L446-L553) in [`controller/wisp_iptv_ptmp_sector_optimizer.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/wisp_iptv_ptmp_sector_optimizer.py) now emit the exact hardware-verified `Stage 36A Champion v10` sequence (deterministic SHA-256 `a0a3ef9ebd0be07ec3321b1350c4948d4c4bc36a2775503d3ba46bdd9caf9311`):

```sh
echo fq_quantum 3028 > /sys/kernel/debug/ieee80211/phy0/aqm
echo fq_memory_limit 4194304 > /sys/kernel/debug/ieee80211/phy0/aqm
echo 1 > /sys/class/net/br-lan/bridge/multicast_snooping
echo 1 > /sys/class/net/br-lan/bridge/multicast_querier
for p in /sys/devices/virtual/net/br-lan/brif/phy0-ap0*/multicast_to_unicast; do echo 1 > $p 2>/dev/null || true; done
echo 5000 > /sys/kernel/debug/ieee80211/phy0/aql_threshold
echo '0 600 1200' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '1 1200 2400' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '2 1500 3000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
echo '3 500 1000' > /sys/kernel/debug/ieee80211/phy0/aql_txq_limit
```

---

## 3. Verification

```bash
python -m pytest tests/test_stage36c_wisp_iptv_optimizer.py tests/test_stage37c_realistic_capacity_and_iptv.py tests/test_stage38c_openwisp_portal_iptv_tab.py tests/test_stage39c_iptv_qoe_exporter.py tests/test_stage40c_champion_v10_aqm_netjson.py -v
```
