<!-- doc-head: STAGE12_AR9888_V2_DESCRIPTOR_AND_CHANNEL_DUMP_MAP.md preserved document content -->
<!-- /doc-head -->

# Stage 12 — AR9888 v2 (Peregrine) Descriptor & Baseband Channel-Dump Map

## 1. Executive Summary & Provenance Ledger

This document establishes the deterministic, commit-pinned hardware register and MAC/PHY descriptor map for the **Qualcomm Atheros QCA988x / AR9888 v2 ("Peregrine")** 802.11ac Wave-1 radio family used in Ubiquiti airMAX AC hardware (`LiteAP GPS`, `LAP-120`, `LiteBeam 5AC Gen2`, `NanoStation 5AC Loco`).

All findings are extracted directly from the pinned source manifest (`Q01..Q15` from `SpaceExplorationTechnologies/starlink-wifi@1d585ee8909bf7bab4391c0c52d8a9d44137b3bb` and `L01..L05` from `torvalds/linux@5b0764a53235d3c77e1ed674e836e1b3fe1a4b1f`) by [`tools/qca988x/fetch_pinned_sources.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/fetch_pinned_sources.py) and [`tools/qca988x/extract_descriptor_map.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/qca988x/extract_descriptor_map.py), with full JSON output stored in [`artifacts/qca988x/ar9888_v2_descriptor_map.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/qca988x/ar9888_v2_descriptor_map.json).

### 1.1 Pinned Hardware Header Manifest (`CONFIRMED`)

| Source ID | Repository & Commit | Path | Size (Bytes) | SHA-256 Digest | Applicability |
| :--- | :--- | :--- | ---: | :--- | :--- |
| **`Q11`** | `starlink-wifi@1d585ee8` | `dl/include/AR9888/v2/hw/mac_descriptors/rx_ppdu_end.h` | `18,324` | `361640290ee3baea12a191c31d30394d70ab256bf558b3ed6b79bd56e6acbe8d` | `EXACT_AR9888_PEREGRINE` |
| **`Q12`** | `starlink-wifi@1d585ee8` | `dl/include/AR9888/v2/hw/mac_descriptors/tx_ppdu_start.h` | `68,192` | `195f0c021ff639e5be4adc4727dfe1ea44ac4aaeb9ecfabf6d85a35f62c53d73` | `EXACT_AR9888_PEREGRINE` |
| **`Q13`** | `starlink-wifi@1d585ee8` | `dl/include/AR9888/v2/hw/mac_descriptors/series_bw.h` | `20,120` | `49f8859e56320a902f9d5ae1e56a8fc16281659e1fedb8dc59a3883f354ff51b` | `EXACT_AR9888_PEREGRINE` |
| **`Q14`** | `starlink-wifi@1d585ee8` | `dl/include/AR9888/v2/extra/hw/bb_lc_reg.h` | `869,235` | `5fbc077b66771a8865abdfe5eacb76e39451565b6208340bd2754101d793391f` | `EXACT_AR9888_PEREGRINE` |

---

## 2. `rx_ppdu_end` Hardware Completion Descriptor (`21` Dwords / `84` Bytes)

In `AR9888/v2`, the hardware DMA engine writes a 21-dword (`84`-byte) `rx_ppdu_end` structure upon completing reception of every PPDU (`#define NUM_OF_DWORDS_RX_PPDU_END 21`).

| Field Name | Macro Prefix | Dword | Byte Offset | Bits `[MSB:LSB]` | Mask (`Hex`) | Physical Boundary & Telemetry Role |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- |
| `evm_p0` .. `evm_p15` | `RX_PPDU_END_0_EVM_P0` .. `_15_EVM_P15` | `0..15` | `0x00..0x3c` | `[31:0]` | `0xffffffff` | **Per-Pilot, Per-Stream EVM**: 16 pilot words (`64` bytes total), each packing four 8-bit EVM values for spatial streams 0, 1, 2, and 3. Enables fine-grained constellation error & phase-noise tracking per subband pilot. |
| `tsf_timestamp` | `RX_PPDU_END_16_TSF_TIMESTAMP` | `16` | `0x40` | `[31:0]` | `0xffffffff` | **RX Clear TSF Timestamp**: 32-bit TSF timer (`1 us` resolution) latched on the rising edge of `rx_clear` (physical frame arrival). |
| `wb_timestamp` | `RX_PPDU_END_17_WB_TIMESTAMP` | `17` | `0x44` | `[31:0]` | `0xffffffff` | **Monotonic WLAN/BT Timestamp**: `1 us` clock immune to TSF beacon jumps/resets; ideal for drift-free RTT & slot timing. |
| `locationing_timestamp` | `RX_PPDU_END_18_LOCATIONING_TIMESTAMP` | `18` | `0x48` | `[7:0]` | `0x000000ff` | **Sub-Microsecond Arrival Phase (`12.5 ns`)**: 8-bit `80 MHz` sample counter (`0..79` within `1 us` TSF tick), yielding `~3.75 m` single-shot ranging resolution (`<0.5 m` when averaged across bursts). |
| `phy_err_code` | `RX_PPDU_END_18_PHY_ERR_CODE` | `18` | `0x48` | `[15:8]` | `0x0000ff00` | Hardware PHY error code (`radar`, `false_detect`, `spectral_scan`, `cck_timing`, etc.) valid when `phy_err=1`. |
| `phy_err` | `RX_PPDU_END_18_PHY_ERR` | `18` | `0x48` | `[16:16]` | `0x00010000` | Indicates a PHY error occurred during the PPDU. |
| `rx_location` | `RX_PPDU_END_18_RX_LOCATION` | `18` | `0x48` | `[17:17]` | `0x00020000` | Indicates fine RTT/ToA locationing information is valid. |
| `txbf_h_info` | `RX_PPDU_END_18_TXBF_H_INFO` | `18` | `0x48` | `[18:18]` | `0x00040000` | **Implicit/Explicit TxBF $H$-Matrix Indicator**: Asserted when RX packet carries valid TxBF $H$ channel matrix data (`CONFIRMED`). |
| `bb_captured_channel` | `RX_PPDU_END_19_BB_CAPTURED_CHANNEL` | `19` | `0x4c` | `[25:25]` | `0x02000000` | **Baseband Channel-Dump Handshake Bit**: Set to `1` by BB when it has captured the per-tone channel dump into `PHY_BB_CHAN_INFO_CHAN_TAB_B0/B1` (`0x00009b00` / `0x0000ab00`) for firmware readout (`CONFIRMED`). |
| `ppdu_done` | `RX_PPDU_END_19_PPDU_DONE` | `19` | `0x4c` | `[31:31]` | `0x80000000` | DMA completion ownership flag (`1` = hardware finished writing `rx_ppdu_end`). |
| `bb_length` | `RX_PPDU_END_20_BB_LENGTH` | `20` | `0x50` | `[15:0]` | `0x0000ffff` | **Captured Baseband Info Byte Length**: Exact byte count of BB debug/channel dump data associated with the PPDU (`CONFIRMED`). |
| `rtt_corr_value` | `RX_PPDU_END_20_RTT_CORR_VALUE` | `20` | `0x50` | `[30:16]` | `0x7fff0000` | **15-bit Fine RTT Correlation Peak**: Cross-correlation peak magnitude for sub-sample ToA refinement. |
| `rtt_normal_mode` | `RX_PPDU_END_20_RTT_NORMAL_MODE` | `20` | `0x50` | `[31:31]` | `0x80000000` | RTT capture mode (`0` = normal data/ACK packet, `1` = dedicated RTT frame). |

---

## 3. `tx_ppdu_start` Hardware Transmit Descriptor (`55` Dwords / `220` Bytes)

In `AR9888/v2`, the MAC/firmware programs `tx_ppdu_start` (`55` dwords / `220` bytes) to govern hardware PPDU transmission, TSF gating, TxBF steering (`cv_ptr`), and ACK/sounding channel-dump capture (`bb_capture_channel`).

| Field Name | Macro Prefix | Dword | Byte Offset | Bits `[MSB:LSB]` | Mask (`Hex`) | Physical Boundary & Control Role |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- |
| `start_of_frame_timestamp` | `TX_PPDU_START_11_START_OF_FRAME_TIMESTAMP` | `11` | `0x2c` | `[31:0]` | `0xffffffff` | **Hardware TX Launch Timestamp**: Exact TSF timestamp (`1 us`) written by PCU when the frame physically starts on the medium. |
| `tsf_filter_time` | `TX_PPDU_START_12_TSF_FILTER_TIME` | `12` | `0x30` | `[31:0]` | `0xffffffff` | **Hardware TSF Gate Comparator**: Compared against live TSF using `filter_Mask` (`dword 13`) to gate/expire hardware transmission at an exact TDMA slot boundary (`CONFIRMED`). |
| `cv_ptr` | `TX_PPDU_START_17_CV_PTR` | `17` | `0x44` | `[31:0]` | `0xffffffff` | **TxBF Compressed Steering Vector DMA Pointer**: Physical address of the beamforming steering vector (`CV`) DMA'd by PCU into the PHY (`CONFIRMED`). |
| `preload_txbf` | `TX_PPDU_START_19_PRELOAD_TXBF` | `19` | `0x4c` | `[27:27]` | `0x08000000` | Instructs PCU to DMA TxBF parameters (`cv_ptr`, `cv_len` bytes) into PHY prior to frame start. |
| `Apply_txbf` | `TX_PPDU_START_19_APPLY_TXBF` | `19` | `0x4c` | `[28:28]` | `0x10000000` | Applies the loaded TxBF steering matrix in the `TX_PHY_DESC` passed to baseband. |
| `bb_capture_channel` | `TX_PPDU_START_19_BB_CAPTURE_CHANNEL` | `19` | `0x4c` | `[30:30]` | `0x40000000` | **TX-Triggered RX Channel Capture (`CONFIRMED`)**: Sets `capture_channel` in the `TX_PHY_DESC` so the baseband automatically captures the $H(f)$ channel dump of the **incoming response frame (ACK / BlockAck / NDP)**! |
| `try_list_0` / `try_list_1` | `TX_PPDU_START_19_TRY_LIST_0..1` | `19..20` | `0x4c..0x50` | `[23:0]` | `0x00ffffff` | Hardware 16-try rate/bandwidth fallback schedule (`4` bits per try: `[3:2]=series`, `[1:0]=bw_index`). |
| `cv_len` | `TX_PPDU_START_20_CV_LEN` | `20` | `0x50` | `[15:0]` | `0x0000ffff` | Length in bytes of the TxBF `CV` buffer pointed to by `cv_ptr`. |
| `s0_bw20..s1_bw160` | `TX_PPDU_START_23..51` | `23..54` | `0x5c..0xd8` | `4 dwords each` | `series_bw[2][4]` | Embedded `series_bw` structures for Series 0 and Series 1 across `20/40/80/160 MHz`. |

---

## 4. `series_bw` Rate / Modulation / FEC Ceiling (`4` Dwords / `16` Bytes)

Each `series_bw` block (`#define NUM_OF_DWORDS_SERIES_BW 4`) defines the physical waveform parameters for one `(series, bandwidth)` combination inside `tx_ppdu_start`.

| Field Name | Macro Prefix | Dword | Byte Offset | Bits `[MSB:LSB]` | Mask (`Hex`) | Legal Values & Physical Ceiling |
| :--- | :--- | ---: | :--- | :--- | :--- | :--- |
| `tpc` | `SERIES_BW_0_TPC` | `0` | `0x00` | `[21:16]` | `0x003f0000` | **Per-Packet Transmit Power Control**: `0.5 dB` step resolution (`6` bits). |
| `stbc` | `SERIES_BW_0_STBC` | `0` | `0x00` | `[24:24]` | `0x01000000` | Enables Space-Time Block Coding (`2x1` Alamouti diversity gain for low-SNR CPEs). |
| `ldpc` | `SERIES_BW_0_LDPC` | `0` | `0x00` | `[25:25]` | `0x02000000` | Enables hardware 802.11ac LDPC FEC (`~1.5-2.0 dB` coding gain over BCC at high MCS). |
| `short_gi` | `SERIES_BW_0_SHORT_GI` | `0` | `0x00` | `[29:28]` | `0x30000000` | Short Guard Interval (`400 ns` vs `800 ns`). |
| `rate` | `SERIES_BW_1_RATE` | `1` | `0x04` | `[27:24]` | `0x0f000000` | **Strict `<legal:0-9>` Ceiling (`CONFIRMED`)**: For VHT (`preamble_type=3`), valid values are strictly `0..9` (`BPSK 1/2` through `256-QAM 5/6`). **Refutes** any hidden `1024-QAM` (`MCS 10/11`) or `4096-QAM` mode in the normal TX descriptor path. |
| `nss` | `SERIES_BW_1_NSS` | `1` | `0x04` | `[29:28]` | `0x30000000` | `<legal:0-2>` (`1..3` streams on `AR9888`, `1..2` streams on `QCA9882`). |
| `preamble_type` | `SERIES_BW_1_PREAMBLE_TYPE` | `1` | `0x04` | `[31:30]` | `0xc0000000` | `0=OFDM`, `1=CCK`, `2=HT`, `3=VHT`. |
| `beamforming` | `SERIES_BW_2_BEAMFORMING` | `2` | `0x08` | `[28:28]` | `0x10000000` | Enables TxBF steering for this rate/bandwidth entry. |

---

## 5. Baseband Channel-Dump & PHY Control Registers (`bb_lc_reg.h`, `Q14`)

Inspection of the 869 KB `AR9888/v2/extra/hw/bb_lc_reg.h` (`7,642` `#define` macros) reveals the exact baseband memory-mapped registers governing implicit/explicit CSI (`chaninfo`) capture, LDPC LLR scaling, FFT timing, and CCA/AGC:

| Register Name | Field Name | Address (`Hex`) | Bits `[MSB:LSB]` | Mask (`Hex`) | Subsystem & Physical Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `PHY_BB_CHAN_INFO_CHAN_TAB_B0` | `CHANINFO_WORD` | `0x00009b00` | `[31:0]` | `0xffffffff` | **Chain 0 Channel-Info Table Memory Window (`CONFIRMED`)**: Baseband RAM window storing captured per-tone $H(f)$ channel estimates for RX Chain 0. |
| `PHY_BB_CHAN_INFO_CHAN_TAB_B1` | `CHANINFO_WORD` | `0x0000ab00` | `[31:0]` | `0xffffffff` | **Chain 1 Channel-Info Table Memory Window (`CONFIRMED`)**: Baseband RAM window storing captured per-tone $H(f)$ channel estimates for RX Chain 1 (`0x1000` above Chain 0). |
| `PHY_BB_CHANINFO_CTRL` | `CAPTURE_CHAN_INFO` | `0x0000a370` | `[0:0]` | `0x00000001` | **Firmware Capture Arm Bit**: Arms baseband to capture channel estimates into `CHAN_TAB_B0`/`B1`. |
| `PHY_BB_CHANINFO_CTRL` | `DISABLE_CHANINFOMEM` | `0x0000a370` | `[1:1]` | `0x00000002` | **Memory Write Gate**: When `1`, blocks writes into channel-info memory; must be `0` to capture. |
| `PHY_BB_CHANINFO_CTRL` | `CAPTURE_SOUNDING_PACKET` | `0x0000a370` | `[2:2]` | `0x00000004` | Arms capture specifically on HT/VHT Null Data Packet (`NDP`) sounding frames. |
| `PHY_BB_CHANINFO_CTRL` | `CHANINFOMEM_S2_READ` | `0x0000a370` | `[3:3]` | `0x00000008` | **Spatial Stream 2 Bank Select**: Selects second spatial stream (`S2`) when reading `CHAN_TAB_B0`/`B1` in $2\times 2$ MIMO mode. |
| `PHY_BB_FRAME_CONTROL` | `PREPEND_CHAN_INFO` | `0x0000a238` | `[16:16]` | `0x00010000` | **Inline RX Prepend Control**: Instructs baseband to prepend captured channel info (`bb_length` bytes) to the RX frame stream. |
| `PHY_BB_CHAN_INFO_NOISE_PWR` | `NOISE_POWER` | `0x0000a374` | `[11:0]` | `0x00000fff` | 12-bit noise power measurement paired with the captured channel dump. |
| `PHY_BB_CHAN_INFO_GAIN_DIFF` | `FINE_PPM` / `ANALOG_GAIN_DIFF_01` | `0x0000a378` | `[11:0]` / `[18:12]` | `0x00000fff` / `0x0007f000` | Fine carrier/clock offset (`FINE_PPM`) and inter-chain analog gain delta (`ANALOG_GAIN_DIFF_01`) for calibrated $2\times 2$ MIMO $H$-matrix reconstruction. |
| `PHY_BB_CHAN_INFO_FINE_TIMING` | `FINE_TIMING` | `0x0000a37c` | `[21:12]` | `0x003ff000` | 10-bit fine symbol timing offset accompanying the channel capture. |
| `PHY_BB_CHAN_INFO_GAIN_B0` | `CHAN_INFO_RSSI_0` | `0x0000a380` | `[7:0]` | `0x000000ff` | Chain 0 RSSI (`[7:0]`), `RF_GAIN_0` (`[15:8]`), and `MB_GAIN_0` (`[22:16]`) latched at channel capture. |
| `PHY_BB_LDPC_CNTL1` | `LDPC_LLR_SCALING0` | `0x00009c04` | `[31:0]` | `0xffffffff` | LDPC decoder LLR scaling control word 0 (confirming fixed-silicon 11ac LDPC with tunable LLR scaling). |
| `PHY_BB_LDPC_CNTL2` | `LDPC_LATENCY` | `0x00009c08` | `[26:16]` | `0x07ff0000` | LDPC decoder iteration/latency budget (`LDPC_LLR_SCALING1` in `[15:0]`). |
| `PHY_BB_TIMING_CONTROLS_1` | `FFT_SCALING` | `0x00009800` | `[31:31]` | `0x80000000` | Baseband FFT scaling and fine timing threshold (`STE_THR` `[6:0]`, `TIMING_BACKOFF` `[16:13]`). |
| `PHY_BB_CCA_B0` | `CCA_CONTROL_WORD` | `0x00009e1c` | `[31:0]` | `0xffffffff` | Chain 0 Clear Channel Assessment (CCA) threshold and energy-detection control. |
| `PHY_BB_AGC_CONTROL` | `DO_CALIBRATE_AND_NF` | `0x0000a2c4` | `[1:0]` | `0x00000003` | Hardware AGC calibration (`bit 0`) and noise-floor measurement trigger (`bit 1`). |

---

## 6. Closed-Loop Physical Boundary Implications for openMAX

1. **Zero-Overhead ACK-Piggybacked Channel Sounding (`CONFIRMED`)**:
   - Setting `TX_PPDU_START_19_BB_CAPTURE_CHANNEL` (`0x40000000`) on a downlink unicast PPDU combined with `PHY_BB_CHANINFO_CTRL = 0x00000001` (`CAPTURE_CHAN_INFO=1, DISABLE_CHANINFOMEM=0`) causes the baseband to capture the full $H(f)$ channel estimate of the CPE's returning `ACK` or `BlockAck` into `0x00009b00` (`CHAN_TAB_B0`) and `0x0000ab00` (`CHAN_TAB_B1`) and assert `RX_PPDU_END_19_BB_CAPTURED_CHANNEL` (`0x02000000`).
2. **Sub-Microsecond Propagation Ranging (`12.5 ns`) & Per-Pilot EVM (`CONFIRMED`)**:
   - Every received PPDU already populates `locationing_timestamp` (`12.5 ns` resolution at `80 MHz`), `rtt_corr_value` (`15-bit` correlation peak), and `16` pilot EVM words (`evm_p0..evm_p15`) in `rx_ppdu_end` (`0x00..0x50`).
3. **No Hidden Higher-Order QAM in Standard Descriptor Path (`REFUTED`)**:
   - `series_bw.h` (`Q13`) proves `SERIES_BW_1_RATE` is strictly bounded to `<legal:0-9>` (`256-QAM 5/6`) in normal packet mode. Arbitrary constellation experiments exist only in the non-packet `GENWAVEFORM` DAC test path (`cmdGenWaveformHandler.h`, analyzed in Workstream E3).
