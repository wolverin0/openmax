<!-- doc-head: Stage933A guarded existing-baseline PowerBeam performance protocol; no firmware or profile activation -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage933A — Existing baseline performance after native preflight

2026-10-27. Workload execution requires the coordinator's exclusive PowerBeam lease.
This document records the frozen protocol before acquisition; actual results are
added after the authorized run. Stage932A observed API2; no API5 file was present.

## Scope and predeclared protocol

Three descriptive windows run from `.242` to the existing HTTP server on
`198.18.0.45`. Each repeats the existing4194304-byte object while20 ICMP requests
run at integer1s intervals, with at most64 HTTP requests per window. Actual body
bytes and native ping summaries/latencies determine metrics; no synthetic capacity
or zero-loss replacement is inserted.

The managed interface and PHY are resolved dynamically. Fresh native baseline
readbacks before and after every window must match: board/kernel/boot, interface,
PHY, channel, AQL, tcp_autocorking, BQL, pktlog, route and kernel default qdisc.
The source hashes and program SHA are frozen before the first measured window.

No firmware, AQL, sysctl, qdisc, channel, interface role or service setter exists in
the runner. No candidate firmware is uploaded, bound, loaded or claimed active.
The workload can encounter the previously observed simultaneous HTTP/ping loss;
every measured result is retained, and no automatic rerun exists.

## Deadline and recovery boundary

A target-side45s timer terminates only the controlling load shell after checking its
start ticks, allowing its trap to stop owned fetch/wc/ping/timer children and remove
only its private RAM FIFO/count/stderr files. The SSH collection deadline is58s.
This is a bounded workload guard, not proof of autonomous firmware rollback.
Forced-fault recovery is not physically exercised by these descriptive windows.

## Metric limits

Receiver Mbps uses actual HTTP body bytes divided by the complete controller
window, including collection overhead. p50/p95/p99 use nearest-rank actual ICMP
reply samples; packet loss uses actual transmitted/received counts. CPU load comes
from native /proc/stat deltas. Missing/invalid observations fail closed.

The management route is br-lan; RF RX/TX counter deltas are captured as activity
witnesses. They do not prove exclusive RF routing or identify every payload frame.
The results are neither iperf nor Triple-Play capacity, an A/B treatment comparison,
a clean A/A calibration or a new firmware performance promotion.

[Runner](../tools/autoresearch/run_stage933a_live_powerbeam_preflight_performance.py),
[native program](../artifacts/verification/stage933a/program.sh),
[receipt after execution](../artifacts/autoresearch/stage933a_live_powerbeam_preflight_performance.json).
