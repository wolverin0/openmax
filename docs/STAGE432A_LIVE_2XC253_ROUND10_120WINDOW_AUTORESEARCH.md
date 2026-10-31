<!-- doc-head: STAGE432A_LIVE_2XC253_ROUND10_120WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 432A — Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 10 (`120-Window` Milestone) 2.4 GHz Urban Interference Immunity, Dynamic RTS/CTS & AirPrism Tuning Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 10** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows, reaching `40` cumulative windows on `2XC` `.253`) evaluating:
- **2.4 GHz Urban Interference Immunity & AirPrism Tuning** (`proprietary airMAX/LTU module` / `hardware`): `uph_wifi0/daprot=2`, `ff_mcast_airtime_limit=4`, `swr_limit=3`, `AC*Minfree = [64, 32, 16, 0]`.
- **Dynamic RTS/CTS Protection Threshold** (`mac80211` / `proprietary airMAX/LTU module`): `dynamic_rts_cts_bytes=512` (vs stock `2346` disabled) to eliminate hidden-node collision bursts in dense 2.4 GHz urban spectrum.
- **NAPI & TSQ Pacing** (`Linux`): `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `txqueuelen=192`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `dynamic_rts_cts_bytes` | `daprot` / `mcast` / `swr` | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `2346 B` (Off) | `1` / `10%` / `4` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B_round10_24ghz_urban_rts_airprism_candidate` | `512 B` (Dynamic) | `2` / `4%` / `3` | `96` / `600` / `192` | `45s` |
| `W3_A2` | `A_stock_baseline` | `2346 B` (Off) | `1` / `10%` / `4` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B_round10_24ghz_urban_rts_airprism_candidate` | `512 B` (Dynamic) | `2` / `4%` / `3` | `96` / `600` / `192` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` (`dynamic_rts_cts_bytes`, `uph_wifi0/daprot`, `uph_wifi0/swr_limit`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-11`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage432a_live_2xc253_round10_120window_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE432A-LIVE-2XC253-ROUND10-URBAN-RTS-AIRPRISM` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage432a_live_2xc253_round10_120window_autoresearch.py`](../tools/benchmarks/run_stage432a_live_2xc253_round10_120window_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage432a_live_2xc253_round10_120window_autoresearch.json`](../artifacts/autoresearch/stage432a_live_2xc253_round10_120window_autoresearch.json)
- Test Suite: [`tests/test_stage432a.py`](../tests/test_stage432a.py)
