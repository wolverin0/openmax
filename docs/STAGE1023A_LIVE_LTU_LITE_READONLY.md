<!-- doc-head: Stage1023A two native LTU passive snapshots; no proprietary device-node access or workload inference -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage1023A — LTU-Lite native passive counters

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE** for actual SSH observations.
Attribution: external controller, Linux proc/native LTU status getters.

Target198.18.0.63 answered both reads as **LTU-Lite**, board.sysid **0xae08**.
The two snapshots have the same boot and a comparable native interval of **3.59s**.

| Observation | Actual value |
| --- | ---: |
| completed native snapshots | 2/2 |
| aggregate CPU busy | 32.4438% |
| CPU0 / CPU1 busy | 33.8028% / 31.1798% |
| IRQ63 CPU1 delta | 0 |
| ath0 received/transmitted byte deltas | 0 / 0 |
| br1 received/transmitted byte deltas | 6566 / 10534 |
| observed interface error/dropped-packet increments | 0 in this short interval |

These are passive system/interface counters, not receiver application goodput or
an A/A benchmark. SSH acquisition contributes to management traffic and CPU.
An observed IRQ delta0 does not establish absence of any LTU firmware bug.
No actual RTT, jitter, capacity, zero-anomaly or false-positive calibration exists;
the corresponding measurement fields remain null/UNKNOWN.

Only authorized board/version, uptime/boot, proc/stat, proc/net/dev, interrupts and
native status getters were read. **No /dev/ame access, ioctl, memory operation,
configuration write, scan, load, service operation or protected-partition access.**
No other production endpoint was queried by this collector.

[Producer](../tools/autoresearch/run_stage1023a_live_ltu_lite_readonly.py),
[receipt](../artifacts/autoresearch/stage1023a_live_ltu_lite_readonly.json).
The receipt binds the exact native captures, source archive and clock/counter checks.
Local verification re-parses the saved outputs and does not contact hardware again.
See stage1023a/local_verification.json for replay checks.
