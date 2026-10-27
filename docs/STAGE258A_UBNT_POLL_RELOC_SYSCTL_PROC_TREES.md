<!-- doc-head: STAGE258A_UBNT_POLL_RELOC_SYSCTL_PROC_TREES.md preserved document content -->
<!-- /doc-head -->


# Stage 258A — `ctl_table` and `proc_ops` trees from relocations

- **Receipt**: [`artifacts/autoresearch/stage258a_ubnt_poll_reloc_sysctl_proc_trees.json`](../artifacts/autoresearch/stage258a_ubnt_poll_reloc_sysctl_proc_trees.json)
- **Tool**: `tools/re/dissect_stage258a_ubnt_poll_reloc_sysctl_proc_trees.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Two relocation classes, two structures

**`ctl_table`** lives in `.data`/`.rodata`. Every pointer field is an `R_MIPS_32` (type 2)
relocation whose **addend is the word content**, so the target is `symbol + word`. The array
stride for this kernel is **44 bytes**, established in Stage 81A-W4B and re-confirmed here by
the `memcpy` of `0x580 = 32 × 44`.

**`proc_ops`** are not stored in the tables; they are passed to
`proc_create_data(name, mode, parent, fops)`. The name (`$a0`) and fops (`$a3`) come from
`lui`/`addiu` pairs bound by `R_MIPS_HI16`/`LO16` in `.init.text` and `.text` — the same sound
join used in 257A.

## 1. Result

| Metric | Value |
| :--- | :-: |
| Images | 2 (WA, XC 8.7.25) |
| `ctl_table` arrays | **13** |
| `ctl_table` entries | **55** |
| Distinct `proc_handler` | **13** |
| Distinct `child` links | reported per entry |
| `proc_create_data` sites | **2** |
| **World-writable entries (`0666`)** | **0** |

Per image the numbers are identical: 13 tables, 55 entries, 2 `proc_create` calls.

## 2. What the tree looks like

The structure is two-level, which is why 13 arrays are found for 55 entries:

- a `dev` directory node (`ctl_name = 7 = CTL_DEV`, mode `0555`) whose `child` points at the
  next array;
- an `uph` directory node, also `0555`, whose `child` points at the leaf array;
- the leaf array holding the real knobs, with `proc_handler` and `maxlen` per entry.

That matches the Stage 81A-W4B finding, and this stage reproduces it from a different code path
(`.rel.data` rather than a hand-walked signature), which is independent confirmation.

## 3. Modes

**`CONFIRMED`: zero entries carry `0666`.** Consistent with W4A (32 registrations, 0
world-writable) and W4B (80 entries, 0 with `0666`).

The two `proc_create_data` sites are the ones previously identified as carrying mode `0`
(kernel default) — recorded here with their resolved name and fops rather than as "unresolved".

## 4. What this addsover W4B

W4B walked the tables with a **signature scan** over `.data`/`.rodata`: stride 44, name pointer
resolves to a string, mode in a plausible set, handler inside `.text`. That heuristic worked but
could in principle admit a false table.

This stage derives the same trees from **relocations only**: a field is a pointer because an
`R_MIPS_32` says so, and its target is `symbol + addend`. No plausibility filter is involved.
The two methods agreeing on 13 / 55 / 13 is a genuine cross-check.

## 5. Gaps

- **`UNKNOWN`** — the fops structure contents (`.open`, `.read`, `.write`, `.unlocked_ioctl`
  slots). Only the pointer is resolved, not the table behind it.
- **`KNOWN LIMIT`** — the `proc_create_data` mode is read from the nearest `addiu` to `$a1`,
  which can belong to an adjacent call in a tight sequence.
- **`KNOWN LIMIT`** — per-entry `proc_handler` semantics are not decoded; W4B established that
  the dominant handler is a name-dispatch `strcmp` chain, not `proc_dointvec`.
- **Not attempted** — dynamic validation.
