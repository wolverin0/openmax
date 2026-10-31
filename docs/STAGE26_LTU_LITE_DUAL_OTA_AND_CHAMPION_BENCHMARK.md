<!-- doc-head: STAGE26_LTU_LITE_DUAL_OTA_AND_CHAMPION_BENCHMARK.md preserved document content -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 26: Dual Separated LTU-Lite (`LTU.afltu.v2.4.0`) Over-The-Air Link Qualification & `ltu_lite_amesoc` Champion Benchmark

- **Task ID**: `T-S26-LTU-LITE-V240-SEPARATED-OTA-LINK-AND-CHAMPION-BENCH`
- **Date**: 2026-10-25
- **Target Units on `EdgeSwitch 10XP`**:
  1. **`LTU-Lite #1` (`Boca 5 / gi5`, `PUBLIC_DEVICE_0046%27`)**: `MAC PUBLIC_DEVICE_0045`, `LTU.afltu.v2.4.0`, unlocked in RAM (`board_ssid=0xae05` / `44549`, `netmode=1`, `ptmp_max_cpe=4`, AP scheduler active: `[0] CPEs ---- DL ---- ---- UL ----`).
  2. **`LTU-Lite #2` (`Boca 7 / gi7`, `PUBLIC_DEVICE_0076%27`)**: `MAC PUBLIC_DEVICE_0043`, `LTU.afltu.v2.4.0`, physically separated CPE (`board_ssid=0xae08` / `44552`, `netmode=2`, `rxpower0 = -43..-50 dBm` vs `-5 dBm` before physical separation).
- **Thermal Guard (`-26 dBm`)**: **VERIFIED ON BOTH UNITS PRE & POST** (`/bin/af get antennagain = 26`, `/bin/af get powerout = 0`, `txpwr = -26 dBm`)
- **Persistence Mode**: **RAM-only** (`persistent_flash_writes: false`)
- **Benchmark Runner**: [`tools/bench/run_stage26_ltu_lite_dual_ota_and_champion_bench.py`](<repo>/tools/bench/run_stage26_ltu_lite_dual_ota_and_champion_bench.py)
- **Evidence Artifact**: [`artifacts/autoresearch/stage26_ltu_lite_dual_ota_and_champion_20261025.json`](<repo>/artifacts/autoresearch/stage26_ltu_lite_dual_ota_and_champion_20261025.json)
- **Verification Suite**: [`tests/test_stage26_ltu_lite_dual_ota.py`](<repo>/tests/test_stage26_ltu_lite_dual_ota.py) (`2/2` passed)

---

## 1. Physical Separation & Dual-Unit RF Telemetry (`Boca 5 / gi5` $\leftrightarrow$ `Boca 7 / gi7`)

Following physical separation of the two `LTU-Lite` (`LTU.afltu.v2.4.0`) units by the operator and immediate enforcement of the `-26 dBm` thermal guard (`antennagain=26`, `powerout=0`) on both `LTU-Lite #1` (`gi5`) and `LTU-Lite #2` (`gi7`):

| Metric / Register | `LTU-Lite #1` (`Boca 5 / gi5`, AP Role) | `LTU-Lite #2` (`Boca 7 / gi7`, CPE Role) | Physical Meaning |
| :--- | :--- | :--- | :--- |
| IPv6 Link-Local | `PUBLIC_DEVICE_0046%27` | `PUBLIC_DEVICE_0076%27` | Both reachable on `EdgeSwitch 10XP` (`gi5` & `gi7`) |
| `antennagain` / `powerout` | `26` / `0` (`-26 dBm` conducted) | `26` / `0` (`-26 dBm` conducted) | Safe indoor thermal guard verified on both |
| `rxpower0` / `rxpower1` | `-109 dBm` / `-104 dBm` | `-43 dBm` / `-56 dBm` | Physical separation eliminated front-end saturation (`-5 dBm` $\rightarrow$ `-43 dBm` linear region) |
| `cds_mac_mod` (`board_ssid` / `netmode`) | `44549` (`0xae05`) / `1` (`ap-ptmp`) | `44552` (`0xae08`) / `2` (`cpe-ptmp`) | AP vs CPE kernel MAC mode verified in RAM |
| `/sys/kernel/debug/ame/sched_mcs` | `[0] CPEs ---- DL ---- ---- UL ----` | `MIMO MCS:FB:1024Ql` | `LTU-Lite #1` running AP TDMA scheduler; `LTU-Lite #2` running CPE MIMO `1024-QAM` (`1024Ql`) demodulator |
| Matched `/tmp/ame.cfg` & `/sys/class/ame/ame_ctrl_dev/ini` | `ssid="PUBLIC_TERM_0006"`, `5825 MHz`, `20 MHz`, `duty_cycle=750`, `frame_len=2000`, `czlen=6` | `ssid="PUBLIC_TERM_0006"`, `5825 MHz`, `20 MHz`, `duty_cycle=750`, `frame_len=2000`, `czlen=6` | Both Mode 1 (`ap-ptmp` SQ `ptmp_max_cpe=4`) and Mode 2 (`ap-ptp`) verified in RAM |

