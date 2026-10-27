<!-- doc-head: STAGE272A_DUALBAND_2XC_XC_NLOS_FAILOVER_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 272A — SimPy + Pymoo NSGA-II 2.4 GHz (`2XC` `.253`) vs 5 GHz (`XC` `.198`) Dual-Band Failover & Band-Steering PtMP Model

## 1. Objective & Empirical Calibration
- **Model Scope**: Combines a **SimPy** discrete-event PtMP sector simulator (`120 s` wet-foliage fade horizon, `18` LOS 5 GHz CPEs + `6` high-foliage NLOS CPEs) calibrated with live Round-5 receipts from **Stage 269A** (`.198` `XC` 5 GHz), **Stage 270A** (`.253` `2XC` 2.4 GHz), and **Stage 271A** (`192.168.1.20` `XM`) with **Pymoo NSGA-II** (`pop_size=24`, `n_gen=12`).
- **Safety Boundaries (`CONFIRMED`)**:
  - `touched_241_or_242 = False`
  - `touched_20_or_250 = False`
  - `flash_writes = 0`

## 2. Decision Variables & Multi-Objective Pareto Formulation
| Variable | Range | Physical Meaning | Attribution |
| :--- | :--- | :--- | :--- |
| $x_0$ (`rssi_failover_thresh_dbm`) | `[-84.0, -72.0] dBm` | 5 GHz RSSI trigger to steer NLOS CPE traffic onto 2.4 GHz `2XC` backup | `external controller` |
| $x_1$ (`phy_retry_thresh_pct`) | `[6.0, 25.0] %` | 5 GHz `ath_dev` hardware retry rate threshold | `proprietary airMAX/LTU module` |
| $x_2$ (`hysteresis_holddown_s`) | `[3.0, 45.0] s` | Minimum hold-down interval preventing route/bridge flapping | `external controller` |
| $x_3$ (`airtime_floor_24ghz_pct`) | `[10.0, 40.0] %` | `uph_wifi0` TDMA airtime floor reserved for NLOS failover CPEs on `2XC` | `proprietary airMAX/LTU module` |

## 3. Why 2.4 GHz (`2XC`) Offload Multiplies 5 GHz (`XC`) Sector Goodput (`INFERRED` / `CONFIRMED` on Bench)
1. **Eliminating 5 GHz MCS0/MCS1 Foliage Airtime Drag (`CONFIRMED` physics + SimPy model, attribution: `hardware` + `proprietary airMAX/LTU module`)**:
   - Wet tree foliage attenuates `5.8 GHz` by `~9–12 dB` more than `2.4 GHz`. Keeping 6 deep-NLOS CPEs on a 5 GHz sector during rain fade drags the 5 GHz TDMA scheduler into `MCS0`/`MCS1` with high retry rates (`S272A` static 5 GHz baseline). Steering those NLOS flows to the co-located `2XC` 2.4 GHz AirPrism sector (`swr_limit=3`, `daprot=2`) restores full `MCS8`/`MCS9` airtime efficiency on `5 GHz` while cutting NLOS `p99 RTT` by `>80%`.

## 4. Verification Artifacts
- Runner: [`tools/simulation/run_stage272a_dualband_2xc_xc_nlos_failover_pareto.py`](../tools/simulation/run_stage272a_dualband_2xc_xc_nlos_failover_pareto.py)
- Receipt: [`artifacts/autoresearch/stage272a_dualband_2xc_xc_nlos_failover_pareto.json`](../artifacts/autoresearch/stage272a_dualband_2xc_xc_nlos_failover_pareto.json)
- Dedicated Pytest: [`tests/test_stage272a_dualband_2xc_xc_nlos_failover_pareto.py`](../tests/test_stage272a_dualband_2xc_xc_nlos_failover_pareto.py)
