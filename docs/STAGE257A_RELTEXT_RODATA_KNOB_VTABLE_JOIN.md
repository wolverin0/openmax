<!-- doc-head: STAGE257A_RELTEXT_RODATA_KNOB_VTABLE_JOIN.md preserved document content -->
<!-- /doc-head -->


# Stage 257A — exact `.rel.text` → `.rodata` join for the knobs

- **Receipt**: [`artifacts/autoresearch/stage257a_reltext_rodata_knob_vtable_join.json`](../artifacts/autoresearch/stage257a_reltext_rodata_knob_vtable_join.json)
- **Tool**: `tools/re/dissect_stage257a_reltext_rodata_knob_vtable_join.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Why this stage exists

254A, 255A and 256A all returned **0 vtable attributions** from a low-16-bit heuristic that was
`REFUTED` as an identifier. This stage replaces it with the sound join.

In an `ET_REL` module a reference to a `.rodata` literal is a **relocation pair**:

```
R_MIPS_HI16 (5) on the lui    -> symbol index + high 16 bits
R_MIPS_LO16 (6) on the addiu  -> low 16 bits (addend)
rodata_offset = st_value(symbol) + (hi << 16) + sign_extend16(lo)
```

The pair is bound to a **symbol index**, so no 16-bit collision is possible.

## 1. Relocation inventory (the evidence that the join can work)

| Module | `.rel.text` entries | HI16 | LO16 | HI16 → `.rodata` |
| :--- | :-: | :-: | :-: | :-: |
| `umac.ko` | **45,722** | 9,003 | 12,974 | **4,544** |
| `ubnt_poll_host.ko` | 2,370 | 557 | 533 | 380 |

The relocations are plentiful and mostly point at `.rodata`. The earlier zero was not a data
problem.

## 2. Two defects fixed in the join

1. **`st_value` was omitted.** The immediates carry only the addend relative to the symbol; the
   object's offset inside its section is `st_value`. Without it the computed address is wrong
   for every non-zero symbol.
2. **Pairing was global per register, not positional.** A dict keyed by register holds the
   *last* HI16 seen, so every LO16 bound to the wrong `lui`. The fix pairs each LO16 with the
   nearest preceding HI16 on the same register **within 8 instructions**, requiring the same
   symbol index.

Defect 2 alone accounted for the difference between **2** and **106** attributions.

## 3. Result

| Module (per image) | Knobs with a literal | **Attributed** | Reaching a 253A slot |
| :--- | :-: | :-: | :-: |
| `WA/XC:umac.ko` | 320 | **41** | **0** |
| `WA/XC:ath_dev.ko` | 6 | **0** | **0** |
| `WA/XC:ubnt_poll_host.ko` | 33 | **12** | **0** |
| **Total (both images)** | 357 | **106** | **0** |

**`CONFIRMED`: 106 exact attributions**, 53 per image, split 41 / 0 / 12.

## 4. The 0 vtable is now a real result

This is the third time the series reports zero vtable reachability, but it is the **first time
it is meaningful**, because the function attribution is now sound.

**`CONFIRMED`**: none of the 53 functions that reference a knob literal in one image dispatches
through any of the eleven 253A slots `{4, 8, 156, 160, 164, 204, 208, 296, 300, 396, 520}`.

That changes the diagnosis. The earlier hypothesis was "the join is broken, so we cannot tell".
The correct reading now is: **the knob-referencing functions and the 253A vtable dispatchers are
different populations.** The 253A slots were recovered from `ath_attach` / `ol_ath_attach` and
their callees; the knob literals are referenced from other code.

## 5. What that implies for 174A

The 340 knobs were expected to reach the HAL through the vtable. This stage shows that the
functions referencing them do not. Two explanations remain:

1. the knobs reach hardware through a **different** mechanism (a HAL call that is not one of the
   eleven slots, or a direct `writel` the 253A scan did not cover), or
2. the literal is referenced from a table/descriptor rather than from the handler that performs
   the write.

Distinguishing them is the next question, and it is now a narrow one rather than a blind one.

## 6. Gaps

- **`UNKNOWN`** — mechanism by which the 53 functions reach hardware.
- **`UNKNOWN`** — the 264 knob literals with no HI16/LO16 site (they may be data-only).
- **`KNOWN LIMIT`** — only the **first** `.text` site is used for attribution; multi-site knobs
  are recorded but not each resolved.
- **Not attempted** — dynamic validation.
