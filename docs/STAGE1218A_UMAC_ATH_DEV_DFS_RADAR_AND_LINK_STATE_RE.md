<!-- doc-head: Stage 1218A - umac.ko / ath_dev.ko DFS radar, NOL+CAC timer and netdev/link-state notification RE, static big-endian MIPS ELF only -->
# Stage 1218A - `umac.ko` / `ath_dev.ko` DFS Radar, NOL/CAC Timers and Link-State Notification

Offline static reverse engineering of two Linux 2.6.32.68 kernel modules from the airOS WA 8.7.25
rootfs. No radio was contacted, no live IP was touched, no firmware was written. Every number below
is reproduced from the bytes; the tool gates itself on the measured ground truth and exits non-zero
if any of it drifts.

| Item | Value |
| :--- | :--- |
| Tool | `tools/re/umac_ath_dev_dfs_radar_and_link_state_re_analyzer.py` |
| Receipt | `artifacts/verification/stage1218a_umac_ath_dev_dfs_radar_re.json` (300,755 B) |
| Provenance | `CONFIRMED_STATIC_BINARY` |
| Determinism | two consecutive runs byte-identical (`FEF976D1...`) |
| Scope | `static` - no execution, no SSH, no firmware write |

## 1. Endianness gate (fail closed)

Both objects are MIPS32 **big-endian** `ET_REL`. The tool asserts `EI_DATA == 2` (`ELFDATA2MSB`),
`EI_CLASS == 1`, `e_type == ET_REL` and `e_machine == EM_MIPS`, and exits with code 3 otherwise.
The assertion exists because a little-endian decode of these bytes produces plausible garbage, and
every offset in this document would then be fiction.

| Module | Bytes | SHA-256 | EI_DATA | Sections | Named syms | Defined | Undefined | Functions with extent |
| :--- | ---: | :--- | :---: | ---: | ---: | ---: | ---: | ---: |
| `umac.ko` | 2,356,432 | `660435ed9c50f1390945535a975565d7234543e01933644bf99dd9deca1b2cd6` | 2 | 31 | 4,749 | 4,518 | 231 | 1,975 |
| `ath_dev.ko` | 287,216 | `9328580821a806feb310dba8024fd59d520ef9d58f23b9f61f29133219adc76c` | 2 | 24 | 867 | 750 | 117 | 310 |

Token census, per module, in each literal match mode. The headline `tokens` value uses the mode the
ledger documents (radar exact, dfs case-insensitive, cac exact); both modes are emitted so either
number can be recomputed from the raw file.

| Module | radar (exact) | radar (ci) | dfs (exact) | dfs (ci, headline) | cac (exact) | cac (ci) |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `umac.ko` | 37 | 43 | 79 | 105 | 29 | 58 |
| `ath_dev.ko` | 1 | 1 | 26 | 30 | 11 | 11 |

## 2. `ubnt_radar_mode` - offset reproduced, section attribution corrected

The directive places `ubnt_radar_mode` at file offset 952628 **in `.modinfo`**. The offset is right;
the section is not. Section bounds settle it:

| Measurement | Value |
| :--- | :--- |
| First occurrence (file offset) | **952628** |
| Containing section | **`.rodata`** (spans file 894,400 .. 964,447) |
| Section-relative offset | 58228 |
| `.modinfo` starts at | file 1,070,688 (size 1304) |
| Other occurrences | `__ksymtab_strings`+666 (file 1,070,242), `.strtab`+10387 (file 1,906,047) |

So `.modinfo` is where the **parameter metadata** lives, not where that string sits. The parameter
metadata and the kernel binding, read separately:

