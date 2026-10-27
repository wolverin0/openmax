<!-- doc-head: FIRMWARE_RE_TARGET_MAP.md preserved document content -->
<!-- /doc-head -->

# QCA988x / AR9888 Target Firmware Reverse-Engineering Map (`PB-010` & `PB-011`)

- **Date**: 2026-10-24
- **Gates Closed**: `PB-010` (`PASSED`), `PB-011` (`PASSED`)
- **Offline Extractors**:
  - [`tools/qca988x/wmi_htt_strip_site_mapper.py`](../tools/qca988x/wmi_htt_strip_site_mapper.py) $\rightarrow$ [`artifacts/qca988x/pb_010_wmi_htt_strip_map.json`](../artifacts/qca988x/pb_010_wmi_htt_strip_map.json)
  - [`tools/qca988x/sgmt_container_inspector.py`](../tools/qca988x/sgmt_container_inspector.py) $\rightarrow$ [`artifacts/qca988x/pb_011_sgmt_container_audit.json`](../artifacts/qca988x/pb_011_sgmt_container_audit.json)
- **Verification Suites**:
  - [`tests/test_pb_010_wmi_htt_strip_map.py`](../tests/test_pb_010_wmi_htt_strip_map.py)
  - [`tests/test_pb_011_sgmt_container_inspector.py`](../tests/test_pb_011_sgmt_container_inspector.py)

---

## 1. Executive Summary (`PB-010` & `PB-011`)

1. **Bit-Exact `SGMT` BCL-LZ77 Container Decompression (`CONFIRMED`, `PB-011`)**:
   - All four embedded QCA988x target binaries inside `umac.ko` (`otp_AR9888v2_bin`, `athwlan_AR9888v2_ptmp_ap_bin`, `athwlan_AR9888v2_ptmp_sta_bin`, `athwlan_AR9888v2_ptp_bin`) across both `WA.v8.7.25` and `XC.v8.7.25` use Qualcomm Atheros `BMI_SGMT` (`"SGMT"`, version `1`) with Basic Compression Library (BCL) LZ77 per-segment compression (`1`-byte escape marker + `7`-bit big-endian varint `(length, distance)` back-references).
   - Every image decompresses with **zero trailing bytes** (`parsed_end_offset == container_size_bytes`), terminating with `[0x00983c00, 0xfffffffd]` (`BMI_SGMT_BEGIN_ADDR`, entry point `0x00983c00`) and `[0x00000000, 0xffffffff]` (`BMI_SGMT_END`).
   - Neither the `SGMT` container nor `ol_transfer_bin_file` (`umac.ko` `.text+0xbd4a0`) contains a cryptographic signature trailer. Only the `2,116`-byte `raw_Data` QC98xx board calibration block has a 16-bit XOR checksum (`xor_sum == 0xffff` across `1,058` `uint16_le` words, verified at `.text+0xbd650..0xbd6b0`).

2. **Exact Host $\leftrightarrow$ Target WMI Opcode & Handler Map (`CONFIRMED`, `PB-010`)**:
   - By decompressing the `SGMT` IRAM (`0x00980000`, `0x00983c00`) and DRAM (`0x0040b000`, `0x0040cce0..0x0040d250`) segments, we located the exact target WMI dispatch table entries and IRAM handler pointers for `0x9064` (`WMI_UBNT_POLL_CMDID`), `0x9044` (`WMI_PEER_RATE_RETRY_SCHED_CMDID`), and `0x901f` (`WMI_PEER_SET_PARAM_CMDID` / `WMI_UBNT_POLL_EVENTID`).

