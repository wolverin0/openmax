<!-- doc-head: Stage1116A saved LTU-Lite passive interval replay; insufficient samples for validated thresholds or false-positive claims -->
No SSH, active load, proprietary device-node access or external alert is performed.
<!-- /doc-head -->

# Stage1116A LTU-Lite passive observability evaluator

The evaluator reads the two hash-bound Stage1023A `.110` native snapshots. It checks LTU-Lite board0xae08, host, boot UUID, collector epoch, two CPU IRQ columns, IRQ owner, successful transport and ordered controller timestamps. CPU tick deltas, IRQ63 CPU1 and interface counters are reconstructed from the saved raw output, rather than inferred from a status label.

| Evidence | Result | Interpretation |
|---|---|---|
| Native snapshots | 2 | One adjacent passive interval |
| Target uptime interval | about3.59 seconds | Saved observation, no new collection |
| IRQ63 CPU1 delta | 0 | No increment in that interval, not absence of an LTU bug |
| CPU1 tick denominator | 356 | Native jiffies; idle plus iowait counted as idle |
| CPU1 busy fraction | about31.18% | Passive utilization, not workload capacity or RF QoE |
| Labelled alarm outcomes | 0 | False-positive and false-negative rates are UNKNOWN |

Missing, boolean, out-of-range or reset counters fail closed. A changed boot, collector, CPU set, IRQ owner, interface set, overlapping or reversed interval is rejected. Non-finite or malformed time and threshold inputs are rejected. No missing metric is silently converted to zero.

The calibrator records valid and invalid intervals and real denominators. It emits no production threshold or threshold candidate from a single passive interval. Optional caller-supplied CPU/IRQ policies are evaluated only as uncalibrated parameters; they do not become validated alert rules. An empty input remains insufficient, with zero observed duration and no invented samples.

Saved captures do not contain `gMaxBDEver`, `rx_target_pwr` or `sched_mcs`. These stay UNKNOWN. Deafness, QAM ceilings, application goodput, latency, causal RF diagnosis and bug absence are not established. Interface byte rates include management and unrelated traffic.

Pure APIs: `parse_snapshot`, `evaluate_pair`, `calibrate`, `build` and `replay_receipt`.

```powershell
python tools/autoresearch/ltu_lite_110_passive_observability_threshold_calibrator.py
```

The output separates local replay integrity from calibration and physical acceptance. No `/dev/ame*` path is opened, no radio configuration is changed and no alert is sent. Scholarship, new benchmarks, production acceptance and durable-memory ingestion are not claimed.
