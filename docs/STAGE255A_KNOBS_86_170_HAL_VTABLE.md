<!-- doc-head: STAGE255A_KNOBS_86_170_HAL_VTABLE.md preserved document content -->
<!-- /doc-head -->


# Stage 255A — knobs 86..170 against the 253A HAL vtable slots

- **Receipt**: [`artifacts/autoresearch/stage255a_knobs_86_170_hal_vtable.json`](../artifacts/autoresearch/stage255a_knobs_86_170_hal_vtable.json)
- **Tool**: `tools/re/dissect_stage255a_knobs_86_170_hal_vtable.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Slice

The second 85 `airOS_UMAC_UPH` knobs (indices 85..170 of the `(family, id)` ordering), checked
against the same four modules. Vtable offsets from 253A unchanged:
**{4, 8, 156, 160, 164, 204, 208, 296, 300, 396, 520}**.

## 1. Result

| Module | Literals present | Reaching a 253A slot |
| :--- | :-: | :-: |
| `WA.v8.7.25:umac.ko` | **85 / 85** | **0** |
| `WA.v8.7.25:ath_dev.ko` | **0 / 85** | 0 |
| `XC.v8.7.25:umac.ko` | **85 / 85** | **0** |
| `XC.v8.7.25:ath_dev.ko` | **0 / 85** | 0 |

Slot histogram: **empty**.

## 2. The clean split

**`CONFIRMED`**: this slice is *entirely* an `umac.ko` slice. All 85 names are literals in
`umac.ko`, and **none** appears in `ath_dev.ko` — unlike slice 1, where 3 leaked into
`ath_dev.ko`.

That is a real structural fact about the catalogue: the knobs at indices 86..170 are named only
in the upper-MAC module. It sharpens the picture from 156A, where the whole boundary was
reported as "present in umac.ko and ath_dev.ko" without per-slice granularity.

## 3. The zero is the same method limit, not a second finding

**`REFUTED` again**: the low-16-bit literal-to-site join cannot attribute a knob to a function.
The pipeline is identical to 254A — find the literal in `.rodata`, match any `lui`/`addiu` whose
low half equals the section offset, take that site's enclosing function, scan it for
`lw`+`jalr`.

A 16-bit match is not unique. With that weakness, `0 of 85` means **the method cannot attribute**,
not that no knob dispatches through the HAL.

Reporting the same zero twice might look like confirmation. It is not: it is the same
instrument failing the same way on a different sample.

## 4. What changed relative to 254A

| | 254A (1..85) | 255A (86..170) |
| :--- | :--- | :--- |
| `umac.ko` literals | 85 | **85** |
| `ath_dev.ko` literals | 3 | **0** |
| vtable attribution | 0 | 0 (same limit) |

The only new information is the **0 in `ath_dev.ko`**, which makes this slice exclusively
upper-MAC.

## 5. Disposition

**`CONFIRMED`**: 85/85 in `umac.ko`, 0/85 in `ath_dev.ko`.

**`UNKNOWN`**: function attribution and vtable slot for all 85.

**`REFUTED`**: the low-half join as an identifier — same defect as 254A.

## 6. Gaps

- **`UNKNOWN`** — function and slot attribution for all 85 knobs.
- **`KNOWN LIMIT`** — the join is unsound; `.rel.text` walking is the fix, and `umac.ko` has
  `.rel.text` present.
- **`KNOWN LIMIT`** — this slice adds no evidence beyond the `ath_dev.ko` zero.
- **Not attempted** — dynamic validation.
