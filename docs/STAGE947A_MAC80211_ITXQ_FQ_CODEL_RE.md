<!-- doc-head: Stage 947A static RE of the mac80211 iTXQ layer and its internal fair queue, and whether it needs the tc binary; CONFIRMED_STATIC_BINARY, offline, no radio contacted -->
# Stage 947A - mac80211 iTXQ and its internal fair queue, independent of `tc`

Evidence class: `CONFIRMED_STATIC_BINARY`. `radio_safety: static only`. Scope: static, offline, one
extracted `.ko`. No module was loaded, no radio was contacted, nothing was written to a device.

## Question

The stage claim is that mac80211 carries its own per-TID fair queue with CoDel-style dropping inside
the module, so that the queue discipline is available even where `/usr/sbin/tc` does not exist. The
measurement has to answer three things: is the iTXQ layer really there, is the fair queue really
inside the module, and is the fair queue a different artefact from the userspace `tc` binary.

## Binary

| Field | Value | Label |
| :--- | :--- | :--- |
| path | `artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko` | CONFIRMED |
| bytes | 829464 | CONFIRMED |
| sha256 | `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416` | CONFIRMED |
| ELF class / endianness | ELF32, big-endian | CONFIRMED |
| e_type / machine | `ET_REL` (relocatable module), MIPS | CONFIRMED |
| sections | 32, including `.symtab`, `.strtab`, `__ksymtab`, `__ksymtab_strings` | CONFIRMED |
| defined symbols (`st_shndx` not zero) | 1012 | CONFIRMED |
| exported symbols (`__ksymtab_strings`) | 145 | CONFIRMED |
| vermagic (`.modinfo`) | `6.6.110 mod_unload MIPS32_R2 32BIT` | CONFIRMED |

The string `backports-6.12.52/include/net/fq_impl.h` sits in `.rodata.str1.4`, which fixes the
backports tree the module was built from. Label: CONFIRMED for the string, INFERRED for the tree.

## Measurement 1 - the iTXQ entry points

Eight expected entry points, counted from `.symtab`, each with the `st_size` of its function:

| Symbol | Present | `st_size` | Exported |
| :--- | ---: | ---: | ---: |
| `ieee80211_tx_dequeue` | 1 | 3528 | 1 |
| `ieee80211_txq_may_transmit` | 1 | 904 | 1 |
| `ieee80211_txq_setup_flows` | 1 | 608 | 0 |
| `ieee80211_txq_teardown_flows` | 1 | 164 | 0 |
| `ieee80211_txq_get_depth` | 1 | 88 | 1 |
| `ieee80211_txq_airtime_check` | 1 | 176 | 1 |
| `ieee80211_txq_set_params` | 1 | 116 | 0 |
| `ieee80211_handle_wake_tx_queue` | 1 | 168 | 1 |
| `ieee80211_txq_schedule_start` | 1 | 236 | 1 |

`itxq_symbols_present = 8`, `itxq_symbols_expected = 8`. Verdict: CONFIRMED, the iTXQ layer is
compiled into this module. `ieee80211_txq_schedule_start` is tracked as the ninth entry point and is
also present at 236 bytes, exported. The two largest bodies are the dequeue path (3528 bytes) and the
transmit-permission path (904 bytes), which is the expected shape of a queue layer that does real
work rather than a thin wrapper.

## Measurement 2 - the fair queue has no symbol, and that is expected

Six helper names were looked up and all six are absent: `fq_tin_dequeue`, `fq_flow_dequeue`,
`fq_tin_enqueue`, `codel_dequeue`, `fq_codel_dequeue`, `fq_codel_enqueue`.
`fq_tin_dequeue_present = 0`, `fq_symbols_present = 0`. Label: CONFIRMED that no such symbol exists.

This is not evidence of absence. mac80211 compiles its fair queue from
`include/net/fq_impl.h` as `static inline` code, so the helpers are inlined into their callers and
never reach `.symtab`. The module image carries the header path string itself
(`backports-6.12.52/include/net/fq_impl.h`), which is the shape left behind by code compiled from
that header.

## Measurement 3 - the vocabulary that proves the fair queue is inside

Raw byte counts over the whole module image:

| Token | Hits | What it is | Label |
| :--- | ---: | :--- | :--- |
| `codel` | 0 | no CoDel name anywhere in the module | CONFIRMED (absent) |
| `fq_` | 13 | fair-queue parameter names and the `fq_impl.h` path | CONFIRMED |
| `flows` | 5 | `fq_flows_cnt`, `new-flows` TXQ stats strings, two symbol names | CONFIRMED |
| `quantum` | 2 | `fq_quantum` parameter and its format string | CONFIRMED |
| `txq` | 22 | iTXQ symbol names and strings | CONFIRMED |
| `airtime` | 16 | AQL and airtime-fairness symbols and strings | CONFIRMED |
| `deficit` | 0 | lowercase form absent | CONFIRMED (absent) |
| `aql` | 6 | four AQL field names plus the debugfs group name | CONFIRMED |
| `AQL` | 3 | two debugfs report headers | CONFIRMED |

The decisive string is the debugfs parameter table compiled out of `fq_impl.h`:

```
access name value\nR fq_flows_cnt %u\nR fq_backlog %u\nR fq_overlimit %u\nR fq_overmemory %u\n
R fq_collisions %u\nR fq_memory_usage %u\nRW fq_memory_limit %u\nRW fq_limit %u\nRW fq_quantum %u\n
```

