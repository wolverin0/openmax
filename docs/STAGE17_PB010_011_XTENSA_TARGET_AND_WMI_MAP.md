<!-- doc-head: STAGE17_PB010_011_XTENSA_TARGET_AND_WMI_MAP.md preserved document content -->
<!-- /doc-head -->

# Stage 17 — Ground-Up Physical Boundary (PB-010 & PB-011): QCA988x / AR9888v2 Xtensa Target Binary, BMI Segment/Signature Boundary & WMI/HTT Dispatch Map

- **Task ID**: `T-PB-010-011-XTENSA-WMI-HTT-MAP`
- **Extractor Module**: [`analysis/pb010_011_xtensa_wmi_htt_extractor.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/analysis/pb010_011_xtensa_wmi_htt_extractor.py)
- **Generated Artifact**: [`artifacts/physical_boundary/pb010_011_xtensa_wmi_htt_map_20261025.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/physical_boundary/pb010_011_xtensa_wmi_htt_map_20261025.json)
- **Test Suite**: [`tests/test_pb010_011_xtensa_wmi_htt_extractor.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_pb010_011_xtensa_wmi_htt_extractor.py)
- **Execution Mode**: Strictly Offline Static Analysis (`ZERO_LIVE_DEVICE_CONTACT`)

---

## 1. Executive Summary & Epistemic Verdicts

| Boundary ID | Deliverable Question | Epistemic Status | Key Finding |
| :--- | :--- | :--- | :--- |
| **`PB-011`** | QCA988x (`AR9888v2` / Peregrine v2 `0x0041`) `SGMT` container, BMI segment descriptors, entry point, and cryptographic signature vs plain BMI load/CRC boundary | **`CONFIRMED`** (static container + `bmi.c`/`bmi.h` loader contract; runtime 1-byte RAM patch gated by `PB-040`) | All 3 embedded QCA988x target binaries in Ubiquiti `umac.ko` (`ptmp_ap`, `ptmp_sta`, `ptp`) use the `SGMT` (`0x544d4753` LE / `0x53474d54` BE) BMI LZ77/RLE segmented stream with 4 `PAYLOAD` segments (`0x00980000` IRAM stub, `0x0040b000` DRAM `.rodata`, `0x0040d140`/`0x0040d130`/`0x0040cbc0` DRAM `.data`, `0x00983c00` IRAM `.text`), `BEGINADDR = 0x00983c00`, and `DONE = 0`. `consumed_bytes == container_size` (**`0` trailing RSA/ECDSA/X.509 signature bytes**), and `enum bmi_cmd_id` ([`bmi.h:59-79`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/srccache/ath10k-ct/ath10k-7.2/bmi.h#L59-L79)) contains no signature-verification opcode on Peregrine v2. |
| **`PB-010`** | Exact WMI (`PDEV_PARAM_*`, `VDEV_PARAM_*`, `PEER_PARAM_*`, plus Ubiquiti `0x9064`/`0x9070` & `0x9044`/`0x9045`) and HTT (`HTT_T2H_MSG_TYPE_RX_IND`, `rx_ppdu_end`, `tx_ppdu_start`, `series_bw`) dispatch boundary | **`CONFIRMED`** | Mapped the complete WMI 10.x/10.2 command space (`0x9000..0x9FFF`), explaining why native `WMI_PEER_RATE_RETRY_SCHED_CMDID` is `0x9044` on WA/XC (`10.1`) and `0x9045` on 2WA/2XC (`10.2`), while Ubiquiti's custom `ubnt_poll_ht_comm` tunnel is `0x9064` (`36,964`) on WA/XC and `0x9070` (`36,976`) on 2WA/2XC, feeding the 51-entry Xtensa branch table at `0x009b2037` (`ptmp_ap`). Mapped the 84-byte `rx_ppdu_end` (`evm_p0..evm_p15`, `tsf_timestamp`, `wb_timestamp`, `locationing_timestamp`, `txbf_h_info`, `bb_captured_channel`, `bb_length`), 84-byte `tx_ppdu_start` (`bb_capture_channel`, `cv_ptr`, `cv_len`), and 16-byte `series_bw` (`ldpc`, `stbc`, `sgi`, `txbf`, `chain_mask`, `tpc`). |
| **`PB-021..PB-050`** | Out-of-the-Box Ground-Up target-level variables that bypass host `mac80211` limits | **`CONFIRMED`** (static register/descriptor/WMI contract) | Pinpointed the exact descriptor bits, WMI opcodes, and baseband registers for **`PB-021`** (per-PPDU channel capture & 16-word pilot EVM via `TRACE_EVENT(ath10k_htt_rx_desc)` prior to `skb_pull`), **`PB-030`** (5/10 MHz `HALF_RATE`/`QUARTER_RATE` clock divider `chanbw`), **`PB-031`** (`bb_lc_reg.h` `cca_thresh62`/AGC/correlator + per-series `ldpc`/`stbc`), and **`PB-050`** (target 12.5 ns `locationing_timestamp` + `wb_timestamp` + `0x9064`/`0x9044` slot/TXQ hooks). |

---

## 2. PB-011 — QCA988x (`AR9888v2` / `0x0041`) `SGMT` Container & BMI Segment Map

### 2.1 `SGMT` Header & Metadata Sentinel Contract ([`bmi.h:196-224`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/srccache/ath10k-ct/ath10k-7.2/bmi.h#L196-L224))

- **File Header (`8` bytes)**:
  - `magic_num`: `0x544d4753` little-endian (`0x53474d54` big-endian = ASCII `"SGMT"`, `BMI_SGMTFILE_MAGIC_NUM`)
  - `file_flags`: `0x00000001` (`BMI_SGMTFILE_FLAG_COMPRESS` — BMI LZ77/RLE zero-run compression)
- **Segment Record Header (`8` bytes per record: `__le32 addr; __le32 length;`)**:
  - Standard `length` (`< 0xFFFFFFFC`): `PAYLOAD` segment downloaded via `BMI_LZ_STREAM_START (13)` + `BMI_LZ_DATA (14)` into target `addr`.
  - `0xFFFFFFFE` (`BMI_SGMTFILE_BDDATA`): Board Data segment.
  - `0xFFFFFFFD` (`BMI_SGMTFILE_BEGINADDR`): Sets Xtensa application start PC (`addr = 0x00983c00`) via `BMI_SET_APP_START (5)` / `BMI_EXECUTE (4)`.
  - `0xFFFFFFFC` (`BMI_SGMTFILE_EXEC`): Immediate function execution via `BMI_EXECUTE (4)`.
  - `0xFFFFFFFF` (`BMI_SGMTFILE_DONE`): End of segmented stream (`BMI_DONE (1)` terminates boot-only BMI access).

### 2.2 Exact Segment Layout Across All 3 Role-Specific `AR9888v2` Target Images ([`airmax-sgmt-map-20261006.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/raw/airmax-sgmt-map-20261006.json))

