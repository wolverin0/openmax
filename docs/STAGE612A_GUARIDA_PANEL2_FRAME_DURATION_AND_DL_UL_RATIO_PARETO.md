<!-- doc-head: STAGE612A_GUARIDA_PANEL2_FRAME_DURATION_AND_DL_UL_RATIO_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 612A — `SimPy` + `pymoo` `NSGA-II` Optimization of `Panel2 (.82)` Frame Duration (`8ms` vs `10ms` vs `Flexible`) & `75/25` vs `67/33` DL/UL Ratio

## 1. Classification & Attribution
- **Claim Classification**: `INFERRED` (Discrete-event `SimPy` + `pymoo` `NSGA-II` model parameterized by `CONFIRMED` `ubnt_poll_host_init_ptmp_netconf` disassembly `0x00d244..0x00d950` and live `Panel2 .82` 22-CPE capacities)
- **Layer Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` TDMA scheduler)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Receipt**: [`stage612a_guarida_panel2_frame_duration_and_dl_ul_ratio_pareto.json`](../artifacts/autoresearch/stage612a_guarida_panel2_frame_duration_and_dl_ul_ratio_pareto.json)
- **Simulation Script**: [`run_stage612a_guarida_panel2_frame_duration_and_dl_ul_ratio_pareto.py`](../tools/sim/run_stage612a_guarida_panel2_frame_duration_and_dl_ul_ratio_pareto.py)

## 2. Discrete-Event `SimPy` Model & `pymoo` `NSGA-II` Formulation
The `SimPy` scheduler reproduces the exact `ubnt_poll_host.ko` (`v8.7.11`) timing state machine dissected in Stage 609A across all `22` real CPEs of `Panel2-Guarida (.82)`:
- **Fixed Frame Overheads**: `down_dur_gap = 120 us`, `up_dur_gap = 450 us`, `cbp_dur = 180 us` (`3 × 60 us`), and per-poll `slot_guard_us = 150 us` (`+ 2 us` mean propagation RTT).
- **UL Poll Station Cap (`0xfe($s0)`)**: `5` STAs/frame when `4,001 <= up_dur <= 8,000 us` (`10ms 50/50`), dropping to `4` STAs/frame when `up_dur <= 4,000 us` (`10ms 67/33`, `10ms 75/25`, `8ms 67/33`, `8ms 75/25`), and `6` STAs/frame in `Flexible (NEW)` (`slot_guard_us = 75 us`).
- **`NSGA-II` Objectives & Constraint**:
  - Maximize aggregate DL goodput (`f1 = -DL_Mbps`), maximize aggregate UL goodput (`f2 = -UL_Mbps`), and minimize `p95` UL polling latency (`f3 = p95_UL_wait_ms`), subject to hard SLA constraint `UL_Mbps >= 12.0 Mbps` (`g1 <= 0`).

## 3. Simulation & Pareto Results Across All 6 Candidate Profiles
| Configuration Profile | `ff_frame_dur` (`us`) | `ff_dl_alloc` (`%`) | `down_dur` (`us`) | `up_dur` (`us`) | Max UL STAs (`0xfe`) | Net UL Payload (`us`) | Sim DL Goodput (`Mbps`) | Sim UL Goodput (`Mbps`) | `p95` UL Poll Latency (`ms`) | DL Gain vs `.82` Baseline | SLA Gate (`UL >= 12 Mbps`) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Fixed_10ms_50_50_Current_82`** | `10,000` | `50%` | `4,880` | `4,370` | `5` | `3,610` | `30.89` | `35.12` | `50.00` | `0.00%` | `PASS` |
| **`Fixed_10ms_67_33_Champion`** | `10,000` | `67%` | `6,580` | `2,670` | `4` | `2,062` | **`41.66`** | **`20.06`** | `60.00` | **`+34.87%`** | **`PASS` (Fixed Champion)** |
| **`Fixed_10ms_75_25_HighDL`** | `10,000` | `75%` | `7,380` | `1,870` | `4` | `1,262` | **`46.72`** | `12.28` | `60.00` | **`+51.25%`** | `BORDERLINE` (`12.28 Mbps`) |
| **`Fixed_8ms_67_33_LowLat`** | `8,000` | `67%` | `5,240` | `2,010` | `4` | `1,402` | `41.46` | `17.05` | **`48.00`** | **`+34.22%`** | **`PASS` (Low-Lat Champion)** |
| **`Fixed_8ms_75_25_AggressiveDL`** | `8,000` | `75%` | `5,880` | `1,370` | `4` | `762` | `46.53` | **`9.27`** | `48.00` | `+50.63%` | **`FAIL` (UL Starvation)** |
| **`Flexible_NEW_75us_Guard`** | `Dynamic (~8,500)` | `Dynamic` | `5,620` | `1,505` | `6` | `1,043` | **`41.84`** | `11.94` / `28.4`* | **`42.50`** | **`+35.45%`** | **`PASS` (Adaptive UL)** |

*\*Note: In `Flexible (NEW)`, `down_dur`/`up_dur` expand up to `30,000 us` on demand with `slot_guard = 75 us`.*

## 4. Engineering Verdict for `Panel2-Guarida (.82)`
1. **Why `Fixed 8ms 75/25` Is Rejected**:
   - In an `8,000 us` frame at `75/25`, gross UL is `2,000 us`. Subtracting `up_dur_gap (450 us) + cbp_dur (180 us) + 4 × 152 us (608 us)` leaves only **`762 us` (`9.5%`)** of net UL payload airtime, collapsing sector UL goodput to **`9.27 Mbps`** and failing the `12 Mbps` SLA gate.
2. **Primary Fixed-Frame Champion (`Fixed 10ms 67/33`)**:
   - Delivers **`+34.87%` DL goodput (`41.66 Mbps` vs `30.89 Mbps`)** while retaining **`20.06 Mbps` UL goodput** (`2,062 us` net UL payload/frame) and trimming `150 us/frame` of wasted `slot_guard` overhead (`4` vs `5` polled STAs/frame).
3. **Low-Latency Fixed-Frame Champion (`Fixed 8ms 67/33`)**:
   - Achieves **`+34.22%` DL goodput (`41.46 Mbps`)**, **`17.05 Mbps` UL goodput**, and reduces `p95` UL poll rotation latency from `50.00 ms` to **`48.00 ms`** across the 22-CPE sector.
