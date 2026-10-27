<!-- doc-head: Stage 904A - the gate passes twenty-six of twenty-six checks with compliant set to one because the remediation scope is complete and the residual is reported honestly, and it deliberately reports full_corpus_zero as zero since 176 receipts across artifacts/autoresearch remain undeclared -->
# Stage 904A — zero-ambiguous gate, scoped honestly

- **Receipt**: [`artifacts/autoresearch/stage904a_zero_ambiguous_receipts_gate.json`](../artifacts/autoresearch/stage904a_zero_ambiguous_receipts_gate.json)
- **Tool**: [`tools/verify/gate_stage904a_zero_ambiguous_receipts.py`](../tools/verify/gate_stage904a_zero_ambiguous_receipts.py)
- **Scope**: offline static verification. Reads three JSON receipts only.

## 0. Result

```
[904A] stages=3/3 checks=26/26 failures=0
remediation_zero=1 full_corpus_undeclared=176 full_corpus_zero=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| checks run | **26** |
| checks passed | **26** |
| failures | **0** |
| remediation targets ambiguous | **0** |
| **full corpus undeclared** | **176** |
| `full_corpus_zero` | **0** |
| `compliant` | **1** |

## 1. Two questions, kept apart

The gate answers two questions that a single boolean would fuse:

1. **Did the remediation succeed on its 31 targets?** Asserted: all classified, all restored, zero
   ambiguous, class counts summing to 31.
2. **Is the whole corpus free of undeclared receipts?** **Not asserted as true**, because it is false.

`compliant` covers question 1 plus the **honesty** of the answer to question 2. `full_corpus_zero` is a
separate field and is **0**, so no downstream summary can quote this gate as evidence that the corpus
is clean.

## 2. Why the gate is not simply "zero across the corpus"

Two options were available and both are worse:

| Option | Consequence |
| :--- | :--- |
| assert zero across the corpus | the gate **fails**, hiding a remediation that did succeed |
| mass-edit 176 receipts to reach zero | a green number **manufactured** by editing other workstreams' history |

The 176 are **156 historical stage receipts** predating the provenance convention and **20 auxiliary
artefacts** such as `champion_state_ledger` and `master_11unit_hardware_atlas`. They are listed by name
in `outstanding` and left unedited.

## 3. The cross-check that matters

**`no_remediated_receipt_left_undeclared`** — the gate takes the 31 targets from Stage 901A, intersects
them with the undeclared list from Stage 902A, and requires the intersection to be **empty**.

That is the check that proves the remediation actually landed: the audit is a separate tool reading the
whole directory, and it does not know which files were targeted.

**`counts_agree_with_901A`** — the registry's 14 / 9 / 8 must equal the remediation receipt's numbers.
A drift here would mean a file had been edited after remediation, which Stage 903A's restoration rows
would then also flag.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| all 31 targets classified | **CONFIRMED** |
| zero ambiguous within the remediation scope | **CONFIRMED** |
| all 31 restorable to their original digest | **CONFIRMED** (903A, independent) |
| the class counts agree across 901A and 903A | **CONFIRMED** |
| no remediated receipt remains undeclared | **CONFIRMED** (intersection empty) |
| the corpus is free of undeclared receipts | **REFUTED** (176 remain) |
| the gate may be quoted as full-corpus clean | **REFUTED** (`full_corpus_zero = 0`) |

## 5. The standing defect

The honest summary of this batch is one sentence: **the 31 are fixed, idempotently, and the corpus is not.**

The follow-up is well defined and cheap per receipt: assign a class with a citation, the method Stage
901A used, one receipt at a time. The 156 historical receipts are the bulk of the work; the 20
auxiliary artefacts may need a different schema rather than a class, since a ledger is not an
experiment.

## 6. Gaps

- **`UNKNOWN`** — the correct class for each of the 176.
- **`UNKNOWN`** — whether the auxiliary artefacts should carry a class at all.
- **Blocked** — a corpus-wide zero requires curating 176 receipts, which this batch deliberately did
  not do.
- **Known limit** — `compliant` here means "scope complete and residual reported", not "corpus clean".
- **Not attempted** — editing any of the 176, any dynamic validation.
