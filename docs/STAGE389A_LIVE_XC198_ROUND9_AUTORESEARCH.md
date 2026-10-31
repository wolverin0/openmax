<!-- doc-head: STAGE389A_LIVE_XC198_ROUND9_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 389A — Live `XC` `Rocket Prism 5AC Gen2` (`198.18.0.64` Boca 4) Round 9 Ground-Up Per-AC WMM Queue Weights & `ubnt_poll` `/proc/sys/dev/uph_wifi0` Deep Audit & Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 9** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC.v8.7.25`, `QCA9558` `720 MHz`, Boca 4) evaluating:
- **Ground-Up `/proc/sys/dev/uph_wifi0/*` & `/proc/1/net/uph_wifi0/*` Audit** (`proprietary airMAX/LTU module`): Auditing and tuning per-AC WMM descriptor reserve watermarks (`ACBKMinfree=64`, `ACBEMinfree=32`, `ACVIMinfree=16`, `ACVOMinfree=0`), `set_multiq=3`, `daprot=2`, `ff_mcast_airtime_limit=5`, `swr_limit=3`, and `vow_extstats=0`.
- **TCP/UDP Burst Pacing & NAPI Budget on `QCA9558` `720 MHz`** (`Linux`): `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `txqueuelen=192`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `AC*Minfree` (`BK/BE/VI/VO`) | `set_multiq` / `daprot` / `mcast` / `swr` | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `[32, 16, 8, 0]` | `1` / `1` / `10%` / `4` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B_round9_wmm_uph_wifi0_candidate` | `[64, 32, 16, 0]` | `3` / `2` / `5%` / `3` | `96` / `600` / `192` | `45s` |
| `W3_A2` | `A_stock_baseline` | `[32, 16, 8, 0]` | `1` / `1` / `10%` / `4` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B_round9_wmm_uph_wifi0_candidate` | `[64, 32, 16, 0]` | `3` / `2` / `5%` / `3` | `96` / `600` / `192` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` (`/proc/sys/dev/uph_wifi0/*` WMM `AC*Minfree`, `set_multiq`, `daprot`, `ff_mcast_airtime_limit`, `swr_limit`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-11`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage389a_live_xc198_round9_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE389A-LIVE-XC198-ROUND9-WMM-UPH-WIFI0` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage389a_live_xc198_round9_autoresearch.py`](../tools/benchmarks/run_stage389a_live_xc198_round9_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage389a_live_xc198_round9_autoresearch.json`](../artifacts/autoresearch/stage389a_live_xc198_round9_autoresearch.json)
- Test Suite: [`tests/test_stage389a.py`](../tests/test_stage389a.py)
