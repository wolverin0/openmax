<!-- doc-head: Stage1066A offline adapters/parsers gate with exact-source replay and separate unresolved physical acceptance -->
The local suite verifies native grammar, parser semantics, saved-evidence integrity and honest measurement limits.
<!-- /doc-head -->

# Stage1066A — Offline PtP adapters and parsers gate

The gate binds only the six new stage modules, their six documents, exact receipts and the saved native evidence required by Stage1024A. It performs no SSH, network access, live traffic, debugfs writes, firmware loading or deployment.

It checks:

- Stage1061A owner-specific AQM payloads and numeric AQL indices, canonical unsigned values, safe paths and requested-field readbacks.
- Stage1062A bounded `/bin/uclient-fetch` plans, actual receiver-byte/time parsing, ICMP packet-size semantics and non-exact interface-counter consistency.
- Stage1063A peer/interface identity, VHT-MCS/NSS, chain signals, optional counters and guarded counter deltas.
- Deterministic regeneration of the historical Stage697A reconciliation and exact saved-receipt readiness matrix.
- Initial paired doc-heads, fewer than180 lines, declared evidence hashes and preservation of the old Stage1024A215-pass revision.

The two requested suites are:

```powershell
python -m pytest tests/test_stage1019a_to_1024a_suite.py tests/test_stage1061a_to_1066a_suite.py
```

The coordinator captures actual argv, exit status, stdout and JUnit XML after all source/doc files are frozen. The final validation binds these files, then generated receipts are refreshed in order1024A,1064A,1065A,1066A. Generated receipts are excluded from validation-source pins to avoid circular hashes. Earlier failed runs remain preserved.

```powershell
python tools/verify/verify_stage1066a_ptp_adapters_and_parsers_gate.py --validation PATH_TO_FINAL_VALIDATION_JSON
```

Output: `artifacts/autoresearch/stage1066a_ptp_adapters_and_parsers_gate.json`. Exit0 means the offline checks passed. It does not mean a live link or production campaign passed. The JSON records `physical_ready=false`, no deployment authority, the pending physical criteria and whether fresh pytest evidence is bound.

Without `--validation`, semantic/source checks can run, but `fresh_pytest_bound=false` prevents presenting them as a newly verified test campaign. New ICMP plans remain unexecuted and are never labeled UDP application QoE. Missing counters remain unknown; a failed admission result is retained rather than retried until green.
