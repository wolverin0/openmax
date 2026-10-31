<!-- doc-head: Stage 1164A master pytest matrix executing every tests/ suite whose filename carries a stage number in 1103A..1156A, per-suite owner and result, other-lane failures recorded not gated, known wave gaps listed -->
# Stage 1164A - master pytest matrix 1103A..1156A

Runner: `tools/verify/run_stage1164a_master_pytest_matrix_1103a_1156a.py`
Receipt: `artifacts/verification/stage1164a_master_pytest_matrix_1103a_1156a.json`
Self-test: `tests/test_stage1164a_master_pytest_matrix.py`

## 1. Method

Discovers `tests/test_stage*.py` with any `NNNNa` token in 1103..1156 and runs
`python -m pytest <file> -q` per file. Owner is `other-lane` for
`test_stage1103a_to_1108a_suite.py` (opencode), else `claude-lane`.

## 2. Gate

`claude_lane_all_green` must be true; status is CONFIRMED only then. `matrix_status` is ALL_GREEN or
PARTIAL over every suite. Other-lane failures are listed in `other_lane_failures` and never gated.

## 3. Result at this checkout

18 suites, 18 passed, `matrix_status` ALL_GREEN, `claude_lane_all_green` true. The opencode suite
reports `45 passed` (the brief expected 3 failed/41 passed; recorded as observed).

## 4. Known gaps

- no 1139A..1144A suite (wave 18 not executed)
- no 1157A..1162A suite (wave 21 not executed); note `tests/test_stage1157a_to_1162a_suite.py` now exists
  but lies outside the 1103A..1156A range, so it is not run here
