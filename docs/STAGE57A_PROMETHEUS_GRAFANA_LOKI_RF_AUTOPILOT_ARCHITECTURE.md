<!-- doc-head: STAGE57A_PROMETHEUS_GRAFANA_LOKI_RF_AUTOPILOT_ARCHITECTURE.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 57A — Prometheus + Grafana + Loki RF Exporter & Closed-Loop Autopilot (`T-S57A-PROMETHEUS-GRAFANA-LOKI-RF-EXPORTER-AND-CLOSED-LOOP-AUTOPILOT`)

## 1. Executive Architecture: Why OpenWISP + UISP Alone Are Insufficient

| Platform | Primary Strength | Critical Gap on Fixed-Wireless PtMP Sectors | Stage 57A Solution |
| :--- | :--- | :--- | :--- |
| **OpenWISP** | Declarative NetJSON configuration templates, PKI VPN enrollment, 5-minute RRD/InfluxDB host checks (`ping`, CPU, RAM) | Does not scrape 15-second `ath10k` channel survey (`busy/rx/tx`), per-chain H/V MIMO imbalance, per-station `mac80211` `airtime_weight`, or `eth0` BQL/AQM/AQL queue counters | **`futuramax-rf-exporter` (`:9108`)** scrapes `LAP-120` (`.20`), `Loco 5AC` (`.250`/`.41`), `Rocket 5AC` (`.198`), and `LiteBeam M5` (`198.18.0.52`) every 15s |
| **UISP / UNMS** | Billing, CRM, topology mapping, native `airOS 8` / `LTU` WebSocket telemetry | Loses proprietary `ubnt_poll` visibility when APs/CPEs migrate to OpenWrt `24.10.5` (`mac80211` + `ath10k`); cannot govern Linux `BQL` or `fq_codel` | **Prometheus TSDB + Grafana + Loki + Alertmanager** unified across OpenWrt `24.10.5`, `airOS 8.7.x`, `airOS 6.3.x`, and `LTU 2.3.x` |

---

## 2. Five-Domain Closed-Loop RF & Queue Autopilot Engine

Implemented in [`tools/telemetry/futuramax_prometheus_rf_exporter.py`](../tools/telemetry/futuramax_prometheus_rf_exporter.py) and [`infra_observability_stack/alert_rules.yml`](../infra_observability_stack/alert_rules.yml):

1. **Channel Interference & Noise Floor Spikes (`FuturaMAXChannelInterferenceSpike`)**:
   - **Metrics**: `fmx_radio_noise_floor_dbm`, `fmx_radio_channel_busy_pct`, `fmx_radio_rx_airtime_pct`, `fmx_radio_tx_airtime_pct`, `fmx_radio_unaccounted_interference_busy_pct = max(0, busy - rx - tx)`.
   - **Trigger**: `noise_floor_dbm > -85 dBm` or `unaccounted_interference_busy_pct > 30%`.
   - **Autopilot Action**: Emits `ADVISORY_CHANNEL_SWITCH` recommendation (evaluates clean DFS/UNII-3 channels via Spectral FFT scan).
2. **Per-CPE Signal Drop vs Historical Baseline (`FuturaMAXCPESignalDropDetected`)**:
   - **Metrics**: `fmx_station_signal_dbm`, `fmx_station_signal_drop_vs_baseline_db`.
   - **Trigger**: `signal_drop_vs_baseline_db >= 4.0 dB` (`warning` at `4..8 dB`, `critical` at `>= 8 dB`).
   - **Autopilot Action**: Flags mast slip, water ingress, or seasonal foliage growth before link drop occurs.
