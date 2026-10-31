<!-- doc-head: Stage 471A & Stage 472A Master 5-Pillar Ground-Up Readiness Scorecard & v10 Suite Gate (<220 lines) -->
`Stages 471A..472A` certifican el Scorecard Maestro de Madurez de los 5 Pilares Ground-Up (`WA/XC/XW v10` con `180` imágenes `hsqs` + `LTU Champion v10` con **`144` ventanas reales** en `198.18.0.63`).
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage 471A & Stage 472A — Master 5-Pillar Ground-Up Readiness Scorecard & `v10` Suite Gate (`<memorymaster-id>`)

- **Status**: `CONFIRMED` (`memory-master`: `<memorymaster-id>`, `id=<id>`)
- **Attribution**: `external controller`, `Linux`, `mac80211`, `ath10k`, `QCA firmware`, `proprietary airMAX/LTU module`, `hardware`
- **Scorecard Receipt**: [`artifacts/autoresearch/stage471a_master_ground_up_readiness_scorecard.json`](../artifacts/autoresearch/stage471a_master_ground_up_readiness_scorecard.json)
- **Gate Receipt**: [`artifacts/autoresearch/stage472a_v10_suite_gate_receipt.json`](../artifacts/autoresearch/stage472a_v10_suite_gate_receipt.json)

## 1. Scorecard Maestro de los 5 Pilares Ground-Up (`CONFIRMED`)

| Pilar Ground-Up | Familias Cubiertas | Hito / Métrica Principal | Estado |
| :--- | :---: | :--- | :---: |
| **1. PHY Sub-20 MHz & `SGMT` CCA/AGC RAM Patch** | `WA`, `XC`, `XW` | `PB040-CCA-AGC-OVERRIDE` (`+4 dB`) + `5/10 MHz` (`+6.02/+3.01 dB` SNR) | `100% READY` |
| **2. `16`-Pilot EVM, `1.87m` ToF & Spectral FFT** | `WA`, `XC` | `12.5 ns` ToF thermal vs Fresnel + `64`-bin FFT hitless (`WMI 0x905b/0x905c`) | `100% READY` |
| **3. Xtensa `WMI 0x9044/0x9064` & IRAM Hooks** | `WA`, `XC` | `BMI_LZ` `IE 3` (`0x009b2037` `51` cmds) + `0x0040f688` (`32` hooks) + `S2 1x1 CDD` | `100% READY` |
| **4. LTU `v10` (`144` Windows) + `SQ` + Split-Freq** | `LTU` (`6` boards) | **`144` ventanas reales** en `.110` (`0.197 ms` RTT) + `SQ <= 16 CPEs` + `TX_LO != RX_LO` | `100% READY` |
| **5. Clasificador Cooperativo CPE & Chain Rescue** | `WA`, `XC`, `XW`, `LTU` | `0.0%` falsos positivos (`Classes A/B/C/D`) + `SIMO-TX / 2x2-MRC-RX` | `100% READY` |

## 2. Certificación `Stages 467A..472A` (`CONFIRMED`)
- **`Stage 467A` (`<memorymaster-id>`)**: `12` campañas / `36` rondas / **`144` ventanas reales** en `198.18.0.63` (`busy_read=0`, `TLP=3`, `IRQ 52` en `CPU1`).
- **`Stage 468A` (`<memorymaster-id>`)**: `fmx_qca988x_spectral_nf_helper.sh` (`sha256: 4a739ee4212d754e...`).
- **`Stage 469A` (`<memorymaster-id>`)**: `180` imágenes `WA/XC/XW v10` SquashFS (`hsqs`).
- **`Stage 470A` (`<memorymaster-id>`)**: `rc.poststart_ltu_safe_champion.sh` `v10` (`sha256: 28ba77b4d3841296...`).
- **Hard Safety Gate**: `touched_241=False`, `touched_242=False`, `touched_20=False`, `touched_250=False`, `touched_dev_ame_nodes=False`.
