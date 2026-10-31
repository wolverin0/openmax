<!-- doc-head: STAGE61A_UNIFIED_MULTIGEN_DETERMINISTIC_RF_COLLECTOR_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 61A — Unified Multi-Generation Deterministic RF Collector & Anti-Freeze Live Bench Verification

## 1. Objective & Scope (`T-S61A-UNIFIED-MULTIGEN-DETERMINISTIC-RF-COLLECTOR-LIVE-BENCH-VERIFICATION`)

Integrate the Stage 57A Closed-Loop Prometheus RF Exporter ([`tools/telemetry/futuramax_prometheus_rf_exporter.py`](../tools/telemetry/futuramax_prometheus_rf_exporter.py)) with the Stage 59A Zero-False-Positive Deterministic RF Monitor Verifier ([`tools/telemetry/deterministic_rf_monitor_verifier.py`](../tools/telemetry/deterministic_rf_monitor_verifier.py)) and execute a **2-Round Live Hardware Collection & Anti-Freeze Verification** across all **4 Ubiquiti hardware generations** on the physical bench:

1. **`OpenWrt 24.10.4` (`ath79` `QCA988x`)**: `LAP-120` AP (`198.18.0.43`) $\leftrightarrow$ `NanoStation 5AC Loco` STA (`198.18.0.47` / `198.18.0.67`, `PUBLIC_DEVICE_0096`)
2. **`airOS 8 XC / 2XC` (`QCA9558` + `QCA9880` / AirPrism)**: `Rocket 5AC Prism Gen2` STA (`198.18.0.64` / `198.18.0.68`, `PUBLIC_DEVICE_0048`) & `Rocket 2AC Prism` AP (`198.18.0.48`, `PUBLIC_DEVICE_0042`, `board.sysid=0xe2f2`)
3. **`airOS 6 XW` (`AR934x`)**: `LiteBeam M5` STA (`198.18.0.52` Over-The-Air via `LAP-120` `198.18.0.43`, `PUBLIC_DEVICE_0066`)
4. **`LTU v2.3.1` (`Broadcom/Beetle + EAB`)**: `LTU-Lite` AP (`PUBLIC_DEVICE_0046%27` / `198.18.0.61`) $\leftrightarrow$ `LTU-Lite` Remote STA (`198.18.0.72` Over-The-Air, `PUBLIC_DEVICE_0043`)

**Strict Isolation Boundary**: Neither `198.18.0.45` nor `198.18.0.46` (reserved for Stage 60A) nor any production Guarida IP (`10.10.100.x`) was touched during Stage 61A.

---

## 2. Live 2-Round Multi-Generation Telemetry & State-Machine Results

Executed via [`tools/telemetry/run_stage61a_unified_multigen_deterministic_rf_collector.py`](../tools/telemetry/run_stage61a_unified_multigen_deterministic_rf_collector.py) and recorded in [`artifacts/autoresearch/stage61a_unified_multigen_deterministic_rf_collector_20261026.json`](../artifacts/autoresearch/stage61a_unified_multigen_deterministic_rf_collector_20261026.json):

