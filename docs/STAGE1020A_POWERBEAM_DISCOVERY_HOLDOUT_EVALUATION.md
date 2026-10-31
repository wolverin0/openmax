<!-- doc-head: Stage1020A separate native capability completion and honest no-cohort evaluation -->
<!-- /doc-head -->

# Stage1020A — Discovery/holdout eligibility

2026-10-27. Workload acceptance **NOT_ACCEPTED**; discovery and holdout are
**NOT_EXECUTED**. This stage must not turn an idle ping test or adapter self-test
into measured TCP/UDP evidence.

Stage1019A measured199 replies to200 idle requests. The zero-loss admission
criterion was not met. Its initial nc usage also lacks the listener/UDP/exec flags
required by Stage1013A's radio reflector plan. The fallback requires two actual
general-purpose hosts separated by the radio bridge; those endpoints have not been
provided or physically qualified. No host loopback is accepted as radio traffic.

## Capability completion lineage

The original BusyBox multi-argument tool lookup returned only the first command.
A separate native probe queries every tool individually, then captures unchanged
nc usage. It does not repeat the100-ping baseline, start a listener or modify
configuration. The raw initial output, original protocol and old adapter bytes are
retained. Corrected capabilities are a new observation, not a silent replacement.
The final receipt records the executed probe program, original/archived source
bindings and the adapter version used to interpret the complementary output.

The completion ran once on each radio: both native SSH captures completed and the
actual Python CLI returned2 for blocked admission. Individual lookups confirmed
nc, dd, awk, wget, uhttpd and cat on both radios. nc still exposes none of
`-l/-p/-u/-e`: radio TCP sink and UDP reflector remain **UNAVAILABLE**.
TCP source and HTTP-client command plans are conditionally runnable, but were not
executed. A generated bridge-host command marked RUNNABLE is a software template,
not proof that a far-end host exists or that traffic crosses the RF link.

The original adapter c5cb616a… was archived before the explicit capability-probe
fix; the completion uses the fixed96fa2ae3… revision. Neither the original raw
capture nor its protocol was rewritten. The coordinator reported possible external
PowerBeam inspection; these two reads do not claim an exclusive benchmark window.

The explicit CLI for that read-only completion is:

```text
python tools/autoresearch/run_stage1020a_powerbeam_discovery_holdout_evaluation.py --complete-capabilities
```

## Statistical boundary

Requested prospective contract: six paired A/A blocks, six discovery blocks and
six independent holdout blocks; objective LATENCY_WITH_CAPACITY_NONINFERIORITY,
one predeclared hypothesis and zero tolerated control loss. The real gate contract
is recorded, but no empty-data gate call is presented as a measured evaluation.

Every cohort has zero acquired pairs and an empty row list. Raw gate and replication
receipt remain null; goodput, loaded p95/p99 and media jitter remain unknown.
The old failed45s autonomous rollback is not a working recovery mechanism.
No TCP sender dd count is reclassified as application receiver goodput; UDP jitter
and percentiles are not fabricated from a TCP transfer or RTT mean/maximum.

Latest explicit user objective/pair count takes precedence over the older1015A
specification. Full acquisition must freeze actual host endpoints, native profile
contrast, source hashes, allocation and independent holdout evidence before load.
The source records source-revision lineage rather than editing past measurements.

[Receipt](../artifacts/autoresearch/stage1020a_powerbeam_discovery_holdout_evaluation.json),
[evaluator](../tools/autoresearch/run_stage1020a_powerbeam_discovery_holdout_evaluation.py).
