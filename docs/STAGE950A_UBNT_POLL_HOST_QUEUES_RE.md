<!-- doc-head: Stage 950A - per-station queue census of ubnt_poll_host.ko (WA/XC 8.7.25), static only, refutes uph_Loaded and ath_TxQueue and shows the module holds no packet queue -->
# Stage 950A - `ubnt_poll_host.ko` per-station queue census

Question under test: how does the airOS TDMA slot scheduler in `ubnt_poll_host.ko` manage per-station
queues, and how does that compare with the mac80211 iTXQ model.

Short answer, stated up front and evidenced below: **it does not manage queues at all**. The module
programs frame geometry and per-station policy and emits WMI commands into the radio. It imports no
queue, skb or netif primitive, so it cannot hold or drain a frame. The slot-scheduler half of the
premise is CONFIRMED; the queue-management half is REFUTED.

- Provenance: `CONFIRMED_STATIC_BINARY`
- Radio safety: `static only`. No module loaded, no radio contacted, no device written.
- Receipt: `artifacts/autoresearch/stage950a_ubnt_poll_host_queues_re.json`
- Script: `tools/re/dissect_stage950a_ubnt_poll_host_queues_re.py`

## 1. Module identity

| Item | WA 8.7.25 | XC 8.7.25 |
| :--- | :--- | :--- |
| Path | `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko` | `.../xc_8725_rootfs/lib/modules/2.6.32.68/ubnt_poll_host.ko` |
| Bytes | 189880 | 189880 |
| SHA256 | `bfc3f499a086766917fcbbf1a52d0fac496ad237ae1671c4e640cccdd122c2b5` | `d327c4c8190b7c2299433695647583008867ff4d7588265cd6065c9233b8dab9` |
| Defined symbol names | 308 | 308 |
| Raw symtab entries | 407 | 407 |
| Undefined (imported) | 50 | 50 |

CONFIRMED: the two files are **not** byte-identical, so `modules_identical = 0`. They are, however,
the same code with a very small delta: exactly **7 differing bytes in 7 runs**, at offsets `0x0cef`,
`0x1103`, `0x113b`, `0x18af3`, `0x18b07`, `0x2369f`, `0x251c3`. The byte pairs are `0xc4 -> 0xc8`
three times, `0x0b -> 0x14` three times and `0x38 -> 0x40` twice. UNKNOWN: what those immediates and
string bytes encode; this stage did not disassemble around them.

The 407 to 308 gap is 99 duplicate names, all literal-pool labels of the form `$LC0`..`$LCn` that
repeat across compilation units. `symbols_total_*` counts unique defined names.

## 2. The two names the stage was handed

| Name | Occurrences in WA | Occurrences in XC | Modules in corpus containing it | Verdict |
| :--- | ---: | ---: | ---: | :--- |
| `uph_Loaded` | 0 | 0 | 0 of 105 with any disputed-token hit | **REFUTED** |
| `ath_TxQueue` | 0 | 0 | 0 | **REFUTED** |
| `tx_queue` | 0 | 0 | - | REFUTED |
| `TxQueue` | 0 | 0 | - | REFUTED |
| `requeue` | 0 | 0 | - | REFUTED |
| `tdma` / `tdd` | 0 | 0 | - | REFUTED |

`uph_Loaded` is absent with capitalisation variants `uph_Loaded` and `uph_loaded` both checked. This is
not a local absence: 1169 `.ko` files were swept and **no module anywhere in the corpus contains
either name**. Any downstream document that cites `uph_Loaded` or `ath_TxQueue` as module symbols is
citing something that does not exist in these artifacts.

## 3. Token census (raw byte occurrences, both modules summed)

