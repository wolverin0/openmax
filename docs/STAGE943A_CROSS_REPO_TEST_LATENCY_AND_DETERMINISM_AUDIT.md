<!-- doc-head: Stage 943A offline audit of post-audit pytest suite latency and generator seed determinism; receipt in artifacts/autoresearch/stage943a_*.json -->
# Stage 943A - Test latency and determinism audit

Offline. No live devices touched.

## Suite latency
- Suites run: 4 (tests/test_stage885a_to_890a_suite.py, tests/test_stage917a_to_922a_suite.py, tests/test_stage837a_to_842a_suite.py, tests/test_stage867a_to_872a_suite.py)
- Wall-clock: 1.428 s, pytest returncode 0
- Tail: `30 passed in 0.80s`

## Determinism (static seed scan of tools/sim + tools/verify)
- Files scanned: 224; seeded: 47; seeded_fraction: 0.2098
- Signal regex: `seed = N`, `random.Random(`, `np.random.default_rng(`, `default_rng(`.
- A file with no signal may simply use no randomness; this is a presence check, not proof of nondeterminism.
- Unseeded files: 177 (full per-file list in the JSON receipt).

## Run
`python tools/verify/build_stage943a_cross_repo_test_latency_and_determinism_audit.py`
`python -m pytest tests/test_stage943a.py -q`