| Monitored Link ID | Hardware Generation | Station / Node MAC | Round 1 $\to$ Round 2 `survey_active_time_ms` | Round 1 $\to$ Round 2 `pkt_delta` (`TX+RX`) | AP-Local 5-Ping Round (`rcvd/sent`, Loss) | Live State (`evaluate_rf_monitor_window`) | Synthetic Frozen-Counter Self-Test (`s1` vs `s1`) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`Loco5AC_WA_OpenWrt`** | `OpenWrt 24.10.4` (`WA` `QCA9882`) | `PUBLIC_DEVICE_0096` | `2,766,803` $\to$ `2,794,915` ms (`+28,112` ms) | `+125` pkts | `5/5` (`0.0%` loss) | **`UP`** (`rf_fails=0`, `kuma_push=true`) | **`MONITOR_STALE_ERROR`** (`kuma_push=false`) |
| **`Rocket5AC_XC_airOS8`** | `airOS 8.7.11` (`XC` `QCA9880` AirPrism) | `PUBLIC_DEVICE_0048` | `2,766,803` $\to$ `2,794,915` ms (`+28,112` ms) | `+33` pkts | `5/5` (`0.0%` loss) | **`UP`** (`rf_fails=0`, `kuma_push=true`) | **`MONITOR_STALE_ERROR`** (`kuma_push=false`) |
| **`LiteBeamM5_XW_airOS6`** | `airOS 6.3.22` (`XW` `AR9342`) | `PUBLIC_DEVICE_0066` | `2,766,803` $\to$ `2,794,915` ms (`+28,112` ms) | `+93` pkts | `5/5` (`0.0%` loss) | **`UP`** (`rf_fails=0`, `kuma_push=true`) | **`MONITOR_STALE_ERROR`** (`kuma_push=false`) |
| **`Rocket2AC_2XC_airOS8`** | `airOS 8.7.11` (`2XC` `0xe2f2` AirPrism) | `PUBLIC_DEVICE_0042` | `136,674,940` $\to$ `136,703,400` ms (`+28,460` ms) | `+274` pkts | `5/5` (`0.0%` loss) | **`UP`** (`rf_fails=0`, `kuma_push=true`) | **`MONITOR_STALE_ERROR`** (`kuma_push=false`) |
| **`LTU_Lite_AF_LTU_OTA`** | `LTU v2.3.1` (`AF-LTU` Beetle + EAB) | `PUBLIC_DEVICE_0043` | `21,623,090` $\to$ `21,651,830` ms (`+28,740` ms) | `+14` pkts | `5/5` (`0.0%` loss) | **`UP`** (`rf_fails=0`, `kuma_push=true`) | **`MONITOR_STALE_ERROR`** (`kuma_push=false`) |

---

## 3. Hardware Control Readbacks & BusyBox Ping Finding

1. **BusyBox `ping` Sub-Second Interval Guard (`CONFIRMED`)**:
   - OpenWrt 24.10.4 default BusyBox `/bin/ping` rejects fractional `-i 0.2` intervals (`invalid number '0.2'`), which would cause a naive sub-second ping wrapper to report `0/5` received (`100%` loss).
   - Standard integer-interval AP-local probes (`ping -c 5 -W 1 -I br-lan <ip>`) combined with `iw dev phy0-ap0 station dump` (`tx_packets + rx_packets` delta) achieve `5/5` (`0.0%` loss) across all 3 `LAP-120` stations (`Loco 5AC`, `Rocket 5AC Prism`, `LiteBeam M5`).
2. **Stage 55A Champion v19 + Stage 50B LTU Champion Compliance (`CONFIRMED`)**:
   - `LAP-120` (`198.18.0.43`) and `Loco 5AC` (`198.18.0.47`) verified `champion_v19_compliant: true` (`limit_min=4542`, `limit_max=42392`, `hold_time=800`, `fq_quantum=4542/1514`, `dev_weight_tx_bias=2`, `active_alerts_count=0`).
   - `LTU-Lite AP` (`PUBLIC_DEVICE_0046%27`) verified `maxBD=0`, `duty_cycle=750`, `pb_boost=1`, `autoMcsCeiling=19` (`256-QAM 8x` Stage 50B Champion), and `SWQ_INTERVAL_EXTEND=2`.
3. **Unified Prometheus Exposition Output (`CONFIRMED`)**:
   - Exported `fmx_rf_monitor_status`, `fmx_rf_monitor_rf_fails`, `fmx_rf_monitor_kuma_push_allowed`, `fmx_rf_monitor_round_loss_pct`, `fmx_rf_monitor_avg_rtt_ms`, `fmx_ltu_eab_maxbd`, `fmx_ltu_auto_mcs_ceiling`, `fmx_ltu_pb_boost`, and `fmx_r2ac_prism_eth0_tx_packets` alongside the Stage 57A RF/AQM/BQL metric suite.
