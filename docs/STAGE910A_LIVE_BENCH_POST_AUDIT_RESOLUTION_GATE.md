<!-- doc-head: Stage910A native replay of WA discovery, clean-control prerequisites, reversible AQL trials and passive telemetry -->
<!-- /doc-head -->

# Stage910A — Post-audit live bench resolution gate

This gate is local-only. Importing or executing it never opens SSH, generates traffic,
changes a profile or writes a radio. It writes a consolidated JSON receipt only.
Acquisition is performed by the explicitly invoked Stage905A..909A collectors.

## Evidence contract

| Stage | Recomputed evidence | Acceptance boundary |
| --- | --- | --- |
| 905A | Native station/neighbor and queue readbacks | ARP candidates do not authenticate a STA; default qdisc and mac80211 iTXQ differ |
| 906A | Six A/A pairs from raw receiver bytes and actual ping replies | Require twelve complete windows, 20/20 replies each and no positive A/A gate verdict |
| 907A | Six discovery and six disjoint holdout pairs; applied/restored configurations | Require real independent45s watchdog restoration proof and hash-bound replication review |
| 908A | Panel1 native passive snapshots and counter deltas | Passive observation; not a controlled A/A or application goodput result |
| 909A | LTU native passive snapshots and observable CPU1/IRQ63 deltas | Missing/reset counters stay UNKNOWN; no `/dev/ame*` access |

For controlled windows the verifier checks the native program/stdin SHA, exact target,
arm/block/dataset/session/times, frozen source revision, pre-window baseline, native
applied profile and separately restored post-window baseline. It regenerates normalized
receipt bytes and independently uses the hardened Flent ping parser and percentiles.
The real paired-block/Sidak gate evaluation must equal the saved JSON wire result.
Source drift, missing fields, hash mismatch, changed identity or restoration failure
prevents closure. No invalid or missing metric becomes a zero.

The independent watchdog probe kills its parent after native candidate readback and
before HTTP. Verification requires the autonomous target watchdog log, restored native
baseline, matching program/source hashes and successful private RAM cleanup.
Normal process-exit rollback alone does not establish this proof.

## Measurement limits

The frozen workload is one existing4MiB HTTP transfer followed by idle ICMP, with a
settling interval declared by the producer. Receiver bytes divided by the complete
window are delivery rate, not saturated TCP capacity. These data do not measure loaded
Triple-Play latency. Direct management addresses do not establish an exclusive RF path.

The existing gate requires chronological fixed A/B order. This protocol declares that
limitation rather than reordering measurements or claiming randomization/counterbalance.
Six complete pairs and a paired_blocks_count field alone do not prove that permutation
inference ran: an earlier safety/effect/CI rejection can leave default statistical fields.
The gate preserves the actual REJECT/KEEP result; positive treatment gain is not invented.

Passive labels A/A_REPEAT are bookkeeping. Both passive collectors observe normal
uncontrolled service and add their own SSH CPU/traffic. They cannot calibrate a global
false-positive rate; that value remains UNKNOWN and promotion remains disabled.

## Reproduction

```text
python tools/verify/verify_stage910a_live_bench_post_audit_resolution_gate.py --validation artifacts/verification/stage905a_to910a_validation.json
python -m pytest tests/test_stage905a_to_910a_suite.py
```

The gate exits0 only when all requested scoped acquisitions, hash/readback replay and
local test evidence pass. Otherwise it exits2 and retains explicit blockers.
`PASS_WITH_LIMITS` accepts the recorded scoped acquisition only; it authorizes no
deployment, RF-path acceptance, saturated-capacity claim or global zero-FP claim.

The final receipt is
`artifacts/autoresearch/stage910a_live_bench_post_audit_resolution_gate.json`.
Actual acquisition counts, gate verdicts, tests and outstanding criteria are read from
that receipt, not pre-filled in this document while physical collection is running.
