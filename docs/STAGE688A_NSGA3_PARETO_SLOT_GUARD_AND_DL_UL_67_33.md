<!-- doc-head: STAGE688A_NSGA3_PARETO_SLOT_GUARD_AND_DL_UL_67_33.md preserved document content -->
<!-- /doc-head -->



# Stage 688A — `NSGA-III` 4-Objective Pareto: `Fixed 10ms 67/33` (`+34.84%` DL Airtime) + `39 us` Slot Guard + `A-MSDU 7935B`

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-688A`
- **Optimizer**: `pymoo` `NSGA-III` (`4` objectives: `dl_goodput_mbps`, `dl_airtime_gain_pct`, `rtt_p99_ms`, `subframe_retry_pct`).
- **Key Breakthrough**: Combining **`Fixed 10ms 67/33`** TDMA framing with `slot_guard_us = 39 us`, `cbp_dur_us = 200 us`, and adaptive **`7935B` / `3839B` A-MSDU** yields **`+34.84%`** usable downlink airtime on high-density `Panel2-Guarida` (`.82`, `22` CPEs), boosting sector downlink goodput from `91.2 Mbps` to **`134.6 Mbps`** while cutting `RTT p99` from `18.40 ms` to **`9.85 ms`**.

## 2. 4-Objective `NSGA-III` Evaluation Table
| Solution ID | TDMA Mode | Slot Guard | `cbp_dur` | DL Goodput (`Mbps`) | DL Airtime Gain | RTT `p99` (`ms`) | Retry (`%`) | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `FLEXIBLE_50_50_SLOT85US_AMSDU3839_BASELINE` | `Flex 50/50` | `85 us` | `420 us` | `91.2` | `+0.00%` | `18.40` | `6.4%` | `False` |
| `FIXED_8MS_67_33_SLOT55US_AMSDU7935_PARETO` | `Fixed 8ms 67/33` | `55 us` | `260 us` | `124.8` | `+29.10%` | `8.95` | `1.4%` | **`True`** |
| `FIXED_10MS_67_33_SLOT39US_AMSDU7935_CHAMPION_PARETO` | **`Fixed 10ms 67/33`** | **`39 us`** | **`200 us`** | **`134.6`** | **`+34.84%`** | **`9.85`** | **`1.1%`** | **`True`** |
| `FIXED_5MS_50_50_ULTRA_LOW_LATENCY_PARETO` | `Fixed 5ms 50/50` | `39 us` | `180 us` | `106.4` | `+8.20%` | **`5.45`** | `1.2%` | **`True`** |

## 3. Artifacts & Tests
- **Script**: [`tools/sim/run_stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33.py`](../tools/sim/run_stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33.py)
- **Receipt**: [`artifacts/autoresearch/stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33.json`](../artifacts/autoresearch/stage688a_nsga3_pareto_slot_guard_and_dl_ul_67_33.json)
- **Pytest**: [`tests/test_stage688a.py`](../tests/test_stage688a.py)
