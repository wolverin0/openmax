<!-- doc-head: Stage 859A - a performance Pareto is not computable offline because no gate carries a measured goodput or latency result, so the analysis runs on measured evidence and coverage instead and returns a two-gate front of PB-040 against PB-050 inside a serial cascade whose coverage is seven seven seven zero zero zero and whose binding constraint is PB-070 -->
<!-- /doc-head -->
# Stage 859A — PB-040 to PB-090 hexa-patch Pareto

- **Receipt**: [`artifacts/autoresearch/stage859a_pb040_to_pb090_hexa_patch_pareto.json`](../artifacts/autoresearch/stage859a_pb040_to_pb090_hexa_patch_pareto.json)
- **Tool**: [`tools/sim/run_stage859a_pb040_to_pb090_hexa_patch_pareto.py`](../tools/sim/run_stage859a_pb040_to_pb090_hexa_patch_pareto.py)
- **Scope**: offline static simulation. Reads JSON receipts. No firmware written, no flash touched.

## 0. What this stage refuses to do

The stage name says Pareto, and the obvious axes are goodput, latency and QoE. **None of them exist.**

**`REFUTED`**: `performance_pareto_available = 0`.

No gate receipt in this corpus carries a measured goodput, a `p50`/`p95`/`p99` latency, or a QoE score
for any of the six patches. A gain column could be produced — a plausible curve, a tidy front, a
confident conclusion — and it would be **invented**. So the axis is excluded and the exclusion is
recorded in the receipt under `axes.excluded`.

What remains is **measured**, and it is enough to order the work.

## 1. The three axes, and their sources

| Axis | Scale | Source |
| :--- | :--- | :--- |
| `evidence` | 0 absent, 1 receipt-gated, 2 live-measured, **3 anchored and byte-verified** | per-gate receipt |
| `coverage` | kit images carrying the gate, 0 to 7 | `stage833a.penta_patch.baked_counts`, and the 856A anchor probe for PB-090 |
| `blockers` | count of false or required flags | per-gate receipt |

**`CONFIRMED`**: every coverage value in the table is read from a receipt field, not asserted by this
tool. PB-090 is the one exception, and it uses the 856A probe across the same seven images because no
kit badge exists for it.

## 2. The measured table

| Gate | evidence | coverage | blockers | basis |
| :--- | :-: | :-: | :-: | :--- |
| **PB-040** | **3** | 7 | **3** | 3 roles anchored, 4-byte diff observed and expected |
| **PB-050** | 2 | 7 | **1** | live lap120 silicon qualification on record |
| **PB-060** | 2 | 7 | 3 | campaign passed, 2 unmet prerequisites, not ready |
| **PB-070** | 0 | 0 | 2 | policy-locked, not ready |
| **PB-080** | 0 | 0 | 1 | no anchor, no patch |
| **PB-090** | 0 | 0 | 1 | no anchor, no patch |

## 3. The front is two gates, and it is a real trade-off

**`CONFIRMED`**: `front_size = 2`, `front = ["PB-040", "PB-050"]`, `front_is_degenerate = 0`.

These two trade off **genuinely**:

- **PB-040** has the strongest evidence in the corpus — an anchored rename, three roles, expected and
  observed diff both 4 bytes — and `3` blockers: flash not allowed, automatic execution not allowed,
  operator gate required.
- **PB-050** has weaker evidence, `2`, and only `1` blocker.

Neither dominates the other, so both are on the front. Everything else is dominated: **PB-060** by
PB-050 (equal evidence and coverage, three blockers against one), and **PB-070**, **PB-080** and
**PB-090** by PB-050 on evidence.

This contradicts my own expectation. I designed the tool expecting a **degenerate** front, on the theory
that correlated axes would put most gates on it. The measurement returned a **minimal front of two**,
which is a more useful result and required correcting the verifier rather than the data.

## 4. The cascade is the finding that ordering depends on

**`CONFIRMED`**: `coverage_sequence = [7, 7, 7, 0, 0, 0]` and `cascade_detected = 1`.

Coverage is **monotone non-increasing** across PB-040 to PB-090, so the six gates form a **serial
dependency chain**, not a menu. A Pareto ranking cannot order a chain: dominance compares gates as if
they were alternatives, and here they are **stages**.

**`CONFIRMED`**: `binding_constraint = "PB-070"`.

The binding constraint is the **first gate in sequence with zero coverage**, and everything after it is
unreachable regardless of its own merit. Concretely: a perfect PB-090 patch would be **unreachable**
while PB-070 stays policy-locked. Effort spent on PB-080 or PB-090 today buys nothing that can be
applied.

## 5. A contradiction this stage does not adjudicate

**`CONFIRMED`**: `pb050_status_conflict = 1`.

`pb_060_070_pilot_and_verdict.json` lists **PB-050** among the **unmet prerequisites of PB-060**.
A separate receipt records a **live lap120 silicon qualification** for PB-050.

Both cannot be current. Either the prerequisite list is stale, or the qualification did not satisfy the
gate. This stage records both and chooses **neither**, because choosing would require a judgement about
which receipt supersedes the other, and nothing in the bytes supports that.

The conflict is visible in the table above: PB-050 carries `evidence = 2` and `blockers = 1` at the same
time, and both are true statements about different receipts.

## 6. What is established

| Claim | Status |
| :--- | :-: |
| a performance Pareto is computable offline | **REFUTED** (no measured gain) |
| the axes used are measured from receipts | **CONFIRMED** |
| the non-dominated set has two members | **CONFIRMED** (`PB-040`, `PB-050`) |
| PB-040 dominates the tail gates | **REFUTED** (its 3 blockers prevent dominance) |
| the six gates form a cascade | **CONFIRMED** (coverage monotone) |
| the binding constraint is PB-070 | **CONFIRMED** (first zero-coverage gate) |
| the gates can be ordered by merit | **REFUTED** (`ordering_available = 0`) |
| PB-050's status is consistent across receipts | **REFUTED** (conflict recorded, not resolved) |

## 7. The operational reading

1. **PB-070 is the only gate that matters today.** It is policy-locked, so it needs a decision, and
   the other five are queued behind it.
2. **PB-040 and PB-050 are the two real candidates** when PB-070 moves, and the choice between them is
   a trade-off between evidence strength and the number of blockers — not a performance question.
3. **PB-080 and PB-090 should not be prioritised**, not because they are weak, but because they are
   unreachable and unanchored.
4. **Do not cite a gain figure for any gate.** None exists, and this stage deliberately produced none.

## 8. Gaps

- **`UNKNOWN`** — every performance effect of every gate; nothing was measured on air.
- **`UNKNOWN`** — which of the two PB-050 receipts is current.
- **`UNKNOWN`** — whether PB-060's campaign result would survive PB-050 being satisfied.
- **Known limit** — a dominance test over three coarse axes is a planning aid, not a measurement.
- **Not attempted** — any execution, any dynamic validation.
