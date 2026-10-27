<!-- doc-head: STAGE738A_GUARIDA_PANEL2_ACTIVITY_AGING_AND_CBP_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 738A — `SimPy` + `pymoo` `NSGA-II` Evaluation of `activity_aging` (`3.0s` vs `1.5s`) + `cbp_dur` + `Fixed 10ms 67/33` on `Panel2 (.82)` (`22` CPEs)

## 1. Classification & Attribution
- **Claim Classification**: `INFERRED` (`SimPy` + `pymoo` `NSGA-II` model parameterized by `CONFIRMED` `0x00d244` & `0x0149b0` binary equations)
- **Layer Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `activity_aging` & `ff_cbp_slots`)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Receipt**: [`stage738a_guarida_panel2_activity_aging_and_cbp_pareto.json`](../artifacts/autoresearch/stage738a_guarida_panel2_activity_aging_and_cbp_pareto.json)
- **Simulation Script**: [`run_stage738a_guarida_panel2_activity_aging_and_cbp_pareto.py`](../tools/sim/run_stage738a_guarida_panel2_activity_aging_and_cbp_pareto.py)

## 2. Joint `activity_aging` + `ff_cbp_slots` + `Fixed 10ms 67/33` Co-Design
In `ubnt_poll_host_init_ptmp_netconf` (`0x00d864: mul $t0, ff_cbp_slots, cbp_dur_slot`), `cbp_dur` is deducted from `up_dur` (`up_dur = gross_ul - 450 - cbp_dur`), while `activity_aging` (`0x1c($s0)`) determines how long a station occupies one of the `4` (`0xfe($s0)`) UL poll slots after a short burst:
- If `ff_dl_alloc` is raised from `50%` to `67%` without adjusting `activity_aging` (`3,000 ms`), `2.4` false-active idle stations per frame consume `446.4 us` (`16.72%` of `up_dur`).
- Simultaneously, keeping `ff_cbp_slots = 3` (`cbp_dur = 180 us`) causes a `20.31%` contention/deferral rate (`FMX-DISC-45`) among warm-idle stations trying to request UL bandwidth.
- Reducing `activity_aging` from `3,000 ms` to **`1,500 ms`** reclaims `241.8 us/frame` of wasted empty-poll airtime, which more than pays for expanding `ff_cbp_slots` from `3` (`180 us`) to **`4` (`240 us`)** (`+60 us`), yielding a net **`+181.8 us/frame` increase in active UL payload airtime** while cutting CBP contention collisions nearly in half!

## 3. `SimPy` + `pymoo` `NSGA-II` Evaluation Matrix Across 5 Profiles
| Candidate Profile | `ff_dl_alloc` | `activity_aging` (`ms`) | `ff_cbp_slots` / `cbp_dur` (`us`) | `down_dur` / `up_dur` (`us`) | Empty-Poll Waste (`us`) | Net Active UL (`us`) | CBP Collision Rate (`%`) | Sim DL / UL (`Mbps`) | `p95` Wake-Up Latency (`ms`) | Wake-Up Latency Reduction |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Current_82_10ms_50_50_Aging3000_CBP180`** | `50%` | `3,000` | `3` (`180 us`) | `4,880` / `4,370` | `595.2` | `3,504.8` | `20.31%` | `30.91` / `34.17` | `52.89 ms` | `0.00%` (baseline) |
| **`Candidate_10ms_67_33_Aging3000_CBP180`** | `67%` | `3,000` | `3` (`180 us`) | `6,580` / `2,670` | `446.4` | `1,983.6` | `20.31%` | `41.68` / `19.34` | `49.53 ms` | `-6.35%` |
| **`Candidate_10ms_67_33_Aging1500_CBP180`** | `67%` | `1,500` | `3` (`180 us`) | `6,580` / `2,670` | `204.6` | `2,030.4` | `20.31%` | `41.68` / `19.80` | `44.07 ms` | `-16.68%` |
| **`Champion_10ms_67_33_Aging1500_CBP240`** | **`67%`** | **`1,500`** | **`4` (`240 us`)** | **`6,580` / `2,610`** | **`204.6`** | **`1,970.4`** | **`11.93%`** | **`41.68` / `19.21`** | **`31.92 ms`** | **`-39.65%` (Champion)** |
| **`HighCBP_10ms_67_33_Aging1500_CBP300`** | `67%` | `1,500` | `5` (`300 us`) | `6,580` / `2,550` | `204.6` | `1,910.4` | `7.90%` | `41.68` / `18.63` | `26.08 ms` | `-50.69%` |