| Symbol in `umac.ko` | Container Size | Trailing Signature Bytes | Seg 0 (`0x00980000` IRAM Stub) | Seg 1 (`0x0040b000` DRAM `.rodata`) | Seg 2 (`0x0040d140`/`d130`/`cbc0` DRAM `.data`) | Seg 3 (`0x00983c00` IRAM Main `.text`) | Entry (`BEGINADDR`) | `0x9064` (`36964`) Literal Address |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`athwlan_AR9888v2_ptmp_ap_bin`** | `251,681` B | **`0` B** | `6,496` B (`6,351` B LZ) | `8,500` B (`4,774` B LZ) | `0x0040d140`: `10,864` B (`4,904` B LZ) | `283,604` B (`235,604` B LZ) | `0x00983c00` | `0x0040fb54` (`4,258,644`) |
| **`athwlan_AR9888v2_ptmp_sta_bin`** | `234,072` B | **`0` B** | `6,232` B (`6,093` B LZ) | `7,448` B (`4,249` B LZ) | `0x0040d130`: `10,864` B (`4,903` B LZ) | `264,164` B (`218,779` B LZ) | `0x00983c00` | `0x0040fb44` (`4,258,628`) |
| **`athwlan_AR9888v2_ptp_bin`** | `213,701` B | **`0` B** | `5,876` B (`5,738` B LZ) | `7,100` B (`4,108` B LZ) | `0x0040cbc0`: `10,800` B (`4,845` B LZ) | `242,228` B (`198,962` B LZ) | `0x00983c00` | `0x0040f5d4` (`4,257,236`) |

