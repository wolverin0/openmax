<!-- doc-head: STAGE476A_XTENSA_HT_COMM_OPCODES_FULL_TABLE_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 476A — `QCA988x` Xtensa `HT_COMM` Full 51-Slot Opcode Tables & Wire Protocol Dissection

- **Claim Status**: `CONFIRMED` (100% static binary instruction disassembly across `WA.v8.7.25` and `XC.v8.7.25` `athwlan.bin` `SGMT` images; `live_devices_touched = False`).
- **Subsystem Attribution**: `proprietary airMAX/LTU module` (`ubnt_poll` Target-Side `HT_COMM` RPC over `WMI` `0x901f`).
- **Generator & Receipt**:
  - [`dissect_stage476a_xtensa_ht_comm_opcodes_full_table_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage476a_xtensa_ht_comm_opcodes_full_table_re.py)
  - [`stage476a_xtensa_ht_comm_opcodes_full_table_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage476a_xtensa_ht_comm_opcodes_full_table_re.json)
  - [`test_stage476a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage476a.py)

---

## 1. Executive Summary & Wire Header Architecture

The proprietary `HT_COMM` channel between host `ubnt_poll_host.ko` and the `QCA988x` Xtensa target (`0x009b1024..0x009b4480`, **100% byte-identical between `WA.v8.7.25` and `XC.v8.7.25`**) uses a **9-byte big-endian wire header**:
- **Bytes `0..1`**: Magic `0xaa 0x05` (`movi.n a8, -86` / `movi.n a11, 5` in `ht_comm_pack_msg` @ `0x009b2f98` and checked in `ht_comm_unpack_msg` @ `0x009b3c88`).
- **Byte `2`**: `uint8_t opcode` (`0..50`, bounds-checked via `movi.n a8, 51; bgeu a10, a8, default`).
- **Bytes `3..6`**: `uint32_t seq_num` (network byte order).
- **Bytes `7..8`**: `uint16_t payload_len` (network byte order).

Target-to-Host packets are serialized by `ht_comm_pack_msg` (`0x009b2f98`) and transmitted by `ht_comm_tx_send` (`0x009b43a0`) using **`WMI` Event ID `0x901f`** (`literal @ 0x00981fa4`) through `*(0x0040ce3c) + 0x10`.

---

## 2. Complete Active `HT_COMM` Opcode Table (Across 51 Slots `0..50`)

Out of 51 slots (`0..50`), **21 opcodes are active in `ht_comm_rx_dispatch` (`JT @ 0x009b1067`)**, **24 opcodes are active in `ht_comm_unpack_msg` (`JT @ 0x009b3d21`)**, and **14 opcodes are serialized in `ht_comm_pack_msg` (`0x009b2f98`)**:

| Opcode | Hex | Name | Direction | RX Handler | Unpack Handler | Payload | Target Effect / Struct Field Modified |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `1` | `0x01` | `HT_COMM_OP_POLL_INIT_PARAMS` | Host $\rightarrow$ Target | `0x009b1459` | `0x009b423c` | `13 B` | Writes target `+0x04`, `+0x08`, `+0x29`, calls `0x009ae8ec` |
| `2` | `0x02` | `HT_COMM_OP_POLL_START_STOP` | Host $\rightarrow$ Target | `0x009b1438` | `0x009b3dba` | `1 B` | Sets `+0x2c`; calls `0x009b2800` (start) / `0x009af98c` (stop) |
| `3` | `0x03` | `HT_COMM_OP_TARGET_EVENT_BASIC` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b423c` | `13 B` | 3x `u32` + 1x `u8` event report |
| `4` | `0x04` | `HT_COMM_OP_TARGET_STATUS_REPORT` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `4 B` | Packed at `0x009b31fd` (1x `u32`) $\rightarrow$ WMI `0x901f` |
| `5` | `0x05` | `HT_COMM_OP_POLL_REINIT_RESET` | Host $\rightarrow$ Target | `0x009b13ef` | `0x009b3de7` | `0 B` | Resets `ubnt_poll` state, calls `0x009ae640` / `0x009afcf4` |
| `6` | `0x06` | `HT_COMM_OP_TARGET_FRAME_STATS` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `16 B` | Packed at `0x009b308c` $\rightarrow$ WMI `0x901f` |
| `7` | `0x07` | `HT_COMM_OP_STA_ADD_ASSOC` | Host $\rightarrow$ Target | `0x009b13c0` | `0x009b4151` | `7 B` | 6B MAC + `u8`; resolves peer (`0x009b3b2c`), calls `0x009af644` (`peer+0x50`) |
| `8` | `0x08` | `HT_COMM_OP_STA_DEL_DISASSOC` | Host $\rightarrow$ Target | `0x009b13b7` | `0x009b4151` | `7 B` | 6B MAC + `u8`; calls `0x009b0240` |
| `9` | `0x09` | `HT_COMM_OP_TARGET_PEER_METRICS` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `74 B` | Packed at `0x009b3220` (6B MAC + 17x `u32` counters) $\rightarrow$ WMI `0x901f` |
| `10` | `0x0a` | `HT_COMM_OP_TIMING_SLOT_CFG` | Host $\rightarrow$ Target | `0x009b1370` | `0x009b40c0` | `11 B` | Writes `+0x34`, `+0x20`, `+0x19`, `+0x1a`, `+0x29`, calls `0x009ae6cc` |
| `12` | `0x0c` | `HT_COMM_OP_STA_QUOTA_WEIGHTS` | Host $\rightarrow$ Target | `0x009b1343` | `0x009b4021` | `20 B` | Updates `peer+0x50` TDMA fields `+0x28`, `+0x2c`, `+0x30`, `+0x25`, `+0x24` |
| `13` | `0x0d` | `HT_COMM_OP_TARGET_AIRTIME_REPORT` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `22+ B` | Packed at `0x009b3270` (per-peer `u16` airtime + 4x `u32`) |
| `14` | `0x0e` | `HT_COMM_OP_SET_SW_RETRY_AND_MODE` | Host $\rightarrow$ Target | `0x009b12e7` | `0x009b3de7` | `0 B` | Sets `g_dbg_max_sw_retry` (`0x0040d364`) to `41` (`mode==2`) or `10`, calls `0x009ad384` |
| `15` | `0x0f` | `HT_COMM_OP_TARGET_SYNC_REPORT_15` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `21 B` | Packed at `0x009b344c` (4x `u32` + 5x `u8`) |
| `16` | `0x10` | `HT_COMM_OP_TARGET_SYNC_REPORT_16` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `1 B` | Packed at `0x009b361d` (1x `u8`) |
| `17` | `0x11` | `HT_COMM_OP_TARGET_SYNC_REPORT_17` | Target $\rightarrow$ Host | `0x009b1100` | `0x009b3de7` | `8 B` | Packed at `0x009b35d7` (2x `u32`) |
| `18` | `0x12` | `HT_COMM_OP_AIRTIME_METRIC_CFG` | Host $\rightarrow$ Target | `0x009b12cc` | `0x009b4012` | `4 B` | Writes target `+0x24`, calls `0x009af42c` |
| `22` | `0x16` | `HT_COMM_OP_GPS_SYNC_FRAME_MODE` | Host $\rightarrow$ Target | `0x009b12a0` | `0x009b3deb` | `1 B` | Writes target `+0x1e` (`0`/`1`), calls `0x009add48` |
| `23` | `0x17` | `HT_COMM_OP_UL_DL_RATIO_CFG` | Host $\rightarrow$ Target | `0x009b1288` | `0x009b3f7f` | `9 B` | Writes target `+0x38`, `+0x3c`, `+0x28`, calls `0x009ade64` |
| `24` | `0x18` | `HT_COMM_OP_UL_DL_RATIO_SYNC` | Bidirectional | `0x009b1100` | `0x009b3f7f` | `9 B` | Unpacks/packs 2x `u32` + 1x `u8` |
| `25` | `0x19` | `HT_COMM_OP_ATPC_POWER_LIMITS` | Host $\rightarrow$ Target | `0x009b1213` | `0x009b3f5e` | `3 B` | Writes target `+0x1f`, `+0x2a`, `+0x40`, checks `0x0040d30c` |
| `26` | `0x1a` | `HT_COMM_OP_ATPC_FEEDBACK` | Bidirectional | `0x009b1100` | `0x009b3f5e` | `3 B` | 3x `u8` ATPC power control state |
| `27` | `0x1b` | `HT_COMM_OP_CHANNEL_BW_FREQ_SYNC` | Bidirectional | `0x009b1102` | `0x009b3ed1` | `13 B` | Updates target `+0x60`, `+0x64`, `+0x68`, `+0x6c` |
| `28` | `0x1c` | `HT_COMM_OP_FIXED_FRAME_DUR_CFG` | Bidirectional | `0x009b11ed` | `0x009b3ed1` | `13 B` | Writes `+0x1d`, `+0x30`, `+0x1c`, `+0x48`, calls `0x009b02c0` |
| `29` | `0x1d` | `HT_COMM_OP_EXT_SYNC_PARAMS` | Bidirectional | `0x009b1100` | `0x009b423c` | `13 B` | 3x `u32` + 1x `u8` sync parameters |
| `30` | `0x1e` | `HT_COMM_OP_STA_LATENCY_MODE` | Host $\rightarrow$ Target | `0x009b11d5` | `0x009b3eb0` | `7 B` | 6B MAC + `u8`; calls `0x009b0c28` on `peer+0x50` |
| `31` | `0x1f` | `HT_COMM_OP_BURST_THRESH_CFG` | Host $\rightarrow$ Target | `0x009b11c6` | `0x009b3ea1` | `5 B` | Writes target `+0x4c` (`u32`) and `+0x1b` (`u8`) |
| `32` | `0x20` | `HT_COMM_OP_CONTENTION_WIN_CFG` | Host $\rightarrow$ Target | `0x009b11bd` | `0x009b3e92` | `4 B` | Calls `0x009ad318` |
| `36` | `0x24` | `HT_COMM_OP_STA_TXOP_RATE_CAP` | Host $\rightarrow$ Target | `0x009b119b` | `0x009b3e3c` | `10 B` | 6B MAC + `u32`; calls `0x009afa7c` on `peer+0x50` |
| `40` | `0x28` | `HT_COMM_OP_MGMT_KEY_TABLE_SYNC` | Host $\rightarrow$ Target | `0x009b1132` | `0x009b3e0f` | `38 B` | Copies 36-byte key entry into target `+0x12d8 + idx*36` |
| `41` | `0x29` | `HT_COMM_OP_MGMT_KEY_INDEX_NOTIFY` | Bidirectional | `0x009b1100` | `0x009b3df4` | `2 B` | 2x `u8` key index notification |
| `45` | `0x2d` | `HT_COMM_OP_FF_SYNC_TOGGLE` | Bidirectional | `0x009b1123` | `0x009b3deb` | `1 B` | Writes target `+0x44` (`u8`), calls `0x009ade64` |
| `50` | `0x32` | `HT_COMM_OP_INTERFERENCE_IMMUNITY` | Host $\rightarrow$ Target | `0x009b1117` | `0x009b3deb` | `1 B` | Calls `0x009af484` |
