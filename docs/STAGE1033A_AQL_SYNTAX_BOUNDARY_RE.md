<!-- doc-head: Stage 1033A is the AQL write-syntax boundary: it re-measures the decisive artefacts in mac80211.ko, confirms the numeric index 0..3 form with a format string plus a decoded sltiu, refutes the access-category name form for input, and partitions fourteen layers into measured absent and not-in-binary; CONFIRMED_STATIC_BINARY, static only -->
<!-- /doc-head -->
# Stage 1033A - the AQL write-syntax boundary

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline
synthesis over one extracted `.ko`, two prior static receipts and one live read-only receipt. No
module was loaded, no radio was contacted, nothing was written to a device.

- **Receipt**: [`artifacts/autoresearch/stage1033a_aql_syntax_boundary_re.json`](../artifacts/autoresearch/stage1033a_aql_syntax_boundary_re.json)
- **Tool**: [`tools/re/dissect_stage1033a_aql_syntax_boundary_re.py`](../tools/re/dissect_stage1033a_aql_syntax_boundary_re.py)
- **Inputs**: Stage 1031A, Stage 1032A, Stage 955A

## The one question

Does the `aql_txq_limit` write path accept a numeric access-category index in 0..3, or the
access-category names `VO`, `VI`, `BE`, `BK`.

Answer carried by the binary: **numeric index**.

## Why that answer is allowed to be `CONFIRMED`

The honesty bar for this corpus is that a syntax may be called confirmed only if a format string or a
decoded comparison chain demonstrates the accepted token. A field name never qualifies. Two artefacts
are present, and both are re-measured here rather than copied from the earlier receipts:

| artefact | location | content | label |
| :--- | :--- | :--- | :--- |
| format string | `.rodata.str1.4+0x538c`, file offset 622044 | `%u %u %u` | CONFIRMED |
| call site | `.text+0x70e34` | `sscanf`, format resolved through `$5`, handler `aql_txq_limit.write` | CONFIRMED |
| conversion count test | `.text+0x70e3c` | `addiu $3,$0,3` then `bne`, so exactly 3 conversions | CONFIRMED |
| bound test | `.text+0x70e48` | `sltiu $3,$2,4`, so the parsed index is below 4 | CONFIRMED |

The handler is entered at `.text+0x70d54`, which is the `write` slot of the `file_operations` at
`.rodata+0x4430` belonging to the name `aql_txq_limit`. The chain from name to format string is
therefore closed: name, then fops, then handler, then format string, then bound.

Accepted input, as far as this module can say:

```
echo "<ac> <low> <high>" > /sys/kernel/debug/ieee80211/phyX/aql_txq_limit     # ac in 0..3
echo "mcast <u32>"       > /sys/kernel/debug/ieee80211/phyX/aql_txq_limit     # INFERRED BC/MC row
```

## Two vocabularies, one file

| surface | vocabulary | evidence | label |
| :--- | :--- | :--- | :--- |
| read and display | names `VO`, `VI`, `BE`, `BK`, `BC/MC` | read format string at `.rodata.str1.4+0x5110` | CONFIRMED |
| write | numeric index 0..3 | `%u %u %u` plus `sltiu` against 4 | CONFIRMED |

`VO`, `VI`, `BE`, `BK` each occur exactly once as a standalone string in the whole image, and zero
`sscanf` format strings contain any of them. The names exist, but only where they label rows in
output. A read-side label cannot accept input, so the name form is `REFUTED` for the write path.

This is the trap the stage exists to document: an operator reading the `AQL_phy0` dump sees `VO` and
`VI` and will reasonably try `echo "VO 1000 2000"`. The binary does not support that, and the same
binary printed the names that invite it.

## Boundary table

Four states, so that "not measured" is never read as "absent".

- `MEASURED` - an artefact in the image demonstrates the layer.
- `ABSENT` - the layer was searched and has zero artefacts.
- `NOT_IN_BINARY` - the layer is a runtime or hardware fact that a module image cannot carry.

