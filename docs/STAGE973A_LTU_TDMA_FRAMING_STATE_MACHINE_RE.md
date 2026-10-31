<!-- doc-head: Stage 973A - the LTU TDMA framing state machine cannot be recovered here, because the corpus yields 90 frame symbols, 28 SFN symbols and 22 FSM-named functions but zero decoded jump tables, so transitions_recovered stays zero and guard, tdma and atpc are refuted as named artifacts -->
# Stage 973A - the LTU TDMA framing state machine

- **Receipt**: [`artifacts/autoresearch/stage973a_ltu_tdma_framing_state_machine_re.json`](../artifacts/autoresearch/stage973a_ltu_tdma_framing_state_machine_re.json)
- **Tool**: [`tools/re/dissect_stage973a_ltu_tdma_framing_state_machine_re.py`](../tools/re/dissect_stage973a_ltu_tdma_framing_state_machine_re.py)
- **Scope**: static only. Offline ELF and symbol inspection of seven extracted LTU `.ko` files. No module loaded, no firmware written, no radio contacted.
- **Provenance**: `CONFIRMED_STATIC_BINARY`

## 0. Result

```
modules_ok=7 (census)   summary scope: radio fabric (ame_*, cds_mac_mod)
frame_symbols=90   sfn_symbols=28   slot_symbols=2   state_symbols=31   fsm_symbols=22
guard_token_hits=0   tdma_token_hits=0   atpc_token_hits=0
states_enumerated=0   transitions_recovered=0   contract_symbols_present=1/5
```

**The state machine is not recovered, and this document does not pretend otherwise.** Naming a routine
`cpeFsmRoutine` is evidence that a routine exists, not evidence of what it transitions to. There is no
disassembler in this scope, so `transitions_recovered` is 0 by construction.

## 1. What the framing vocabulary actually is

Scope note: the summary is computed over the **radio fabric** modules (`ame_core`, `ame_dev`,
`ame_radio_mod`, `cds_mac_mod`, `ame_dfs`). `qca-ssdk.ko` and `ubnthal.ko` are in the tree, are fully
censused in the receipt, and are excluded from the summary for the reason given in section 4.

| token | symbols | radio strings | note |
| :--- | ---: | ---: | :--- |
| `frame` | 90 | 315 | the dominant framing word |
| `sfn` | 28 | 172 | system frame number, 32-bit per the log formats |
| `slot` | 2 | 63 | two symbols: a CZ slot allocator and an AES slot counter |
| `pulse` | 16 | 97 | frame pulse offset among them |
| `offset` | 30 | 111 | |
| `state` | 31 | 153 | |
| `fsm` | 22 | 120 | |
| `tdd` | 1 | 1 | `bbp_mrx_foe_TDDeRotCFO` |
| `autopwr` | 37 | 50 | |
| `guard` | 0 | 0 | **REFUTED** |
| `tdma` | 0 | 0 | **REFUTED** |
| `atpc` | 0 | 0 | **REFUTED** |

This is the stage's sharpest result. The LTU framing vocabulary is **frame, sfn, slot, symbol**. It does
not use the words `guard`, `tdma` or `atpc` anywhere a symbol table or a string table can see, so a reader
expecting an explicit TDMA scheduler, guard field and ATPC loop will not find them named here.

## 2. The frame surface

```
ame_bbp_get_frame_pulse_offset   ame_bbp_set_frame_pulse_offset   ame_bbp_set_rxpulse
ame_bbp_check_frame_start        ame_bbp_op_frame_start           ame_bbp_op_frame_stop_real
ame_bbp_get_frame_len            ame_bbp_set_frame_len            ame_bbp_op_framelen_reset
ame_core_ptmp_frame_adjust_ap    ame_core_ptmp_frame_adjust_cpe   ame_core_deliver_frame
AME_EAB_AdjustFrameLength   AME_Scheduler_MaxFragPerFrame   AME_Scheduler_SetFrameOp
```

The `cz_cross_frame_*` family is the most structurally interesting group: six getters and one setter
covering backoff enable, grouping count, window size, max timeout, and a multiple-resolution pair with its
own enable flag - a backoff configuration surface with named knobs, **CONFIRMED** as names only.

