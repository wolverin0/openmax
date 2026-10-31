<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

<!-- doc-head: Stage 971A - the LTU 4096-QAM ladder is a byte fact in ame_core.ko, present in exactly two of five autoMcs tables while the other three stop at MCS 23, and eab_driver.ko does not exist in this corpus so every eab claim is refuted with a measured count of zero -->
# Stage 971A - the 4096-QAM ladder in `ame_core.ko`

- **Receipt**: [`artifacts/autoresearch/stage971a_ltu_ame_core_4096qam_tables_re.json`](../artifacts/autoresearch/stage971a_ltu_ame_core_4096qam_tables_re.json)
- **Tool**: [`tools/re/dissect_stage971a_ltu_ame_core_4096qam_tables_re.py`](../tools/re/dissect_stage971a_ltu_ame_core_4096qam_tables_re.py)
- **Scope**: static only. Offline ELF, section, symbol and byte inspection of extracted `.ko` files. No module loaded, no firmware written, no radio contacted.
- **Provenance**: `CONFIRMED_STATIC_BINARY`

## 0. Result

```
modules_ok=7          symbols_total_ame_core=9823
qam4096_hits=18       mcs_token_hits=377        evm_token_hits=33
modulation_symbols=186   rate_table_symbols=21
tables_confirmed=16   tables_inferred=5
ladder_tables_reaching_mcs31=2   ladder_tables_ceiling_at_mcs23=3
eab_driver_present=0  eab_driver_files=0
```

## 1. The corpus

The LTU 2.4.2 module tree holds **154** modules. Seven are the airMAX/LTU fabric and all seven parsed as
32-bit little-endian `ET_REL`:

| module | bytes | .symtab entries |
| :--- | ---: | ---: |
| `ame_core.ko` | 3,282,052 | 9,823 (9,799 named) |
| `qca-ssdk.ko` | 1,607,052 | - |
| `ame_radio_mod.ko` | 578,424 | - |
| `ame_dev.ko` | 298,760 | 1,855 (1,833 named) |
| `ubnthal.ko` | 152,640 | - |
| `ame_dfs.ko` | 141,472 | - |
| `cds_mac_mod.ko` | 139,672 | - |

`vermagic=3.14.65 SMP preempt mod_unload ARMv7 p2v8` is read from the `.modinfo` string of both
`ame_core.ko` and `ame_dev.ko`. **CONFIRMED.**

## 2. The one load-bearing measurement

Five `STT_OBJECT` byte tables in `.rodata` carry an MCS ladder at a 2-byte stride. The bytes are read
directly from the section at each symbol's `st_value`, so they are **CONFIRMED**:

| symbol | bytes (hex) | entries | byte 0 | byte 1 |
| :--- | :--- | ---: | :--- | :--- |
| `autoMcsUseSisoTbl` | `07000b000f000f01130117011f01` | 7 | 7,11,15,15,19,23,31 | 0,0,0,1,1,1,1 |
| `autoMcsOthersTbl` | `070007010b010f01130117011f01` | 7 | 7,7,11,15,19,23,31 | 0,1,1,1,1,1,1 |
| `autoMcsAllSisoTbl` | `07000b000f0013001700` | 5 | 7,11,15,19,23 | all 0 |
| `autoMcsMimoTP` | `07010b010f0113011701` | 5 | 7,11,15,19,23 | all 1 |
| `autoMcsSisoTP` | `07000b000f0013001700` | 5 | 7,11,15,19,23 | all 0 |

The shape is unambiguous: **MCS 31 occurs in two of the five tables and nowhere else.** The three
5-entry tables stop at MCS 23. Reading byte 0 as an MCS index is **INFERRED** - the values form a
4-step ladder terminating at 31, which is the index [<memorymaster-id>] assigns to 4096-QAM 5/6, but no code was
disassembled to prove the mapping.

Reading byte 1 as a SISO/MIMO selector is **UNKNOWN**. It is 0 on the three all-SISO tables, 1 on
`autoMcsMimoTP`, and split on the two 7-entry tables. That is suggestive and not proof.

**This corroborates [<memorymaster-id>] at the byte level**: the claim that 4096-QAM is gated to the 2x2 MIMO
tables reproduces as a static fact. The further claim that the gate closes at 60/80/100 MHz does
**not** reproduce here, because mapping a 7-entry ladder to a bandwidth list requires the calling code.
That part stays **UNKNOWN** in this stage and is recorded as a gap.

## 3. Symbol-level 4096-QAM artefacts

Six `ame_core.ko` symbols carry the literal `4096` (**CONFIRMED**):

