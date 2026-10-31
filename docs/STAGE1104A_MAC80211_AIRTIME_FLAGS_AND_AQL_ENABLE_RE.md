<!-- doc-head: Stage 1104A static dissection of the canary mac80211.ko - airtime_flags, aql_enable and aql_pending debugfs handlers, their modes, format strings and bit masks -->
# Stage 1104A - mac80211 airtime_flags and aql_enable dissection

100% offline, static only. No module loaded, no radio contacted, no firmware written, no live address used.
Script: `tools/re/dissect_stage1104a_mac80211_airtime_flags_and_aql_enable_re.py`.
Receipt: `artifacts/autoresearch/stage1104a_mac80211_airtime_flags_and_aql_enable_re.json`.

## 1. Input

`artifacts/canary_panel1_guarida/panel1_native_cutover_20261019/after/mac80211.ko`, 829464 bytes,
sha256 `19a8fde6c6e5efbec3b5b3ddb28399631fc3bba516c5341c8f40e7263124c416`, MIPS32 big-endian `ET_REL`.

This directory holds only `mac80211.ko`. It never held ath10k. ath10k is dissected in Stage 1103A from
the `stage117a_build/stock.tar` member.

Build identity from embedded `__FILE__` markers: `backports-6.12.52/net/mac80211/`. Backports source, so
the `file_operations` layout follows the 6.6.110 kernel headers, not the 6.12 headers. That matters in
section 4 and it is measured, not assumed.

## 2. Anchor

All three files are created in one function, `debugfs_hw_add` at `0x711a0`, size 800 bytes. It makes 22
`debugfs_create_*` calls. The four that matter:

| File | Mode | `debugfs_create_file` call | fops |
| :--- | :--- | ---: | ---: |
| `aql_enable` | `0o600` | `0x71358` | `0x43ac` |
| `aql_pending` | `0o400` | `0x7137c` | `0x44b4` |
| `airtime_flags` | `0o600` | `0x713c4` | `0x4538` |
| `aql_txq_limit` | `0o400` | `0x713e8` | `0x4430` |

Mode is read from the `addiu $a1, $zero, <imm>` that precedes each `jal debugfs_create_file`. `0x180` is
`0o600`, `0x100` is `0o400`. Nothing here is inferred from source.

## 3. Handler offsets - CONFIRMED

The `file_operations` structs live in `.rodata` and are resolved slot by slot through `.rel.rodata`. In a
`SHT_REL` object the addend is the word already stored at the slot, so the handler address is
`stored_word + symbol_value`. That is a link-time relocation, which is why these offsets are trusted.

| File | Role | Offset | Upper bound | Mode |
| :--- | :--- | ---: | ---: | :--- |
| `airtime_flags` | read | `0x6fb18` | `0x6fc50` | `0o600` |
| `airtime_flags` | write | `0x70790` | `0x708d8` | `0o600` |
| `aql_enable` | read | `0x6faa8` | `0x6fb18` | `0o600` |
| `aql_enable` | write | `0x6fe74` | `0x7011c` | `0o600` |
| `aql_pending` | read | `0x6f97c` | `0x6fa3c` | `0o400` |

`aql_pending` has no write slot: the struct `0x44b4` carries no relocation at that position. A `0o400`
file with no `.write` handler cannot be written.

Handler counts: `airtime_flags_handlers` 2, `aql_enable_handlers` 2, `aql_pending_handlers` 1.

Exact sizes are **not** reported. All five bodies sit in a region with no `STT_FUNC` symbol: the last
symbol before them ends at `0x6f8a0` and the next begins at `0x70f70` (`mac80211_format_buffer`). Each
record carries `exact_size_recovered: false` and an upper bound taken from the next confirmed entry
point, and all five are listed in `meta.unresolved_bounds`.

## 4. Layout derivation, not assumption

The read and write slot numbers were derived rather than assumed. The slot holding `default_llseek` is
llseek; read and write follow at `+4` and `+8`; `simple_open` was observed at `+0x30`. All three structs
gave `llseek 4, read 8, write 12, open 52` and `layout_consistent: true`.

That is the legacy 32-bit layout with no `fop_flags` field, which is what the 6.6.110 headers produce.
Had this been compiled against 6.12 headers the observation would have disagreed, and the stage would
have reported the disagreement instead of a handler offset.

## 5. Format strings - CONFIRMED

Recovered by backtracking the format argument register of each `scnprintf`, then reading the `$LCn`
symbol it relocates to. Four strings belong to the three contracted files:

