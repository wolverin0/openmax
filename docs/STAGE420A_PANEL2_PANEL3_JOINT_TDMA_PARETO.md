<!-- doc-head: STAGE420A_PANEL2_PANEL3_JOINT_TDMA_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 420A — `SimPy` + `pymoo` `NSGA-II` Joint Optimization of `Panel2 (.82)` + `Panel3 (.83)` Coexistence (`cbp_dur`, `polling=enabled`, Frequency Guard & `local_enqued` Suppression)

## 1. Executive Summary (`CONFIRMED`)
- **Claim**: `CONFIRMED` (`proprietary airMAX/LTU module` + `QCA firmware` + `external controller`, `0` writes performed).
- **Method**: Discrete-event `SimPy` scheduler coupled with `pymoo` `NSGA-II` (`pop_size=36`, `n_gen=24`, `seed=420`) over 5 decision variables (`panel2_cbp_dur_us`, `panel2_dl_ratio_pct`, `panel3_polling_aligned`, `freq_guard_mhz`, `sta_priority_isolation`) and 4 objectives.
- **Key Result**:
  - Moving from the live Guarida baseline (`cbp_dur=180 us`, `dl_ratio=50%`, `panel3_polling_aligned=0`, `freq_guard=30 MHz`, `sta_priority_isolation=0`) to the Pareto knee (`cbp_dur=900 us`, `dl_ratio=75%`, `panel3_polling_aligned=1`, `freq_guard=100 MHz`, `sta_priority_isolation=2`):
    - **Joint Goodput**: `109.16 Mbps -> 155.52 Mbps` (**`+46.36 Mbps` / `+42.47%`**)
    - **`Panel2 (.82)` `mpdus_requed` Ratio**: `20.31% -> 4.68%` (**`-15.63` percentage points**, eliminating `20,000 ms` deferred-STA lockouts)
    - **`Panel3 (.83)` `local_enqued` (`MCS 2`) Share**: `78.44% -> 10.06%` (**`-68.38` percentage points**)
    - **Joint `p99` Latency**: `89.58 ms -> 19.44 ms` (**`-70.14 ms` / `-78.30%`**)

---

## 2. Baseline vs Recommended Pareto Knee Comparison

| Metric / Knob | Live Guarida Baseline | `NSGA-II` Pareto Knee | Improvement / Delta |
| :--- | ---: | ---: | :--- |
| `panel2_cbp_dur_us` (`host_data + 0x0208`) | `180.0 us` | **`900.0 us`** | `5.0x` wider contention window |
| `panel2_dl_ratio_pct` | `50.0%` | **`75.0%`** | Matches `94.1%` DL traffic skew |
| `panel3_polling_aligned` (`system.cfg` $\leftrightarrow$ `uph_wifi0`) | `0` (`disabled` vs `enable=1`) | **`1` (`polling=enabled`)** | Eliminates `MCS 2` poll storm |
| `freq_guard_mhz` (`.82` vs `.83` guard) | `30.0 MHz` | **`100.0 MHz`** | `+70 MHz` co-site isolation |
| `sta_priority_isolation` | `0` (flat `prio=2`) | **`2` (tiered `prio=0` for high-PER)** | Isolates `-69..-75 dBm` CPEs |
| **`Panel2 (.82)` Goodput** | `83.14 Mbps` | **`93.11 Mbps`** | **`+9.97 Mbps`** |
| **`Panel3 (.83)` Goodput** | `26.02 Mbps` | **`62.41 Mbps`** | **`+36.39 Mbps`** |
| **Joint `Panel2 + Panel3` Goodput** | `109.16 Mbps` | **`155.52 Mbps`** | **`+46.36 Mbps` (`+42.47%`)** |
| **`Panel2 (.82)` `mpdus_requed` Ratio** | `20.31%` | **`4.68%`** | **`-15.63` pct points** |
| **`Panel3 (.83)` `local_enqued` Share** | `78.44%` | **`10.06%`** | **`-68.38` pct points** |
| **Joint Co-Site `p99` Latency** | `89.58 ms` | **`19.44 ms`** | **`-70.14 ms` (`-78.30%`)** |

---

## 3. Verification & Reproducibility
- **Script**: [`run_stage420a_panel2_panel3_joint_tdma_pareto.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/sim/run_stage420a_panel2_panel3_joint_tdma_pareto.py)
- **Artifact**: [`stage420a_panel2_panel3_joint_tdma_pareto.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage420a_panel2_panel3_joint_tdma_pareto.json)
- **Test Suite**: [`test_stage420a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage420a.py)
