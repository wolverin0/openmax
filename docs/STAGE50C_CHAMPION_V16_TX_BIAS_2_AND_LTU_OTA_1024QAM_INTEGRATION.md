<!-- doc-head: STAGE50C_CHAMPION_V16_TX_BIAS_2_AND_LTU_OTA_1024QAM_INTEGRATION.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 50C — Stage 46A Champion v16 (`dev_weight_tx_bias=2` @ Full `netdev_budget=600` + Dynamic Kernel `dql` BQL) & Stage 47B LTU OTA 1024-QAM MIMO Integration

**Task ID**: `T-S50C-GEM2-STAGE46A-CHAMPION-V16-TX-BIAS-2-AND-STAGE47B-LTU-OTA-PACKAGER`  
**Stage**: `50C`  
**Safety Policy**: Offline packaging, profile validation, closed-loop reactor synthesis, and OpenWISP Dual-NMS portal integration (`0` SSH connections, `0` flash writes, live radios untouched).

---

## 1. Empirical Hardware Evidence Summary

### 1.1 Stage 46A (`artifacts/autoresearch/stage46a_m28_m29_bql_and_tx_bias_bench_20261025.json`)
- **`S46A-R3` (`M29b_PURE_DEV_WEIGHT_TX_BIAS_2_AT_FULL_BUDGET_600`, `PROMOTE_NEW_CHAMPION` — Stage 46A Champion v16 `CONFIRMED`)**:
  - Isolating `net.core.dev_weight_tx_bias = 2` on `LAP-120` (`198.18.0.43`) and `NanoStation 5AC Loco` (`198.18.0.47`) while preserving full `net.core.netdev_budget = 600`, `net.core.dev_weight = 64`, `net.core.netdev_budget_usecs = 20000`, `net.core.netdev_max_backlog = 1000`, and `/sys/class/net/eth0/tx_queue_len = 1000` prioritizes `ath10k` HTT TX completion ring cleanup without the `-1.416%` goodput penalty caused by halving `netdev_budget = 300` in `S44A-R3`:
    - **Aggregate Sector Goodput**: `39.642 -> 41.025 Mbps` (**`+3.489%`**)
    - **Loaded `p95` RTT**: `90.986 -> 85.262 ms` (**`-6.291%`**)
    - **Loaded `p99` RTT**: `95.257 -> 89.434 ms` (**`-6.113%`**)
    - **Dual 1080p60 IPTV (`AC_VI`) Jitter**: `2.412 -> 1.985 ms` (**`-17.703%`**)
    - **VoIP (`AC_VO`) Jitter**: `2.689 -> 2.549 ms` (**`-5.206%`**)
    - **Pareto Score Delta**: **`+5.6906%`**
- **`S46A-R1` (`M28`, `REFUTED`) & `S46A-R5` (`M28b`, `REFUTED`) — Static `ag71xx` BQL Override Penalty**:
  - Manually bounding `ag71xx` `eth0` `byte_queue_limits` (`limit_max=24576, limit_min=3028, hold_time=500` in `S46A-R1`; `limit_max=65536, limit_min=4542, hold_time=1000` in `S46A-R5`) clipped bulk TCP bursts by **`-0.977%`** (`42.283 -> 41.870 Mbps`) to **`-10.267%`** (`36.066 -> 32.363 Mbps`) compared to Linux kernel `dql`'s self-tuning dynamic BQL (`limit_min=0, limit_max=1879048192, hold_time=1000` ms).
- **`S46A-R2` (`M29a`, `REFUTED`) & `S46A-R6` (`M29c`, `REFUTED`) — 400 MHz AR934x `LiteBeam M5` `netdev_budget=600` Softirq Penalty**:
  - Raising `net.core.netdev_budget = 600` on the single-core 400 MHz AR934x `LiteBeam M5` (`.251`, `airOS 6 XW`) inflated loaded `p95` RTT by **`+8.839%`** (`91.517 -> 99.606 ms`) and Dual IPTV jitter by **`+66.23%`**, proving 400 MHz AR934x `airOS 6` must retain `net.core.netdev_budget = 300`.

