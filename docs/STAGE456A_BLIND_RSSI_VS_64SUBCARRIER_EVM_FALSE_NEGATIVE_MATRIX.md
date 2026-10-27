<!-- doc-head: STAGE456A_BLIND_RSSI_VS_64SUBCARRIER_EVM_FALSE_NEGATIVE_MATRIX.md preserved document content -->
<!-- /doc-head -->



# Stage 456A — Blind Chain RSSI vs 64-Element Per-Chain EVM False-Negative Matrix (`Guarida`)

- **Claim Classification**: `CONFIRMED`
- **Attribution**: `hardware` (frequency-selective Fresnel multipath & cross-pol leakage) + `proprietary airMAX/LTU module` (`ubnt_poll_host.ko` `sta + 0x0b7..0x1b6` 64-byte per-chain EVM circular history) + `QCA firmware` (`QCA988x` BB per-chain EVM demodulator reports)
- **Safety Gate**: `0` writes executed on `.60`, `.61`, `.82`, `.83`, `.84`.

---

## 1. Physical Law: Why Balanced `Chain RSSI` Masks Severe `EVM` Degradation

Traditional WISP NMS tools (including airOS WebUI chain bars and standard SNMP `chainrssi` alarms) evaluate MIMO alignment by checking whether:
$$\left|\text{RSSI}_{\text{Chain 0}} - \text{RSSI}_{\text{Chain 1}}\right| \le 2\text{..}3\text{ dB}$$

1. **Wideband Power vs Post-Equalizer Constellation Error (`CONFIRMED`)**:
   - `chainrssi` measures total wideband RF energy ($S + I + N + \text{multipath reflections}$) at the ADC input before OFDM FFT demodulation.
   - When a link suffers an in-band reflected ray (two-ray Fresnel reflection with excess path $\Delta d$) or cross-polarization leakage from the orthogonal chain, total integrated power on Chain 0 remains nearly identical to Chain 1 ($\left|\Delta\text{RSSI}\right| = 0\text{..}1\text{ dB}$), yet destructive phase cancellation on a subset of OFDM subcarriers or inter-stream interference degrades post-MMSE equalizer constellation error (`rx.evm` / `tx.evm`) by **`7.4..16.1 dB`**.

---

## 2. Quantitative False-Negative Matrix Across Guarida (`34` Endpoints Audited, `12` Live 64-EVM Vectors)

Across the `32` Guarida sector CPEs + `2` PtP backbone endpoints (`34` total endpoints, with `26/32` sector CPEs classified as healthy under a `4 dB` RSSI delta threshold) and `12` online `WA.v8.7.x` links exporting full 64-element `rx.evm` / `tx.evm` vectors:
- **Strict `<= 2 dB` RSSI Gate False Negatives**: **`5 / 12` (`41.67%`)** of online links pass `|Delta_RSSI| <= 2 dB` while suffering `>= 7.4 dB` per-chain EVM asymmetry or `>= 6.0 dB` multipath notches.
- **Moderate `<= 3 dB` RSSI Gate False Negatives**: **`6 / 12` (`50.00%`)** of online links pass `|Delta_RSSI| <= 3 dB` while suffering `7.41..16.13 dB` per-chain EVM asymmetry.
- **Hidden EVM Asymmetry Excess (`max(|Delta_EVM|) - |Delta_RSSI|`)**: Mean **`+6.55 dB`**, peaking at **`+15.13 dB`** on `SOSA_Joaquin_Alejandro` (`.83`).

| Radio | Peer / CPE | Signal | `Ch0/Ch1` RSSI (`\|\Delta\|`) | `Ch0/Ch1` RX EVM Mean | Max `\|\Delta\text{EVM}\|` | Max Notch | Hidden Excess | Traditional NMS (`<=3 dB`) | 64-EVM Ground Truth |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `.60` | `ptp-guarida-sta` (`.61`) | `-54 dBm` | `39 / 39 dB` (`0 dB`) | `30.45 / 38.39 dB` | `7.94 dB` | `6.45 dB` | **`+7.94 dB`** | `HEALTHY` | **`FALSE_NEGATIVE`** |
| `.61` | `ptp-guarida-ap` (`.60`) | `-54 dBm` | `38 / 39 dB` (`1 dB`) | `31.02 / 38.55 dB` | `7.86 dB` | `6.52 dB` | **`+6.86 dB`** | `HEALTHY` | **`FALSE_NEGATIVE`** |
| `.82` | `Rocio Belen DURAN` | `-52 dBm` | `39 / 42 dB` (`3 dB`) | `30.58 / 41.81 dB` | `11.23 dB` | `7.58 dB` | **`+8.23 dB`** | `HEALTHY` | **`FALSE_NEGATIVE`** |
| `.82` | `FRANCO_Debora` | `-63 dBm` | `29 / 30 dB` (`1 dB`) | `22.92 / 30.70 dB` | `7.78 dB` | `5.92 dB` | **`+6.78 dB`** | `HEALTHY` | **`FALSE_NEGATIVE`** |
| `.83` | `TABORDA_Ada` | `-61 dBm` | `31 / 32 dB` (`1 dB`) | `24.81 / 32.22 dB` | `7.41 dB` | `9.81 dB` | **`+6.41 dB`** | `HEALTHY` | **`FALSE_NEGATIVE`** |
| `.83` | `SOSA_Joaquin` | `-56 dBm` | `36 / 37 dB` (`1 dB`) | `24.14 / 39.22 dB` | `16.13 dB` | `4.14 dB` | **`+15.13 dB`** | `HEALTHY` | **`FALSE_NEGATIVE`** |
| `.82` | `RODRIGUEZ_Marina` | `-56 dBm` | `31 / 39 dB` (`8 dB`) | `27.77 / 34.84 dB` | `7.44 dB` | `3.77 dB` | `-0.56 dB` | `WARN` | `DETECTED` |
| `.82` | `MONZON_Thomas` | `-46 dBm` | `37 / 50 dB` (`13 dB`) | `31.08 / 49.38 dB` | `18.30 dB` | `5.42 dB` | `+5.30 dB` | `WARN` | `DETECTED` |
| `.82` | `Ivana ECHEVARRIA` | `-58 dBm` | `33 / 37 dB` (`4 dB`) | `26.47 / 36.28 dB` | `9.81 dB` | `8.47 dB` | `+5.81 dB` | `WARN` | `DETECTED` |
| `.82` | `Marilina SEVERO` | `-72 dBm` | `23 / 19 dB` (`4 dB`) | `20.05 / 25.34 dB` | `5.29 dB` | `5.05 dB` | `+1.29 dB` | `WARN` | `DETECTED` |
| `.82` | `Alesia STUDER` | `-61 dBm` | `30 / 34 dB` (`4 dB`) | `24.14 / 35.81 dB` | `11.67 dB` | `2.30 dB` | `+7.67 dB` | `WARN` | `DETECTED` |
| `.83` | `GALEANO_Rocio` | `-59 dBm` | `36 / 29 dB` (`7 dB`) | `26.11 / 38.50 dB` | `14.71 dB` | `3.67 dB` | `+7.71 dB` | `WARN` | `DETECTED` |

---

## 3. Reproducible Verification
- Tool: [`build_stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.py`](../tools/observability/build_stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.py)
- Artifact: [`stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.json`](../artifacts/autoresearch/stage456a_blind_rssi_vs_64subcarrier_evm_false_negative_matrix.json)
- Test Suite: [`test_stage456a.py`](../tests/test_stage456a.py)