| Field | Measured value |
| :--- | :--- |
| `parm=` entry | `parm=ubnt_radar_mode:AP behaviour upon STA radar detection` (file 1,071,028) |
| `parmtype=` entry | `parmtype=ubnt_radar_mode:uint` (file 1,071,088) |
| `__param` entry | `__param`+80, file 1,072,072 (20-byte stride on this build) |
| set / get ops | `param_set_uint` / `param_get_uint` |
| Backing object | `ubnt_radar_mode`, `STT_OBJECT`, size 4, section 27 (`.bss`), bss offset 113,800 |
| Permission word | `0644` (decimal 420), level 0, flags 0 |
| Exported | yes - `__ksymtab`+224, name string `__ksymtab_strings`+666, value section 27 |

So the knob is a writable-at-runtime `uint` bound to a 4-byte `.bss` object **and exported to other
modules**. Where it is read is less convenient than a name suggests: all four static reference sites
are

| Site | Section | Offset | Via |
| :--- | :--- | ---: | :--- |
| 1 | `.text.unlikely` | 80 | `R_MIPS_HI16` into `.bss` |
| 2 | `.text.unlikely` | 84 | `R_MIPS_LO16` into `.bss` |
| 3 | `__ksymtab` | 224 | `R_MIPS_32` pointer |
| 4 | `__param` | 96 | `R_MIPS_32` pointer |

There is **no reference inside `.text`**, and `.text.unlikely` carries no `STT_FUNC` symbol beyond its
own section symbol. The consumer is an unnamed cold-path region. Naming a function here would be
invention, so the receipt records `attribution: unnamed_text_region` and leaves the consumer UNKNOWN.

## 3. DFS radar surface in `umac.ko` (11 symbols)

Five regulatory pulse tables, each referenced exactly twice (`HI16`+`LO16`, one instruction pair)
from `ol_if_dfs_configure`, i.e. the offload DFS configuration path:

| Table | Size (B) | Installed by |
| :--- | ---: | :--- |
| `dfs_fcc_radars` | 504 | `ol_if_dfs_configure` |
| `dfs_etsi_radars_full` | 504 | `ol_if_dfs_configure` |
| `dfs_mkk4_radars` | 504 | `ol_if_dfs_configure` |
| `dfs_korea_radars` | 224 | `ol_if_dfs_configure` |
| `dfs_etsi_radars` | 112 | `ol_if_dfs_configure` |

Radar functions, `st_value` section-relative in `.text`, `reference_sites` counted across named
relocations, decoded `R_MIPS_26` jal targets and `R_MIPS_32` data pointers:

| Symbol | Offset | Size | Reference sites |
| :--- | ---: | ---: | ---: |
| `ieee80211_send_ubnt_action_radar` | 169,832 | 292 | 1 |
| `ieee80211_scan_entry_is_radar_detected_period` | 294,200 | 12 | 1 |
| `ieee80211_scan_entry_set_radar_detected_timestamp` | 294,212 | 12 | 0 |
| `ieee80211_unmark_radar` | 321,964 | 148 | 4 |
| `ieee80211_dfs_notify_radar` | 322,300 | 188 | **0** |

`ieee80211_dfs_notify_radar` has zero static reference edges: no named relocation, no decoded jal
target, no data pointer. It does itself call `mod_timer` and `del_timer`, so it is a live radar
notifier that nothing in this build statically reaches. Whether it is dead code or entered through a
runtime-computed pointer cannot be decided statically: `CONFIRMED_STATIC` for the absent edge,
`INFERRED` for the consequence.

## 4. NOL and CAC

