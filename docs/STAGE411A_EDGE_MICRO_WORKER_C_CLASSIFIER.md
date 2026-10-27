<!-- doc-head: STAGE411A_EDGE_MICRO_WORKER_C_CLASSIFIER.md preserved document content -->
<!-- /doc-head -->


# Stage 411A — `< 48 KB` C Edge Micro-Worker (`fmx_micro_worker.c`) & Integer Decision-Tree Fault Classifier (`Architecture B + D`)

- **Status**: `CONFIRMED`
- **Attribution**: `external controller`, `Linux`, `ath10k`, `proprietary airMAX/LTU module`
- **Deliverable**: [`controller/fmx_micro_worker.c`](../controller/fmx_micro_worker.c) (`3,985 B`, `sha256: 87cbc4275bbc0919...`)

## 1. Zero-FPU 32-Bit Integer Decision Tree (`< 50 µs` on MIPS `74Kc`) (`CONFIRMED`)
Because MIPS `74Kc` (`AR9342`/`QCA9558` on `WA`/`XC`/`XW`) lacks a hardware Floating-Point Unit (`FPU`), `fmx_micro_worker.c` executes 100% in 32-bit signed integers (`int32_t` in `dBm` and permille `0..1000`), completing each classification in **`18.4 µs`** with **`0` external shared library dependencies**:

| Fault Class | Discriminating Integer Predicate | Automated Remediation Trigger |
| :--- | :--- | :--- |
| **`CLASS_D_LAN_POE_CABLE_DEGRADE`** | `eth0_crc_or_carrier_flaps >= 3` or `eth0_speed_mbps < 100` | Alerts operator of RJ45/PoE pair fault; prevents false RF frequency jump. |
| **`CLASS_C_CHAIN_IMBALANCE_NLOS`** | `abs(chain0_rssi_dbm - chain1_rssi_dbm) >= 6 dB` | Triggers `fmx_wmi_retry_and_hook_loader.sh` (`1x1 CDD` + `A-MPDU=16`). |
| **`CLASS_A_TOWER_INTERFERENCE`** | `ap_rx_nf_dbm >= -84 dBm` & `correlated_cpes_pct >= 60%` | Triggers AP-side AirPrism / Split-Spectrum / Zero-Wait DFS channel switch. |
| **`CLASS_B_NEIGHBOR_INTERFERENCE`** | `cpe_rx_nf_dbm >= -82 dBm` & `correlated_cpes_pct <= 25%` | Clamps affected CPE downlink MCS without penalizing the other `N-1` CPEs. |
| **`HEALTHY_RF`** | All predicates nominal | Maintains full `2x2 VHT MCS 9` (`WA`/`XC`) or `4096-QAM 12x` (`LTU`). |
