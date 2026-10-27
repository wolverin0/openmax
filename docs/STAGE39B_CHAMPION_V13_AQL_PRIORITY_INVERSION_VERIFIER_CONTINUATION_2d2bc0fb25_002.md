<!-- doc-head: STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER.md continuation 2 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER.md) | Part 2/2
<a id="stage39b-champion-v13-aql-quantum-and-airtime-verifier"></a> [Stage39B: Champion v13 AQL, quantum and airtime verifier](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER_CONTINUATION_2d2bc0fb25_001.md#stage39b-champion-v13-aql-quantum-and-airtime-verifier) | <a id="historical-evidence-and-interpretation"></a> [Historical evidence and interpretation](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER_CONTINUATION_2d2bc0fb25_001.md#historical-evidence-and-interpretation) | <a id="exact-accepted-linux-vector"></a> [Exact accepted Linux vector](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER_CONTINUATION_2d2bc0fb25_001.md#exact-accepted-linux-vector) | <a id="api-and-acquisition-contract"></a> [API and acquisition contract](STAGE39B_CHAMPION_V13_AQL_PRIORITY_INVERSION_VERIFIER_CONTINUATION_2d2bc0fb25_001.md#api-and-acquisition-contract)

<!-- stage822a-payload-begin -->
- `dual_netdev_readbacks`: station_mac, netdev, ifindex, station_epoch,
  airtime_weight, return_code0, evidence_sha256 and sequence/time;
  source `qualified_nl80211_station_get`, with
  `dual_netdev_inventory_complete=True`.

The five required views are three parent-MAC pairs plus the two applicable
child-MAC pairs. Unrelated Cartesian MAC/VLAN pairs are rejected. A failed or
missing child view is UNKNOWN and blocks acceptance; the verifier has no
parent-value fallback. The native station lookup must actually resolve that
station in the requested interface context; see the primary
[mac80211 station lookup](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/cfg.c).
Collector qualification and interface-readback support are external
prerequisites, not proven by a caller supplying a source label or a hash.

## Bounded window and receiver delivery

`verify_canary(before_raw, after_raw, plan, flow_trace=..., receiver_reports=...,
now=...)` verifies two already acquired post-apply snapshots. It does not apply
the profile or run traffic. Before may be at most60s old; after at most10s.
Each device needs an increasing capture sequence and5..55s UTC and monotonic
elapsed time. Boot/netns/wiphy/module/station identities, AQM inodes,
parameters and AP_VLAN inventory/epochs must remain stable. Counter reset,
wrap/replay and airtime RX/TX reset fail. Deficits may move in either direction.

All captured TXQ drop/overlimit counters must be zero at both endpoints;
TID7 packets and bytes must have zero delta on every AP/CPE peer. Qualified,
complete `qualified_txq_flow_trace` evidence must bind the exact plan, AP,
window, sequences, station path/epoch and flow IDs. Observed classes are
IPTV TID4/AC1 UDP, VoIP TID6/AC0 UDP, and bulk TID0/AC2 TCP. Each planned flow
needs positive packet/byte counts, its minimum exposure, distinct evidence
within its station/class and aggregate counts no greater than TXQ dequeue
deltas. DSCP intent alone does not prove actual classification.

The wrapper for traces and receiver reports has `complete=True`, `source`,
`run_id`, `plan_sha256`, AP `device_id`, `before_seq`, `after_seq`, exact
`window_start`/`window_end` and `evidence_sha256`. Wrapper timestamps must use
the normalized ISO spelling returned by snapshots (`+00:00`); an equivalent
`Z` spelling is not interchangeable in the reused strict trace binder.

`qualified_udp_receiver_reports` must contain exactly one report for each
planned UDP flow. Each report includes flow_id, service, station_mac,
receiver_device_id, receiver_boot_id, receiver_netns_inode, window_start/end,
total_datagrams, lost_datagrams, received_datagrams, jitter_ms and
evidence_sha256. It binds the Loco epoch and a minimum5s interval inside the
common AP/CPE window. Total must meet the planned exposure; lost must be0 and
received must equal total. Jitter must be finite and nonnegative. Zero TXQ
drops alone never substitute for these receiver reports. The verifier does
not impose an unrequested jitter-improvement threshold.

Successful results explicitly retain `physical_acceptance=False` and
`wireless_gain_claimed=False`. Supplied qualified receiver evidence can be
internally consistent without proving its authentic native acquisition.
This stage does not verify the complete Rocket/UPH/IGMP runtime and does not
make those independent acquisition tasks a prerequisite for these Linux
parameter checks.

## Validation and stop condition

Fresh, direct disposable-fixture command:

```text
python -m pytest tests/test_stage39b_champion_v13_verifier.py -q
```

Initial result: **53PASS,0FAIL,0ERROR,0SKIP,exit0 in0.65s** (console `f547c9`).
Coverage includes accepted R2 despite VI<BE, rejected R1/R3/R4 diagnostics,
complete parent/applicable-child inventories, wrong/rekeyed weights, TCP
namespace and parser errors, signed deficits, reset/epoch/TID7/drop guards,
all three bulk peers, and lossy/underexposed/missing/nonfinite UDP evidence.
The existing pytest_asyncio fixture-loop deprecation warning is retained.

Source/test pins, execution history and independent-review status live in
[stage39b_champion_v13_validation_20261025.json](../artifacts/autoresearch/stage39b_champion_v13_validation_20261025.json).
Stop after the requested module, tests, documentation and independent review.
No radio/SSH/WSL/NMS/service, native collector installation, flash action or
new physical experiment was executed. Native acquisition and physical
acceptance remain UNKNOWN; E2 remains NOT_ACCEPTED. No background runner or
next-stage execution is claimed.
<!-- stage822a-payload-end -->
