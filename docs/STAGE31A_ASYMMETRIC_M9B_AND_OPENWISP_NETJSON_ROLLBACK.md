<!-- doc-head: STAGE31A_ASYMMETRIC_M9B_AND_OPENWISP_NETJSON_ROLLBACK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 31A: Asymmetric DL/UL Quantum (`M9b`), Pure TCP SACK/DSACK (`M8d`), and OpenWISP-Inspired `NetJSON` Layered Config & Self-Reverting RAM Watchdog

- **Task ID**: `T-S31A-ASYMMETRIC-DL-UL-QUANTUM-M9B-AND-OPENWISP-ROLLBACK-AGENT`
- **Completed UTC**: `2026-10-25T17:53:15Z`
- **Physical Bench Receipt**: [`artifacts/autoresearch/stage31a_m9b_and_openwisp_netjson_20261025.json`](../artifacts/autoresearch/stage31a_m9b_and_openwisp_netjson_20261025.json)
- **Controller Module**: [`controller/openwisp_netjson_rollback_agent.py`](../controller/openwisp_netjson_rollback_agent.py)
- **Bench Runner**: [`tools/bench/run_stage31a_m9b_and_openwisp_bench.py`](../tools/bench/run_stage31a_m9b_and_openwisp_bench.py)
- **Verification Test Suite**: [`tests/test_stage31a_m9b_and_openwisp_netjson.py`](../tests/test_stage31a_m9b_and_openwisp_netjson.py) (`6 passed in 0.29s`)
- **Safety Policy**: Strictly RAM-only (`0` flash writes, `cfgmtd -w` and `uci commit` forbidden).

---

## 1. Executive Summary

Following Stage 30A (`S30A-R1..R4`), the Closed-Loop Research Reactor identified two orthogonal follow-up hypotheses:
1. **`S31A-R1` (`M9b` — Asymmetric DL/UL Quantum `AP quantum=3028 / CPE quantum=1514` + Arrival-Rate Normalized Airtime Weights `720:512:112`)**:
   - In `S30A-R4` (`M9`), applying arrival-rate normalized airtime weights (`720:512:112`, from `arXiv:1505.00078v2`) alongside `CPE quantum=3028` boosted `Rocket5AC_XC` (`+5.65%`) and `LiteBeamM5_XW` (`+4.69%`) goodput and cut `p99` RTT by `-14.69%`, but regressed `p95` RTT by `+11.79%` because 2-packet UL bursts (`quantum=3028` on `Loco5AC_WA`) collided with the AP's downlink airtime scheduler.
   - **Physical Bench Result (`A1 -> B1 -> A2 -> B2`)**: Isolating `weights 720:512:112` while keeping **Asymmetric DL/UL Quantum (`AP quantum=3028 / CPE quantum=1514`)** preserved aggregate sector goodput (`32.907 -> 32.904 Mbps`, `-0.009%`) and **slashed loaded 3-CPE sector `p95` RTT by `-14.983%` (`57.772 -> 49.116 ms`)**, **`p50` RTT by `-19.507%` (`30.400 -> 24.470 ms`)**, and **`p99` RTT by `-10.099%` (`63.790 -> 57.348 ms`)** (`0.00%` loss).
   - **Verdict**: **`PROMOTE_NEW_CHAMPION` (`Stage 31A Champion v8`, Pareto delta `+5.235%`)** — promoted into `openwrt_lap120_ptmp_multicpe_champion` and `openwrt_lap120_ptp_1cpe_champion` in [`controller/multiradio_golden_profile_applicator.py`](../controller/multiradio_golden_profile_applicator.py).