3. **MIMO Chain Imbalance & Fresnel Obstruction (`FuturaMAXCPEChainImbalanceFresnel`)**:
   - **Metrics**: `fmx_station_chain_imbalance_db = |chain0_dbm - chain1_dbm|`.
   - **Trigger**: `chain_imbalance_db >= 4.0 dB` on 2x2 MIMO CPEs (`is_mimo=True`; automatically excluded on 1x1 SISO `LiteBeam M5`).
   - **Live Bench Finding (`CONFIRMED`)**: On the physical bench, `Rocket5AC_XC_airOS8` (`PUBLIC_DEVICE_0048`) exhibits `chain0 = -47.0 dBm`, `chain1 = -43.0 dBm` (`chain_imbalance_db = 4.0 dB`), triggering `FuturaMAXCPEChainImbalanceFresnel` and generating a `CHAIN_IMBALANCE_ALIGNMENT_TICKET`. Meanwhile, `Loco5AC_WA_OpenWrt` (`PUBLIC_DEVICE_0036`) has `chain0 = -45.0 dBm`, `chain1 = -45.0 dBm` (`0.0 dB` imbalance).
4. **Airtime Saturation & Bad-Apple CPE Detection (`FuturaMAXBadAppleCPEStarvingSector`)**:
   - **Metrics**: `fmx_station_bad_apple_score`, `fmx_station_tx_retries_pct`, `fmx_station_tx_bitrate_mbps`, `fmx_station_airtime_weight`.
   - **Trigger**: `tx_retries_pct > 15%` or (`tx_bitrate_mbps < 26 Mbps` while `channel_busy_pct > 50%`).
   - **Closed-Loop RAM Action**: Automatically executes `iw dev phy0-ap0 station set <MAC> airtime_weight 128` in RAM to prevent a single low-MCS / high-retry CPE from inflating sector `p95` latency.
5. **Hardware Queue & Bufferbloat Governance (`FuturaMAXChampionV19QueueDrift`)**:
   - **Metrics**: `fmx_eth0_bql_limit_min_bytes` (`4542`), `fmx_eth0_bql_limit_max_bytes` (`42392`), `fmx_eth0_bql_hold_time_ms` (`800`), `fmx_mac80211_fq_quantum_bytes` (`4542` AP / `1514` CPE), `fmx_autopilot_champion_v19_compliant` (`1.0`).
   - **Closed-Loop RAM Action**: If any parameter drifts from **`Stage 55A Champion v19`**, the exporter immediately re-applies `limit_min=4542`, `limit_max=42392`, `hold_time=800`, `fq_quantum=4542`, and `dev_weight_tx_bias=2` in RAM (`0` flash writes).

---

## 3. Live Bench Snapshot Summary (`2026-10-26`)

Artifact: [`artifacts/autoresearch/stage57a_prometheus_rf_autopilot_snapshot_20261025.json`](../artifacts/autoresearch/stage57a_prometheus_rf_autopilot_snapshot_20261025.json)

| Station / Device | Role | RSSI (dBm) | Drop vs Baseline | Chain0 / Chain1 (dBm) | Chain Imbalance | TX Rate / Retries | Airtime Weight | Idle `p95` RTT |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **`LAP-120` (`.20`)** | OpenWrt `24.10.5` AP (`5180 MHz`) | Noise `-95.0` | Busy `22.85%` | RX `0.97%` / TX `7.09%` | Unaccounted `14.79%` | `BQL 4542..42392 @ 800ms` | `fq_quantum=4542` | Compliant (`1.0`) |
| **`Loco5AC_WA` (`.41`)** | OpenWrt `24.10.5` 4-addr WDS | `-42.0` | `+1.0 dB` | `-45.0` / `-45.0` | **`0.0 dB`** | `144.4 Mbps` / `8.43%` | `768` | `3.38 ms` |
| **`Rocket5AC_XC` (`.198`)** | Stock `airOS 8.7.11` (`XC`) | `-41.0` | `+2.0 dB` | `-47.0` / `-43.0` | **`4.0 dB` (Alert)** | `78.0 Mbps` / `0.00%` | `512` | `3.20 ms` |
| **`LiteBeamM5_XW` (`.4`)** | Stock `airOS 6.3.2` (`XW` SISO) | `-52.0` | `-1.0 dB` | `-50.0` (1x1 SISO) | `0.0 dB` (SISO) | `72.2 Mbps` / `0.00%` | `128` | `2.05 ms` |
