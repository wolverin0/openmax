<!-- doc-head: Stage 860A - the verifier reads the five receipts 855A through 859A and runs fifty-five checks across per-stage invariants and three cross-stage agreements with zero failures and compliant set to one, including the two PB-090 agreements between 855A and 856A and between 856A and 859A, and the shared corpus-defect agreement between 857A and 858A -->
<!-- /doc-head -->
# Stage 860A — verification of the 855A..859A receipts

- **Receipt**: [`artifacts/autoresearch/stage860a_re_pb090_and_spectral_suite_receipt.json`](../artifacts/autoresearch/stage860a_re_pb090_and_spectral_suite_receipt.json)
- **Tool**: [`tools/verify/verify_stage860a_re_pb090_and_spectral_suite.py`](../tools/verify/verify_stage860a_re_pb090_and_spectral_suite.py)
- **Scope**: offline static verification. Reads five JSON receipts only.

## 0. Final result

```
[860A] stages=5/5 checks=55/55 cross=3 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages present | **5 / 5** |
| checks run | **55** |
| checks passed | **55** |
| cross-stage checks | **3** |
| failures | **0** |
| `compliant` | **1** |

`compliant` is the **emptiness of a named failures list**, not a boolean assembled from counts, so any
failure is reported with its stage and check name.

## 1. Per-stage invariants

| Stage | Invariants asserted |
| :--- | :--- |
| **855A** | transfer vocabulary absent; 16-bit constants at chance; control like chance; 2 segments; magic present; base ambiguity recorded; fast path not claimed |
| **856A** | 7 images; 0 with anchor; 0 container anchor; patch not emitted; hexa 3 of 6; 1 policy block; 2 anchor blocks |
| **857A** | `ubnt_spectral` absent on WA/XC; WA/XC is `ath_spectral`; radar only on AC; fft doubled on XW; `airview` user-space; 6 zero-byte clients; protocol not claimed |
| **858A** | `eab_driver` absent; 5 prior receipts without source; `nl80211` zero; netlink generic; 3 channels; telemetry not claimed |
| **859A** | no performance Pareto; front is two gates; cascade detected; binding is `PB-070`; ordering not claimed |

Each stage also gets four structural checks: receipt present, `static` in scope, `radio_safety` equals
`static only`, and at least one gap declared.

## 2. The three cross-stage checks

**`pb090_anchor_agrees`** — 855A measures zero transfer vocabulary in the container, and 856A measures
zero anchors in the container **and** in all seven kit payloads. Two measurements, different artefacts,
same conclusion.

**`pb090_coverage_agrees`** — 856A emits no patch, and 859A records the PB-090 gate at coverage 0. The
builder and the planner therefore agree on the same gate's state.

**`stub_defect_agrees`** — 857A reports six zero-byte spectral clients and refuses to claim a protocol;
858A reports an absent module and refuses to claim telemetry. Both are **corpus defects**, and both
stages decline to promote a conclusion from missing bytes.

The third check is the one that guards against a systematic failure mode rather than a disagreement:
two stages independently reaching an absence and **both declining to over-interpret it** is the
behaviour the series has been enforcing since Stage 424A.

## 3. Corrections this suite forced

Two of my own tools were **wrong before the verifier was satisfied**, and both corrections are worth
recording:

1. **856A** first reported **6 of 7** images with an anchor. The probe was matching `ring` inside
   innocent ASCII such as `string`. Tightening to delimited uppercase tokens returned **0 of 7**.
2. **859A** first reported a **degenerate** front. I had designed the tool expecting one. The measured
   front is **two gates**, so the verifier was corrected to assert two, not the data to fit the
   expectation.

Neither correction was cosmetic: the first would have produced a false "viable target" list, and the
second would have replaced a real trade-off with a vague statement about correlation.

## 4. What the verifier does not do

**`REFUTED`**: it does **not** re-dissect a binary.

Its own gaps say so:

> *"the verifier checks receipt self-consistency, not binary truth: a consistent wrong value would
> pass"*

So it catches **drift and inconsistency**: a missing `static` word, a stage that stopped declaring a
gap, two stages disagreeing about one gate. It cannot catch a wrong measurement. The pytest suite covers
that separately by re-running every tool and comparing receipt bytes.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| all five receipts are present and readable | **CONFIRMED** (5/5) |
| all five declare `static` scope and `static only` safety | **CONFIRMED** |
| all five declare at least one gap | **CONFIRMED** |
| 855A and 856A independently agree PB-090 has no anchor | **CONFIRMED** |
| 856A and 859A agree PB-090 has zero coverage | **CONFIRMED** |
| two stages independently refuse to over-read a corpus defect | **CONFIRMED** |
| the suite is compliant | **CONFIRMED** (`compliant = 1`) |
| the verifier proves binary truth | **REFUTED** |

## 6. The operational reading

A reader can rely on three things after this stage:

1. the five receipts are **mutually consistent**, including two independent PB-090 measurements;
2. **no stage over-claims** — every `*_recovered = 0` flag is still zero;
3. the negatives are **explicit**: no transfer vocabulary, no anchor in 7 images, no
   `ubnt_spectral.ko` on WA/XC, no `eab_driver.ko` in 154 modules, no performance Pareto.

And one thing not to infer: that the measurements are correct. The verifier never touched a binary.

## 7. Gaps

- **`UNKNOWN`** — whether any recorded value is wrong but consistently recorded.
- **`UNKNOWN`** — whether the PB-090 agreement is weaker because both sides read the same corpus.
- **Blocked** — binary-truth verification needs re-dissection, which the pytest suite provides.
- **Known limit** — self-consistency is necessary and not sufficient.
- **Not attempted** — dynamic validation.
