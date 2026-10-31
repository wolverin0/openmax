<!-- doc-head: STAGE390A_LIVE_2XC253_ROUND9_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 390A — Live `2XC` `Rocket 2AC Prism` (`198.18.0.65` Boca 6) Round 9 Ground-Up 2.4 GHz `/proc/sys/dev/uph_wifi0` & AirPrism 2.4 GHz Coexistence Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 9** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `Rocket 2AC Prism` (`198.18.0.65`, `2XC.v8.7.11`, Boca 6) evaluating:
- **Ground-Up 2.4 GHz `/proc/sys/dev/uph_wifi0/*` & `/proc/1/net/uph_wifi0/*` Audit** (`proprietary airMAX/LTU module`): Auditing and tuning per-AC WMM descriptor reserve watermarks (`ACBKMinfree=64`, `ACBEMinfree=32`, `ACVIMinfree=16`, `ACVOMinfree=0`), `set_multiq=3`, `daprot=2` (AirPrism 2.4 GHz coexistence & adjacent-channel immunity), `ff_mcast_airtime_limit=4`, `swr_limit=3`, and `vow_extstats=0`.
- **NAPI & TSQ Pacing on 2.4 GHz `2XC`** (`Linux`): `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `txqueuelen=192`, `gc_stale_time=120`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `AC*Minfree` (`BK/BE/VI/VO`) | `set_multiq` / `daprot` / `mcast` / `swr` | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `[32, 16, 8, 0]` | `1` / `1` / `10%` / `4` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B_round9_24ghz_uph_wifi0_coexistence_candidate` | `[64, 32, 16, 0]` | `3` / `2` / `4%` / `3` | `96` / `600` / `192` | `45s` |
| `W3_A2` | `A_stock_baseline` | `[32, 16, 8, 0]` | `1` / `1` / `10%` / `4` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B_round9_24ghz_uph_wifi0_coexistence_candidate` | `[64, 32, 16, 0]` | `3` / `2` / `4%` / `3` | `96` / `600` / `192` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` (`/proc/sys/dev/uph_wifi0/*` WMM `AC*Minfree`, `set_multiq`, `daprot`, `ff_mcast_airtime_limit`, `swr_limit`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-11`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage390a_live_2xc253_round9_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE390A-LIVE-2XC253-ROUND9-UPH-WIFI0-COEXISTENCE` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage390a_live_2xc253_round9_autoresearch.py`](../tools/benchmarks/run_stage390a_live_2xc253_round9_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage390a_live_2xc253_round9_autoresearch.json`](../artifacts/autoresearch/stage390a_live_2xc253_round9_autoresearch.json)
- Test Suite: [`tests/test_stage390a.py`](../tests/test_stage390a.py)
