<!-- doc-head: STAGE254A_KNOBS_1_85_HAL_VTABLE.md preserved document content -->
<!-- /doc-head -->


# Stage 254A — knobs 1..85 against the 253A HAL vtable slots

- **Receipt**: [`artifacts/autoresearch/stage254a_knobs_1_85_hal_vtable.json`](../artifacts/autoresearch/stage254a_knobs_1_85_hal_vtable.json)
- **Tool**: `tools/re/dissect_stage254a_knobs_1_85_hal_vtable.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Slice and inputs

The first 85 `airOS_UMAC_UPH` knobs, ordered by `(family, id)`, checked against four modules:
`umac.ko` and `ath_dev.ko` in both `WA.v8.7.25` and `XC.v8.7.25`.

The vtable offsets carried forward from 253A: **{4, 8, 156, 160, 164, 204, 208, 296, 300, 396, 520}**.

## 1. Result

| Module | Literals present | Reaching a 253A vtable slot |
| :--- | :-: | :-: |
| `WA.v8.7.25:umac.ko` | **85 / 85** | **0** |
| `WA.v8.7.25:ath_dev.ko` | 3 / 85 | 0 |
| `XC.v8.7.25:umac.ko` | **85 / 85** | **0** |
| `XC.v8.7.25:ath_dev.ko` | 3 / 85 | 0 |

Slot histogram: **empty**.

## 2. What the 85/85 means

**`CONFIRMED`**: every one of the 85 knob names appears as a NUL-terminated literal in
`umac.ko`. That is a real, useful result: this slice of the catalogue is genuinely named in the
driver, not merely catalogued.

Only 3 of 85 appear in `ath_dev.ko`, and those three also appear in `umac.ko`. So for this
slice, `umac.ko` is where the names live.

## 3. What the zero means — and what it does not

**The zero is a limit of this tool's attribution method, not evidence that no knob reaches the
HAL.** The pipeline was:

1. find the literal in `.rodata` and take its section offset;
2. search `.text` for any `lui`/`addiu` whose low 16 bits equal that offset;
3. take the enclosing function of the **first** such site;
4. scan that function for `lw`+`jalr` pairs and compare against the 253A offsets.

Step 2 is the weak link. A 16-bit low-half match is not a unique identification: any function
that loads an address with the same low half — or an unrelated constant — matches first. The
"enclosing function" can therefore be an arbitrary one, and its `jalr` slots have nothing to do
with the knob.

With that weakness, `0 of 85` cannot be read as "no knob reaches the vtable". It reads as
**"this method cannot attribute a knob to a function"**.

## 4. What would make the attribution sound

The right join is through **relocations**, not low-half matching:

- `.ko` files are `ET_REL`. A reference to a `.rodata` literal is an `R_MIPS_HI16`/`LO16` pair
  whose symbol and addend identify the target exactly.
- Walking `.rel.text` gives every code site that touches a given literal, with no ambiguity.
- That is the same technique Stage 81A-W4B used successfully for `ctl_table` strings.

For `umac.ko` specifically, the `.rel.text` section is present. The absence of a relocation for
a knob literal would also be informative: it would mean the literal is data-only and never
addressed from code.

## 5. Disposition

**`CONFIRMED`**: 85/85 literals in `umac.ko`, 3/85 in `ath_dev.ko`.

**`UNKNOWN`**: which function references each knob, and therefore which vtable slot (if any) it
reaches.

**`REFUTED`**: the implicit assumption that a low-16-bit match is a sufficient identifier for
the referencing site.

## 6. Gaps

- **`UNKNOWN`** — function attribution for all 85 knobs.
- **`UNKNOWN`** — vtable slot per knob.
- **`KNOWN LIMIT`** — the literal-to-site join is unsound; the relocation-based join is the fix.
- **Not attempted** — dynamic validation.
