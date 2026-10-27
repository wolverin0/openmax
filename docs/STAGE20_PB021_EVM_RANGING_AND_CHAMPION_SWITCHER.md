<!-- doc-head: STAGE20_PB021_EVM_RANGING_AND_CHAMPION_SWITCHER.md preserved document content -->
<!-- /doc-head -->

# Stage 20 & PB-021 — Per-PPDU Pilot EVM, 12.5 ns Fine ToF Ranging, and Closed-Loop Champion Regime Switcher

**Task ID**: `T-S18-PB021-EVM-RANGING-AND-CHAMPION-SWITCHER`  
**Status**: `CONFIRMED` (Strictly Offline Closed-Loop Verification)  
**Controller Implementation**: [`controller/stage20_closed_loop_champion_switcher.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/stage20_closed_loop_champion_switcher.py)  
**Verification Artifact**: [`artifacts/physical_boundary/stage20_closed_loop_champion_switcher_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/physical_boundary/stage20_closed_loop_champion_switcher_20261025.json)  
**Champion State Ledger**: [`artifacts/autoresearch/champion_state_ledger.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/champion_state_ledger.json)  

---

## 1. Executive Summary

This specification implements **PB-021** (per-PPDU hardware pilot EVM and `12.5 ns` fine ToF ranging extraction from `struct htt_rx_ppdu_end` on QCA988x) together with the **Stage 20 Closed-Loop Champion Regime Switcher & Incremental Champion Promoter**:

1. **PB-021 Hardware Per-PPDU Pilot EVM & 12.5 ns Fine ToF Ranging (`PpduEvmAndRangingAnalyzer`)**:
   - Decodes the `84`-byte QCA988x `rx_ppdu_end` descriptor (`rx_ppdu_end_common` `72` B + `rx_ppdu_end_qca988x` `12` B) exposed via `HTT_T2H_MSG_TYPE_PKTLOG` (`0x08`).
   - Extracts all 16 per-pilot EVM dB values across NSS0 (`pilots 0..7`) and NSS1 (`pilots 8..15`), computing per-stream mean EVM (`stream0_mean_evm_db`, `stream1_mean_evm_db`), inter-stream EVM imbalance (`evm_chain_delta_db`), and optimal single-chain TX mask (`best_single_tx_chainmask` $\in \{1, 2\}$).
   - Combines `wb_timestamp` ($1\ \mu\text{s}$ coarse clock) and `locationing_timestamp` ($80\ \text{MHz}$ fine counter, $12.5\ \text{ns}$ step = $1.875\ \text{m}$ two-way free-space resolution) to compute per-PPDU propagation distance (`estimated_distance_m`), optimal 802.11 `coverage_class` ($0..31$, $3\ \mu\text{s}$ slot/ACK step), and hardware `ack_timeout_us`.
   - Extracts Implicit TxBF / H-matrix capture flags (`txbf_h_info` bit `12`, `bb_captured_channel` bit `0`, `bb_length` bits `1..16`, `ppdu_done` bit `31`).

2. **Stage 20 Closed-Loop Champion Regime Switcher (`ClosedLoopChampionSwitcher`)**:
   - Dynamically switches the AP between the two physically verified Golden Profiles in [`controller/multiradio_golden_profile_applicator.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/controller/multiradio_golden_profile_applicator.py) based on active subscriber demand (`active_busy_cpes`):
     - `active_busy_cpes <= 1` $\rightarrow$ `openwrt_lap120_ptp_1cpe_champion` (`aql_txq_limit=900/1500 us`, `aql_threshold=4000`, `tcp_limit_output_bytes=131072`).
     - `active_busy_cpes >= 2` $\rightarrow$ `openwrt_lap120_ptmp_multicpe_champion` (`aql_txq_limit=1850/3700 us`, `aql_threshold=6000`, `airtime_weight=512:512:128`).
   - Drives hysteresis-guarded **Per-Station Asymmetric ChainMask Rescue** (`enter >= 5.0 dB` chain RSSI/EVM imbalance $\rightarrow$ `txchainmask=best_single_chain, rxchainmask=3`; `exit <= 3.0 dB` $\rightarrow$ `txchainmask=3, rxchainmask=3`).
   - Automatically updates sector-wide `iw phy phy0 set coverage <N>` from the maximum active subscriber ToF distance.