| Offset in `.rodata.str1.4` | Handler | Text |
| ---: | :--- | :--- |
| `0x51cc` | `airtime_flags` read | `AIRTIME_TX\t(%lx)\n` |
| `0x51e0` | `airtime_flags` read | `AIRTIME_RX\t(%lx)\n` |
| `0x51c8` | `aql_enable` read | `%d\n` |
| `0x5164` | `aql_pending` read | `AC     AQL pending\nVO     %u us\n...` |

Note the `%lx` in both airtime banners: the read path prints the whole flags word after each banner, so
the file reports the flags value, not just a yes/no.

## 6. Bit masks - CONFIRMED

Inside the `airtime_flags` read handler, immediately after a halfword load, two consecutive `andi` tests
gate which banner is printed:

    0006fb68  lhu     $v1, 0x114($s4)
    0006fb6c  andi    $v0, $v1, 1
    0006fb70  bnez    $v0, 0x6fbd8          -> prints AIRTIME_TX
    0006fb74  andi    $v1, $v1, 2
    0006fb78  bnez    $v1, 0x6fc04          -> prints AIRTIME_RX

`bitmask_constants` therefore reports `AIRTIME_TX = 0x1` and `AIRTIME_RX = 0x2`.

The names are attached by convention. The binary proves the numbers. No enum name string exists in the
module, and that limit is recorded in the gaps.

The field is a 16-bit halfword at `0x114` of the structure reached through `0x80(first argument)`. That
is a compiled artefact of the 6.6.110 headers and is not stable across kernels.

## 7. Write paths - the answer to "writes accepted"

`writes_accepted` in the receipt is one paragraph; this is the evidence under it.

**airtime_flags accepts writes.** Mode is `0o600` and a `.write` handler exists at `0x70790`. That
handler calls `kstrtou16(buf, 0, local + 0x114)` and stores unconditionally. There is no `andi`, no `ori`
and no range check between the parse and the store, so any u16 is persisted. Claim C-1104A-04.

**aql_enable accepts writes.** Mode is `0o600` and a `.write` handler exists at `0x6fe74`. It does a
manual `__raw_copy_from_user`, bounds the count with `sltiu $v0, $a2, 4`, runs `strnlen(buf, 3)`, then
compares single characters against `0x30` and `0x31`. Only the strings `0` and `1` change state. The state
itself is the global `aql_disable`, updated through an `ll`/`sc` loop.

**aql_pending does not accept writes.** Mode is `0o400` and the struct has no `.write` slot.

**No sscanf anywhere in the three.** Call targets were recovered from `R_MIPS_26` relocations, plus `$at`
backtracking for the indirect `__raw_copy_from_user` calls. `sscanf` appears only on `aql_txq_limit`, at
`0x70d54`, with `mcast %u` and `%u %u %u`. That control is kept in `aql_txq_limit_control` to show the
contrast rather than to pad the contracted numbers.

## 8. Grades

| Claim | Grade |
| :--- | :--- |
| C-1104A-01 module present, digest matches | CONFIRMED |
| C-1104A-02 modes `0o600`, `0o600`, `0o400` from `addiu $a1` immediates | CONFIRMED |
| C-1104A-03 read/write slot population per file | CONFIRMED |
| C-1104A-04 `AIRTIME_TX`/`AIRTIME_RX` bit tests, no write-side mask | CONFIRMED |
| C-1104A-05 no sscanf on the three contracted write paths | CONFIRMED |
| C-1104A-06 backports-6.12.52 on 6.6.110 headers | CONFIRMED |
| C-1104A-07 out-of-range `airtime_flags` write is not rejected by the driver | INFERRED |

C-1104A-07 is INFERRED on purpose. The absence of a static gate is proven; how mac80211 consumes an
out-of-range u16 afterwards is a runtime property and is not claimed.

## 9. Unresolved

Exact handler sizes are not recovered - see section 3. The `airtime_flags` write upper bound spans more
than one unnamed function, so its bracket over-estimates and no size claim is made from it. `AIRTIME_TX`
and `AIRTIME_RX` exist only as numeric immediates. The six-item `gaps` array in the receipt carries the
full list.

## 10. Reproduce

    python tools/re/dissect_stage1104a_mac80211_airtime_flags_and_aql_enable_re.py

Two consecutive runs produce byte-identical output; the script re-renders its own payload and refuses to
write if the renders differ. No timestamp, host path or iteration order reaches the JSON: keys are sorted
and sibling keys pass through `decase(node)` so no two can collide case-insensitively.
