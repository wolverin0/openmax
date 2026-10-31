<!-- doc-head: Stage 1223A Wave 30 OpenCode gate: audits receipts 1218A..1223A against the pinned contract, runs the three named cross-stage checks, enforces the doc prose contract, recounts fabricated offsets independently and confirms the offline posture. Static only, fail-closed. -->
# Stage 1223A: Wave 30 OpenCode Gate

- **Claim status**: `CONFIRMED` (offline gate)
- **Attribution**: `external controller (offline gate)`; no radio, no SSH, no firmware write
- **Tool**: `tools/verify/verify_stage1223a_wave30_opencode_gate.py`
- **Receipt**: `artifacts/verification/stage1223a_wave30_opencode_gate.json`
- **Evidence class**: `CONFIRMED_STATIC_BINARY`
- **Suite**: `tests/test_stage1218a_to_1223a_suite.py`

## 1. What this gate is for

Wave 30 produced four RE stages and one reconciliation matrix. Each of them
wrote its own receipt with its own idea of what a field is called. This gate is
the single place where the pinned contract is applied to all six at once, so
that a green suite means the whole wave agrees, not that each tool agrees with
itself.

The gate is fail-closed: it writes its receipt, prints the headline, and exits
non-zero when any check fails. It never repairs an upstream receipt and never
rewrites a value to make it conform.

## 2. Contract audited

| Stage | Invariants |
| :--- | :--- |
| `1218A` | `modules_analysed == 2`, `ubnt_radar_mode_offset == 952628`, `radar_symbols` non-empty, `per_module` has 2 entries |
| `1219A` | `modules_total == 154`, `eab_present == 0`, `eab_loose == 0`, `eab_tar_members == 0`, `roles` at least 3 entries |
| `1220A` | `timeout_resolves_to` in `30s` / `1800000ms` / `UNKNOWN`; when not `UNKNOWN`, `timeout_ms > 0` and a `timer_call_sites` entry exists; `penalty_threshold_offset` not null; `disagreements_resolved` non-empty |
| `1221A` | `entries_total > 0`, `fabricated_offsets == 0`, `offsets_table` non-empty, every entry carries `source_stage` |
| `1222A` | `receipts_found >= 4`, `0 <= coverage_measured <= 1`, `conflicts_total >= 2` |
| `1223A` | `failures` empty |

Every one of the six also has to satisfy the safety envelope independently:
`meta.radio_safety == "static only"`, `meta.scope` containing `static`, a
non-empty `gaps` list, a present `evidence_provenance_class`, and zero
case-insensitive sibling key collisions.

The collision walk is run twice on purpose: `decase()` refuses to serialise a
colliding document, and `key_collisions()` re-walks the finished payload as an
independent check on the serialiser.

## 3. Cross-stage checks

Exactly three, named as contract:

1. `radar_mode_offset_agrees` - the `ubnt_radar_mode_offset` reported by 1218A
   must appear identically in 1222A's reconciliation rows or in 1221A's
   `offsets_table`. This catches a stage that quotes the symbol at one offset in
   prose and a different offset in its ledger, and it catches an image
   substitution that moves the string table.
2. `absent_module_agrees` - 1219A must report `eab_present == 0` and no
   `offsets_table` entry in 1221A may name `eab_driver.ko`. This catches a
   ledger that keeps an offset for a module the census says is not in the tree.
3. `bmiss_resolution_consistent` - 1220A's `timeout_resolves_to` and the
   corresponding 1222A reconciliation row must agree, or both must say
   `UNKNOWN`. Disagreement here means the matrix drifted from the stage that
   owns the constant.

## 4. What the gate refuses to assume

Two of the audited quantities are measurements over a corpus with known
absences, not booleans. The gate is written accordingly:

- `timeout_resolves_to` is accepted as `UNKNOWN`. When the bytes do not
  discriminate between `30 s` and `1,800,000 ms`, a receipt that honestly says
  `UNKNOWN` is compliant, and a receipt that asserts a value without
  `timeout_ms > 0` and a `timer_call_sites` entry is not;
- `coverage_measured` is accepted anywhere in `[0, 1]`, and the gate additionally
  requires that 1222A carries its own `coverage_definition` string so the number
  is auditable. The gate never requires `1.0` and never asserts a particular
  coverage.

## 5. Fabricated offsets

`fabricated_offsets` is recomputed here instead of copied from 1221A. An entry
is counted when its offset is not an integer, is negative, or exceeds the byte
size of the module it names, where that module is resolvable in the local
corpus. A module that cannot be resolved locally is skipped, not counted:
unverifiable is not the same as fabricated, and conflating the two would make
the count meaningless.

The radar offset is additionally pinned: entry `952628` for `ubnt_radar_mode`
in the `2,356,432` B `umac.ko` must hold the symbol name. A ledger that moves
that number fails `radar_mode_offset_agrees`.

## 6. Prose contract

Every Wave 30 doc must be under `220` lines, open with exactly one doc-head
HTML comment on line 1, and carry no exclamation mark outside HTML comments and
fenced code blocks. The scanner tracks fence state and comment state per line
rather than running a global regex, because a global count would either flag the
doc-head marker itself or miss a marker inside a fence.

## 7. Offline posture

`offline_confirmed` is `1` only when none of the six tool sources imports a
network module. The scan is anchored to real import statements rather than prose
so that a docstring saying "no SSH" is not a false positive, and a smuggled
`socket` import is not a false negative. No tool in the wave opens a socket,
contacts an IP, loads a module or writes firmware.

## 8. Reproduction

```
python tools/verify/verify_stage1222a_re_reconciliation_matrix.py
python tools/verify/verify_stage1223a_wave30_opencode_gate.py
python -m pytest tests/test_stage1218a_to_1223a_suite.py -q
```

The gate is deterministic: it writes no wall-clock field, so running it twice
produces byte-identical receipts. The suite relies on that property and asserts
it directly.

## 9. Failure policy

When a check fails the gate still writes its receipt, so the failure is durable
and inspectable, then exits `1`. A failing clause is reported, never relaxed.
The three outcomes that must stay distinguishable are: a stage that measured
honestly and found `UNKNOWN`, a stage that measured a different image than the
pinned one, and a stage that reports a value it did not measure. Only the first
is compliant with `UNKNOWN`; the second and third surface as contract failures
with the specific field named in `summary.failures`.
