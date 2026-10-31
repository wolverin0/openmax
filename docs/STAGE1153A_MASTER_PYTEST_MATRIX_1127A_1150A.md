<!-- doc-head: Stage 1153A master pytest matrix over every stage-numbered suite 1127A..1150A; per-suite rc and summary, claude-lane vs other-lane, recorded honestly -->
# Stage 1153A - master pytest matrix 1127A..1150A

Evidence class: MASTER_PYTEST_MATRIX_1127A_1150A (offline, no devices touched).

- matrix_status: `ALL_GREEN`; claude_lane_status: `ALL_GREEN`; status: `CONFIRMED`
- Known gap: no 1139A..1144A suite exists (wave 18 not executed).

| file | stage | owner | rc | summary |
| --- | --- | --- | --- | --- |
| `tests/test_stage1127a_cohort_stats.py` | 1127A | other-lane | 0 | 6 passed in 0.42s |
| `tests/test_stage1127a_to_1132a_suite.py` | 1127A..1132A | claude-lane | 0 | 16 passed in 0.35s |
| `tests/test_stage1133a_to_1138a_suite.py` | 1133A..1138A | other-lane | 0 | 53 passed in 1.27s |
| `tests/test_stage1135a_1136a_passive_contracts.py` | 1135A..1136A | other-lane | 0 | 22 passed in 0.52s |
| `tests/test_stage1145a_ltulite_passive_safety_fence.py` | 1145A | claude-lane | 0 | 7 passed in 0.32s |
| `tests/test_stage1145a_to_1150a_suite.py` | 1145A..1150A | claude-lane | 0 | 18 passed in 0.33s |
| `tests/test_stage1146a_ptp_v16_v17_parity.py` | 1146A | claude-lane | 0 | 5 passed in 0.32s |

Other-lane failures are recorded, not gated. Runner: `tools/verify/run_stage1153a_master_pytest_matrix_1127a_1150a.py`
Receipt: `artifacts/verification/stage1153a_master_pytest_matrix_1127a_1150a.json`
