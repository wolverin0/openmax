<!-- doc-head: Stage 1031A recovers the write syntax of the mac80211 AQL debugfs fields from relocation-resolved format strings and a decoded bound check, and refutes the access-category name form for input; CONFIRMED_STATIC_BINARY, static only, no radio -->
<!-- /doc-head -->
# Stage 1031A - the actual debugfs write syntax of the AQL fields

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline, one
extracted `.ko`. No module was loaded, no radio was contacted, nothing was written to a device.

- **Receipt**: [`artifacts/autoresearch/stage1031a_mac80211_aql_debugfs_write_syntax_re.json`](../artifacts/autoresearch/stage1031a_mac80211_aql_debugfs_write_syntax_re.json)
- **Tool**: [`tools/re/dissect_stage1031a_mac80211_aql_debugfs_write_syntax_re.py`](../tools/re/dissect_stage1031a_mac80211_aql_debugfs_write_syntax_re.py)

## Question

What syntax does the `aql_txq_limit` debugfs file actually accept. A field name is not syntax. The
only artefacts that can decide the question are the format string handed to `sscanf` and the
comparison chain that bounds whatever that string parses.

## Binary

| Field | Value | Label |
| :--- | :--- | :--- |
| path | `artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko` | CONFIRMED |
| bytes | 829464 | CONFIRMED |
| sha256 | `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416` | CONFIRMED |
| class | ELF32, big-endian, `ET_REL`, machine `MIPS` | CONFIRMED |
| vermagic | `6.6.110 mod_unload MIPS32_R2 32BIT` | CONFIRMED |
| backports tag | `backports-6.12.52`, 98 occurrences | CONFIRMED |
| `24.10.4` | 0 occurrences | CONFIRMED |
| `OpenWrt` | 0 occurrences | CONFIRMED |

**The label "OpenWrt 24.10.4" is not verifiable from this binary.** Neither `OpenWrt` nor `24.10.4`
occurs anywhere in the image. The string that would have confirmed the label is a `.modinfo` entry
carrying either token; both are absent, so the release label stays `UNVERIFIED` here and must come
from an artefact that is not this module.

## The count trap

The operator measured `sscanf = 1` and `scnprintf = 1` in the whole module. That reproduces exactly,
and it does not mean one call site of each.

| Measurement | Value | Meaning |
| :--- | :--- | :--- |
| byte count of `sscanf` | 1 | the symbol name in `.strtab` |
| byte count of `scnprintf` | 1 | the tail of `vscnprintf`, suffix-merged in `.strtab` |
| `sscanf` call sites (`R_MIPS_26`) | 8 | relocations against the undefined symbol |
| `scnprintf` call sites (`R_MIPS_26`) | 383 | relocations against the undefined symbol |

`.strtab` is suffix-merged, so the symbol named `scnprintf` shares the bytes of `vscnprintf` and adds
no occurrence of its own; the same trick hides `sprintf` inside `kasprintf`. A byte count of these
words is a count of symbol-table names, never of format strings. Only the relocation counts are
syntax evidence, and they are 8 and 383.

`aql_txq_limit_read` and `aql_txq_limit_write` have **0** occurrences each, so those upstream handler
names do not exist in this build in any form. `REFUTED` for both.

## The field-name cluster

Six names sit contiguously in `.rodata.str1.4` and are created by a single `debugfs_create_file`
sequence inside `debugfs_hw_add` (`.text+0x711a0`, size 800).

| name | `.rodata.str1.4` | file offset | fops | read handler | write handler |
| :--- | ---: | ---: | ---: | ---: | ---: |
| `aql_enable` | 0x5428 | 622200 | 0x43ac | 0x6faa8 | 0x6fe74 |
| `aql_pending` | 0x5434 | 622212 | 0x44b4 | 0x6f97c | none |
| `aqm` | 0x5440 | 622224 | 0x45bc | 0x6fc50 | 0x70a50 |
| `airtime_flags` | 0x5444 | 622228 | 0x4538 | 0x6fb18 | 0x70790 |
| `aql_txq_limit` | 0x5454 | 622244 | 0x4430 | 0x6f8a0 | 0x70d54 |
| `aql_threshold` | 0x5464 | 622260 | created by `debugfs_create_u32` | - | - |

Handlers are recovered from the `.rodata` `struct file_operations`: `+0x08` is `read`, `+0x0c` is
`write`, and the in-place `R_MIPS_32` addend is the handler's `.text` offset. That binding is what
lets a format string be attributed to a file name at all.

## What each handler parses

