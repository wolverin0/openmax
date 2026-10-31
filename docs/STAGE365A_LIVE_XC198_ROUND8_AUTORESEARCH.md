<!-- doc-head: STAGE365A_LIVE_XC198_ROUND8_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 365A — Live `XC` `Rocket Prism 5AC Gen2` (`198.18.0.64` Boca 4) Round 8 Ground-Up AirPrism Active Filter GPIO & WAL Queue Drain Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 8** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `Rocket Prism 5AC Gen2` (`198.18.0.64`, `XC.v8.7.25`, Boca 4) evaluating:
- **Ground-Up AirPrism Active Filter GPIO & HSR State** (`proprietary airMAX/LTU module` + `hardware`): Verifying `uph_wifi0/daprot=2` (`ACTIVE_HSR_DAPROT_2` dynamic adjacent-channel rejection filter state) + `swr_limit=3` + `AC*Minfree` (`64/32/16/0`).
- **QCA9880 WAL Queue Drain Telemetry (`athstats -ol` / `wal_dbg_stats`)** (`QCA firmware`): Tracking `mpdus_requed`, `excess_retries`, `tx_xretries`, and `pdev_tx_timeout` during burst load to confirm zero WAL ring starvation.
- **TCP Small Queues (`TSQ`) + UDP Socket Buffer Floor** (`Linux`): Tightening `net.ipv4.tcp_limit_output_bytes=49152` (`48 KB` vs stock `128 KB`) while raising default UDP socket buffers (`net.core.rmem_default=131072`, `net.core.wmem_default=131072`) alongside `dev_weight=96`, `netdev_budget=600`, and `txqueuelen=192`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `daprot` / `swr_limit` | `tcp_limit_output_bytes` | `rmem_default` / `wmem_default` | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A_stock_baseline` | `1` / `4` | `131072 B` | `110592 B` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B_round8_airprism_wal_tsq_candidate` | `2` / `3` | `49152 B` | `131072 B` | `96` / `600` / `192` | `45s` |
| `W3_A2` | `A_stock_baseline` | `1` / `4` | `131072 B` | `110592 B` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B_round8_airprism_wal_tsq_candidate` | `2` / `3` | `49152 B` | `131072 B` | `96` / `600` / `192` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ubnt_poll_host.ko`, `umac.ko`, `ath_dev.ko` symbols (`uph_wifi0/daprot`, `uph_wifi0/swr_limit`, `wal_dbg_stats`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-11`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage365a_live_xc198_round8_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `wal_mpdus_requed`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE365A-LIVE-XC198-ROUND8-AIRPRISM-WAL` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage365a_live_xc198_round8_autoresearch.py`](../tools/benchmarks/run_stage365a_live_xc198_round8_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage365a_live_xc198_round8_autoresearch.json`](../artifacts/autoresearch/stage365a_live_xc198_round8_autoresearch.json)
- Test Suite: [`tests/test_stage365a.py`](../tests/test_stage365a.py)
