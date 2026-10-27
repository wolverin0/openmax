<!-- doc-head: STAGE220A_LTU_SPLIT_SPECTRUM_PTMP_PARETO.md preserved document content -->
<!-- /doc-head -->


# Stage 220A: SimPy + Pymoo NSGA-II Split-Spectrum PtMP Benchmark

## 1. Asymmetric WISP Tower Noise Problem (`INFERRED` / `CONFIRMED`)
- **Mechanism**: WISP towers experience severe uplink noise (`-72 dBm`) near the AP antenna while rural CPE rooftops see clean downlink spectrum (`-90 dBm`). On a symmetric co-channel link (`txfreq == rxfreq`), uplink CINR drops to `16 dB` (`BLER = 24%`), starving TCP ACKs and throttling downlink TCP goodput.
- **Split-Spectrum Solution**: Using `prefer_work_txfreq != prefer_work_rxfreq` (`Stage 219A`), moving UL to a clean `20 MHz` frequency (`-92 dBm` noise floor) restores `36 dB` UL CINR (`BLER = 0.8%`), unlocking full `50 MHz` `75/25` `4096-QAM` DL capacity.

## 2. Symmetric Co-Channel vs Split-Spectrum Champion
| Mode | DL / UL BW (MHz) | Duty Split | UL CINR (dB) | UL BLER | DL Goodput (Mbps) | UL Goodput (Mbps) | Aggregate (Mbps) | `p99` RTT (ms) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Symmetric Co-Channel | `40 / 40 MHz` | `67/33` | `16.0` | `0.24` | `391.27` | `26.52` | `417.78` | `9.158` |
| **Split-Spectrum Champion** | **`50 / 20 MHz`** | **`75/25`** | **`36.0`** | **`0.008`** | **`578.44`** | **`66.37`** | **`644.81` (`+54.34%`)** | **`2.532`** |
