<!-- doc-head: Stage 1158A offline RE of mac80211 AQL threshold vs per-AC limits, decoded branch condition; static only -->
# Stage 1158A — the exact AQL condition in this mac80211

## 1. The question, and the answer in one paragraph

The question was: in `ieee80211_txq_may_transmit` and
`ieee80211_sta_update_pending_airtime`, what exactly makes `aql_threshold` select
the low versus the high per-AC limit. The bytes give a negative answer and a
different, positive one. Neither function reads `aql_threshold` at all. The two
per-AC limits are **combined arithmetically**, not selected:
`budget = aql_txq_limit_high[ac] + ((count_of_queued_txqs_on_that_ac *
aql_txq_limit_low[ac]) >> 1)`, and per-AC pending airtime is compared against that
budget with `sltu`. A census of every sized `FUNC` symbol finds exactly two reads
of `aql_threshold` in a decision, in `ieee80211_txq_airtime_check` and in
`ieee80211_next_txq`, where it is a **global admission gate** on AP-wide pending
airtime: at or above the threshold the strict per-AC test is skipped or the station
is denied, and no per-AC limit is consulted. Verdict on the premise: **REFUTED**.

## 2. Inputs and reproduction

| item | value |
| :--- | :--- |
| binary | `artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko` |
| bytes | `829464` |
| sha256 | `19a8fde6c6e5efbe...` (prefix asserted by the tool) |
| vermagic | `6.6.110` |
| build | file markers in `.rodata.str1.4` read `backports-6.12.52`, so mainline 6.6 source is not a valid reference |
| ELF | `ET_REL`, `EM_MIPS`, ELF32, big endian |
| tools | `tools/re/mac80211_aql_threshold_may_transmit_re_verifier.py`, python stdlib only |
| receipt | `artifacts/verification/stage1158a_mac80211_aql_threshold_may_transmit_re.json` |

```text
python tools/re/mac80211_aql_threshold_may_transmit_re_verifier.py
python tools/re/mac80211_aql_threshold_may_transmit_re_verifier.py --check
```

Two consecutive runs are byte-identical: sha256
`f6f57950c683fe7444fea9866f2efb995d97bff9cd3eaee824e2c13e13b4bc3f` (83428 bytes).

## 3. Symbols (CONFIRMED)

| symbol | offset | size |
| :--- | ---: | ---: |
| `ieee80211_txq_may_transmit` | `0x3c5a4` | 904 |
| `ieee80211_sta_update_pending_airtime` | `0xb258` | 652 |
| `ieee80211_txq_airtime_check` | `0x3ba7c` | 176 |
| `ieee80211_next_txq` | `0x3ced4` | 796 |

All four are `FUNC` symbols with sizes in `.text`, so boundaries are given, not
bracketed.

## 4. `ieee80211_local` AQL block, derived not assumed

Two derivations were used, and both are mechanical:

- `aql_threshold`: the rodata literal is located, its `addiu` reference is
  followed, and the window is decoded to the `jal` whose callee symbol is
  `debugfs_create_u32`. That function's fourth argument is the field pointer, and
  it is built by `addiu $a3, $s0, 0x13c` at `.text+0x713f8`. So the field offset is
  `0x13c` — anchored by the name string and by the callee, not by a guess.
- `aql_txq_limit_*`: the debugfs reader's format string
  `AC\tAQL limit low\tAQL limit high\nVO\t%u\t\t%u\n...BC/MC\t%u\n` has nine
  unsigned slots in a known order. Each `%u` is fed from a specific vararg slot
  (`$a3`, then `0x10($sp)` onward), so tracking register to load to slot maps each
  slot to a field. The result then had to match the structural prediction (two
  runs of four `u32`, one run `0x10` above the other, plus one isolated scalar);
  the tool aborts if it does not.