3. **Incremental Champion-as-Baseline Promoter (`IncrementalChampionPromoter`)**:
   - Enforces the mandatory `CHAMPION (A)` vs `CHAMPION + MUTATION (B)` autoresearch discipline against [`artifacts/autoresearch/champion_state_ledger.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/champion_state_ledger.json).

---

## 2. PB-021 Hardware Struct Layout (`rx_ppdu_end`, 84 Bytes)

| Offset | Field | Size | Description |
| :--- | :--- | :--- | :--- |
| `0x00..0x3F` | `evm_p0..evm_p15` | `16 x u32` (`64` B) | Pilot EVM words (`0x80000000` unused sentinel; low byte signed int8 dB) |
| `0x40` | `tx_antenna_mask` | `u32` (`4` B) | Transmit antenna mask |
| `0x44` | `flags` | `u32` (`4` B) | Bit `0`: `bb_captured_channel`, Bit `12`: `txbf_h_info` |
| `0x48` | `bb_Captured_timeout` | `u8` (`1` B) | Baseband capture timeout counter |
| `0x49` | `locationing_timestamp` | `u8` (`1` B) | **80 MHz fine ToF counter** (`0..79` ticks $\times 12.5\ \text{ns}$) |
| `0x4A` | `phy_err_code` | `u16` (`2` B) | PHY error code (`phy_err_valid` at bit `15`) |
| `0x4C` | `wb_timestamp` | `u32` (`4` B) | **1 $\mu$s coarse baseband timestamp** |
| `0x50` | `tsf_timestamp` | `u16` (`2` B) | Lower 16-bit TSF timestamp |
| `0x52` | `info0` | `u16` (`2` B) | Bits `0..14`: `bb_length`, Bit `15`: `ppdu_done` |

### Verified Offline Decoding Samples

| Sample | `wb_timestamp` ($\mu$s) | `locationing_timestamp` (ticks) | Two-Way ToF (ns) | Est. Distance (m) | Recommended `coverage_class` | Stream0 / Stream1 EVM (dB) | `evm_chain_delta_db` |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `cpe1_near_150m` | `17` | `0` | `1,000.0` | `149.896` | `1` (`28 us` ACK) | `-28.0` / `-27.0` | `1.0` |
| `cpe2_mid_2265m` | `31` | `9` | `15,112.5` | `2,265.307` | `6` (`43 us` ACK) | `-24.0` / `-25.0` | `1.0` |
| `cpe3_weak_6015m_imbalanced` | `56` | `10` | `40,125.0` | `6,014.586` | `14` (`67 us` ACK) | `-18.0` / `-11.0` | `7.0` (`txchainmask=2`) |

---

## 3. Closed-Loop Regime Transition & Asymmetric Rescue Verification

| Step | Busy CPEs | Selected AP Profile | Sector Max Distance | Sector `coverage_class` | CPE-3 Weak ChainMask State |
| :--- | :---: | :--- | :---: | :---: | :--- |
| **Step A** | `1` (`CPE-1` only) | `openwrt_lap120_ptp_1cpe_champion` (`900/1500 us`, `thr=4000`) | `149.896 m` | `1` | N/A |
| **Step B** | `3` (`CPE-1..3`) | `openwrt_lap120_ptmp_multicpe_champion` (`1850/3700 us`, `thr=6000`) | `6014.586 m` | `14` | `ASYMMETRIC_SIMO_TX_MRC_RX (tx=2, rx=3)` |