`frame_pulse_offset` is **REFUTED** as a symbol. The shipped names are the accessor pair
`ame_bbp_get_frame_pulse_offset` / `ame_bbp_set_frame_pulse_offset` in `ame_core.ko` and the sysfs pair
`frame_pulse_offset_show` / `frame_pulse_offset_store` in `ame_dev.ko`. All four are **CONFIRMED**.

## 3. SFN synchronisation

28 symbols forming a counter-and-sync API rather than a state machine - getters
(`ame_bbp_get_rx_sfn`, `ame_bbp_get_tx_sfn`, `ame_bbp_get_sync_sfn_count`), setters
(`ame_bbp_set_rx_sfn`, `ame_bbp_set_tx_sfn`, `ame_bbp_set_remote_SFN`), sync (`ame_bbp_sync_SFN`,
`ame_bbp_op_sync_sfn`, `ame_bbp_is_remote_SFN_synchronized`, and the `bbp_base_*` twins `syncSFN`,
`is_sfn_sync`, `is_remote_SFN_synchronized`), `bbp_mrx_*` / `bbp_mtx_*` / `fty_bbp_*` mirrors, and the
sysfs pair `sfn_sync_cnt_show` / `sfn_sync_cnt_store`.

`ame_bbp_is_remote_SFN_synchronized` is the only one of the five contract-named symbols that exists, and
it is a 12-byte `STT_FUNC`, which reads as a predicate over a cached flag. **CONFIRMED** present,
**UNKNOWN** behaviour.

The log format strings confirm the width. The same field is emitted twice, once from the software
counter and once from the hardware counter, as `<TXnRX> sw SFN    : 0x%x :` and
`<TXnRX> hw SFN    : 0x%x :`, and the capture path logs `Set SFN=%08x at %08x`. **CONFIRMED** as
strings.

## 4. Why guard and slot homonyms had to be separated

An unscoped census reports 61 `guard` hits and 27 `slot` symbol hits, which would look like a
guard-interval field and a slot scheduler. Every one of them is a homonym. The `guard` total is 17
symbols plus 44 strings, all in `qca-ssdk.ko`; the `slot` total is 25 symbols in `qca-ssdk.ko` plus 2
genuine radio-fabric symbols:

| homonym | symbols | strings | actual meaning |
| :--- | ---: | ---: | :--- |
| `guard` | 17 | 44 | `fal_ip_arp_guard_*`, `fal_ip_source_guard_*` - L2 anti-spoofing |
| `slot` | 25 | - | `fal_*_shaper_timeslot_*`, `fal_policer_timeslot_*` - shaper windows |

Counting either as TDMA framing vocabulary would be a category error, so the receipt carries both the
scoped summary and a `homonym_audit` block with the excluded names. `guard_fields` is therefore `[]`,
and that emptiness is a measurement, not an omission.

## 5. The FSM-shaped names

| family | count | members |
| :--- | ---: | :--- |
| `apFsm*` | 8 | `CalcSigDone CheckCalcSig CheckCrystalLock InitDone Routine Start StartCalcSig Stop` |
| `cpeFsm*` | 13 | `CheckCIREst CheckCrystalLock CheckRFAlign CheckSFO InitDone LockDone NxN_DownlinkTA NxN_OffGPS_OnCIR RestartAfterSFO Routine Scan Start Stop` |
| other | 1 | `fsmResetModemRuntime` |

The member names describe **crystal lock, carrier estimation, sampling frequency offset and RF align**.
That is a modem bring-up sequence, not a TDMA superframe scheduler. `apFsmRoutine` is 1,280 bytes and
`cpeFsmRoutine` is 808 bytes, so they are real dispatch loops. **CONFIRMED** as names and sizes. What
they dispatch to is **UNKNOWN**.

## 6. Why states_enumerated is zero

31 state symbols exist. 29 are `STT_FUNC`; the two `STT_OBJECT` entries are `state` (a 156-byte `.bss`
struct in `ame_dfs.ko`) and `g_dbg_state` (a 4-byte `.bss` scalar in `cds_mac_mod.ko`). Neither is an
enumerator, and `.bss` has no file bytes, so no state value is readable from the file.

