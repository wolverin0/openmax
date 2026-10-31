<!-- doc-head: Stage1093A offline comparison of current v15/v16/v17 kit source and rollback limits -->
SHA256-bound source evidence is separate from native execution and physical acceptance.
<!-- /doc-head -->

# Stage1093A PtP kit comparison

This audit reads the current WA v15/v16/v17 kits, PowerBeam v16/v17 kits and three common champion hotplugs. A separate PowerBeam v15 kit is not declared; that row stays UNKNOWN rather than borrowing WA identity.

| Source family | v15 | v16 | v17 |
|---|---|---|---|
| WA kit | Metadata `stat` and optional `tc` backend references; transient queue transaction | Numeric AQL; BC/MC readback; default policy plus persistence files | Numeric AQL, threshold, optional named AQM writes and lowat; runtime controls |
| PowerBeam kit | UNKNOWN: no separate declared kit | Numeric AQL with same-process link polling and manual restore | Adds named AQM/threshold/lowat controls to same-process link polling |
| Common hotplug | Scalar `aql_txq_limit` write conflicts with the numeric three-field grammar | Same scalar-write mismatch | Numeric AQL and named AQM payloads; final exit0 is not a complete readback guarantee |

The source receipt stores exact file paths, SHA256 hashes, line-numbered evidence, profile assignments and known unsupported-applet findings. The inherited Stage1025A sanitizer excludes comments and strings when checking executable applet references; its known-pattern scope does not prove that every used applet exists on a target.

AQM is one debugfs file accepting named payloads such as `fq_quantum 1514`. AQL takes numeric indices0..3 with low/high values. A displayed AC label or a scalar value alone is not evidence of valid write syntax. The analyzer records source patterns and their limits; it is not a full shell interpreter.

Manual rollback code, snapshot code, readback checks and a loop waiting for a link are reported independently. Same-process polling cannot restore state after its own SIGKILL. This wave supplies no native restoration, loss-free baseline, workload, autonomous watchdog or production-acceptance proof.

WA v16 persistence handling differs from v17 runtime controls. Profile values also differ by kit; this comparison does not normalize them, recommend a new profile or certify their performance.

```powershell
python tools/autoresearch/ptp_v16_vs_v17_kit_comparison_matrix.py
```

Receipt: `artifacts/autoresearch/stage1093a_ptp_v15_v16_v17_kit_comparison_matrix.json`.

No kit, SSH command, firmware operation, RF traffic or radio write is executed. Local syntax checks, if recorded, are Bash parser checks only and do not certify BusyBox runtime compatibility.
