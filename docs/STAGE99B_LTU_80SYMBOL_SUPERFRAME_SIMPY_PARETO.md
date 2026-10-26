<!-- doc-head: Stage 99B SimPy Discrete-Event & pymoo NSGA-II Pareto Model of the 80-Symbol (2.0 ms / 500 Hz, 22.4 MS/s) AF-LTU OFDM Superframe and CPU0/CPU1 SMP IRQ Architecture (<180 lines) -->
# Stage 99B — `AF-LTU` `80`-Symbol (`2.0 ms` / `500 Hz`) OFDM Superframe `SimPy` & `pymoo` NSGA-II Pareto Model

- **Status**: `CONFIRMED` (`2026-10-26`)
- **Task ID**: `T-S99B-LTU-80SYMBOL-SUPERFRAME-SIMPY-AND-PYMOO-PARETO-MODEL`
- **Subsystem Attribution**: `proprietary airMAX/LTU module` + `Linux` (`ame_core.ko` `500 Hz` TDMA superframe scheduler + `Stage 96A/97C` Dual-Core SMP `IRQ 52/53` `CPU0` vs `IRQ 63/92` `CPU1` isolation)
- **Primary Verifier & Receipt**:
  - [`tools/sim/run_stage99b_ltu_80symbol_superframe_simpy_pymoo.py`](../tools/sim/run_stage99b_ltu_80symbol_superframe_simpy_pymoo.py) $\rightarrow$ [`artifacts/autoresearch/stage99b_ltu_80symbol_superframe_simpy_pymoo.json`](../artifacts/autoresearch/stage99b_ltu_80symbol_superframe_simpy_pymoo.json)
  - Calibrated to [`docs/STAGE97C_LTU_LITE1_FPGA_IRQ_AND_TELEMETRY_AUDIT.md`](STAGE97C_LTU_LITE1_FPGA_IRQ_AND_TELEMETRY_AUDIT.md) (`/bin/ame-debug-sched` `ame_debug:sched_result` + `/sys/class/ame/ame_debug_dev/isr_giveup`)

---

## 1. Hardware `80`-Symbol (`2.0 ms` / `500 Hz`, `22.4 MS/s`) Superframe Geometry (`CONFIRMED`)

Live telemetry from `/bin/ame-debug-sched record /tmp/s97c_sched.json 4` on `LTU-Lite #1` (`192.168.100.110`, `20 MHz`, `sample_rate = 22.4 MS/s`, `560` samples/symbol $\rightarrow$ **`T_sym = 25.0 µs`**) established the exact OFDM symbol map across frame periods (`1.0 ms` = `40` symbols, `2.0 ms` = `80` symbols, `4.0 ms` = `160` symbols):

| Superframe Zone (`2.0 ms`, `duty_cycle = 750`) | Symbol Indices | Symbol Count (`%`) | Duration (`µs`) | Hardware Framing & Dynamic Allocation (`CONFIRMED`) |
| :--- | :---: | :---: | :---: | :--- |
| **DL Preamble (`F_PREAMBLE`)** | `index 0` | `1` (`1.25%`) | `25.0 µs` | Fixed superframe synchronization preamble symbol. |
| **DL Primary Beacon (`F_BEACON`)** | `index 1` | `1` (`1.25%`) | `25.0 µs` | Primary AP broadcast beacon (`fragments: 1`). |
| **DL Dynamic Pool (`F_CNTRL` / `F_MNAGR` / `F_DATA` / `F_ACK`)** | `index 2..59` | `58` (`72.50%`) | `1,450.0 µs` | Partitioned into `29+14+7+4+2+2 = 58` `F_NULL` symbols when `N=0` CPEs; allocated to `F_CNTRL`+`F_MNAGR`+`F_ACK` (`2..6` symbols) and `F_DATA` (`51..56` symbols) for `N=1..32` CPEs. |
| **DL Tail Beacon (`F_BEACON`)** | `index 60` | `1` (`1.25%`) | `25.0 µs` | Secondary tail beacon (`fragments: 1`), bringing total DL to **`61` symbols (`76.25%`)**. |
| **UL Window (`F_RESERVE` + `F_DATA`)** | `index 0..18` | `19` (`23.75%`) | `475.0 µs` | `F_RESERVE` (`2..4` symbols for UL Contention / Ranging / Resource Requests) + `15..17` scheduled UL `F_DATA` symbols. |

---

## 2. `SimPy` Discrete-Event Comparison: `Stage 96A/97C` SMP Isolation vs Unpinned (`2.0 ms`, `750` Duty, `10x` `1024-QAM`)

Calibrated to `/sys/class/ame/ame_debug_dev/isr_giveup` (`checkpoint1 = 7,592`, `checkpoint2 = 12,938`, `checkpoint3 = 32,116` cycles on `500 MHz` `CPU0`, budget `1,000,000` cycles per `2.0 ms` superframe) and `Stage 97C` `GMAC0` + `ame-debug-sched` load tests (`174.861 -> 189.811 Mbps` SoC TCP, `2.617 -> 2.289 ms` `GMAC0` `p50` RTT):

