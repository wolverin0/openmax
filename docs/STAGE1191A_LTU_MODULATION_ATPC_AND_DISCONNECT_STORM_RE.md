<!-- doc-head: Stage 1191A LTU ame_core modulation, ATPC and disconnect-storm static RE scoped to 2.4.2 only; 100% offline -->

# Stage 1191A - LTU modulation, ATPC and disconnect storm

`evidence_provenance_class`: `CONFIRMED_STATIC_BINARY`. `radio_safety`: `static only`.
No target was contacted, no firmware was written.

## 1. Two premises, both refuted, reported not worked around

| Premise | Measured | Verdict |
| :--- | :--- | :--- |
| `eab_driver.ko` exists | 0 loose, 0 tar members, 141 archives / 209121 members scanned | `REFUTED` |
| `LTU 2.3.1` exists | 0 filename hits, 0 tar members | `REFUTED` |

Both counts are zero. `eab_driver.ko` is therefore described nowhere in this document:
with no bytes to read, any sentence about its internals would be invention. The same
applies to 2.3.1, so the stage is re-scoped to the only version present, 2.4.2, and every
result below belongs to 2.4.2.

## 2. What is actually present

| Version tree |
| :--- |
| `artifacts/firmware_re_xc_ltu/ltu_extracted/afltu_2.4.2` |
| `artifacts/firmware_re_xc_ltu/ltu_extracted/aflturocket_2.4.2` |

5 distinct module binaries were analysed, one per distinct SHA-256,
drawn from `ame_core.ko`, `ame_dev.ko` and `ame_radio_mod.ko`.

| Module | Bytes | SHA-256 |
| :--- | :--- | :--- |
| `ame_core.ko` | 3282052 | `fe5d489ea66bd2f32d6844d4ebefc4a1` |
| `ame_dev.ko` | 298760 | `912a7c1923aad381ac38ae922b78f698` |
| `ame_radio_mod.ko` | 578424 | `4aeac9b76454446ea8a05cc7cac886ea` |
| `ame_core.ko` | 3318764 | `a8d58e8d6a0c0665da361b6c188f8d26` |
| `ame_radio_mod.ko` | 578528 | `f36b837822fcefcc7a7db5957c9f5539` |

## 3. ATPC is spelled autopwr, and atpc is absent

`atpc_name_hits`: **0**. `autopwr` symbols recovered: **38**.

Stage 834A established this; it was re-measured here rather than inherited. The names are
recovered with offsets so they can be checked independently:

| Symbol | Offset | Size | Type |
| :--- | :--- | :--- | :--- |
| `autoMCS_rate_mapping_autoPwr_idx` | `0x159c00` | 124 | STT_FUNC |
| `ame_core_set_autopwr_remote_sysid` | `0x24a14` | 84 | STT_FUNC |
| `auto_pwr_update_mcs_history` | `0x24a68` | 236 | STT_FUNC |
| `auto_pwr_restore` | `0x24b54` | 100 | STT_FUNC |
| `auto_pwr_set_r_txoffset` | `0x24bb8` | 16 | STT_FUNC |
| `auto_pwr_get_l_txoffset` | `0x24bc8` | 40 | STT_FUNC |
| `autopwr_reset` | `0x24bf0` | 388 | STT_FUNC |
| `auto_pwr_decision` | `0x24d74` | 5636 | STT_FUNC |
| `autopwr_init` | `0x26378` | 92 | STT_FUNC |
| `autopwr_pwr_recfg_indicate` | `0x263d4` | 20 | STT_FUNC |
| `ame_core_get_autopwr_exp_txpwr` | `0x263e8` | 116 | STT_FUNC |
| `ame_core_get_autopwr_enable` | `0x2645c` | 24 | STT_FUNC |
| `ame_core_set_autopwr_enable` | `0x26474` | 36 | STT_FUNC |
| `ame_core_get_autopwr_info` | `0x26498` | 108 | STT_FUNC |
| `autopwr_dump_info` | `0x26504` | 908 | STT_FUNC |
| `ptmp_cpe_autopwr_check_txpwr` | `0x2a250` | 120 | STT_FUNC |
| `ptmp_cpe_autopwr_routine` | `0x2a2c8` | 48 | STT_FUNC |
| `ptmp_autopwr_get_dl_dgain_enable` | `0x36d30` | 16 | STT_FUNC |
| `ptmp_autopwr_set_dl_dgain_enable` | `0x36d40` | 212 | STT_FUNC |
| `ptmp_autopwr_get_dl_dgain_enable_cur` | `0x36e14` | 72 | STT_FUNC |
| `ptmp_autopwr_set_dl_dgain_enable_cur` | `0x36e5c` | 52 | STT_FUNC |
| `ptmp_cpe_autopwr_dump_info` | `0x370bc` | 296 | STT_FUNC |

38 symbols in total; the first 22 are shown. The decision core is `auto_pwr_decision` (5636 bytes) and the sampled-history path is
`auto_pwr_update_mcs_history`, which is the first hard link between the power loop and the
modulation decision.

## 4. Modem vocabulary that the directive asks about, and does not exist

| Token | Hits in `ame_core.ko` | Consequence |
| :--- | :--- | :--- |
| `atpc` | 0 | no named mechanism |
| `target_evm` | 0 | no named mechanism |
| `hyster` | 0 | no named mechanism |
| `downshift` | 0 | no named mechanism |
| `upshift` | 0 | no named mechanism |
| `disconnect` | 0 | no named mechanism |
| `deauth` | 0 | no named mechanism |
| `aging` | 0 | no named mechanism |
| `storm` | 0 | no named mechanism |

