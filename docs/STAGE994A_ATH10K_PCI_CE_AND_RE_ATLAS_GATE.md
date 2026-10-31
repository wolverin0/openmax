<!-- doc-head: Stage994A ath10k PCI/CE absence plus 571-knob and 1000-module RE atlas gate; static, offline, coverage measured not guaranteed -->
<!-- /doc-head -->

# Stage994A - ath10k PCI/CE absence and RE atlas gate

Fail-closed gate over the saved Stage 989A..993A receipts. It re-reads what those
stages published, resolves the real knob catalog on disk, and decides whether the
ath10k absence story, the 571-knob atlas and the 1000-module atlas are internally
consistent and agree with each other. It acquires nothing new.

Provenance of this receipt is **EVIDENCE_RECONCILIATION_ONLY**. Radio safety scope is
**static only**: no SSH session, no radio, no driver load, no firmware write, no live
capture. Every number below is a property of files in this repository.

## Boundary

The gate opens five saved receipts, the two documented catalog filenames, six stage
documents and six stage tools. It writes exactly one file, its own receipt. It never
writes into the upstream receipts, their tools or their docs, and it never touches a
device. Its payload is a pure function of those inputs, so two consecutive runs must
produce identical bytes; the wall clock is not recorded.

## Per-stage contract

Each stage publishes a `summary` object. The gate asserts these fields:

| Stage | Asserted in `summary` |
| :--- | :--- |
| 989A | `ath10k_modules_found == 0`, `ath10k_pci_present == 0`, `ath10k_core_present == 0`, `sweep_methods >= 3`, `absence_proven == 1`, `exact_offsets_recovered >= 0` |
| 990A | `ath10k_core_present == 0`, `htt_tx_32_present == 0`, `credit_flow_recovered == 0`, `offsets_from_ath10k == 0`, `offsets_from_umac >= 0`, `firmware_htt_hits == 0` |
| 991A | `layers_total >= 2`, `layers_absent >= 1`, `ath10k_offsets_claimed == 0`, `boundary_documented == 1` |
| 992A | `knobs_total == 571`, `catalog_knob_count == 571`, `knobs_with_provenance + knobs_without_provenance == knobs_total`, `coverage_fraction` in `[0.0, 1.0]`, non-empty `provenance_field_used` |
| 993A | `modules_total >= 1000`, `modules_with_receipt + modules_without_receipt == modules_total`, `coverage_fraction` in `[0.0, 1.0]`, non-empty `provenance_field_used`, non-empty `architectures` object |

Every one of the six receipts, including this gate's, must also carry
`evidence_provenance_class`, `meta.radio_safety == "static only"`, a `meta.scope`
that mentions static work, and a non-empty `gaps` list.

## Coverage is measured, not guaranteed

This is the load-bearing rule of the stage. The gate does not require
`coverage_fraction == 1.0` and never rewards it. It requires three things:

1. the arithmetic closes: the with-part plus the without-part equals the total;
2. the fraction is a probability-like number inside `[0.0, 1.0]`;
3. a receipt is allowed to claim full coverage only when its own counts actually reach
   the total. A receipt that declares `coverage_fraction == 1.0` while
   `knobs_with_provenance < knobs_total` or `modules_with_receipt < modules_total`
   fails the stage at `full_coverage_claim_corroborated`.

Any shortfall must be enumerated. When the without-part is greater than zero, the
stage must list at least one entry in `gaps_listed`; a silent shortfall fails
`shortfall_enumerated_in_gaps_listed`.

## The three cross checks

Exactly three cross-stage checks are asserted, by name.

1. `ath10k_absent_agrees` - 989A, 990A and 991A must all report zero ath10k presence,
   and 991A must claim zero ath10k offsets. Values: the three 989A absence fields, the
   990A core and HTT-Tx fields, and the 991A `layers_absent` and `ath10k_offsets_claimed`.
   A single nonzero value flips this cross check to failed.
2. `knob_total_agrees` - 992A `knobs_total` and `catalog_knob_count` must both equal
   571, and the resolved catalog file must really hold 571 entries in its `knobs` list.
   Two filenames are considered in order:
   `orchestration/autoresearch/firmware_knobs_candidates.json`, then
   `orchestration/autoresearch/firmware_knob_candidates.json`. Whichever exists is
   the one resolved, and the receipt records that path plus the entry count. The gate
   reports which path it resolved instead of assuming a particular one.
3. `atlas_field_agrees` - 992A `provenance_field_used` must be non-empty and identical
   to 993A `provenance_field_used`, so the two atlases are keyed by the same provenance
   field instead of two drifting conventions.

## What this gate does not do

The gate deliberately stops at consistency. It does not re-derive a single measurement
from the five upstream stages, does not scan a single binary, and does not promote any
claim. Concretely:

- Ath10k absence is a scoped negative result over the saved corpus. Vendor images that
  are not in that corpus remain unexamined, so absence is not proven globally.
- The 571 catalog entries are enumerated and counted, not individually re-validated.
  An entry that is present but wrong still counts as present here.
- Module receipts are counted, not replayed. `modules_without_receipt` entries stay
  unverified no matter what a summary asserts.
- No physical acceptance, no zero-false-positive claim and no deployment authority is
  conferred. A green gate means the published numbers agree with each other and with
  the files on disk.

## Artifacts

| Item | Path |
| :--- | :--- |
| Gate tool | `tools/verify/verify_stage994a_ath10k_pci_ce_and_re_atlas_gate.py` |
| Gate receipt | `artifacts/autoresearch/stage994a_ath10k_pci_ce_and_re_atlas_gate.json` |
| Suite | `tests/test_stage989a_to_994a_suite.py` |
| Upstream tools | 989A..991A under `tools/re/`, 992A..993A under `tools/verify/` |
| Upstream receipts | `artifacts/autoresearch/`, one per stage 989A..993A |

The receipt carries `checks`, `checks_run`, `checks_passed`, `failures` and
`compliant`, plus a `summary` block with the same headline counts, the resolved paths,
the resolved catalog path and one entry per cross check.

## Reproduction

```
python tools/verify/verify_stage994a_ath10k_pci_ce_and_re_atlas_gate.py
python -m pytest tests/test_stage989a_to_994a_suite.py -q
```

The suite resolves each stage tool across `tools/re` and `tools/verify`, resolves each
receipt, checks the six docs for the line budget, a single doc-head and zero
exclamation marks outside html comments and fenced code, replays the per-stage
invariants and the three cross checks, and then runs all six scripts twice to prove
byte-identical receipts. A missing or malformed upstream receipt fails the gate; it is
never papered over with a fabricated assertion.

## Attribution

`external controller` for the orchestration, `static repository evidence` for every
claim, `UNKNOWN` for anything not present in the saved corpus. Memory claim id
`FMX-STAGE994A-ATH10K-PCI-CE-AND-RE-ATLAS-GATE`.
