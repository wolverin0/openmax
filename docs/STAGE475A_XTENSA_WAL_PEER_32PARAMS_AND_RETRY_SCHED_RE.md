<!-- doc-head: STAGE475A_XTENSA_WAL_PEER_32PARAMS_AND_RETRY_SCHED_RE.md preserved document content -->
<!-- /doc-head -->



# Stage 475A — `QCA988x` Xtensa `wal_peer` 32-Parameter Table & Rate/Retry Context Dissection

- **Claim Status**: `CONFIRMED` (100% static binary instruction disassembly across `WA.v8.7.25` and `XC.v8.7.25` `athwlan.bin` `SGMT` images; `live_devices_touched = False`).
- **Subsystem Attribution**: `QCA firmware` (`QCA988x` Xtensa `WAL` peer management & rate-control context pointers).
- **Generator & Receipt**:
  - [`dissect_stage475a_xtensa_wal_peer_32params_and_retry_sched_re.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tools/re/dissect_stage475a_xtensa_wal_peer_32params_and_retry_sched_re.py)
  - [`stage475a_xtensa_wal_peer_32params_and_retry_sched_re.json`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/artifacts/autoresearch/stage475a_xtensa_wal_peer_32params_and_retry_sched_re.json)
  - [`test_stage475a.py`](file:///G:/_OneDrive/OneDrive/Desktop/Py%20Apps/futuraMAX/tests/test_stage475a.py)

---

## 1. Executive Summary

Following Stage 471A's discovery of `wal_peer_set_param` (`0x0098c0c0`) and `wal_peer_get_param` (`0x0098c4c8`), Stage 475A dissects all **33 jump-table slots (`0..32`)** (`bgeui a10, 33, 0x0098c161`) in both the setter (`JT @ 0x0098c0eb`) and getter (`JT @ 0x0098c4e5`). Both functions are **100% byte-identical (`SHA-256` match)** between `WA.v8.7.25` and `XC.v8.7.25`.

Out of the 33 slots (`0..32`):
- **22 slots are active in `wal_peer_set_param`** (and **21 slots in `wal_peer_get_param`**, since Slot `0` is write-only pause/unpause).
- **11 slots (`5, 9, 14, 19..22, 29..32`)** are compiled no-ops (`j 0x0098c161` in `set_param`, returning `0` in `get_param`).
- **Slots `15, 16, 17` (`0x0f, 0x10, 0x11`)** directly read and write the three 32-bit per-peer rate-control and scheduler context pointers at **`peer + 0x44`**, **`peer + 0x48`**, and **`peer + 0x40`** (`s32i` / `l32i`), linking `wal_peer` to `_rate_find_rc` (`0x0099d1c0`), `_rate_Input_tx_status` (`0x0099dc64`), and `_tx_send_setup_ppdu_retry` (`0x009914bc`).

---

## 2. Reconstructed `wal_peer` Struct Layout in Xtensa DRAM

| Offset | Width | Field Name | Instruction Evidence & Bitfields |
| :--- | :--- | :--- | :--- |
| `0x00` (`0`) | `uint32_t` | `vdev_ptr` | Dereferenced in Slot `0` (`l32i.n a10, a5, 0` $\rightarrow$ `l32i.n a9, a10, 12`) to notify `wal_vdev` on peer unpause. |
| `0x08` (`8`) | `uint32_t` | `tid_list_head` | Dereferenced in Slot `25` (`l32i.n a2, a5, 8`) to walk per-peer TIDs (`next` at `+0x00`) and call `0x0098fb7c`. |
| `0x20` (`32`) | `uint32_t` | `peer_cap_flags` | Bit `0` (`0x1`): `AUTHORIZED` (Slot 27); Bit `1` (`0x2`): `QOS_CAPABLE` (Slot 23); Bit `2` (`0x4`): `HT_CAPABLE` (Slot 24); Bits `11..31` (`0xfffff800`): `PMF_MFP` (Slot 26). |
| `0x24` (`36`) | `uint32_t` | `peer_ps_and_rts_flags` | Byte `0` (`+36`): TID sleep state (Slot 18 get); Bits `8..9`: PS state machine (Slot 8); Bit `21` (`0x00200000`): `NON_AGG_RTS_ENABLE` (Slot 28). |
| `0x28` (`40`) | `uint16_t` | `uapsd_or_tid_mask16` | Checked in Slot `18` (`l16ui a11, a5, 40`) before calling `0x00997c14` / `0x00997a9c`. |
| `0x30` (`48`) | `uint32_t` | `peer_key_and_pause_word` | Bits `0..7` (`+48`): `KEY_TYPE` (Slot 2); Bits `24..25`: `USE_4ADDR` (Slot 7); Bit `26`: PS active (Slot 8); Bit `27`: `DEFAULT_KEY` (Slot 3); Bit `28`: `UAPSD_TRIGGER` (Slot 12); Bit `29`: `UAPSD_DELIVERY` (Slot 13); Bit `30` (`0x40000000`): `PAUSE_STATE` (Slot 0). |
| `0x31` (`49`) | `uint8_t` | `mcast_bcast_echo` | Read/written in Slot `1` (`s8i a4, a5, 49` / `l8ui a2, a2, 49`). |
| `0x32` (`50`) | `uint8_t` | `ampdu_factor` | Read/written in Slot `10` (`s8i a4, a5, 50` / `l8ui a2, a2, 50`). |
| `0x34` (`52`) | `uint16_t` | `assoc_or_tim_id` | Read/written in Slot `4` (`s16i a4, a5, 52` / `l16ui a2, a2, 52`). |
| `0x36` (`54`) | `uint16_t` | `max_sp_and_vht_flags16` | Read/written in Slot `6` (`s16i a4, a5, 54` / `l16ui a2, a2, 54`); Bit `14` (`0x4000`) controlled by Slot `25`. |
| `0x3a` (`58`) | `uint16_t` | `ampdu_density` | Read/written in Slot `11` (`s16i a4, a5, 58` / `l16ui a2, a2, 58`). |
| `0x40` (`64`) | `uint32_t` | `rc_sched_ctx_ptr0` | Read/written in Slot `17` (`s32i a4, a5, 64` / `l32i a2, a2, 64`) — primary per-peer rate-control context pointer. |
| `0x44` (`68`) | `uint32_t` | `rc_sched_ctx_ptr1` | Read/written in Slot `15` (`s32i a4, a5, 68` / `l32i a2, a2, 68`) — secondary rate/scheduler context pointer. |
| `0x48` (`72`) | `uint32_t` | `rc_sched_ctx_ptr2` | Read/written in Slot `16` (`s32i a4, a5, 72` / `l32i a2, a2, 72`) — tertiary airMAX/TDMA peer extension pointer. |

---

## 3. Complete 33-Slot (`0..32`) `wal_peer` Jump-Table Map

| Slot | Hex | Parameter Name | `set_param` VA | `get_param` VA | Struct Offset | Semantics |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `0` | `0x00` | `WAL_PEER_PARAM_PAUSE_STATE` | `0x0098c163` | `0x0098c548` | `0x30` bit 30 | Calls `0x0098cee0` (pause) / `0x0098ccf8` (unpause) |
| `1` | `0x01` | `WAL_PEER_PARAM_MCAST_BCAST_ECHO` | `0x0098c2e9` | `0x0098c5f0` | `0x31` (`u8`) | `s8i`/`l8ui` byte 49 |
| `2` | `0x02` | `WAL_PEER_PARAM_KEY_TYPE` | `0x0098c2e4` | `0x0098c5ea` | `0x30` (`u8`) | `s8i`/`l8ui` byte 48 |
| `3` | `0x03` | `WAL_PEER_PARAM_DEFAULT_KEY_FLAG` | `0x0098c2d8` | `0x0098c5e2` | `0x30` bit 27 | Mask `0xf7ffffff` / `0x08000000` |
| `4` | `0x04` | `WAL_PEER_PARAM_ASSOC_OR_PS_TIM_ID` | `0x0098c2d3` | `0x0098c5dc` | `0x34` (`u16`) | `s16i`/`l16ui` offset 52 |
| `5` | `0x05` | `WAL_PEER_PARAM_RESERVED_05` | `0x0098c161` | `0x0098c54f` | `none` | No-op |
| `6` | `0x06` | `WAL_PEER_PARAM_MAX_SP_OR_FLAGS16` | `0x0098c1d8` | `0x0098c5d6` | `0x36` (`u16`) | `s16i`/`l16ui` offset 54 |
| `7` | `0x07` | `WAL_PEER_PARAM_USE_4ADDR_MODE` | `0x0098c2c7` | `0x0098c5ce` | `0x30` bits 24..25 | 2-bit WDS 4-addr mode (`0xfcffffff`) |
| `8` | `0x08` | `WAL_PEER_PARAM_POWERSAVE_STATE_MACHINE` | `0x0098c237` | `0x0098c5c6` | `0x24` bits 8..9 | Updates `0x30` bit 26 & calls `0x0098caf0` |
| `9` | `0x09` | `WAL_PEER_PARAM_RESERVED_09` | `0x0098c161` | `0x0098c54f` | `none` | No-op |
| `10` | `0x0a` | `WAL_PEER_PARAM_AMPDU_FACTOR` | `0x0098c232` | `0x0098c5c0` | `0x32` (`u8`) | `s8i`/`l8ui` byte 50 (A-MPDU max len exp) |
| `11` | `0x0b` | `WAL_PEER_PARAM_AMPDU_DENSITY` | `0x0098c22d` | `0x0098c5ba` | `0x3a` (`u16`) | `s16i`/`l16ui` offset 58 (MPDU spacing) |
| `12` | `0x0c` | `WAL_PEER_PARAM_UAPSD_TRIGGER_CAP` | `0x0098c221` | `0x0098c553` | `0x30` bit 28 | Mask `0xefffffff` / `0x10000000` |
| `13` | `0x0d` | `WAL_PEER_PARAM_UAPSD_DELIVERY_CAP` | `0x0098c14e` | `0x0098c5b2` | `0x30` bit 29 | Mask `0xdfffffff` / `0x20000000` |
| `14` | `0x0e` | `WAL_PEER_PARAM_RESERVED_14` | `0x0098c161` | `0x0098c55a` | `none` | No-op |
| `15` | `0x0f` | `WAL_PEER_PARAM_RC_SCHED_CTX_44` | `0x0098c21c` | `0x0098c5ac` | `0x44` (`u32`) | `s32i`/`l32i` offset 68 (RC/sched ctx #2) |
| `16` | `0x10` | `WAL_PEER_PARAM_RC_SCHED_CTX_48` | `0x0098c217` | `0x0098c5a6` | `0x48` (`u32`) | `s32i`/`l32i` offset 72 (TDMA peer ext #3) |
| `17` | `0x11` | `WAL_PEER_PARAM_RC_SCHED_CTX_40` | `0x0098c212` | `0x0098c5a0` | `0x40` (`u32`) | `s32i`/`l32i` offset 64 (Primary RC ctx #1) |
| `18` | `0x12` | `WAL_PEER_PARAM_TID_PAUSE_OR_UAPSD_SP` | `0x0098c1fd` | `0x0098c55f` | `0x24` / `0x28` | Calls `0x00997c14` / `0x00997a9c` |
| `19..22` | `0x13..16` | `WAL_PEER_PARAM_RESERVED_19..22` | `0x0098c161` | `0x0098c59b` | `none` | No-op |
| `23` | `0x17` | `WAL_PEER_PARAM_QOS_CAPABLE` | `0x0098c1ed` | `0x0098c591` | `0x20` bit 1 | Mask `0xfffffffd` / `0x2` |
| `24` | `0x18` | `WAL_PEER_PARAM_HT_CAPABLE` | `0x0098c1dd` | `0x0098c587` | `0x20` bit 2 | Mask `0xfffffffb` / `0x4` |
| `25` | `0x19` | `WAL_PEER_PARAM_VHT_OR_TID_AGG_ENABLE` | `0x0098c1b6` | `0x0098c57e` | `0x36` bit 14 | Walks TID list `peer+0x08` (`0x0098fb7c`) |
| `26` | `0x1a` | `WAL_PEER_PARAM_PMF_MFP_CAPABLE` | `0x0098c1a5` | `0x0098c578` | `0x20` bits 11..31 | Mask `0x000007ff` / `0xfffff800` |
| `27` | `0x1b` | `WAL_PEER_PARAM_AUTHORIZED` | `0x0098c190` | `0x0098c56d` | `0x20` bit 0 | Mask `0xfffffffe` / `0x1` |
| `28` | `0x1c` | `WAL_PEER_PARAM_NON_AGG_RTS_ENABLE` | `0x0098c184` | `0x0098c565` | `0x24` bit 21 | Mask `0xffdfffff` / `0x00200000` |
| `29..32` | `0x1d..20` | `WAL_PEER_PARAM_RESERVED_29..32` | `0x0098c161` | `0x0098c59b` | `none` | No-op |
