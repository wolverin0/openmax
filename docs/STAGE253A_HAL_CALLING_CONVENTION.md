<!-- doc-head: STAGE253A_HAL_CALLING_CONVENTION.md preserved document content -->
<!-- /doc-head -->


# Stage 253A — HAL calling convention in `ath_hal.ko` and `umac.ko`

- **Receipt**: [`artifacts/autoresearch/stage253a_hal_calling_convention.json`](../artifacts/autoresearch/stage253a_hal_calling_convention.json)
- **Tool**: `tools/re/dissect_stage253a_hal_calling_convention.py`
- **Scope**: offline static. MIPS32 big-endian capstone disassembly. No module loaded, no radio contacted.

## 0. Targets

Located by `.symtab`, not by guessed addresses:

| Module | Functions found |
| :--- | :--- |
| `ath_hal.ko` | `ath_hal_attach` (`0x630`), `_ath_hal_attach` (`0x1fc`) |
| `umac.ko` | `ath_attach` (`0x1c2fc`), `__ath_attach` (`0x91114`), `ol_ath_attach` (`0xa9c94`), `__ol_ath_attach` (`0xbbdc4` / `0xbbdc8`) |

`CONFIRMED`: all six exist. `ol_ath_attach` is in `umac.ko`, **not** in `ath_hal.ko`.

## 1. Method

For each function, disassemble with capstone and for every `jalr $rX`:

1. walk backwards up to 0x40 bytes for the `lw $rX, off($base)` that defined the target;
2. record `(base, off)` — the **vtable slot**;
3. capture the last write to `$a0..$a3` — the **arguments in flight**.

A `jalr` whose target was not loaded from a base register inside the window is **skipped**,
not guessed.

## 2. Result

| Metric | Value |
| :--- | :-: |
| Modules | 4 (WA, XC × `ath_hal.ko`, `umac.ko`) |
| Functions located | **12** |
| `jalr` sites resolved | **90** |
| Distinct vtable offsets | **11** |

### Offset histogram

| Offset | Count |
| :-: | :-: |
| **4** | **48** |
| 164 | 12 |
| 8 | 12 |
| 520 | 4 |
| 296 / 300 / 396 / 156 / 204 / 208 / 160 | 2 each |

### Base registers

| Base | Count |
| :--- | :-: |
| **`$s2`** | **70** |
| `$v1` | 10 |
| `$v0` | 10 |

### Call distribution

`ath_attach` carries **41** of the 90 sites; `__ath_attach` carries 4. The two `*_hal_attach`
functions carry **zero** — the attach path itself does not dispatch through the vtable, it
builds it.

## 3. The convention

**`CONFIRMED`**: the dominant dispatch shape is `lw $t9, 4($s2)` followed by `jalr $t9`, with
`$s2` holding the HAL struct base. Offset **4** accounts for more than half of all sites.

That is a concrete, actionable convention:

```
$s2  = HAL struct base
4($s2) = first function-pointer slot (48 of 90 dispatches)
$a0..$a3 = arguments as captured per site
```

**Why offset 4 and not 0**: offset 0 in this struct is not used for dispatch at all — zero
sites reference it. So the first slot is at 4, which suggests a leading scalar field rather
than a pointer.

## 4. What this gives Stage 254A

Stage 222A could not map knobs to sinks because the vtable slot was unknown. It is now known
for the dominant path: **`$s2 + 4`**. The next stage can take each knob's setter and check
whether it reaches `lw $t9, 4($s2) / jalr $t9`.

## 5. Gaps

- **`UNKNOWN`** — the semantic role of each argument. The capture reports the last write to
  `$a0..$a3`, which is the setup, not the meaning.
- **`UNKNOWN`** — which of the 11 offsets is the **register-write** accessor. Offset 4 is the
  most used, not the write path.
- **`UNKNOWN`** — the struct field at offset 0.
- **`KNOWN LIMIT`** — the backward window is 0x40 bytes; a target loaded earlier is skipped.
- **Not attempted** — dynamic validation.
