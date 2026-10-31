<!-- doc-head: Stage 877A - the seven-gate PB-040 to PB-100 Pareto keeps the same two-gate front of PB-040 against PB-050 and the same serial cascade with a seventh zero, while the completion fraction falls from three of six to three of seven without any gate being lost, and the binding constraint remains PB-070 -->
# Stage 877A — PB-040 to PB-100 hepta-patch Pareto

- **Receipt**: [`artifacts/autoresearch/stage877a_pb040_to_pb100_hepta_patch_pareto.json`](../artifacts/autoresearch/stage877a_pb040_to_pb100_hepta_patch_pareto.json)
- **Tool**: [`tools/sim/run_stage877a_pb040_to_pb100_hepta_patch_pareto.py`](../tools/sim/run_stage877a_pb040_to_pb100_hepta_patch_pareto.py)
- **Scope**: offline static simulation. Reads JSON receipts. No firmware written, no flash touched.

## 0. The performance axis is still refused

**`REFUTED`**: `performance_pareto_available = 0`.

No gate receipt in this corpus carries a measured goodput, a `p50`/`p95`/`p99` latency or a QoE score.
A gain column could be produced and would be **invented**, so the axis is excluded and the exclusion is
recorded under `axes.excluded` — the same refusal as Stage 859A, restated because adding a gate does not
create a measurement.

What remains is measured from receipts.

## 1. The measured table

| Gate | evidence | coverage | blockers | basis |
| :--- | :-: | :-: | :-: | :--- |
| **PB-040** | **3** | 7 | **3** | 3 roles anchored, expected and observed diff both 4 bytes |
| **PB-050** | 2 | 7 | **1** | live lap120 qualification; listed unmet for PB-060 |
| **PB-060** | 2 | 7 | 3 | campaign passed, 2 unmet prerequisites, not ready |
| **PB-070** | 0 | 0 | 2 | policy-locked, not ready |
| **PB-080** | 0 | 0 | 1 | no anchor, no patch |
| **PB-090** | 0 | 0 | 1 | no anchor, no patch |
| **PB-100** | 0 | 0 | 1 | no anchor, no patch |

Coverage comes from three measured sources and each row records which one: the Stage 833A kit manifest
for PB-040 through PB-080, the Stage 856A probe for PB-090, and the Stage 874A probe for PB-100.

## 2. The seventh gate changes the fraction, not the front

**`CONFIRMED`**: `front_size = 2`, `front = ["PB-040", "PB-050"]`.

The front is **identical to Stage 859A**. PB-100 has zero evidence, zero coverage and one blocker, so
PB-050 dominates it exactly as it dominates PB-080 and PB-090. Adding a blocked gate cannot change a
front built on evidence and coverage.

**`CONFIRMED`**: `applied_gates = 3`, `completion_fraction = 0.4286`.

| Measure | Stage 859A (6 gates) | Stage 877A (7 gates) |
| :--- | :-: | :-: |
| applied gates | **3** | **3** |
| completion fraction | 0.5 | **0.4286** |

The fraction fell by **seven points** while **no gate was lost**. This is the same arithmetic trap Stage
856A flagged when the penta-patch became the hexa-patch. A reader comparing these stages must compare
**counts**; comparing fractions would suggest a regression that did not happen.

## 3. The cascade still binds at PB-070

**`CONFIRMED`**: `coverage_sequence = [7, 7, 7, 0, 0, 0, 0]`, `cascade_detected = 1`,
`binding_constraint = "PB-070"`.

The sequence is monotone non-increasing, so the seven gates form a **serial chain**. Dominance compares
gates as if they were alternatives; here they are stages.

PB-100 joins the queue behind PB-070. A perfect PB-100 patch would be **as unreachable** as a perfect
PB-090 one, so the priority order does not change:

1. **PB-070** — a policy decision, not analysis;
2. **PB-080, PB-090, PB-100** — all three need anchors that do not exist in the corpus;
3. **PB-040 and PB-050** — the only two real candidates once the chain moves.

## 4. What is established

| Claim | Status |
| :--- | :-: |
| a performance Pareto is computable offline | **REFUTED** |
| the non-dominated set has two members | **CONFIRMED** |
| adding PB-100 changed the front | **REFUTED** (still PB-040 and PB-050) |
| adding PB-100 lowered the completion fraction | **CONFIRMED** (0.5 to 0.4286) |
| adding PB-100 lost an applied gate | **REFUTED** (3 before, 3 after) |
| the seven gates form a cascade | **CONFIRMED** |
| the binding constraint is PB-070 | **CONFIRMED** |
| the gates can be ordered by merit | **REFUTED** (`ordering_available = 0`) |

## 5. The operational reading

1. **Nothing about the priority order changed.** A seventh blocked gate does not create work; it queues
   behind the same decision.
2. **The only number that moved is the denominator.** Track `applied_gates`, not the fraction, or the
   series will appear to regress every time a blocked gate is added.
3. **Do not cite a gain figure.** None exists for any of the seven gates.

## 6. Gaps

- **`UNKNOWN`** — every performance effect of every gate; nothing was measured on air.
- **`UNKNOWN`** — whether PB-100 would even be reachable if anchored, since PB-070 gates the chain.
- **`UNKNOWN`** — which of the two PB-050 receipts is current.
- **Known limit** — a dominance test over three coarse axes is a planning aid, not a measurement.
- **Not attempted** — any execution, any dynamic validation.
