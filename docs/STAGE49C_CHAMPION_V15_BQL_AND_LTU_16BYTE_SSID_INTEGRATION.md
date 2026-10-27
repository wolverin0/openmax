<!-- doc-head: STAGE49C_CHAMPION_V15_BQL_AND_LTU_16BYTE_SSID_INTEGRATION.md preserved document content -->
<!-- /doc-head -->

# Stage 49C (`T-S49C-GEM2-STAGE44A-CHAMPION-V15-AND-LTU-16BYTE-SSID-PACKAGER`) — Stage 44A Champion v15 Hardware BQL (`eth0=1000` vs `R5AC br0=256`) & Stage 45B LTU 16-Byte SSID + Full DCXO Integration

## 1. Executive Summary

Stage 49C (`T-S49C-GEM2-STAGE44A-CHAMPION-V15-AND-LTU-16BYTE-SSID-PACKAGER`) promotes **Stage 44A Champion v15** (`S44A-R5`: `M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000`) and the **Stage 45B LTU 16-Byte Beacon SSID + Alternating `freq_list` Full DCXO Guard** (`FMX-LTU` + `5500 5520 5500 5520`) across the FuturaMAX controller profiles, OpenWrt 24.10.4 ImageBuilder overlay packager, Closed-Loop Research Reactor (`M32` & `M33`), and OpenWISP 26.09 + Dual-UISP NMS Portal (`GET /api/v1/controller/template/champion-v15-aqm/` and Card `a7)`).

All work in Stage 49C was executed **100% offline in software/packaging with zero SSH connections to live radios**.

---

## 2. Empirical Hardware Laws Codified in Stage 49C

### 2.1 Stage 44A (`stage44a_m26_m27_napi_and_r5ac_txq_bench_20261025.json`)

| Round ID | Mechanism ID | Treatment Summary | Goodput (`A -> B`) | `p95` RTT (`A -> B`) | `p99` RTT (`A -> B`) | Dual IPTV / VoIP Loss | Pareto Score | Decision / Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `S44A-R1` | `M26_R5AC_BR0_TXQ_256_AND_ETH0_256_UNIFORM_SECTOR_TXQ` | `R5AC` `br0/ath0/eth0=256` & `budget=600` + **OpenWrt `eth0=256`** | `45.803 -> 44.894 Mbps` (**`-1.985%`**) | `97.380 -> 104.997 ms` (**`+7.822%`**) | `98.613 -> 104.997 ms` | `6.38%` / `0.00%` (VoIP jitter `+46.581%`) | `-4.7223%` | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**) |
| `S44A-R2` | `M27a_NAPI_DEFER_HARD_IRQS_2_GRO_TIMEOUT_100US` | `napi_defer_hard_irqs=2`, `gro_flush_timeout=100000` ns (`100 us`) | `46.040 -> 45.385 Mbps` (**`-1.423%`**) | `105.852 -> 96.483 ms` (**`-8.851%`**) | `105.852 -> 99.396 ms` | `8.16%` / `0.00%` | `+1.6752%` | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**) |
| `S44A-R3` | `M27b_DEV_WEIGHT_TX_BIAS_2_BUDGET_USECS_8000` | `dev_weight=48`, `dev_weight_tx_bias=2`, `netdev_budget=300`, `usecs=8000` | `47.441 -> 46.769 Mbps` (**`-1.416%`**) | `107.637 -> 104.715 ms` (**`-2.715%`**) | `111.469 -> 105.560 ms` | `5.89%` / `0.00%` | `-0.4664%` | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**) |
| `S44A-R4` | `M26_M27c_UNIFORM_TXQ_256_AND_TX_BIAS_2_BUDGET_12MS` | OpenWrt `eth0=256` + `R5AC br0=256` + `dev_weight_tx_bias=2` | `43.493 -> 28.646 Mbps` (**`-34.137%`**) | `132.595 -> 88.442 ms` (**`-33.299%`**) | `132.595 -> 92.217 ms` | `2.56%` / `0.00%` | `-22.4818%` | `RETAIN_CURRENT_CHAMPION` (**`REFUTED`**) |
| **`S44A-R5`** | **`M26b_PURE_R5AC_BR0_TXQ_256_OPENWRT_ETH0_1000`** | **Pure `R5AC` `br0/ath0/eth0=256` & `netdev_budget=600` + OpenWrt `eth0=1000` BQL & `br-lan/phy0-ap0*=256`** | **`32.998 -> 35.354 Mbps` (`+7.140%`)** | **`85.782 -> 82.678 ms` (`-3.618%`)** | **`97.689 -> 85.123 ms` (`-12.863%`)** | **`0.00%` / `0.00%`** | **`+8.4063%`** | **`PROMOTE_NEW_CHAMPION` (`CONFIRMED` Champion v15)** |

- **Physical Causal Mechanism (`S44A-R1` vs `S44A-R5`)**:
  - On OpenWrt 24.10.4 (`Linux 6.6.110`), the `ag71xx` Ethernet MAC driver on `eth0` already enforces hardware **Byte Queue Limits (`BQL limit=54250/1780`)**. Shrinking `/sys/class/net/eth0/tx_queue_len` from `1000` to `256` (`S44A-R1`) prematurely drops burst Ethernet frames before BQL backpressure can regulate the qdisc, regressing goodput by `-1.99%` (`-1.985%`) and inflating p95 RTT by `+7.82%` (`+7.822%`).
  - Conversely, virtual software bridges (`br-lan` on OpenWrt; `br0` on `Rocket Prism 5AC Gen2` `airOS 8 XC`) and 4-addr WDS netdevs (`phy0-ap0*`) have **no hardware BQL**; leaving `Rocket Prism 5AC Gen2` `br0` at `tx_queue_len=1000` creates unthrottled software ring bloat. Bounding `Rocket Prism 5AC Gen2` `br0/ath0/eth0` to `256` with `net.core.netdev_budget=600` while preserving OpenWrt `eth0=1000` (`S44A-R5`) achieved **`+7.14%` goodput**, **`-3.62%` p95 RTT**, **`-12.86%` p99 RTT**, **`0.00%` Dual IPTV loss**, and **`0.00%` VoIP loss**.

