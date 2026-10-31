<!-- doc-head: Stage 1086A dissects the 4-address, AP_VLAN and iTXQ transmit path inside the only .ko the panel cutover ships, mac80211.ko, resolving every hop by st_value, st_size, section and binding; CONFIRMED_STATIC_BINARY, offline, no radio contacted -->
# Stage 1086A - the 4-address, AP_VLAN and iTXQ transmit path in `mac80211.ko`

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline.
No module was loaded, no radio was contacted, no live IP was read, nothing was written to a device.

This is the stage that can actually be measured. Stage 1085A established that no ath10k binary
exists in the corpus, so this stage drops that premise entirely and dissects the module the panel
really ships. Every symbol below is resolved out of `.symtab` with `st_value`, `st_size`, section
and binding, so the TX path for `phy2-ap0.sta1` can be followed by symbol rather than by prose.

## Binary

| Field | Value | Label |
| :--- | :--- | :--- |
| path | `artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko` | CONFIRMED |
| bytes | 829464 | CONFIRMED |
| sha256 | `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416` | CONFIRMED |
| ELF class / endianness | ELF32, big-endian | CONFIRMED |
| e_type / machine | `ET_REL`, MIPS | CONFIRMED |
| sections | 32 | CONFIRMED |
| `.symtab` entries | 1974 total, 1631 with `st_shndx` not zero | CONFIRMED |
| unique defined symbol names | 1012 | CONFIRMED |
| exported (`__ksymtab_strings`) | 145 | CONFIRMED |
| `depends=` | `cfg80211,compat` | CONFIRMED |
| `vermagic` | `6.6.110 mod_unload MIPS32_R2 32BIT` | CONFIRMED |
| target interface | `phy2-ap0.sta1` | given |

Every symbol in the families below has binding `LOCAL` and section `.text`, which is the normal
shape for an `ET_REL` module built with hidden visibility. The exported surface is separate and
lives in `__ksymtab_strings`.

## The 4-address family

| Symbol | `st_value` | `st_size` | Binding | Section | Label |
| :--- | ---: | ---: | :--- | :--- | :--- |
| `ieee80211_send_4addr_nullfunc` | 400620 | 376 | LOCAL | `.text` | CONFIRMED |

The byte token `4addr` appears 2 times in the module. The token `four_addr` appears 0 times, so a
search for the spelled-out form would wrongly report the 4-address path as absent. `four_addr_token_hits`
is 2 in the receipt and refers to the `4addr` form.

`ieee80211_send_4addr_nullfunc` is the nullfunc sender a 4-address station must emit before data
frames can pass. Its presence is what makes the 4-address mode reachable at all. Label: CONFIRMED.

## The AP_VLAN family

| Symbol | `st_value` | `st_size` | Binding | Section | Label |
| :--- | ---: | ---: | :--- | :--- | :--- |
| `ieee80211_apvlan_link_clear` | 143496 | 88 | LOCAL | `.text` | CONFIRMED |
| `ieee80211_apvlan_link_setup` | 143584 | 256 | LOCAL | `.text` | CONFIRMED |
| `ieee80211_link_copy_chanctx_to_vlans` | 358904 | 8 | LOCAL | `.text` | CONFIRMED |
| `ieee80211_link_vlan_copy_chanctx` | 365928 | 92 | LOCAL | `.text` | CONFIRMED |
| `ieee80211_txq_remove_vlan` | 272420 | 260 | LOCAL | `.text` | CONFIRMED |

The symbols are spelled `apvlan` with no underscore. The literal `ap_vlan` has 0 byte hits in the
module, so a grep for the underscore form finds nothing while the AP_VLAN path is fully present.
`ieee80211_txq_remove_vlan` is the interesting one: teardown of a VLAN station goes through the
queue layer, which links the VLAN path to the iTXQ family directly.

## The WDS family is empty, and that is the result

| Symbol | Count | Label |
| :--- | ---: | :--- |
| symbols matching `wds` | 0 | CONFIRMED |
| lowercase token `wds` byte hits | 0 | CONFIRMED |
| uppercase token `WDS` byte hits | 1 | CONFIRMED |

There is no WDS symbol family in `mac80211.ko`. This is not a failed search: the same scan finds the
subif and queue entry points without difficulty. In this build the WDS function is carried by the
4-address and AP_VLAN helpers instead, and the `wds_*` entry points that do exist live in
`umac.ko` as `wmi_unified_node_add_wds_entry` and `wmi_unified_node_del_wds_entry`. Label:
CONFIRMED for the absence in mac80211, CONFIRMED for their presence in umac.

## The iTXQ family, 17 symbols

