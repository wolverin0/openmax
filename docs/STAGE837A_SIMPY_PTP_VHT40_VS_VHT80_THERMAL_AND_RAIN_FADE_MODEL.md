<!-- doc-head: Stage 837A offline SimPy PtP fade-margin & MCS-stability model, VHT40 vs VHT80, 2-15 km, nominal vs stressed link; shows VHT80 3 dB noise penalty costs range -->
<!-- /doc-head -->
# Stage 837A — SimPy PtP VHT40 vs VHT80 Thermal + Rain-Fade Model (2–15 km)

- **Claim Status**: `CONFIRMED` (offline model)
- **Attribution**: `external controller (offline model)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage837a_simpy_ptp_vht40_vs_vht80_thermal_and_rain_fade_model.json`
- **Tool**: `tools/sim/run_stage837a_simpy_ptp_vht40_vs_vht80_thermal_and_rain_fade_model.py`

## 1. What it models
A PowerBeam 5AC Gen2–class PtP hop at 5.5 GHz as a SimPy discrete-event process:
free-space path loss + ITU-R P.838-style rain attenuation + thermal noise →
instantaneous SNR → highest sustainable 1-stream VHT MCS. A 3-state Markov rain
process (clear/light/heavy, exponential dwell) drives time-varying fade over a
24 h simulation sampled every 10 s. Deterministic (seeded).

## 2. Link budget (model constants)
| Parameter | Value |
| :--- | :--- |
| Frequency | 5.5 GHz |
| Tx power | 25 dBm |
| Antenna gain (per end) | 25 dBi |
| Noise figure | 6 dB |
| "Stable" target | ≥ MCS4 |
| VHT80 vs VHT40 noise penalty | **+3.01 dB** (double bandwidth) |

Two link conditions are swept: **nominal** (`system_loss = 8 dB`, well-aligned
dishes) and **stressed** (`system_loss = 20 dB`, cable/pointing/atmospheric
degradation).

## 3. Key results
**Nominal**: both widths hold 100 % MCS-stability across the whole 2–15 km range;
rain at 5.5 GHz is negligible (heavy 30 mm/h over a 15 km path ≈ 1.4 dB). VHT80 is
the clear winner here — ~2× PHY rate at identical stability.

**Stressed** (where the 3 dB penalty bites):
| Distance | VHT40 stability | VHT40 rate | VHT80 stability | VHT80 rate |
| :--- | :--- | :--- | :--- | :--- |
| 6 km | 100 % | 121 Mbps | 100 % | 176 Mbps |
| 8 km | 100 % | 81 Mbps | 97.5 % | 174 Mbps |
| 10 km | 100 % | 81 Mbps | **0 %** | 117 Mbps |
| 12 km | 98.9 % | 81 Mbps | 0 % | 116 Mbps |
| 15 km | 0 % | 54 Mbps | 0 % | 88 Mbps |

- **VHT80 stability crossover**: 8 km (first distance where VHT80 falls below VHT40).
- **100 %-stable range**: VHT40 = 10 km, VHT80 = 6 km.

## 4. Engineering takeaway
VHT80 doubles throughput where the link is strong (short range / clean alignment)
but its +3 dB noise-bandwidth penalty costs ~2–4 km of usable range under system
loss. The decision rule the sim supports: **VHT80 for short, well-aligned hops;
VHT40 to extend range or when alignment/atmospheric margin is uncertain.** Rain
fade is a second-order effect at 5.5 GHz — distance and system loss dominate.

## 5. Reproduce
```sh
python tools/sim/run_stage837a_simpy_ptp_vht40_vs_vht80_thermal_and_rain_fade_model.py
python -m pytest tests/test_stage837a.py -q
```

## 6. Limits
Model, not measurement: single-stream MCS thresholds and ITU rain coefficients are
nominal literature values; multipath, interference, and MIMO spatial-stream gains
are out of scope. Use for width/range planning intuition, not link certification.