| Metric | Value | Reading |
| :--- | ---: | :--- |
| `txqueue_token_hits` (`tx_queue`, `TxQueue`, `txq`) | 4 | only `ubnt_poll_host_set_txq_param` and `_get_txq_param` |
| `slot_token_hits` (`slot`, `Slot`, `SLOT`) | 8 | `cbp_dur_slot`, `ff_cbp_slots` and two printf strings |
| `tdma_token_hits` (`tdma`, `TDMA`, `tdd`, `TDD`) | 0 | the literal token is absent |
| `fair_queue_present` | 0 | no fair-queue vocabulary |
| `codel_present` | 0 | no CoDel vocabulary |
| `deficit_present` | 0 | no deficit or debt vocabulary |
| `poll` occurrences | 227 | the module is unambiguously the polling host |

Also measured as 0: `quantum`, `drr`, `wrr`, `round robin`, `fq_tin`, `fq_flow`, `aqm`, `admission`,
`may_transmit`, `tx_dequeue`, `flow`. CONFIRMED: there is no fair-queue, CoDel or deficit-round-robin
naming anywhere in the module. The only airtime vocabulary present is `ff_mcast_airtime_limit`, which
is a multicast cap and not a per-station accounting primitive.

## 4. Frame-geometry fields: 10 of 10 present

| Field | Hits (both modules) | Field | Hits |
| :--- | ---: | :--- | ---: |
| `ff_guard_units` | 4 | `atpc_target_rssi` | 4 |
| `ff_frame_dur` | 4 | `atpc_max_power` | 4 |
| `ff_dl_alloc` | 4 | `atpc_min_power` | 4 |
| `ff_cbp_s` | 4 | `sta_priority` | 6 |
| `ul_rate_ratio_thresh_nb` | 4 | `ul_per_thresh_nb` | 4 |

Each appears twice per module, consistent with one sysctl-table name plus one format string. Related
strings recovered alongside them: `cbp_dur_slot`, `ff_cbp_slots`,
`flags: %d, down_dur_min=%d, cfp_dur_min=%d, cbp_dur_slot=%d` and `ff_unit_shift`. CONFIRMED: the
module exposes duration, guard, allocation, slot-budget, ATPC and UL-threshold policy. It exposes no
rate, quantum or debt field.

## 5. The decisive measurement: the import table

A host-side queue manager must depend on a queue primitive. The module's 50 imports contain **zero**
matches from the probe set `skb_queue_tail`, `skb_queue_head`, `__skb_dequeue`, `skb_dequeue`,
`netif_tx_wake_queue`, `netif_stop_queue`, `netif_tx_stop_queue`, `dev_queue_xmit`, `kfree_skb`,
`alloc_skb`, `dev_kfree_skb`, `napi_gro_receive`. `queue_api_imports = 0`.

What it does import instead:

| Group | Symbols |
| :--- | :--- |
| WMI command path | `__wmi_unified_cmd_send`, `wmi_buf_alloc`, `wmi_unified_register_event_handler`, `wmi_unified_unregister_event_handler` |
| ieee80211 node ops | `ieee80211_find_node`, `ieee80211_free_node`, `ieee80211_indicate_node_assoc`, `ieee80211_kick_node`, `ieee80211_mlme_sta_bmiss_ind` |
| ath hooks | `ath_hook_host_register`, `ath_kickout_node_notify` |
| proc and sysctl | `proc_create_data`, `proc_dointvec`, `proc_dostring`, `proc_mkdir`, `register_sysctl_table` |
| vendor allocator | `amalloc_private`, `afree_private` |
| timers and GPIO | `add_timer`, `del_timer`, `mod_timer`, `init_timer_key`, `gpio_line_set`, `gpio_line_config` |

CONFIRMED: the module's data path is a control path. It moves policy into the radio over WMI and
bookkeeps stations through ieee80211 node operations. It never touches a frame. The only stack
symbols it imports are `memcpy`, `memset`, `memcmp`, `snprintf`, `sscanf`, `strlen` and friends.

## 6. Symbol census

143 of 308 defined names match `queue|slot|tdma|tdd|poll|tx|sta|sched`. The 40 shipped in the receipt
are prioritised so queue-shaped names come first; the full 143 are in
`modules[].matching_symbols`. The queue-shaped names are exactly two: `ubnt_poll_host_set_txq_param`
and `ubnt_poll_host_get_txq_param`. No defined symbol contains `slot`, `tdma`, `tdd`, `queue` or
`sched`. The remainder are `ubnt_poll_host_*` station, poll, scan and diagnostic entry points.

