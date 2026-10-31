<!-- doc-head: Stage 878A - the verifier reads the five receipts 873A through 877A and runs sixty-five checks across per-stage invariants and three cross-stage agreements with zero failures and compliant set to one, including the RX anchor agreement between 873A and 874A, the PB-100 coverage agreement between 874A and 877A and the PB-040 measurement agreement -->
# Stage 878A — verification of the 873A..877A receipts

- **Receipt**: [`artifacts/autoresearch/stage878a_re_pb100_and_ltu_cfo_suite_receipt.json`](../artifacts/autoresearch/stage878a_re_pb100_and_ltu_cfo_suite_receipt.json)
- **Tool**: [`tools/verify/verify_stage878a_re_pb100_and_ltu_cfo_suite.py`](../tools/verify/verify_stage878a_re_pb100_and_ltu_cfo_suite.py)
- **Scope**: offline static verification. Reads five JSON receipts only.

## 0. Final result

```
[878A] stages=5/5 checks=65/65 cross=3 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages present | **5 / 5** |
| checks run | **65** |
| checks passed | **65** |
| cross-stage checks | **3** |
| failures | **0** |
| `compliant` | **1** |

`compliant` is the **emptiness of a named failures list**, so every failure would be printed with its
stage and check name.

## 1. Per-stage invariants

| Stage | Invariants asserted |
| :--- | :--- |
| **873A** | receive vocabulary absent; `ring` word absent; byte space saturated; discriminant uninformative; 2 segments; RX ring not claimed |
| **874A** | 7 images; 0 anchors; 0 container anchor; patch not emitted; 3 VA records; offset-base consistent; 0 collisions; 32-byte minimum gap; combo not claimed verified; fraction 0.1429 |
| **875A** | deficit absent; grant absent; 0 scheduler symbols; airtime is a multicast cap; TXOP is a threshold; 16 UL threshold fields; threshold-and-priority model; no fair queuing |
| **876A** | 10 CFO symbols; 6 chain stages; pass threshold present; IFOE and SFO loop present; hysteresis absent; 4 modulation symbols; auto-switch present; 18 hits of 4096 |
| **877A** | no performance Pareto; two-gate front; cascade detected; binding `PB-070`; 3 applied of 7; ordering not claimed |

Each stage also gets four structural checks: receipt present, `static` in scope, `radio_safety` equals
`static only`, and at least one gap declared.

## 2. The three cross-stage checks

**`rx_anchor_agrees`** — 873A measures zero receive vocabulary in the container, and 874A measures zero
anchors in the container **and** in all seven payloads. Two artefacts, two tools, same conclusion.

**`pb100_coverage_agrees`** — 874A emits no patch, and 877A records PB-100 at coverage 0. The builder and
the planner agree on the gate's state.

**`pb040_measurement_agrees`** — 874A extracts **3** virtual-address records, and 877A records PB-040 with
evidence **3** and **3** verified roles. The address count and the evidence grade come from the same
receipt and must not drift apart.

That last check is the one that would catch a specific silent failure: if someone extended PB-040 with a
fourth role, 874A's address count would rise while 877A's evidence grade stayed at 3, and the mismatch
would surface here rather than in a downstream report.

## 3. Corrections this batch forced

Two of my own readings were wrong before the verifier was satisfied:

1. **876A** — I expected **two** CFO symbols and wrote the docstring around a two-entry chain. The symbol
   census returned **ten**, including `cfo_pass_threshold`, which I had assumed was absent. The
   document was rewritten before publication, so the threshold now appears where it belongs.
2. **873A** — I initially treated the 32-bit candidate scan as a usable lead. It returns **16 of 16**
   values, which is a signature of zero-padding rather than a discrimination, so the scan is recorded as
   offsets with **no attribution**.

Recording these matters because both would have produced a wrong headline: a missing threshold that
exists, and a lead that is noise.

## 4. What the verifier does not do

**`REFUTED`**: it does not re-dissect a binary.

Its own gaps say so:

> *"the verifier checks receipt self-consistency, not binary truth: a consistent wrong value would
> pass"*

The pytest suite covers reproducibility separately by re-running every tool and comparing receipt bytes,
and every tool in this batch writes atomically so an interrupted run cannot leave a half-written
receipt.

## 5. What is established

| Claim | Status |
| :--- | :-: |
| all five receipts are present and readable | **CONFIRMED** (5/5) |
| all five declare `static` scope and `static only` safety | **CONFIRMED** |
| all five declare at least one gap | **CONFIRMED** |
| 873A and 874A independently agree PB-100 has no RX anchor | **CONFIRMED** |
| 874A and 877A agree PB-100 has zero coverage | **CONFIRMED** |
| 874A and 877A agree PB-040 carries 3 measured roles | **CONFIRMED** |
| the suite is compliant | **CONFIRMED** (`compliant = 1`) |
| the verifier proves binary truth | **REFUTED** |

## 6. The operational reading

Three things a reader can rely on after this stage:

1. the five receipts are **mutually consistent**, including two independent PB-100 measurements;
2. **no stage over-claims** — every `*_recovered = 0` flag is still zero, including
   `airtime_deficit_recovered`, `ul_grant_recovered`, `rx_ring_recovered` and
   `modulation_hysteresis_recovered`;
3. the negatives are **explicit**: no receive vocabulary, no RX anchor in 7 images, no deficit counter,
   no UL grant, no hysteresis name, no performance Pareto.

And one thing not to infer: that the measurements are correct. The verifier never touched a binary.

## 7. Gaps

- **`UNKNOWN`** — whether any recorded value is wrong but consistently recorded.
- **`UNKNOWN`** — whether the cross-stage agreements are weaker because both sides read the same corpus.
- **Blocked** — binary-truth verification needs re-dissection, which the pytest suite provides.
- **Known limit** — self-consistency is necessary and not sufficient.
- **Not attempted** — dynamic validation.
