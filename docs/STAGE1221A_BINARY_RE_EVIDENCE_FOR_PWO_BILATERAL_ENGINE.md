<!-- doc-head: Stage 1221A — measured symbol and offset table backing the Bilateral Site-Awareness and PWO engine (static only) -->
# Stage 1221A — Binary RE evidence table for the Bilateral Site-Awareness and PWO engine

Status: `CONFIRMED_STATIC_BINARY`. Scope: static only. No SSH, no live IP, no firmware write, no
execution of any measured code. Values are static image contents; this document makes no claim about
runtime behaviour.

Builder: [`tools/re/binary_re_evidence_for_pwo_bilateral_engine.py`](../tools/re/binary_re_evidence_for_pwo_bilateral_engine.py)
Receipt: [`artifacts/verification/stage1221a_binary_re_pwo_bilateral_evidence.json`](../artifacts/verification/stage1221a_binary_re_pwo_bilateral_evidence.json)

| Module | Arch | Bytes | SHA-256 |
| :--- | :--- | ---: | :--- |
| `ubnt_poll_host.ko` (`WA.v8.7.25`) | MIPS32 big-endian, `ET_REL` | `189880` | `bfc3f499a086766917fcbbf1a52d0fac496ad237ae1671c4e640cccdd122c2b5` |
| `ame_core.ko` (`afltu_2.4.2`, CPE) | ARM little-endian, `ET_REL` | `3282052` | `fe5d489ea66bd2f32d6844d4ebefc4a12df367c2e5a1df3568973b28685059d2` |
| `ame_core.ko` (`aflturocket_2.4.2`, AP) | ARM little-endian, `ET_REL` | `3318764` | `a8d58e8d6a0c0665da361b6c188f8d266856b703ec76961927e450acacb143af` |

## 1. Why this table exists

The Bilateral Site-Awareness and PWO engine reasons about two things it cannot guess: whether a TDMA
client's poll stream is still alive, and how far a link can be pushed on the LTU modulation ladder before
its own hysteresis throws it back down. Both are governed by constants that live in the modules above.
This stage freezes those constants, with an address for each one, so the engine cites bytes instead of
folklore.

## 2. Provenance discipline

No row is transcribed from a document. Each row must resolve from a file on disk through exactly one of
three anchors:

| Anchor | What it means | Count |
| :--- | :--- | ---: |
| `symbol` | `.symtab` `st_value`, with the containing section resolved through `st_shndx` | 26 |
| `relocation` | an `.rel.*` entry naming the symbol, reported at the instruction that consumes it | 3 |
| `instruction` | a decoded `lui`/`ori` constant pair, or an exact branch word | 2 |
| `field` | a store displacement decoded from a single instruction (struct field) | 2 |

The three-anchor rule is what keeps `fabricated_offsets` at `0`: an offset that cannot be produced by one
of those anchors has no way into the table. Symbols that exist only as struct fields are excluded rather
than given an invented address; see section 6.

Every row is then re-derived a second time from a fresh parse by `reverify()`, which re-reads `.symtab`,
re-walks the relocation sections and re-decodes the instruction stream without reusing any cached value.
Four negative controls were run to confirm the check actually bites:

| Injected fault | Result |
| :--- | :--- |
| `startThrd_4096` offset changed to `0x9999` | `symbol offset moved` (expected 54464, got 39321) |
| deadline constant changed to `30,000,000` | `constant changed` (expected 30001000, got 30000000) |
| field displacement changed to `0x289` | `displacement changed` (expected 0x288, got 0x289) |
| a relocation row moved to `0x1234` | `no relocation for add_timer at 0x1234` |

`fabricated_offsets = 0` is therefore the output of a measurement, not an assertion. The builder raises
and refuses to write if the count is ever non-zero.

## 3. `ubnt_poll_host.ko` — poll liveness and the missing-poll watchdog

