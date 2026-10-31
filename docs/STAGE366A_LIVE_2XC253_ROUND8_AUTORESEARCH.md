<!-- doc-head: STAGE366A_LIVE_2XC253_ROUND8_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 366A — Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 8 Ground-Up 2.4 GHz Asymmetric Chain-Imbalance & `athstats -ol` Verification

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 8** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `Rocket 2AC Prism` (`198.18.0.65`, `2XC.v8.7.11`, Boca 6) evaluating:
- **Ground-Up 2.4 GHz Asymmetric Chain-Imbalance Monitoring** (`hardware` / `proprietary airMAX/LTU module`): Real-time monitoring of Chain-0 / Chain-1 RSSI balance (`chain_delta_db`) and 2.4 GHz noise floor (`noise_floor_dbm`) with `uph_wifi0` `daprot=2`, `ff_mcast_airtime_limit=4`, `swr_limit=3`, and `AC*Minfree` (`64/32/16/0`).
- **QCA9880 `athstats -ol` WAL Telemetry** (`QCA firmware`): Tracking `mpdus_requed`, `excess_retries`, and `tx_xretries` under burst traffic.
- **SoftIRQ Budget & TSQ Tightening** (`Linux`): `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `txqueuelen=192`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `daprot` / `mcast` / `swr` | `tcp_limit_output_bytes` | `dev_weight` / `budget` / `txq` | Chain Delta Gate | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `1` / `10%` / `4` | `131072 B` | `64` / `300` / `1000` | `< 5 dB` | `45s` |
| `W2_B1` | `B_round8_24ghz_chain_athstats_ol_candidate` | `2` / `4%` / `3` | `49152 B` | `96` / `600` / `192` | `< 5 dB` | `45s` |
| `W3_A2` | `A_stock_baseline` | `1` / `10%` / `4` | `131072 B` | `64` / `300` / `1000` | `< 5 dB` | `45s` |
| `W4_B2` | `B_round8_24ghz_chain_athstats_ol_candidate` | `2` / `4%` / `3` | `49152 B` | `96` / `600` / `192` | `< 5 dB` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` (`uph_wifi0/daprot`, `uph_wifi0/swr_limit`, `athstats -ol` WAL counters).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-11`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage366a_live_2xc253_round8_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `chain_delta_db`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE366A-LIVE-2XC253-ROUND8-CHAIN-ATHSTATS` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage366a_live_2xc253_round8_autoresearch.py`](../tools/benchmarks/run_stage366a_live_2xc253_round8_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage366a_live_2xc253_round8_autoresearch.json`](../artifacts/autoresearch/stage366a_live_2xc253_round8_autoresearch.json)
- Test Suite: [`tests/test_stage366a.py`](../tests/test_stage366a.py)
