<!-- doc-head: Stage 446A Pillar 2 80 MHz MAC Clock (12.5 ns / 1.87 m) Hardware Time-of-Flight Ranging & Fresnel Multipath Drift Detector -->
Documents the Pillar 2 (`PB-021`) passive Time-of-Flight (`ToF`) ranging and 16-pilot subcarrier EVM slope Fresnel multipath detector extracted from `rx_ppdu_end_qca988x` prior to `ath10k` `skb_pull`.
<!-- /doc-head -->

# Stage 446A — Pillar 2 `80 MHz` MAC Clock (`12.5 ns` / `1.87 m`) Hardware ToF Ranging & Fresnel Multipath Drift Detector

- **Epistemic Status**: `CONFIRMED` (`rx_ppdu_end_qca988x` 84-byte DMA trailer layout + 4-link physics & delay-spread verification)
- **Attribution**: `QCA firmware` (`QCA988x` baseband `rx_ppdu_end`) · `ath10k` (`htt_rx.c` `ath10k_htt_rx_amsdu_pop`)
- **Generator**: [`build_stage446a_hardware_tof_187m_fresnel_drift_detector.py`](../tools/observability/build_stage446a_hardware_tof_187m_fresnel_drift_detector.py)
- **JSON Receipt**: [`stage446a_hardware_tof_187m_fresnel_drift_detector.json`](../artifacts/autoresearch/stage446a_hardware_tof_187m_fresnel_drift_detector.json)

---

## 1. Hardware Physics inside `rx_ppdu_end_qca988x` (`84` Bytes)

Before `ath10k_htt_rx_amsdu_pop` calls `skb_pull` to strip the hardware RX descriptor trailer, the `QCA9880`/`QCA9882` baseband writes:
1. **`dwords 0..15` (`evm_p0..evm_p15`)**: Per-pilot, per-spatial-stream Error Vector Magnitude (`EVM`) in dB across all 16 OFDM pilot tones.
2. **`dword 18 [7:0]` (`locationing_timestamp`)**: Fine arrival clock driven at **`80 MHz`** (`12.5 ns` per tick = **`1.873 m` round-trip path resolution**).

When wind blows wet tree branches into the 1st Fresnel zone or thermal ducting bends the main lobe, the direct Line-of-Sight (`LOS`) component attenuates while reflected non-LOS (`NLOS`) paths arrive later:
- **Excess ToF Path Drift (`Delta d >= 3.75 m` / `>= 2` ticks)**: Proves the receiver is locking onto a longer reflected path rather than the direct ray.
- **Pilot Edge-vs-Center EVM Slope (`>= 4.5 dB`)**: Proves frequency-selective multipath notches across the channel bandwidth, warning that delay spread is approaching the **`400 ns` Short Guard Interval (`SGI`)** limit.

---

## 2. Quantitative Link Verification Matrix

| Link ID | Baseline Dist (`m`) | Current Dist (`m`) | Excess Drift (`m`) | Delay Spread (`ns`) | Stream EVM $\Delta$ (`dB`) | Classification & Proactive PHY Action |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`GUARIDA_MONZON_41_LOS`** | `771.7 m` | `772.1 m` | `+0.37 m` | `5.6 ns` | `0.5 dB` | `CLEAN_FIRST_FRESNEL_ZONE_LOS` $ightarrow$ Keep `2x2 VHT SGI=1` |
| **`GUARIDA_GAMBOA_223_WET_FOLIAGE`** | `1283.1 m` | `1291.3 m` | **`+8.24 m`** | `48.1 ns` | **`8.3 dB`** | `FRESNEL_POLARIZATION_MULTIPATH` $ightarrow$ Clamp `NSS=1 CDD SGI=0` |
| **`GUARIDA_TOLABA_80_THERMAL`** | `1760.8 m` | `1766.6 m` | **`+5.81 m`** | `36.3 ns` | `0.7 dB` | `SPECULAR_MULTIPATH_ISI` $ightarrow$ Force `LGI (800 ns)` |
| **`BENCH_PBE5AC_241_242_NLOS`** | `15.0 m` | `21.7 m` | **`+6.74 m`** | `42.5 ns` | **`10.8 dB`** | `FRESNEL_POLARIZATION_MULTIPATH` $ightarrow$ Clamp `NSS=1 CDD SGI=0` |