Additional measured string evidence: a station can be placed on a **deferred list**
(`STA %02X:... added to deferred list`, 2 occurrences), which is a station-state deferral and not a
frame requeue.

## 7. Answer to the question

`queue_model = "tdma_slot_scheduler"`, `manages_per_station_queues = 0`.

- CONFIRMED: the module is the poll host and it owns slot geometry, CBP slot budget, per-station
  priority, ATPC targets and UL admission thresholds.
- CONFIRMED: it owns no per-station frame queue, because it imports no queue primitive and carries no
  fair-queue, CoDel or deficit vocabulary.
- INFERRED: the geometry is time-division shaped rather than byte-fair shaped, because every field is
  a duration, guard, allocation or slot count, and none is a rate, quantum or debt. The inference rests
  on field semantics, since the literal token `tdma` is absent.
- UNKNOWN: which entity owns the per-station queue the radio drains. This stage bounds ownership to
  "not this module". `umac.ko`, `ath_dev.ko` and the AR9888v2 SGMT blobs are present in the corpus but
  were not measured here.

## 8. Boundary against the mac80211 iTXQ model

The mac80211 comparison baseline is present and was measured in the same run: 1011 unique defined
symbol names, with `ieee80211_tx_dequeue`, `ieee80211_txq_may_transmit` and
`ieee80211_txq_setup_flows` all defined, so `mac80211_itxq_present = 1` (3 of 3, consistent with the
8 of 8 recorded in stage 947A). mac80211 also imports and defines its own skb-queue primitives, which
is precisely what `ubnt_poll_host.ko` does not.

That asymmetry is the whole comparison: on the OpenWrt side the queue lives in the module under
inspection; on the airOS side the equivalent module holds no queue, so the two cannot be compared
symbol-for-symbol. The explicit two-column matrix, the shared-vocabulary count and the
non-comparable boundary are established in Stage 951A.

## 9. Claims ledger

| ID | Label | Claim |
| :--- | :--- | :--- |
| C1 | REFUTED | `uph_Loaded` is a symbol or string in `ubnt_poll_host.ko` |
| C2 | REFUTED | `ath_TxQueue` is a symbol or string in `ubnt_poll_host.ko` |
| C3 | REFUTED | the module manages per-station packet queues |
| C4 | CONFIRMED | the module is a slot and frame-geometry scheduler |
| C5 | CONFIRMED | WA and XC are distinct binaries, 7 bytes apart |
| C6 | CONFIRMED | the module hands work to the radio over WMI |
| C7 | CONFIRMED | no fair-queue, CoDel or deficit vocabulary exists in the module |
| C8 | CONFIRMED | mac80211 exports the three iTXQ entry points used for comparison |
| C9 | UNKNOWN | which entity owns the per-station queue the radio drains |
| C10 | INFERRED | the slot geometry encodes a time-division schedule, not a byte-fair share |
| C11 | UNKNOWN | what the 7 differing bytes encode |

## 10. Gaps

- Queue ownership is bounded to "not this module". `umac.ko`, `ath_dev.ko` and the SGMT firmware blobs
  were not measured in this stage, so no other module is named as the owner.
- No disassembly was performed. The arithmetic that converts per-station priority into a slot
  allocation is not recovered, and the 7-byte delta is not explained.
- Sysctl field names are confirmed; the programmed values are not read, because no target was queried.
- Version coverage is two 8.7.25 builds. Seven other `ubnt_poll_host.ko` copies exist in the corpus and
  were swept for the disputed names only, not fully censused.
- The stage identifier 950A is already used by `stage950a_mac80211_aql_txq_limit_re`, an unrelated
  mac80211 AQL stage. Consumers must key on the slug `ubnt_poll_host_queues_re`, not on the number.
