<!-- doc-head: Stage 945A times the post-audit pytest suites with --durations=25, reports wall-clock and flags tests slower than 10s -->
# Stage 945A - Pytest Execution-Time Audit

- **Claim Status**: `CONFIRMED` (offline audit)
- **Attribution**: `external controller (offline audit)`; no radio, no SSH
- **Artifact**: `artifacts/autoresearch/stage945a_pytest_execution_time_audit.json`
- **Tool**: `tools/verify/build_stage945a_pytest_execution_time_audit.py`
- **Evidence class**: `PYTEST_TIMING_AUDIT`

## Result
- Suites: `test_stage885a_to_890a_suite.py`, `test_stage917a_to_922a_suite.py`, `test_stage837a_to_842a_suite.py`
- Pytest: 22 passed in 0.65s
- Total wall-clock: **1.54 s**
- Slow tests (> 10.0 s): **0**

## Top durations
| s | phase | test |
| :--- | :--- | :--- |
| 0.0 | call | `test_stage887a_classifier` |
| 0.0 | call | `test_stage885a_field_kits_hardened` |
| 0.0 | setup | `test_stage885a_field_kits_hardened` |
| 0.0 | call | `test_stage919a_loss_attribution` |
| 0.0 | call | `test_stage886a_aa_control_selftests` |
| 0.0 | call | `test_stage889a_power_arithmetic` |
| 0.0 | call | `test_stage888a_reclassification_flags` |
| 0.0 | call | `test_stage890a_gate_and_master_doc_sync` |
| 0.0 | call | `test_stage917a_recalibration` |
| 0.0 | call | `test_stage920a_docs_audit` |
| 0.0 | call | `test_stage837a_model_invariants` |
| 0.0 | call | `test_stage922a_gate` |
| 0.0 | call | `test_stage921a_master_sync` |
| 0.0 | call | `test_stage918a_false_positive_within_alpha` |
| 0.0 | call | `test_stage839a_invariants` |
| 0.0 | call | `test_stage837a_vht80_loses_range_under_stress` |
| 0.0 | call | `test_stage838a_pareto_invariants` |
| 0.0 | call | `test_stage842a_suite_gate_receipt` |
| 0.0 | call | `test_stage840a_kpis` |
| 0.0 | call | `test_stage841a_ledger_invariants` |
| 0.0 | call | `test_stage839a_anomaly_and_airtime_fairness` |
| 0.0 | call | `test_stage838a_knee_respects_safe_envelope` |
| 0.0 | call | `test_stage841a_airtime_fairness_is_significant` |
| 0.0 | teardown | `test_stage885a_field_kits_hardened` |
| 0.0 | teardown | `test_stage842a_suite_gate_receipt` |

## Reproduce
```sh
python tools/verify/build_stage945a_pytest_execution_time_audit.py
python -m pytest tests/test_stage945a.py -q
```
Limit: timings are a point-in-time, machine-dependent snapshot.