Three functions prove a symbolic name table exists in `.rodata`: `Ctrl_GetCurrStateToStr` (184 bytes),
`ame_modem_get_state_str` (328 bytes) and `ame_modem_get_state_to_str` (24 bytes). State names are
therefore almost certainly present as strings, and still not enumerable here: mapping a string table to
enum indices requires decoding those functions, and the `<ctrl>` log formats print integers rather than
names - `<ctrl>: ap state now %d evt %d`, `<ctrl>: ap state to %d`, `<ctrl>: cpe state now %d evt %d` - so
the runtime text carries no state vocabulary to harvest.

`AME_HSM_BUSY` (48 bytes), `AME_HSM_SORT` (92 bytes), `AME_HSM_RESET` (128 bytes) and their siblings look
like an enum but are `STT_FUNC` command handlers, not constants, and must not be read as a state set.

## 7. Power control

37 `autopwr` symbols across the radio fabric. The contract-named `auto_pwr_run_handlr`, `autopwr_algo` and
`auto_pwr_adjust_pwr_by_mcs` are all **REFUTED**: zero exact matches. The shipped names are
`autopwr_init`, `autopwr_reset`, `autopwr_pwr_recfg_indicate`, `autopwr_dump_info`,
`ptmp_cpe_autopwr_routine`, `ptmp_cpe_autopwr_routine_work`, `ptmp_cpe_autopwr_check_txpwr`,
`ptmp_cpe_autopwr_get_max_txpwr_by_mcs`, `ptmp_cpe_autopwr_calc_expected_mcs`,
`ptmp_ap_autopwr_tx_power_adjust_routine`, `ptmp_ap_autopwr_calc_max_expected_dl_mcs`, and the sysfs
pairs `autopwr_en_show/store` and `autopwr_info_show/store`.

`ptmp_cpe_autopwr_get_max_txpwr_by_mcs` is the closest shipped relative of the refuted
`auto_pwr_adjust_pwr_by_mcs`, and the two are not the same claim: a getter of a per-MCS power ceiling is
not an adjuster. **CONFIRMED** names, **UNKNOWN** control law. `atpc` appears zero times, so calling this
loop ATPC is a naming choice, not a binary fact.

## 8. Labels

| claim | label |
| :--- | :--- |
| 90 frame, 28 sfn, 31 state, 22 fsm symbols exist in the radio fabric | CONFIRMED |
| `ame_bbp_is_remote_SFN_synchronized` is a 12-byte function | CONFIRMED |
| `apFsm*` and `cpeFsm*` are real dispatch routines of 1,280 and 808 bytes | CONFIRMED |
| SFN is 32-bit, with separate software and hardware counters | CONFIRMED (format strings) |
| `frame_pulse_offset` is a symbol | REFUTED (accessors exist, the bare name does not) |
| `auto_pwr_run_handlr`, `autopwr_algo`, `auto_pwr_adjust_pwr_by_mcs` exist | REFUTED |
| `guard` appears in the radio fabric | REFUTED (0 symbols, 0 strings) |
| `tdma` and `atpc` appear anywhere | REFUTED (0 symbols, 0 strings each) |
| any state enumeration or state-to-state transition | UNKNOWN (0 recovered) |
| the `*_to_str` name tables | UNKNOWN (functions not decoded) |

## 9. Gaps

1. No disassembler in scope: no jump table, switch case or comparison chain was decoded, so
   `transitions_recovered=0` and `states_enumerated=0` are method-bounded.
2. The framing vocabulary is name-level. Which symbol executes in which frame phase is **UNKNOWN**.
3. `guard`, `tdma` and `atpc` are absent as names. The corresponding behaviour may exist unnamed; that is
   not excluded, and it is not claimed.
4. The `*_to_str` state tables in `.rodata` are not attributable without decoding those functions.
5. `AME_HSM_*` are command handlers, not enum constants; they must not be read as a state set.
6. The SFN surface is a counter and sync API. The handshake itself is not recovered.
7. The unscoped census inflates `guard` to 61 (17 symbols plus 44 strings) and `slot` to 27 symbols
   through `qca-ssdk.ko` ARP-guard and timeslot homonyms. Both numbers are in the receipt for audit.
8. `eab_driver.ko` is absent from the corpus (0 files, 154 modules in tree), so no framing claim can be
   attributed to it. No dynamic verification was run and no radio was contacted.

## 10. Reproduce

```
python tools/re/dissect_stage973a_ltu_tdma_framing_state_machine_re.py
```

Two consecutive runs are byte-identical, including under differing `PYTHONHASHSEED`.
