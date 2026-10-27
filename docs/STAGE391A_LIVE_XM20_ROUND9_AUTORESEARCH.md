<!-- doc-head: STAGE391A_LIVE_XM20_ROUND9_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->


# Stage 391A — Live `XM` `NanoStation M5` (`192.168.1.20` / `.20` via `.253` Bridge) Round 9 Ground-Up OpenWrt `ath9k` Queue Depth, `AQL`/`BQL` & SoftIRQ Coalescing Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 9** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `NanoStation M5` (`192.168.1.20` / logical `.20` via `.253` bridge, `AR7241` `32 MB` RAM) evaluating:
- **Ground-Up OpenWrt `ath9k` Queue Depth & Airtime Queue Limits (`AQL`)** (`mac80211`): Tightening per-AC `aql_txq_limit` (`low=2000 us`, `high=4000 us` vs stock `5000/12000 us`), `aql_threshold=12000`, and `ath9k_txq_max_depth=64` (vs stock `256`) to cap hardware queue latency and `32 MB` RAM SKB occupancy.
- **Ethernet `BQL` & SoftIRQ Coalescing** (`Linux` / `hardware`): `eth0` `byte_queue_limits/limit_max=24576`, `txqueuelen=48`, `dev_weight=48`, `netdev_budget=240`, `netdev_budget_usecs=4000` (vs stock `8000 us`).
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `aql_txq_limit` (`low`/`high`) | `aql_threshold` / `txq_depth` | `eth0` BQL / `txq` | `dev_weight` / `budget` / `usecs` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A` (Baseline) | `5000` / `12000 us` | `24000` / `256` | `65536 B` / `1000` | `64` / `300` / `8000 us` | `45s` |
| `W2_B1` | `B` (Candidate) | `2000` / `4000 us` | `12000` / `64` | `24576 B` / `48` | `48` / `240` / `4000 us` | `45s` |
| `W3_A2` | `A` (Baseline) | `5000` / `12000 us` | `24000` / `256` | `65536 B` / `1000` | `64` / `300` / `8000 us` | `45s` |
| `W4_B2` | `B` (Candidate) | `2000` / `4000 us` | `12000` / `64` | `24576 B` / `48` | `48` / `240` / `4000 us` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ath_dev.ko`, `ath_rate_atheros.ko`, `mac80211.ko`, `ath9k.ko` (`aql_txq_limit`, `aql_threshold`, `ath_txq` max depth).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-07`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage391a_live_xm20_round9_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, and `jitter_ms`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE391A-LIVE-XM20-ROUND9-AQL-BQL-SOFTIRQ` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage391a_live_xm20_round9_autoresearch.py`](../tools/benchmarks/run_stage391a_live_xm20_round9_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage391a_live_xm20_round9_autoresearch.json`](../artifacts/autoresearch/stage391a_live_xm20_round9_autoresearch.json)
- Test Suite: [`tests/test_stage391a.py`](../tests/test_stage391a.py)
