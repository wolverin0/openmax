<!-- doc-head: STAGE77A_AEON_MULTIVARIATE_RF_TIMESERIES_REGIME_CLASSIFIER.md preserved document content -->
<!-- /doc-head -->



# Stage 77A — `aeon` Multivariate RF Time-Series Regime & Zero-False-Positive Anomaly Classifier (`2026-10-26`)

- **Task ID**: `T-S77A-AEON-TIME-SERIES-RF-REGIME-AND-ANOMALY-CLASSIFIER`
- **Epistemic Status**: `CONFIRMED`
- **Layer Attribution**: `external controller`, `proprietary airMAX/LTU module`, `Linux`, `mac80211`, `ath10k`, `hardware`
- **Classifier Script**: [`tools/telemetry/run_stage77a_aeon_rf_timeseries_regime_classifier.py`](../tools/telemetry/run_stage77a_aeon_rf_timeseries_regime_classifier.py)
- **JSON Receipt (`5/5` Pillars Compliant)**: [`artifacts/autoresearch/stage77a_aeon_rf_timeseries_regime_classifier_20261026.json`](../artifacts/autoresearch/stage77a_aeon_rf_timeseries_regime_classifier_20261026.json)
- **Unit Test Suite**: [`tests/test_stage77a_aeon_rf_timeseries_classifier.py`](../tests/test_stage77a_aeon_rf_timeseries_classifier.py)

---

## 1. Multivariate Time-Series Data Contract & Physical Regime Signatures (`CONFIRMED`)

Following `.agents/skills/aeon/SKILL.md` v1.3, the dataset uses `aeon`'s standard 3D NumPy tensor layout `(n_cases, n_channels, n_timepoints) = (500, 6, 60)` (`100` windows per class, `6` physical telemetry channels, `60` 1-second samples per window; stratified `70/30` train/test split: `350` train, `150` held-out test):

| Channel Index | Telemetry Channel | Physical Source (`airOS 8` / `OpenWrt` / `AF-LTU`) |
| :---: | :--- | :--- |
| `0` | `rx_signal_dbm` | `wstalist` / `iw dev station dump` / `/sys/class/ame/ame_ctrl_dev/sta_list` |
| `1` | `channel_busy_pct` | `athstats` / `iw survey dump` (`busy_time / active_time`) |
| `2` | `tx_retries_pct` | `ath_dev.ko` / `mac80211` `tx_retries / tx_packets` |
| `3` | `p95_rtt_ms` | Active/passiveloaded `p95` RTT probe (`fmx_autoresearch_harness.py`) |
| `4` | `rx_bytes_delta` | Per-second `rx_bytes` derivative (`/sys/class/net/*/statistics/rx_bytes`) |
| `5` | `max_bd_or_aql_backlog` | `AF-LTU` `gBDHandleOnce/maxBD` or `OpenWrt` `mac80211` `aql_txq_limit` backlog |

### Five Operational & Fault Regimes (`Classes 0..4`)
1. **`Class 0 — NORMAL_LOAD`**: Healthy Triple-Play traffic under `OpenWrt Champion v20` / `airOS 8 PtP Champion v6` (`rx_signal_dbm ~ -51..-61 dBm`, `channel_busy_pct ~ 36..56%`, `tx_retries_pct ~ 2..5.5%`, `p95_rtt_ms ~ 6.2..38 ms`, `rx_bytes_delta > 2.2 MB/s`).
2. **`Class 1 — CO_CHANNEL_INTERFERENCE`**: Adjacent-sector or external co-channel interference (`Stage 71B` pre-mitigation): high `channel_busy_pct ~ 80..95%` + elevated `tx_retries_pct ~ 19..34%` + `p95_rtt_ms ~ 72..128 ms` while `rx_signal_dbm` remains strong (`-52..-62 dBm`).
3. **`Class 2 — BAD_APPLE_AIRTIME_HOG`**: Weak-signal (`-79..-82.5 dBm`) subscriber (`MCS0 6.5 Mbps` cold-start or unaligned CPE on `Panel2-Guarida`) monopolizing sector airtime (`channel_busy_pct ~ 84..97%`, `p95_rtt_ms ~ 115..188 ms`, `max_bd_or_aql_backlog ~ 88..125`).
4. **`Class 3 — LTU_BUG05_LNA_DEAFNESS`**: `AF-LTU` `LTU-BUG-05` signature (`Stage 63B/64A`): when `ulpwr_enable=1` is left active, the firmware control loop resets `ulpwrtune` from `-75 dBm` to `-51 dBm` (`-24 dB` step-function drop every `3` seconds), creating a high-energy lag-3 autocorrelation signature and periodic throughput notches.
5. **`Class 4 — FROZEN_COLLECTOR_FALSE_ALARM`**: Stale SNMP/SSH collector cache or zero-traffic link (`rx_bytes_delta == 0` / zero temporal variance across channels). Per `Stage 59A` Zero-False-Positive WISP Observability rules, this regime must be isolated as `Class 4` with **`0.0%` false-positive RF fault alarms**.

---

## 2. Classifier Architecture & Held-Out Verification Metrics (`CONFIRMED`)

`AeonMultivariateMiniRocketSummaryClassifier` combines:
- **240 Dilated 1D Random Convolutional Kernels (`MiniRocket` / `ROCKET`)** across `dilations = [1, 2, 4, 8]` with **Proportion of Positive Values (`PPV`)** and **Max Pooling** features (`480` features),
- **Catch22-Style Per-Channel Temporal Summary & Step-Change Features** (`mean`, `std`, `min`, `max`, `q25`, `q75`, `max_abs_diff`, `mean_abs_diff`, `zero_diff_frac`, and `lag-3 autocorrelation` for `LTU-BUG-05` step detection — `60` features),
- **`StandardScaler` + `RidgeClassifierCV`** with a deterministic zero-variance / zero-`rx_bytes_delta` guard for `Class 4 (FROZEN_COLLECTOR_FALSE_ALARM)`.

| Evaluation Metric | Target Gate | Measured Result | Status |
| :--- | :---: | :---: | :---: |
| **Held-Out Test Accuracy (`150` cases, `30` per class)** | `>= 98.0%` | **`100.00%` (`1.0000`)** | **`PASS` (`CONFIRMED`)** |
| **Held-Out Macro $F_1$ Score** | `>= 0.98` | **`1.0000`** | **`PASS` (`CONFIRMED`)** |
| **5-Fold Stratified Cross-Validation Mean Accuracy** | `>= 98.0%` | **`100.00%` (`[1.0, 1.0, 1.0, 1.0, 1.0]`)** | **`PASS` (`CONFIRMED`)** |
| **False-Positive RF Alarm Rate on `FROZEN_COLLECTOR_FALSE_ALARM`** | `== 0.0%` | **`0.0000%` (`0 / 30`)** | **`PASS` (`CONFIRMED`)** |

---

## 3. Verification Commands (`CONFIRMED`)

```powershell
$env:PYTHONPATH="."; python tools/telemetry/run_stage77a_aeon_rf_timeseries_regime_classifier.py
python tools/verify/enforce_5pillar_research_gate.py artifacts/autoresearch/stage77a_aeon_rf_timeseries_regime_classifier_20261026.json
pytest tests/test_stage77a_aeon_rf_timeseries_classifier.py -v
```