A module that never instantiated a fair queue has no reason to carry `fq_quantum`, `fq_limit`,
`fq_memory_limit`, `fq_flows_cnt` and `fq_collisions` as exported debugfs knobs. Label: CONFIRMED
that the fair-queue state machine is compiled in. `fq_impl_header_string = 1` and
`fq_debugfs_table_string = 1`.

Caveat on attribution, stated plainly: the strings live inside relocation-referenced string groups
(`$LC` locals addressed by HI16/LO16 pairs), and the exact byte offset inside a group is carried in
the LO16 addend. This stage does not decode MIPS instructions, so the attribution is group level, not
byte level. Label: INFERRED for "this string is used by function X", CONFIRMED for "this string is
inside the module image".

## The positive evidence, stated the way it must be stated

The positive evidence for the internal queue is `ieee80211_txq_setup_flows` plus the `fq_` and sysfs
strings. It is *not* the dequeue helper names. `ieee80211_txq_setup_flows` is a 608-byte function
that only exists if there is a per-TID flow table to set up, and the `fq_*` debugfs table only exists
if that table is a `struct fq`. The dequeue helpers are header-inline and have no symbol, so any
search that requires `fq_tin_dequeue` to appear in `.symtab` will wrongly conclude the feature is
missing.

## Does the integrated FQ-CoDel need `/usr/sbin/tc`

| Fact | Value | Label |
| :--- | ---: | :--- |
| `tc` binary in corpus | 8 | CONFIRMED |
| reference `tc` | `artifacts/firmware_re_xc_ltu/wa_8725_rootfs/bin/tc`, 229032 B, sha256 `f8c7bca2...34cd6` | CONFIRMED |
| `fq_codel` hits in the reference `tc` | 3 | CONFIRMED |
| `mac80211` hits in the reference `tc` | 0 | CONFIRMED |
| `mac80211` hits summed over all 8 `tc` binaries | 0 | CONFIRMED |
| `sch_fq_codel.ko` in the 1163-module corpus | 0 | CONFIRMED |

Reading:

1. `tc` never references mac80211. It is a netlink client that asks the kernel to attach a qdisc to a
   netdev; it does not link against, nor call into, the mac80211 module. Label: CONFIRMED.
2. mac80211 carries its own fair queue keyed on the iTXQ/`fq_tin` structure, which is not a netdev
   qdisc at all. The two artefacts therefore cannot be the same code path. Label: CONFIRMED.
3. Therefore the internal fair queue does not require the `tc` binary to exist. Removing
   `/usr/sbin/tc` from an image cannot remove the mac80211 queue layer. Label: CONFIRMED for the
   static dependency question.
4. Whether a *netdev qdisc* named `fq_codel` can still be attached without `tc` is a different
   question: the qdisc is selected by `net.core.default_qdisc` and attached by the kernel, and the
   corpus contains no `sch_fq_codel.ko`, so on this box the qdisc would have to be built into the
   kernel. Label: UNKNOWN. It is not decided by this stage.
5. Whether the internal queue is *active* at runtime depends on the driver using iTXQ. Label:
   UNKNOWN, a runtime fact.

The honest summary sentence is: mac80211's fair queue is internal and independent of `tc`
(CONFIRMED); the CoDel *stage* of that queue is not evidenced by any name in this module, so calling
the whole thing "FQ-CoDel" is an INFERRED extension of a CONFIRMED fair queue.

## Verdicts

| ID | Claim | Label |
| :--- | :--- | :--- |
| C1 | 8 of 8 iTXQ entry points are defined with nonzero `st_size` | CONFIRMED |
| C2 | the fair queue is compiled in (`fq_impl.h` path string plus the `fq_*` debugfs table) | CONFIRMED |
| C3 | the fair-queue helpers have zero symbols, as expected for header-inline code | CONFIRMED |
| C4 | a CoDel stage is present | INFERRED (zero `codel` hits; rests on `fq_impl.h` alone) |
| C5 | `tc` is a separate artefact that never references mac80211 | CONFIRMED |
| C6 | the internal queue is active on a running radio | UNKNOWN |
| C7 | `ieee80211_txq_setup_flows` exists without any per-TID flow table | REFUTED (it is a 608-byte setup body) |

## Gaps

- The fair queue is header-inline, so no per-function size can be reported for it and its code cannot
  be located by symbol.
- No disassembly was performed. The per-TID flow count, the `fq_quantum` value, and any CoDel target
  or interval are not extracted.
- The CoDel stage has zero naming evidence (`codel = 0`); the claim is carried by `fq_impl.h` and by
  the expectation that mac80211 uses the paired implementation, not by a measured byte pattern.
- String to function attribution is group level only, because MIPS HI16/LO16 addends were not decoded.
- `sch_fq_codel` may be built into the kernel; absence of `sch_fq_codel.ko` in the corpus is not proof
  that the qdisc is unavailable.
- No dynamic validation. Nothing was loaded and no radio was contacted.

## Files

- `tools/re/dissect_stage947a_mac80211_itxq_fq_codel_re.py`
- `artifacts/autoresearch/stage947a_mac80211_itxq_fq_codel_re.json`
- `docs/STAGE947A_MAC80211_ITXQ_FQ_CODEL_RE.md`
