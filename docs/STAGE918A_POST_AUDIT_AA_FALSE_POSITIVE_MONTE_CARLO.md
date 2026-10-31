<!-- doc-head: Stage 918A offline A/A false-positive Monte Carlo (1000 null campaigns) through the hardened gatekeeper; FP rate 0.1% <= alpha, gate does not manufacture wins from noise -->
# Stage 918A — A/A False-Positive Monte Carlo

- **Claim Status**: `CONFIRMED` (offline Monte Carlo)
- **Attribution**: `external controller (offline Monte Carlo)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage918a_post_audit_aa_false_positive_monte_carlo.json`
- **Tool**: `tools/sim/run_stage918a_post_audit_aa_false_positive_monte_carlo.py`
- **Evidence class**: `SIMULATED_MODEL_ONLY`

## 1. What it does
Builds a true-null baseline pool (A and B drawn from the **same** distribution — any
"win" is a false positive) and replays **1000 A/A campaigns** (6 paired blocks each,
seeded) through the hardened `RegressionGatekeeper` via its own
`run_aa_null_replay_validation` harness, measuring the false-positive rate against α.

## 2. Result
| Quantity | Value |
| :--- | :--- |
| Trials | 1000 |
| Verdicts | REJECT 380, INCONCLUSIVE 619, SYNTHETIC_PASS 1, KEEP/PROMOTE 0 |
| False positives (KEEP+PROMOTE+SYNTHETIC_PASS) | 1 |
| **False-positive rate** | **0.1 %** |
| α | 0.05 |
| Within α | **yes** |

## 3. Reading the result
Under a genuine null the hardened gate promotes essentially nothing: 0 KEEP/PROMOTE
and a single SYNTHETIC_PASS out of 1000 → FP rate 0.1 % ≤ α = 5 %. The strict Šidák
paired contract does **not** manufacture wins from noise, which is the property the
audit (A03/A07) demanded. (The lone SYNTHETIC_PASS is correctly labelled synthetic,
not a physical promotion.)

## 4. Reproduce & limits
```sh
python tools/sim/run_stage918a_post_audit_aa_false_positive_monte_carlo.py
python -m pytest tests/test_stage917a_to_922a_suite.py -q
```
A null-model check of the gate's calibration, not a statement about any real
campaign; it confirms the gate's false-positive control, not its power on true effects
(that is Stage 889A's resolution analysis).
