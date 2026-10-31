<!-- doc-head: Stage 1032A dissects ieee80211_txq_airtime_check as a real symbol with st_size 176, inventories the aqm airtime_flags and aql field names with exact offsets, and refutes the claim that aql_disable is an exported symbol; CONFIRMED_STATIC_BINARY, static only -->
<!-- /doc-head -->
# Stage 1032A - `ieee80211_txq_airtime_check` and the AQM field inventory

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline, one
extracted `.ko`. No module was loaded, no radio was contacted, nothing was written to a device.

- **Receipt**: [`artifacts/autoresearch/stage1032a_mac80211_aqm_and_airtime_check_re.json`](../artifacts/autoresearch/stage1032a_mac80211_aqm_and_airtime_check_re.json)
- **Tool**: [`tools/re/dissect_stage1032a_mac80211_aqm_and_airtime_check_re.py`](../tools/re/dissect_stage1032a_mac80211_aqm_and_airtime_check_re.py)

## Question

Is the airtime check a real symbol or a string artefact, what exactly does it read, and which
`aqm`, `airtime_flags` and `aql_*` field names exist at which offsets.

## The symbol

| Field | Value | Label |
| :--- | :--- | :--- |
| name | `ieee80211_txq_airtime_check` | CONFIRMED |
| symbol index | 1388 | CONFIRMED |
| `st_value` | `0x3ba7c` (244348) | CONFIRMED |
| `st_size` | 176 bytes | CONFIRMED |
| section | `.text` | CONFIRMED |
| `st_info` binding | LOCAL | CONFIRMED |
| in `__ksymtab_strings` | yes | CONFIRMED |

So the answer to the first question is yes: it is a defined function of 176 bytes, and the name is an
anchor that can be used to address it.

The two occurrences of the name in the image are **metadata, not code**: one sits in
`__ksymtab_strings` at file offset 638188 and one in `.strtab` at 686011. A count of 2 therefore does
not mean two definitions, and does not mean two call sites.

One oddity is reported and not explained: `st_info` says LOCAL while the name is in the export
table. The binary carries both facts, so both are recorded and the reason is left `UNKNOWN`.

## What the function reads

The whole 176-byte extent is decoded in the receipt. The shape is:

| offset | what it does | label |
| ---: | :--- | :--- |
| `0x3ba7c` | `lw $2,0x38($4)` then `lhu`, tests bit 0 of a halfword at `+0x41` of the first argument | CONFIRMED |
| `0x3ba84` | `andi $2,$2,1` - the mask is 1 | CONFIRMED |
| `0x3ba8c` | `lui`/`lw` of the `aql_disable` global, `bgtz` returns early when it is set | CONFIRMED |
| `0x3ba9c` | reads `+0x4`, `+0x8`, `+0x9` of the second argument | CONFIRMED |
| `0x3bac4` | `addiu` with displacement `0xf9dc` (-1572) | CONFIRMED |
| `0x3bad4` | `lw` with displacement `0xf9e0` (-1568) | CONFIRMED |
| `0x3bb04` | `lw` with displacement `0xf9e4` (-1564) | CONFIRMED |
| `0x3bb18` | returns 1 | CONFIRMED |
| `0x3bb0c` | returns 0 | CONFIRMED |

The three negative displacements are consecutive 4-byte slots, compared with `sltu`, which is the
shape of a per-queue limit comparison. Which structure owns those slots is not established from the
image alone, so the slots are reported positionally and the ownership stays `UNKNOWN`.

The relocation census inside the extent has exactly two entries, both against one data object:

```
0x3ba8c  R_MIPS_HI16  aql_disable  (.bss)
0x3ba90  R_MIPS_LO16  aql_disable  (.bss)
```

`CONFIRMED`: the airtime check consumes the AQL disable flag directly. It does not call into a
separate AQL module, because there is no call relocation at all in the extent.

## Correction to Stage 950A

Stage 950A described `aql_disable` as "one of its exported symbols". That is `REFUTED`:

| test | result |
| :--- | :--- |
| `aql_disable` in `.symtab` | yes, index 1152 |
| symbol type | OBJECT (`st_info` type 1), not FUNC |
| section | `.bss` |
| size | 4 bytes |
| in `__ksymtab_strings` | no |
| `parm=aql_disable` in `.modinfo` | no |

