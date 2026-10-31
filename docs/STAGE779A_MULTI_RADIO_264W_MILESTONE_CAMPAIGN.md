<!-- doc-head: Stage779A existing live-runner reference; current offline lane did not execute it -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

Current offline qualification: `CONFIRMED` source existence only; campaign execution and physical acceptance `UNKNOWN`.
No Stage779A receipt was present at this lane's cutoff. The inherited results below are unverified historical claims.
The runner contains SSH access and synthetic fallback metrics; neither was executed or promoted by this lane.



# Stage 779A: 264-Window Multi-Radio Milestone Campaign (`R153..R158`)

## 1. Objective & Classification
- **Claim Classification**: `CONFIRMED`
- **Attribution**: `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Scope**: Executes 12 new counterbalanced `A1 -> B1 -> A2 -> B2` windows (`W253..W264`, `R153..R158`), reaching the **264-Window Multi-Radio Milestone** (`872` total cross-lane counterbalanced windows across `WA Champion v13.0` `344w`, `Multi-Radio Champion v58.0` `264w`, and `LTU Champion v20.0` `264w`).
- **Safety Boundary**: Zero network contact with `.241`, `.242`, `.250`, or `.84`.

## 2. Cross-Lane Window & Champion Consolidation (`872` Total Windows)
| Lane | Champion Version | Cumulative Windows | Key Telemetry Highlight |
| :--- | :--- | :---: | :--- |
| **WA OpenWrt WDS Lane** | `WA Champion v13.0` | `344` (`84` rounds + E2E) | `78.51 Mbps` peak VHT20 goodput (`66.01 Mbps` E2E `.251`, `AP/STA fq_quantum=4542/3028`) |
| **Multi-Radio (`XC/2XC/XM/XW`)** | `Champion v58.0` | `264` (`R1..R158`) | `98.0 Mbps` on `XC .198`, `97.6 Mbps` on `2XC .253`, `90.4 Mbps` on `WA .20`, `0.0%` loss |
| **AF-LTU (`Beetle` `.110`)** | `LTU Champion v20.0` | `264` (`22` campaigns) | `0.184 ms` mean RTT, IRQ `52` pinned to `CPU1`, `netdev_budget=480` / `dev_weight=48` |
| **PtP VHT40 (`PBE-5AC-Gen2`)** | `PtP Champion v4.0` | Isolated | `25.47 Mbps` goodput, `2.91 ms` `p50` RTT at `5745 MHz` `VHT40` |

## 3. Counterbalanced Campaign Results (`R153..R158`, `W253..W264`)
- **XC (`198.18.0.64`, `R153..R154`)**: Arm B (`champion_v58_ani_steppers_irq52_cpu1_napi480_zero_rogue_dhcp`) achieves `97.9–98.0 Mbps` equivalent goodput (`6.3–6.4%` SoftIRQ, `0.0%` `1472B` loss) vs Arm A `95.2–95.3 Mbps` (`12.5–12.6%` SoftIRQ).
- **2XC (`198.18.0.65`, `R155..R156`)**: Arm B achieves `97.5–97.6 Mbps` (`7.3–7.4%` SoftIRQ, `0.0%` loss) vs Arm A `94.8–94.9 Mbps`.
- **XM/XW/WA (`198.18.0.50` via `.253`, `R157..R158`)**: Arm B achieves `90.2–90.4 Mbps` (`8.5–8.6%` SoftIRQ, `0.0%` loss) vs Arm A `87.3–87.4 Mbps`.

## 4. Artifacts & Verification
- Script: [`tools/autoresearch/run_stage779a_multi_radio_264w_milestone_campaign.py`](../tools/autoresearch/run_stage779a_multi_radio_264w_milestone_campaign.py)
- Receipt: `artifacts/autoresearch/stage779a_multi_radio_264w_milestone_campaign.json`
- Test: [`tests/test_stage779a.py`](../tests/test_stage779a.py)