| Symbol | Offset | Where | Value | Grade | Source |
| :--- | :--- | :--- | ---: | :--- | :--- |
| `ubnt_poll_host_sta_bmiss_ind` | `0x167c` | `.text` | fn (8 B thunk) | `CONFIRMED` | 1220A |
| `ubnt_poll_host_start_os_timer` | `0x1468` | `.text` | fn (228 B) | `CONFIRMED` | 1220A |
| `ubnt_poll_host_stop_os_timer` | `0x154c` | `.text` | fn | `CONFIRMED` | 1220A |
| `ubnt_poll_host_data_create` | `0x7170` | `.text` | fn (488 B) | `CONFIRMED` | 1220A |
| `add_timer` call site | `0x151c` | `.text` | call | `CONFIRMED` | 1220A |
| `mod_timer` call site | `0x102c` | `.text` | call | `CONFIRMED` | 1220A |
| bmiss trampoline caller | `0x7800` | `.text` | call | `CONFIRMED` | 10 |
| `deadline_const` | `0x7bf8` | `.text` | `30,001,000` | `CONFIRMED` | 1220A |
| `panic_branch` | `0x7c08` | `.text` | `0x14400006` (`bnez`) | `CONFIRMED` | 10 |
| poll liveness stamp | `0x288` | `dev` struct | field | `INFERRED` | 1220A |
| timer handle slot | `0x178` | `dev` struct | field | `INFERRED` | 1220A |

The engine can use this chain end to end. `data_create` (`0x7170`) stamps `dev+0x288` and arms a
`1,000,000` us interval on `start_os_timer`; the callback compares `(jiffies - dev+0x288) * 1000` against
`30,001,000` us at `0x7c04` and takes `bnez` at `0x7c08` while the link is still alive. A silence longer
than `30.001 s` reaches `panic`. That is the exact inequality the engine must model, and both operands are
cited above.

The two `INFERRED` rows are honest about their status: the displacement is decoded from a single `sw`
instruction, but the field *name* comes from how the value is stored and later subtracted, not from a
header or DWARF.

## 4. `ame_core.ko` (CPE) — rate adaptation and PA power surface

| Symbol | Offset | Where | Value | Grade | Source |
| :--- | :--- | :--- | ---: | :--- | :--- |
| `startThrd_4096` | `0xd4c0` | `.rodata` | `97` | `CONFIRMED` | 651A |
| `stayThrd_4096` | `0xd4c4` | `.rodata` | `90` | `CONFIRMED` | 651A |
| `penaltyThreshold` | `0x12d2` | `.data` | `60` | `CONFIRMED` | 249A |
| `penaltyTime` | `0x12a8` | `.data` | `4` | `CONFIRMED` | 249A |
| `mcsUpThreshold` | `0x12e4` | `.data` | `7` | `CONFIRMED` | 12 |
| `mcsDownThreshold` | `0x12e0` | `.data` | `10` | `CONFIRMED` | 12 |
| `mcsUpThrd_1024` | `0xd4b4` | `.rodata` | `93` | `CONFIRMED` | 12 |
| `avgWeight` | `0xd4a2` | `.rodata` | `20` | `CONFIRMED` | 12 |
| `cont1024Threshold` | `0x12d4` | `.data` | `1` | `CONFIRMED` | 12 |
| `smallTrafficTimer` | `0x129e` | `.data` | `1` | `CONFIRMED` | 12 |
| `ackAccuulateCnt` | `0x12d1` | `.data` | `25` | `CONFIRMED` | 1220A |
| `cpeFsmStop` | `0x4d870` | `.text` | fn (900 B) | `CONFIRMED` | 64A |
| `mcs_ceiling_toggle_txpwr` | `0x36f20` | `.text` | fn (412 B) | `CONFIRMED` | 12 |
| `table_ptpPwrRange` | `0x1ec` | `.data` | 448 B table | `CONFIRMED` | 12 |
| `table_ptmpAPPwrRange` | `0x5438` | `.rodata` | 96 B table | `CONFIRMED` | 12 |
| `bbp_rf_set_super4096` | `0x171584` | `.text` | fn (348 B) | `CONFIRMED` | 11 |
| `ame_core_set_automcsUpDown` | `0x72ac` | `.text` | fn (172 B) | `CONFIRMED` | 12 |
| `sensitivity` | `0x5870` | `.rodata` | 30 B table | `CONFIRMED` | 12 |
| `mcs_txpwr_freq_ptp` | `0x4e14` | `.rodata` | 84 B table | `CONFIRMED` | 12 |