| file | role | handler | format string | label |
| :--- | :--- | ---: | :--- | :--- |
| `aqm` | write | 0x70a50 | `fq_limit %u` | CONFIRMED |
| `aqm` | write | 0x70a50 | `fq_memory_limit %u` | CONFIRMED |
| `aqm` | write | 0x70a50 | `fq_quantum %u` | CONFIRMED |
| `aql_txq_limit` | write | 0x70d54 | `mcast %u` | CONFIRMED |
| `aql_txq_limit` | write | 0x70d54 | `%u %u %u` | CONFIRMED |
| unnamed handler | write | - | `limit %u %u %u` | CONFIRMED artefact, INFERRED owner |
| unnamed handler | write | - | `strict=%d` | CONFIRMED artefact, UNKNOWN owner |

`fq_limit`, `fq_memory_limit` and `fq_quantum` are the three fields that the live `aqm` dump marks
`RW`, and they are the only three names that appear as formats in that handler. That is a clean
independent check of the binding.

The two unattributed formats are reported as measured strings with no owner, because their call sites
fall outside every AQL handler extent. Guessing which file owns them would be the failure mode this
stage exists to avoid.

## The decoded chain

Inside the `aql_txq_limit` write handler, immediately after the `sscanf` call at `.text+0x70e34`
(format `.rodata.str1.4+0x538c`), the instructions are:

```
0x70e3c  addiu  $3, $0, 3      return value must equal 3 conversions
0x70e40  bne    $3, $2         otherwise reject
0x70e44  lw     $2, 0x1c($29)  the parsed ac
0x70e48  sltiu  $3, $2, 4      ac < 4
0x70e4c  beq    $0, $3         otherwise reject
```

The bound is a `sltiu` against 4, and the two arrays the handler then indexes sit at `+0x11c` and
`+0x12c` of the private structure, sixteen bytes apart, which is four 4-byte entries each. Both the
comparison and the geometry say four access categories indexed 0 to 3.

## Verdict

`CONFIRMED`: the accepted token for the access category is a **numeric index 0..3**, followed by two
unsigned decimals:

```
echo "<ac> <low> <high>" > /sys/kernel/debug/ieee80211/phyX/aql_txq_limit     # ac in 0..3
```

`REFUTED`: the name form `VO`, `VI`, `BE`, `BK`. The four tokens do exist in the image, but each one is
a standalone string used only as a row label inside the read format string
`"AC\tAQL limit low\tAQL limit high\nVO\t%u\t\t%u\n..."`. No `sscanf` format string in the whole module
contains any of the four. A label in a read table cannot accept input.

`INFERRED`: the same handler also accepts `mcast <u32>`, because a `mcast %u` format is resolved at a
call site inside that handler and the read table prints a matching `BC/MC` row. The literal is
`CONFIRMED`; the row it addresses is the inference.

## The stage 955A premise

The premise that the live receipt carries the fq defaults 512, 3145728 and 4096 is **CONFIRMED**, with
one qualification that matters for anyone parsing it.

```
RW fq_memory_limit 3145728
RW fq_limit 512
R  fq_flows_cnt 4096
```

Those lines live inside the `raw` string of an `aqm` debugfs dump. They are text, not JSON numbers: a
walk of every numeric leaf in that 54908-byte document finds none equal to 512, 4096 or 3145728. The
values are `RW` for the two limits, which is exactly why the write syntax in this stage matters.

## Claims

| id | label | claim |
| :--- | :--- | :--- |
| C1 | CONFIRMED | six AQL debugfs names exist as literals and are created by `debugfs_hw_add` |
| C2 | CONFIRMED | `aql_txq_limit` owns fops `0x4430`, write handler `.text+0x70d54` |
| C3 | CONFIRMED | the write syntax is three unsigned decimals with the first bounded to 0..3 |
| C4 | REFUTED | the AC name form is not accepted on the write path |
| C5 | REFUTED | `aql_txq_limit_read` and `aql_txq_limit_write` do not exist |
| C6 | UNKNOWN | the OpenWrt release label is not carried by this module |
| C7 | CONFIRMED | stage 955A carries the three fq values as raw debugfs text |

## What this does not say

- The handler block `.text+0x6f8a0..0x70f70` carries no `FUNC` symbol, so handlers are attributed by
  fops addend and string cross-reference, not by a C function name.
- The `mcast` branch is proven as a literal, but the store it feeds was not followed.
- Whitespace tolerance belongs to the libc `sscanf`, which is not in this module.
- Runtime values are carried from the earlier live receipt and were not re-measured here.

## Reproduction

```
python tools/re/dissect_stage1031a_mac80211_aql_debugfs_write_syntax_re.py
```

Two consecutive runs produce a byte-identical receipt. The receipt is written through a `decase`
normaliser that turns any object whose keys collide case-insensitively into a `{key, value}` list, and
the normaliser is self-tested on every run.
