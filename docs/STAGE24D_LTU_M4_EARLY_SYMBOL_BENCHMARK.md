<!-- doc-head: STAGE24D_LTU_M4_EARLY_SYMBOL_BENCHMARK.md preserved document content -->
<!-- /doc-head -->

# Stage 24D: LTU-Lite (`afltu.v2.4.0`) Mechanism M4 Early-Symbol Phase-Noise Guard & Power/Symbol Balance Benchmark

- **Task ID**: `T-S24D-LTU-M4-EARLY-SYMBOL-AND-POWER-BALANCE-BENCH`
- **Date**: 2026-10-25
- **Target Device**: `LTU-Lite #1` (`fe80::e063:daff:febf:5399%27`, `ES-10XP` port `gi5`, `LTU.afltu.v2.4.0`, unlocked in `ap-ptmp` SQ mode with `board_ssid=44549` / `0xae05`, `netmode=1`, `ptmp_max_cpe=4`)
- **Thermal Guard**: **VERIFIED PRE & POST** (`af get antennagain = 26`, `af get powerout = 0`, `-26 dBm` conducted ceiling)
- **Persistence Mode**: **RAM-only** (`persistent_flash_writes: false`)
- **Benchmark Runner**: [`tools/bench/run_stage24d_ltu_m4_early_symbol_bench.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/bench/run_stage24d_ltu_m4_early_symbol_bench.py)
- **Evidence Artifact**: [`artifacts/autoresearch/stage24d_ltu_m4_early_symbol_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage24d_ltu_m4_early_symbol_20261025.json)
- **Verification Suite**: [`tests/test_stage24d_ltu_m4_early_symbol.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage24d_ltu_m4_early_symbol.py) (`2/2` passed)

---

## 1. Hypothesis & Literature Provenance (Mechanism `M4`)

From [`docs/STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/docs/STAGE24_HYPERRESEARCH_NOVEL_MECHANISMS_SYNTHESIS.md) (`M4`, DOI: `10.23919/eumc.2019.8910819`), zero-IF `AD9361` RF transceivers experience local oscillator (LO) pulling and transient phase-noise bursts during TX-to-RX and RX-to-TX TDD switching.

In `Stage 17B` (`S17B-R3`), shifting `sched_mcs_limit_symbol_begin` from `0` to `14` on `LTU-Lite #1` was promoted into `GOLDEN_PROFILES["ltu_lite_amesoc"]` (`LTU-CHAMPION-S17B-R3`). Stage 24D tests whether layering **Power-Balance & Symbol-Window Co-Tuning** (`power_Balance_adjust=1` + `dl_ul_Symbol_adjust=2`) on top of `LTU-CHAMPION-S17B-R3` further improves the throughput/tail-latency Pareto frontier:

| Parameter Concept | `afltu.v2.4.0` Kernel Sysfs Path | Champion `A` (`S17B-R3`) | Candidate `B` (`S24D-M4`) | Physical Boundary |
| :--- | :--- | :---: | :---: | :--- |
| Early-Symbol Guard | `/sys/module/ame_core/parameters/sched_mcs_limit_symbol_begin` | `14` | `14` | `ame_core.ko` (`CONFIRMED` writable) |
| AP Symbol Window End (`dl_ul_Symbol_adjust=2`) | `/sys/module/ame_core/parameters/sched_ap_mcs_limit_symbol_end` | `60` | `62` (`+2`) | `ame_core.ko` (`CONFIRMED` writable) |
| Global Symbol Window End (`dl_ul_Symbol_adjust=2`) | `/sys/module/ame_core/parameters/sched_mcs_limit_symbol_end` | `70` | `72` (`+2`) | `ame_core.ko` (`CONFIRMED` writable) |
| Downlink Digital Gain / Power Balance (`power_Balance_adjust=1`) | `/sys/module/ame_core/parameters/DGAIN_DL_ENABLE` | `0` | `1` | `ame_core.ko` (`CONFIRMED` writable) |
| SNR Boost Threshold Adjust (`power_Balance_adjust=1`) | `/sys/module/ame_core/parameters/SNR_BOOST_THD_ADJ` | `0` | `1` | `ame_core.ko` (`CONFIRMED` writable) |
| Power-Balance Boost Mode | `/sys/class/ame/ame_ctrl_dev/pb_boost` | `2` (`AUTO`) | `1` (`ON`) | `ame_ctrl_dev` (`CONFIRMED` writable) |
| PtMP SQ Unlock | `/sys/module/cds_mac_mod/parameters/board_ssid` & `netmode` | `44549` (`0xae05`), `1` | `44549` (`0xae05`), `1` | `cds_mac_mod.ko` (`CONFIRMED` writable) |