Note `0xd4c0` and `0xd4c4` are four bytes apart, which is only consistent with `u32` scalars. The
neighbouring `avgWeight` at `0xd4a2` is a `u8`, so the block mixes widths and must be read per symbol,
never as one struct.

`ackAccuulateCnt` is included on purpose. It is the byte immediately before `penaltyThreshold`, and its
value `25` is the figure Stage 12 reported for `penaltyThreshold`. Carrying it in the table makes the
engine's own `penaltyThreshold` reading self-checking: if a future build ever reports `25` there, the row
above it is the first thing to inspect.

## 5. `ame_core.ko` (AP) — cross-check

| Symbol | Offset | Where | Value | Grade | Source |
| :--- | :--- | :--- | ---: | :--- | :--- |
| `startThrd_4096` | `0xd5dc` | `.rodata` | `97` | `CONFIRMED` | 64A |
| `stayThrd_4096` | `0xd5e0` | `.rodata` | `90` | `CONFIRMED` | 64A |
| `penaltyThreshold` | `0x12ee` | `.data` | `60` | `CONFIRMED` | 1232A |

Same three values, different addresses. The rate gate is a property of the LTU build, not of the
CPE-versus-AP role, so the engine may apply one threshold pair to both ends while resolving each address
per module.

## 6. Excluded symbols

These were checked and deliberately left out, because a plausible address would be a fabrication:

| Symbol | Reason |
| :--- | :--- |
| `autoMcsCeiling` | no `.symtab` entry; it is a struct field, so no offset is offered |
| `autoMcsUpDown` | no `.symtab` entry; the handler `ame_core_set_automcsUpDown` at `0x72ac` is the anchored proxy |
| `frame_len_store` | no `.symtab` entry |
| `duty_cycle_store` | no `.symtab` entry |

The builder re-checks these four against the symbol table and fails if any of them ever does appear.

## 7. Offset drift against earlier documents

Four rows carry a measured address that contradicts a previously published figure. The measured value is
used; the older figure is retained for traceability only.

| Symbol | Earlier figure | Measured | Reading |
| :--- | :--- | :--- | :--- |
| `mcs_ceiling_toggle_txpwr` | `0x391b0` | `0x36f20` | different build lineage, or a mis-transcription; both are UNKNOWN |
| `table_ptpPwrRange` | `0x1f8` | `0x1ec` | `0x1f8` is 12 bytes inside the 448-byte table, not its base |
| `bbp_rf_set_super4096` | `0x1766bc` | `0x171584` | different build lineage |
| `ame_core_set_automcsUpDown` | `0x84d8` | `0x72ac` | different build lineage |

The `table_ptpPwrRange` case is instructive: a pointer 12 bytes into a table still dereferences to
plausible-looking data, so the error would not have announced itself. Anchoring on the symbol base rather
than on a remembered address is what caught it.

## 8. How the engine should consume this

1. Resolve addresses per module, never across modules. `startThrd_4096` is `0xd4c0` on the CPE build and
   `0xd5dc` on the AP build.
2. Read scalars at their declared width. `penaltyThreshold` is one byte; reading four bytes at `0x12d2`
   would fold in `cont1024Threshold` and produce nonsense.
3. Treat the watchdog as an inequality, not a timer: poll silence greater than `30.001 s` reaches
   `panic`. The `1 s` arming period only sets the sampling granularity.
4. Treat the `INFERRED` rows as named field offsets, and re-check them if a new firmware build changes the
   store site.

## 9. Gaps

- Three modules only. `ame_dev.ko`, `ame_radio_mod.ko`, `mac80211` and `ath10k` objects are not in this
  table.
- The two `INFERRED` field names are not confirmed by DWARF or a header.
- The build lineage behind the four drifted figures is `UNKNOWN`; this stage cannot say which firmware
  those documents were describing.
- Values are static image contents. Nothing here establishes runtime causality.
- Static only: no device was contacted, no firmware was written.

## 10. Reproduce

```powershell
python tools/re/binary_re_evidence_for_pwo_bilateral_engine.py --check-determinism
```

Two consecutive runs are byte-identical. Receipt SHA-256:
`ecdefe857a584dbc1bd5e5218379ad1094cbfbd60ecd713b0b30412730510213`. The payload is serialised through
`decase()` with no wall clock, so regeneration is reproducible.
