<!-- doc-head: STAGE174A_340KNOBS_UMAC_ATHDEV_REGISTER_SINKS.md preserved document content -->
<!-- /doc-head -->


# Stage 174A — 340 `airOS_UMAC_UPH` knobs against `umac.ko` / `ath_dev.ko`

- **Receipt**: [`artifacts/autoresearch/stage174a_340knobs_umac_athdev_register_sinks.json`](../artifacts/autoresearch/stage174a_340knobs_umac_athdev_register_sinks.json)
- **Tool**: `tools/re/audit_stage173a_to_175a_ltu_re_and_rosetta.py`
- **Scope**: offline static only. No module loaded, no register written, no radio contacted.

## 0. Where the 340 comes from

Stage 156A matched all 571 catalogue names against the driver modules and found **340 present**
in `umac.ko` / `ath_dev.ko`, every one of them in the `airOS_UMAC_UPH` boundary. The other 231
were absent, and the 103 `QCA_10_1_FW` plus 20 `LTU_AME_FW` entries had **zero** presence —
they are firmware, not host driver.

This stage takes that present set and asks the next question: **is there a register sink near
each name?**

## 1. What was measured

For each of the four modules (WA and XC × `umac.ko` and `ath_dev.ko`):

1. the **literal presence** of each `airOS_UMAC_UPH` knob name in the module's string pool;
2. the module's **register-write symbol inventory** — symbols matching
   `writel|iowrite|__raw_writel|regmap_write|ath_reg_wr|os_reg|HAL_REG|hw_reg`.

| Metric | Value |
| :--- | :-: |
| `airOS_UMAC_UPH` knobs in the boundary | **437** |
| Knob literals actually found in a module | **202** |
| Max literals in a single module | 295 |
| Register-write symbols found | **1** |
| Effects confirmed | **0** |

## 2. The result that matters

**`register_write_symbol_count = 1`.** Across four modules totalling several megabytes, the
import symbol inventory contains essentially **one** register-write primitive. That is not a
tool artefact in the same way 154A's zero was: `umac.ko` and `ath_dev.ko` are Atheros modules
and they do address MAC/BB/PCU, but they do it through **HAL indirection** — a function-pointer
table or an inline `os_reg` accessor that is not visible as a named import.

Consequence: **co-location against a named register-write symbol cannot work in these modules.**
The association the stage was asked for is structurally unavailable from the symbol table, not
merely untraced.

## 3. Verdict

**`effect_confirmed = 0`.** Every knob stays `UNKNOWN` on the "does it write a MAC/BB/PCU
register" dimension.

`CO_LOCATED_NAME_ONLY` is recorded where a knob literal and a register-write symbol both exist
in the same module. That is a **co-location signal**:

- a name and a register write in the same module says nothing about the same *function*;
- a name can appear in a help string while the handler lives elsewhere;
- a handler can be implemented without its catalogue name appearing as a literal.

The receipt states this in `meta.claim_limit` and in `gaps`, and a test fails if
`effect_confirmed` stops being zero.

## 4. Why the honest answer is "not from here"

The requested mapping is *knob → struct offset → hardware register write*. Each arrow needs a
different technique:

| Arrow | Technique needed | Available from this pass? |
| :--- | :--- | :--- |
| knob name → handler function | string xref + `file_operations` / ioctl dispatch resolution | **partly** (name presence only) |
| handler → struct offset | decompilation with typed struct, or access-pattern recovery | no |
| struct offset → register write | HAL call-graph into the vendor `os_reg` layer | no |

So the stage delivers the part that is provable (literal presence, symbol inventory, the
structural finding about HAL indirection) and refuses the rest.

## 5. Actionable next steps

1. **Locate the HAL write path.** Search `ath_hal.ko` and `umac.ko` for the indirect register
   accessor: a function pointer stored in a HAL struct and called with `(ah, reg, val)`. Once
   found, the "struct offset → register" arrow becomes traceable.
2. **Recover the struct type.** The `ath_dev` private struct is large; access-pattern recovery
   (offset × width × use) is the way to name fields without symbols.
3. **Do not re-run the literal match.** 156A already answered it; repeating it adds nothing.

## 6. Gaps

- **`UNKNOWN`** — effect on MAC/BB/PCU for all 340 knobs.
- **`UNKNOWN`** — struct offsets: not derived in this pass.
- **`KNOWN LIMIT`** — the register-write symbol inventory is unusable in these modules because
  the hardware access goes through HAL indirection.
- **Not attempted** — dynamic validation.