### 2.2 Stage 45B (`stage45b_ltu_16byte_ssid_fmx_ltu_provision_20261025.json`)

1. **16-Byte Beacon SSID Truncation (`ame_core_beacon_update @ 0x007008` vs `slm_find_preferred_record @ 0x045e20`)**:
   - Ghidra reverse-engineering of `ame_core.ko` (`AF-LTU.v2.4.0`) proved that the AP beacon builder `ame_core_beacon_update @ 0x007008` copies at most **16 bytes** (`[s_beacon, #0x0e..0x1d]`) of the configured SSID into the over-the-air LTU beacon, whereas the CPE scanner `slm_find_preferred_record @ 0x045e20` runs a full-string `strcmp(beacon_ssid, prefer_ssid)`.
   - The previous 19-byte SSID `FuturaMAX-LTU-Bench` was truncated over the air to 16-byte `FuturaMAX-LTU-Be`, causing `strcmp` to fail permanently.
   - **Fix**: Enforced 7-byte SSID `FMX-LTU` (`1 <= len(ltu_ssid.encode('utf-8')) <= 16`).
2. **CPE `Quick TCXO` vs. Full `DCXO` Crystal Calibration (`cpeFsmStart @ 0x048000`)**:
   - When consecutive frequencies in `freq_list` are identical (`5500 5500 5500 5500`), `cpeFsmStart @ 0x048000` takes the `Quick TCXO` shortcut (`coarse=40 fine=32767`) instead of full `DCXO` crystal lock.
   - **Fix**: Enforced alternating adjacent frequencies `5500 5520 5500 5520` (`f[i] != f[i+1]`), plus `board_ssid=0xae08` `intmode=1`, achieving verified `Crystal Locked at Freq[5500]`.

---

## 3. Updated Modules & Generated Artifacts

1. **Controller Profiles & Guard**:
   - [`controller/wisp_iptv_ptmp_sector_optimizer.py`](../controller/wisp_iptv_ptmp_sector_optimizer.py)
   - [`controller/openwrt_ptmp_2cpe_aqm_profile.py`](../controller/openwrt_ptmp_2cpe_aqm_profile.py)
   - [`controller/airos_stock_champ_profile.py`](../controller/airos_stock_champ_profile.py)
   - Added `validate_stage44a_bql_eth0_and_ltu_16byte_ssid_guard(openwrt_eth0_txq, openwrt_br_wds_txq, r5ac_br0_txq, r5ac_netdev_budget, ltu_ssid, ltu_freq_list)`, `load_empirical_stage44a_and_stage45b_champion_v15_evidence()`, `render_openwrt_bql_eth0_r5ac_txq256_champion_v15_script()`, and `export_openwisp_bql_eth0_r5ac_txq256_champion_v15_netjson_template()`.
2. **OpenWrt 24.10.4 ImageBuilder Packager**:
   - [`firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py`](../firmware/openwrt/futuramax_openwrt_imagebuilder_packager.py)
   - [`controller/futuramax_openwrt_imagebuilder_packager.py`](../controller/futuramax_openwrt_imagebuilder_packager.py)
   - Added `render_uci_defaults_98_futuramax_champion_v15_aqm()` and `generate_stage49c_imagebuilder_champion_v15_manifest()`, writing [`artifacts/autoresearch/stage49c_imagebuilder_champion_v15_manifest_20261025.json`](../artifacts/autoresearch/stage49c_imagebuilder_champion_v15_manifest_20261025.json).
3. **Closed-Loop Research Reactor**:
   - [`tools/research/closed_loop_research_reactor.py`](../tools/research/closed_loop_research_reactor.py)
   - [`controller/closed_loop_research_reactor.py`](../controller/closed_loop_research_reactor.py)
   - Added `ingest_stage44a_and_stage45b_and_synthesize_m32_m33()`, synthesizing `M32` (`PB-050` Hardware BQL `eth0=1000` + `R5AC br0=256` Co-Design) and `M33` (`PB-051` LTU 16-Byte Beacon SSID + Alternating `freq_list` Full DCXO Calibration) into [`artifacts/autoresearch/stage49c_closed_loop_reactor_champion_v15_20261025.json`](../artifacts/autoresearch/stage49c_closed_loop_reactor_champion_v15_20261025.json).
4. **OpenWISP 26.09 + Dual-UISP NMS Portal & REST API**:
   - [`tools/nms/serve_openwisp_dual_nms_live.py`](../tools/nms/serve_openwisp_dual_nms_live.py)
   - [`tools/serve_openwisp_dual_nms_live.py`](../tools/serve_openwisp_dual_nms_live.py)
   - [`artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html`](../artifacts/dashboard/OPENWISP_DUAL_NMS_PORTAL.html)
   - Exposed `/api/v1/controller/template/champion-v15-aqm/` and rendered Card `a7)` in `OPENWISP_DUAL_NMS_PORTAL.html`.
