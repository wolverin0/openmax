<!-- doc-head: STAGE367A_LIVE_XM20_ROUND8_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->


# Stage 367A — Live `XM` `NanoStation M5` (`192.168.1.20` / `.20` via `.253` Bridge) Round 8 Ground-Up OpenWrt `23.05.5` `ath9k` Per-Chain RSSI & `Minstrel-HT` Retry-Chain Autoresearch

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 8** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `NanoStation M5` (`192.168.1.20` / logical `.20` via `.253` bridge, `AR7241` `32 MB` RAM) evaluating:
- **Ground-Up `ath9k` Per-Chain RSSI Telemetry** (`mac80211` / `hardware`): Tracking `chain0_rssi_dbm`, `chain1_rssi_dbm`, and `chain_delta_db` (`< 5 dB` symmetry gate) alongside `ani_enable=1` (`intmit=1`).
- **`Minstrel-HT` 4-Stage Retry-Chain & A-MPDU Aggregation Ceiling** (`mac80211` / `proprietary airMAX/LTU module`): Bounded retry chain `c0..c3 = [4, 4, 2, 2]` (vs stock `[7, 7, 7, 7]`) paired with `aggr_limit_bytes=16384` (`16 KB` / `16` subframes vs `64 KB` / `32` subframes) to prevent head-of-line retry stalls and `32 MB` RAM SKB exhaustion.
- **Small-RAM BQL & SoftIRQ Budget** (`Linux`): `vm.min_free_kbytes=1536`, `eth0` BQL `limit_max=24576`, `txqueuelen=48`, `dev_weight=48`, `netdev_budget=240`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `minstrel_retry_chain` | `aggr_limit_bytes` | `eth0` BQL `limit_max` | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A` (Baseline) | `[7, 7, 7, 7]` | `65536 B` | `65536 B` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B` (Candidate) | `[4, 4, 2, 2]` | `16384 B` | `24576 B` | `48` / `240` / `48` | `45s` |
| `W3_A2` | `A` (Baseline) | `[7, 7, 7, 7]` | `65536 B` | `65536 B` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B` (Candidate) | `[4, 4, 2, 2]` | `16384 B` | `24576 B` | `48` / `240` / `48` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ath_dev.ko`, `ath_rate_atheros.ko`, `mac80211.ko`, `ath9k.ko` retry-chain and A-MPDU aggregation watermarks.
2. **Pillar B (Closed-Loop Research)**: Grounded in `tools/research/closed_loop_research_reactor.py` (`FMX-DISC-07`, `FMX-DISC-33`).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage367a_live_xm20_round8_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, `jitter_ms`, and `chain_delta_db`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE367A-LIVE-XM20-ROUND8-ATH9K-MINSTREL` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage367a_live_xm20_round8_autoresearch.py`](../tools/benchmarks/run_stage367a_live_xm20_round8_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage367a_live_xm20_round8_autoresearch.json`](../artifacts/autoresearch/stage367a_live_xm20_round8_autoresearch.json)
- Test Suite: [`tests/test_stage367a.py`](../tests/test_stage367a.py)