3. **Three-Stage `rx_ppdu_end` Strip Pipeline & Pre-Strip Hook Design (`CONFIRMED`, `PB-010`)**:
   - `htt_h2t_rx_ring_cfg_msg_ll` (`umac.ko` `.text+0xd5298`) programs the exact dword offsets of `htt_host_rx_desc_base`: `rx_header=1` (`4`B), `fw_rx_desc=2` (`8`B), `rx_attention=6` (`24`B), `rx_frag_info=9` (`36`B), `rx_mpdu_start=3` (`12`B), `rx_mpdu_end=14` (`56`B), `rx_msdu_start=15` (`60`B), `rx_msdu_end=25` (`100`B), `rx_ppdu_start=46` (`184`B), and **`rx_ppdu_end=62` (`248`B)**.
   - `htt_rx_get_vowext_stats` (`.text+0xd6ad4`) reads only `rssi_comb` (`+192`), per-chain RSSI (`+60..+76`), rate flags (`+80..+88`), and `tsf32` (`+164`), ignoring `rx_ppdu_end` (`+248..+335`), before `ol_rx_deliver` (`.text+0xcd6ec`) calls `skb_pull` (`0xcd760`) and discards the descriptor prefix.

---

## 2. `PB-010`: WMI Opcode Cross-Reference (`Host` $\rightarrow$ `Target IRAM/DRAM`)

| WMI Opcode | Symbolic Name (`umac.ko` `.rodata.str1.4`) | Host Sender / Listener (`WA.v8.7.25` / `XC.v8.7.25`) | Payload Size | Target Dispatch Table VA (`ptmp_ap` / `ptmp_sta` / `ptp`) | Target IRAM Handler Pointers (`ptmp_ap`) |
| :---: | :--- | :--- | ---: | :--- | :--- |
| **`0x9064`** | `WMI_UBNT_POLL_CMDID` | `ubnt_poll_host_ht_comm_tx` (`.text+0x1080`, call at `0x1114`) | `1,024` B | `0x0040fbcc` / `0x0040fc7c` / `0x0040f70c` | `0x009b1bd8`, `0x009b1cfc`, `0x009b1d40`, `0x009b0428` (with OUI `0x00222700`) |
| **`0x9070`** | `WMI_UBNT_POLL_CMDID` (2WA/2XC Wave-2 shift) | Shifted Wave-2 (`QCA9984`) table only; not used on Wave-1 `WA`/`XC` | `1,024` B | N/A on `AR9888v2` (`0x9064` is used) | N/A |
| **`0x9044`** | `WMI_PEER_RATE_RETRY_SCHED_CMDID` | `wmi_send_node_rate_sched` (`umac.ko` `.text+0xb0120`, opcode at `0xb0184`) | `188` B (`0xbc`) | `0x00980e1c` / `0x00980e1c` / `0x00980df4` | `0x009a8834`, `0x009a974c`, `0x009a96f8`, `0x009a9550` |
| **`0x9045`** | `WMI_WLAN_PROFILE_ENABLE_PROFILE_ID_CMDID` (WA/XC) | `wmi_unified_wlan_profile_enable` (`umac.ko` `.text+0xa9284`, opcode at `0xa92c8`) | `12` B | Shifted rate-sched on `2WA`/`2XC` | Profile enable on `AR9888v2` |
| **`0x901f`** | `WMI_PEER_SET_PARAM_CMDID` / `WMI_UBNT_POLL_EVENTID` | Host TX: `wmi_unified_node_set_param` (`.text+0xaff54`); Host RX event: `ubnt_poll_host.ko` `.text+0x9b4`, `0xb6c`, `0xf60` | `20` B (`0x14`) | `0x0098058c` / `0x0098058c` / `0x00980594` | `0x009c4dc0`, `0x009c4df0` |

---

## 3. `PB-010`: HTT RX Descriptor Layout & `rx_ppdu_end` Strip Pipeline

### 3.1 Exact Dword & Byte Layout Programmed by `htt_h2t_rx_ring_cfg_msg_ll` (`.text+0xd5298`)

