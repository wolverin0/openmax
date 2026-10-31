<!-- doc-head: Stage1115A offline WA V17 transaction planning, complete readback and synthetic fault model; native admission remains blocked -->
Saved captures are read only; no kit, SSH, device write or watchdog is executed.
<!-- /doc-head -->

# Stage1115A WA V17 transaction planner and verifier

The planner extracts the actual `T_*` constants from the hash-bound WA V17 kit. Native configuration is reconstructed from the saved Stage1021A `.20` and Stage1022A Panel1 `.84` raw command envelopes. The parser verifies the host, LAP-120 board, kernel, boot UUID, interface, PHY mapping and expected local MAC; identical hostnames are not treated as identity proof.

| Saved target | Known before-state | Missing before-state | Full native admission |
|---|---|---|---|
| `.20` | BE1500/2500, notsent8192, AQM512/3145728/3028, four ACs, BC/MC50000, fq_codel | aql_threshold | BLOCKED |
| Panel1 `.84` | BE1500/3000, AQM512/3145728/3, four ACs, BC/MC50000, fq_codel | aql_threshold; notsent value/presence | BLOCKED |

The real baseline is never completed with guessed defaults. Panel1's observed quantum3 is preserved as saved evidence; this wave does not establish its cause or a performance regression. AQL is per AC, not per TID. Default qdisc policy does not prove the qdisc parameters of existing interfaces.

The plan uses numeric AQL commands `0..3 low high` and named AQM commands `fq_limit N`, `fq_memory_limit N`, `fq_quantum N`. Readback validation requires the complete typed configuration, identity/epoch equality and the exact BC/MC value. Missing, boolean, floating-point and malformed counter values fail closed. ABI-valid native zero values remain restorable.

The dictionary model covers normal apply/readback/restore, failures before and after each of ten write effects, a readback mismatch, and failure of each restoration field: 32 cases per target. Missing fields are completed only in explicitly synthetic fixtures, and the exact synthetic fields are listed in the receipt. A restore error remains a failure even if that field already equals baseline; later restore attempts continue in the model.

This model is stronger than the existing shell kit and is not proof that the kit implements it. The kit requests manual `--rollback` after apply failure and returns early on a rollback write error. Its BC/MC check tests presence; this verifier also checks the saved value. No independent background watchdog, SIGKILL recovery, hardware transaction or fault injection into the actual kit is proven.

Pure APIs: `build_plan`, `validate_readback`, `simulate_transaction`, `fault_matrix`, `build` and `replay_receipt`. Imports do not execute commands or write files.

```powershell
python tools/autoresearch/wa_v17_pareto_transaction_planner_and_verifier.py
```

The CLI exports the offline receipt. Local integrity can pass while both operational plans remain blocked. No new traffic, throughput, latency, promotion or production acceptance is asserted. External research, new benchmarks and durable-memory writes are not claimed.
