<!-- doc-head: Wave31 byte-bound static discovery and passive-policy gate; direct pytest is local validation only -->
<!-- /doc-head -->

# Stage1229A Wave31 gate

This gate replays1224A/1225A detector evidence,1226A qualified discovery-ledger synchronization,
1227A bilateral PWO admission and1228A master-doc synchronization. Every explicit file binding is
checked against current bytes. Qualified aliases preserve the older global DISC27/28 identities.

The binary limits are mandatory: a call to `ieee80211_free_node` is not association-deletion proof,
the timer comparison requires an established timebase before a millisecond conversion, and1/90
is a parameter ratio rather than measured recovery latency. Runtime causality remains UNKNOWN.

PWO admission remains recommend-only, `auto_approve=false`, with no control actions. Missing or
conflicting bilateral observations cannot authorize a radio, channel, power, reset or width change.

The operator explicitly authorized direct local pytest for this wave, without the unrelated
heavy-slot pool. The actual command is the requested two-suite command; JUnit is configured by
`PYTEST_ADDOPTS`, and its raw argv, exit, log, JUnit and before/after source pins are preserved.
Network calls are denied in the test subprocess. Existing attempt directories are never reused.

```powershell
python tools/verify/verify_stage1229a_wave31_codex1_gate.py --sync --run-tests combined1
```

An offline PASS means current provenance, passive-policy contracts, documentation and local tests
agree. It leaves `physical_ready=false`, `deployment_authorized=false` and RF acceptance unproven.
Wave23 runtime closure is independently recorded; a software test pass cannot fill its missing
native readbacks. The gate itself never connects to a radio or retries native access.

Output: `artifacts/verification/stage1229a_wave31_codex1_gate.json`.
Doc-sync output: `artifacts/verification/stage1228a_master_docs_sync.json`.
