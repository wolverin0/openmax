<!-- doc-head: STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE.md continuation 1 of 2; source lines preserved -->
<!-- /doc-head -->

[Document router](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE.md) | Part 1/2
<a id="verification-and-disposition"></a> [Verification and disposition](STAGE36B_IPTV_DMS_AC_VI_CANARY_GATE_CONTINUATION_efaee85008_002.md#verification-and-disposition)

<!-- stage822a-payload-begin -->

Direct focused pytest:73PASS,0FAIL,0ERROR,exit0 in1.62s; disposable clocks/state only.
Verify bridge snooping/querier and every discovered parent/WDS DMS port with MAC/ifindex/boot/netns binding.
Requested AQL VO600/1200,VI1200/2400,BE1000/2000,BK500/1000; threshold and BC/MC remain captured values.
Require explicit receiver jitter/loss budgets and fresh classified IPTV/HLS windows; no modeled QoE acceptance.
Independent60s lease triggers fenced exact-state restoration; device/runtime/physical acceptance remain UNKNOWN.


# Stage36B â€” IPTV DMS / AC_VI canary gate

Task: `T-S36B-CODEX-IPTV-AC-VI-DMS-AND-HLS-PACING-CONTROLLER-INTEGRATION`.
Software result: **73/73 focused tests passed**. Runtime and physical acceptance:
**UNKNOWN / not authorized or executed by this task**. E2 remains **NOT_ACCEPTED**.
Behavior belongs to the external controller. Readbacks describe Linux bridge and
mac80211 AQL controls used by ath10k; no QCA firmware/PHY gain is claimed.

The operator explicitly requested direct pytest without `heavy-slot.cjs`.
Stage35B's prior wait is closed; its direct66PASS/exit0 result and completed task
are recorded in [its report](STAGE35B_UNIFIED_OPENWISP_UISP_CANARY_PROVISIONER.md).
The accepted Stage35B product module is unchanged. This gate is additive:
[controller/iptv_dms_ac_vi_canary_gate.py](../controller/iptv_dms_ac_vi_canary_gate.py).

Parent: external-controller, telemetry and reversible experiment deliverables in
the [original forward plan](../artifacts/2026-09-20-forward-plan.html). The Stage36B
section of [BENCH_PLAN](BENCH_PLAN.md) fixes acceptance before implementation.

## Inspected evidence and scope

Three requested inputs were inspected: the IPTV optimizer, the Stage35B unified
provisioner and the [Stage35A bench artifact](../artifacts/autoresearch/stage35a_openwisp_portal_and_m15_5ghz_bench_20261025.json).
The narrowly relevant [Stage36A bench artifact](../artifacts/autoresearch/stage36a_live_iptv_ac_vi_ptmp_bench_20261025.json)
and AP ledger were also checked as source evidence.

Stage35A `S35A-R1` B1/B2 report snooping=1, querier=1 and DMS=1 on `phy0-ap0`
and its dynamic WDS ports. That source also changes stock R198's M15 control;
the reported result is a **compound AP+CPE treatment**. The AP ledger still
declares the v8 vector. Accordingly, the new plan pins the Stage35A artifact
(`779d29dcâ€¦68ebb`) and labels v9 as source-reported. It verifies the AP multicast
delta plus the requested IPTV limits, with independently qualified unchanged v8
foundation readbacks; it does not silently rewrite the ledger or execute stock
CPE M15 commands.

The saved Stage36A `S36A-R1` round reports IPTV receiver jitter **1.706â†’2.157ms (+26.436%)**,
goodput **69.077â†’64.777Mbps (-6.225%)**, and `RETAIN_CURRENT_CHAMPION`.
These are source reports, not newly executed measurements. They do not establish
a universal acceptable jitter threshold, a promotion or player rebuffering behavior.

The optimizer supplies useful QoS context but its script hardcodes `wlan0`, uses
BK1000/2000, applies extra qdisc/nft/stock controls and swallows setter errors.
The operator's **BK500/1000** requirement governs this gate. Its modelled capacity
and `ZERO_REBUFFERING` strings are not acceptance evidence. The script is not run.

## Required readbacks and targets

| Effective control | Required value | Ownership |
| --- | --- | --- |
| `br-lan/bridge/multicast_snooping` | 1 | AP bridge RAM |
| `br-lan/bridge/multicast_querier` | 1 | AP bridge RAM |
| Parent `phy0-ap0` and all discovered `phy0-ap0.sta*` DMS flags | 1 on each port | AP bridge-port RAM |
| AC_VO / index0 | 600 / 1200Âµs | mac80211 global AQL |
| AC_VI / index1 | 1200 / 2400Âµs | mac80211 global AQL |
| AC_BE / index2 | 1000 / 2000Âµs | mac80211 global AQL |
| AC_BK / index3 | 500 / 1000Âµs | mac80211 global AQL |
| `aql_threshold` and optional `BC/MC` limit | Preserve captured values | Readback only |

`parse_aql_readback` reads the kernel's named AC header/rows. An optional BC/MC
line and appended threshold from combined bench captures are parsed separately;
they are not a fifth queue or an inferred default. Four queues are mandatory.
Duplicate/missing rows, invalid integers, low>high, malformed/extra lines and
conflicting separately observed thresholds fail. Row labels govern identity.
The index mapping and conditional peer-limit propagation follow
[Linux6.6 mac80211 debugfs](https://github.com/torvalds/linux/blob/v6.6/net/mac80211/debugfs.c)
and the [mac80211 AC enumeration](https://github.com/torvalds/linux/blob/v6.6/include/net/mac80211.h).
The exact installed build remains a separate adapter qualification requirement.

There is an additional necessary restore boundary: global AQL writes update peer
limits selectively. If a station originally has custom limits, applying and then
restoring global values could change that station's pre-existing override.
Therefore every affected station must expose all four effective limits, uniform
with the current global values. Unknown or custom limits block before arming.
The snapshot retains every station's values and restoration verifies them too.
This gate does not promise restoration of arbitrary custom peer AQL settings.

## Dynamic WDS inventory and setter fencing

The collector must enumerate the **whole affected wiphy station set**, including
peers on other VAPs. It must match the explicit plan inventory exactly. A collector
that only sees the IPTV subset cannot establish safe global AQL ownership.
An extra peer on another VAP, incomplete inventory, non-ath10k driver, missing
readback or unbound dynamic bridge port fails closed.

Each effective receipt identifies run, device, timestamp, OpenWrt AP role,
four-address WDS, wiphy, driver, boot UUID and network-namespace inode. It includes
bridge and parent ifindices, every parent/dynamic-port ifindex and DMS value, and
each station's MAC, bound interface/ifindex, association, authorization and AQL.
No station-number constants are embedded; fixtures use `.sta17` and `.sta103`.
The parent DMS flag is captured separately because saved control data already has
parent=1 while child ports are0. Restoration cannot assume all flags started at0.

MAC/interface/ifindex/parent/bridge/boot/netns bindings must remain identical.
A join, disappearance, port rename/recycle, deauthorization or missing four-address
evidence fails the treatment. The coordinator rereads identity before each typed
setter. The qualified adapter must **atomically** recheck that identity, whole
wiphy membership, current global AQL and per-station uniformity with the setter,
under exclusive fencing. A controller-side check alone cannot close that race.

## Prespecified IPTV and HLS receiver gate

`JitterPolicy` is required when building the plan. It has no numerical QoE defaults:

| Policy field | Meaning |
| --- | --- |
| `max_jitter_ms` | Absolute receiver jitter ceiling |
| `max_increase_pct` | Optional additional ceiling relative to the paired baseline |
| `max_loss_pct` | Allowed receiver loss, computed from explicit denominators |
| `min_received_units` | Minimum received datagrams or segments |
| `min_window_s` | Minimum receiver measurement window |

Every planned stream has an explicit ID, station MAC, baseline jitter and metric
kind. `udp_receiver_jitter_ms` uses UDP datagrams; `hls_intersegment_jitter_ms`
uses HLS segment arrivals. Ping RTT variation, modelled rebuffering and these two
receiver metrics cannot substitute for one another. A relative ceiling requires
a positive baseline; an explicit absolute-only policy can represent a zero baseline.
Budgets and stream membership are bound into the plan hash before application.

All planned streams must provide fresh matching receiver reports under bulk load,
post-application start/end times, sufficient sent/received units, valid loss and
finite jitter. Each must show actual AC_VI classification, TID4/5 and DSCP
codepoint32(CS4) or34(AF41). Codepoints are distinct from the IP ToS octets
0x80/0x88; passing136 as the DSCP codepoint fails. A marking rule or stream label
alone does not prove classification.

The plan requires at least three healthy samples spanning at least ten seconds
on monotonic time, radio timestamps and every receiver stream's window ends.
Radio timestamps and receiver windows must progress; refreshed wrapper timestamps
cannot turn a replay into a fresh sample. Windows may overlap: no independent
replicate count, causal performance estimate or player-quality claim is made.

Existing HLS pacing and classifier configuration remain untouched. The gate checks
observed delivery/classification and rejects unhealthy behavior. It does not
install a global eth0 rate cap, replace qdiscs, flush nft tables, change CPEs,
persist UCI or invoke the Stage36C script.

## Independent60s lease and exact restoration

`execute_iptv_canary` consumes the Stage35B-style qualified runtime adapter boundary.
There is no default SSH, device writer, service installer or live canary CLI.
Library execution defaults to disposable fixtures; a device adapter needs explicit
`fixture_only=False` and an independently approved qualification digest for the
exact plan/build. A caller-supplied hash alone is not independent acceptance.
IPTV acquisition does not require unrelated native UISP protocol qualification.

Before mutation, the controller captures the complete normalized identity and
values, creates explicit restore writes from that snapshot and obtains the
independent resident guard's READY receipt. The guard owns the snapshot/restore
<!-- stage822a-payload-end -->
