<!-- doc-head: Stage 321A Master Dossier for QCA988x Xtensa Target Firmware (XC 3x3 vs WA 2x2), Rate Control, 32 Full Polling Hooks, and HT_COMM 36-Opcode State Machine (<220 lines) -->
Consolidates the binary reverse-engineering proofs of Stages 317A..320A across `XC.v8.7.25`, `WA.v8.7.25`, and `WA.v8.7.11` (`umac.ko` + `ubnt_poll_host.ko`).
All claims are 100% offline (`live_devices_touched = False`) and machine-verified in `tests/test_stage317a_to_322a_qca988x_xtensa_re.py`.
<!-- /doc-head -->

# Stage 321A — `QCA988x` Xtensa Target Firmware, Rate Control, 32 Full Polling Hooks & `HT_COMM` Master Dossier

## 1. Executive Summary & Artifact Routing (`CONFIRMED`)

| Stage | Scope | Production RE Tool | Machine-Checked JSON Receipt |
| :--- | :--- | :--- | :--- |
| **317A** | `XC` (`QCA9880` 3x3) vs `WA` (`QCA9882` 2x2) `SGMT` Target Firmware Audit | [`tools/re/xc_vs_wa_qca988x_target_firmware_audit.py`](../tools/re/xc_vs_wa_qca988x_target_firmware_audit.py) | [`artifacts/autoresearch/stage317a_xc_vs_wa_target_firmware_audit.json`](../artifacts/autoresearch/stage317a_xc_vs_wa_target_firmware_audit.json) |
| **318A** | `QCA988x` Xtensa Target Rate-Control (`rc_update_ht`, `rc_sib_update`, WMI & PER/EVM) | [`tools/re/qca988x_xtensa_rate_control_dissection.py`](../tools/re/qca988x_xtensa_rate_control_dissection.py) | [`artifacts/autoresearch/stage318a_qca988x_xtensa_rate_control_dissection.json`](../artifacts/autoresearch/stage318a_qca988x_xtensa_rate_control_dissection.json) |
| **319A** | `QCA988x` Target `Full Polling Hooks` (`32` Function Pointers) Dissection | [`tools/re/qca988x_target_full_polling_hooks_dissection.py`](../tools/re/qca988x_target_full_polling_hooks_dissection.py) | [`artifacts/autoresearch/stage319a_qca988x_target_full_polling_hooks_dissection.json`](../artifacts/autoresearch/stage319a_qca988x_target_full_polling_hooks_dissection.json) |
| **320A** | `ubnt_poll_host.ko` $\leftrightarrow$ `QCA988x` `HT_COMM` (`0x9065`) 36-Opcode State Machine | [`tools/re/ubnt_poll_ht_comm_state_machine_dissection.py`](../tools/re/ubnt_poll_ht_comm_state_machine_dissection.py) | [`artifacts/autoresearch/stage320a_ubnt_poll_ht_comm_state_machine_dissection.json`](../artifacts/autoresearch/stage320a_ubnt_poll_ht_comm_state_machine_dissection.json) |

---

## 2. Stage 317A — `XC` (`QCA9880` 3x3) vs `WA` (`QCA9882` 2x2) Target Firmware Comparative Dissection (`CONFIRMED`)

- **Host `umac.ko` Parity (`CONFIRMED`, attributed to `Linux` + `proprietary airMAX/LTU module`)**:
  - `.text` is `892,816 B` in both `XC.v8.7.25` (`QCA9558`) and `WA.v8.7.25` (`AR9342`). All `234` differing functions (`1,975` 32-bit words, of which `1,972` are exact `+4` immediate offsets) stem from a `+4 B` `struct sk_buff` field offset (`0xc8` on `XC` vs `0xc4` on `WA`).
  - `.data` differs by exactly `+2,336 B` (`747,632 - 745,296 B`), matching the sum of the 3 compressed `SGMT` firmware size deltas (`775 + 775 + 786 = 2,336 B`).
