<!-- doc-head: Stage1117A exact five-suite offline pytest matrix, saved input archives and strict evidence replay -->
No SSH, network connections or radio operations are performed by this runner.
<!-- /doc-head -->

# Stage1117A — consolidated offline pytest

The runner executes precisely these requested files, preserving each actual argv, exit code, stdout/stderr log, JUnit XML and testcase identity:

- `tests/test_stage1079a_to_1084a_suite.py`
- `tests/test_stage1085a_to_1090a_suite.py`
- `tests/test_stage1091a_to_1096a_suite.py`
- `tests/test_stage1097a_to_1102a_suite.py`
- `tests/test_stage1103a_to_1108a_suite.py`

Source/test/kit bytes are hashed before and after execution. Every original input has a hash-addressed archive. Missing, substituted, duplicate, empty, skipped, failed, unbound or changed evidence prevents a passing matrix.

The reviewed 1085A..1090A and1107A..1108A fixtures run only their local static producers and can regenerate their own receipt/document outputs. These changes are recorded separately from source drift; other data changes remain failures. No stage producer that contacts a radio is invoked.

Python children inherit a network-denial guard. Its `Popen` subclass preserves Windows asyncio class semantics while rejecting direct network-tool executables. Guard attempts are retained and make the matrix fail.

Run under the machine-wide heavy-job semaphore:

```powershell
node ../wezbridge/scripts/heavy-slot.cjs run -- python tools/verify/run_stage1117a_consolidated_pytest_1079a_1108a.py --attempt matrix1
```

An existing attempt directory cannot be overwritten. Prior failures remain available. `replay_receipt(record)` independently checks exact mandatory input sets, archive coverage, hashes, commands, XML, raw log counts, native integer exit codes and all five suites.

Pass counts describe offline testcase executions. They do not supply new A/A, discovery, holdout, OTA, production or rollback measurements. The adjacent JSON receipt is the authority for actual counts and missing prerequisites.