| Symbol | `st_value` | `st_size` | Label |
| :--- | ---: | ---: | :--- |
| `ieee80211_tx_dequeue` | 259764 | 3528 | CONFIRMED |
| `ieee80211_txq_may_transmit` | 247204 | 904 | CONFIRMED |
| `ieee80211_txq_setup_flows` | 273584 | 608 | CONFIRMED |
| `ieee80211_txq_schedule_start` | 243096 | 236 | CONFIRMED |
| `ieee80211_txq_teardown_flows` | 274192 | 164 | CONFIRMED |
| `ieee80211_txq_airtime_check` | 244348 | 176 | CONFIRMED |
| `ieee80211_txq_get_depth` | 304008 | 88 | CONFIRMED |
| `ieee80211_txq_set_params` | 273468 | 116 | CONFIRMED |
| `ieee80211_handle_wake_tx_queue` | 305940 | 168 | CONFIRMED |
| `__ieee80211_schedule_txq` | 252244 | 592 | CONFIRMED |
| `ieee80211_next_txq` | 249556 | 796 | CONFIRMED |
| `ieee80211_txq_init` | 272680 | 364 | CONFIRMED |
| `ieee80211_txq_purge` | 273044 | 424 | CONFIRMED |
| `ieee80211_txq_remove_vlan` | 272420 | 260 | CONFIRMED |
| `ieee80211_purge_sta_txqs` | 38892 | 92 | CONFIRMED |
| `ieee80211_fill_txq_stats` | 197056 | 264 | CONFIRMED |
| `ieee80211_wake_txqs` | 310160 | 68 | CONFIRMED |

Nine of nine expected iTXQ entry points are present. This corroborates Stage 947A, which measured
the same eight-symbol API as complete plus `ieee80211_txq_schedule_start` as an extra.

## The push side

| Symbol | `st_value` | `st_size` | Label |
| :--- | ---: | ---: | :--- |
| `ieee80211_subif_start_xmit` | 285564 | 1228 | CONFIRMED |
| `__ieee80211_subif_start_xmit` | 284364 | 1200 | CONFIRMED |
| `ieee80211_subif_start_xmit_8023` | 286792 | 1336 | CONFIRMED |
| `ieee80211_monitor_start_xmit` | 280184 | 808 | CONFIRMED |

`ieee80211_subif_start_xmit` is the `ndo_start_xmit` handler. It is the top of the path.

## Following `phy2-ap0.sta1`

| Hop | Symbol | Present | Role | Label |
| ---: | :--- | ---: | :--- | :--- |
| 1 | `ieee80211_subif_start_xmit` | 1 | netdev `ndo_start_xmit` entry for the AP VLAN interface | CONFIRMED |
| 2 | `__ieee80211_subif_start_xmit` | 1 | 4-address handling and queue selection | CONFIRMED |
| 3 | `ieee80211_send_4addr_nullfunc` | 1 | 4-address nullfunc, required before data frames pass | CONFIRMED |
| 4 | `ieee80211_txq_may_transmit` | 1 | airtime and deficit gate for the station AC | CONFIRMED |
| 5 | `ieee80211_tx_dequeue` | 1 | driver pull of the next frame from the station TID queue | CONFIRMED |
| 6 | `ieee80211_txq_enqueue` | 0 | push side of the TID queue | INFERRED |

Five of six hops are addressable by a defined symbol. The sixth is not, and is not claimed to be.

## Why `txq_enqueue` is absent but not refuted

`ieee80211_txq_enqueue` has no symbol. In the source tree it is a file-static helper, and in an
optimised object an inlined file-static helper leaves no `.symtab` entry. The absence therefore
grades INFERRED: the push side is reached inside the `__ieee80211_subif_start_xmit` body rather
than through a callable symbol. Reporting this as REFUTED or as a gap would overstate what a symbol
table can say. The receipt records `txq_enqueue_present: 0` and `enqueue_grade: "INFERRED"`.

## Claims

| ID | Label | Claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | `mac80211.ko` present, 829464 B, 1974 `.symtab` entries, 1012 unique defined names |
| C2 | CONFIRMED | 4-address path present as `ieee80211_send_4addr_nullfunc` at 400620, 376 B |
| C3 | CONFIRMED | AP_VLAN path present, and VLAN teardown runs through `ieee80211_txq_remove_vlan` |
| C4 | CONFIRMED | `wds` is not a symbol family in `mac80211.ko`; the WDS entries live in `umac.ko` |
| C5 | CONFIRMED | iTXQ layer complete, 9 of 9 expected entry points, `tx_dequeue` 3528 B |
| C6 | CONFIRMED | push side present as `ieee80211_subif_start_xmit` and its internal sibling |
| C7 | INFERRED | `ieee80211_txq_enqueue` was inlined, so hop 6 has no callable symbol |
| C8 | REFUTED | the premise that this module carries an ath10k peer phymode or VHT-NSS offset |
| C9 | UNKNOWN | the concrete queue index and AC mapping `phy2-ap0.sta1` gets at runtime |

Evidence grade for the stage as a whole: `CONFIRMED`, because every hop above except the inlined
one rests on a parsed symbol table with explicit size.

## Gaps

- no disassembly: hops are resolved by symbol presence and address, and call edges are not proven
- `ieee80211_txq_enqueue` is absent as a symbol, so hop 6 is an inference from source shape
- AP_VLAN runtime linkage for `phy2-ap0.sta1` is not established; the symbols exist, but which vif
  is an AP_VLAN vif on the running panel was not measured
- the 4-address decision depends on the runtime 4addr vif flag, which is a runtime fact
- `4addr` token hits are not tied to a specific function body without relocation addend decoding
- the corpus sweep counts which modules carry the xmit and dequeue entry points but does not
  compare their bodies
- no dynamic validation: nothing was loaded and no radio was contacted

## Reproduce

```
python tools/re/dissect_stage1086a_mac80211_4addr_wds_itxq_re.py
```

Receipt: `artifacts/autoresearch/stage1086a_mac80211_4addr_wds_itxq_re.json`.
Two consecutive runs are byte-identical; the receipt parses under `ConvertFrom-Json`.