| field | offset | derivation |
| :--- | ---: | :--- |
| `aql_txq_limit_bc_mc` | `0x118` | reader slot 9, the `BC/MC` line |
| `aql_txq_limit_low[0..3]` | `0x11c` | reader slots 1,3,5,7 |
| `aql_txq_limit_high[0..3]` | `0x12c` | reader slots 2,4,6,8 |
| `aql_threshold` | `0x13c` | `debugfs_create_u32` value pointer |
| `aql_pending_total` | `0x140` | pending reader slot 6 (`total`) |
| `aql_pending_bc_mc` | `0x144` | pending reader slot 5 (`BC/MC`) |
| `aql_pending_per_ac[0..3]` | `0x148` | pending reader slots 1-4 |

The block is gapless from `0x118` to `0x157`, which is the strongest single check
on the whole layout: `0x118`, `0x11c+0x10`, `0x12c+0x10`, `0x13c`, `0x140`,
`0x144`, `0x148+0x10` tile the region exactly with no hole and no overlap.

## 5. The decoded branch, instruction by instruction

`ieee80211_txq_may_transmit`, all words asserted by the tool against the image:

| address | hex | instruction | role |
| :--- | :--- | :--- | :--- |
| `0x3c5d4` | `90b70009` | `lbu $s7, 9($a1)` | `ac` |
| `0x3c64c` | `8cc2011c` | `lw $v0, 284($a2)` | `aql_txq_limit_low[ac]` |
| `0x3c654` | `70a21002` | `mul $v0, $a1, $v0` | `count * low[ac]` |
| `0x3c65c` | `8cc5012c` | `lw $a1, 300($a2)` | `aql_txq_limit_high[ac]` |
| `0x3c660` | `8c630000` | `lw $v1, 0($v1)` | per-AC pending, `local+0x148+4*ac` |
| `0x3c664` | `00021042` | `srl $v0, $v0, 1` | halve the scaled term |
| `0x3c668` | `00451021` | `addu $v0, $v0, $a1` | `budget = ((count*low)>>1) + high[ac]` |
| `0x3c66c` | `0062102b` | `sltu $v0, $v1, $v0` | unsigned `pending[ac] < budget` |
| `0x3c670` | `14400020` | `bnez $v0, 0x3c6f4` | taken below budget, fall through on or above |

The count is not a constant. At `0x3c604..0x3c63c` the function walks the per-AC
list head at `local+0xe8+8*ac` and counts its nodes, and sets the count to `-1`
when the list is empty (`addiu $a1, $zero, -1` at `0x3c8c0`). Control flow: taken
means the per-AC rotation body at `0x3c6f4`; not taken means the list-delete path
at `0x3c678` and a return of `1` at `0x3c6e8`.

`ieee80211_txq_airtime_check`, the only threshold-consuming decision:

| address | hex | instruction | role |
| :--- | :--- | :--- | :--- |
| `0x3baa4` | `24060010` | `addiu $a2, $zero, 0x10` | `tid == IEEE80211_NUM_TIDS` guard |
| `0x3bac4` | `24a6f9dc` | `addiu $a2, $a1, -0x624` | sta per-AC element base |
| `0x3bad0` | `8cc50000` | `lw $a1, 0($a2)` | slot at element+4 |
| `0x3bad4` | `8c67f9e0` | `lw $a3, -0x620($v1)` | slot at element+8 |
| `0x3bad8` | `00a7282b` | `sltu $a1, $a1, $a3` | deny when element+4 < element+8 |
| `0x3bae4` | `8c820140` | `lw $v0, 320($a0)` | total AQL pending |
| `0x3bae8` | `8c84013c` | `lw $a0, 316($a0)` | `aql_threshold` |
| `0x3baec` | `0044102b` | `sltu $v0, $v0, $a0` | `total_pending < aql_threshold` |
| `0x3baf0` | `10400005` | `beqz $v0, 0x3bb08` | at or above threshold: deny |
| `0x3bb04` | `0043102b` | `sltu $v0, $v0, $v1` | else `element+4 < element+12` |

There is also a BC/MC path when no station is present (`0x3bb1c..0x3bb28`):
`return local->aql_pending_bc_mc < local->aql_txq_limit_bc_mc`.
`ieee80211_next_txq` carries the same gate, so the census finds two reads:

| address | hex | instruction | role |
| :--- | :--- | :--- | :--- |
| `0x3cffc` | `8e660140` | `lw $a2, 0x140($s3)` | total AQL pending, `$s3` = local |
| `0x3d000` | `8e67013c` | `lw $a3, 0x13c($s3)` | `aql_threshold` |
| `0x3d004` | `00c7302b` | `sltu $a2, $a2, $a3` | `total_pending < aql_threshold` |
| `0x3d008` | `10c00006` | `beqz $a2, 0x3d024` | at or above: skip the strict per-AC test |

Below the threshold it tests `sltu(element+4, element+12)` and jumps to the deny
path at `0x3d0f4`. These two are the only threshold reads a census over every sized
`FUNC` symbol finds on a first-argument-derived base.

## 6. Claims

| id | grade | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | symbol offsets and sizes in section 3 |
| C2 | CONFIRMED | `aql_threshold = 0x13c`, anchored on `debugfs_create_u32` |
| C3 | CONFIRMED | `aql_txq_limit_low = 0x11c`, `aql_txq_limit_high = 0x12c`, from the reader's nine slots |
| C4 | CONFIRMED | `ieee80211_txq_may_transmit` and `ieee80211_sta_update_pending_airtime` contain 0 accesses to `local+0x13c` |
| C5 | CONFIRMED | the low and high limits are combined by `mul`/`srl`/`addu`, then one `sltu` against per-AC pending |
| C6 | CONFIRMED | exactly two reads of `aql_threshold` on a local-derived base exist, one in `ieee80211_txq_airtime_check` and one in `ieee80211_next_txq`, both testing `total_pending >= aql_threshold` |
| C7 | REFUTED | the premise that `aql_threshold` selects the low versus the high per-AC limit |
| C8 | INFERRED | the source-level expression shape `high[ac] + ((count * low[ac]) >> 1)` |
| C9 | UNKNOWN | runtime values of the count and the pending counters, and which branch the hardware takes |

## 7. Gaps

- The instruction order proves the arithmetic; it does not prove the source-level
  operand names. C8 stays inferred.
- The sta-side slots at `element+4`, `+8`, `+12` are proven to be four consecutive
  `u32` slots of a 40-byte per-AC element, and the slot at `element+0` is proven
  to be a signed deficit (sign test plus refill by `airtime_weight << 3`). The
  struct names of the other three slots are not claimed; this object carries no
  type information.
- The census that finds the two threshold reads is a candidate list, not a type
  proof: it attributes a read to the local struct when the base register descends
  from the first argument inside the current basic block. Both hits are in AQL
  scheduling code, but a function whose first argument is a different object could
  still slip in. The per-AC index scan is linear, so a witness after an epilogue
  register restore can be missed; the receipt reports only what it proves.
- The two threshold gates are the same test with different actions: at or above
  the threshold, `ieee80211_txq_airtime_check` returns false while
  `ieee80211_next_txq` jumps past the strict per-AC test. Which binds first depends
  on call order, a runtime property.
- The guard at the top of `ieee80211_txq_may_transmit`,
  `ieee80211_sta_update_pending_airtime` and `ieee80211_txq_airtime_check`
  dereferences `local+0x38` and tests bit 0 of a byte at `+0x41`. Its `C` name is
  not claimed. An `aql_disable` `.bss` parameter is also read and gated with
  `bgtz`, so its loaded default is a runtime property.
- The `-1` used when the per-AC list is empty makes the scaled term enormous under
  unsigned arithmetic, so the "below budget" branch is taken. That is what the
  instructions do; whether it is the intended design is not asserted here.
- This is a backports `6.12.52` mac80211, so any argument that reasons from a
  mainline 6.6 tree is invalid for this binary. Every structural statement above
  comes from these bytes. Static only: no runtime experiment here shows which
  branch executes, and the effect of writing the debugfs nodes is not measured.
