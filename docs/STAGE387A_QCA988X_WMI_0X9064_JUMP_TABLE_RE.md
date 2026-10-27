<!-- doc-head: STAGE387A_QCA988X_WMI_0X9064_JUMP_TABLE_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 387A — `WMI_UBNT_CMDID`, 0x9064 / 0x9070 and the 51-entry jump table

- **Receipt**: [`artifacts/autoresearch/stage387a_qca988x_wmi_0x9064_jump_table_re.json`](../artifacts/autoresearch/stage387a_qca988x_wmi_0x9064_jump_table_re.json)
- **Tool**: [`tools/re/qca988x_wmi_0x9064_51entry_jump_table_re.py`](../tools/re/qca988x_wmi_0x9064_51entry_jump_table_re.py)
- **Scope**: offline static. No firmware loaded, no module loaded, no radio contacted.

## 0. The trap this stage has to survive

Stage 372A established a **dense slot array** in `umac.ko`: id `0x9000 + 4k`, 8 bytes per entry,
every entry trailing `0x00000102`. Re-measured here, the array is **larger than the slice seen
then**:

| Property | Value |
| :--- | :--- |
| start | `0x239f70` |
| entries | **432** |
| id range | `0x9000` … `0x96bc` |
| trailing word | `0x00000102` (constant) |

**432 slots means essentially the whole `0x90xx` command space is enumerable.** Any `0x90xx`
constant will be present in `umac.ko` whether or not it means anything. So the ids cannot be used
as evidence on their own, and this tool classifies every aligned hit as inside or outside the run.

| Id | Total hits | Aligned | Aligned offset | Slot index | Inside dense run |
| :--- | :-: | :-: | :--- | :-: | :-: |
| `0x9064` | 12 (11 + 1) | 1 | `0x23a038` | **25** | **yes** |
| `0x9070` | 1 | 1 | `0x23a050` | **28** | **yes** |

**`REFUTED`**: neither id appears outside the dense array. In `umac.ko` the counts are
exactly `0x239f70 + 8×25` and `0x239f70 + 8×28`. **`id_hits_outside_dense_run = 0`.**

The blob adds nothing: `0x9064` has **0** occurrences in either endianness, `0x9070` has **1**,
little-endian only, with no surrounding structure.

## 1. The claimed jump table address is outside every window

`0x009b2037` was checked against all four readings of the `SGMT` base field:

| Segment | Base reading | Window | Contains `0x009b2037` |
| :-: | :--- | :--- | :-: |
| 4 | BE `0x00009800` | `0x00009800`..`0x0000b3e4` | no |
| 4 | LE `0x00980000` | `0x00980000`..`0x00981be4` | no |
| 3 | BE `0x00009800` | `0x00009800`..`0x00039ba1` | no |
| 3 | LE `0x00980000` | `0x00980000`..`0x009b03a1` | **no** |

The widest window is segment 3 under the LE reading, and it ends at **`0x009b03a1`**. The target
is **7,318 bytes past the end** (`0x1c96`).

**`REFUTED`**: the address cannot be indexed in this container under any self-consistent reading
of its own header.

The jump target fares the same: `0x009b5c02` is also outside every window, by **22,625 bytes**.

**`CONFIRMED`**: no 51-entry pointer run exists either. The longest run of consecutive aligned
words that look like in-firmware pointers is **below 51** in both segments, so even ignoring the
address there is no candidate table of that shape.

## 2. The namespace is real, the exact name is not

`umac.ko` carries **6 hits** for `WMI_UBNT`, and the name table spells them out:

```
WMI_UBNT_POLL_CMDID          WMI_REQ_UBNT_STATS_CMDID
WMI_UBNT_PDEV_FAILURE_EVENTID   WMI_UBNT_POLL_EVENTID
WMI_UBNT_STATS_EVENTID          WMI_UBNT_PEER_ADD_EVENTID
WMI_UBNT_PEER_DEL_EVENTID
```

**`CONFIRMED`**: a `WMI_UBNT_*` command/event namespace exists, with two command ids
(`POLL`, `REQ_STATS`) and five event ids.

**`REFUTED`**: the literal `WMI_UBNT_CMDID` does **not** exist. The stage names a single tunnel
command; the firmware names a set of specific ones. Those are different claims.

## 3. The subcommand handlers are real — in the other module

The stage names `0x17 set_txq_param` and `0x1e set_rate_override`. The **names are real symbols**,
and they are in `ubnt_poll_host.ko`, not in `umac.ko`:

| Symbol | Hits |
| :--- | :-: |
| **`ubnt_poll_host_set_txq_param`** | 1 |
| **`ubnt_poll_host_set_rate_override`** | 1 |
| `txq_param` (substring total) | 2 |
| `rate_override` (substring total) | 1 |

**`CONFIRMED`**: `ubnt_poll_host_set_txq_param` and `ubnt_poll_host_set_rate_override` are
exported function symbols. The two handlers the stage describes exist.

**`UNKNOWN`**: that they are reached by subcommand ids `0x17` and `0x1e`. No subcommand dispatch
table was found, and the numeric ids are not bound to these symbols anywhere in the receipt.
Handler existence and opcode assignment are separate facts.

## 4. What is established

| Claim | Status |
| :--- | :--- |
| `0x9064` / `0x9070` are slots 25 / 28 of a 432-entry dense array | **CONFIRMED** |
| either id appears outside that array | **REFUTED** (0 hits outside) |
| a `WMI_UBNT_*` cmd/event namespace exists in `umac.ko` | **CONFIRMED** |
| a single `WMI_UBNT_CMDID` symbol exists | **REFUTED** |
| `ubnt_poll_host_set_txq_param` / `set_rate_override` are real symbols | **CONFIRMED** |
| `0x17` → `set_txq_param`, `0x1e` → `set_rate_override` | **UNKNOWN** |
| a 51-entry jump table at `0x009b2037` | **REFUTED** (address out of range, no 51-run) |
| subcommand `0x17` jumps to `0x009b5c02` | **REFUTED** (target also out of range) |

## 5. Gaps

- **`UNKNOWN`** — the real SGMT load address. The base field reads `0x00980000` under both
  endiannesses, which is suspicious, and the u32 at payload offset 12 (148 / 5,484) is
  uninterpreted. The windows used here are the widest available, not proven mappings.
- **`UNKNOWN`** — whether a jump table exists elsewhere in the blob under a different encoding.
- **`UNKNOWN`** — the opcode numbers for `set_txq_param` and `set_rate_override`.
- **`UNKNOWN`** — what `WMI_UBNT_POLL_CMDID` carries, and how it relates to the `uph` TDMA poll.
- **Known limit** — an id present in an enumeration is not a command.
- **Not attempted** — Xtensa disassembly, dynamic validation.