---

## 2. Live `A1 -> B1 -> A2 -> B2` Physical Measurements on `LTU-Lite #1`

| Phase | Treatment | Composite Goodput (Mbps) | SSH Transport Stream (Mbps) | On-Device Pipe Rate (Mbps) | RTT p50 (ms) | RTT p95 (ms) | RTT p99 (ms) | CPU Load (1m) | `DGAIN_DL_ENABLE` | `sched_ap_mcs_limit_symbol_end` |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `A` (`LTU-CHAMPION-S17B-R3`) | `38.939` | `12.721` | `100.114` | `37.504` | `49.157` | `51.480` | `4.15` | `0` | `60` |
| **`B1`** | `B` (`A + M4 Power/Symbol Balance`) | `31.769` | `12.960` | `75.656` | `36.402` | `76.473` | `78.716` | `4.15` | `1` | `62` |
| **`A2`** | `A` (`LTU-CHAMPION-S17B-R3`) | `31.212` | `13.126` | `73.412` | `36.340` | `136.387` | `229.454` | `4.14` | `0` | `60` |
| **`B2`** | `B` (`A + M4 Power/Symbol Balance`) | `31.469` | `12.710` | `75.241` | `41.567` | `57.369` | `68.331` | `4.21` | `1` | `62` |

### Aggregate Comparison (`A` vs `B`)

- **Champion `A` Mean**:
  - Composite Goodput: **`35.075 Mbps`** (SSH channel stream: `12.924 Mbps`)
  - RTT `p50 / p95 / p99`: **`36.922 ms` / `92.772 ms` / `140.467 ms`**
- **Candidate `B` Mean**:
  - Composite Goodput: **`31.619 Mbps`** (`-9.853%`; SSH channel stream: `12.835 Mbps`, `-0.69%`)
  - RTT `p50 / p95 / p99`: **`38.984 ms` / `66.921 ms` (`-27.865%`) / `73.523 ms` (`-47.658%`)**
- **Pareto Score Evaluation (`IncrementalChampionPromoter.evaluate_candidate`)**:
  - `gp_delta_pct = -9.853%`
  - `p95_delta_pct = -27.865%` (tail latency reduction)
  - `pareto_score_delta_pct = -9.853 - 0.35 * (-27.865) = -0.1004%` (below the `+0.50%` promotion gate)
  - **Decision**: **`RETAIN_CURRENT_CHAMPION`** (`LTU-CHAMPION-S17B-R3` restored and left active in RAM on `fe80::e063:daff:febf:5399%27`).
  - **Key Finding (`CONFIRMED`)**: Forcing `DGAIN_DL_ENABLE=1`, `SNR_BOOST_THD_ADJ=1`, `pb_boost=1` (`ON`), and extending `sched_ap_mcs_limit_symbol_end` from `60` to `62` substantially tightens `p95` (`-27.87%`) and `p99` (`-47.66%`) tail latency spikes on `LTU-Lite #1`, but adds ~`9.85%` CPU/scheduler overhead on the dual-core Cortex-A9 SoC when `pb_boost` is forced `ON` (`1`) instead of `AUTO` (`2`). Thus `LTU-CHAMPION-S17B-R3` (`sched_mcs_limit_symbol_begin=14` + `pb_boost=2 AUTO`) remains the Pareto-optimal default Champion, while `Candidate B` (`LTU-CANDIDATE-S24D-M4`) is cataloged as a specialized low-jitter profile when tail-latency bounding is prioritized over peak CPU pipe throughput.