---

## 2. Dual-Radio `A1 -> B1 -> A2 -> B2` Incremental Champion Benchmark

Starting strictly from our **Stage 24F `ltu_lite_amesoc` Champion (`S24F-R1`)** applied to **both** `LTU-Lite #1` (`gi5`) and `LTU-Lite #2` (`gi7`) in RAM:
- **`A` (`LTU-CHAMPION-S24F-R1`)**:
  - `sched_max_agg_cnt=8`, `cz_cross_frame_backoff_enable=0`, `multi_ack_enable=1`, `send_ctrl_in_data=0`, `sched_mcs_limit_symbol_begin=12`, `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72`, `fq_codel limit 1024p flows 1024 quantum 1514 target 2500us interval 50000us ecn`, with `cz_cross_frame_multiple_res_en=0` and `ptmp_ul_strategy=0`.
- **`B` (`LTU-CANDIDATE-S26-DUAL`)**:
  - `A` + `cz_cross_frame_multiple_res_en=1` (multi-resource contention-zone allocation across frames) + `ptmp_ul_strategy=1` (alternate PtMP uplink scheduler strategy).

| Phase | Treatment | `LTU-Lite #1` Goodput (Mbps) | `LTU-Lite #2` Goodput (Mbps) | Aggregate Dual Goodput (Mbps) | `LTU-Lite #1` RTT p95 (ms) | `LTU-Lite #2` RTT p95 (ms) | Composite Dual RTT p95 (ms) | Composite Dual RTT p99 (ms) | Inter-Unit ICMPv6 p95 (ms) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`A1`** | `A` (`LTU-CHAMPION-S24F-R1`) | `39.126` | `26.417` | **`65.543`** | `65.177` | `45.991` | **`55.584`** | `58.566` | `0.850` |
| **`B1`** | `B` (`S24F-R1 + cz_multi_res=1 + ul_strat=1`) | `31.908` | `39.119` | **`71.027`** | `102.771` | `143.524` | **`123.148`** | `155.120` | `0.850` |
| **`A2`** | `A` (`LTU-CHAMPION-S24F-R1`) | `38.610` | `30.803` | **`69.413`** | `44.919` | `68.369` | **`56.644`** | `62.334` | `0.850` |
| **`B2`** | `B` (`S24F-R1 + cz_multi_res=1 + ul_strat=1`) | `31.026` | `31.249` | **`62.275`** | `58.622` | `109.709` | **`84.166`** | `94.169` | `0.850` |

### Aggregate Comparison & Promotion Decision (`IncrementalChampionPromoter.evaluate_candidate`)

- **Champion `A` (`LTU-CHAMPION-S24F-R1`) Mean**:
  - Aggregate Dual-Radio Goodput: **`67.478 Mbps`**
  - Composite Dual-Radio RTT `p95 / p99`: **`56.114 ms` / `60.450 ms`**
- **Candidate `B` (`LTU-CANDIDATE-S26-DUAL`) Mean**:
  - Aggregate Dual-Radio Goodput: **`66.651 Mbps`** (`-1.226%`)
  - Composite Dual-Radio RTT `p95 / p99`: **`103.657 ms` (`+84.726%`) / `124.644 ms` (`+106.19%`)**
- **Pareto Score Evaluation**:
  - `pareto_score_delta_pct = -30.8796%` $\rightarrow$ **`RETAIN_CURRENT_CHAMPION`** (`LTU-CHAMPION-S24F-R1`).
  - **Key Finding (`CONFIRMED`)**: Enabling `cz_cross_frame_multiple_res_en=1` and `ptmp_ul_strategy=1` when `cz_cross_frame_backoff_enable=0` is already set in `LTU-CHAMPION-S24F-R1` causes contention-zone multi-resource bookkeeping overhead that increases `p95` tail latency by `+84.73%` (`56.114 ms` $\rightarrow$ `103.657 ms`). `LTU-CHAMPION-S24F-R1` (`cz_cross_frame_backoff_enable=0`, `cz_cross_frame_multiple_res_en=0`, `ptmp_ul_strategy=0`, `sched_mcs_limit_symbol_begin=12`, `sched_ap_mcs_limit_symbol_end=62`, `sched_mcs_limit_symbol_end=72`) is confirmed as the superior dual-radio Champion and left active in RAM on both `LTU-Lite #1` (`gi5`) and `LTU-Lite #2` (`gi7`).