| Active CPEs (`N`) | DL / UL Data Symbols (`80`-Sym Frame) | Unpinned (`smp_affinity=3`) Goodput (`Mbps`) | Isolated (`CPU0` TDMA / `CPU1` GMAC0) Goodput (`Mbps`) | Goodput Gain (`%`) | Unpinned $\rightarrow$ Isolated VoIP `p99` RTT (`ms`) | Unpinned $\rightarrow$ Isolated `CPU0` ISR Headroom (`%`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`N = 1`** | `56` DL / `17` UL | `140.976 Mbps` | **`152.987 Mbps`** | **`+8.52%`** | `2.990 ms` $\rightarrow$ **`2.637 ms`** | `96.670%` $\rightarrow$ **`98.075%`** |
| **`N = 8`** | `55` DL / `17` UL | `139.044 Mbps` | **`150.892 Mbps`** | **`+8.52%`** | `3.495 ms` $\rightarrow$ **`2.981 ms`** | `96.108%` $\rightarrow$ **`97.749%`** |
| **`N = 16`** | `53` DL / `16` UL | `133.251 Mbps` | **`144.605 Mbps`** | **`+8.52%`** | `4.586 ms` $\rightarrow$ **`3.888 ms`** | `95.468%` $\rightarrow$ **`97.383%`** |
| **`N = 32`** | `51` DL / `15` UL | `127.457 Mbps` | **`138.317 Mbps`** | **`+8.52%`** | `5.211 ms` $\rightarrow$ **`4.145 ms`** | `94.174%` $\rightarrow$ **`96.634%`** |

---

## 3. `pymoo` NSGA-II Multi-Objective Pareto Frontier (`pop_size=40, n_gen=25, seed=99`)

Evaluating all **`288` design configurations** (`frame_period_ms` $\in \{1.0, 2.0, 4.0\}$, `duty_cycle` $\in \{500, 670, 750\}$, `mod_order` $\in \{6\text{x}, 8\text{x}, 10\text{x}, 12\text{x}\}$, `N` $\in \{1, 8, 16, 32\}$, `smp_isolated` $\in \{\text{False}, \text{True}\}$) yielded **`13` unique Pareto-optimal solutions** (`3D Hypervolume = 437,888.948`), **100% of which have `smp_isolated = True`** (`0` `scheduler_giveup` / `symbol_giveup` deadline misses):

| Frame Period (`Symbols`) | Duty Cycle (`DL/UL`) | Modulation (`20 MHz` `2x2`) | Active CPEs (`N`) | SMP Isolated | DL + UL Goodput (`Mbps`) | VoIP `p50` / `p99` RTT (`ms`) | `CPU0` `p99` Cycles / Headroom (`%`) | Operational Regime (`CONFIRMED`) |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`4.0 ms` (`160` sym)** | `670` (`107/53`) | `12x (4096-QAM)` | `1` | `True` | **`189.573 Mbps`** (`126.4` DL / `63.2` UL) | `3.889` / `5.088 ms` | `23,621` (`98.819%`) | Maximum bulk PtP / low-N throughput (`3` fixed symbols = `1.88%` overhead). |
| **`4.0 ms` (`160` sym)** | `750` (`120/40`) | `12x (4096-QAM)` | `8` | `True` | **`188.334 Mbps`** (`141.3` DL / `47.1` UL) | `4.188` / `4.965 ms` | `28,113` (`98.594%`) | High-throughput `8`-CPE PtMP sector (`75/25` asymmetric DL). |
| **`2.0 ms` (`80` sym)** | `670` (`54/26`) | `12x (4096-QAM)` | `1` | `True` | **`180.899 Mbps`** (`121.4` DL / `59.5` UL) | `1.998` / **`2.701 ms`** | `18,590` (`98.141%`) | **Balanced Triple-Play Sweet Spot** (`500 Hz` superframe, `< 3 ms` VoIP `p99`). |
| **`2.0 ms` (`80` sym)** | `500` (`40/40`) | `10x (1024-QAM)` | `1` | `True` | **`152.987 Mbps`** (`73.4` DL / `79.6` UL) | `2.020` / **`2.420 ms`** | `17,261` (`98.274%`) | Symmetric `1024-QAM` backhaul (`3.75%` fixed beacon/preamble overhead). |
| **`1.0 ms` (`40` sym)** | `750` (`30/10`) | `12x (4096-QAM)` | `1` | `True` | **`163.553 Mbps`** (`123.9` DL / `39.6` UL) | `1.130` / **`1.467 ms`** | `16,306` (`96.739%`) | Ultra-low-latency (`1,000 Hz` superframe, `7.50%` fixed beacon/preamble overhead). |
| **`1.0 ms` (`40` sym)** | `500` (`20/20`) | `12x (4096-QAM)` | `1` | `True` | **`163.552 Mbps`** (`74.3` DL / `89.2` UL) | `1.123` / **`1.326 ms`** | `15,339` (`96.932%`) | Minimum VoIP `p99` jitter (`1.326 ms`) across the entire `288`-point design space. |

---

## 4. Verification Commands
```bash
python tools/sim/run_stage99b_ltu_80symbol_superframe_simpy_pymoo.py
pytest tests/test_stage99b_ltu_80symbol_superframe.py tests/test_00_deterministic_workflow_and_memory_gate.py -q
python tools/verify/enforce_5pillar_research_gate.py --check-repo
```
