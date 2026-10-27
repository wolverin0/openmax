<!-- doc-head: STAGE12_UMAC_BEACON_IE_AND_AIRPRISM_CALLGRAPH_RE.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE12_UMAC_BEACON_IE_AND_AIRPRISM_CALLGRAPH_RE.md) | Part 1/2
<a id="5-xc-rocket-prism-5ac-gen2-ubnt_prism_hook--ath_devko-ath-spectral-filter-call-graph"></a> [5. `XC` (`Rocket Prism 5AC Gen2`) `ubnt_prism_hook` & `ath_dev.ko` `ath-spectral-filter` Call-Graph](STAGE12_UMAC_BEACON_IE_AND_AIRPRISM_CALLGRAPH_RE_CONTINUATION_139684a2de_002.md#5-xc-rocket-prism-5ac-gen2-ubnt_prism_hook--ath_devko-ath-spectral-filter-call-graph) | <a id="51-complete-channelbandwidth-transition-call-graph-confirmed"></a> [5.1 Complete Channel/Bandwidth Transition Call-Graph (`CONFIRMED`)](STAGE12_UMAC_BEACON_IE_AND_AIRPRISM_CALLGRAPH_RE_CONTINUATION_139684a2de_002.md#51-complete-channelbandwidth-transition-call-graph-confirmed) | <a id="52-ubnt_prism_filters-table-in-umacko-data--0x1510-264-bytes--6-times-44-bytes"></a> [5.2 `ubnt_prism_filters` Table in `umac.ko` (`.data + 0x1510`, `264` Bytes = `6` $\times$ `44` Bytes)](STAGE12_UMAC_BEACON_IE_AND_AIRPRISM_CALLGRAPH_RE_CONTINUATION_139684a2de_002.md#52-ubnt_prism_filters-table-in-umacko-data--0x1510-264-bytes--6-times-44-bytes) | <a id="53-architectural-separation-between-umacko-ubnt_prism_hook-and-ath_devko-ath_spectral_filter_-confirmed"></a> [5.3 Architectural Separation Between `umac.ko` `ubnt_prism_hook` and `ath_dev.ko` `ath_spectral_filter_*` (`CONFIRMED`)](STAGE12_UMAC_BEACON_IE_AND_AIRPRISM_CALLGRAPH_RE_CONTINUATION_139684a2de_002.md#53-architectural-separation-between-umacko-ubnt_prism_hook-and-ath_devko-ath_spectral_filter_-confirmed)

<!-- stage822a-payload-begin -->
# Stage 12 Deep Reverse Engineering: `umac.ko` Ubiquiti Vendor IE (`0x00156d` vs `0x002722`) State Machine & `ubnt_prism_hook` / `ath_dev.ko` Call-Graph (`WA.v8.7.25` & `XC.v8.7.25`)

- **Task ID**: `T-SUB-GEM3-03`
- **Date**: `2026-10-24`
- **Evidence Status**: **CONFIRMED** (100% offline binary ELF/relocation/symbol/control-flow extraction from `WA.v8.7.25` and `XC.v8.7.25` root filesystems)
- **Verification Script**: [`analysis/re_umac_and_airprism_callgraph.py`](../analysis/re_umac_and_airprism_callgraph.py)
- **Machine-Readable Receipt**: [`artifacts/firmware_re_xc_ltu/umac_vendor_ie_and_airprism_re_20261024.json`](../artifacts/firmware_re_xc_ltu/umac_vendor_ie_and_airprism_re_20261024.json)
- **Test Suite**: [`tests/test_re_umac_and_airprism_callgraph.py`](../tests/test_re_umac_and_airprism_callgraph.py)

---

## 1. Executive Summary & Binary Identity (`WA.v8.7.25` vs `XC.v8.7.25`)

We performed a complete static reverse-engineering pass across `umac.ko`, `ubnt_poll_host.ko`, `ath_dev.ko`, and `/bin/wpad` from both `WA.v8.7.25` (`LiteAP GPS` / `LiteBeam 5AC Gen2` / `NanoStation 5AC Loco`) and `XC.v8.7.25` (`Rocket Prism 5AC Gen2`):

| Binary / Module | `WA.v8.7.25` Size (B) | `XC.v8.7.25` Size (B) | Size Delta | Symbol & Section Layout | Root Cause of Any Binary Difference |
| :--- | ---: | ---: | ---: | :--- | :--- |
| `umac.ko` | `2,356,432` | `2,358,768` | `+2,336 B` | Identical section sizes for `.text` (`892,816 B`), `.rodata` (`70,048 B`), `.rodata.str1.4` (`104,704 B`), `.bss` (`115,568 B`), `__param` (`300 B`), and `4,766` symbols | Entire `+2,336 B` file size delta is in `.data` (`747,632` vs `745,296 B`) due to the 3 embedded QCA988x target firmware blobs (`athwlan_AR9888v2_ptmp_sta_bin` `+775 B`, `athwlan_AR9888v2_ptmp_ap_bin` `+786 B`, `athwlan_AR9888v2_ptp_bin` `+775 B`). |
| `ubnt_poll_host.ko` | `189,880` | `189,880` | `0 B` | Identical `.text` (`101,072 B`), `.rodata` (`26,048 B`), `.rodata.str1.4` (`11,580 B`), `.data` (`832 B`), `.bss` (`2,560 B`), and `469` symbols | Identical `.rodata`, `.rodata.str1.4`, `.data`, and `.bss`; minor relocation/build-path difference in `.text`/`.modinfo`. |
| `ath_dev.ko` | `287,216` | `287,216` | `0 B` | Identical `.text` (`180,160 B`), `.rodata` (`10,544 B`), `.rodata.str1.4` (`17,176 B`), `.data` (`1,024 B`), `.bss` (`208 B`), `__param` (`140 B`), and `880` symbols | Identical `.rodata`, `.rodata.str1.4`, `.data`, `.bss`, and `__param`. |
| `/bin/wpad` | `709,880` | `709,880` | `0 B` | **100% Byte-for-byte identical** (`SHA-256: 3359defe476bb4fc2104029cd4a90829cdb815e543e3fbe20e27d4e8adb6a281`) | Identical userspace supplicant/authenticator binary. |

---

## 2. Ubiquiti Vendor IE Architecture: OUI `00:15:6d` vs `00:27:22`

### 2.1 Definitive OUI Split Across the `airOS 8` Firmware (`CONFIRMED`)

1. **OUI `00:15:6d` (`\x00\x15\x6d`)**:
   - **Occurrences in `umac.ko`**: **`0`**
   - **Occurrences in `ubnt_poll_host.ko`**: **`0`**
   - **Occurrences in `/bin/wpad`**: **`0`**
   - **Occurrences across the rest of `wa_8725_rootfs`**:
     - `lib/modules/2.6.32.68/urd.ko`: `36` occurrences (regulatory country-code table entries)
     - `bin/athbox`: `36` occurrences (userspace regulatory country-code table entries)
     - `bin/lighttpd`: `1` occurrence
   - **Conclusion (`CONFIRMED`)**: In `airOS 8` (`WA.v8.7.25` / `XC.v8.7.25`), `00:15:6d` is **never** constructed, parsed, or recognized as a 802.11 management-frame Vendor IE by `umac.ko`, `ubnt_poll_host.ko`, or `/bin/wpad`. Injecting an unencrypted `dd ... 00156d ...` IE into OpenWrt `hostapd` Beacons has zero effect on an `airOS 8` AC STA's `airmax_ie` scan flag or `sta_list` admission gate.

2. **OUI `00:27:22` (`\x00\x27\x22`)**:
   - **In `ubnt_poll_host.ko` `.data + 0x2bc` (file offset `0x2316c`)**:
     - `.data + 0x2b0`: `ff:ff:ff` (`3`-byte airMAX AC Vendor IE sub-header following `00:27:22`)
     - `.data + 0x2b4`: `ff:ff:ff:ff:ff:ff` (`6`-byte broadcast MAC passed to `hmac_sha1` at `0xb320` as the recipient address for broadcast Beacons/ProbeResps)
     - `.data + 0x2bc`: `00:27:22` (`3`-byte Ubiquiti OUI checked via `memcmp(ie + 2, "\x00\x27\x22", 3)` in `ubnt_poll_host_proto_check_ie` at `0xbd9c`, `ubnt_poll_host_proto_parse_ie` at `0xbde4`, and written by `ubnt_poll_host_proto_insert_ie` at `0xb950`)
   - **In `umac.ko` `.text` (Native `00:27:22` CSA, airMAX IE Pre-Filter & Radar Action Handlers)**:
     - `ieee80211_parse_beacon` (`0x2ab10`):
       1. At `0x2b188..0x2b1b0`: loads 32-bit little-endian constant **`0x55222700`** (wire bytes `00:27:22:55`, **Ubiquiti Channel Switch Announcement Vendor IE**) and stores the IE pointer at **`scan_params + 0xf4`**.
       2. At `0x2b198..0x2b22c`: loads 32-bit little-endian constant **`0xff222700`** (wire bytes `00:27:22:ff`, **Ubiquiti airMAX AC Vendor IE**) and stores the IE pointer at **`scan_params + 0xf8`**, which is then passed to `hook_host_ops[13]` (`ubnt_poll_host_on_beacon_rx`, `step = 1` at `0x2af68`).
     - `ieee80211_add_ubnt_csa` (`0x27cc0..0x27d6c`, `172` bytes): writes the 13-byte (`len = 0x0b`) Ubiquiti CSA Vendor IE:
       `dd 0b 00 27 22 55 01 <mode:1> <chan:1> <tbtt_count:1> <sec_chan_offset:1> <bw:2>`
     - `ieee80211_send_ubnt_action_radar` (`0x29768..0x2988c`, `292` bytes): allocates a `14`-byte (`0x0e`) 802.11 Vendor Specific Action frame (`category = 0x7f`, OUI `00:27:22` at `0x297dc..0x297e8`) for DFS radar reporting.
   - **In `umac.ko` `.data`**: appears inside the 3 embedded QCA988x target firmware binaries (`0xcb7f`, `0x45c5d`, `0x82b87` in `WA`; `0xce85`, `0x4626f`, `0x834a2` in `XC`).

### 2.2 `ubnt_poll_host.ko` `00:27:22` Encrypted Vendor IE Wire Format (`msg_type = 1, 2, 3`)

All airMAX AC TDMA negotiation IEs in Beacon, Probe Response, Association Request, and Association Response frames are constructed and parsed by `ubnt_poll_host.ko`:

| Function Symbol | `.text` Offset | Size (B) | Role |
| :--- | :--- | ---: | :--- |
| `hmac_sha1` | `0xb320` | `272` | Computes `HMAC-SHA1` via `crypto_alloc_tfm("sha1", 0)`. Derives the 16-byte `AES-128-ECB` key as `HMAC-SHA1(key=DA_MAC6, data=SA_MAC6)[:16]` (where `DA_MAC6 = ff:ff:ff:ff:ff:ff` for Beacons/ProbeResps). |
| `ubnt_poll_host_proto_decrypt` | `0xb430` | `664` | Derives 16-byte key via `hmac_sha1` and decrypts 16-byte `AES-128-ECB` blocks via `crypto_alloc_base("aes", 0, 0)`. |
| `ubnt_poll_host_proto_encrypt` | `0xb6c8` | `616` | Derives 16-byte key via `hmac_sha1` and encrypts zero-padded 16-byte blocks with `AES-128-ECB`. |
| `ubnt_poll_host_proto_insert_ie` | `0xb950` | `1,100` | Constructs `0xdd` Vendor IE (`00:27:22` + `ff:ff:ff` + `msg_ver=2` + `msg_type=1/2/3` + `be16(enc_len)` + `ciphertext`). |
| `ubnt_poll_host_proto_check_ie` | `0xbd9c` | `72` | Fast validator: checks `ie[0] == 0xdd`, `ie[1] >= 0x1b` (`27` B), and `memcmp(ie + 2, "\x00\x27\x22", 3) == 0`. |
| `ubnt_poll_host_proto_parse_ie` | `0xbde4` | `1,572` | Full parser: checks `00:27:22` + `ff:ff:ff`, calls `ubnt_poll_host_proto_decrypt`, verifies `proto_ver == 9` and sender MAC, and unpacks `msg_type = 1`, `2`, or `3`. |

| `msg_type` | Frame Type | Outer Header (`12 B`) | Encrypted Plaintext Layout (`AES-128-ECB`, 16B Zero-Padded) |
| :---: | :--- | :--- | :--- |
| **`1`** | Beacon / Probe Response (`AP -> STA`) | `dd <len> 00 27 22 ff ff ff 02 01 <be16:enc_len>` | `be16(proto_ver=9)` + `bssid(6B)` + `mac(6B)` + `be32(caps)` (`0x01`=PtP, `0x02`=PtMP, `0x10`=airMAX AC, `0x20`=FF; `step=1` requires `(caps & 3) != 0`) + `be32(extra_caps)` + `TLV 1` (`hostname`) + `TLV 2` (`ssid`) |
| **`2`** | Association Request (`STA -> AP`) | `dd <len> 00 27 22 ff ff ff 02 02 <be16:enc_len>` | `be16(proto_ver=9)` + `sta_mac(6B)` + `tx_chainmask(1B)` + `rx_chainmask(1B)` + `caps(1B)` + `TLV 1` (`hostname`) + `TLV 3` (`fw_version`) |
| **`3`** | Association Response (`AP -> STA`) | `dd <len> 00 27 22 ff ff ff 02 03 <be16:enc_len>` | `be16(proto_ver=9)` + `ap_mac(6B)` + `tx_chainmask(1B)` + `rx_chainmask(1B)` + `be32(nonce)` + `rssi_feedback(2B)` + `TLV 3` (`fw_version`) + `ap_txpower(1B)` |

---

## 3. Complete 27-Slot `hook_host_ops` Dispatch Table (`ubnt_poll_host.ko` $\leftrightarrow$ `umac.ko`)

During `init_module` (`.init.text + 0x70`), `ubnt_poll_host.ko` calls `ath_hook_host_register(&hook_host_ops, &hook_cb)` in `umac.ko` (`0xd9f70`), which stores the pointer to `ubnt_poll_host.ko`'s `108`-byte (`27` $\times$ `4`-byte) `hook_host_ops` table (`.data + 0x00..0x68`) into `umac.ko` `.bss + 0x1c360` (`struct ath_hook_host_ops *hook_host_ops`). Every wrapper in `ubnt_poll_host.ko` `.text` (`0x00..0xea0`) checks `hook_cb != NULL` and loads the per-radio `struct uph_dev *handle` from **`*(struct uph_dev **)(ic + 0x1dedc)`** (`lui $v0, 2; lw -0x2124($v0)`).

Across `umac.ko` `.text`, there are **`54` `R_MIPS_LO16` references** to `hook_host_ops` (`1` pointer store in `ath_hook_host_register` at `0xd9f74` + `53` caller load sites):

| Slot | Byte Offset | Wrapper `.text` | Hook Name | Target Function(s) in `ubnt_poll_host.ko` | `umac.ko` Call Sites (`R_MIPS_LO16` offset & containing function) |
| ---: | :--- | :--- | :--- | :--- | :--- |
| **0** | `+0x00` | `0x0a10` | `attach_radio` | `ubnt_poll_host_data_create`, `ubnt_poll_host_radio_set_data`, `wmi_unified_register_event_handler`, `ubnt_poll_host_ht_comm_rx` | `0xae200` (`wmi_unified_vdev_set_param_send_or_static`) |
| **1** | `+0x04` | `0x0954` | `detach_radio` | `ubnt_poll_host_data_destory`, `wmi_unified_unregister_event_handler` | `0xad6d8` (`wmi_unified_vdev_delete_send_or_static`) |
| **2** | `+0x08` | `0x0000` | `alloc_node_init` | Inline: `*(ni + 0x23e8) = NULL` | `0x8b1c` (`ieee80211_alloc_node`) |
| **3** | `+0x0c` | `0x0914` | `free_node_cleanup` | `ubnt_poll_host_on_sta_destroy` | `0x6238` (`_ieee80211_free_node`) |
| **4** | `+0x10` | `0x00d8` | `on_rx_input` | Inline RX input check | `0x57818` (`ieee80211_input`) |
| **5** | `+0x14` | `0x08b4` | `should_add_ssid` | `ubnt_poll_host_assoc_req_tx_should_add_ssid` | `0x22234` (`ieee80211_mark_dfs_or_static`), `0x31ee8` (`ieee80211_send_assoc`), `0x3a9a0` (`ieee80211_send_proberesp`) |
| **6** | `+0x18` | `0x084c` | `on_probe_req_tx` | `ubnt_poll_host_on_probe_req_tx` | `0x28e34` (`ieee80211_send_probereq`) |
| **7** | `+0x1c` | `0x0808` | `on_beacon_tx` | `ubnt_poll_host_on_beacon_tx` | `0x228d4`, `0x228ec` (`ieee80211_mark_dfs_or_static` / beacon init/update), `0x3b048` (`ieee80211_send_proberesp`) |
| **8** | `+0x20` | `0x071c` | `on_assoc_req_tx` | `ubnt_poll_host_sta_list_find`, `ubnt_poll_host_set_ignore_nav`, `ubnt_poll_host_on_assoc_req_tx` | `0x324c4` (`ieee80211_send_assoc`) |
| **9** | `+0x24` | `0x06e4` | `on_assoc_resp_tx` | `ubnt_poll_host_on_assoc_resp_tx` | `0x2e7d0` (`ieee80211_setup_assocresp`) |
| **10** | `+0x28` | `0x05fc` | `on_deauth_tx` | `ubnt_poll_host_on_deauth_tx` | `0x2938c`, `0x293ac` (`ieee80211_send_deauth`), `0x2961c`, `0x2963c` (`ieee80211_send_disassoc_with_callback`) |
| **11** | `+0x2c` | `0x0564` | `on_auth_tx` | `ubnt_poll_host_sta_list_find`, `ubnt_poll_host_set_ignore_nav` | `0x29114` (`ieee80211_send_auth`) |
| **12** | `+0x30` | `0x0504` | `on_auth_rx` | `ubnt_poll_host_on_auth_rx` | `0x2c534` (`ieee80211_recv_mgmt`) |
| **13** | `+0x34` | `0x04a4` | `on_beacon_rx` | `ubnt_poll_host_on_beacon_rx` | `0x2ac80` (`step=0`), `0x2af68` (`step=1`), `0x2b308` (`step=2`) in `ieee80211_parse_beacon` |
| **14** | `+0x38` | `0x043c` | `on_assoc_req_rx` | `ubnt_poll_host_on_assoc_req_rx` | `0x2ebd4`, `0x2ecfc`, `0x2effc` (`ieee80211_recv_asreq`) |
| **15** | `+0x3c` | `0x03dc` | `on_assoc_resp_rx` | `ubnt_poll_host_on_assoc_resp_rx` | `0x38204`, `0x38344`, `0x38470` (`ieee80211_recv_asresp`) |
| **16** | `+0x40` | `0x0374` | `on_probe_req_rx` | `ubnt_poll_host_on_probe_req_rx` | `0x3b1e8`, `0x3b228`, `0x3b324` (`ieee80211_recv_probereq`) |
| **17** | `+0x44` | `0x0280` | `on_deauth_rx` | `ubnt_poll_host_on_deauth_rx` | `0x2c9dc`, `0x2cc00` (`ieee80211_recv_mgmt`) |
| **18** | `+0x48` | `0x0240` | `on_sta_disconnect` | `ubnt_poll_host_on_sta_disconnect` | `0x6ea0` (`ieee80211_sta_leave`), `0x34524`, `0x345a0` (`ieee80211_mlme_recv_deauth`), `0x346dc`, `0x34794` (`ieee80211_mlme_recv_disassoc`) |
| **19** | `+0x4c` | `0x0210` | `on_sta_connect` | `ubnt_poll_host_on_sta_connect` | `0x36c14` (`ieee80211_mlme_recv_assoc_request`), `0x3a0e0` (`ieee80211_mlme_recv_assoc_response`) |
| **20** | `+0x50` | `0x01bc` | `on_sta_authorize` | `ubnt_poll_host_on_sta_authorize` | `0x6934` (`ieee80211_node_authorize`), `0x69e0` (`ieee80211_node_unauthorize`) |
| **21** | `+0x54` | `0x0180` | `on_scan` | `ubnt_poll_host_on_scan` | `0x4200c`, `0x422d8` (`ieee80211_resmgr_attach_or_static`), `0x4406c` (`ieee80211_scan_run`) |
| **22** | `+0x58` | `0x0148` | `is_ap_valid` | `ubnt_poll_host_is_ap_valid` | `0x450fc` (`wlan_get_scan_requested_or_static` / `ieee80211_candidate_aplist_match_entry`) |
| **23** | `+0x5c` | `0x0c5c` | `ioctl_handler` | Inline ioctl dispatcher | `0x9e8f4`, `0x9e9b4` (`osif_receive_monitor_80211_or_static` / `osif_ioctl`) |
| **24** | `+0x60` | `0x00a4` | `set_dfs_backoff` | `ubnt_poll_host_set_dfs_backoff` | `0x21b04` (`ieee80211_dfs_update_backoff`), `0x21b84` (`ieee80211_dfs_set_backoff`) |
| **25** | `+0x64` | `0x002c` | `get_dfs_backoff` | Inline DFS backoff getter | `0x21bb0` (`ieee80211_dfs_get_backoff`) |
| **26** | `+0x68` | `0x0064` | `set_txpower` | `ubnt_poll_host_set_txpower` | `0x5170` (`wlan_set_txpow`) |

---

## 4. `umac.ko` Module Parameters, `ubnt_op_mode`, `ni_ubnt_poll`, and Step 1C Two-Stage IE Withdrawal

### 4.1 `umac.ko` `__param` Module Parameters & `ubnt_op_mode` Firmware Selection (`CONFIRMED`)

`umac.ko` exports `15` module parameters in `__param` (`300` bytes = `15` $\times$ `20` bytes), including:
- **`ubnt_op_mode`** (`.bss + 0x1bc8c`):
  1. **`ol_transfer_bin_file` (`0xbd6c4`)**:
     - Checks `is_ubnt_ptp` (`.data + 0x8b34`) at `0xbd81c`: if non-zero, loads `athwlan_AR9888v2_ptp_bin`.
     - Otherwise checks **`ubnt_op_mode`** at `0xbd83c`:
       - If **`ubnt_op_mode == 0`**, selects **`athwlan_AR9888v2_ptmp_ap_bin`** (`0xbd84c..0xbd860`), the AP / standard 802.11 CSMA/CA QCA988x target firmware.
       - If **`ubnt_op_mode != 0`** (`1` on a Stock PtMP CPE), branches to `0xbdbd0` and selects **`athwlan_AR9888v2_ptmp_sta_bin`**, the PtMP STA QCA988x target firmware.
  2. **`ol_ath_service_ready_event` (`0xa7940`)**:
     - Checks `ubnt_op_mode` at `0xa7b7c` to configure QCA988x target peer/TID resource pools:
       - `ubnt_op_mode == 0` & `is_ubnt_ff == 0` (Flexible AP): `85` peers, `170` TIDs, `340` keys/vdevs.
       - `ubnt_op_mode == 0` & `is_ubnt_ff != 0` (Fixed-Frame AP): `60` peers, `120` TIDs, `240` keys/vdevs.
       - `ubnt_op_mode != 0` (STA): `30` peers, `60` TIDs, `120` keys/vdevs.
- Other Ubiquiti parameters in `umac.ko`: `is_ubnt_ff` (`.bss + 0x1bc90`), `is_ubnt_ptp` (`.data + 0x8b34`), `host_80211_enable` (`.data + 0x8b38`), `ubnt_radar_mode` (`.bss + 0x1bc88`), `ubnt_ewma_ht_PLR` (`.data + 0x1c78`), and `ubnt_tx_SCALE` (`.data + 0x1c7c`).

### 4.2 `struct ieee80211_node` (`ni`) Ubiquiti Extensions (`CONFIRMED`)

| Field Purpose | `struct ieee80211_node` Offset | Writer / Initializer | Reader / Consumer |
| :--- | :--- | :--- | :--- |
| **`ni->ni_ubnt_poll`** (`struct uph_sta *`) | **`ni + 0x23e8`** | Initialized to `NULL` by `hook_host_ops[2]` (`0x00`) in `ieee80211_alloc_node` (`0x8b1c`); set to `uph_sta` pointer by `ubnt_poll_host_set_drv_sta_data` (`0x1140 + 0x28`); cleared by `ubnt_poll_host_clear_drv_sta_data` (`0x1184 + 0x28`). | Read by `ubnt_poll_host_get_drv_sta_data` (`0x116c + 0x0c`) and `hook_host_ops[3]` (`0x914`) in `_ieee80211_free_node` (`0x6238`). |
| **`ni->ni_ubnt_hostname`** (`char[64]`) | **`ni + 0x23a4..0x23e3`** | `ubnt_poll_host_set_node_hostname` (`0x1498`) | `wlan_node_gethostname` (`0x81dc` in `umac.ko`) |
| **`ni->ni_ubnt_rtt`** (`u32` distance/RTT) | **`ni + 0x2394` & `0x23a0`** | `ubnt_poll_host_set_node_rtt` (`0x1450`) and `wmi_unified_distance_report_handler` (`0xa6600..0xa6618` in `umac.ko`) | `wlan_node_getrtt` (`umac.ko`) |
| **A-MSDU Intolerant Flag** | **`ni + 0x9ac` (bit 3, `0x0008`)** | `ubnt_poll_host_set_node_amsdu_intolerant` (`0x16c4`) | `umac.ko` A-MSDU aggregation check |

### 4.3 The 5-Gate Stock `airOS 8` STA Association State Machine & Why Step 1C Works (`CONFIRMED`)

<!-- stage822a-payload-end -->
