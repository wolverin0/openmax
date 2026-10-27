<!-- doc-head: 959A offline evidence and acceptance boundaries -->
<!-- /doc-head -->

# Unified raw physical-retest runner software contract

Source-bound Flent raw parsing and the real RegressionGatekeeper are connected in one runner.
freeze_plan binds controller role, configurations, station roster, family, gate contract and sources before A/A.
Inspection never invokes an acquirer. Execution requires execute=True; the CLI requires --execute.
A physical acquirer must match a frozen repository source file; the runner itself provides no SSH transport.
Every window supplies exact raw envelope bytes with iperf3 JSON and native ping text for every configured station.
Empty responses, iperf errors, absent receiver counts, missing peers/readbacks/sentinels and all capture/reset faults reject.
A/A and every enclosing sentinel require zero loss. Passing a generic gate control label alone is insufficient.
Discovery must pass before disjoint holdout. IDs, cookies, raw payloads, windows and sessions cannot be reused.
Physical callbacks must consume the measured duration and timestamps must fit observed acquisition boundaries.
Acquirers must enforce the supplied deadline and restore baseline on abort; synchronous callbacks cannot be forcibly cancelled here.
The runner owns acquisition validation, not a universal transport timeout or hardware rollback implementation.
Raw bytes, observed callback timing, normalized receipts, plan and phase results are saved with SHA256 hashes.
Existing campaign directories and files are never overwritten. Root paths, source/data drift and duplicate JSON keys reject.
Synthetic fixtures retain SYNTHETIC origin and can never become physical promotion evidence.
Hashes authenticate supplied bytes, not the honesty of an instrument. Physical acceptance remains UNKNOWN.
A statistical PROMOTE does not authorize deployment, flashing or radio mutation.
All task verification is local; no radio campaign, SSH or durable-memory ingestion is executed.
