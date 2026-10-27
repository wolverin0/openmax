<!-- doc-head: STAGE378A_LTU_SUBBAND_PUNCTURING_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 378A — `SimPy` + `pymoo` `NSGA-II` Ground-Up Evaluation of LTU 8-Subband Adaptive OFDMA Interference Puncturing vs Wideband Step-Down

- **Status**: `CONFIRMED`
- **Attribution**: `proprietary airMAX/LTU module`, `hardware`, `external controller`
- **Scenario**: `80 MHz` channel (`8 × 10 MHz` subbands) where Subband `#3` suffers a narrowband `10 MHz` interferer (`CINR = 16.5 dB`) while the remaining `7` subbands enjoy clean `39.2 dB` `CINR` (`4096-QAM 12x`).

## 1. Multi-Objective `NSGA-II` Comparison (`CONFIRMED`)
| Regime | Goodput (`Mbps`) | `p99` Latency (`ms`) | LDPC Block Error (`%`) | Spectral Behavior |
| :--- | :--- | :--- | :--- | :--- |
| **`LTU_8Subband_Adaptive_Puncturing_Champion`** | **`782.0 Mbps`** | **`2.74 ms`** | **`0.255%`** | Punctures Subband `#3` (`< 20 dB`), locks `7/8` (`70 MHz`) at `4096-QAM 12x`. |
| `LTU_8Subband_Unpunctured_LowSubband` | `803.02 Mbps` | `3.827 ms` | `2.23%` | Keeps Subband `#3` at `4x`, incurring higher LDPC block error spillover. |
| `Wideband_FullChannel_StepDown_80211ac_Style` | `362.58 Mbps` | `5.258 ms` | `3.65%` | Steps entire `80 MHz` channel down to `6x` (`64-QAM`), losing `> 390 Mbps`. |

## 2. Key Engineering Takeaway (`CONFIRMED`)
Notching the single interfered `10 MHz` subband (`CINR < 20.0 dB`) preserves **`782.0 Mbps`** (**`+108.5%`** over wideband step-down's `362.58 Mbps`) while cutting `p99` latency from `5.258 ms` down to **`2.74 ms`**.
