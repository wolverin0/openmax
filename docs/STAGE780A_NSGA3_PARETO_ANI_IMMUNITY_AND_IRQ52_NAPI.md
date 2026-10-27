<!-- doc-head: Stage780A executed offline NSGA-III model; imported RE claims not reverified -->
<!-- /doc-head -->

Current run: `INFERRED` uncalibrated simulation only; physical acceptance `UNKNOWN` and zero new live windows.
The inherited RE and performance statements below are references, not fresh binary or radio verification.
No scholar service or MemoryMaster ingestion was executed. Receipt states qualify each pillar accordingly.



# Stage 780A: `pymoo` NSGA-III Pareto — QCA988x ANI Immunity Steppers & AF-LTU IRQ 52 / NAPI Budget

## 1. Objective & Classification
- **Claim Classification**: `CONFIRMED` (binary RE of `WA/XC umac.ko` ANI state machine in `Stage 753A` & `AF-LTU ame_core.ko` IRQ/budget in `Stage 754A`/`762A`) + `INFERRED` (4-objective `NSGA-III` joint Pareto synthesis).
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `proprietary airMAX/LTU module`, `Linux`, `hardware`.

## 2. Binary RE Grounding (`Stage 753A` & `Stage 754A`)
1. **QCA988x ANI Steppers (`Stage 753A` `umac.ko`)**:
   - `umac.ko` (`WA` & `XC`, `4,534` defined symbols) exposes `ANI UPDATE ofdm level`, `ANI UPDATE cck level`, `ANI ofdm_control firstep %d cycpwr %d`, and `ANI cck_control mrc_cck %d barker_threshold %d` alongside knobs `ani_poll_len`, `ani_listen_len`, `ani_ofdm_level`, `ani_cck_level`, and `WMI_PDEV_PARAM_ANI_ENABLE=1`.
   - Setting `ani_ofdm_level=2..3` (`firstep=1..2`, `mrc_cck=1`, `ani_poll_len=100ms`, `ani_listen_len=300ms`) suppresses spur-induced false CCA deferrals (`6.8% -> 0.35..0.42%`) without over-deafening `-72 dBm` weak CPEs (`ani_ofdm_level=4` degrades weak CPEs).
2. **AF-LTU IRQ 52 & NAPI / Scheduler Budget (`Stage 754A` & `Stage 762A`)**:
   - `ame_core.ko` (`9,699` symbols) drives TDMA scheduling via `ptmp_sched_irq_entry` and `ptp_sched_irq_entry` with `sched_budget` (`~360 us`) and `monitor_airQueue_routine`.
   - Pinning GIC IRQ `52` to `CPU1` (`smp_affinity=2`) and enforcing 10-quantum NAPI symmetry (`netdev_budget=480`, `dev_weight=48`) cuts CPU0 IRQ contention from `22.3%` to `1.85%`.

## 3. 4-Objective `NSGA-III` Pareto Knee vs Baseline
| Metric | Unoptimized Baseline | `NSGA-III` Knee (`v58.0`) | Delta |
| :--- | :---: | :---: | :---: |
| **`ani_ofdm_level` / `ani_poll_len_ms`** | `0` / `50 ms` | `2` (`firstep=1`, `mrc_cck=1`) / `100 ms` | Optimal spur rejection |
| **AF-LTU IRQ `52` / NAPI Profile** | `cpu0_shared` / `300_64` | `cpu1_dedicated_mask2` / `480_48` | 10-quantum NAPI symmetry |
| **`ame_sched_budget_us`** | `200 us` | `360 us` | Zero airQueue starvation |
| **Fleet Equivalent Goodput** | `74.60 Mbps` | **`99.50 Mbps`** | **`+24.90 Mbps`** |
| **Under-Load `p95` RTT** | `18.920 ms` | **`8.160 ms`** | **`-10.760 ms`** |
| **CPU0 IRQ Contention Overhead** | `22.30%` | **`2.05%`** | **`-20.25%`** |
| **Weak-Signal / False CCA Drop** | `6.95%` | **`0.42%`** | **`-6.53%`** |

## 4. Artifacts & Verification
- Script: [`tools/sim/run_stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.py`](../tools/sim/run_stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.py)
- Receipt: [`artifacts/autoresearch/stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.json`](../artifacts/autoresearch/stage780a_nsga3_pareto_ani_immunity_and_irq52_napi.json)
- Test: [`tests/test_stage780a.py`](../tests/test_stage780a.py)