| Bucket | Symbol | Offset | Size | Ref sites |
| :--- | :--- | ---: | ---: | ---: |
| NOL | `acs_dfs_nol_event_handler_arg` | 35,648 (`.bss`) | 4 | 8 |
| NOL | `acs_dfs_nol_event_handler` | 35,652 (`.bss`) | 4 | 9 |
| NOL | `ieee80211_dfs_nol_update` | 321,180 | 364 | 1 |
| CAC | `ieee80211_dfs_override_cac_timeout` | 319,972 | 112 | 1 |
| CAC | `ieee80211_dfs_get_override_cac_timeout` | 320,084 | 52 | 0 |
| CAC | `ieee80211_dfs_get_cac_timeout` (`ieee80211_get_cac_timeout`) | 320,136 | 60 | 3 |
| CAC | `ieee80211_dfs_cac_required` | 320,364 | 32 | 2 |
| CAC | `ieee80211_dfs_cac_start` | 320,396 | 8 | 2 |
| CAC | `ieee80211_dfs_cac_stop` | 320,404 | 164 | 6 |
| CAC | `ieee80211_dfs_cac_cancel` | 320,568 | 132 | 2 |
| CAC | `ieee80211_dfs_cac_finished` | 320,700 | 480 | 1 |
| CAC | `ieee80211_dfs_find_cac_chan` | 321,544 | 420 | 1 |
| CAC | `wlan_scan_cac_in_progress` | 281,956 | 20 | 2 |
| CAC | `ath_vap_dfs_cac` | 82,564 | 32 | 3 |

Timer relations are relocation edges, not name guesses (`mod_timer` 42 sites, `del_timer` 59,
`init_timer_key` 21 across `umac.ko`; 28 of the `del_timer` sites fall in unnamed regions):

| Primitive | DFS-relevant callers (CONFIRMED_STATIC) |
| :--- | :--- |
| `init_timer_key` | `ieee80211_dfs_attach` |
| `mod_timer` | `ieee80211_dfs_notify_radar`, `ieee80211_mark_dfs` |
| `del_timer` | `ieee80211_dfs_cac_stop`, `ieee80211_dfs_notify_radar`, `ieee80211_dfs_reset` |

The timer objects initialised by `ieee80211_dfs_attach` carry no `.symtab` name, so **which**
`timer_list` backs the CAC path stays UNKNOWN. Only the init/arm/cancel sites are claimed. Operator
attribute names recovered from `.rodata` (names only, no mode or semantics claimed from a string):
`cac_timeout`, `set_cactimeout`, `get_noltimeout`, `get_nolstate`, `no_wradar`, `get_no_wradar`.

## 5. `ath_dev.ko` does not detect radar

`ath_dev.ko` contains zero radar, zero NOL and zero CAC symbols. It contains exactly one `radar` byte
string, and that string argues the opposite of detection:

| String | Location | Referenced by |
| :--- | :--- | :--- |
| `%s: rs_phyer=0x%x not a radar error\n` | `.rodata.str1.4`+6040 | `ath_process_phyerr`, `.text`+54,792 |

What `ath_dev.ko` does own is the DFS **ops registration and prescan** surface: `ath_dfs_register`
(162,560), `ath_dfs_unregister` (162,572), `ath_dfs_prescan_register` (163,080),
`ath_dfs_prescan_unregister` (163,092), the objects `ath_dfs_ops`, `ath_dfs_prescan_ops`,
`ath_dfs_prescan_control`, `ath_ignoredfs_enable`, plus `ath_show_ignoredfs` / `ath_write_ignoredfs`
and the `athignoredfs` sysfs name. Its DFS strings are lifecycle text: `DFS prescan attach failed`,
`DFS prescan attached`, `ic_dfs_update_backoff`, `DFS_WAIT state`, `ath_dfs_clear_cac`.

Read that as a split, not a duplication: `umac.ko` holds the policy (pulse tables, NOL, CAC, channel
moves) and `ath_dev.ko` holds device-side registration and PHY-error plumbing. Split is `INFERRED`
for role, `CONFIRMED_STATIC` for the symbols behind it.

## 6. Netdev / link-state

`netdev_notifier_symbols` is empty in **both** modules, and neither module imports
`atomic_notifier_chain_register`, `blocking_notifier_chain_register` or `raw_notifier_chain_register`.
The link-state surface that does exist is direct calls:

