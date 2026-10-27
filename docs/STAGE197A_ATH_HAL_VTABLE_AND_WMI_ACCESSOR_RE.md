<!-- doc-head: STAGE197A_ATH_HAL_VTABLE_AND_WMI_ACCESSOR_RE.md preserved document content -->
<!-- /doc-head -->


# Stage 197A — HAL accessor reality in `ath_hal.ko` and `umac.ko`

- **Receipt**: [`artifacts/autoresearch/stage197a_ath_hal_vtable_and_wmi_accessor_re.json`](../artifacts/autoresearch/stage197a_ath_hal_vtable_and_wmi_accessor_re.json)
- **Tool**: `tools/re/audit_stage197a_to_199a_hal_and_xw_delta.py`
- **Scope**: offline static only. No module loaded, no register written, no radio contacted.

## 0. The stage was scoped on three names. Two of them do not exist.

| Name | Raw hits in `ath_hal.ko` | Raw hits in `umac.ko` | Verdict |
| :--- | :-: | :-: | :--- |
| `ah_reg_write` | **0** | 0 | **`REFUTED`** — no such symbol |
| `OS_REG_WRITE` | **0** | 0 | **`REFUTED`** — no such symbol |
| `wmi_unified_cmd_send` | 0 | **3** | **`CONFIRMED`** |
| `os_reg_write` | 0 | 0 | absent |
| `reg_write` (substring) | **3** | — | present, but not the named accessor |

**`CONFIRMED`**: the two register-write accessors named in the task do not exist under those
names in either image. Nothing is reported for them beyond their absence.

## 1. What does exist

Four modules audited (WA and XC × `ath_hal.ko` and `umac.ko`).

- **`wmi_unified_cmd_send`** is present in `umac.ko`, with 110 `wmi_unified` strings overall.
  That is the firmware command path and it is real.
- **3 register-write symbols** were found by pattern (`reg.*write|write.*reg`), in `ath_hal.ko`.
- **5 HAL vtable-shaped symbols** were found (`hal.*func|tbl|table|vtable|ops|ah_func`).

So the vendor HAL does carry a function-table structure, which is consistent with Stage 174A's
finding that `umac.ko`/`ath_dev.ko` show essentially **one** named register-write import: the
writes go through the HAL table, not through a libc-style import.

## 2. What this means for Stage 174A

Stage 174A could not associate 340 knobs with register writes because the register-write
inventory in `umac.ko`/`ath_dev.ko` was effectively empty. This stage shows **why**: the
accessor is not a symbol there at all. It lives in the HAL as a table entry.

**The unblock is narrower than "resolve a vtable"**: it is "identify the HAL struct field that
holds the register-write function pointer, and the calling convention it uses". That is a
struct-layout problem, not a symbol-resolution problem, and this stage does not solve it.

## 3. Verdict

**`REFUTED`**: the premise that `ah_reg_write` and `OS_REG_WRITE` are resolvable accessors in
`ath_hal.ko`.

**`CONFIRMED`**: `wmi_unified_cmd_send` exists in `umac.ko` and is the firmware command
submission path.

**`UNKNOWN`**: the concrete HAL vtable slot for register writes. It was not traced.

## 4. Gaps

- **`UNKNOWN`** — which of the 5 HAL vtable-shaped symbols holds the write pointer, and at what
  struct offset.
- **`UNKNOWN`** — the `wmi_unified_cmd_send` call graph into the firmware command path. It is
  located, not reconstructed.
- **`KNOWN LIMIT`** — a raw-string hit count is presence, not a resolved symbol. `reg_write`
  appearing 3 times may be part of longer names.
- **Not attempted** — dynamic validation. Nothing was loaded or executed.

## 5. Next step that would actually unblock 174A

Recover the HAL struct layout from access patterns: find every `lw` that loads a function
pointer from a HAL base register, record the offset, and cross-reference those offsets against
call sites that pass `(reg, value)` pairs. That yields the slot without needing symbol names.
