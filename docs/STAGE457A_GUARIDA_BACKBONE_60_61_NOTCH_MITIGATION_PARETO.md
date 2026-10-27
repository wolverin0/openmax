<!-- doc-head: STAGE457A_GUARIDA_BACKBONE_60_61_NOTCH_MITIGATION_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 457A — `Almafuerte (.60)` $\leftrightarrow$ `Guarida (.61)` Fresnel Notch Mitigation Pareto (`SimPy` + `pymoo` `NSGA-II`)

- **Claim Classification**: `CONFIRMED` (offline `SimPy` + `pymoo` `NSGA-II` Pareto model anchored on Stage 454A 5-snapshot live telemetry)
- **Attribution**: `hardware` (two-ray Fresnel reflection phase cancellation on `Chain 0` V-pol at `5705 MHz`) + `QCA firmware` (`WMI_PDEV_PARAM_ANI_ENABLE = 0x9044` equalizer step) + `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` A-MPDU / A-MSDU aggregation)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.

---

## 1. Physical Model of the `5705 MHz` Chain 0 Fresnel Null

Across the 5-snapshot live audit (`Stage 454A`), `Almafuerte-BH (.60)` $\leftrightarrow$ `Guarida-BH (.61)` (`417 m`, `20 MHz` VHT20 at `5705 MHz`) exhibits:
- **Chain 1 (H-pol)**: `38.16 dB` mean RX EVM (`0/64` samples `< 27 dB`).
- **Chain 0 (V-pol)**: `29.95 dB` mean RX EVM (`9.0/64` samples `< 27 dB`, notch minimum `25 dB` on `.60` and `22 dB` on `.61`), forcing **`32.27%` of all DL PPDUs (`29.60M / 91.73M`)** down from `MCS 8` (`256-QAM`, `173.3 Mbps`) to `MCS 7` (`64-QAM`, `144.4 Mbps`).

For a two-ray reflection with excess delay $\tau_{\text{excess}} \approx 50\text{ ns}$ ($20\text{ MHz}$ frequency periodicity), a center-frequency shift $\Delta f \in \{-10, -5, +5, +10\}\text{ MHz}$ rotates the reflected ray phase by:
$$\Delta\phi = 2\pi \Delta f \tau_{\text{excess}}$$
At $\Delta f = \pm 10\text{ MHz}$ (`5695 MHz` or `5715 MHz`), $\Delta\phi = \pi\text{ rad}$, shifting the destructive null out of the `20 MHz` passband.

---

## 2. Center-Frequency Sweep (`5695..5715 MHz`) & `NSGA-II` Pareto Knee

| Candidate (`center_freq_mhz`, `ANI`, `A-MPDU`, `A-MSDU`) | `Ch0` RX EVM | `Ch1` RX EVM | `\|\Delta\text{EVM}\|` | `MCS 8` (`256-QAM`) Share | Bidir Goodput | `p99` Slot RTT | MPDU Requeue |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Baseline (`5705 MHz`, `ANI=1`, `32`, `2`)** | `30.65 dB` | `38.31 dB` | `7.66 dB` | `76.94%` | `138.70 Mbps` | `1.728 ms` | `1.50%` |
| **`5700 MHz` (`\Delta f = -5\text{ MHz}`, `ANI=2`, `32`, `2`)** | `35.17 dB` | `38.36 dB` | `3.19 dB` | `96.55%` | `145.76 Mbps` | `1.542 ms` | `0.23%` |
| **`5710 MHz` (`\Delta f = +5\text{ MHz}`, `ANI=2`, `32`, `2`)** | `35.17 dB` | `38.36 dB` | `3.19 dB` | `96.55%` | `146.00 Mbps` | `1.542 ms` | `0.18%` |
| **`5695 MHz` (`\Delta f = -10\text{ MHz}`, `ANI=2`, `32`, `2`)** | `39.34 dB` | `38.36 dB` | `0.98 dB` | `98.80%` | `146.67 Mbps` | `1.542 ms` | `0.09%` |
| **`5715 MHz` (`\Delta f = +10\text{ MHz}`, `ANI=2`, `32`, `2`)** | `39.34 dB` | `38.36 dB` | `0.98 dB` | `98.80%` | `146.54 Mbps` | `1.542 ms` | `0.12%` |
| **Pareto Knee (`5695 MHz`, `ANI=4`, `64`, `3`)** | **`38.64 dB`** | **`38.26 dB`** | **`0.38 dB`** | **`98.80%`** (`+21.86%`) | **`155.87 Mbps`** (`+17.17 Mbps`) | **`1.511 ms`** (`-0.217 ms`) | **`0.09%`** |

---

## 3. Reproducible Verification
- Tool: [`run_stage457a_guarida_backbone_60_61_notch_mitigation_pareto.py`](../tools/sim/run_stage457a_guarida_backbone_60_61_notch_mitigation_pareto.py)
- Artifact: [`stage457a_guarida_backbone_60_61_notch_mitigation_pareto.json`](../artifacts/autoresearch/stage457a_guarida_backbone_60_61_notch_mitigation_pareto.json)
- Test Suite: [`test_stage457a.py`](../tests/test_stage457a.py)
