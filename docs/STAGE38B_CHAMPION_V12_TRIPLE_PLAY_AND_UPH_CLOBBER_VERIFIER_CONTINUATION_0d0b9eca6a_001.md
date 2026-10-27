<!-- doc-head: STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER.md) | Part 1/2
<a id="exact-captured-parameter-restoration-scripts"></a> [Exact captured-parameter restoration scripts](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER_CONTINUATION_0d0b9eca6a_002.md#exact-captured-parameter-restoration-scripts) | <a id="validation-and-completion-boundary"></a> [Validation and completion boundary](STAGE38B_CHAMPION_V12_TRIPLE_PLAY_AND_UPH_CLOBBER_VERIFIER_CONTINUATION_0d0b9eca6a_002.md#validation-and-completion-boundary)

<!-- stage822a-payload-begin -->

Direct focused pytest:52PASS,0FAIL,0ERROR,exit0; disposable three-device fixtures only.
Verify v11 AQM/AQL and v12 single-querier IGMPv2, WDS fast-leave/DMS and final UPH5.
Reject TID7 activity, IGMPv3/CS6 query traces, incomplete write journals and UPH alias/vector drift.
Generate captured-parameter restoration recipes with one full UPH vector last, requiring a qualified native guard.
No device or script execution; native guard/collector qualification and physical acceptance remain UNKNOWN.


# Stage38B Champion v12 triple-play and UPH clobber verifier

Task: `T-S38B-CODEX-CHAMPION-V12-UPH-SYSCTL-CLOBBER-AND-IGMPV2-CANARY-VERIFIER`.
The requested implementation filename intentionally follows its source champion:
[stage39a_champion_v12_triple_play_canary_verifier.py](../controller/stage39a_champion_v12_triple_play_canary_verifier.py).
Tests: [test_stage38b_champion_v12_canary_verifier.py](../tests/test_stage38b_champion_v12_canary_verifier.py).
Parent: external-controller, telemetry/control-authority and reversible experiment
deliverables in the [original forward plan](../artifacts/2026-09-20-forward-plan.html).
Acceptance was fixed before implementation in the Stage38B section of
[BENCH_PLAN](BENCH_PLAN.md). Software disposition is independent of RF acceptance;
E2 remains **NOT_ACCEPTED**.

## The two observed failure modes and source boundaries

All four requested inputs were inspected:

- [Stage37A JSON](../artifacts/autoresearch/stage37a_triple_play_aqm_fq_limit_bench_20261025.json)
  and [Stage37A report](STAGE37A_TRIPLE_PLAY_IPTV_VOIP_AND_MAC80211_FQ_LIMIT_BENCHMARK.md).
- [Stage39A JSON](../artifacts/autoresearch/stage39a_m19_m20_igmp_fast_leave_bench_20261025.json)
  and [Stage39A report](STAGE39A_M19_M20_IGMP_FAST_LEAVE_AND_MCAST_STALL_BENCHMARK.md).

| Source round | Observed/source-reported result | Consequence for this gate |
| --- | --- | --- |
| S37A-R1 | AP quantum3028 with VO600/1200 under triple-play: goodput-3.628% | Reject this older vector as v11/v12 |
| S37A-R2 / v11 | Quantum4542/1514, limit2048/1024, VO300/600: goodput+2.648%, p95-3.778%, p50-22.452%, zero IPTV/VoIP loss | Require this complete core, by role |
| S39A-R1 | Writing voip_bias1 after ff_mcast5 leaves both scalar getters1; IGMP3 with TID7 deltas2/1; goodput-4.560%, p95+12.729% | Reject clobber, IGMP3 and TID7 activity; enforce last UPH write |
| S39A-R2 | Per-phase qdisc/snooping resets accompany TID0 drops5/1/4/2 | Reject active-window writes, qdisc operations and nonzero drop endpoints |
| S39A-R3 / v12 | Goodput+5.863%, p95-5.361%, p50-8.747%, IPTV0/5669 and VoIP0/1199 lost, TID7 delta0 | Verify overlay and trace silence; no newly measured gain |

Those are historical bench facts, not measurements performed by this task.
The experiments change multiple controls together. Their reports' EDCA/DRR and
shared-pointer explanations are not isolated causal proofs from this verifier.
In particular, the runner's `parse_bridge_mcast_readback` retains only the first
integer. The scalar clobber is observed; these four inputs do **not** include a
native full16-integer buffer dump or complete alias-address map. The specific
shared-vector layout remains **INFERRED from the report**, requiring separate
native qualification before full-vector restoration is enabled.

The canonical positive rounds are sealed separately:

| Round | Canonical SHA256 |
| --- | --- |
| S37A-R2 | `69fec2437b2e13c6a9bcf4296b7827c920fa2902d997b9a3024d6f62995be131` |
| S39A-R3 | `4b3153a2305c35b4770b6a9db0bd01b85558cf5507d7898722a633eb38a1ac26` |

`source_contract` verifies their hashes and actual saved positive getter values.
Later appended rounds do not redefine these profiles. R3 does not reacquire
AQM/AQL, AP querier, Loco querier or Rocket snooping/querier getters. Their
requirements are declared recipe/inheritance contracts and require fresh
observations; the verifier never supplies absent values from R2 or a label.
R3 Rocket fast-leave is already1 in both arms, and AP WDS DMS is1 in both arms.
The observed control values take precedence over prose saying all fast-leave0;
the measured difference cannot be attributed to DMS or Rocket fast-leave alone.

## Deterministic readback contract

| Control | OpenWrt AP | OpenWrt Loco CPE | Stock Rocket CPE |
| --- | --- | --- | --- |
| Build | OpenWrt24.10.4 / Linux6.6.110 / ath10k | same | Rocket Prism5AC Gen2 / airOS8.7.11 |
| Internal quantum | 4542 | 1514 | Not inferred from mac80211 |
| FQ memory / packet limit / allocated flows | 4194304 / 2048 / 4096 | 4194304 / 1024 / 4096 | Not inferred |
| AQL VO / VI | 300/600 / 1200/2400us | same | Not inferred |
| AQL BE / BK | 1500/3000 / 500/1000us | 900/1500 / 500/1000us | Not inferred |
| AQL threshold | 5000 | 4000 | Not inferred |
| IGMP version | 2 | 2 | No version getter assumed |
| Snooping / querier | 1 / 1 | 0 / 0 | 0 / 0 |
| v12 fast-leave | 1 on every phy0-ap0 or phy0-ap0.staN port | 1 on every bridge port | 1 on every bridge port |
| DMS | 1 on every Wi-Fi WDS parent/child port | Capture if exposed | Capture if exposed |
| UPH multicast limit | Not applicable | Not applicable | 5, final shared-UPH write |

v11 verification fixes the core and single-querier prerequisites without
inventing fast-leave0 values. v12 additionally requires the fast-leave overlay.
AP Ethernet fast-leave is captured and restored as observed, rather than forced1.

`build_plan` requires a run ID, three distinct device UUIDs, explicit AP/CPE
station inventories, complete per-device bridge-port names and named IPTV,
voice and bulk flow specifications. `validate_plan` rebuilds and compares the
entire sealed plan. Names are literal, bounded netdev names; no shell globs,
addresses as identities, arbitrary shell fragments or guessed station numbers.

`normalize_bundle` consumes a qualified complete bundle containing `run_id`,
`source=qualified_stage38b_collector`, `inventory_complete=true` and exactly
`devices.ap`, `devices.cpe`, `devices.rocket`. Each device binds role/UUID/run,
boot UUID, namespace inode, module hash, increasing sequence, monotonic time
and fresh UTC. Three device timestamps must agree within1s.

OpenWrt device objects reuse the exact global AQM/per-station TXQ schema from
[Stage37B](STAGE37B_MAC80211_AQM_PER_TID_CANARY_VERIFIER.md), plus a complete
`aql_limits` dictionary on every station. Effective station limits must match
the global table, otherwise global restoration could overwrite a custom peer
override. The stable-tag [mac80211 global implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/debugfs.c)
and [station AQL implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/mac80211/debugfs_sta.c)
define the relevant readback/setter boundaries. Their source is not proof of
the installed image's identity; the native collector remains a separate gate.

Each bridge object contains its exact `/sys/devices/virtual/net/br-lan` or
`br0` path, ifindex, generation hash, snooping/querier and the OpenWrt IGMP
version, plus `ports_complete=true` and exactly the planned port set. Each port
has its name, ifindex, generation, fast-leave and optional DMS value. Missing
flags, unknown peers, recycled interfaces, generation changes or newly appearing
flag capabilities fail. IGMP versions2/3 are distinct kernel settings in the
[Linux bridge implementation](https://raw.githubusercontent.com/gregkh/linux/v6.6.110/net/bridge/br_multicast.c).

Rocket requires its scalar readback and `uph.vector_capture`: a complete
newline-terminated line of exactly16 signed32 integers, the full raw view of
each qualified alias, module binding, qualification digest and explicit
complete-alias/full-vector-setter attestations. All alias vectors and the scalar
must agree. This bounded qualification profile includes ff_mcast_airtime_limit,
voip_bias, fixed_frame, atpc, cms_bias and evm_meas_config; it is **not** a claim
that their complete native alias layout was proved by the historical JSON.
An unknown/partial/inconsistent layout blocks rather than becoming a scalar
rollback. Non-target indices1..15 must stay equal to baseline, and the whole
buffer must remain stable through the measured window.

## Post-apply triple-play, query and write evidence

`verify_readbacks` checks a single typed snapshot. `verify_canary` separately
requires **baseline, post-apply before, post-apply after**. The baseline is a
valid v11 foundation and the later endpoints both match v12. This prevents a
cached pre-apply interval from satisfying treatment evidence. Every device must
advance sequence, UTC and monotonic time over a5..55s window; the final readback
is at most10s old, earlier snapshots at most60s old. Station and bridge epochs,
whole memberships and module/boot/netns identity must remain unchanged.
Every captured numeric parameter must also remain identical between the two
post-apply endpoints, including AP Ethernet fast-leave and optional CPE DMS.
Being outside the v12 target overlay does not permit a silent in-window change.

Global event totals and drops/overlimits on every observed TXQ must be zero at
all endpoints. Missing counters, reset/wrap or replay never imply zero.
All AP **and CPE** TID7 TX packet/byte deltas must be exactly zero. This is
stricter than diagnosing only the particular72-byte query signature. TXQ
dequeue statistics are not receiver packet-delivery evidence; hardware ACK,
goodput, jitter, player QoE and wireless improvement are not accepted here.

Two explicit complete traces bind device/run/plan, before/after sequences,
the exact window and evidence hashes:

- `qualified_txq_flow_trace` identifies every planned flow at the same FQ
  dequeue boundary: UDP IPTV=TID4/AC1, UDP VoIP=TID6/AC0, TCP bulk=TID0/AC2.
  Positive disjoint matched counts per station/TID cannot exceed TXQ deltas;
  same-class reused evidence digests fail. A rule or service label alone is
  insufficient to identify actual traffic.
- `qualified_igmp_tx_trace` explicitly lists observed queries, including a
  qualified empty list when none occurred. Version3 or the72-byte CS6
  codepoint48/TID7/AC0 signature fails. DSCP/TID/AC/length bounds and TID-to-AC
  consistency are checked. A missing trace cannot establish silence.

<!-- stage822a-payload-end -->
