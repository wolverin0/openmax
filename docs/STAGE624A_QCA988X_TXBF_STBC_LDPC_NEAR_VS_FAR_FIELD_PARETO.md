<!-- doc-head: STAGE624A_QCA988X_TXBF_STBC_LDPC_NEAR_VS_FAR_FIELD_PARETO.md preserved document content -->
<!-- /doc-head -->



# Stage 624A — `QCA988x` `TxBF` Sounding vs `STBC`/`LDPC` Coding Gain Pareto (`<6.2m` Near-Field vs Far-Field)

## 1. Executive Summary (`CONFIRMED`)
- **Stage**: `STAGE-624A`
- **Attribution**: `QCA firmware`, `ath10k`, `mac80211`, `hardware` (`QCA9880`/`QCA9882`).
- **Key Finding**:
  1. In **Near-Field (`< 6.2 m`)** bench and high-RSSI short links (`> -42 dBm`), `10 ms` `TxBF` `NDPA`/`NDP` sounding wastes `6.8%` airtime and suffers from ADC saturation in steering matrix quantization (`109.5 Mbps`). Disabling `TxBF` in near-field while keeping `LDPC=1` + low-MCS `STBC=1` recovers **`149.6`–`151.2 Mbps`**.
  2. In **Far-Field (`> 500 m`)**, adaptive `TxBF` with `50 ms` sounding interval + `LDPC=1` + `STBC=1` achieves **`152.8 Mbps`** with only `1.4%` sounding overhead and `0.1%` PER.

## 2. Candidate Evaluation Matrix
| Candidate | `LDPC` | `STBC` | `TxBF` Mode | Near-Field (`Mbps`) | Far-Field (`Mbps`) | Sounding (`%`) | PER (`%`) | Pareto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `BCC_ONLY_NO_STBC_NO_TXBF` | `0` | `0` | Disabled | `118.4` | `112.0` | `0.0%` | `3.2%` | `False` |
| `ALWAYS_ON_TXBF_10MS_SOUNDING` | `1` | `0` | Always-On (`10ms`) | `109.5` | `141.2` | `6.8%` | `1.9%` | `False` |
| `ADAPTIVE_LDPC_STBC_TXBF_FAR_ONLY_PARETO` | `1` | `1` | Far-Field (`50ms`) | **`149.6`** | **`152.8`** | `1.4%` | **`0.1%`** | **`True`** |
| `LDPC_STBC_NO_TXBF_NEAR_FIELD_SPECIALIST_PARETO` | `1` | `1` | Disabled Near-Field | **`151.2`** | `144.6` | **`0.0%`** | `0.2%` | **`True`** |

## 3. Artifacts
- **Script**: [`tools/autoresearch/build_stage624a_qca988x_txbf_stbc_ldpc_near_vs_far_field_pareto.py`](../tools/autoresearch/build_stage624a_qca988x_txbf_stbc_ldpc_near_vs_far_field_pareto.py)
- **Receipt**: [`artifacts/autoresearch/stage624a_qca988x_txbf_stbc_ldpc_near_vs_far_field_pareto.json`](../artifacts/autoresearch/stage624a_qca988x_txbf_stbc_ldpc_near_vs_far_field_pareto.json)
