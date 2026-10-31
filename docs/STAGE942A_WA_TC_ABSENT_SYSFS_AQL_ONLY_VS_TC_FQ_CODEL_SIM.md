<!-- doc-head: Stage 942A SimPy model, tc-absent default fq_codel+AQL vs tuned tc fq_codel vs FIFO; SIMULATED_MODEL_ONLY, offline, no devices touched -->
# Stage 942A - WA without `tc`: sysfs/AQL-only vs tuned tc fq_codel (offline model)

Evidence class: `SIMULATED_MODEL_ONLY`. `live_devices_touched: false`. Nothing here was measured on a radio.

## Question
An 8MB-flash OpenWrt WA lacks `/usr/sbin/tc`. How much queueing quality is lost versus a box where
`tc qdisc replace ... fq_codel quantum 1514 target 5ms interval 100ms flows 1024 ecn` is available?

## Configs
| Config | Model |
| :--- | :--- |
| no_fq_codel_fifo | Single FIFO (1000 pkt), driver ring 16 pkts. Worst case. |
| A tc-ABSENT | `net.core.default_qdisc=fq_codel` + AQL + tcp_notsent_lowat. Kernel-default fq_codel (5ms/100ms), drop-only, driver ring 8 pkts. |
| B tc-PRESENT | Explicit tuned fq_codel, ECN marking, driver ring 4 pkts. |

## Model
- SimPy, serialized medium 50 Mbps with 0.9x-1.4x airtime jitter, 60 s, seed 20261027.
- Bulk flow: AIMD source (1500 B packets, 10 ms base RTT). Probe flow: 200 B every ~20 ms (VoIP/ICMP proxy).
- fq_codel: per-flow queues, DRR quantum 1514, new/sparse flow priority, CoDel per flow.
- Assumed differences A vs B (the only tunables): ECN on/off for the bulk flow and driver ring depth.
  These are modelling assumptions, not measured values.

## Results (probe one-way latency, ms)
| Config | p50 | p95 | p99 | Bulk goodput Mbps | Drops | ECN marks |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| no_fq_codel_fifo | 123.48 | 172.02 | 176.36 | 43.309 | 0 | 0 |
| A tc-ABSENT | 7.61 | 7.88 | 7.96 | 43.286 | 114 | 0 |
| B tc-PRESENT | 6.53 | 6.74 | 6.81 | 43.188 | 0 | 127 |

## Gap (honest reading)
- A cuts p99 by ~22x versus FIFO and removes ~99.3% of the p99 bufferbloat that B removes.
- The residual A-vs-B gap is about 1.15 ms at p95 and p99. It is real and nonzero: A is NOT equal to B.
- Bulk goodput differs by under 0.3% (B marginally lower here; within model noise, no claim of a goodput win).
- Reason A is close: flow isolation and CoDel live in the kernel qdisc selected by `default_qdisc`,
  and AQL bounds airtime queued in the driver. `tc` only adds fine-tuning.

## Conclusion
On a tc-less WA, set `net.core.default_qdisc=fq_codel` (and keep AQL + tcp_notsent_lowat); expect
most of the latency benefit. Do not expect parity with the tuned configuration. Field validation is
a separate, gated step; this stage proposes nothing to deploy.

## Files
- `tools/sim/run_stage942a_wa_tc_absent_sysfs_aql_only_vs_tc_fq_codel_sim.py`
- `artifacts/autoresearch/stage942a_wa_tc_absent_sysfs_aql_only_vs_tc_fq_codel_sim.json`
- `tests/test_stage942a.py`