### 1.2 Stage 47B (`artifacts/autoresearch/stage47b_boca7_live_flash_and_ota_verification_20261025.json`)
- **Live OTA Association & 1024-QAM MIMO Data-Plane Verification (`CONFIRMED`)**:
  - Applying the 7-byte SSID `FMX-LTU` (`<= 16` bytes for `ame_core_beacon_update @ 0x007008` and `slm_find_preferred_record @ 0x045e20` `strcmp`), alternating `freq_list` (`5500 5520 5500 5520`) for full DCXO calibration in `cpeFsmStart @ 0x048000`, `board_ssid=0xae08` `intmode=1`, and `+15 dBm` TX power (`28 dBm EIRP`) achieved:
    - **`5.1s` OTA Association**: `AP-PTMP(Run)` (`LTU-1` `PUBLIC_DEVICE_0045`, `198.18.0.63`) $\leftrightarrow$ `CPE-PTMP(Run)` (`LTU-2` `PUBLIC_DEVICE_0043`, `198.18.0.118`)
    - **Timing Advance & Modulation**: `TA=235`, `SpectrumEfficient=1535` (AP) / `1319` (CPE) **1024-QAM MIMO**
    - **20 MHz @ 5500 MHz Throughput**: **`61.4 Mbps` mean / `79.1 Mbps` peak DL**, **`41.9 Mbps` mean / `42.4 Mbps` peak UL** (**`103.3 Mbps` aggregate**, **`5.165 bps/Hz`**)
    - **ICMP Latency & Persistence**: `3.16 ms` min / `5.25 ms` avg RTT (`0.0%` loss), persisted to SPI flash via `cfgmtd -w -p /etc/`.

---

## 2. Implemented Stage 50C Components

1. **Profile & Safety Guards (`controller/openwrt_ptmp_2cpe_aqm_profile.py`, `controller/airos_stock_champ_profile.py`, `controller/wisp_iptv_ptmp_sector_optimizer.py`)**:
   - `validate_stage46a_tx_bias_2_dynamic_bql_and_lbm5_budget_guard(dev_weight_tx_bias, netdev_budget, ag71xx_bql_mode, lbm5_netdev_budget)` enforcing:
     - `dev_weight_tx_bias == 2` at full `netdev_budget == 600` on OpenWrt
     - dynamic kernel `dql` BQL on `ag71xx` `eth0` (rejecting static `limit_max` overrides)
     - `lbm5_netdev_budget == 300` on 400 MHz AR934x `airOS 6`
   - `load_empirical_stage46a_and_stage47b_champion_v16_evidence()`
   - `render_openwrt_tx_bias_2_dynamic_bql_champion_v16_script()`
   - `export_openwisp_tx_bias_2_dynamic_bql_champion_v16_netjson_template()`
2. **OpenWrt 24.10.4 ImageBuilder First-Boot Packager (`controller/futuramax_openwrt_imagebuilder_packager.py` & `firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`)**:
   - `render_uci_defaults_98_futuramax_champion_v16_aqm()`
   - `generate_stage50c_imagebuilder_champion_v16_manifest()` -> `artifacts/autoresearch/stage50c_imagebuilder_champion_v16_manifest_20261025.json`
3. **Closed-Loop Research Reactor (`controller/closed_loop_research_reactor.py` & `tools/research/closed_loop_research_reactor.py`)**:
   - `ingest_stage46a_and_stage47b_and_synthesize_m34_m35()` -> `artifacts/autoresearch/stage50c_closed_loop_reactor_champion_v16_20261025.json` (`M34` & `M35`)
4. **OpenWISP 26.09 + Dual-UISP Portal & REST API (`tools/nms/serve_openwisp_dual_nms_live.py` & `tools/serve_openwisp_dual_nms_live.py`)**:
   - `GET /api/v1/controller/template/champion-v16-aqm/`
   - Card `a8)` in `artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`
