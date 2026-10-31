<!-- doc-head: Stage956A fresh passive LTU-Lite board CPU IRQ and network audit with no device-node access -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage956A — LTU-Lite passive audit

2026-10-27. Authorized endpoint:198.18.0.63, read-only SSH.
Attribution: external controller, Linux counters and native LTU status output.

The producer reads board name/sysid, firmware version, boot/uptime, /proc/stat,
/proc/net/dev, /proc/interrupts and mca-status. It does not open proprietary device
nodes, invoke ioctls, read physical memory, change settings or generate test traffic.

Two native snapshots3s apart allow subtraction only if target boot, collector epoch,
target uptime, local monotonic timing and counter monotonicity agree. CPU uses the
first eight /proc/stat fields without double-counting guest time. IRQ63/CPU1 needs
the real CPU header and IRQ row; absence remains UNKNOWN, never assumed zero.
All counter/interface totals are passive traffic observations, not receiver goodput.

Values such as gMaxBDEver, rx_target_pwr and sched_mcs are reported only if the
ordinary native status output exposes them. Missing getters do not become values
inferred from old benchmark receipts. A zero IRQ delta cannot prove a bug absent.

[Producer](../tools/autoresearch/run_stage956a_live_ltu_lite_readonly_audit.py),
[receipt](../artifacts/autoresearch/stage956a_live_ltu_lite_readonly_audit.json),
[native captures](../artifacts/verification/stage956a/).

The receipt contains actual successful-read counts and per-field native availability.
There is no controlled A/A, injected UDP stream, RTT test or calibrated false-positive
rate. Physical workload acceptance is NOT_APPLICABLE_PASSIVE_ONLY; zero-FP is UNKNOWN.
The SSH collector contributes a small amount of CPU/network activity itself.

## Final native result

Two of two reads completed on LTU-Lite board0xae08. The3.61s passive interval
showed aggregate CPU busy31.93% and native IRQ63/CPU1 delta0. Radio ath0 counters
did not advance in this short interval. This is not absence-of-bug or RF-health proof.
No proprietary device-node access or active workload occurred. Collector completed;
all SSH handles closed before the operator replaced the queue with995A..1000A.
