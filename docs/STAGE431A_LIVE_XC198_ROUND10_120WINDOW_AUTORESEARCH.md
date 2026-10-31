<!-- doc-head: STAGE431A_LIVE_XC198_ROUND10_120WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 431A — Live `XC` `Rocket Prism 5AC Gen2` (`198.18.0.64` Boca 4) Round 10 (`120-Window` Milestone) Active-AirPrism GPIO `13..16` Filter Index Selection & WMI Retry Profile Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 10** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows, reaching `40` cumulative windows on `XC` `.198`) evaluating:
- **Active-AirPrism GPIO `13..16` 4-Bit Filter Index Selection** (`hardware` / `proprietary airMAX/LTU module`): Dynamic channel-tracked 4-bit filter index selection via GPIO pins `[13, 14, 15, 16]` paired with `uph_wifi0/daprot=2`.
- **QCA9880 WMI Retry Profile & `ubnt_poll` SWR Ceiling** (`QCA firmware` / `proprietary airMAX/LTU module`): Bounded hardware/software retry profile (`hw_short_retries=4`, `hw_long_retries=3`, `swr_limit=3`) with WMM descriptor watermarks (`AC*Minfree = [64, 32, 16, 0]`).
- **NAPI & TSQ Pacing** (`Linux`): `dev_weight=96`, `netdev_budget=600`, `tcp_limit_output_bytes=49152`, `txqueuelen=192`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | AirPrism GPIO `13..16` Mode | WMI Retry (`short`/`long`/`swr`) | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `STATIC_BYPASS_DAPROT_1` | `7` / `4` / `4` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B_round10_airprism_gpio13_16_wmi_retry_candidate` | `DYNAMIC_4BIT_CHANNEL_TRACKED_DAPROT_2` | `4` / `3` / `3` | `96` / `600` / `192` | `45s` |
| `W3_A2` | `A_stock_baseline` | `STATIC_BYPASS_DAPROT_1` | `7` / `4` / `4` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B_round10_airprism_gpio13_16_wmi_retry_candidate` | `DYNAMIC_4BIT_CHANNEL_TRACKED_DAPROT_2` | `4` / `3` / `3` | `96` / `600` / `192` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` (`airprism_gpio_pins=[13,14,15,16]`, `uph_wifi0/daprot`, `uph_wifi0/swr_limit`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-11`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage431a_live_xc198_round10_120window_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `softirq_pct`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE431A-LIVE-XC198-ROUND10-GPIO13-16-WMI` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage431a_live_xc198_round10_120window_autoresearch.py`](../tools/benchmarks/run_stage431a_live_xc198_round10_120window_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage431a_live_xc198_round10_120window_autoresearch.json`](../artifacts/autoresearch/stage431a_live_xc198_round10_120window_autoresearch.json)
- Test Suite: [`tests/test_stage431a.py`](../tests/test_stage431a.py)
