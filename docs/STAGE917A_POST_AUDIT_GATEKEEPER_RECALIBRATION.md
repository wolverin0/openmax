<!-- doc-head: Stage 917A replays historical WA/PowerBeam/LTU/Guarida series through the hardened gatekeeper; 0/4 pass the strict paired contract, each with a documented honest reason -->
# Stage 917A — Post-Audit Gatekeeper Recalibration

- **Claim Status**: `CONFIRMED` (offline recalibration)
- **Attribution**: `external controller (offline recalibration)` — no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage917a_post_audit_gatekeeper_recalibration.json`
- **Tool**: `tools/verify/run_stage917a_post_audit_gatekeeper_recalibration.py`
- **Evidence class**: `GATE_RECALIBRATION`

## 1. What it does
Replays representative historical counterbalanced series through the **hardened**
`analysis/regression_gate/gatekeeper.py` (canonical paired-block evaluator,
single-step Šidák, `channel_width_mhz` + `goodput_per_mhz` validation, objective
`CAPACITY_WITH_QOE_CONSTRAINTS`). It also computes an explicit **65536-permutation**
paired sign-flip p-value on the per-block goodput/MHz deltas.

## 2. Result: 0 / 4 series pass the strict gate
| Platform | Verdict | Reason |
| :--- | :--- | :--- |
| PowerBeam PtP (695A) | INCONCLUSIVE | temporal baseline drift 907.9% > 25% (the degraded v4 window) + only 2 paired blocks |
| WA .20↔.250 | NOT_EVALUABLE | `WIDTH_NOT_RECORDED` — historical receipts omit explicit `channel_width_mhz` (audit A05) |
| LTU .110 | NOT_EVALUABLE | no arm-labelled counterbalanced windows in the receipt |
| Guarida | NOT_EVALUABLE | readiness/sim receipts, no counterbalanced A/B bench |

## 3. Reading the result
This is the audit's point made executable: under the hardened contract the historical
series **do not meet the bar** — too few paired blocks, missing channel width, or no
counterbalanced arms. The gate's own drift check even catches the Stage 695A degraded
window (907.9% p99 drift). The strict gatekeeper cannot be made to pass these series
without acquiring compliant new data.

## 4. Reproduce & limits
```sh
python tools/verify/run_stage917a_post_audit_gatekeeper_recalibration.py
python -m pytest tests/test_stage917a_to_922a_suite.py -q
```
The extractor is best-effort over heterogeneous historical schemas; `NOT_EVALUABLE`
means "this receipt does not expose the fields the hardened gate requires", not that
the underlying link was bad. Fresh, schema-complete acquisition is the remedy.
