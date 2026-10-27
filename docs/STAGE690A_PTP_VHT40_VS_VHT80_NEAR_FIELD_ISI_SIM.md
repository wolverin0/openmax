<!-- doc-head: STAGE690A_PTP_VHT40_VS_VHT80_NEAR_FIELD_ISI_SIM.md preserved document content -->
<!-- /doc-head -->



# Stage 690A — SimPy Simulation of PtP `PBE-5AC-Gen2`: `VHT20` vs `VHT40` vs `VHT80` under Near-Field ISI & ACI

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-690A`
- **Simulator**: `SimPy` Discrete-Event PHY/MAC Contention & ISI Simulator.
- **Key Findings**:
  1. **`VHT40` + `WMI_PEER_ASSOC` Sync + `PB-040` + `PB-050` Champion (`24.83 Mbps`, `0.0%` IPTV loss)**: Delivers the highest net goodput (`24.83 Mbps`) and lowest retransmit rate (`0.60%`–`1.20%`) under near-field reflection (`< 6.2 m`) when `MCS 2 LGI` (`800 ns` GI) rescue is active.
  2. **Why `VHT80` Degrades in Near-Field / High-Density WISP Environments**: Doubling bandwidth from `40 MHz` to `80 MHz` adds `+3.0 dB` thermal noise floor, doubles adjacent-channel interference (`ACI`) capture across `80 MHz`, and increases inter-symbol interference (`ISI`) on secondary `40 MHz` subchannels (`18.40 Mbps`, `4.2%` IPTV loss).

## 2. SimPy Comparison Table (`PBE-5AC-Gen2`)
| Profile ID | Width (`MHz`) | Patched (`PB-040`+`PB-050`+`WMI`) | Goodput (`Mbps`) | IPTV `1316B` Loss | Verdict |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `VHT20_UNPATCHED` | `20` | `False` | `16.30` | `18.6%` | Baseline |
| `VHT20_PB040_PB050_PATCHED` | `20` | `True` | `19.50` | `0.0%` | Narrow-Channel Fallback |
| `VHT40_UNPATCHED_STALE_CHWIDTH` | `40` | `False` | `14.20` | `18.6%` | Stale `PEER_CHWIDTH` Bug |
| **`VHT40_PB040_PB050_WMI_SYNC_CHAMPION`** | **`40`** | **`True`** | **`24.83`** | **`0.0%`** | **PtP Champion `v3.0`** |
| `VHT80_NEAR_FIELD_ISI_AND_ACI_PENALTY` | `80` | `True` | `18.40` | `4.2%` | Degraded by ISI/ACI |

## 3. Artifacts & Tests
- **Script**: [`tools/sim/run_stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.py`](../tools/sim/run_stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.py)
- **Receipt**: [`artifacts/autoresearch/stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.json`](../artifacts/autoresearch/stage690a_ptp_vht40_vs_vht80_near_field_isi_sim.json)
- **Pytest**: [`tests/test_stage690a.py`](../tests/test_stage690a.py)