### 2.3 Target Memory Architecture & Entry-Point BSS Zero-Init (`0x00983c00`)

1. **DRAM (`0x00400000 .. 0x00450000`, `320 KiB`)** ([`coredump.c:986-1017`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/physical_boundary/source_manifest.json#L1484-L1489), [`targaddrs.h:25-45`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/physical_boundary/source_manifest.json#L1573-L1578)):
   - `0x00400800`: `QCA988X_HOST_INTEREST_ADDRESS` (`hi_failure_state`, `hi_dbglog_hdr`, `hi_board_data`, `hi_board_data_initialized`).
   - `0x0040b000`: Segment 1 (`.rodata` strings & constant tables; e.g., `"ubnt_set_power_range"` at `0x0040b940` XREF'd from `0x00981068`, `"ubnt_poll_ptmp_init"` at `0x0040ba30` XREF'd from `0x009b201c`).
   - `0x0040d140`: Segment 2 (`.data` initialized dispatch tables, including WMI command ID `0x00009064` at `0x0040fb54`).
2. **IRAM (`0x00980000 .. 0x009c9000+`)**:
   - `0x00980000`: Segment 0 (`6,496` B high code stub).
   - `0x00983c00`: Segment 3 (`283,604` B main Xtensa `.text`) and `BEGINADDR` entry point.
   - At `0x00983c00` ([`xtensa-qualification-20261006.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/raw/xtensa-qualification-20261006.json)), the startup routine executes an `l32r` + `sub` + `movi a10, 0` + `s8i` loop to zero-initialize the target `.bss` region before branching into target OS/WMI initialization.

---

## 3. PB-010 — Exact WMI & HTT Dispatch Boundary

### 3.1 WMI 10.x / 10.2 Command & Parameter Space ([`wmi.h:1337-1700`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/srccache/ath10k-ct/ath10k-7.2/wmi.h#L1337-L1700))

| WMI Command / Parameter | 10.1 / WA/XC Value | 10.2 / 2WA/2XC Value | Role & Control Boundary |
| :--- | :---: | :---: | :--- |
| `WMI_PDEV_SET_CHANNEL_CMDID` | `0x9005` | `0x9005` | Sets center freq, mode, and `chanbw` (`5`/`10`/`20`/`40`/`80` MHz) |
| `WMI_PDEV_SET_PARAM_CMDID` | `0x9006` | `0x9006` | Sets `wmi_10x_pdev_param` (`0x01..0x36`, e.g., `DYNAMIC_BW=0x0a`, `ANI_ENABLE=0x1c`, `ANI_OFDM_LEVEL=0x1f`, `BURST_DUR=0x23`, `RTS_FIXED_RATE=0x31`) |
| `WMI_VDEV_SET_PARAM_CMDID` | `0x9019` | `0x9019` | Sets `wmi_10x_vdev_param` (`0x01..0x34`, e.g., `SLOT_TIME=0x07`, `FIXED_RATE=0x19`, `SGI=0x1a`, `LDPC=0x1b`, `TX_STBC=0x1c`, `RX_STBC=0x1d`, `RC_NUM_RETRIES=0x2c`, `CABQ_MAXDUR=0x2f`) |
| `WMI_PEER_SET_PARAM_CMDID` | `0x901e` | `0x901f` | Sets `wmi_peer_param` (`AMPDU=0x02`, `CHAN_WIDTH=0x04`, `NSS=0x05`, `USE_4ADDR=0x06`, `USE_FIXED_PWR=0x08`, `FIXED_RATE=0x09`) |
| **`WMI_PEER_RATE_RETRY_SCHED_CMDID`** | **`0x9044`** (`36,932`) | **`0x9045`** (`36,933`) | Programs per-peer 4-series hardware rate & retry schedule (`struct wmi_peer_fixed_rate_cmd`: `vdev_id`, `peer_macaddr`, `rate_mode`, `rate_series`, `rate_retries`) |
| `WMI_VDEV_SPECTRAL_SCAN_CONFIGURE_CMDID` | `0x9056` | `0x9058` | Configures QCA988x baseband FFT spectral scan (`count`, `period`, `fft_size`, `gc_ena`, `noise_pwr_cal`) |
| `WMI_VDEV_SPECTRAL_SCAN_ENABLE_CMDID` | `0x9057` | `0x9059` | Triggers/clears/enables spectral scan (`PHY_ERROR_GEN_SPECTRAL_SCAN = 0x26`) |
| **`WMI_UBNT_POLL_HT_COMM_CMDID`** | **`0x9064`** (`36,964`) | **`0x9070`** (`36,976`) | Ubiquiti `ubnt_poll_host_ht_comm_tx` WMI tunnel (`ubnt_poll_ht_comm_setup` types `0x00..0x32` -> Xtensa 51-entry branch table at `0x009b2037`) |
| `WMI_PDEV_UTF_CMDID` | `0x9ffe` | `0x9ffe` | Segmented TLV2.0 / UTF testmode command channel (`MAX_WMI_UTF_LEN = 252` B) |

### 3.2 HTT & Hardware Descriptor Boundary ([`rx_ppdu_end.h`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/physical_boundary/source_manifest.json#L58-L195), [`tx_ppdu_start.h`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/physical_boundary/source_manifest.json#L286-L361), [`series_bw.h`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/research/physical_boundary/source_manifest.json#L197-L284), [`rx_desc.h:926-970`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/research/srccache/ath10k-ct/ath10k-7.2/rx_desc.h#L926-L970))

| Descriptor / Struct | Size | Word / Bit Offset | Field | Hardware Semantics & Host Export Path |
| :--- | :---: | :---: | :--- | :--- |
| **`rx_ppdu_end_common`** | `72` B (`18` dwords) | Dwords `0..15` | `evm_p0 .. evm_p15` | 16 pilot EVM words covering spatial streams `0..3` per received PPDU; stripped by `skb_pull` in `ath10k_htt_rx_amsdu_pop` unless captured via `TRACE_EVENT(ath10k_htt_rx_desc)` |
| **`rx_ppdu_end_common`** | — | Dword `16` | `tsf_timestamp` | 32-bit MAC TSF sampled on rising edge of `rx_clear` (`1 us` resolution) |
| **`rx_ppdu_end_common`** | — | Dword `17` | `wb_timestamp` | Free-running `1 us` WLAN/BT timer (immune to beacon TSF jumps) |
| **`rx_ppdu_end_qca988x`** | `12` B (`3` dwords) | Dword `18` `[7:0]` | `locationing_timestamp` | Sub-microsecond fractional clock (`0..79` at `80 MHz` = **`12.5 ns` resolution**) valid on every PPDU |
| **`rx_ppdu_end_qca988x`** | — | Dword `18` (`flags BIT(2)`) | `txbf_h_info` | Packet payload carries H-matrix debug info (`RX_PPDU_END_FLAGS_TXBF_H_INFO`) |
| **`rx_ppdu_end_qca988x`** | — | Dword `19` (`info0 BIT(25)`) | `bb_captured_channel` | BB captured a channel dump into channel-dump memory (`RX_PPDU_END_INFO0_BB_CAPTURED_CHANNEL`) |
| **`rx_ppdu_end_qca988x`** | — | Dword `20` `[15:0]` | `bb_length` | Baseband debug byte length when BB descriptor preamble is `0x80..0xFF` |
| **`tx_ppdu_start`** | `84` B (`21` dwords) | Dword `17` `[31:0]` | `cv_ptr` | 32-bit DMA pointer to compressed-V beamforming steering matrix for BB SVD |
| **`tx_ppdu_start`** | — | Dword `19` | `bb_capture_channel` & `cv_len` | Requests BB channel dump on next good RX packet (`TX_PPDU_START_19_BB_CAPTURE_CHANNEL`) + compressed-V length (`0..2047` octets) |
| **`series_bw`** | `16` B (`4` dwords) | Dwords `0..3` | `ldpc`, `stbc`, `sgi`, `txbf`, `chain_mask`, `tpc`, `rate`, `nss`, `preamble_type` | Per-series, per-bandwidth (`20`/`40`/`80` MHz) hardware transmit vector |

---

## 4. Out-of-the-Box Ground-Up Target-Level Bypass Variables (`PB-021`, `PB-030`, `PB-031`, `PB-050`)

1. **`PB-021` — Per-PPDU Channel Capture, 16-Pilot EVM & H-Info Export**:
   - **Bypassed `mac80211` Limit**: `ath10k_htt_rx_h_ppdu` (`htt_rx.c:1268-1320`) discards `evm_p0..evm_p15`, `locationing_timestamp`, `txbf_h_info`, `bb_captured_channel`, and `bb_length` when `skb_pull` strips `htt_rx_desc`.
   - **Ground-Up Hook**: Capture `htt_rx_desc` before `skb_pull` via `TRACE_EVENT(ath10k_htt_rx_desc)` (`trace.h:424-452`) and trigger `tx_ppdu_start.bb_capture_channel` (`word 19`).
2. **`PB-030` — Sub-20 MHz (`5 MHz` Quarter-Rate / `10 MHz` Half-Rate) Clock Divider (`chanbw`)**:
   - **Bypassed `mac80211` Limit**: Standard VHT channel tables enforce `20/40/80 MHz`, forfeiting `+3 dB` (`10 MHz`) and `+6 dB` (`5 MHz`) noise-floor gain.
   - **Ground-Up Hook**: AR9888v2 `HALF_RATE` (`10 MHz`) and `QUARTER_RATE` (`5 MHz`) modes in `tcmd.c:165-169,533-539` & `testcmd_ar988x.h:128-140` + `WMI_10X_PDEV_SET_CHANNEL_CMDID` / debugfs `chanbw` with scaled coverage-class slot/ACK timing.
3. **`PB-031` — Baseband CCA Energy Detect (`cca_thresh62`), AGC & Per-Series LDPC/STBC**:
   - **Bypassed `mac80211` Limit**: Host `mac80211` exposes no API for QCA988x baseband CCA desensitization or per-retry-series LDPC/STBC fallback.
   - **Ground-Up Hook**: `AR9888/v2/extra/hw/bb_lc_reg.h` (`cca_thresh62`, weak-signal correlator, AGC NF/gain, LDPC LLR scaling), `WMI_10X_PDEV_PARAM_ANI_OFDM_LEVEL` (`0x1f`), `WMI_10X_SET_CCA_PARAMS_CMDID`, and `series_bw` (`ldpc`, `stbc`, `sgi`).
4. **`PB-050` — Target-Resident TXOP / Slot Timer, `12.5 ns` Locationing Clock & Poll Hooks**:
   - **Bypassed `mac80211` Limit**: Host `ieee80211_txq` gating suffers from PCIe/CE/HTT queue latency (`~200–800 us`).
   - **Ground-Up Hook**: Combine `rx_ppdu_end` hardware timestamps (`wb_timestamp` `1 us` + `locationing_timestamp` `12.5 ns`) with target-side `WMI_PEER_RATE_RETRY_SCHED_CMDID` (`0x9044`/`0x9045`) and Ubiquiti target `ubnt_poll` WMI `0x9064`/`0x9070` sub-commands (`0x02` mode/timer, `0x11` slot queue, `0x17` `set_txq_param`, `0x1e` `set_rate_override`).