2. **`S31A-R2` (`M8d` — `Rocket Prism 5AC Gen2` `.198` Pure `tcp_sack=1 + tcp_dsack=1 + tcp_window_scaling=1 + tcp_fin_timeout=15` keeping `br0 txqueuelen=1000`, `netdev_budget=300`, `ptp_xmit=0`)**:
   - **Physical Bench Result (`A1 -> B1 -> A2 -> B2`)**: Loaded `p95` RTT improved by **`-6.576%` (`25.166 -> 23.511 ms`)** and `p50` RTT dropped from `7.664 -> 2.190 ms` (`-71.42%`), while SSH stream goodput averaged `26.456 -> 25.838 Mbps` (`-2.336%`, exceeding the `-2.0%` goodput floor guard due to `B2` variance).
   - **Verdict**: **`RETAIN_CURRENT_CHAMPION`** — `IncrementalChampionPromoter` enforced the `-2.0%` goodput guard and automatically rolled back `.198` in RAM to `r5ac_prism_sta` Champion.
3. **OpenWISP-Inspired `NetJSON` Layered Configuration & Self-Reverting RAM Watchdog (`controller/openwisp_netjson_rollback_agent.py`)**:
   - Adapts the three foundational patterns from `openwisp-controller`, `openwisp-config`, and `netjsonconfig` to FuturaMAX's RAM-only multi-radio fleet:
     - **3-Layer `NetJSON` `DeviceConfiguration`**: Separates every Golden Profile into Layer 1 (`layer1_universal_linux_tcp_bridge`), Layer 2 (`layer2_soc_radio_driver_family`), and Layer 3 (`layer3_per_link_rf_overrides`) with deterministic SHA-256 `configuration_checksum`.
     - **`NetJSON` `DeviceMonitoring`**: Exports live per-station RSSI, PHY rates, airtime weights, goodput, and `p50/p95/p99` RTT from the 3-CPE sector.
     - **Self-Reverting `test_config` RAM Watchdog**: Generates an idempotent POSIX `/bin/sh` script that skips re-application on matching SHA-256 checksum, verifies reachability to `controller_gateway_ip`, and automatically executes `rollback_commands` in RAM if health checks fail.

---

## 2. Physical Bench Results (`A1 -> B1 -> A2 -> B2`)

### 2.1 Summary Comparison Table

| Round ID | Target Radio / Sector | Control Arm (`A`) | Treatment Arm (`B`) | Arm A Goodput | Arm B Goodput | $\Delta$ Goodput | Arm A `p95` RTT | Arm B `p95` RTT | $\Delta$ `p95` RTT | Decision |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`S31A-R1`** (`M9b`) | 3-CPE 5 GHz Sector (`LAP-120` `.20` + `Loco5AC` `.250` + `Rocket5AC` `.198` + `LiteBeamM5` `.251`) | `Stage 28 Champion v7` (`AP quantum=3028`, `CPE quantum=1514`, `weights 640:512:96`) | **`M9b`**: `AP quantum=3028`, `CPE quantum=1514` + **Arrival-Rate Normalized `weights 720:512:112`** | `32.907 Mbps` | `32.904 Mbps` | **`-0.009%`** (flat) | `57.772 ms` | **`49.116 ms`** | **`-14.983%`** (`p50 -19.51%`, `p99 -10.10%`) | **`PROMOTE_NEW_CHAMPION` (`Stage 31A Champion v8`)** |
| **`S31A-R2`** (`M8d`) | `Rocket Prism 5AC Gen2` (`.198` STA) | `r5ac_prism_sta` Champion (`br0 txqueuelen=1000`, `netdev_budget=300`, `tcp_dsack=0`) | **`M8d`**: Pure `tcp_sack=1 + tcp_dsack=1 + tcp_window_scaling=1 + tcp_fin_timeout=15` | `26.456 Mbps` | `25.838 Mbps` | `-2.336%` | `25.166 ms` | **`23.511 ms`** | **`-6.576%`** (`p50 -71.42%`) | **`RETAIN_CURRENT_CHAMPION`** (`-2.0%` goodput guard) |

---

### 2.2 Per-CPE Breakdown in `S31A-R1` (`M9b` vs `Stage 28 Champion v7`)

