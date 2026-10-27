<!-- doc-head: STAGE256A_KNOBS_171_255_HAL_VTABLE.md preserved document content -->
<!-- /doc-head -->


# Stage 256A — knobs 171..255 against `ath_dev.ko` and `ubnt_poll_host.ko`

- **Receipt**: [`artifacts/autoresearch/stage256a_knobs_171_255_hal_vtable.json`](../artifacts/autoresearch/stage256a_knobs_171_255_hal_vtable.json)
- **Tool**: `tools/re/dissect_stage256a_knobs_171_255_hal_vtable.py`
- **Scope**: offline static. No module loaded, no radio contacted.

## 0. Slice and targets

The third 85 `airOS_UMAC_UPH` knobs (indices 170..255), checked against **`ath_dev.ko`** and
**`ubnt_poll_host.ko`** in both WA and XC, as the stage specified.

Vtable offsets carried from 253A: **{4, 8, 156, 160, 164, 204, 208, 296, 300, 396, 520}**.

## 1. Result

| Module | Literals present | Reaching a 253A slot |
| :--- | :-: | :-: |
| `WA.v8.7.25:ath_dev.ko` | **6 / 85** | 0 |
| `WA.v8.7.25:ubnt_poll_host.ko` | **2 / 85** | 0 |
| `XC.v8.7.25:ath_dev.ko` | **6 / 85** | 0 |
| `XC.v8.7.25:ubnt_poll_host.ko` | **2 / 85** | 0 |

Slot histogram: **empty**.

## 2. The real finding: this slice is not here

**`CONFIRMED`**: only **6 of 85** knob names exist in `ath_dev.ko` and **2 of 85** in
`ubnt_poll_host.ko`. Compared with the previous slices:

| Slice | `umac.ko` | `ath_dev.ko` | `ubnt_poll_host.ko` |
| :--- | :-: | :-: | :-: |
| 1..85 (254A) | **85 / 85** | 3 / 85 | — |
| 86..170 (255A) | **85 / 85** | 0 / 85 | — |
| **171..255 (256A)** | — | **6 / 85** | **2 / 85** |

The first two slices are entirely `umac.ko`. This third slice is **not in either module the
stage named**. It is a different population: `unifi`/`mcad`-side parameters, radio-driver
internals that live in `ame_*` or the QCA firmware, or catalogue entries whose implementation
was never in the host driver.

**That is the actionable output**: don't look for knobs 171..255 in `ath_dev.ko` or
`ubnt_poll_host.ko`. Two of them are in `ubnt_poll_host.ko` and six in `ath_dev.ko`; the other
77 are elsewhere.

## 3. Why the 2 and the 6 matter

They are the only concrete leads in this slice. The tool records their names, their `.rodata`
sections and offsets, and their `text_sites`. Those are the eight knobs a follow-up pass can
actually chase in these two modules.

The 77 absent are not "unimplemented": the catalogue has them `CONFIRMED` (Stage 156A verified
all 571 as `CONFIRMED`). Absent from these modules means **absent from these modules**, nothing
more.

## 4. The zero, third time

Same instrument, same defect: the low-16-bit literal-to-site join cannot attribute a knob to a
function. `0 of 85` here is even less informative than in 254A/255A, because the denominator is
mostly absent.

**`REFUTED`**: the low-half join as an identifier. Restated so it is not mistaken for a
replicated confirmation.

## 5. Disposition

**`CONFIRMED`**: 6/85 in `ath_dev.ko`, 2/85 in `ubnt_poll_host.ko`, all eight identified by
section and offset.

**`CONFIRMED`**: this slice lives outside the two modules the stage targeted.

**`UNKNOWN`**: where the other 77 are, and what function/sink any of the eight reaches.

## 6. Gaps

- **`UNKNOWN`** — location of the 77 absent knobs.
- **`UNKNOWN`** — function and vtable attribution for the eight present.
- **`KNOWN LIMIT`** — the join is unsound; `.rel.text` walking is the fix.
- **Not attempted** — dynamic validation.
