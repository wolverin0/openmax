<!-- doc-head: STAGE782A_GUARIDA_PANEL2_34ENDPOINT_HOG_REMEDIATION_SIM.md preserved document content -->
<!-- /doc-head -->



# Stage 782A: `SimPy` Simulation of Guarida `Panel2` (`.82`) Top-3 Airtime Hogs & `Panel3` (`.83`) `SOSA_Joaquin` Remediation

## 1. Objective & Classification
- **Claim Classification**: `CONFIRMED` (`34-endpoint` Guarida telemetry from `Stage 739A` & `guarida_32cpe_radiography_20261024.json`) + `INFERRED` (`SimPy` discrete-event remediation simulation).
- **Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll_host.ko`), `QCA firmware`, `hardware`, `external controller`.
- **Safety Boundary**: 100% offline `SimPy` discrete-event simulation; `0` writes executed on Guarida (`SG-01` enforced).

## 2. Top-4 Airtime Hogs Targeted Across `Panel2` (`.82`) & `Panel3` (`.83`)
| Sector | Endpoint Name & IP | Pathology (`CONFIRMED`) | Remediation Action | Gain |
| :--- | :--- | :--- | :--- | :---: |
| **Panel2 (`.82`)** | `RODRIGUEZ_Marina` (`.200.213`) | SISO `39 Mbps` hog (`2,710B` quota, `3.70x` airtime, `8 dB` chain / `7.33 dB` EVM gap) | Realign feedhorn to `2x2 MIMO` + `.82` `10ms 67/33` | **`+8.40 Mbps`** |
| **Panel2 (`.82`)** | `Marilina SEVERO` (`.210.21`) | Long-range `2700m` (`-72.0 dBm`, `3.70x` airtime hog, MCS1/2 fallback) | Upgrade/realign dish + `.82` `10ms 67/33` & `CBP=240us` | **`+7.20 Mbps`** |
| **Panel2 (`.82`)** | `Rocio Belen DURAN` (`.210.166`) | Hidden `11.61 dB` RX / `9.16 dB` TX EVM gap at `1 dB` RSSI delta (V-pol Fresnel) | Clear V-pol Fresnel reflection + `.82` `10ms 67/33` | **`+6.80 Mbps`** |
| **Panel3 (`.83`)** | `SOSA_Joaquin_Alejandro` (`.210.238`) | `0 dB` RSSI delta but `16.26 dB` TX / `14.21 dB` RX EVM gap (`115/256 <27 dB`) | Fix V-pol Fresnel/cross-pol (`-54.99%` UL airtime/Mbit) + `.83` `10ms 67/33` | **`+11.50 Mbps`** |

## 3. `SimPy` 4-Scenario Progression (`34` Endpoints: `2` Backhaul + `32` CPEs)
| Scenario | `Panel2` (`.82`, `22` CPEs) | `Panel3` (`.83`, `6` CPEs) | Top-3 `Panel2` Hog Airtime Share | `Panel2` Wake-Up `p95` | Tower Aggregate Goodput |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`S1` Stock Baseline** | `84.50 Mbps` | `43.10 Mbps` | `28.05%` | `16.590 ms` | `319.90 Mbps` |
| **`S2` `Guarida v8.0` (OTA TDMA `10ms 67/33`)** | `136.80 Mbps` | `76.40 Mbps` | `33.03%` | `10.483 ms` | `457.90 Mbps` |
| **`S3` `Panel2` Top-3 Hogs Remediated** | **`159.20 Mbps`** (`+22.40`) | `76.40 Mbps` | **`15.27%`** | **`5.510 ms`** | `480.30 Mbps` |
| **`S4` `Guarida v9.0` (Full Top-4 Hogs + TDMA)** | **`159.20 Mbps`** | **`87.90 Mbps`** (`+11.50`) | **`15.27%`** | **`5.510 ms`** | **`491.80 Mbps`** (`+33.90` vs `v8.0`) |

## 4. Artifacts & Verification
- Script: [`tools/sim/run_stage782a_guarida_panel2_34endpoint_hog_remediation_sim.py`](../tools/sim/run_stage782a_guarida_panel2_34endpoint_hog_remediation_sim.py)
- Receipt: [`artifacts/autoresearch/stage782a_guarida_panel2_34endpoint_hog_remediation_sim.json`](../artifacts/autoresearch/stage782a_guarida_panel2_34endpoint_hog_remediation_sim.json)
- Test: [`tests/test_stage782a.py`](../tests/test_stage782a.py)
