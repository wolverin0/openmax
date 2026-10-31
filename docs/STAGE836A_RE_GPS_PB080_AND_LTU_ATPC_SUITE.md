<!-- doc-head: Stage 836A - the verifier reads the five receipts 831A through 835A and runs forty-four checks across per-stage invariants and two cross-stage agreements, all passing, including the check that 832A and 833A independently agree no PB-080 anchor exists and that the AC and LTU ATPC spellings do not contradict -->
<!-- /doc-head -->
# Stage 836A — verification of the 831A..835A receipts

- **Receipt**: [`artifacts/autoresearch/stage836a_re_gps_pb080_and_ltu_atpc_suite_receipt.json`](../artifacts/autoresearch/stage836a_re_gps_pb080_and_ltu_atpc_suite_receipt.json)
- **Tool**: [`tools/verify/verify_stage836a_re_gps_pb080_and_ltu_atpc_suite.py`](../tools/verify/verify_stage836a_re_gps_pb080_and_ltu_atpc_suite.py)
- **Scope**: offline static verification. Reads five JSON receipts only.

## 0. Final result

```
[836A] stages=5/5 checks=44/44 cross=2 failures=0 compliant=1
```

| Metric | Value |
| :--- | :-: |
| stages present | **5 / 5** |
| checks run | **44** |
| checks passed | **44** |
| cross-stage checks | **2** |
| failures | **0** |
| `compliant` | **1** |

## 1. Per-stage invariants

| Stage | Invariants asserted |
| :--- | :--- |
| **831A** | `1pps` absent; `pps` is VoIP rate; `frame_start_offset` absent; guard field present; ATPC has 3 controls; panel alignment not claimed |
| **832A** | firmware queue vocabulary absent; host queue vocabulary absent; no PB-080 point claimed |
| **833A** | 7 images; 0 viable PB-080 images; patch not emitted; Penta-Patch at 3 of 5 |
| **834A** | `atpc` absent on LTU; `autopwr` named; per-MCS adjust present; target EVM absent; gain matrix not overclaimed |
| **835A** | `uav` zero-byte in all copies; validator not named; persistence is tar; schema not recovered |

Each stage also gets four structural checks: receipt present, `static` in scope, `radio_safety` equals
`static only`, and at least one gap declared.

## 2. The cross-stage checks are where this verifier earns its keep

**`pb080_anchor_agrees`**: 832A reports `anchor_available = 0` and 833A reports
`pb080_viable_images = 0`. These are **two independent measurements on different artefacts** — one on
the container, one on the 7 kit payloads — and they agree.

That is the strongest statement in the suite: PB-080 is blocked **on the evidence**, not because one
tool searched badly.

**`atpc_naming_is_line_specific`**: 831A reports `atpc_control_count = 3` on the **AC** side; 834A
reports `atpc_name_absent = 1` on the **LTU** side. Those two findings **look contradictory** if read
naively — one says `atpc` exists, the other says it does not.

The check confirms they are **compatible**: the names are line-specific, and neither stage claims the
other's spelling exists on its own line. Without this check a later reader could reasonably conclude
one of the two receipts is wrong.

A 44-check suite with one genuine cross-artefact agreement and one anti-contradiction check is worth
more than 44 self-consistency checks.

## 3. What the verifier does not do

**`REFUTED`**: it does **not** re-dissect a binary.

Its own gaps say so:

> *"the verifier checks receipt self-consistency, not binary truth: a consistent wrong value would
> pass"*

So it catches **drift and inconsistency** — a missing `static` word, a count that does not sum, two
stages disagreeing on the same fact. It cannot catch a wrong measurement. The pytest reproducibility
tests cover that separately by re-running each tool.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| all five receipts are present and readable | **CONFIRMED** (5/5) |
| all five declare `static` scope and `static only` safety | **CONFIRMED** |
| all five declare at least one gap | **CONFIRMED** |
| 832A and 833A independently agree PB-080 is blocked | **CONFIRMED** |
| the AC and LTU ATPC spellings are compatible, not contradictory | **CONFIRMED** |
| the suite is compliant | **CONFIRMED** (`compliant = 1`) |
| the verifier proves binary truth | **REFUTED** |

## 5. The operational reading

Three things a reader can rely on after this stage:

1. **the five receipts are mutually consistent**, including two independent PB-080 measurements;
2. **no stage over-claims** — every `*_recovered = 0` flag is still zero;
3. **the negatives are explicit** — no 1PPS, no frame-start offset on AC, no queue vocabulary, no
   viable PB-080 image, no target EVM, no key validator, no readable `uav`.

And one thing not to infer: that the measurements are correct. The verifier never touched a binary.

## 6. Gaps

- **`UNKNOWN`** — whether any recorded value is wrong but consistently recorded.
- **`UNKNOWN`** — whether the two PB-080 measurements share a mistaken assumption; agreement is
  weaker when both tools were written by the same author from the same reading.
- **Blocked** — binary-truth verification needs re-dissection, which the pytest suite provides.
- **Known limit** — self-consistency is necessary and not sufficient.
- **Not attempted** — dynamic validation.
