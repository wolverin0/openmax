<!-- doc-head: STAGE173A_LTU_MOVW_MOVT_AND_HTCOMM_SWITCH_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 173A — ARM `movw`/`movt` register constants and the HT_COMM compare chain

- **Receipt**: [`artifacts/autoresearch/stage173a_ltu_movw_movt_and_htcomm_switch_re.json`](../artifacts/autoresearch/stage173a_ltu_movw_movt_and_htcomm_switch_re.json)
- **Tool**: `tools/re/audit_stage173a_to_175a_ltu_re_and_rosetta.py`
- **Scope**: offline static only. No module loaded, no register read, no radio contacted.

## 0. What this closes

Stage 154A declared a hard gap: the AME modules are **ARM little-endian**, and the register
sweep implemented only the MIPS `lui`/`addiu` idiom, so `register_constants` was **0 by
construction**. That zero was explicitly marked as "not evidence that no register is
addressed". This stage implements the ARM idiom and fills the column.

## 1. Premise correction

**`eab_driver.ko` does not exist** in either LTU image. The audited set is:

| Image | Modules |
| :--- | :--- |
| `AF-LTU.v2.4.2` | `ame_core.ko`, `ame_dev.ko`, `cds_mac_mod.ko` |
| `AF-LTU-Rocket.v2.4.2` | same three |

`CONFIRMED` by directory listing of `lib/modules/3.14.65/`. Nothing is reported for a module
that is not present.

## 2. ARM constant recovery

The ARM idiom is a pair:

```
movw rX, #lo        ; 0xE300_0000 | imm4<<16 | rd<<12 | imm12
movt rX, #hi        ; 0xE340_0000 | ...
```

`addr = (hi << 16) | lo`. A pair is kept only when both instructions target the same register
and the result lands inside a register window (`0x18xxxxxx`–`0x1Bxxxxxx`, `0x1Axxxxxx`,
`0x2xxxxxxx`, `0x3xxxxxxx`).

| Module | Bytes | `movw`/`movt` pairs | Register constants |
| :--- | :-: | :-: | :-: |
| `ame_core.ko` (LTU) | 3,282,052 | **44,067** | **7** |
| `ame_core.ko` (Rocket) | 3,318,764 | **44,493** | **7** |
| `ame_dev.ko` (both) | 298,760 | 2,276 | 0 |
| `cds_mac_mod.ko` (LTU) | 139,672 | 76 | 0 |
| `cds_mac_mod.ko` (Rocket) | 145,332 | 79 | 0 |

**Totals: 93,267 pairs, 14 register constants.** All 14 live in `ame_core.ko`, which is
consistent with that module being the radio core rather than an interface shim.

**What this does not prove.** A `movw`/`movt` pair materialises a constant; it does not show
the value is dereferenced as a register. The same idiom builds masks, sizes and magic numbers.
The 14 are addresses in a register window, not fourteen verified MMIO accesses.

## 3. HT_COMM compare chain

`ubnt_poll_host.ko` (WA and XC 8.7.25) was scanned for the small-immediate compare chain that
would implement an opcode dispatch: `slti`/`sltiu` with a bound in 1..21, `beq`/`bne` with an
immediate in 0..20, and `addiu reg,$zero,N` in 0..20.

**Result: 20 distinct values in the 0..20 range, in both images.** That is consistent with a
`HT_COMM` family of 21 opcodes, but it is a histogram, not a switch table.

**Why it is not a table.** A constant in 0..20 can be:

- an opcode in a compare chain;
- an array index into a message-name table;
- a size, a count, or a loop bound.

Separating those requires following the branch targets into a jump table and matching each arm
to a handler. This stage does not do that, and the receipt says so in `gaps`.

## 4. What changed versus 154A

| Claim in 154A | After 173A |
| :--- | :--- |
| `register_constants = 0` for all AME modules | **14 across the set**, all in `ame_core.ko` |
| "zero by construction, needs a movw/movt sweep" | sweep implemented; the caveat is discharged |
| HT_COMM reported as an immediate histogram only | same histogram, now with the branch-form breakdown |

## 5. Gaps

- **`UNKNOWN`** — whether the 14 recovered constants are dereferenced as MMIO. Proving that
  needs each site traced into a load/store.
- **`UNKNOWN`** — the actual `HT_COMM` switch table. The compare chain is located; the arm-to-
  handler mapping is not resolved.
- **`UNKNOWN`** — `ame_dev.ko` and `cds_mac_mod.ko` show **0** register constants. That may be
  real (they may use a HAL indirection) or a limitation of the window list. Not claimed either
  way.
- **Not attempted** — dynamic validation. Nothing was loaded or executed.