```
autoMCS_get4096   autoMCS_set4096   bbp_rf_get_super4096   bbp_rf_set_super4096
startThrd_4096    stayThrd_4096
```

`check_4096mimo_ofdm` and `choose_mcsTPindex_ofdm` are **REFUTED**: zero exact matches and zero
substring matches across all seven modules. `autoMCS_updateDL` is present as `STT_FUNC` at 6,628 bytes
and `af_ltu5_mcs_txpwr_freq`, `af_ltuLR_mcs_txpwr_freq` and `af_5xhd_mcs_txpwr_freq` are present as
48-byte `STT_OBJECT` tables in `.rodata`.

## 4. Table inventory

`tables_confirmed` (16) counts table-like `STT_OBJECT`s whose bytes exist in a `PROGBITS` section, so a
reader can verify them. `tables_inferred` (5) counts table-like `STT_OBJECT`s that live in `.bss` and
therefore assert a table the file does not contain:

```
confirmed: af_5xhd_mcs_txpwr_freq af_ltu5_mcs_txpwr_freq af_ltuLR_mcs_txpwr_freq
           autoMcsAllSisoTbl autoMcsMimoTP autoMcsOthersTbl autoMcsSisoTP autoMcsTP
           autoMcsUseSisoTbl fft_full_table mcs_txpwr_freq_ptp ptmp_ap_mcs_txpwr_freq
           ra_offset_table table_ptmpAPPwrRange table_ptmpCPEPwrRange table_ptpPwrRange
inferred:  DLSymbolTbl LCSymbolTbl ULSymbolTbl mac_addr_table tt_hash_tbl
```

`table_ptpPwrRange` is a 448-byte `.data` object and is the table [<memorymaster-id>] names for power-range
gating. Its bytes are recoverable and are stored in the receipt, but its row and column semantics are
**UNKNOWN** here: the 14-byte periodicity is visible in the hex, the meaning of the second lane is not.

## 5. EVM and rate vocabulary

14 `ame_core.ko` symbols carry `evm`, including `ame_bbp_op_evm_mcs_map` (`STT_FUNC`, 88 bytes) and the
`bbp_mrx_evm_*` configuration family. 124 symbols carry `mcs`; the notable families are the
`autoMCS_*` control set, the `AME_Scheduler_AutoMCS*` set, the `Sched_fetch_*mcs*` getters and the
`AME_Sched_MixMcs_*` portion controls. All **CONFIRMED** as names.

## 6. `eab_driver.ko` is absent

Measured, not asserted:

- `*eab*.ko` across `artifacts/` and `firmware/`: **0 files**.
- Modules in the 3.14.65 tree: **154**, none of them eab.
- Prior receipts whose filename mentions `eab` and which therefore describe a binary that is not in
  this corpus: 6, listed in the receipt.

**REFUTED**: any claim of the form "`eab_driver.ko` does X". There is no source binary in this corpus,
and nothing in this stage can reproduce such a claim. This agrees with the earlier 858A finding.

## 7. Labels

| claim | label |
| :--- | :--- |
| seven focus modules parse as ARM LE `ET_REL`, kernel 3.14.65 | CONFIRMED |
| `ame_core.ko` symtab has 9,823 entries, 9,799 named | CONFIRMED |
| MCS 31 occurs in `autoMcsUseSisoTbl` and `autoMcsOthersTbl` only | CONFIRMED |
| the three 5-entry ladders stop at MCS 23 | CONFIRMED |
| byte 0 of a ladder entry is an MCS index | INFERRED |
| byte 1 is a SISO/MIMO selector | UNKNOWN |
| 4096-QAM is gated off at 60/80/100 MHz | UNKNOWN here |
| `check_4096mimo_ofdm` exists | REFUTED |
| `choose_mcsTPindex_ofdm` exists | REFUTED |
| `eab_driver.ko` exists in the corpus | REFUTED (0 files) |
| which function reads which table | UNKNOWN (no disassembly) |

## 8. Gaps

1. No disassembler was used, so no table-to-caller binding exists. Every "who reads this table" question
   is **UNKNOWN**.
2. The MCS reading of byte 0 is inference from the ladder shape, not from code.
3. The bandwidth index of the 7-entry ladders is not recovered, so the 10-50 MHz gating claim is not
   re-verified.
4. `tables_inferred` names occur in `.bss`; their contents do not exist in the file and cannot be read.
5. No dynamic verification of any 4096-QAM behaviour.
6. `eab_driver.ko` claims in 6 prior receipts are not reproducible from this corpus.

## 9. Reproduce

```
python tools/re/dissect_stage971a_ltu_ame_core_4096qam_tables_re.py
```

Two consecutive runs are byte-identical, including under differing `PYTHONHASHSEED`.