| Symbol | Defined | Reference sites | Callers |
| :--- | :---: | ---: | :--- |
| `netif_carrier_on` | no (import) | 3 | `osif_ioctl_switch_vap` |
| `netif_carrier_off` | no (import) | 2 | `osif_ioctl_switch_vap` |
| `netif_rx` | no (import) | 3 | `osif_deliver_data`, `osif_deliver_data_ol`, `osif_receive_monitor_80211_base` |
| `register_netdev` | no (import) | 2 | `__ath_attach`, `__ol_ath_attach` |
| `unregister_netdev` | no (import) | 2 | `__ath_detach`, `__ol_ath_detach` |
| `register_netdevice` | no (import) | 1 | `osif_ioctl_create_vap` |
| `alloc_netdev_mq` | no (import) | 3 | `__ol_ath_attach`, `init_ahb`, `osif_ioctl_create_vap` |
| `ath_get_netif_settings` | yes (593,352) | 1 | via `net80211_ops` ops table |
| `mlme_get_linkrate` | yes (236,040) | 4 | `ieee80211_recv_mgmt`, `ieee80211_recv_beacon_sta`, `ieee80211_mlme_recv_assoc_response`, `wlan_get_linkrate` |

Carrier state is therefore toggled only from the VAP switch ioctl, not from a notifier callback. The
absence claim covers `.symtab` only; a notifier registered by a different module cannot be excluded.

## 7. String evidence method, and where it stops

`.rel.text` is `SHT_REL`, so string references carry **no** addend field. Two mechanisms are used and
both are byte-level: named `$LCn` symbols in `.rodata.str1.4` (2,410 of them here), and `HI16`/`LO16`
pairs whose addend is reconstructed from the instruction immediates (`value = symbol + (hi<<16 + lo)`).
A `HI16` run is paired only with the `LO16` that immediately follows in relocation order. Several DFS
strings resolve to unnamed `.text` regions no sized symbol covers, for example `_check_and_start_cac`
from 318,964 / 319,200 / 319,280 and the CAC-timer text from 318,696. Those carry
`attribution: unnamed_text_region`, the nearest preceding symbol and the gap - never a neighbour's name.

## 8. Grades

| Claim | Grade |
| :--- | :--- |
| Sizes, SHA-256, `EI_DATA`, token counts, offset 952628 | `CONFIRMED_STATIC` |
| Five radar tables installed by `ol_if_dfs_configure` | `CONFIRMED_STATIC` |
| `ubnt_radar_mode` is a 0644 `uint` param bound to a 4-byte `.bss` object and exported | `CONFIRMED_STATIC` |
| `ubnt_radar_mode` consumer is an unnamed `.text.unlikely` region | `CONFIRMED_STATIC` |
| `ieee80211_dfs_notify_radar` has no static reference edge | `CONFIRMED_STATIC` |
| `notify_radar` re-arms/cancels a timer when reporting radar | `INFERRED` |
| `ath_dev.ko` registers DFS ops but does not detect radar | `INFERRED` (role), `CONFIRMED_STATIC` (symbols) |
| Which `timer_list` backs CAC | `UNKNOWN` |

## 9. Gaps

1. Static only: nothing was executed, so no runtime timing, expiry or radar-trigger behaviour is claimed.
2. The CAC timer object is anonymous in `.symtab`; only init/arm/cancel call sites are reported.
3. `ieee80211_dfs_notify_radar`'s zero reference count cannot exclude a runtime-computed pointer.
4. Unnamed `.text` regions that emit radar/CAC strings are labelled as unnamed, not attributed.
5. Notifier absence is asserted over `.symtab` of these two modules only.
6. `ath_dfs_ops` is registered here; which module consumes it at runtime is not proven from here.
7. Token counts are literal byte substrings, not semantic knobs (79 vs 105 for `dfs` in `umac.ko`).
8. The 20-byte `__param` stride is measured from this build's relocation pattern, not from a header.
9. Permission words are recovered mode bits; a running system's exposure of them was not verified.