`target_evm` and `hyster` are zero, which independently reproduces Stage 834A and
Stage 876A. There is no symbol called `downshift` or `upshift` either, so the 4x/6x sticky
lock has to be explained by the threshold pairs rather than by a named function.

## 5. Modulation downshift is a cheap-down expensive-up threshold pair

`downshift_evidence`: `INFERRED`.

| Field | Section + offset | Value |
| :--- | :--- | :--- |
| `mcsDownThreshold` | `.data+0x12e0` | 10 |
| `mcsUpThreshold` | `.data+0x12e4` | 7 |
| `mcsDnThreshold_timer` | `.data+0x12d8` | 1 |
| `mcsUpThreshold_timer` | `.data+0x12dc` | 90 |
| `ackmcsUpThrd` | `.rodata+0xd4a4` | 98 |
| `mcsUpThrd_lowqam` | `.rodata+0xd4ac` | 95 |
| `mcsUpThrd_256` | `.rodata+0xd4b0` | 96 |
| `mcsUpThrd_1024` | `.rodata+0xd4b4` | 93 |
| `penaltyThreshold` | `.data+0x12d2` | 60 |

Downshift needs `1` unit of evidence at threshold `10`. Upshift needs `90` units at
threshold `7`, a ratio of **90.0x**. A link that has
fallen to a low QAM therefore waits far longer to climb than it took to fall, which is
the observable shape of a 4x/6x sticky lock.

`ame_core_set_automcsUpDown` is the setter for the whole group: it maps its first four
arguments onto `mcsUpThreshold`, `mcsDownThreshold`, `mcsUpThreshold_timer` and
`mcsDnThreshold_timer`, then six stack arguments onto `mcsUpThrd_1024`,
`cont1024Threshold`, `avgWeight`, `penaltyThreshold`, `penaltyTime`, `ackAccuulateCnt` and
`smallTrafficTimer`, and finally calls `autoMCS_update_ack_timer_thr`.

## 6. The MCS ceiling is coupled to the power budget

`mcs_ceiling_toggle_txpwr` gates on the system config mode, calls
`ame_bbp_get_desired_txpower` and `get_mcs_max_pwr`, and compares the two before it will
move the ceiling. The power loop and the modulation decision are therefore not independent:
a power limit can impose an MCS ceiling. This is the mechanism that makes an autopwr
misconfiguration look like a modulation fault.

## 7. Disconnect storm has no home in these modules

`disconnect_symbols`: `phy_disconnect`, `ubus_disconnect`.

Both are imported kernel symbols, not local code, so they are dependency names rather
than triggers. There is no `deauth`, no `aging` and no `storm` vocabulary at all.

The `kick` token was kept out of that count on purpose. It has 6 local hits and every one is RF bring-up:

`bbp_base_txnrx_kickoff_cpe`, `bbp_mrx_PwrMon_kickOff_once`, `bbp_util_freq_analyze_decide_isr_kickoff`, `bbp_util_freq_analyze_isr_kickoff`, `fty_bbp_base_txnrx_kickoff_cpe`, `fty_bbp_mrx_run_PwrMon_kickOff_once`

Folding those into a teardown count would have produced a number that looks like evidence
and means nothing. The disconnect-storm question is unanswerable from this module set and
is recorded as absent rather than inferred from a symbol that merely contains a word.

## 8. jumps, transitions and the honesty bar

`transitions_recovered`: **0**.

A scan of 15982 decoded ARM instructions found
0 `add?? pc, pc, rN, lsl #2` idioms and
0 `ldr pc, [...]` idioms. There is no jump table in this
module, so there is no switch to decode. The auto-MCS path is a threshold-and-timer setter,
not a state machine. Naming `ulpwr_state_change` does not make it a recovered transition,
so the count stays 0 rather than being inflated to look complete.

## 9. Hypotheses

| ID | Claim | Supported |
| :--- | :--- | :--- |
| `H1` | eab_driver.ko is present for analysis | `no` |
| `H2` | LTU 2.3.1 is present | `no` |
| `H3` | LTU spells ATPC as autopwr, not atpc | `yes` |
| `H4` | target_evm has no name in LTU | `yes` |
| `H5` | the CFO loop hysteresis has no symbol name | `yes` |
| `H6` | modulation downshift is governed by a threshold/timer pair | `yes` |
| `H7` | downshift and upshift are symmetric | `no` |
| `H8` | the MCS ceiling is independent of the power limit | `no` |
| `H9` | the auto-MCS path is a switch-based state machine | `no` |
| `H10` | CPE disconnect-storm vocabulary exists in the module code | `no` |

4 of 10 hypotheses survived the binary.

## 10. Gaps

- eab_driver.ko is absent from this repository: 0 loose files and 0 archive members across every tar scanned, so no statement is made about its internals.
- LTU 2.3.1 is absent: 0 filename hits and 0 tar members. The stage is scoped to 2.4.2 and 2.3.1 is recorded as REFUTED rather than reasoned about.
- No CPE disconnect-storm trigger exists as named code in these three modules; the only disconnect vocabulary is two imported kernel symbols in ame_dev.ko, so the storm question cannot be answered from this module set.
- transitions_recovered is 0 because no pc-relative dispatch table exists; naming a symbol is not a transition and no transition count was manufactured to look complete.
- The auto-MCS thresholds are reported as literal field values with their argument mapping; the sampled ACK statistics that drive them are runtime data this stage never sees.
- The CFO loop hysteresis has no symbol name in any of the three modules, so its constants cannot be attributed to a named function without disassembling the whole BBP receiver.
- No target was executed. Every verdict is static-binary only and is labelled CONFIRMED_STATIC_BINARY, never live.

