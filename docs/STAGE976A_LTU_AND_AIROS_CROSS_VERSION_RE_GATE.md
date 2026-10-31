<!-- doc-head: Stage 976A cross-version static RE gate — reconciles the LTU (ame_core.ko) and airOS 8.7.11/8.7.21 symbol+ioctl receipts of 971A..975A with three named cross-stage checks; offline, read-only, one open contract conflict -->
# Stage 976A — LTU and airOS Cross-Version RE Gate

- **Claim Status**: `PARTIAL` — 52 of 53 invariants hold, 1 contract conflict (section 7)
- **Attribution**: `external controller (offline static gate)` — no radio, no SSH, no firmware write
- **Artifact**: `artifacts/autoresearch/stage976a_ltu_and_airos_cross_version_re_gate.json`
- **Tool**: `tools/verify/verify_stage976a_ltu_and_airos_cross_version_re_gate.py`
- **Suite**: `tests/test_stage971a_to_976a_suite.py`
- **Evidence class**: `STATIC_BINARY_CROSS_VERSION_RECONCILIATION_GATE`

## 1. Purpose

Stages 971A..975A dissect LTU (`ame_core.ko`, `eab_driver.ko`) and compare exported
symbols and ioctl surfaces across `airOS 8.7.11`, `airOS 8.7.25`, `airOS 8.7.4cs`,
`XW 6.1.4`, `XW 6.3.6` and `LTU 2.4.2` trees. Those five stages were produced in
parallel by separate agents. This gate is their consumer: it reads the five receipts,
refuses to promote anything they do not declare, and pins three agreements that no
single stage can prove alone. It re-runs no dissection and rewrites no sibling
artifact.

## 2. Shared receipt contract

Every receipt 971A..976A must carry all four:

| Field | Requirement |
| :--- | :--- |
| `meta.radio_safety` | exactly `static only` |
| `meta.scope` | string or list that contains the token `static` |
| `gaps` | non-empty array (no silent completeness claims) |
| `evidence_provenance_class` | present and non-empty |

The gate applies these four rules to 971A..975A and to itself, so the receipt it
writes cannot exempt itself from the contract it enforces.

## 3. Per-stage invariants

| Stage | Invariants asserted under `summary` |
| :--- | :--- |
| 971A | `eab_driver_present == 0`; `eab_driver_files == 0`; `modules_ok >= 1`; `qam4096_hits > 0`; `mcs_token_hits > 0`; `modulation_symbols >= 1`; `tables_confirmed + tables_inferred >= 1` |
| 972A | `modules_ok >= 1`; `dma_token_hits > 0`; `dma_symbols >= 0`; `register_values_recovered == 0` |
| 973A | `modules_ok >= 1`; `frame_symbols >= 1`; `states_enumerated >= 0`; `transitions_recovered == 0` |
| 974A | `eab_driver_present == 0`; `versions_available >= 4`; `airOS 8.7.21` and `LTU 2.3.1` in `versions_absent`; `trees_scanned >= 4`; `shared_symbols_all >= 1` |
| 975A | `versions_available >= 4`; `modules_with_ioctl >= 1`; `airOS 8.7.21` and `LTU 2.3.1` in `missing_versions`; `divergence_count >= 0` |

The two zero-assertions are the honest ones. 972A performed no disassembly, so
`register_values_recovered` cannot exceed zero: a non-zero value would mean an
invented register, and the gate fails on it. Likewise 973A named states, and naming a
state is not a recovered transition, so `transitions_recovered` must stay zero.

## 4. Cross-stage checks (exactly three)

1. **`eab_absent_agrees`** — 971A and 974A both report `eab_driver_present == 0`. The
   LTU batch therefore contains no `eab_driver.ko` evidence, and no stage may imply one.
2. **`absent_versions_agree`** — the label set of 974A `versions_absent` equals the label
   set of 975A `missing_versions`. Comparison is on normalised labels (case, `_`, `-` and
   spacing folded); both raw sets and the symmetric difference are recorded.
3. **`ltu_version_reported`** — 974A and 975A both count `LTU 2.4.2` among available
   versions, and neither claims `LTU 2.3.1` as available (both list it as absent or
   missing). The available-version inventory is read from `trees[].version`, so the
   check does not depend on a filename or on a hand-maintained version list.

All three hold on the current receipts.

## 5. Receipt layout

`checks_run`, `checks_passed`, `failures` and `compliant` are duplicated at top level and
under `summary` so a consumer can read either place. `checks` holds one entry per
assertion; `cross_checks` holds exactly the three named checks with their evidence
sets; `contract_conflicts` holds every clause that the corpus contradicts, with the
remediation left to the operator; `receipt_index` maps each stage to the receipt file
actually consumed, which makes the gate robust to upstream filenames.

## 6. Determinism

The gate writes no timestamps, no absolute paths and no unordered collections, so two
consecutive runs produce identical receipt bytes. The suite enforces that property for
all six stages by running each stage script twice and diffing its receipt bytes. Byte
determinism is asserted separately from exit status, because a fail-closed gate is
allowed to exit non-zero while still writing stable bytes.

## 7. Result and the one open conflict

- Gate headline: `checks_run=53`, `checks_passed=52`, `failures=1`, `compliant=false`,
  `contract_conflicts=1`.
- Suite: 37 passed, 2 failed — both failures are the same single conflict.

The conflict is `974A.summary.shared_symbols_all`. The contract asks for `>= 1` and
974A reports `0`. The zero is not a bug: `shared_symbols_all` is the strict intersection
of exported symbol sets across *every* scanned tree, and `airOS 8.7.11` exists only as a
4-module partial rescue (mtd5-adjacent image set) while the other trees contribute 95 to
154 modules each. 974A states this in its own gaps and publishes the coverage-fair
companion `shared_symbols_all_full_trees_only = 105`, which does prove non-vacuous
cross-version sharing.

This gate does not amend the contract on its own authority, because a verifier that
rewrites its acceptance criteria to reach green is worth nothing. Two remedies, both
one turn:

1. 974A re-expresses `shared_symbols_all` on the coverage-fair lens (105), or
2. the batch contract is amended to accept
   `shared_symbols_all_full_trees_only >= 1`.

Either lands green with no change to this gate's code: the check reads declared fields.

## 8. Scope and limits

Offline only. Nothing here authorises a deployment, promotes a champion, or substitutes
for live RF measurement. The five upstream receipts are read-only inputs; two sibling
agents own 971A..975A, their tools, their receipts and their docs. Every claim in this
batch is static binary evidence at best `CONFIRMED_STATIC_BINARY`; none is
`CONFIRMED_LIVE_BENCH`.

## 9. Reproduce

```sh
python tools/verify/verify_stage976a_ltu_and_airos_cross_version_re_gate.py
python -m pytest tests/test_stage971a_to_976a_suite.py -q
```
