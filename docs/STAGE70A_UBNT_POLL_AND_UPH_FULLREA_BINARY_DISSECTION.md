<!-- doc-head: STAGE70A_UBNT_POLL_AND_UPH_FULLREA_BINARY_DISSECTION.md preserved document content -->
<!-- /doc-head -->



# Stage 70A — `/fullrea` Binary Dissection of `ubnt_poll_host.ko` (`WA` `AR9342`) & `uph.ko` (`XC` `QCA9558`)

- **Task ID**: `T-S70A-UBNT-POLL-HOST-KO-AND-UPH-KO-FULLREA-DISSECTION`
- **Status**: **`CONFIRMED`** (`100%` Offline Binary Dissection + `ClosedLoopResearchReactor` + `memorymaster.db` Ingested)
- **Dissector Tool**: [`tools/re/dissect_stage70a_ubnt_poll_and_uph_ko.py`](../tools/re/dissect_stage70a_ubnt_poll_and_uph_ko.py)
- **JSON Receipt**: [`artifacts/autoresearch/stage70a_ubnt_poll_and_uph_fullrea_dissection_20261026.json`](../artifacts/autoresearch/stage70a_ubnt_poll_and_uph_fullrea_dissection_20261026.json)

---

## 1. Cross-Platform Binary Identity (`WA.v8.7.25` `AR9342` vs `XC.v8.7.25` `QCA9558`)