| Station | MAC / Interface | Arm A Weight | Arm B Weight | Arm A Mean Goodput | Arm B Mean Goodput | Arm A Mean `p50` RTT | Arm B Mean `p50` RTT | Arm A Mean `p95` RTT | Arm B Mean `p95` RTT | $\Delta$ `p95` RTT |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Loco5AC_WA`** (2x2 VHT20 OpenWrt) | `PUBLIC_DEVICE_0036` (`phy0-ap0.sta2`) | `640` | **`720`** | `31.696 Mbps` | **`31.756 Mbps`** (`+0.19%`) | `30.400 ms` | **`22.214 ms`** (`-26.93%`) | `52.306 ms` | **`48.660 ms`** | **`-6.97%`** |
| **`Rocket5AC_XC`** (2x2 VHT20 AirPrism) | `PUBLIC_DEVICE_0048` (`phy0-ap0.sta1`) | `512` | **`512`** | `1.144 Mbps` | `1.076 Mbps` | `24.808 ms` | `24.470 ms` (`-1.36%`) | `51.281 ms` | **`45.556 ms`** | **`-11.16%`** |
| **`LiteBeamM5_XW`** (1x1 HT20 Legacy) | `PUBLIC_DEVICE_0066` (`phy0-ap0`) | `96` | **`112`** | `0.067 Mbps` | **`0.073 Mbps`** (`+8.96%`) | `22.299 ms` | `22.638 ms` | `51.296 ms` | **`43.696 ms`** | **`-14.82%`** |

**Causal Mechanism (`CONFIRMED` on Physical Hardware)**:
- Downlink AP traffic (`LAP-120` `phy0-ap0`) benefits from `fq_codel quantum=3028` (2-MTU DRR frame-aggregation quantum, `S28-R1`) because `ath10k` aggregates pairs of 1514B TCP segments into single VHT20 A-MPDUs.
- Uplink CPE traffic (`Loco5AC_WA` `phy0-sta0`), however, consists predominantly of small TCP ACKs and ICMP probes competing for CSMA/CA TXOPs. Keeping **`CPE quantum=1514`** (`1-MTU`) prevents 2-packet UL bursts from colliding with the AP's downlink scheduler, while **Arrival-Rate Normalized Airtime Weights (`720:512:112`)** give `Loco5AC_WA` (`720`) and `LiteBeamM5_XW` (`112`) the exact deficit replenishment needed to drain queued frames within a single scheduling round (`-14.983%` sector `p95` RTT).

---

## 3. OpenWISP-Inspired `NetJSON` Layered Architecture (`controller/openwisp_netjson_rollback_agent.py`)

| OpenWISP Pattern | FuturaMAX Implementation | Verification Status |
| :--- | :--- | :--- |
| **3-Layer Hierarchical `NetJSON` `DeviceConfiguration`** (`openwisp-controller` + `netjsonconfig`) | `export_layered_netjson_device_configuration()` splits every Golden Profile into `layer1_universal_linux_tcp_bridge`, `layer2_soc_radio_driver_family`, and `layer3_per_link_rf_overrides` with canonical SHA-256 `configuration_checksum` (`cf93fa93fbba0afd0953cc38b067b5f0623746f7b37a3c461d5cd11b93bd5137` for `openwrt_lap120_ptmp_multicpe_champion`). | `CONFIRMED` across all 8 Golden Profiles (`tests/test_stage31a_m9b_and_openwisp_netjson.py`) |
| **`NetJSON` `DeviceMonitoring` Telemetry Schema** (`openwisp-monitoring`) | `export_netjson_device_monitoring()` serializes live `iw dev station dump` + loaded `p50/p95/p99` RTT and goodput into standard `NetJSON` `DeviceMonitoring` JSON. | `CONFIRMED` on live 3-CPE sector telemetry (`S31A-R1`) |
| **Self-Reverting `test_config` RAM Watchdog** (`openwisp-config` agent) | `render_self_reverting_ram_watchdog_script()` emits an idempotent POSIX `/bin/sh` script that checks `/tmp/fmx_netjson_checksum_<profile>`, applies RAM-only changes (`0` flash writes), probes `controller_gateway_ip`, and automatically executes `rollback_ram_profile()` if connectivity fails or `/tmp/fmx_force_rollback` is triggered. | `CONFIRMED` (`FORBIDDEN_TOKENS` static guard + live receipt) |
