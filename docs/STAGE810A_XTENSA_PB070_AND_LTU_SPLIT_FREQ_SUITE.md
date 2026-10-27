<!-- doc-head: STAGE810A_XTENSA_PB070_AND_LTU_SPLIT_FREQ_SUITE.md preserved document content -->
<!-- /doc-head -->


# Stage 810A — verification of the 805A..809A receipts

- **Receipt**: [`artifacts/autoresearch/stage810a_xtensa_pb070_and_ltu_split_freq_suite.json`](../artifacts/autoresearch/stage810a_xtensa_pb070_and_ltu_split_freq_suite.json)
- **Tool**: [`tools/verify/verify_stage810a_xtensa_pb070_and_ltu_split_freq_suite.py`](../tools/verify/verify_stage810a_xtensa_pb070_and_ltu_split_freq_suite.py)
- **Scope**: offline static verification. Reads five JSON receipts only.

## 0. A verifier that cannot fail is useless

So `failures` is a **list** and `compliant` is `len(failures) == 0`. The first run produced:

```
[810A] stages=5/5 checks=39/40 failures=1 compliant=0
        FAIL 809A:static_scope
```

**It caught a real defect.** Stage 809A's scope read *"offline simulation"* and did not contain the
word **static**, which every other stage in the series declares. The scope string was corrected to
*"offline static simulation"* and the suite re-ran clean.

That is the verifier doing its job on its own run, and it is recorded here rather than quietly fixed.

## 1. Final result

```
[810A] stages=5/5 checks=40/40 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages expected | 5 |
| stages present and readable | **5** |
| checks run | **40** |
| checks passed | **40** |
| failures | **0** |
| `compliant` | **1** |

## 2. Per-stage invariants

| Stage | Invariants asserted |
| :--- | :--- |
| **805A** | firmware names absent; ratefind walk complete; walk is host-side; sounding absent; no firmware table claimed |
| **806A** | `patch_emitted = 0`; `segments_viable = 0`; a blocking reason is stated |
| **807A** | subchannel vocabulary absent; `ulmap` is a named subsystem; split-frequency pair present; no subchannel map claimed |
| **808A** | AirView absent from the kernel; AirView present as a userspace binary; no kernel arbitration claimed |
| **809A** | `execution_authorised = 0`; all roles blocked; labelled `projection`; front + dominated = roles |

Each stage also gets four structural checks: receipt present, `static` in scope, `radio_safety` equals
`static only`, and at least one gap declared.

## 3. The cross-stage checks are the ones that matter

**`sgmt_segment_count_agrees`**: 805A and 806A both parse the same container and must agree on
**2 segments**. If they disagreed, one of the two parsers would be wrong and both receipts would be
suspect.

That is the only check here that compares **two independent parses** of the same artefact, and it is
the one with real diagnostic power: the rest compare a receipt against itself.

## 4. What the verifier does not do

**`REFUTED`**: the verifier does **not** re-dissect any binary. It reads receipts.

So its own gaps say it plainly:

> *"the verifier checks receipt self-consistency, not binary truth: a wrong value recorded
> consistently in a receipt would pass"*

That is the honest limit. A verifier of this shape catches **drift and inconsistency** — a scope
string missing a word, a front that does not sum to its roles, two parsers disagreeing on segment
count. It cannot catch a **wrong measurement**, because it has no second opinion on the binary.

Closing that would require re-running 805A..809A from scratch and comparing, which is what the pytest
reproducibility tests do — a different and complementary check.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| all five receipts are present and readable | **CONFIRMED** (5/5) |
| all five declare `static` scope and `static only` safety | **CONFIRMED** (after the 809A fix) |
| all five declare at least one gap | **CONFIRMED** |
| the two container parsers agree on segment count | **CONFIRMED** (2 = 2) |
| no stage claims a recovery its sibling refuted | **CONFIRMED** |
| the suite is compliant | **CONFIRMED** (`compliant = 1`) |
| the verifier proves binary truth | **REFUTED** (it reads receipts) |
| 809A's scope originally omitted `static` | **CONFIRMED** (caught, then fixed) |

## 6. The operational reading

Three things a reader can rely on after this stage:

1. **the five receipts are mutually consistent** — including two independent container parses;
2. **no stage over-claims** — every `*_recovered = 0` flag is still zero and none was quietly
   promoted;
3. **the negatives are explicit** — no firmware names, no viable patch segment, no subchannel
   vocabulary, no kernel AirView, no authorised execution.

And one thing a reader must **not** infer: that the measurements are correct. The verifier never
touched a binary.

## 7. Gaps

- **`UNKNOWN`** — whether any recorded value is wrong but consistently recorded.
- **`UNKNOWN`** — whether the two container parsers share a mistaken assumption; agreement is not
  independent validation if both were written from the same reading.
- **Blocked** — binary-truth verification needs re-dissection, which the pytest suite provides
  separately via reproducibility.
- **Known limit** — self-consistency is necessary and not sufficient.
- **Not attempted** — dynamic validation, any live comparison.
