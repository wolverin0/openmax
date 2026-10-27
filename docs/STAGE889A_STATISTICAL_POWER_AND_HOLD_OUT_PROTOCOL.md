<!-- doc-head: Stage 889A statistical power & hold-out resolution protocol (A07 remediation); reproduces N=500 Sidak alpha vs permutation min-p incompatibility, deterministic arithmetic -->
# Stage 889A — Statistical Power & Hold-Out Resolution Protocol

- **Claim Status**: `CONFIRMED` (offline arithmetic)
- **Attribution**: `external controller (offline arithmetic)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage889a_statistical_power_and_holdout_protocol.json`
- **Tool**: `tools/verify/build_stage889a_statistical_power_and_holdout_protocol.py`
- **Evidence class**: `DERIVED_ARITHMETIC`

## 1. The A07 problem, reproduced
With one-step Šidák correction `alpha = 1-(1-0.05)^(1/N)` and a paired test whose
smallest achievable two-sided p is `2/2^n` (exact enumeration, n ≤ 14 pairs) or the
permutation floor `1/(perm+1)` above that, a large hypothesis count makes the gate
unable to reject **any** effect, however large.

**Headline case N = 500:**
| Quantity | Value |
| :--- | :--- |
| Šidák alpha | 0.00010258 |
| min p (14 pairs, exact) | 0.00012207 |
| min p (permutation, 4096) | 0.00024408 |
| Verdict | **UNDER_POWERED — no effect can pass** |

Both minimum achievable p-values exceed the corrected alpha — matching the audit's
A07 arithmetic exactly.

## 2. Resolution table
The receipt enumerates `sidak_alpha` and `min_achievable_p` for
`N ∈ {1,10,50,100,500,1000}` × `n_pairs ∈ {8,12,14,20}` with a `can_ever_reject`
flag, so any planned configuration can be power-checked before acquisition.

## 3. Protocol (A06/A07 remediation)
1. **Pre-register the contract** (LATENCY_WITH_CAPACITY_NONINFERIORITY,
   CAPACITY_WITH_QOE_CONSTRAINTS, ROBUSTNESS, CAPABILITY_DISCOVERY) before the trial.
2. **Power-check first**: require `min_achievable_p ≤ corrected alpha` for the planned
   `n_pairs` and `N` before acquiring data.
3. **No alpha inflation** to force a pass — increase `n_pairs` or cut hypotheses.
4. **Hold-out identity** disjoint from discovery (ids + raw hashes; see Stage 886A).
5. **Sequential budget**: track attempts/revisions against a persistent family-wise
   budget — a one-step Šidák is not a sequential budget.

## 4. Reproduce & limits
```sh
python tools/verify/build_stage889a_statistical_power_and_holdout_protocol.py
python -m pytest tests/test_stage885a_to_890a_suite.py -q
```
Pure arithmetic over the stated model (exact sign-flip enumeration and permutation
floor); it characterizes resolution, not the power of any specific effect size. It
prescribes the protocol; wiring it into `analysis/regression_gate/gatekeeper.py`
(owned by another lane) is a separate change.