- **Target `SGMT` (`BCL-LZ77`) Segment Matrix (`CONFIRMED`, attributed to `QCA firmware` + `proprietary airMAX/LTU module`)**:
  - `otp_AR9888v2_bin`: Byte-for-byte identical across `XC.v8.7.25`, `WA.v8.7.25`, and `WA.v8.7.11` (`6,917 B` compressed, SHA-256 `c6f55649832e3b37...`).
  - `seg[0]` (`.lit4` at `0x00980000`, `LITBASE = 0x009bb000`): Identical size between `XC.v8.7.25` and `WA.v8.7.25` (`5,720 B` PtP, `6,328 B` PtMP AP, `6,060 B` PtMP STA).
  - `seg[1]` (`.rodata` at `0x0040b000`): `XC.v8.7.25` is `+36 B` larger (`7,420 vs 7,384 B` PtP, `8,636 vs 8,600 B` AP, `8,808 vs 8,772 B` STA), replacing `WA` 2x2 board CTL strings (`LAP-GPS`, `LBE-AC-23`, `Loco5AC`, `NBE-5AC-G2`, `NBE-AC-16`, `NBE-AC-16C`, `PBE-AC-300`, `PBE-AC-400`) with `XC` 3x3 / AirPrism board strings (`Low Power 1`, `Low Power 2`, `NBE-AC-19`, `PBE-AC-500`, `PBE-AC-500-ISO`, `PBE-AC-620`, `PBE-AC-620-ISO`, `RM5AC-PTMP`, `RM5AC-PTP`, `RM5ACL`).
  - `seg[2]` (`.data`): `XC.v8.7.25` is `+3,392 B` (`+0x0d40 B`) larger (`14,280 vs 10,888 B` PtP, `14,048 vs 10,656 B` AP, `13,708 vs 10,316 B` STA) to hold 3-chain `QCA9880` CTL/EIRP power tables, shifting `Initial Hooks` and `Full Polling Hooks` by `+0x0d60` (`+0x20` base + `+0x0d40` size):
    - `PtP`: `0x0040f608` / `0x0040f688` (`WA.v8.7.25`) $\rightarrow$ `0x00410368` / `0x004103e8` (`XC.v8.7.25`); `0x0040f4d4` / `0x0040f554` (`WA.v8.7.11`).
    - `PtMP AP`: `0x0040fac8` / `0x0040fb48` (`WA.v8.7.25`) $\rightarrow$ `0x00410828` / `0x004108a8` (`XC.v8.7.25`); `0x0040fa54` / `0x0040fad4` (`WA.v8.7.11`).
    - `PtMP STA`: `0x0040fb78` / `0x0040fbf8` (`WA.v8.7.25`) $\rightarrow$ `0x004108d8` / `0x00410958` (`XC.v8.7.25`); `0x0040fa44` / `0x0040fac4` (`WA.v8.7.11`).
  - `seg[3]` (`.text` at `0x00983c00`): `PtP` is `237,524 B` in both `XC` and `WA` (hook VAs shifted by `+4 B` in `XC`), while `PtMP AP` (`278,772 vs 278,756 B`) and `PtMP STA` (`259,268 vs 259,252 B`) are `+16 B` larger in `XC` for 3-stream (`NSS=3`) spatial-stream handling.

---

## 3. Stage 318A — `QCA988x` Xtensa Rate Control & Why OpenWrt `24.10.4` Avoids the "MCS Cliff" (`CONFIRMED`)

- **Target Rate-Control Globals & Vtables in `QCA988x` RAM (`CONFIRMED`, attributed to `QCA firmware` + `proprietary airMAX/LTU module`)**:
  - `g_rc_rate_max_per_thr` (`0x0040da7c`), `g_default_xretry_per_penalty` (`0x0040da78`), and `g_default_no_ack_wifi_thr` (`0x0040da14`), printed at `0x0040c8f8` and mutated via `HT_COMM` `opcode 1` (`SET_REG` `@ 0x009b9234`).
  - `g_rc_probe_period` (`0x0040d4e0`, initialized to `0x1388 = 5000` in `WMI_PEER_ASSOC_CMDID` `@ 0x0098a018`), `g_rc_probe_pkt_threshold` (`0x0040d4e4 = 32`), `g_rc_probe_enable` (`0x0040d4e8 = 1`), `g_dbg_max_sw_retry` (`0x0040d364`), and `g_dbg_vht_illegal_rate_err_cnt` (`0x00410b58`).
  - Rate-control vtables: `0x0040da20` (`rc_sib_update` at `+0x08` invoked at `0x0099bdd7`), `0x0040d898` (`20` xrefs), and `0x0040de28` (`13` xrefs).
