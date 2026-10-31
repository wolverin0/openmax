<!-- doc-head: STAGE337A_LIVE_XM20_ROUND7_AUTORESEARCH.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.


# Stage 337A — Live `XM` `NanoStation M5` (`198.18.0.50` via `.253` Bridge) Round 7 `ath9k`/`ath_dev` ANI/SoftIRQ/BQL Deep Tuning

## 1. Objective & Safety Envelope (`CONFIRMED`)
Execute **Round 7** (`4` counterbalanced `A1 -> B1 -> A2 -> B2` windows) on the live bench `NanoStation M5` (`198.18.0.50` via `198.18.0.65` bridge, `AR7241` `32 MB` RAM, `XM.v6.1.12`) evaluating:
- **Adaptive Noise Immunity (`ANI`)** (`mac80211` / `proprietary airMAX/LTU module`): `ani_enable=1` (`phy0/ath9k/ani` and `/proc/sys/dev/wifi0/intmit=1`) + `AC*Minfree` (`0/16/32/64`) to prevent false-CCA OFDM weak-signal lockups without inducing OOM pressure.
- **Ethernet Byte Queue Limits (`BQL`)** (`Linux` / `hardware`): `eth0` `byte_queue_limits/limit_max=24576` (`24 KB` vs stock `64 KB`) to prevent 100 Mbps Fast-Ethernet TX ring queueing spikes on `AR7241`.
- **`fq_codel` Small-RAM Tuning & SoftIRQ Budget** (`Linux`): `target=5000 us` (`5 ms`), `interval=50000 us` (`50 ms`), `quantum=300`, `limit=384` packets (capping worst-case qdisc SKB footprint under `32 MB` RAM), paired with `dev_weight=48`, `netdev_budget=240`, and `txqueuelen=48`.
- **Safety Boundaries**: `45s` Non-DFS rollback watchdog armed per window; strictly RAM-only (`0` flash writes); **NEVER** touches `.241`, `.242`, or `.250`.

## 2. Counterbalanced `A1 -> B1 -> A2 -> B2` Design
| Window | Arm | `ani_enable` | `eth0` BQL `limit_max` | `fq_codel` (`target` / `interval` / `quantum` / `limit`) | `dev_weight` / `budget` / `txq` | Watchdog |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `W1_A1` | `A` (Baseline) | `1` | `65536 B` | `5ms` / `100ms` / `1514` / `1024` | `64` / `300` / `1000` | `45s` |
| `W2_B1` | `B` (Candidate) | `1` | `24576 B` | `5ms` / `50ms` / `300` / `384` | `48` / `240` / `48` | `45s` |
| `W3_A2` | `A` (Baseline) | `1` | `65536 B` | `5ms` / `100ms` / `1514` / `1024` | `64` / `300` / `1000` | `45s` |
| `W4_B2` | `B` (Candidate) | `1` | `24576 B` | `5ms` / `50ms` / `300` / `384` | `48` / `240` / `48` | `45s` |

## 3. Five-Pillar Traceability
1. **Pillar A (Binary RE)**: `ath_dev.ko`, `ath_rate_atheros.ko`, `ubnt_poll.ko` ANI (`intmit`) and `AC*Minfree` descriptor watermarks.
2. **Pillar B (Closed-Loop Research)**: Verified against `FMX-DISC-07` (`32 MB` OOM shield) and `FMX-DISC-33` (SoftIRQ / SKB reserve).
3. **Pillar C (Karpathy Autoresearch Harness)**: `4` counterbalanced `A1 -> B1 -> A2 -> B2` windows with `45s` watchdog (`artifacts/autoresearch/stage337a_live_xm20_round7_autoresearch.json`).
4. **Pillar D (Scientific Skills)**: Multi-objective evaluation across `goodput_mbps`, `rtt_p95_ms`, `rtt_p99_ms`, and `jitter_ms`.
5. **Pillar E (`memory-master`)**: Durable claim `MM-STAGE337A-LIVE-XM20-ROUND7-CHAMPION` under `scope="project:futuramax"`.

## 4. Verification Artifacts
- Script: [`tools/benchmarks/run_stage337a_live_xm20_round7_autoresearch.py`](../tools/benchmarks/run_stage337a_live_xm20_round7_autoresearch.py)
- Receipt: [`artifacts/autoresearch/stage337a_live_xm20_round7_autoresearch.json`](../artifacts/autoresearch/stage337a_live_xm20_round7_autoresearch.json)
- Test Suite: [`tests/test_stage337a.py`](../tests/test_stage337a.py)
