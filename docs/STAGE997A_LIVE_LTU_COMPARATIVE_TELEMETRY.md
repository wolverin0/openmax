<!-- doc-head: Stage997A fresh LTU-Lite passive comparison; observed IRQ63 delta zero is not zero-FP or bug absence -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage997A — LTU-Lite comparative native telemetry

2026-10-27. Provenance **CONFIRMED_LIVE_HARDWARE**;2/2 fresh passive SSH reads
of198.18.0.63, usernameubnt through the documented credential accessor.
Native board identity is LTU-Lite/sysid0xae08 in both observations.
Attribution: external collector, Linux counters and proprietary LTU status getters.

## Actual interval

| Getter / derived observation | Native result | Limit |
| --- | --- | --- |
| Boot identity | Stable; matches latest956A/909A history | No reboot observed between these snapshots |
| Target uptime interval | 3.66s | Short passive interval, not a soak test |
| Aggregate CPU busy | 32.18% | First8 CPU tick fields; guest not double-counted |
| CPU0 / CPU1 busy | 38.40% / 26.17% | Native counter differences |
| IRQ63 CPU1 delta | 0, OBSERVED | Present CPU1 column and unchanged IRQ descriptor |
| RX/TX interface error increments | 0 on comparable interfaces | Not proof of RF or application health |

IRQ63 delta0 is an observed counter difference, not proof that LTU firmware bugs
are absent. Missing IRQ columns/rows would remain UNKNOWN. Interface br1/eth0 byte
activity includes these SSH reads and does not equal application receiver goodput.
No `/dev/ame*` access, ioctl, raw memory, ping, generated traffic, configuration,
power, service, RF, firmware or storage change was performed.

## Honest detector result

Telemetry-quality events:0 in this interval. Confirmed native interface-error events:0.
Local RF alerts emitted:0. The RF composite remains **NOT_EVALUABLE** without matched
RF failure/QoE ground truth. `zero_anomalies_verified=false` and
`zero_false_positives_verified=false`; `false_positive_rate=null`, not0.
No labelled negative-control experiment or full hardware-bug surveillance exists.
This passive comparison cannot authorize a champion or deployment.

## Evidence and reproduction

[Producer](../tools/autoresearch/run_stage997a_live_ltu_comparative_telemetry.py),
[receipt](../artifacts/autoresearch/stage997a_live_ltu_comparative_telemetry.json),
[execution](../artifacts/verification/stage997a/execution.json).
Source bindings identify historical956A/909A inputs separately from fresh capture
hashes. Local replay verifies native command, host, username, parsed counters and
the exact delta. Original analysis source and offline parser-failure evidence remain
archived; parser repairs did not repeat or replace the hardware observations.
CLI exit0 records completed collection, not universal zero-anomaly/zero-FP acceptance.
