<!-- doc-head: Stage 481A Fraunhofer Near-Field (< 2*D^2/lambda = 6.15m for 400mm Dish) vs Far-Field Automatic Detector and VHT Policy Switch -->
Reconciles Stage 105A and Stages 425A–429A live `PBE-5AC-Gen2` (`400 mm` dish) measurements with Fraunhofer aperture physics (`2*D^2/lambda = 6.19 m` at `5.8 GHz`) and builds the automatic near-field vs far-field VHT rate/GI/NSS policy switch.
<!-- /doc-head -->

# Stage 481A — Fraunhofer Near-Field (`< 6.15 m` for `400 mm` Dish) vs Far-Field Automatic Detector & VHT Policy Switch

- **Epistemic Status**: `CONFIRMED` (Live counterbalanced bench sweeps in `Stages 105A` & `425A–429A` + electromagnetic aperture physics)
- **Attribution**: `hardware` (`400 mm` parabolic dish radiative near-field phase curvature & indoor standing-wave cavity) · `QCA firmware`
- **Generator**: [`build_stage481a_nearfield_fraunhofer_dish_cavity_compensator.py`](../tools/observability/build_stage481a_nearfield_fraunhofer_dish_cavity_compensator.py)
- **JSON Receipt**: [`stage481a_nearfield_fraunhofer_dish_cavity_compensator.json`](../artifacts/autoresearch/stage481a_nearfield_fraunhofer_dish_cavity_compensator.json)

---

## 1. Reconciling `Stage 105A` and `Stages 425A–429A`: Why `400 mm` Dishes Behave Differently Below `6.15 m`

For a `PowerBeam 5AC Gen2` (`D_eff = 0.400 m` reflector, `420 mm` housing) operating at `5805 MHz` (`lambda = 0.05168 m`):
- **Reactive Near-Field Boundary**: $R_1 = 0.62 \sqrt{D^3 / \lambda} = \mathbf{0.692\text{ m}}$
- **Fraunhofer Far-Field Boundary**: $R_F = \frac{2 D^2}{\lambda} = \mathbf{6.19\text{ m}}$ (`~6.15 m` across `5.7–5.8 GHz`)

When two `400 mm` dishes are placed `1–3 m` apart on a bench (`< 6.15 m` Fraunhofer limit) and angled off-axis:
1. **Refutation of LNA Front-End Overload (`Stage 426A`)**: Lowering TX power to `4–8 dBm` caused **`100%` packet loss**, while `12 dBm` yielded `-65 dBm` (Chain 1) / `-74 dBm` (Chain 0) (`9 dB` imbalance). Off-axis placement couples via sidelobes (`~75–85 dB` path loss), so **`txpower >= 18–20 dBm`** is required to keep the weaker chain above noise.
2. **Coherence Bandwidth Limit (`Stage 427A`)**: Standing-wave reflections between the two `400 mm` metal dishes create frequency notches every `15–25 MHz`. Consequently, `VHT40` and `VHT80` fail association (`100%` loss), whereas **`VHT20`** locks cleanly with **`0.0%` loss on `1472 B`**.
3. **Asymmetric Constellation Ceiling (`Stage 425A`)**: Quadratic phase error across the dish surface bounds EVM even at high SNR, making **`AP VHT-MCS 3 (16-QAM) / STA VHT-MCS 2 (QPSK), NSS=1, SGI=0 (800 ns LGI)`** with `htt_max_amsdu_ampdu = "3 64"` the deterministic near-field champion (**`19.62 Mbps` aggregate, `0.0%` `1472 B` loss**).

---

## 2. Automatic 3-Regime Detector & VHT Policy Matrix

| Detected Regime (`80 MHz` ToF + Chain $\Delta$) | ToF Distance | Chain $\Delta$ | Selected Bandwidth | AP / STA Rate & GI Policy | `htt_max_amsdu_ampdu` |
| :--- | :---: | :---: | :---: | :--- | :---: |
| **`RADIATIVE_NEAR_FIELD_CAVITY`** | **`< 6.15 m`** | `>= 7.0 dB` | **`VHT20`** | `MCS 3 DL / MCS 2 UL, NSS=1, SGI=0 (LGI)` | `"3 64"` |
| **`FAR_FIELD_FRESNEL_ASYMMETRY`** | `>= 6.15 m` | `>= 6.0 dB` | **`VHT40`** | `MCS 5 DL / MCS 4 UL, NSS=1, SGI=0 + 0x9044` | `"3 64"` |
| **`FAR_FIELD_CLEAN_2X2_MIMO_LOS`** | `>= 6.15 m` | `< 6.0 dB` | **`VHT80`** | `MCS 8/9, NSS=2, SGI=1` | `"3 64"` |