| id | layer | status |
| :--- | :--- | :--- |
| L01 | ELF container and ABI | MEASURED |
| L02 | kernel and backports identity | MEASURED |
| L03 | distribution release label (`OpenWrt 24.10.4`) | ABSENT |
| L04 | AQL debugfs field names | MEASURED |
| L05 | name to `file_operations` to handler binding | MEASURED |
| L06 | read and display format strings | MEASURED |
| L07 | write format string for `aql_txq_limit` | MEASURED |
| L08 | numeric index bound check on the write path | MEASURED |
| L09 | AC name form on the write path | ABSENT |
| L10 | upstream handler symbol names | ABSENT |
| L11 | airtime check entry point | MEASURED |
| L12 | runtime field values 512, 3145728, 4096 | NOT_IN_BINARY |
| L13 | enforcement semantics per station or per TID | NOT_IN_BINARY |
| L14 | radio and hardware effect of a written value | NOT_IN_BINARY |

```
layers_total = 14   layers_measured = 8   layers_absent = 3   layers_not_in_binary = 3
```

The tool asserts that the three counts partition the fourteen rows before writing the receipt, so a
row can never be silently mislabelled as absent when it is merely unmeasured.

### The three absent layers

- **L03** `24.10.4` occurs 0 times and `OpenWrt` occurs 0 times. The confirming string would be a
  `.modinfo` entry carrying either token. The release label is `UNVERIFIED` from this binary and must
  come from elsewhere.
- **L09** the name form, refuted by the absence of any accepting format string.
- **L10** `aql_txq_limit_read` and `aql_txq_limit_write` each occur 0 times. Those upstream handler
  names do not exist here in any form, `REFUTED` for both, and no claim may quote them as present.

### The three layers outside the binary

- **L12** the values 512, 3145728 and 4096 are live facts. Stage 955A carries them inside the `raw`
  text of an `aqm` dump as `RW fq_memory_limit 3145728`, `RW fq_limit 512` and `R fq_flows_cnt 4096`.
  A numeric walk of that document finds no JSON number equal to any of the three, so a parser must
  read the text form.
- **L13** the image carries arrays and comparisons, but no statement of which queue the limit applies
  to at runtime.
- **L14** no channel, scheduler or hardware register is reachable from a relocatable object without a
  running radio.

## What the binary does not prove

| statement | status |
| :--- | :--- |
| a name form is *rejected at runtime* | not proven: the evidence is the absence of an accepting format string, not a decoded rejection |
| whitespace tolerance of the parse | not in this module: it belongs to the libc `sscanf` |
| whether the two limit arrays are per radio or per interface | not proven: only the array displacements were recovered |
| the runtime values behind the fields | outside the binary, carried from Stage 955A |
| what a written value does to a radio | outside the binary |

An absence of an accepting format string is weaker than a decoded rejection path, and it is labelled
as such rather than upgraded.

## Cross-check of the inputs

Every decisive fact was re-measured from the module, then compared with the two prior receipts. All
seven checks agree, which is what makes this stage a synthesis rather than a restatement.

| check | value |
| :--- | ---: |
| Stage 1031A receipt present | 1 |
| Stage 1032A receipt present | 1 |
| backports tag agrees at 98 occurrences | 1 |
| release label agrees at 0 and 0 | 1 |
| handler symbol names agree at 0 and 0 | 1 |
| syntax verdict agrees | 1 |
| airtime check symbol agrees at 2 name occurrences | 1 |
| `aqm` token agrees at 3 occurrences | 1 |

## Claims

| id | label | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | the write syntax is a numeric index in 0..3 followed by two unsigned decimals |
| C2 | REFUTED | the AC name form is not an accepted input |
| C3 | CONFIRMED | the read side is name based while the write side is index based |
| C4 | REFUTED | the `OpenWrt 24.10.4` label and the two upstream handler names are not carried by this module |
| C5 | UNKNOWN | which queue the limit applies to, and what a written value does to a radio |

## What this does not say

- Every `MEASURED` row is an artefact in the image; no row was validated on a running radio.
- Handler extents are bounded by stack-frame prologues, so a leaf handler without a frame would be
  attributed to the following function.
- The `mcast` branch is proven as a literal at the same handler, but its target row is inferred from
  the read table.

## Reproduction

```
python tools/re/dissect_stage1033a_aql_syntax_boundary_re.py
```

Two consecutive runs produce a byte-identical receipt. The receipt is written through a `decase`
normaliser that turns any object whose keys collide case-insensitively into a `{key, value}` list, and
the normaliser is self-tested on every run.