- **WMI Parameter Dispatchers (`CONFIRMED`, attributed to `QCA firmware`)**:
  - `WMI_PDEV_SET_PARAM_CMDID` (`0x9006` `@ 0x00989170`, 54-slot JT `@ 0x0098918c`, `29` active params).
  - `WMI_VDEV_SET_PARAM_CMDID` (`0x901a` `@ 0x0099bb50`, 48-slot JT `@ 0x0099bb72` PtP / `0x0099bf0a` AP / `0x0099bf36` STA, `28` active params: `RTS_THRESHOLD=0x01`, `SLOT_TIME=0x0f`, `FORCE_RTS_CTS=0x13`, `CHWIDTH=0x19`, `FIXED_RATE=0x1a` calling `rc_sib_update` and `Slot 5` `0x009afd14`, `SGI=0x1e`, `VHT_SGIMASK=0x23`, `VHT80_RATEMASK=0x24`, `LDPC=0x2a`, `TX_STBC=0x2b`, `NSS=0x2e..0x2f`).
  - `WMI_PEER_ASSOC_CMDID` (`0x901e` `@ 0x00989f31`) & `wal_peer_set_param` (`0x0098c0c0`, 32-slot JT `@ 0x0098c0eb`, `32` active peer params `1..32`).
- **Root Cause of Stock `airOS 8` "MCS Cliff" vs OpenWrt `24.10.4` `ath10k` (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` vs `ath10k`)**:
  - In stock `airOS 8`, `ubnt_poll_host.ko` (`ubnt_poll_host_set_rate_override` `@ 0x0b2d4`, `ubnt_poll_host_set_reg` `@ 0x07f0c`) consumes target pilot `EVM` reports (`HT_COMM` `opcode 40` `@ 0x009b1132`), inflates `g_default_xretry_per_penalty` (`0x0040da78`), and pushes restricted 4-series rate tables via `HT_COMM` `opcode 10` (`0x009b6afc`), clamping links to `2x/4x` across multiple `5000 ms` probe windows.
  - In OpenWrt `24.10.4` `ath10k`, `ubnt_poll` is absent, `g_default_xretry_per_penalty` stays unpenalized, and `WMI_VDEV_SET_PARAM_CMDID` (`0x901a`) allows floor-bounded `VHT80_RATEMASK` (`0x24`), `SGI` (`0x1e`), `LDPC` (`0x2a`), and `RTS_THRESHOLD` (`0x01`).

---

## 4. Stage 319A — `QCA988x` Target `32 Full Polling Hooks` Table (`CONFIRMED`)

- **Registration & Switching (`CONFIRMED`, attributed to `proprietary airMAX/LTU module`)**:
  - `g_ubnt_active_hooks_ptr` (`0x00411aec`) is initialized to `Initial Hooks` (`0x0040f608`, `15/32` non-null slots `[0..11, 19, 23, 25]` in `v8.7.25`; `14/32` `[0..11, 23, 25]` in `v8.7.11`) by `ubnt_poll_ptp_init` (`0x009af28f`), and switched to `Full Polling Hooks` (`0x0040f688`, `32/32` non-null slots) by `platform_install_hooks` (`0x009af2f8`) when `HT_COMM` `opcode 13` (`0x009b1c80 @ 0x009b1d25`) enables TDMA.
  - At `0x00988fcc..0x00989006`, `&g_ubnt_active_hooks_ptr` (`0x00411aec`) and `g_ubnt_hooks_handle` (`0x00411af0`, 40-byte struct at `*0x00411b38`) are registered with the ROM WAL attach routine (`*0x0040d0e0`).

| Slot | `WA.v8.7.25` PtP VA | Initial (`v8.7.25`) | Hook Name & Target Role |
| :---: | :---: | :---: | :--- |
| `0` | `0x009afc94` | Yes | `on_pdev_init`: allocates 40-byte handle `*0x00411b38`, inits poll timers (`0x009addb8`), calls `ubnt_poll_ptp_init` |
| `1` | `0x009afcc0` | Yes | `on_pdev_post_init`: binds `WMI_UBNT_HT_COMM_CMDID` (`0x9065`) via `0x009ade5c` |
| `2..5` | `0x009afcc8..0x009afd14` | Yes | `on_vdev_set_mode`, `on_vdev_up_start` (`ubnt_poll_start`), `on_vdev_down_stop` (`ubnt_poll_stop`), `on_vdev_rate_update` |
| `6..9` | `0x009afd60..0x009afe14` | Yes | `on_mgmt_tx_intercept`, `on_pool_alloc_init`, `on_desc_pool_pop`, `on_desc_pool_push` (flag bit `0x02`) |
| `10..11` | `0x009afe34..0x009afe70` | Yes | `on_peer_create` (`0x009ad6a8`), `on_peer_delete` (`0x009ad914`) |
| `12..13` | `0x009aff58..0x009afeac` | No | `on_rx_frame_filter` (`0x009adaf8`), `on_rx_ppdu_status` (`0x009b57ec`) |
| `14` | `0x009b0d24` | No | `on_reserved_noop_14` (returns `0`) |
| `15..18` | `0x009b0004..0x009b00e8` | No | `on_tx_enqueue_sched` (`0x009b516c`), `on_tx_tid_classify`, `on_tx_ppdu_dur_limit` (`0x009b555c`), `on_tx_frame_filter` |
| `19` | `0x009b0174` | Yes (`8.7.25`) | `on_tx_ppdu_complete_early_guard` (`0x009b5954` arg `0`, added in `v8.7.25`) |
| `20..22` | `0x009b06a0..0x009b0724` | No | `on_tx_sched_slot_window_check` (`0x009b53e4`), `on_tx_ppdu_hw_setup` (`NOACK`), `on_tx_queue_pause_gate` (bit `0x04`) |
| `23..25` | `0x009b0cd4..0x009b0f54` | `23, 25` Yes | `on_tx_ppdu_complete_full` (`0x009b5954` arg `1`), `on_tx_drop_stat_inc` (`+0x24`), `on_tx_allow_check` (bit `0x10`) |
| `26..29` | `0x009b0d2c..0x009b0e7c` | No | `on_swbmiss_notify`, `on_bmiss_suppress_check`, `on_hw_reset_bottom_half`, `on_tx_alloc_fail_reason_stat` (`+0x10..+0x1c`) |
| `30..31` | `0x009b0f38..0x009b0f64` | No | `on_tsf_timestamp_read` (`0x009ae8dc`), `on_reserved_noop_31` (returns `0`) |

---

## 5. Stage 320A — `HT_COMM` (`WMI_UBNT_HT_COMM_CMDID = 0x9065`) 36-Opcode State Machine (`CONFIRMED`)

- **Bidirectional WMI Contract (`CONFIRMED`, attributed to `proprietary airMAX/LTU module`)**:
  - **Host $\rightarrow$ Target**: `ubnt_poll_host_ht_comm_prepare` (`0x0d204`) $\rightarrow$ `ubnt_poll_ht_comm_setup` (`0x14090`) $\rightarrow$ `wmi_unified_ubnt_ht_comm_send` (`0x057920`, `WMI_UBNT_HT_COMM_CMDID = 0x9065`) $\rightarrow$ target `0x009ade71` $\rightarrow$ wire unpacker `0x009b3c88` (`JT @ 0x009b3d21` PtP / `0x009b53c5` AP / `0x009b4d05` STA) $\rightarrow$ state-machine RX dispatcher `0x009b1024` (`JT @ 0x009b1067` PtP / `0x009b1e8b` AP / `0x009b1fb2` STA, `18` active RX opcodes).
  - **Target $\rightarrow$ Host**: `ubnt_poll_ht_comm_tx` (`0x009b43a0`) $\rightarrow$ wire packer `0x009b2f98` (`JT @ 0x009b3ba4` AP / `0x009b34e4` STA) $\rightarrow$ target event alloc `0x901f` (host `WMI_UBNT_HT_COMM_EVENTID = 0x902b`) $\rightarrow$ `ubnt_poll_ht_comm_parse` (`0x14894`) $\rightarrow$ `ubnt_poll_host_ht_comm_rx` (`0x0e67c`).
  - **36 Active Opcodes per Mode (`37` in union across `0..50`)**: `PtP` (`36` opcodes, includes `opcode 42` fast-retransmit, omits `opcode 14`), `PtMP AP` (`36` opcodes, includes `opcode 14` PtMP schedule map, omits `opcode 42`), and `PtMP STA` (`36` opcodes).
