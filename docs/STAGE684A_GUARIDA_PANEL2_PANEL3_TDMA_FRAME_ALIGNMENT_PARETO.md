<!-- doc-head: STAGE684A_GUARIDA_PANEL2_PANEL3_TDMA_FRAME_ALIGNMENT_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 684A — `SimPy` + `pymoo` `NSGA-II` Optimization of `Panel2 (.82)` + `Panel3 (.83)` Co-Channel & Adjacent-Channel TDMA Frame Alignment

## 1. Classification & Attribution
- **Claim Classification**: `INFERRED` (`SimPy` + `pymoo` `NSGA-II` co-location interference model parameterized by `CONFIRMED` `.82`/`.83` `netconf` timing windows)
- **Layer Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` TDMA frame sync) + `hardware` (Guarida tower near-field antenna coupling)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.
- **Receipt**: [`stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.json`](../artifacts/autoresearch/stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.json)
- **Simulation Script**: [`run_stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.py`](../tools/sim/run_stage684a_guarida_panel2_panel3_tdma_frame_alignment_pareto.py)

## 2. Tower Self-Interference Mechanism Between `Panel2 (.82)` & `Panel3 (.83)`
On the Guarida tower, `Panel2 (.82)` (`22` CPEs) runs `Fixed 10ms 50/50` (`down_dur = 4,880 us`, `up_dur = 4,370 us`), whereas `Panel3 (.83)` (`6` CPEs) runs an unaligned `Flexible` / split-brain cycle (`down_dur = 30,000 us`, `up_dur = 30,000 us`, `cbp_dur = 900 us`). Because both APs are mounted on the same tower mast:
- Whenever `.82` transmits Downlink (`+24 dBm`) while `.83` is listening for Uplink CPE bursts (or vice-versa), near-field mast coupling raises the receiving AP's noise floor and corrupts in-flight UL A-MPDUs and DL BlockAck frames.
- Even if both APs run `Fixed 10ms`, mismatching their DL/UL ratio (`67/33` vs `50/50`) creates a `1,700 us` (`17.0%`) TX-over-RX collision zone every `10 ms` frame (`4,880..6,580 us`).

## 3. `SimPy` + `pymoo` `NSGA-II` Co-Location Alignment Matrix
| Co-Location Alignment Profile | `.82` Frame / Ratio | `.83` Frame / Ratio | Phase Offset (`us`) | AP-to-AP `TX/RX` Overlap (`%`) | `.82` DL / UL (`Mbps`) | `.83` DL / UL (`Mbps`) | Tower Total Goodput (`Mbps`) | Tower Gain vs Current |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`Current_Unaligned_82_50_50_vs_83_SplitBrain`** | `10ms 50/50` | `Unaligned Flex` | `2,300` | **`43.15%`** | `29.27` / `28.56` | `37.16` / `24.13` | `119.12` | `0.00%` (baseline) |
| **`Mismatched_Ratio_82_67_33_vs_83_50_50`** | `10ms 67/33` | `10ms 50/50` | `0` | `17.00%` | `40.78` / `20.83` | `35.14` / `24.85` | `121.60` | `+2.08%` |
| **`Phase_Shifted_10ms_67_33_2500us_Offset`** | `10ms 67/33` | `10ms 67/33` | `2,500` | `37.40%` | `39.67` / `15.58` | `44.97` / `13.59` | `113.81` | `-4.46%` |
| **`Synchronized_8ms_67_33_Both_Panels`** | `8ms 67/33` | `8ms 67/33` | `0` | **`0.00%`** | `41.59` / `19.60` | `47.16` / `17.09` | `125.44` | **`+5.31%`** |
| **`Synchronized_10ms_67_33_Champion_0us_Offset`** | **`10ms 67/33`** | **`10ms 67/33`** | **`0`** | **`0.00%`** | **`41.78` / `20.83`** | **`47.38` / `18.16`** | **`128.15`** | **`+7.58%`** |

## 4. Engineering Verdict
Aligning both `Panel2 (.82)` and `Panel3 (.83)` (while on `airOS 8` TDMA) to identical **`Fixed 10ms 67/33`** boundaries (`down_dur = 6,580 us`, `up_dur = 2,670 us`, `0.00%` TX/RX overlap) eliminates the `43.15%` AP-to-AP TX/RX collision window, boosting `.82` DL goodput by **`+42.74%` (`29.27 -> 41.78 Mbps`)** and total 2-sector tower goodput by **`+7.58%` (`119.12 -> 128.15 Mbps`)**.