- **Claim (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` + `Linux` + `hardware`)**:
  - `WA.v8.7.25` [`ubnt_poll_host.ko`](../artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko) (`189,880` B, SHA256 `bfc3f499...`) and `XC.v8.7.25` [`ubnt_poll_host.ko`](../artifacts/firmware_re_xc_ltu/xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko) (`189,880` B, SHA256 `d327c4c8...`) have **100% byte-identical** `.rodata` (`26,048` B), `.rodata.str1.4` (`11,580` B), `.data` (`832` B), and `.bss` (`2,548` B).
  - Across all `101,072` bytes of `.text` (`154` functions), `WA` and `XC` differ at **only 5 instructions (`20` bytes)**:

| `.text` Offset | Function | `WA.v8.7.25` (`AR9342`) | `XC.v8.7.25` (`QCA9558`) | Subsystem & Physical Cause (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :--- |
| `0x00cac` | `on_rx_input_wrapper` (`hook_host_ops[4]`) | `8e2400c4` (`lw $a0, 0xc4($s1)`) | `8e2400c8` (`lw $a0, 0xc8($s1)`) | `Linux` `struct sk_buff` `skb->data` offset (`+0xc4` on `WA` vs `+0xc8` on `XC`) |
| `0x010c0` | `ubnt_poll_host_ht_comm_tx` | `8e0200c4` (`lw $v0, 0xc4($s0)`) | `8e0200c8` (`lw $v0, 0xc8($s0)`) | `Linux` `struct sk_buff` `skb->data` offset when building WMI `0x901f` `ht_comm` |
| `0x010f8` | `ubnt_poll_host_ht_comm_tx` | `8e1000c4` (`lw $s0, 0xc4($s0)`) | `8e1000c8` (`lw $s0, 0xc8($s0)`) | `Linux` `struct sk_buff` `skb->data` offset prior to `dev_queue_xmit` |
| `0x18ab0` | `ubnt_poll_host_io_init` | `2404000b` (`li $a0, 11`) | `24040014` (`li $a0, 20`) | `hardware` GPS reset GPIO pin (`GPIO 11` on `WA` vs `GPIO 20` on `XC`) |
| `0x18ac4` | `ubnt_poll_host_gps_reset` | `2404000b` (`li $a0, 11`) | `24040014` (`li $a0, 20`) | `hardware` GPS reset GPIO toggle (`GPIO 11` on `WA` vs `GPIO 20` on `XC`) |

---

## 2. Control-Plane Hierarchy (`/proc/sys/dev/ubnt_poll/*` vs `/proc/sys/dev/uph/*` vs `/proc/sys/dev/uph_wifi0/*`)

- **Claim (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` + `external controller` `/bin/ubntbox`)**:
  1. **Legacy `M5` (`XW`/`XM`) vs `AC` (`WA`/`XC`) Branch in `/bin/ubntbox` (`0x0041ed70` / `0x0041eda8`)**:
     - `ubntbox` executes `ext $v0, $s2, 0x15, 1` (`(radio_caps & 0x200000)` bit 21 = PCIe offload radio).
     - When bit 21 is `0` (`M5` direct-attach `ubnt_poll.ko`), `ubntbox` emits `/proc/sys/dev/ubnt_poll/mode` (`0x0041f780`) and `/proc/sys/dev/ubnt_poll/no_ack_rate` (`0x0041faa4` & `0x0042005c`: `echo "<0|1> <mcs>" > /proc/sys/dev/ubnt_poll/no_ack_rate`).
     - When bit 21 is `1` (`WA`/`XC` `QCA988x`), `ubntbox` loads `umac.ko` with `/sys/module/umac/parameters/{is_ubnt_ptp,tgdeb,is_ubnt_ff,ubnt_op_mode,ubnt_radar_mode}` (`0x0041ec1c..0x0041ecd0`), loads `ubnt_poll_host.ko`, registers `wifi0` via `/proc/sys/dev/uph/addradio` (`0x0041f858`: `<phy> <ptp> <compat> <flex_new> <11ax_compat>`), and writes per-radio sysctls to `/proc/sys/dev/uph_wifi0/*`.
  2. **Global `/proc/sys/dev/uph/` Sysctls (`.data+0x007c..0x02a0`)**:
     - `debug` (`0x001bbc` -> `.bss+0x008c`), `addradio` (`0x001c78` -> `ubnt_poll_host_radio_add` `0x005164`), `delradio` (`0x001be8` -> `ubnt_poll_host_radio_del` `0x0050ec`).
  3. **Per-Radio `/proc/sys/dev/uph_wifi0/` Sysctls (`.rodata+0x0528..0x091f`, `26` entries)**:
     - Registered in `ubnt_poll_host_register_sysctl` (`0x0053ac..0x00557c`): `21` integer sysctls share a single `.bss+0x09a8..0x09e7` (`int sysctl_vec[16]`, `maxlen=64` B) buffer dispatched by `0x002138`, while `5` string sysctls (`sta_Debug`, `sta_kick`, `ap_filter`, `sta_priority`, `tx_power_limit`) share `.bss+0x09e8..0x0a4b` (`char sysctl_str[100]`) dispatched by `0x0045f0`.
  4. **`umac.ko` <-> `ubnt_poll_host.ko` Hook Table (`hook_cb` `.bss+0x0000` & `hook_host_ops` `.data+0x0000..0x0068`)**:
     - `init_module` (`0x018be4`) calls `umac.ko` `ubnt_poll_host_Attach(&hook_host_ops)` to register `27` callbacks (`slot 0` `radio_set_data` `0x005580`, `slot 4` `on_rx_input` `0x000c60`, `slot 8` `on_sta_connect` `0x008134`, `slot 11..16` `on_beacon_tx/rx`, `on_assoc_req_tx/rx`, `on_assoc_resp_tx/rx`, `slot 18` `ht_comm_rx` `0x00ae84`, `slot 22` `is_ap_valid` `0x00a3a4`, `slot 26` `check_sta` `0x001860`).

---

## 3. How `allow_80211=1` + `op_mode=0` (`enable=0` / `ptp_xmit`) Bypass the airMAX TDMA Poller

- **Claim (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` + `QCA firmware` + `mac80211`)**:
  1. **`umac.ko` `ubnt_op_mode` (`.bss+0x01bc8c`) & Target Firmware Selection**:
     - Set by `/bin/ubntbox` (`0x0041ea7c` & `0x0041ec94`) to `0` (`master`/AP) or `1` (`managed`/STA).
     - In `umac.ko` `ol_transfer_bin_file` (`0x000bd6c4`, branch `0x000bd81c..0x000bd83c`), when `is_ubnt_ptp == 0`, `ubnt_op_mode == 0` loads `athwlan_AR9888v2_ptmp_ap_bin` and configures `ol_ath_service_ready_event` (`0x000a7b7c`) for `85` peers / `170` TIDs (Flex) or `60` peers / `120` TIDs (FF), whereas `ubnt_op_mode == 1` loads `athwlan_AR9888v2_ptmp_sta_bin` (`30` peers / `60` TIDs).
  2. **`/proc/sys/dev/uph_wifi0/enable` (`0x0024b0..0x002544`) & `ptp_xmit` (`0x003290..0x003314`)**:
     - `/bin/ubntbox` (`0x0041ed94..0x0041edc8`) sets `enable = (radio.1.veriwave == 0) ? radio.1.polling : 0` (`radio+0xc4`).
     - On VAP creation (`ubnt_poll_host_radio_set_data` `0x005824..0x005890`), if `is_ptp == 0`, it calls `ubnt_poll_host_set_ptmp_poll_info(uph_dev, enable)` (`0x007588`), storing `enable` at `uph_dev+0x08` and sending WMI `0x901f` `ht_comm` `msg_type=0x0d` with `msg[0x0c] = enable` (`0` = disable QCA988x TDMA poller). Writing `0` to `/proc/sys/dev/uph_wifi0/ptp_xmit` (`0x003290`) invokes `ubnt_poll_host_set_ptmp_poll_info(uph_dev, 0)` at runtime.
  3. **STA-Side 5-Gate Bypass (`allow_80211=1` + Normal-AP Fallback & `xc_8725_uph_patched.ko`)**:
     - **Gate 1 (`on_beacon_rx` `0x008afc`)**: Step `0` (`0x008b60`) deletes BSSID from `sta_list` (`uph_dev+0x10ec`) if `connected_ap == NULL`; Step `1` (`0x008b80`) only inserts BSSID into `sta_list` if Beacon carries an encrypted `00:27:22` `msg_type=1` IE with `(caps & 3) != 0`.
     - **Gate 2 (`/bin/wpad` `0x0043176c..0x00431780`)**: Checks `scan_res->airmax_ie` (`+0x68`) and `wpa_s->conf->allow_80211` (`+0x224`, parsed at `0x00446220`). Adding `allow_80211=1` in `/etc/wpasupplicant_WPA-PSK.conf` bypasses Gate 2.
     - **Gate 3 (`is_ap_valid` `0x00a3a4`, called by `umac.ko` `0x000450fc`)**: Returns `sta_list_find(uph_dev+0x10ec, bssid) != NULL` (`sltu $v0, $zero, $v0` at `0x00a3b8`). Bypassed by either Two-Stage Beacon IE Withdrawal or patching `0x00a3b8` to `24 02 00 01` (`li $v0, 1`, as in [`xc_8725_uph_patched.ko`](../artifacts/xc_8725_uph_patched.ko)).
     - **Gate 4 (`on_assoc_req_tx` `0x009234`, branch `0x0092bc`)**: When `sta_list_find == NULL`, calls `ubnt_poll_host_set_ignore_nav(0)` (restoring standard 802.11 CSMA/CA NAV), sends WMI `0x901f` `msg_type = (is_ptp ? 0x0c : 0x0d)` with `mode = 0` (`sw $zero, 0x3c($sp)` / `sb $zero, 0x3c($sp)` at `0x0092d4`/`0x0092ec`) to disable the QCA988x TDMA poller, logs `"Associating with normal AP"`, and omits the `00:27:22` `msg_type=2` IE.
     - **Gate 5 (`on_assoc_resp_rx` `0x009ff0` branch `0x00a05c` & `on_sta_connect` `0x008134` branch `0x0083e4`)**: When `sta_list_find == NULL`, sets `*(u8 *)(uph_dev + 8) = 0`, logs `"Associated with Normal AP"`, returns `0` (allow), and leaves `uph_dev->connected_ap` (`+0x10f0`) = `NULL` so the `2000 jiffies` (`20s`) missing-poll watchdog (`ubnt_poll_host_sta_bmiss_ind` `0x007800`) never fires.
  4. **AP-Side 4-Gate Bypass ([`xc_8725_uph_ap_patched.ko`](../artifacts/xc_8725_uph_ap_patched.ko))**:
     - Stock `airOS 8` AP (`uph_dev->mode == 1`) rejects non-airMAX STAs in `on_assoc_req_rx` (`0x009594`, requiring `00:27:22` `msg_type=2` IE) and `check_sta` (`0x001860`).
     - `xc_8725_uph_ap_patched.ko` patches 5 functions (`check_sta` `0x001860` -> `return 1`, `on_sta_connect` `0x008134` -> `return 1`, `on_assoc_req_rx` `0x009594` -> `return 1`, `is_ap_valid` `0x00a3b8` -> `return 1`, and `proto_insert_ie` `0x00b950` -> `return 0`), converting the `airOS 8` AP into a pure CSMA/CA 4-address WDS AP that accepts standard `mac80211` (`OpenWrt`) STAs directly.

---

## 4. Internal State Variables: `SyncFlex`/`fixed_frame`, `AtpcTarget`/`atpc`, `Timing`, & `no_ack_rate`/`noack_mode`/`ro`

### 4.1 `SyncFlex` & `fixed_frame` (`/proc/sys/dev/uph_wifi0/fixed_frame`, `.text+0x002e08..0x003288` & `0x00d75c..0x00da94`)
- **Claim (`CONFIRMED`, attributed to `proprietary airMAX/LTU module` + `external controller` `/bin/ubntbox`)**:
  - `/bin/ubntbox` (`0x0041e31c..0x0041e4a8`) maps `radio.1.polling_ff_dur` enum `{0=Auto (0 us), 1=FF_4ms (4000 us), 2=FF_8ms (8000 us), 3=FF_2ms (2000 us), 4=FF_5ms (5000 us), 5=FF_10ms (10000 us)}` and writes a **10-integer vector** (`vec[0..9]` at `.bss+0x09a8..0x09cc`):

| Vector Slot | Field Name | `radio_entry` Offset | `uph_dev` / `netconf` Offset | Exact Quantizer & Target WMI `0x901f` Effect (`CONFIRMED`) |
| :--- | :--- | :--- | :--- | :--- |
| `vec[0]` | `ff_frame_dur` | `u16 radio+0xd8` | `u16 uph_dev+0x10c` / `netconf+88` (`+0xf4`) | Quantized (`0x2e58..0x2f34`) to `{0, 2000, 4000, 5000, 8000, 10000}` us; sets `uph_dev+0x1e` bit 13 (`0x2000`). If `vec[9] != 0` and `vec[0] == 0`, `0x2f50` forces `10000` us. |
| `vec[1]` | `ff_dl_alloc` | `radio+0xd8` bits `9..15` | `uph_dev+0x10c` bits `9..15` / `netconf+90` (`+0xf6`) | Quantized (`0x2f84..0x2ffc`) to `{25, 33, 50, 67, 75}`%. In `init_ptmp_netconf` (`0xd764..0xd88c`), splits usable frame (`ff_frame_dur - gaps - cbp_slots*slot_dur`) into `down_dur` (`+0xa6`) and `up_dur` (`+0xa8`). |
| `vec[2]` | `ff_cbp_slots` | `radio+0xd8` bits `4..7` | `uph_dev+0x10c` bits `4..7` / `netconf+91` (`+0xf7`) | Clamped (`0x3004..0x3034`) to `3..10` Contention-Based Polling (CBP) slots. |
| `vec[3..4]` | `ff_dl/ul_ctrl_rate` | `u8 radio+0xdc..0xdd` | `u8 uph_dev+0x110..0x111` / `netconf+92..93` | Quantized (`0x3038..0x30dc`) to `{12 (0x0c), 18 (0x12), 24 (0x18), 36 (0x24)}`. |
| `vec[5..6]` | `ff_dl/ul_swr_count` | `u8 radio+0xde..0xdf` | `u8 uph_dev+0x112..0x113` / `netconf+94..95` | Clamped (`0x30e0..0x310c`) to `<= 40` (`0x28`) software retries. |
| `vec[7]` | `gps_sync_mode` | `radio+0xd8` bits `8,1,0` | `uph_dev+0x10c` -> `netconf.flags` (`+0xb0`) | Selects `netconf.flags` `0x4009` (non-GPS FF) vs `0x10009` (GPS bit 0) vs `0x20009` (GPS bit 1) at `0xd938..0xd980`. |
| `vec[8]` | `ctrl_rate_40` | `radio+0xd8` bits `2..3` | `uph_dev+0x10c` -> `netconf.flags \|= 0x80` | Clamped `<= 1`; on 40 MHz (`0xda10..0xda48`) sets `ff_unit_shift=5`, `hyb_bal_dl_avg_dur_thresh=2200`, `txuse_thresh=200`. |
| `vec[9]` | `ff_flex` (`SyncFlex`) | `u8 radio+0xe0` bit `7/6` | `u8 uph_dev+0x114` -> `netconf.flags` | Enables `SyncFlex` hybrid framing (`netconf.flags \|= 0x0002` at `0xd9c4` or `0x8000` at `0xd9ec`). |

### 4.2 `AtpcTarget` / `atpc`, `Timing` / `timing`, and `no_ack_rate` / `noack_mode` / `ro`
- **Claim (`CONFIRMED`, attributed to `proprietary airMAX/LTU module`)**:
  - **`/proc/sys/dev/uph_wifi0/atpc` (`0x00292c..0x002ac4` & `0x00dab8..0x00dae8`)**: 5-int vector `<enable> <target_rssi_dbm> <max_or_min_1> <min_or_max_2> <def_power_dbm>` stored in `radio+0xc0` bit 6 (`uph_dev+0x1e` bit 1 -> `netconf.flags |= 0x1000`), `radio+0xcf` (`uph_dev+0x105` -> `netconf+87` `uph_dev+0xf3`, default `-50` dBm), `radio+0xd1` (`uph_dev+0x106` -> `netconf+100`), `radio+0xd0` (`uph_dev+0x107` -> `netconf+101`), and `radio+0xd2` (`uph_dev+0x108` -> sent via `ubnt_poll_host_set_ptp_atpc_def_power` `0x007494` or `set_ptmp_sta_atpc` `0x00762c`).
  - **`/proc/sys/dev/uph_wifi0/timing` (`0x0021fc..0x002254` & `0x002548..0x0025e4`)**: 3-int vector `<down_dur_us> <up_dur_us> <burst_dur_us>` stored at `u16 radio+0xc6..0xca` (`uph_dev+0x18..0x1c`), immediately calling `ubnt_poll_host_set_ptp_poll_info` (`0x0074c8`, WMI `0x901f` `msg_type=0x0c`).
  - **`/proc/sys/dev/uph_wifi0/noack_mode` (`0x002850..0x0028c8`) & `/proc/sys/dev/uph_wifi0/ro` (`0x00276c..0x0027f4`)**:
    - `noack_mode` stores `u8 noack` at `radio+0xcc` (`uph_dev+0x1e` bit 15 `0x8000`) and switches WMI `0x901f` `msg_type=0x0c` `mode` between `1` (ACKed PtP) and `3` (No-ACK PtP).
    - `ro` (`rate_override`, replacing legacy M5 `/proc/sys/dev/ubnt_poll/no_ack_rate`) accepts a 9-int vector `<aid> <dl_mcs> <dl_nss> <dl_bw> <dl_sgi> <ul_mcs> <ul_nss> <ul_bw> <ul_sgi>` and calls `ubnt_poll_host_set_rate_override` (`0x00b2d4`, WMI `0x901f` `msg_type=0x1e`).

---

## 5. Hidden Bugs & Suboptimal Constants in `ubnt_poll_host.ko` (`UPH-BUG-01..08`)

| Bug ID | Severity & Status | `.text` / `.rodata` / `.bss` Offset | Root Cause & Hardware/Kernel Impact (`CONFIRMED`) |
| :--- | :--- | :--- | :--- |
| **`UPH-BUG-01`** | **CRITICAL** (`CONFIRMED`) | `.text+0x0000c..0x00c68` (`sb $zero, 0($zero)`) & `.text+0x07bd8..0x07c20` (`jal panic`) | 1) All 26 `hook_host_ops` wrappers execute `sb $zero, 0($zero)` (`a0 00 00 00`) if `hook_cb` is NULL. 2) Timer callback `0x07bd8` calls `panic("ubnt-poll-host: #8e511820")` (`0x07c18`) after `30` min (`1,800,000` ms = `0x001b7740`) if `uph_dev+0x288` is not refreshed (`xc_8725_uph_patched.ko` patches `0x07c08` `14 40 00 06` -> `10 00 00 06` to defuse). |
| **`UPH-BUG-02`** | **HIGH** (`CONFIRMED`) | `.text+0x01c78..0x01cf0` (`addradio`) & `.text+0x052ec..0x05300` (`radio_add`) | `ubnt_poll_host_sysctl_addradio` runs `sscanf(buf, "%s %d %d %d %d", sp+0x20, ...)` from a `100`-byte buffer (`.bss+0x0118`) into a `32`-byte stack buffer (`sp+0x20..0x3f`), overflowing `$s0/$s1/$ra` if token 1 > 31 B. |
| **`UPH-BUG-03`** | **MEDIUM** (`CONFIRMED`) | `.text+0x02fbc..0x02fe4` (`fixed_frame` `ff_dl_alloc` parser) | At `0x02fcc`, `slti $v1, $v1, 0x19` overwrites input register `$v1` with boolean `0`/`1`, and `0x02fe4` (`movz $v1, $a2, $v0` with `$a2=0x32`) forces `ff_dl_alloc` inputs `25..32%` to jump to **`50%` (`0x32`)** instead of `25%` (`0x19`)! |
| **`UPH-BUG-04`** | **MEDIUM** (`CONFIRMED`) | `.bss+0x09a8..0x09e7` & `.text+0x02258` / `0x0276c` (`ro`) | 1) All 21 integer sysctls share `.bss+0x09a8` (`FMX-DISC-11`), clobbering `ff_mcast_airtime_limit` unless written last. 2) `ro` write (`0x0276c`) sends WMI `msg_type=0x1e` (`0x0b2d4`) without updating `uph_dev+0x15e..0x166`, so reading `/proc/sys/dev/uph_wifi0/ro` always returns `0 0 0 0 0 0 0 0 0`. |
| **`UPH-BUG-05`** | **MEDIUM** (`CONFIRMED`) | `.text+0x02990..0x0299c` (`atpc`), `0x0dac8..0x0dae0`, & `ubntbox` `0x004217ac` | `atpc` readback (`0x02320`) treats `vec[2]` (`radio+0xd1`) as `min` and `vec[3]` (`radio+0xd0`) as `max`, while `init_ptmp_netconf` (`0x0dac8`) copies `vec[2]` to `netconf+100` (`max=30`) and `vec[3]` to `netconf+101` (`min=0`). |
| **`UPH-BUG-06`** | **LOW/MED** (`CONFIRMED`) | `.text+0x02884` (`noack_mode`) & `.text+0x02d18` (`daprot`) | Rejects runtime writes whenever `radio->uph_dev != NULL` (`lw $v0, 0xe4($s2); bnez $v0, reject`), even though `set_ptp_poll_info` (`0x074c8`) and `send_ptmp_netconf` (`0x0dc28`) support live WMI updates. |
| **`UPH-BUG-07`** | **MEDIUM** (`CONFIRMED`) | `.rodata+0x0b28..0x0e67` (`8` `ptmp_netconf` profiles) | All 8 default profiles initialize `cms_bias=0` (`+102`) and `voip_bias=0` (`+103`), disabling hidden-node retry suppression (`.rodata+0x0ea4`) and VoIP dynamic duration (`.rodata+0x0e68`) until `6/6` is written. |
| **`UPH-BUG-08`** | **MEDIUM** (`CONFIRMED`) | `/bin/ubntbox` `0x0041ef2c` & `.text+0x0323c` (`ff_mcast_airtime_limit`) | `ubntbox` defaults `polling_ff_mcast_airtime` to `10%` (`0x0a`) with `tx_queue_len=50`, causing multicast airtime bloat or tail-drop until `ff_mcast_airtime_limit=5` (written last) + `tx_queue_len=256` are applied. |