It is a 4-byte boolean in `.bss`, used inside the module. It cannot serve as a cross-module anchor,
and the "disable path on the iTXQ layer" phrasing built on it does not follow.

## Field inventory

Every name below is a NUL-terminated string, with its section and both offsets. All of them live in
`.rodata.str1.4`.

`aql_*` names, 5 entries:

| name | offset | file offset |
| :--- | ---: | ---: |
| `aql_enable` | 0x5428 | 622200 |
| `aql_pending` | 0x5434 | 622212 |
| `aql_txq_limit` | 0x5454 | 622244 |
| `aql_threshold` | 0x5464 | 622260 |
| `aql` | 0x7698 | 631016 |

`aqm`, 3 occurrences (`aqm_token_hits = 3`, which reproduces the operator count):

| offset | file offset | role |
| ---: | ---: | :--- |
| 0x5440 | 622224 | debugfs file name created by `debugfs_hw_add` |
| 0x768c | 631004 | second literal, `INFERRED` to be the same file name in another table |
| 0x7c38 | 632456 | third literal, `UNKNOWN` owner |

`airtime_flags`, 1 occurrence:

| name | offset | file offset |
| :--- | ---: | ---: |
| `airtime_flags` | 0x5444 | 622228 |

Four `aql_*` debugfs names plus one bare `aql` token, three `aqm` tokens and one `airtime_flags` token
is the complete inventory of these tokens as strings. The uppercase forms (`AQL`, `AQM`) do not appear
as field names; they appear only inside the human-readable read tables, which is a separate artefact
and is measured in Stage 1031A.

## Symbols containing `aql`

| symbol | section | value | size | type | exported |
| :--- | :--- | ---: | ---: | :--- | ---: |
| `aql_disable` | `.bss` | 0 | 4 | OBJECT | no |

That is the only `aql`-named symbol in the module. The exported airtime symbols are
`ieee80211_sta_register_airtime`, `ieee80211_txq_airtime_check`, `ieee80211_calc_rx_airtime` and
`ieee80211_calc_tx_airtime`; none of them carries an `aql` name.

## Cross-check against the live receipt

The stage 955A receipt is consulted read-only, for presence only:

| check | value |
| :--- | ---: |
| `AQL limit low` read table present | 1 |
| `fq_flows_cnt` aqm read table present | 1 |
| access-category rows found | `VO`, `VI`, `BE`, `BK`, `BC/MC` |

The live `AQL_phy0` dump is an AC table with those five rows, which matches the read format string
recovered in Stage 1031A from `.rodata.str1.4+0x5110`. Two independent artefacts agree, and that is
the strongest statement this stage makes about the read side.

## Claims

| id | label | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | `ieee80211_txq_airtime_check` is a 176-byte LOCAL function at `.text+0x3ba7c` |
| C2 | CONFIRMED | the function's only data relocation is against `aql_disable` in `.bss` |
| C3 | CONFIRMED | the two image occurrences of the name are `__ksymtab_strings` and `.strtab` metadata |
| C4 | CONFIRMED | `aqm` has three occurrences and all three are in `.rodata.str1.4` |
| C5 | UNKNOWN | why a LOCAL symbol appears in the export name table |
| C6 | REFUTED | `aql_disable` is not an exported symbol and not a module parameter |
| C7 | UNKNOWN | which structure owns the three negative displacement slots |

## What this does not say

- The body is decoded but not type-recovered: the three 4-byte slots are described positionally.
- No caller of the airtime check is resolved here, so the check's place in the transmit path is not
  established by this stage.
- The field inventory is string level: it proves names and offsets, not the order of the values the
  read handler prints.
- The live receipt is cross-checked for presence, not re-read for values.

## Reproduction

```
python tools/re/dissect_stage1032a_mac80211_aqm_and_airtime_check_re.py
```

Two consecutive runs produce a byte-identical receipt. The receipt is written through a `decase`
normaliser that turns any object whose keys collide case-insensitively into a `{key, value}` list, and
the normaliser is self-tested on every run.
