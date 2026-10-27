<!-- doc-head: Public redacted derivative; original evidence and replay remain private -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

# Stage899A — PowerBeam measured baseline control and Rocket native identity

2026-10-27. Status **PARTIAL**, physical acceptance **NOT_ACCEPTED**.
Attribution: external controller HTTP/ICMP acquisition; Linux/native RF counters;
no ath10k, firmware, qdisc or RF configuration changes.

## Confirmed native bench

.241/.242 are PowerBeam5ACGen2 OpenWrt24.10.4/kernel6.6.110, root native access.
Association is VHT20 at5200MHz, not an assumed VHT40 treatment. .242 uses phy2-sta0.
The existing AP HTTP endpoint `198.18.0.8/bench4m.bin` serves4194304 bytes.
Pktlog reads0; native AQL/BQL/sysctl/boot/channel readbacks were stable before and
after every window. `tc` is unavailable: full qdisc identity is **UNKNOWN**.

.251 is independently observed Rocket2AC Prism/airOS2XC8.7.11 at2422MHz, board0xe2f2.
No assigned2.4GHz peer exists for a valid Rocket OTA A/A cohort. Rocket coverage is
read-only identity/status/qdisc/tool inspection, not a measured Rocket control.

## Actual acquisition

Eight baseline/baseline A/B-labelled pairs,16 windows, with one predeclared control
hypothesis, Sidak adjusted alpha0.05. Both labels have the same configuration hash.
The plan/code hashes were frozen before acquisition. Each window repeats the existing
4MiB HTTP object while20 ICMP requests run at integer1s intervals (max64 fetches).
Acquisition uses a private RAM FIFO/count/stderr directory, own-child PID checks,
40s deadline and cleanup. No global service/process termination or persistent write.

| Block | A Mbps | B Mbps | A replies/20 | B replies/20 |
| --- | ---: | ---: | ---: | ---: |
| 0 | 10.974 | 11.509 | 15 | 16 |
| 1 | 7.080 | 8.809 | 13 | 16 |
| 2 | 10.949 | 8.615 | 18 | 15 |
| 3 | 9.315 | 12.273 | 14 | 17 |
| 4 | 14.814 | 8.207 | 20 | 15 |
| 5 | 11.745 | 8.316 | 20 | 14 |
| 6 | 7.259 | 9.486 | 17 | 19 |
| 7 | 11.050 | 9.975 | 16 | 16 |

Total actual receiver bytes457179136;261/320 ping replies,18.4375% aggregate loss.
Mbps uses receiver bytes divided by the complete controller-observed window,
including collection overhead; it is not a pure TCP capacity or Triple-Play result.
Nearest-rank p95/p99 use actual reply arrays (13..20 samples/window); no missing
reply becomes zero RTT. Single-peer fairness does not establish sector fairness.

## Gate outcome and limits

Adapter status **EVALUATED**, control_result **PASS_NO_PROMOTION**.
The unmodified gate returns **REJECT: Excessive packet loss in candidate**.
It exits before paired inference: paired_blocks_count0. Gate p=1 and zero effect/CI
fields are early-rejection defaults, **not computed statistical estimates**.
This proves no promotion in this acquisition, not false-positive calibration success.

All native RF RX deltas cover receiver payload bytes, supporting RF byte activity;
exclusive OTA routing remains **UNKNOWN**. Interface-bound ping failed earlier;
normal bridged ping/HTTP worked. These outcomes are preserved independently.
Reset evidence is unchanged boot plus kernel-log restart delta0; silent resets cannot
be excluded. Capture-drop0 means complete bounded SSH/ping output, not pcap evidence.

The first A/A attempt failed because BusyBox rejected fractional ping interval0.2.
It yielded zero valid windows and is preserved, excluded from this new frozen dataset.
Final native readback equals initial configuration; no collector RAM directories or
owned workload processes remained.

[Producer](../tools/autoresearch/run_stage899a_live_powerbeam_rocket_readonly_aa.py),
[receipt](../artifacts/autoresearch/stage899a_live_powerbeam_rocket_readonly_aa.json),
[native evidence](../artifacts/verification/stage899a/).
Stage900A independently recomputes all windows and uses the hardened Flent ping
parser/percentiles; it does not claim Flent/iperf workload execution on these devices.
