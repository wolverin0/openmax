<!-- doc-head: STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->
PUBLIC_REDACTED_DERIVATIVE; inherited historical claims are not acceptance of this derivative.

[Document router](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER.md) | Part 1/2
<a id="bounded-window-and-receiver-delivery"></a> [Bounded window and receiver delivery](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER_CONTINUATION_2d2bc0fb25_002.md#bounded-window-and-receiver-delivery) | <a id="validation-and-stop-condition"></a> [Validation and stop condition](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER_CONTINUATION_2d2bc0fb25_002.md#validation-and-stop-condition)

<!-- stage822a-payload-begin -->

Pins four Stage41A rounds and their16 windows; R2 is the accepted historical vector.
Rejects observed R1/R3/R4 vectors without asserting a universal VI<BE scheduling law.
Requires fresh AP/CPE readbacks, parent/applicable-child weights and explicit UDP delivery.
Focused disposable fixtures:53PASS, exit0; independent review recorded in validation receipt.
Offline software acceptance only; no new physical result, device action or E2 acceptance.


# Stage39B: Champion v13 AQL, quantum and airtime verifier

Task: `T-S39B-CODEX-CHAMPION-V13-AQL-PRIORITY-INVERSION-AND-AQM-QUANTUM-VERIFIER`.
Parent: the original forward-plan external-controller telemetry/control-authority
and reproducible-experiment deliverables, under the fixed contract in
[BENCH_PLAN.md](BENCH_PLAN.md). The question is whether offline verification can
accept the exact Stage41A-R2 Linux vector while rejecting known bad profiles,
missing child-interface evidence and zero-loss claims unsupported by receivers.

Implementation: [stage41a_champion_v13_aql_inversion_verifier.py](../controller/stage41a_champion_v13_aql_inversion_verifier.py).
Fixtures: [test_stage39b_champion_v13_verifier.py](../tests/test_stage39b_champion_v13_verifier.py).
These are pure functions over supplied captures. No setter, device connection,
canary launcher, restoration script or new acquisition platform is included.

## Historical evidence and interpretation

The supplied [Stage41A JSON](../artifacts/autoresearch/stage41a_m22_m23_fq_quantum_and_voip_guard_bench_20261025.json)
and [benchmark report](STAGE41A_M22_M23_DYNAMIC_FQ_QUANTUM_AND_VOIP_GUARD_BENCHMARK.md)
contain four rounds, each with A1/B1/A2/B2. All four canonical round hashes are
pinned by `source_contract()`. Appending unrelated rounds does not replace this
evidence; changing a pinned round fails verification. The following are saved
hardware observations, not measurements repeated by Stage39B.

| Round | Treatment observation | Stored decision | Interpretation |
| --- | --- | --- | --- |
| R1 | AP quantum6056, BE1400/2800, threshold4000; goodput -1.029%; target BE drops2/0 | REFUTED; retain champion | Reject this compound quantum/budget vector. Mid-quantum blocking is an inferred explanation. |
| R2 | Exact v13 vector; goodput49.585 to50.310Mbps (+1.462%); IPTV0/5672, voice0/1202; target BE drops0/0 | CONFIRMED; promote champion | Preserve the local observed result and exact getter vector. |
| R3 | VI1000/2000 with BE1500/3000; mean IPTV loss4.728%; goodput -3.303%; target BE drops2/2 | REFUTED; retain champion | Reject the observed video-budget vector; the cause was not isolated. |
| R4 | VI restored1200/2400, VO250/500 and changed TCP controls; IPTV0/5681; goodput+0.828%, p95+3.321% | REFUTED; retain champion | Zero observed IPTV loss does not make this the accepted v13 profile. |

**There is no verified universal VI<BE inversion law.** Accepted R2 itself uses
VI1200/2400 below BE1500/3000. R3/R4 also change VO/TCP controls, so their contrast
does not isolate VI as the cause. In upstream Linux6.6.110,
`ieee80211_txq_may_transmit()` checks pending airtime and deficits for the
selected AC; it does not directly compare VI_low with BE_low. This supports
per-AC gating, not the proposed universal cross-AC inequality.
See the primary [mac80211 TX implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/tx.c).
Quantum is measured in bytes and AQL in estimated microseconds; a universal
conversion requires additional rate/aggregation evidence.

R2 does not show a latency or jitter improvement: saved p95 is118.851 to119.538ms
(+0.578%), p50 is46.129 to46.981ms (+1.847%), IPTV jitter0.810 to1.669ms
(+106.049%), and voice jitter0.851 to1.296ms (+52.291%). No confidence interval,
new RF gain or sum of historical champion gains is manufactured here. R3's
4.728% is the saved mean of phase percentages;268/5667 is its aggregate loss
count and is a different statistic.

The original report remains unchanged. Its R3 p50 row47.530 to47.419ms conflicts
with JSON45.394 to46.743ms, and R4's47.375 to48.368ms conflicts with JSON46.493
to42.596ms. Its R3 zero-BE-drop description conflicts with JSON B1/B2=2/2
(control A2=5). R4 control A2 has one BE drop; target B1/B2 have zero. These
discrepancies stay explicit; normalized verification pins the JSON rounds.

## Exact accepted Linux vector

| Control | AP | Loco CPE |
| --- | --- | --- |
| fq_quantum, bytes | 4542 | 1514 |
| fq_memory_limit, bytes | 4194304 | 4194304 |
| fq_limit, packets | 2048 | 1024 |
| fq_flows_cnt | 4096 | 4096 |
| AQL VO, low/high microseconds | 300/600 | 300/600 |
| AQL VI | 1200/2400 | 1200/2400 |
| AQL BE | 1500/3000 | 900/1500 |
| AQL BK | 500/1000 | 500/1000 |
| aql_threshold | 5000 | 4000 |
| tcp_notsent_lowat | 8192 | 8192 |
| tcp_limit_output_bytes | 98304 | 98304 |
| tcp_pacing_ca_ratio / tcp_pacing_ss_ratio | 105/140 | 105/140 |

The AP maps explicit Loco/Rocket/LiteBeam MAC identities to airtime weights
768/512/128. The historical MACs are `PUBLIC_DEVICE_0036`, `PUBLIC_DEVICE_0048`
and `PUBLIC_DEVICE_0066`, respectively; new captures require their own explicit
plan. Loco and Rocket each bind to a discovered, distinct `phy0-ap0.staN`
AP_VLAN, while LiteBeam binds to `phy0-ap0`. Child suffixes are not fixed.

`tcp_notsent_lowat` is a default for sockets without their own
TCP_NOTSENT_LOWAT setting; `tcp_limit_output_bytes` limits queued TCP bytes
per socket, and the pacing values are ratios, not fixed link-rate caps.
Readbacks prove the sysctl values, not every socket's effective policy.
See the primary [Linux6.6.110 TCP sysctl documentation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/Documentation/networking/ip-sysctl.rst).

Historical getters save canonical parent debugfs airtime values. They do not
save successful child readbacks or prove that dual writes prevent a later
rekey reset. The runner's literal candidate-command description also contains
two MACs inconsistent with its actual apply function and saved getters; it
must not be copied into a new plan. The source contract reports
`dual_child_readbacks_saved=False`. Future dual-view verification therefore
requires additional explicit evidence rather than silently treating the
historical parent getter as a child getter.

These controls belong to Linux TCP and mac80211/AQL, observed by an external
verifier. They do not establish QCA firmware queue ownership, proprietary
airMAX behavior or new silicon capability.

## API and acquisition contract

`build_plan(run_id=..., device_ids={"ap": UUID, "cpe": UUID},
cpe_peer_mac=..., stations=[...], flows=[...])` seals the source pins and
explicit inventory. Each station is exactly `{role, mac, netdev}`; each flow
is exactly `{flow_id, service, station_mac, min_packets}`. Services are `iptv`,
`voip` and `bulk`. UDP receivers bind to the planned Loco; TCP bulk must cover
all three AP peers. At least five flow specifications are required, and each
minimum exposure must be a positive, predeclared integer. A plan may identify
both IPTV streams separately. A single aggregate IPTV specification does not
independently establish the historical two-stream/5Mbps workload, fairness,
offered-load equivalence or benchmark acceptance. Fixture exposure20 is a test
value, not a hardware sampling recommendation.

`parse_tcp_sysctls()` accepts complete newline-terminated text containing
exactly the four fully qualified `net.ipv4.tcp_* = integer` rows above. Missing,
duplicate, unexpected, negative, boolean-like and out-of-range values fail.
`parse_station_airtime()` accepts the exact four-line debugfs ABI:

```text
RX: 1000 us
TX: 2000 us
Weight: 768
Deficit: VO: -100 us VI: 200 us BE: -300 us BK: 0 us
```

RX/TX are unsigned64 counters, weight is1..65535, and deficits are signed32
gauges. Negative deficits are valid scheduler state, not loss or inversion
proof. The parser follows the primary
[mac80211 station debugfs format](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/debugfs_sta.c).

`verify_readbacks(raw, plan, now=UTC_datetime)` requires a complete, read-only,
post-apply capture with `source="qualified_v13_readback_collector"` and both
devices. Device TXQ/AQM inputs reuse the existing Stage37B strict raw formats,
identity, freshness, kernel/driver and complete station-inventory checks.
Every captured peer must expose the same effective AQL vector as its role.
AP/CPE timestamps must differ by at most1s; a single snapshot must be at most
10s old. All four TCP fields must match in each device's network namespace.

New per-device `tcp_sysctls` components contain `source`, `capture_seq`,
`observed_at`, `netns_inode` and `raw`. Their sequence/time must match the TXQ
capture. The source is `qualified_procfs_tcp_collector`.

The AP additionally requires these complete lists:

- `netdevs`: `{name, ifindex, epoch, up, kind, parent_ifindex}` for the parent
  and two planned AP_VLANs, with unique current indices, SHA256 epochs and
  correct parent binding; `netdev_inventory_complete=True`.
- `station_airtime`: canonical parent path, inode, ifindex, station_epoch,
  associated_netdev, station_mac, raw four-line text and sequence/time fields;
  source `qualified_debugfs_airtime_collector`. All three effective weights
  must match. The airtime inode/epoch binds to the corresponding AQM station.
<!-- stage822a-payload-end -->
