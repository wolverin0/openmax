<!-- doc-head: STAGE24F_LTU_PURE_SYMBOL_WINDOW_BENCHMARK.md preserved document content -->
<!-- /doc-head -->

# Stage 24F: LTU-Lite (`afltu.v2.4.0`) Pure Early/Late Symbol-Window Isolation Benchmark & Champion Promotion

- **Task ID**: `T-S24F-LTU-PURE-SYMBOL-WINDOW-ISOLATION-BENCH`
- **Date**: 2026-10-25
- **Target Device**: `LTU-Lite #1` (`fe80::e063:daff:febf:5399%27`, `ES-10XP` port `gi5`, `LTU.afltu.v2.4.0`, unlocked in `ap-ptmp` SQ mode with `board_ssid=44549` / `0xae05`, `netmode=1`, `ptmp_max_cpe=4`)
- **Thermal Guard**: **VERIFIED PRE & POST** (`af get antennagain = 26`, `af get powerout = 0`, `-26 dBm` conducted ceiling)
- **Persistence Mode**: **RAM-only** (`persistent_flash_writes: false`)
- **Benchmark Runner**: [`tools/bench/run_stage24f_ltu_pure_symbol_window_bench.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/bench/run_stage24f_ltu_pure_symbol_window_bench.py)
- **Evidence Artifact**: [`artifacts/autoresearch/stage24f_ltu_pure_symbol_window_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage24f_ltu_pure_symbol_window_20261025.json)
- **Verification Suite**: [`tests/test_stage24f_ltu_pure_symbol_window.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage24f_ltu_pure_symbol_window.py) (`2/2` passed)
- **Golden Profile Updated**: [`controller/multiradio_golden_profile_applicator.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/multiradio_golden_profile_applicator.py) (`GOLDEN_PROFILES["ltu_lite_amesoc"]`, `validated_rounds` += `"S24F-R1"`)

---

## 1. Hypothesis & Isolation Rationale (`Stage 24D` $\rightarrow$ `Stage 24F`)

In [`docs/STAGE24D_LTU_M4_EARLY_SYMBOL_BENCHMARK.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE24D_LTU_M4_EARLY_SYMBOL_BENCHMARK.md), combining `DGAIN_DL_ENABLE=1 + SNR_BOOST_THD_ADJ=1 + pb_boost=1` with `sched_ap_mcs_limit_symbol_end=62 + sched_mcs_limit_symbol_end=72` reduced `p95` RTT by `-27.87%` and `p99` RTT by `-47.66%`, but forcing `DGAIN_DL_ENABLE=1`, `SNR_BOOST_THD_ADJ=1`, and `pb_boost=1` (`ON`) added digital-gain processing overhead on the dual-core Cortex-A9 SoC that lowered composite goodput by `-9.85%`.

**Stage 24F Hypothesis**: Isolating **pure early/late symbol-window optimization** (`sched_mcs_limit_symbol_begin=12`, `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72`) while keeping `DGAIN_DL_ENABLE=0`, `SNR_BOOST_THD_ADJ=0`, and `pb_boost=2` (`AUTO`) retains the tail-latency reduction of the wider TDD symbol window without incurring the digital-gain CPU penalty, while reclaiming `+2` early OFDM data symbols (`12` vs `14`) after the `AD9361` TX-to-RX PLL settling transient (`~40 us`).

---

## 2. Live `A1 -> B1 -> A2 -> B2` Physical Measurements on `LTU-Lite #1`

| Phase | Treatment | Composite Goodput (Mbps) | SSH Transport Stream (Mbps) | RTT p50 (ms) | RTT p95 (ms) | RTT p99 (ms) | CPU Load (1m) | `sched_mcs_limit_symbol_begin` | `sched_ap_mcs_limit_symbol_end` | `sched_mcs_limit_symbol_end` | `DGAIN_DL_ENABLE` |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `A` (`LTU-CHAMPION-S17B-R3`: `14..60/70`) | `31.682` | `12.710` | `38.647` | `204.602` | `238.120` | `4.05` | `14` | `60` | `70` | `0` |
| **`B1`** | `B` (`S24F Pure Symbol Window`: `12..62/72`) | `32.519` | `12.639` | `36.494` | `134.819` | `145.102` | `4.09` | `12` | `62` | `72` | `0` |
| **`A2`** | `A` (`LTU-CHAMPION-S17B-R3`: `14..60/70`) | `32.280` | `13.100` | `46.977` | `223.248` | `284.736` | `4.07` | `14` | `60` | `70` | `0` |
| **`B2`** | `B` (`S24F Pure Symbol Window`: `12..62/72`) | `32.315` | `12.431` | `36.836` | `127.195` | `137.634` | `4.10` | `12` | `62` | `72` | `0` |

### Aggregate Comparison (`A` vs `B`)

- **Champion `A` (`LTU-CHAMPION-S17B-R3`) Mean**:
  - Composite Goodput: **`31.981 Mbps`**
  - RTT `p50 / p95 / p99`: **`42.812 ms` / `213.925 ms` / `261.428 ms`**
- **Candidate `B` (`LTU-CANDIDATE-S24F-SYM-WINDOW`) Mean**:
  - Composite Goodput: **`32.417 Mbps`** (**`+1.363%`**)
  - RTT `p50 / p95 / p99`: **`36.665 ms` (`-14.36%`) / `131.007 ms` (`-38.760%`) / `141.368 ms` (`-45.925%`)**
- **Pareto Score Evaluation (`IncrementalChampionPromoter.evaluate_candidate`)**:
  - `gp_delta_pct = +1.363%`
  - `p95_delta_pct = -38.760%`
  - `pareto_score_delta_pct = +1.363 - 0.35 * (-38.760) = +14.9294%` (`>= +0.50%` promotion gate)
  - **Decision**: **`PROMOTE_NEW_CHAMPION`** (`LTU-CANDIDATE-S24F-SYM-WINDOW` promoted into `GOLDEN_PROFILES["ltu_lite_amesoc"]` as `S24F-R1` and left active in RAM on `fe80::e063:daff:febf:5399%27`).
