<!-- doc-head: STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER.md) | Part 1/2
<a id="validation-and-remaining-acceptance"></a> [Validation and remaining acceptance](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER_CONTINUATION_680eee28ad_002.md#validation-and-remaining-acceptance)

<!-- stage822a-payload-begin -->

Direct focused pytest:86PASS,0FAIL,0ERROR,exit0; disposable clocks and state only.
Require post-apply IPTV TID4/AC1, VoIP TID6/AC0 and TCP bulk TID0/AC2 flow evidence.
Reject nonzero drop/overlimit totals, missing rows, replay, reset and counter-epoch changes.
Snapshot and restore exactly three global RW parameters under an independent60s guard.
Software verification only; device-adapter and physical acceptance remain UNKNOWN.


# Stage37B mac80211 AQM per-TID canary verifier

Task: `T-S37B-CODEX-CHAMPION-V10-MAC80211-AQM-AND-TRIPLE-PLAY-CANARY-VERIFIER`.
Implementation: [mac80211_aqm_per_tid_canary_verifier.py](../controller/mac80211_aqm_per_tid_canary_verifier.py).
Tests: [test_stage37b_mac80211_aqm_canary.py](../tests/test_stage37b_mac80211_aqm_canary.py).
Parent: external-controller, telemetry/control-authority and reversible experiment
deliverables in the [original forward plan](../artifacts/2026-09-20-forward-plan.html),
with acceptance fixed in the Stage37B section of [BENCH_PLAN](BENCH_PLAN.md).

Question: can effective mac80211 internal FQ readbacks and complete, bound TXQ
statistics verify the v10 triple-play contract and fail closed on a drop or a
readback mismatch? This is external-controller software describing Linux/mac80211
controls used with ath10k. It does not implement a QCA firmware or PHY change.

## Evidence inspected and limits

The requested [Stage36A JSON](../artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json),
[Stage36A report](STAGE36A_LIVE_IPTV_AC_VI_AND_DMS_PTMP_BENCHMARK.md) and
[Stage36B gate](../controller/iptv_dms_ac_vi_canary_gate.py) were inspected.
The plan binds the complete canonical `S36A-R2` round to SHA256
`b51d0e5e932bc403250e4e3c066451e0b717c04c4fadeadea22a8869d94c1310`.
Appending a later round does not change this binding; changing R2 fails closed.

R2 B1/B2 save AP/CPE global AQM getters and AP AQL. They report `tid4_ac1`
activity with zero drops/marks/overlimits. The saved delta subset contains
TIDs0,4,7, with **no TID6 or identified VoIP flow**. TID7 activity cannot prove
the requested voice classification. The JSON also lacks a CPE AQL getter;
the CPE profile below follows the report's explicit section3.2 declaration and
must be confirmed by a fresh exact readback before a canary.

The source reports promotion to v10, goodput55.352 to56.743Mbps (+2.513%) and
IPTV jitter1.425 to2.050ms (+43.86%). These historical source facts are retained
together; this task makes no new performance or jitter-reduction claim.
The older Stage36B BE1000/2000 target is not the v10 AP profile.

## Effective readback contract

| Field | AP | CPE | Access |
| --- | --- | --- | --- |
| `fq_quantum` | 3028 bytes | 1514 bytes | RW |
| `fq_memory_limit` | 4194304 bytes | 4194304 bytes | RW |
| `fq_limit` | 8192 packets | 8192 packets | RW |
| `fq_flows_cnt` | 4096 allocated flows | 4096 allocated flows | R |
| AQL VO / VI | 600/1200 / 1200/2400us | same | Readback only here |
| AQL BE / BK | 1500/3000 / 500/1000us | 900/1500 / 500/1000us | Readback only here |
| `aql_threshold` | 5000us | 4000us | Readback only here |

`parse_global_aqm` consumes the single file
`/sys/kernel/debug/ieee80211/phy0/aqm`, with its exact access/name/value header,
six R rows and three RW rows. All nine names must appear once, with correct
access and unsigned32 values. It preserves backlog, memory usage, collisions
and both event counters rather than treating them as controls. Unknown, missing,
duplicate, malformed or unterminated input fails. A directory-shaped path is
never a setter target. The ABI and three setters follow the
[exact Linux6.6.110 source](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/debugfs.c).

That source swaps the backing arguments of the displayed `fq_overlimit` and
`fq_overmemory` labels. The parser preserves the labels and emits an explicit
semantics warning; both must be zero, so the acceptance decision does not depend
on guessing which event occurred. Qualification still needs the installed
build's source/module identity. Historical JSON getters were stripped; only
the explicit saved-capture reader normalizes their terminating newline.
Live snapshots require the newline to reject partial reads that end in a digit.

`parse_station_aqm` reads each literal
`/sys/kernel/debug/ieee80211/phy0/netdev:<interface>/stations/<MAC>/aqm` file.
It requires the CoDel preamble, exact twelve-column header and every TID0..7.
It retains AC, backlog bytes/packets, new-flows, drops, marks, overlimit,
collisions, TX bytes/packets and the complete flags suffix, including spaces.
This bounded profile permits optional management TID16/AC0 and rejects other
TIDs. Missing TXQs are unavailable evidence, never fabricated zero rows.
These station files expose read-only statistics in the
[exact station implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/debugfs_sta.c).

Backlog is a gauge. Cumulative counter decreases are rejected as reset/wrap,
without clamping or rebasing. TX counters describe dequeue from FQ; collisions
describe FQ hashing rather than RF collisions. They are not ACK/receiver delivery
counts. See the [FQ implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/include/net/fq_impl.h).
Marks and collisions remain visible but are not relabelled as drops.

## Snapshot and flow evidence

`build_canary_plan` requires device UUID, run ID, explicit `ap`/`cpe` role,
an exact station-MAC inventory and named flow specifications covering IPTV,
VoIP and bulk. `validate_plan` rebuilds the canonical plan and checks its
complete content and digest. No target, flow or evidence policy can be changed
without changing the plan.

`normalize_snapshot` requires these collector fields:

| Evidence group | Required fields |
| --- | --- |
| Plan/build | device_id, run_id, role, OpenWrt24.10.4, Linux6.6.110, phy0, ath10k/ath10k_pci |
| Global identity | boot_id, netns_inode, wiphy_epoch, aqm_inode, module_sha256 |
| Collector provenance | source=`qualified_debugfs_txq_collector`, exact global path and file assertion |
| Values/time | global_aqm, aql_txq_limit, aql_threshold, capture_seq, monotonic_ns, observed_at |
| Complete stations | station_inventory_complete=true and exactly the planned MACs |
| Each station | literal path, aqm_is_file=true, associated/authorized=true, ifindex, aqm_inode, station_epoch, raw aqm |

The qualified collector must enumerate the whole affected wiphy, detect
same-MAC reassociation/TXQ recreation and bind station generation and file
identity. Merely hashing a MAC is not an epoch implementation. Missing, extra,
rebound or unhealthy peers fail. Boot/netns/wiphy/module/file and per-station
interface/MAC/generation must remain identical. Sequence, radio UTC and
monotonic time must advance; the initial snapshot is fresh within10s.

The measured window starts from the verified **post-apply** snapshot, after
the last setter. It spans at least5s and at most55s on monotonic time; its final
snapshot is fresh within10s. The plan requires explicit same-window qualified
flow witnesses, bound to device/run/plan, before/after sequence, station path
and epoch, and an evidence digest:

| Service | Transport | Required TID | Required AC |
| --- | --- | --- | --- |
| IPTV | UDP | 4 | 1 / AC_VI |
| VoIP | UDP | 6 | 0 / AC_VO |
| Bulk | TCP | 0 | 2 / AC_BE |

Every witness includes its named flow, positive matched packet/byte counts,
observed TID/AC and start/end UTC fully within that post-apply window. Each
corresponding TXQ must also have positive TX packet/byte deltas. A QoS rule,
counter increase or service label alone cannot identify a flow. A native
qualified flow tracer is an adapter prerequisite; this module does not pretend
to implement or physically qualify one.

Qualified traces count disjoint flow packets at the same FQ dequeue boundary.
Aggregated flow packet/byte counts per station/TID cannot exceed that TXQ's
measured deltas; a reused evidence digest within one station/TID also fails.
Both snapshots must already match v10. Pre-apply traffic and cached earlier
windows cannot satisfy the treatment window.

Both endpoints and every runtime readback must show zero global event totals
and zero drops/overlimits on **all observed TIDs**, including unrelated data
queues and optional management TXQ. Historical nonzero totals block too.
This is deliberately stricter than checking only newly added drops. Counters
are never reset to obtain a pass. Failure and restoration cannot undo loss.
Receiver delivery, jitter and player QoE require separate receiver evidence.

## Canary and exact restoration

`execute_aqm_canary` defaults to `fixture_only=True`. It accepts a disposable
runtime implementing `AQMRuntime`; there is no default SSH, device CLI,
service installer, NMS call or traffic generator. A real adapter requires
explicit opt-in, an independently approved qualification digest and preflight
proof of exact-build parsing, counter epochs, flow tracing, independent guard,
exact restoration and atomic setter fencing. A supplied digest is not itself
physical qualification or operator authorization.
<!-- stage822a-payload-end -->