| Descriptor Section | Programmed Dword Offset | Byte Offset in `htt_host_rx_desc_base` | Section Size | Key Hardware Fields |
| :--- | ---: | ---: | ---: | :--- |
| `rx_header` | `1` | `4` (`0x04`) | `4` B | Ring buffer header |
| `fw_rx_desc` | `2` | `8` (`0x08`) | `4` B | `u8 fw_rx_desc_bytes` (discard/forward/inspect/mcast flags) |
| `rx_mpdu_start` | `3` | `12` (`0x0c`) | `12` B | `peer_id`, `seq_num`, `pn`, `encrypt_type`, `tid` |
| `rx_attention` | `6` | `24` (`0x18`) | `12` B | `first_mpdu`, `last_mpdu`, `msdu_done`, `fcs_err`, `phy_err` |
| `rx_frag_info` | `9` | `36` (`0x24`) | `16` B | Ring buffer pointers |
| `rx_mpdu_end` | `14` | `56` (`0x38`) | `4` B | `overflow_err`, `mpdu_length_err` |
| `rx_msdu_start` | `15` | `60` (`0x3c`) | `40` B | Per-chain RSSI (`+60..+76`), `sgi`, `rate_mcs`, `bw`, `nss` (`+80..+88`) |
| `rx_msdu_end` | `25` | `100` (`0x64`) | `84` B | Decap/L3/L4 checksum & `wep_key_id` |
| `rx_ppdu_start` | `46` | `184` (`0xb8`) | `40` B | `rssi_comb` (`+192`), `preamble_type`, `is_greenfield` |
| **`rx_ppdu_end`** | **`62`** | **`248` (`0xf8`)** | **`88` B (`22` dwords)** | `evm_p0..evm_p15` (`+248..+311`), `tsf_timestamp` (`+312`), `wb_timestamp` (`+316`), `txbf_h_info` (`+324` bit 10), `bb_captured_channel` (`+328` bit 25), `bb_length` (`+332` bits `15:0`) |

### 3.2 Pre-Strip Export Specification (`openmax_prestrip_rx_ppdu_telemetry_v1`)
To recover `evm_p0..evm_p15`, `txbf_h_info`, `bb_captured_channel`, and `bb_length` without altering the 802.11 datapath:
- **AirOS Hook Point**: `htt_rx_get_vowext_stats` (`.text+0xd6ad4`) / `ol_rx_deliver` (`.text+0xcd6ec`) immediately before `skb_pull` (`0xcd760`).
- **OpenWrt `ath10k` Hook Point**: `ath10k_htt_rx_h_ppdu()` in `htt_rx.c` when `RX_ATTENTION_FLAGS_LAST_MPDU` is asserted, exporting the 40-byte `openmax_prestrip_rx_ppdu_telemetry_v1` struct into a lockless relayfs/debugfs ring buffer.

---

## 4. `PB-011`: `SGMT` Container Segment Map Across `WA.v8.7.25` & `XC.v8.7.25`

| Firmware Symbol (`WA.v8.7.25`) | Total Container Bytes | Segment 1 (`0x00980000` IRAM Vector/Patch) | Segment 2 (`0x0040b000` DRAM Data 1) | Segment 3 (`0x0040cce0..0x0040d250` DRAM Data 2) | Segment 4 (`0x00983c00` IRAM Main Text) | Entry Point (`0xfffffffd`) | EOF Match |
| :--- | ---: | ---: | ---: | ---: | ---: | :---: | :---: |
| `otp_AR9888v2_bin` | `6,917` | `108` B (`comp: 105`B) | `28` B (`comp: 26`B) | `25,601` B at `0x0040b020` (`comp: 4,913`B) | `1,996` B (`comp: 1,817`B) | `0x00983c00` | **Yes (`6,917`)** |
| `athwlan_AR9888v2_ptmp_ap_bin` | `250,900` | `6,328` B (`comp: 6,181`B) | `8,600` B (`comp: 4,863`B) | `10,888` B at `0x0040d1a0` (`comp: 5,618`B) | `278,756` B (`comp: 234,182`B) | `0x00983c00` | **Yes (`250,900`)** |
| `athwlan_AR9888v2_ptmp_sta_bin` | `233,509` | `6,060` B (`comp: 5,940`B) | `8,772` B (`comp: 4,922`B) | `10,888` B at `0x0040d250` (`comp: 5,622`B) | `259,252` B (`comp: 216,969`B) | `0x00983c00` | **Yes (`233,509`)** |
| `athwlan_AR9888v2_ptp_bin` | `214,299` | `5,720` B (`comp: 5,597`B) | `7,384` B (`comp: 4,182`B) | `10,888` B at `0x0040cce0` (`comp: 5,621`B) | `237,524` B (`comp: 198,843`B) | `0x00983c00` | **Yes (`214,299`)** |
