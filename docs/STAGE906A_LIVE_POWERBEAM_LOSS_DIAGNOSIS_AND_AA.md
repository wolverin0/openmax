<!-- doc-head: Stage906A PowerBeam idle versus saturated route diagnosis and separately frozen direct AA -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage906A — PowerBeam loss diagnosis and direct A/A

2026-10-27. Native acquisition **CONFIRMED_LIVE_HARDWARE**.
Attribution: external controller workload, Linux route/CPU counters, native RF counters.

## Diagnostic observations, excluded from the A/A campaign

Both PowerBeam5ACGen2 units are OpenWrt at5200MHz/VHT20. `.242` dynamically resolves
to `phy2-sta0`; `.241` has AP/WDS interfaces on phy2. No RF settings were changed.

| Diagnostic | Actual replies | CPU busy |
| --- | --- | --- |
| .241→.242 management, idle | 10/10 | 3.85% across both idle targets |
| .241→198.18.0.74, idle | 10/10 | Same interval |
| .242→.241 management, idle | 10/10 | 2.38% across both idle targets |
| .242→198.18.0.8, idle | 10/10 | Same interval |
| Continuous HTTP + ping→198.18.0.8 | 19/20 | 79.26% on .242 |
| Continuous HTTP + ping→198.18.0.45 | 16/20 | 61.96% on .242 |

CPU uses first8 /proc/stat fields; guest time is not double-counted.
Both routes use br-lan. On .242 the radio-alias route selects source198.18.0.46.
Changing the destination IP did not eliminate loss under simultaneous bulk.
Load/CPU/queue contention is **INFERRED**; exclusive RF loss, driver failure and a
specific causal bottleneck are **UNKNOWN**. These short observations do not prove
that CPU saturation alone caused the prior18.44% loss.

The HTTP Range feasibility request returned the full4194304-byte object; no rate cap
was assumed. nohup was absent. These failed feasibility assumptions are preserved.

## Frozen clean-control protocol

Six fixed A→B paired blocks with identical baseline settings, one Sidak hypothesis,
max_loss_pct0. Each window downloads one existing4MiB object, waits2s, then sends
20 integer-interval idle pings directly from.242 to198.18.0.45.
The before-plan diagnostic loss is not relabelled or retried as passing A/A data.
All measured windows remain in the frozen dataset, including any nonzero loss.

This measures receiver delivery bytes per complete HTTP+idle-ping window and idle
RTT, not saturated TCP capacity, loaded latency, Triple-Play or exclusive OTA routing.
Fixed AB order is required by the current gate and is not randomized/order-balanced.
Six temporal pairs on one physical link are not six independent hardware replicates.
Actual baseline: BE1500/2000, tcp_autocorking1. A/A performs no setters.

Result and exact per-window counts are in the [receipt](../artifacts/autoresearch/stage906a_live_powerbeam_loss_diagnosis_and_aa.json).
Acquisition was running when this protocol was written; the final result is added
after completion without changing the frozen sources or allocation.

[Script](../tools/autoresearch/run_stage906a_live_powerbeam_loss_diagnosis_and_aa.py),
[campaign engine](../tools/autoresearch/stage906_907_campaign.py).
The gate result is preserved verbatim; no promotion differs from full statistical
false-positive calibration. A paired-block count alone does not prove permutation
inference was reached. Post-window native baseline readback and RAM cleanup are required.
