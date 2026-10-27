<!-- doc-head: STAGE656A_NSGA3_PARETO_PB060_TXOP_TID_SCHED_AND_VHT40.md preserved document content -->
<!-- /doc-head -->



# Stage 656A — `NSGA-III` 4-Objective Pareto: `PB-060` + `PB-050` + `PB-040` + Adaptive `VHT40`/`VHT20`

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-656A`
- **Optimizer**: `pymoo` `NSGA-III` (`4` objectives: `goodput_mbps`, `rtt_p99_ms`, `iptv_jitter_ms`, `loss_1472b_pct`).
- **Key Breakthrough**: Combining `PB060-TXOP-CABQ-SCHED` (`cabq_txop_us = 1504 us` / `1024 us` to prevent multicast/BE TXOP starvation of `VO`/`VI` TIDs) with `PB050-RC-PROBE-DAMPEN` (`4000 ms`) and `PB040-CCA-AGC-OVERRIDE` (`-62 dBm`) cuts `RTT p99` from `14.80 ms` to **`1.94`–`2.38 ms`**, reduces IPTV `1316B` jitter from `4.92 ms` to **`0.58`–`0.74 ms`**, and lifts sector goodput to **`154.6 Mbps`** with `0.0%` `1472B` loss.

## 2. 4-Objective `NSGA-III` Evaluation Table
| Solution ID | `PB-060` (`us`) | `PB-050` (`ms`) | `PB-040` (`dBm`) | Goodput (`Mbps`) | RTT `p99` (`ms`) | IPTV Jitter (`ms`) | `1472B` Loss | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `STOCK_UNPATCHED_VHT40_BASELINE` | `4096` | `1000` | `-72` | `112.4` | `14.80` | `4.92` | `2.8%` | `False` |
| `PB040_PB050_ONLY_NO_PB060` | `4096` | `4000` | `-62` | `144.2` | `4.65` | `1.62` | `0.2%` | `False` |
| `NSGA3_CHAMPION_PB060_1504US_PB050_4000MS_PB040_M62_VHT40` | **`1504`** | **`4000`** | **`-62`** | **`154.6`** | **`2.38`** | **`0.74`** | **`0.0%`** | **`True`** |
| `NSGA3_ULTRA_LOW_LATENCY_PB060_1024US_PB050_4000MS_PB040_M62` | **`1024`** | **`4000`** | **`-62`** | **`149.8`** | **`1.94`** | **`0.58`** | **`0.0%`** | **`True`** |
| `NSGA3_HIGH_NOISE_PB060_1504US_PB050_6000MS_PB040_M58_VHT20` | `1504` | `6000` | `-58` | `96.4` | `2.12` | `0.65` | `0.0%` | `False` |

## 3. Artifacts & Tests
- **Script**: [`tools/sim/run_stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40.py`](../tools/sim/run_stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40.py)
- **Receipt**: [`artifacts/autoresearch/stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40.json`](../artifacts/autoresearch/stage656a_nsga3_pareto_pb060_txop_tid_sched_and_vht40.json)
- **Pytest**: [`tests/test_stage656a.py`](../tests/test_stage656a.py)
