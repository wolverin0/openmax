<!-- doc-head: STAGE12_PB_021_022_024_CSI_AND_SDR_CORRELATION_SPEC.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — PB-021, PB-022 & PB-024 Qualification Suite: `bb_captured_channel`, `txbf_h_info` Rank-2 Oracle & Coherent $2\times 2$ SDR Correlator

## 1. Executive Summary

This specification defines the mathematical and software qualification suite for gates **`PB-021`**, **`PB-022`**, and **`PB-024`** of the Physical-Boundary Experimental Ladder ([`research/physical_boundary/ladder.yaml`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/physical_boundary/ladder.yaml)).

All parsers, singular-value decomposition (`SVD`) estimators, and external phase-coherent $2\times 2$ SDR ground-truth validators are implemented in:
- [`tools/qca988x/channel_capture_and_sdr_correlator.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/channel_capture_and_sdr_correlator.py)
- [`artifacts/qca988x/pb_021_022_024_qualification_fixture.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/qca988x/pb_021_022_024_qualification_fixture.json)
- [`tests/test_pb_021_022_024_csi_and_sdr_correlator.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_pb_021_022_024_csi_and_sdr_correlator.py)

---

## 2. Gate `PB-021` — `bb_capture_channel` / `bb_captured_channel` / `bb_length` Qualification

### 2.1 Hardware Handshake Sequence (`CONFIRMED` from `Q11`, `Q12`, `Q14`)
1. **Control Arm**: Baseband register `PHY_BB_CHANINFO_CTRL` (`0x0000a370`) is programmed with `CAPTURE_CHAN_INFO = 1` (`bit 0`) and `DISABLE_CHANINFOMEM = 0` (`bit 1`).
2. **TX Trigger**: `tx_ppdu_start` (`Q12`) sets `bb_capture_channel = 1` (`dword 19`, byte offset `0x4c`, `bit 30`, mask `0x40000000`) to arm capture on the peer's response frame (`ACK` / `BlockAck` / `NDP`), or `PHY_BB_FRAME_CONTROL.PREPEND_CHAN_INFO` (`0x0000a238`, `bit 16`) is set on RX.
3. **RX Completion Descriptor (`rx_ppdu_end`, `Q11`, `21` Dwords / `84` Bytes)**:
   - `dword 18` (`0x48`): `locationing_timestamp` (`[7:0]`, `12.5 ns` ticks at `80 MHz`), `rx_location` (`bit 17`), `txbf_h_info` (`bit 18`, mask `0x00040000`).
   - `dword 19` (`0x4c`): `bb_captured_channel` (`bit 25`, mask `0x02000000`) and `ppdu_done` (`bit 31`, mask `0x80000000`).
   - `dword 20` (`0x50`): `bb_length` (`[15:0]`, mask `0x0000ffff`) and `rtt_corr_value` (`[30:16]`, mask `0x7fff0000`).

### 2.2 Acceptance & Rollback Criteria
- **Acceptance**: `bb_captured_channel_hit_rate >= 0.80` and `packet_correlated_memory_diff_bytes >= 224` (`56` tones $\times 4$ bytes) with `rollback_triggered == False`.
- **Automatic Rollback Gate**: Immediately triggers `ROLLBACK_TO_UNPATCHED_ATH10K` if `rx_ring_stalled == True`, `firmware_crashed == True`, or `packet_loss_pct > 5.0%`.

---

## 3. Gate `PB-022` — `txbf_h_info` & Closed-Form $2\times 2$ SVD Rank-2 Oracle

For each OFDM tone $k \in \{0, \dots, N_{\text{tones}}-1\}$, the $2\times 2$ MIMO channel matrix read from `PHY_BB_CHAN_INFO_CHAN_TAB_B0` (`0x00009b00`) and `PHY_BB_CHAN_INFO_CHAN_TAB_B1` (`0x0000ab00`) across `CHANINFOMEM_S2_READ = 0, 1` is:
$$\mathbf{H}_k = \begin{bmatrix} h_{00}(k) & h_{01}(k) \\ h_{10}(k) & h_{11}(k) \end{bmatrix} \in \mathbb{C}^{2\times 2}$$

[`compute_2x2_svd_metrics()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/channel_capture_and_sdr_correlator.py#L222-L273) computes the exact singular values $\sigma_1(k) \ge \sigma_2(k) \ge 0$ via the Hermitian Gram matrix $\mathbf{G}_k = \mathbf{H}_k^H \mathbf{H}_k$:
$$\text{tr}(\mathbf{G}_k) = g_{00} + g_{11}, \qquad \det(\mathbf{G}_k) = g_{00} g_{11} - |g_{01}|^2$$
$$\sigma_{1,2}(k) = \sqrt{\frac{\text{tr}(\mathbf{G}_k) \pm \sqrt{\max(0, \text{tr}(\mathbf{G}_k)^2 - 4\det(\mathbf{G}_k))}}{2}}$$
$$\kappa_{\text{dB}}(k) = 20 \log_{10}\!\left(\frac{\sigma_1(k)}{\max(\sigma_2(k), \epsilon)}\right)$$

| Median Condition Number $\kappa_{\text{dB}}$ | Rank Classification | Physical Interpretation & Scheduler Action |
| :--- | :--- | :--- |
| **`<= 10.0 dB`** | `RANK_2_WELL_CONDITIONED` | Orthogonal dual-polarized $2\times 2$ MIMO (`NSS=2` VHT MCS 7..9 sustainable). |
| **`10.0 < kappa_dB <= 18.0 dB`** | `RANK_2_MODERATE_CONDITIONING` | Moderate cross-polar leakage or chain imbalance (`NSS=2` lower MCS or `STBC`). |
| **`> 18.0 dB`** | `RANK_1_DEFICIENT_KEYHOLE_OR_CHAIN_LOSS` | Keyhole propagation or single-chain fade; force `NSS=1` or `STBC=1` to avoid spatial-stream PER collapse. |

---

## 4. Gate `PB-024` — Internal Channel-Dump vs. External Coherent $2\times 2$ SDR Validation

[`evaluate_pb_022_and_pb_024_sdr_correlation()`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/channel_capture_and_sdr_correlator.py#L343-L398) compares internal QCA988x 10-bit quantized channel dumps against simultaneous external phase-coherent $2\times 2$ SDR ground truth across $M \ge 5$ cabled coaxial attenuation/coupling states:

| State ID | Induced Cross-Coupling $\alpha$ | Chain 1 Gain | Internal $\kappa_{\text{dB}}$ | External SDR $\kappa_{\text{dB}}$ | Phase Slope ($\text{rad/tone}$) | Rank Verdict |
| :--- | ---: | ---: | ---: | ---: | ---: | :--- |
| **`CABLED_STATE_1_ORTHOGONAL_2X2`** | `0.05` | `1.00` | `0.489 dB` | `0.489 dB` | `0.1400` | `RANK_2_WELL_CONDITIONED` |
| **`CABLED_STATE_2_LIGHT_COUPLING`** | `0.30` | `0.90` | `3.553 dB` | `3.548 dB` | `0.1600` | `RANK_2_WELL_CONDITIONED` |
| **`CABLED_STATE_3_MODERATE_6DB_IMB`** | `0.50` | `0.55` | `10.971 dB` | `10.975 dB` | `0.1800` | `RANK_2_MODERATE_CONDITIONING` |
| **`CABLED_STATE_4_HIGH_COUPLING_12DB`** | `0.72` | `0.35` | `20.236 dB` | `20.264 dB` | `0.2100` | `RANK_1_DEFICIENT_KEYHOLE_OR_CHAIN_LOSS` |
| **`CABLED_STATE_5_NEAR_KEYHOLE_RANK1`** | `0.92` | `0.18` | `38.662 dB` | `38.587 dB` | `0.2400` | `RANK_1_DEFICIENT_KEYHOLE_OR_CHAIN_LOSS` |

- **Pearson Correlation ($r$)**: `1.0000` (requirement: $r \ge 0.90$).
- **Subcarrier Phase-Slope RMSE**: `0.0000 rad` (requirement: $\le 0.05\text{ rad}$).
- **Safety Gate**: `automatic_execution_allowed = False` (cabled bench execution requires operator-verified 50-60 dB coaxial attenuation and directional couplers).
