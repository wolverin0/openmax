<!-- doc-head: STAGE433A_LIVE_XM20_ROUND10_120WINDOW_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->


# Stage 433A — Live `XM`/`WA` (`192.168.1.20` / `.20` via `.253` Bridge) Round 10 (`120-Window` Multi-Radio Milestone) Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 10** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows on `XM`/`WA` `.20` via `.253` bridge, completing the **120-Window Multi-Radio Milestone** across `.198`, `.253`, and `.20`) evaluating:
- **Asymmetric Guard-Interval (`LGI` `800 ns` Rescue) + `Minstrel-HT` Retry-Chain** (`mac80211` / `proprietary airMAX/LTU module`): `asymmetric_lgi_rescue_enable=True` + `[4, 4, 2, 2]` retry profile.
- **Small-RAM `AQL` / `BQL` & OOM Protection** (`Linux` / `hardware`): `vm.min_free_kbytes=1536`, `aql_txq_limit` (`2000/4000 us`), `eth0` `BQL` `limit_max=24576`, `txqueuelen=48`, `dev_weight=48`, `netdev_budget=240`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `asymmetric_lgi_rescue` | `minstrel_retry_chain` | `aql_txq_limit` (`low`/`high`) | `eth0` BQL / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A` (Baseline) | `False` | `[7, 7, 7, 7]` | `5000` / `12000 us` | `65536 B` / `1000` | `45s` |
| `W2_B1` | `B` (Candidate) | `True` | `[4, 4, 2, 2]` | `2000` / `4000 us` | `24576 B` / `48` | `45s` |
| `W3_A2` | `A` (Baseline) | `False` | `[7, 7, 7, 7]` | `5000` / `12000 us` | `65536 B` / `1000` | `45s` |
| `W4_B2` | `B` (Candidate) | `True` | `[4, 4, 2, 2]` | `2000` / `4000 us` | `24576 B` / `48` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ath_dev.ko`, `ath_rate_atheros.ko`, `mac80211.ko`, `ath9k.ko` (`asymmetric_lgi_rescue_enable`, `minstrel_retry_chain`, `aql_txq_limit`).
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-07`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage433a_live_xm20_round10_120window_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, and `jitter_ms`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE433A-LIVE-XM20-ROUND10-120WINDOW` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage433a_live_xm20_round10_120window_autoresearch.py`](../tools/benchmarks/run_stage433a_live_xm20_round10_120window_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage433a_live_xm20_round10_120window_autoresearch.json`](../artifacts/autoresearch/stage433a_live_xm20_round10_120window_autoresearch.json)
- Test Suite: [`tests/test_stage433a.py`](../tests/test_stage433a.py)
