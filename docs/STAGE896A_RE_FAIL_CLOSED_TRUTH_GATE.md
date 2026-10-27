<!-- doc-head: Stage 896A - the fail-closed truth gate reads the five receipts 891A through 895A and runs fifty checks across per-stage invariants and three cross-stage agreements with zero failures, asserting that no gate reaches runtime and that an undeclared receipt may be cited as nothing -->
# Stage 896A — fail-closed truth gate

- **Receipt**: [`artifacts/autoresearch/stage896a_re_fail_closed_truth_gate.json`](../artifacts/autoresearch/stage896a_re_fail_closed_truth_gate.json)
- **Tool**: [`tools/verify/verify_stage896a_re_fail_closed_truth_gate.py`](../tools/verify/verify_stage896a_re_fail_closed_truth_gate.py)
- **Audit reference**: section A09
- **Scope**: offline static verification. Reads five JSON receipts only.

## 0. Result

```
[896A] stages=5/5 checks=50/50 cross=3 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages present | **5 / 5** |
| checks run | **50** |
| checks passed | **50** |
| cross-stage checks | **3** |
| failures | **0** |
| `compliant` | **1** |

`compliant` is the emptiness of a **named** failures list, so any failure is printed with its stage and
check name.

## 1. What the gate asserts per stage

| Stage | Asserted |
| :--- | :--- |
| **891A** | 35 of 35 containers parse, zero failures, 140 segments, **zero uncompressed**, 12 of 12 patches valid, 3 of 3 RAM roles matched |
| **892A** | 7 gates, 3 static, 2 present, **0 site execution**, 7 pending, **0 dmesg** |
| **893A** | 143 classified, structural completeness, residual listed and counted |
| **894A** | 258 classified, at least 10 modules tracked, per-module fractions in range |
| **895A** | 333 receipts, tallies sum, **0 disagreements**, **0 gates at runtime**, 5 promotion rules |

The negative assertions carry the weight. `gates_site_execution_proven == 0` and
`gates_runtime_proven == 0` are asserted as **equalities to zero**, so a later receipt that quietly
promoted a gate to runtime would fail the gate rather than pass unnoticed.

## 2. The three cross-stage checks

**`static_gate_count_agrees`** — the verifier derives, from the Stage 891A container list itself, which
gates have a valid carrier, and compares that to Stage 892A's static column. Both must equal **3**. The
derivation is written in the verifier, not copied from 892A, so the two counts are independent.

**`runtime_zero_agrees`** — Stage 892A and Stage 895A must both report **0** gates at runtime. These are
computed by different tools from different inputs, and a mismatch would mean one of them had begun
counting a presence as an execution.

**`subset_labels_agree`** — Stage 895A compares its own labels to 893A and 894A on the shared receipts,
and reports **0** disagreements. The verifier asserts that count is zero rather than recomputing it, so
the check is of the receipt, not of the classifier.

## 3. What the gate cannot do

**`REFUTED`**: it cannot prove runtime.

`gates_runtime_proven == 0` is an assertion that **the corpus contains no such proof**. It is not, and
cannot be, an assertion that the patches do not work. The gate makes a negative claim precise; it does
not make a positive one possible.

The same limit applies to the classifiers: three implementations agreeing proves the **rules** are
consistently applied, not that they are complete. A receipt could be misclassified by all three in the
same way, and this gate would pass it.

## 4. The defect that this gate caught while being written

The first cross-check read a `carriers` field from Stage 891A. That field lives in Stage 892A, so the
check compared **0** against **3** and failed.

The fix was not to relax the comparison but to **derive the count independently** inside the verifier
from the container filenames in 891A. A cross-check that reads the same derived field from both sides
is not a cross-check, and the initial version would have passed a genuine divergence between the two
stages.

That is recorded here because it is the archetype of a vacuous verification: green because both sides
quote the same number, not because two measurements agree.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| all five receipts are present and readable | **CONFIRMED** (5/5) |
| all five declare `static only` radio safety | **CONFIRMED** |
| all five declare at least one gap | **CONFIRMED** |
| every SGMT container in the corpus is valid | **CONFIRMED** (891A, 35 of 35) |
| no gate reaches runtime | **CONFIRMED** (0 of 7, asserted twice) |
| the three classifiers agree | **CONFIRMED** (0 disagreements) |
| an undeclared receipt may be cited as nothing | **CONFIRMED** (rule asserted) |
| the suite is compliant | **CONFIRMED** (`compliant = 1`) |
| the gate proves any patch works | **REFUTED** |

## 6. The operational reading

1. **The gate is a floor, not a ceiling.** Passing it means nothing was over-claimed, not that anything
   was proven to work.
2. **Its negatives are the deliverable.** Seven gates at zero runtime, zero dmesg across 333 receipts,
   zero uncompressed containers, zero classifier disagreements.
3. **A green gate after a fix to the gate itself deserves suspicion.** Section 4 documents one case
   where the check was vacuous before the fix, and the reason it was changed.

## 7. Gaps

- **`UNKNOWN`** — whether any individual finding is correct.
- **`UNKNOWN`** — whether the rules are complete; only their consistency is tested.
- **Blocked** — runtime for all seven gates.
- **Known limit** — self-consistency across five receipts is necessary and not sufficient.
- **Not attempted** — any dynamic validation.
